"""USD_JPY 10-pip range-bar MTF breakout — ``usdjpy_range_bar_mtf_breakout 0.1.0-c029``.

CAMPAIGN_029 scaffold only. **NOT approved** for paper, demo, or live.
See ``docs/research/CAMPAIGN_029_PRECOMMIT_SCOPE.md`` (binding precommit) and
``docs/research/CAMPAIGN_029_HTF_ALIGNMENT_DESIGN.md``.

This is a *pure research strategy*: no broker / executor / OANDA imports, signals
are deterministic functions of the provided data, and it refuses any live/paper/
demo use. The execution frame is a sequence of ``non_time_bars.RangeBar`` records
(range bars are **not** a ``CandleFrame.Granularity``), so this module is
deliberately **not** registered in ``strategies/__init__.py`` and **not** wired to
the executor/loop — it cannot reach an order path.

Trigger: trend-aligned continuation *after a pullback and reclaim*, measured on
10-pip range bars, gated by H4 (H4M1) EMA50-slope trend bias and an optional
native-H4-derived D1AGG "not against" confirmation. HTF context is the last
completed HTF bar at the range bar's close timestamp (``align_last_completed``);
entry is the **open of the next completed range bar** (no same-bar fill).
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Literal

import pandas as pd

from forex_bot.data.non_time_bars import RangeBar, pip_size
from forex_bot.domain.candles import CandleFrame
from forex_bot.domain.signals import Signal
from forex_bot.features.htf_align import HTF_UNAVAILABLE, align_last_completed
from forex_bot.strategies.indicators import ema

Side = Literal["long", "short"]
Trend = Literal["bullish", "bearish", "neutral"]

CAMPAIGN_ID = "CAMPAIGN_029"
PAIR = "USD_JPY"
EXECUTION_TIMEFRAME = "RANGE_10PIP"  # free-form Signal.timeframe label (not a Granularity)
RANGE_THRESHOLD_PIPS = 10.0

EXECUTION_BARS_PROVENANCE = "range_bar_10pip_m1_mid"
D1AGG_SOURCE_NATIVE = "native_h4_derived_d1agg"
D1AGG_SOURCE_M1 = "m1_derived_d1agg"

# Exit reasons (frozen vocabulary — precommit §6).
EXIT_STOP = "stop"
EXIT_TIME = "time"
EXIT_EOD = "end_of_data"


class LiveTradingRefused(RuntimeError):
    """Raised on any attempt to use this scaffold for paper/demo/live trading."""


# --------------------------------------------------------------------------- #
# Provenance / config
# --------------------------------------------------------------------------- #
def validate_c029_data_provenance(provenance: dict[str, Any] | None) -> None:
    """Reject ambiguous or forbidden data sources for CAMPAIGN_029."""
    if not provenance:
        raise ValueError("BLOCKED_PROVENANCE_AMBIGUITY: data_provenance missing")
    exec_bars = provenance.get("execution_bars")
    if exec_bars != EXECUTION_BARS_PROVENANCE:
        raise ValueError(
            f"CAMPAIGN_029 requires execution_bars={EXECUTION_BARS_PROVENANCE!r}, got {exec_bars!r}"
        )
    if provenance.get("context_h4") != "m1_derived":
        raise ValueError("CAMPAIGN_029 requires context_h4=m1_derived")
    d1_src = provenance.get("d1agg_context")
    # D1AGG is optional, but if declared it must be the native-derived source.
    if d1_src is not None and d1_src not in (D1AGG_SOURCE_NATIVE,):
        if d1_src == D1AGG_SOURCE_M1:
            raise ValueError("CAMPAIGN_029 rejects m1_derived_d1agg")
        raise ValueError(
            f"CAMPAIGN_029 requires d1agg_context={D1AGG_SOURCE_NATIVE!r}, got {d1_src!r}"
        )


@dataclass(frozen=True)
class RangeBarMtfBreakoutConfig:
    """Frozen, precommitted parameters (see CAMPAIGN_029_PRECOMMIT_SCOPE.md §2)."""

    range_threshold_pips: float = RANGE_THRESHOLD_PIPS
    pullback_lookback: int = 5
    structure_lookback: int = 5
    h4_ema_fast: int = 20
    h4_ema_slow: int = 50
    h4_ema_slope_bars: int = 3
    d1_ema_fast: int = 20
    d1_ema_slow: int = 50
    d1_ema_slope_bars: int = 3
    d1agg_required: bool = False
    overshoot_max_thresholds: int = 1
    overshoot_max_pips: float = 10.0
    stop_range_multiple: float = 2.0
    max_bars_in_trade: int = 12

    @classmethod
    def from_config(cls, cfg: dict[str, Any]) -> RangeBarMtfBreakoutConfig:
        block = cfg.get("usdjpy_range_bar_mtf_breakout", cfg)
        return cls(
            range_threshold_pips=float(block.get("range_threshold_pips", RANGE_THRESHOLD_PIPS)),
            pullback_lookback=int(block.get("pullback_lookback", 5)),
            structure_lookback=int(block.get("structure_lookback", 5)),
            h4_ema_fast=int(block.get("h4_ema_fast", 20)),
            h4_ema_slow=int(block.get("h4_ema_slow", 50)),
            h4_ema_slope_bars=int(block.get("h4_ema_slope_bars", 3)),
            d1_ema_fast=int(block.get("d1_ema_fast", 20)),
            d1_ema_slow=int(block.get("d1_ema_slow", 50)),
            d1_ema_slope_bars=int(block.get("d1_ema_slope_bars", 3)),
            d1agg_required=bool(block.get("d1agg_required", False)),
            overshoot_max_thresholds=int(block.get("overshoot_max_thresholds", 1)),
            overshoot_max_pips=float(block.get("overshoot_max_pips", 10.0)),
            stop_range_multiple=float(block.get("stop_range_multiple", 2.0)),
            max_bars_in_trade=int(block.get("max_bars_in_trade", 12)),
        )

    def __post_init__(self) -> None:
        if abs(self.range_threshold_pips - RANGE_THRESHOLD_PIPS) > 1e-9:
            raise ValueError(
                f"CAMPAIGN_029 is a 10-pip range-bar campaign; got "
                f"range_threshold_pips={self.range_threshold_pips}"
            )
        if self.pullback_lookback < 1 or self.structure_lookback < 1:
            raise ValueError("pullback_lookback and structure_lookback must be >= 1")


# --------------------------------------------------------------------------- #
# HTF frame helpers (backward-looking only)
# --------------------------------------------------------------------------- #
def _htf_close_frame(frame: CandleFrame, *, ema_fast: int, ema_slow: int) -> pd.DataFrame:
    df = frame.completed_only().df
    if df.empty:
        return pd.DataFrame(columns=["time", "complete", "close", "ema_fast", "ema_slow"])
    close = df["close"].astype(float).reset_index(drop=True)
    out = pd.DataFrame(
        {
            "time": pd.to_datetime(df.index, utc=True),
            "complete": True,
            "close": close.to_numpy(),
        }
    )
    out["ema_fast"] = ema(close, ema_fast)
    out["ema_slow"] = ema(close, ema_slow)
    return out


def _slope(series: pd.Series, anchor_time: pd.Timestamp, times: pd.Series, bars: int) -> float | None:
    """Change in ``series`` over ``bars`` completed bars, anchored at ``anchor_time``.

    Measured strictly on bars at/before ``anchor_time`` so it can never read a bar
    that closed after the decision.
    """
    mask = pd.to_datetime(times, utc=True) <= anchor_time
    vals = series[mask].dropna()
    if len(vals) < bars + 1:
        return None
    return float(vals.iloc[-1] - vals.iloc[-(bars + 1)])


def aligned_h4_trend(
    h4_frame: CandleFrame, decision_dt: datetime, *, ema_fast: int, ema_slow: int, slope_bars: int
) -> tuple[Trend, datetime | None, str | None]:
    """H4 (H4M1): close vs EMA50 with an agreeing EMA50 slope (precommit §3)."""
    htf = _htf_close_frame(h4_frame, ema_fast=ema_fast, ema_slow=ema_slow)
    if len(htf) < ema_slow + slope_bars + 1:
        return "neutral", None, HTF_UNAVAILABLE
    aligned = align_last_completed(
        pd.DatetimeIndex([decision_dt]), htf, ["close", "ema_slow"], prefix="h4"
    )
    reason = aligned.get("h4_blocked_reason", pd.Series([None])).iloc[0]
    if reason:
        return "neutral", None, reason
    close = float(aligned["h4_close"].iloc[0])
    es = float(aligned["h4_ema_slow"].iloc[0])
    feat_time = aligned["h4_close_time"].iloc[0]
    anchor = pd.Timestamp(feat_time)
    if pd.isna(anchor):
        return "neutral", None, HTF_UNAVAILABLE
    if anchor.tzinfo is None:
        anchor = anchor.tz_localize("UTC")
    slope = _slope(htf["ema_slow"], anchor, htf["time"], slope_bars)
    if slope is None or not all(math.isfinite(v) for v in (close, es)):
        return "neutral", None, HTF_UNAVAILABLE
    ts = anchor.to_pydatetime()
    if close > es and slope > 0:
        return "bullish", ts, None
    if close < es and slope < 0:
        return "bearish", ts, None
    return "neutral", ts, None


def aligned_d1agg_regime(
    d1agg_frame: CandleFrame, decision_dt: datetime, *, ema_fast: int, ema_slow: int, slope_bars: int
) -> tuple[str, datetime | None, str | None]:
    """D1AGG permissive regime → ``not_bearish_only`` / ``not_bullish_only`` / ``both`` / ``neither``."""
    htf = _htf_close_frame(d1agg_frame, ema_fast=ema_fast, ema_slow=ema_slow)
    if len(htf) < ema_slow + slope_bars + 1:
        return "neither", None, HTF_UNAVAILABLE
    aligned = align_last_completed(
        pd.DatetimeIndex([decision_dt]), htf, ["close", "ema_fast", "ema_slow"], prefix="d1agg"
    )
    reason = aligned.get("d1agg_blocked_reason", pd.Series([None])).iloc[0]
    if reason:
        return "neither", None, reason
    close = float(aligned["d1agg_close"].iloc[0])
    es = float(aligned["d1agg_ema_slow"].iloc[0])
    feat_time = aligned["d1agg_close_time"].iloc[0]
    anchor = pd.Timestamp(feat_time)
    if pd.isna(anchor):
        return "neither", None, HTF_UNAVAILABLE
    if anchor.tzinfo is None:
        anchor = anchor.tz_localize("UTC")
    slope = _slope(htf["ema_fast"], anchor, htf["time"], slope_bars)
    if slope is None or not all(math.isfinite(v) for v in (close, es)):
        return "neither", None, HTF_UNAVAILABLE
    not_bearish = close >= es or slope >= 0
    not_bullish = close <= es or slope <= 0
    ts = anchor.to_pydatetime()
    if not_bearish and not_bullish:
        return "both", ts, None
    if not_bearish:
        return "not_bearish_only", ts, None
    if not_bullish:
        return "not_bullish_only", ts, None
    return "neither", ts, None


def d1agg_allows(regime: str, side: Side) -> bool:
    if side == "long":
        return regime in ("not_bearish_only", "both")
    return regime in ("not_bullish_only", "both")


# --------------------------------------------------------------------------- #
# Range-bar trigger (pure)
# --------------------------------------------------------------------------- #
def is_extreme_overshoot(bar: RangeBar, *, max_thresholds: int, max_overshoot_pips: float) -> bool:
    """Anti-spike guard (precommit §2): reject violent multi-threshold trigger bars."""
    return bar.thresholds_crossed > max_thresholds or bar.overshoot_pips > max_overshoot_pips


def pullback_reclaim_side(bars: Sequence[RangeBar], *, pullback_lookback: int) -> Side | None:
    """Continuation trigger: the reclaim direction of the most recent completed bar.

    Long  iff trigger bar is ``range_up``   and >=1 of the prior ``pullback_lookback``
          completed bars was ``range_down`` (a pullback then a reclaim up).
    Short iff trigger bar is ``range_down`` and >=1 of the prior bars was ``range_up``.
    Returns ``None`` if there is no pullback-then-reclaim. Direction is *not* yet
    confirmed against the H4 bias — the caller does that.
    """
    if len(bars) < 2:
        return None
    trigger = bars[-1]
    if trigger.incomplete:
        return None
    window = bars[-(pullback_lookback + 1):-1]  # the bars BEFORE the trigger
    if not window:
        return None
    if trigger.completion_reason == "range_up" and any(b.completion_reason == "range_down" for b in window):
        return "long"
    if trigger.completion_reason == "range_down" and any(b.completion_reason == "range_up" for b in window):
        return "short"
    return None


def structural_stop(
    bars: Sequence[RangeBar],
    *,
    side: Side,
    structure_lookback: int,
    range_threshold_pips: float,
    stop_range_multiple: float,
    instrument: str = PAIR,
) -> float:
    """Stop = max(structural-swing distance, range-size floor) from the trigger close."""
    psize = float(pip_size(instrument))
    trigger_close = bars[-1].close
    window = bars[-structure_lookback:]
    if side == "long":
        structure_level = min(b.low for b in window)
    else:
        structure_level = max(b.high for b in window)
    d_struct = abs(trigger_close - structure_level)
    d_floor = stop_range_multiple * range_threshold_pips * psize
    distance = max(d_struct, d_floor)
    return trigger_close - distance if side == "long" else trigger_close + distance


def resolve_exit(
    *,
    side: Side,
    stop_price: float,
    entry_index: int,
    highs: list[float],
    lows: list[float],
    max_bars_in_trade: int,
) -> tuple[str, int]:
    """Frozen exit priority over post-entry RANGE bars: stop → time → end_of_data.

    ``highs``/``lows`` are the full range-bar series; bars strictly after
    ``entry_index`` are the holding window. (For the future execution sprint;
    no profit target, no trail, no second stop.)
    """
    n = len(highs)
    last_held = min(entry_index + max_bars_in_trade, n - 1)
    for i in range(entry_index + 1, last_held + 1):
        if side == "long" and lows[i] <= stop_price:
            return EXIT_STOP, i
        if side == "short" and highs[i] >= stop_price:
            return EXIT_STOP, i
        if i - entry_index >= max_bars_in_trade:
            return EXIT_TIME, i
    return EXIT_EOD, last_held


# --------------------------------------------------------------------------- #
# Strategy
# --------------------------------------------------------------------------- #
class UsdJpyRangeBarMtfBreakoutStrategy:
    """CAMPAIGN_029 — USD_JPY 10-pip range-bar MTF breakout (scaffold only).

    Pure-signal research class. Call :meth:`generate_signal` with a sequence of
    completed :class:`RangeBar` records (up to and including the trigger bar) plus
    HTF :class:`CandleFrame`s. It returns at most one :class:`Signal`; the engine
    of a *future* execution sprint is responsible for the next-range-bar-open fill.
    """

    name: str = "usdjpy_range_bar_mtf_breakout"

    def __init__(self, version: str = "0.1.0-c029") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        return 6  # >= structure_lookback (5) + the trigger bar

    # -- live/paper/demo refusal ------------------------------------------- #
    def for_live_trading(self, *_args: Any, **_kwargs: Any) -> None:
        raise LiveTradingRefused(
            "usdjpy_range_bar_mtf_breakout 0.1.0-c029 is SCAFFOLD_ONLY / NOT_APPROVED: "
            "it has no executor wiring and refuses paper/demo/live use. "
            "configs/approved_strategies.yaml must stay approved: []."
        )

    on_paper = for_live_trading
    on_demo = for_live_trading
    on_live = for_live_trading

    def generate_signal(
        self,
        range_bars: Sequence[RangeBar],
        *,
        h4_frame: CandleFrame,
        d1agg_frame: CandleFrame | None = None,
        open_positions: Sequence[Any] = (),
        config: dict[str, Any],
    ) -> Signal | None:
        validate_c029_data_provenance(config.get("data_provenance"))
        params = RangeBarMtfBreakoutConfig.from_config(config.get("strategy", config))

        bars = [b for b in range_bars if not b.incomplete]
        if len(bars) < max(self.warmup_bars_required(), params.structure_lookback + 1):
            return None

        trigger = bars[-1]
        if trigger.instrument != PAIR:
            raise ValueError(f"CAMPAIGN_029 is {PAIR}-only; got {trigger.instrument!r}")

        # One position per instrument.
        if any(
            not getattr(pos, "is_flat", True) and getattr(pos, "instrument", None) == PAIR
            for pos in open_positions
        ):
            return None

        # 1) Trigger direction from pullback-and-reclaim.
        side = pullback_reclaim_side(bars, pullback_lookback=params.pullback_lookback)
        if side is None:
            return None

        # 2) Anti-spike guard.
        if is_extreme_overshoot(
            trigger,
            max_thresholds=params.overshoot_max_thresholds,
            max_overshoot_pips=params.overshoot_max_pips,
        ):
            return None

        decision_dt = trigger.close_time
        if decision_dt.tzinfo is None:
            decision_dt = decision_dt.replace(tzinfo=UTC)

        # 3) Mandatory H4 trend bias.
        h4_trend, h4_time, h4_block = aligned_h4_trend(
            h4_frame,
            decision_dt,
            ema_fast=params.h4_ema_fast,
            ema_slow=params.h4_ema_slow,
            slope_bars=params.h4_ema_slope_bars,
        )
        if h4_block:
            return None
        wanted: Trend = "bullish" if side == "long" else "bearish"
        if h4_trend != wanted:
            return None

        # 4) Optional D1AGG "not against" confirmation.
        d1_regime = "unavailable"
        d1_time: datetime | None = None
        d1agg_applied = False
        if d1agg_frame is not None:
            regime, d1_time_r, d1_block = aligned_d1agg_regime(
                d1agg_frame,
                decision_dt,
                ema_fast=params.d1_ema_fast,
                ema_slow=params.d1_ema_slow,
                slope_bars=params.d1_ema_slope_bars,
            )
            if not d1_block:
                d1_regime = regime
                d1_time = d1_time_r
                d1agg_applied = True
                if not d1agg_allows(regime, side):
                    return None
            elif params.d1agg_required:
                return None
        elif params.d1agg_required:
            return None

        # 5) Structural stop.
        stop = structural_stop(
            bars,
            side=side,
            structure_lookback=params.structure_lookback,
            range_threshold_pips=params.range_threshold_pips,
            stop_range_multiple=params.stop_range_multiple,
        )

        htf_times: dict[str, datetime] = {}
        if h4_time is not None:
            htf_times["h4"] = h4_time
        if d1_time is not None:
            htf_times["d1agg"] = d1_time

        bar_iso = pd.Timestamp(decision_dt).tz_convert(UTC).isoformat()
        signal_id = _stable_signal_id(
            self.name, self.version, PAIR, EXECUTION_TIMEFRAME, bar_iso, side
        )
        provenance = dict(config.get("data_provenance") or {})
        psize = float(pip_size(PAIR))
        stop_quant = Decimal(str(stop)).quantize(Decimal("0.001"))

        return Signal(
            signal_id=signal_id,
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=PAIR,
            timeframe=EXECUTION_TIMEFRAME,
            timestamp=decision_dt,
            side=side,
            entry_intent="market",  # filled at NEXT range-bar open by the engine
            stop_model=(
                f"RANGE_max(struct{params.structure_lookback}_swing,"
                f"{params.stop_range_multiple}x{params.range_threshold_pips:g}pip)"
            ),
            stop_price=stop_quant,
            exit_model="hard_stop_or_time",
            campaign_id=CAMPAIGN_ID,
            decision_time=decision_dt,
            available_data_cutoff=decision_dt,
            source_candle_timestamp=decision_dt,
            htf_feature_times=htf_times or None,
            features={
                "trigger_completion_reason": trigger.completion_reason,
                "trigger_thresholds_crossed": trigger.thresholds_crossed,
                "trigger_overshoot_pips": trigger.overshoot_pips,
                "range_threshold_pips": params.range_threshold_pips,
                "pullback_lookback": params.pullback_lookback,
                "structure_lookback": params.structure_lookback,
                "h4_trend": h4_trend,
                "d1agg_regime": d1_regime,
                "d1agg_applied": d1agg_applied,
                "stop_distance_pips": abs(trigger.close - stop) / psize,
                "max_bars_in_trade": params.max_bars_in_trade,
                "fill_timing": "next_bar_open",
                "data_provenance": provenance,
            },
            reason=(
                f"USD_JPY 10pip range continuation {side}: H4 {wanted}, "
                f"D1AGG {d1_regime} (applied={d1agg_applied}), pullback-reclaim"
            ),
        )


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]

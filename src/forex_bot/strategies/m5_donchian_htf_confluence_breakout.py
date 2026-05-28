"""M5 Donchian + HTF confluence breakout — ``m5_donchian_htf_confluence_breakout 0.1.0-c024``.

CAMPAIGN_024 scaffold only. **NOT approved** for paper, demo, or live.
See ``docs/research/CAMPAIGN_024_PRECOMMIT_M5_DONCHIAN_HTF_CONFLUENCE_SCOPE.md``.

M5 execution with M15 setup + H1/H4/D1AGG context via ``align_last_completed``.
The Donchian channel uses prior completed bars only (``donchian_high``/
``donchian_low`` shift by one), so the current bar is never part of its own
channel — no current-bar lookahead. D1AGG must use ``native_h4_derived_d1agg``
provenance; M1-derived D1AGG is rejected.

This module is a *pure research strategy*: no broker, executor, or order-API
imports, and signals are deterministic functions of the provided bar data.
"""

from __future__ import annotations

import hashlib
import math
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Literal

import pandas as pd

from forex_bot.domain.candles import CandleFrame
from forex_bot.domain.signals import Signal
from forex_bot.features.htf_align import HTF_UNAVAILABLE, align_last_completed
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import atr, donchian_high, donchian_low, ema

Side = Literal["long", "short"]
Trend = Literal["bullish", "bearish", "neutral"]

EXECUTION_TIMEFRAME = "M5"
CAMPAIGN_ID = "CAMPAIGN_024"

D1AGG_SOURCE_NATIVE = "native_h4_derived_d1agg"
D1AGG_SOURCE_M1 = "m1_derived_d1agg"

# Exit reasons (frozen vocabulary — see precommit §6).
EXIT_STOP = "stop"
EXIT_TIME = "time"
EXIT_EOD = "eod"


# --------------------------------------------------------------------------- #
# Provenance / context guards
# --------------------------------------------------------------------------- #
def validate_c024_data_provenance(provenance: dict[str, Any] | None) -> None:
    """Reject ambiguous or forbidden data sources for CAMPAIGN_024."""
    if not provenance:
        raise ValueError("BLOCKED_PROVENANCE_AMBIGUITY: data_provenance missing")
    d1_src = provenance.get("d1agg_context") or provenance.get("d1agg_source")
    if d1_src == D1AGG_SOURCE_M1:
        raise ValueError("CAMPAIGN_024 rejects m1_derived_d1agg")
    if d1_src != D1AGG_SOURCE_NATIVE:
        raise ValueError(
            f"CAMPAIGN_024 requires d1agg_context={D1AGG_SOURCE_NATIVE!r}, got {d1_src!r}"
        )
    for key in ("execution_m5", "context_m15", "context_h1", "context_h4"):
        if provenance.get(key) != "m1_derived":
            raise ValueError(f"CAMPAIGN_024 requires {key}=m1_derived")


def _require_context_frames(cfg: dict[str, Any]) -> dict[str, CandleFrame]:
    raw = cfg.get("context_frames")
    if not isinstance(raw, dict):
        raise ValueError("context_frames required in strategy config")
    for name in ("M15", "H1", "H4", "D1AGG"):
        if name not in raw or not isinstance(raw[name], CandleFrame):
            raise ValueError(f"missing context frame: {name}")
    return raw


# --------------------------------------------------------------------------- #
# HTF frame helpers
# --------------------------------------------------------------------------- #
def _htf_close_frame(frame: CandleFrame) -> pd.DataFrame:
    """Build a ``time/complete/close`` + EMA frame from completed HTF candles."""
    df = frame.completed_only().df
    if df.empty:
        return pd.DataFrame(columns=["time", "complete", "close"])
    close = df["close"].astype(float).reset_index(drop=True)
    out = pd.DataFrame(
        {
            "time": pd.to_datetime(df.index, utc=True),
            "complete": True,
            "close": close.to_numpy(),
        }
    )
    out["ema_fast"] = ema(close, 20)
    out["ema_slow"] = ema(close, 50)
    return out


def _slope(series: pd.Series, anchor_time: pd.Timestamp, times: pd.Series, bars: int) -> float | None:
    """EMA slope over ``bars`` completed bars, anchored at the aligned bar.

    The slope is measured strictly on bars at or before ``anchor_time`` so it can
    never read a bar that closed after the decision.
    """
    mask = pd.to_datetime(times, utc=True) <= anchor_time
    vals = series[mask].dropna()
    if len(vals) < bars + 1:
        return None
    return float(vals.iloc[-1] - vals.iloc[-(bars + 1)])


def aligned_h1_trend(h1_frame: CandleFrame, decision_dt: datetime, *, slope_bars: int) -> tuple[Trend, datetime | None, str | None]:
    """H1: EMA20 vs EMA50 with an agreeing EMA20 slope (last ``slope_bars`` bars)."""
    htf = _htf_close_frame(h1_frame)
    if len(htf) < 52:
        return "neutral", None, HTF_UNAVAILABLE
    aligned = align_last_completed(
        pd.DatetimeIndex([decision_dt]), htf, ["ema_fast", "ema_slow"], prefix="h1"
    )
    reason = aligned.get("h1_blocked_reason", pd.Series([None])).iloc[0]
    if reason:
        return "neutral", None, reason
    ef = float(aligned["h1_ema_fast"].iloc[0])
    es = float(aligned["h1_ema_slow"].iloc[0])
    feat_time = aligned["h1_ema_fast_time"].iloc[0]
    anchor = pd.Timestamp(feat_time)
    if pd.isna(anchor):
        return "neutral", None, HTF_UNAVAILABLE
    if anchor.tzinfo is None:
        anchor = anchor.tz_localize("UTC")
    slope = _slope(htf["ema_fast"], anchor, htf["time"], slope_bars)
    if slope is None or not all(math.isfinite(v) for v in (ef, es)):
        return "neutral", None, HTF_UNAVAILABLE
    ts = anchor.to_pydatetime()
    if ef > es and slope >= 0:
        return "bullish", ts, None
    if ef < es and slope <= 0:
        return "bearish", ts, None
    return "neutral", ts, None


def aligned_h4_trend(h4_frame: CandleFrame, decision_dt: datetime) -> tuple[Trend, datetime | None, str | None]:
    """H4: close vs EMA50 and EMA20 vs EMA50."""
    htf = _htf_close_frame(h4_frame)
    if len(htf) < 52:
        return "neutral", None, HTF_UNAVAILABLE
    aligned = align_last_completed(
        pd.DatetimeIndex([decision_dt]), htf, ["close", "ema_fast", "ema_slow"], prefix="h4"
    )
    reason = aligned.get("h4_blocked_reason", pd.Series([None])).iloc[0]
    if reason:
        return "neutral", None, reason
    close = float(aligned["h4_close"].iloc[0])
    ef = float(aligned["h4_ema_fast"].iloc[0])
    es = float(aligned["h4_ema_slow"].iloc[0])
    feat_time = aligned["h4_close_time"].iloc[0]
    ts = pd.Timestamp(feat_time).to_pydatetime() if pd.notna(feat_time) else None
    if not all(math.isfinite(v) for v in (close, ef, es)):
        return "neutral", ts, HTF_UNAVAILABLE
    if close > es and ef >= es:
        return "bullish", ts, None
    if close < es and ef <= es:
        return "bearish", ts, None
    return "neutral", ts, None


def aligned_d1agg_regime(d1agg_frame: CandleFrame, decision_dt: datetime, *, slope_bars: int) -> tuple[str, datetime | None, str | None]:
    """D1AGG permissive regime: returns ``not_bearish`` / ``not_bullish`` flags.

    Returns a string in {"not_bearish_only", "not_bullish_only", "both",
    "neither"} describing which directions the D1 regime permits, plus the
    aligned bar time and any block reason.
    """
    htf = _htf_close_frame(d1agg_frame)
    if len(htf) < 52:
        return "neither", None, HTF_UNAVAILABLE
    aligned = align_last_completed(
        pd.DatetimeIndex([decision_dt]), htf, ["close", "ema_fast", "ema_slow"], prefix="d1agg"
    )
    reason = aligned.get("d1agg_blocked_reason", pd.Series([None])).iloc[0]
    if reason:
        return "neither", None, reason
    close = float(aligned["d1agg_close"].iloc[0])
    ef = float(aligned["d1agg_ema_fast"].iloc[0])
    es = float(aligned["d1agg_ema_slow"].iloc[0])
    feat_time = aligned["d1agg_close_time"].iloc[0]
    anchor = pd.Timestamp(feat_time)
    if pd.isna(anchor):
        return "neither", None, HTF_UNAVAILABLE
    if anchor.tzinfo is None:
        anchor = anchor.tz_localize("UTC")
    slope = _slope(htf["ema_fast"], anchor, htf["time"], slope_bars)
    if slope is None or not all(math.isfinite(v) for v in (close, ef, es)):
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
# M15 setup (pullback OR compression)
# --------------------------------------------------------------------------- #
def m15_setup_present(
    *,
    side: Side,
    high: pd.Series,
    low: pd.Series,
    ema_fast: pd.Series,
    pullback_lookback: int,
    donchian_width: float,
    atr_value: float,
    compression_width_atr_max: float,
) -> tuple[bool, bool, bool]:
    """Return ``(setup_present, pullback, compression)`` for the M15 frame.

    pullback (long): an M15 low touched/dipped below EMA20 within the last
    ``pullback_lookback`` completed bars. compression: Donchian width / ATR is
    below the precommitted threshold.
    """
    if len(high) < pullback_lookback + 1:
        return False, False, False
    win_low = low.iloc[-pullback_lookback:]
    win_high = high.iloc[-pullback_lookback:]
    win_ef = ema_fast.iloc[-pullback_lookback:]
    if side == "long":
        pullback = bool((win_low <= win_ef).any())
    else:
        pullback = bool((win_high >= win_ef).any())
    compression = bool(
        math.isfinite(donchian_width)
        and math.isfinite(atr_value)
        and atr_value > 0
        and (donchian_width / atr_value) <= compression_width_atr_max
    )
    return (pullback or compression), pullback, compression


# --------------------------------------------------------------------------- #
# M5 Donchian breakout + stop
# --------------------------------------------------------------------------- #
def m5_breakout_side(
    *, last_close: float, prior_donchian_high: float, prior_donchian_low: float
) -> Side | None:
    """Long if close breaks above the prior channel high, short if below low."""
    if math.isfinite(prior_donchian_high) and last_close > prior_donchian_high:
        return "long"
    if math.isfinite(prior_donchian_low) and last_close < prior_donchian_low:
        return "short"
    return None


def compute_stop(
    *,
    side: Side,
    signal_close: float,
    prior_atr: float,
    atr_multiple: float,
    structure_level: float,
) -> float:
    """Frozen stop: farther of (2.0xATR) and (opposite recent channel side).

    ``structure_level`` is the prior-N-bar Donchian low (long) / high (short).
    """
    d_atr = atr_multiple * prior_atr
    d_struct = abs(signal_close - structure_level)
    stop_distance = max(d_atr, d_struct)
    if side == "long":
        return signal_close - stop_distance
    return signal_close + stop_distance


# --------------------------------------------------------------------------- #
# Deterministic exit resolver: only the stop -> time -> eod priority exists.
# There is intentionally no take-profit, no trail, and no second stop.
# --------------------------------------------------------------------------- #
def resolve_exit(
    *,
    side: Side,
    stop_price: float,
    entry_index: int,
    highs: list[float],
    lows: list[float],
    max_bars_in_trade: int,
) -> tuple[str, int]:
    """Resolve the exit over post-entry M5 bars honoring the frozen priority.

    ``highs``/``lows`` are the full M5 series; bars strictly after
    ``entry_index`` are the holding window. Stop checked intrabar (high/low),
    then the time stop at exactly ``max_bars_in_trade`` bars, else end-of-data.
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
class M5DonchianHtfConfluenceBreakoutStrategy:
    """CAMPAIGN_024 — M5 Donchian + HTF confluence breakout (scaffold only)."""

    name: str = "m5_donchian_htf_confluence_breakout"

    def __init__(self, version: str = "0.1.0-c024") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        return 60

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        validate_c024_data_provenance(ctx.config.get("data_provenance"))
        if ctx.candles.granularity != EXECUTION_TIMEFRAME:
            raise ValueError(
                f"execution frame must be {EXECUTION_TIMEFRAME}, got {ctx.candles.granularity}"
            )
        context_frames = _require_context_frames(ctx.config)
        cfg = ctx.config

        entry_len = int(cfg.get("entry_channel_length", 20))
        atr_len = int(cfg.get("atr_lookback", 14))
        atr_multiple = float(cfg.get("atr_stop_multiple", 2.0))
        structure_lookback = int(cfg.get("structure_lookback", entry_len))
        h1_slope_bars = int(cfg.get("h1_ema_slope_bars", 3))
        d1_slope_bars = int(cfg.get("d1_ema_slope_bars", 3))
        m15_pullback_lookback = int(cfg.get("m15_pullback_lookback", 8))
        m15_comp_donch = int(cfg.get("m15_compression_donchian_lookback", 12))
        m15_comp_atr = int(cfg.get("m15_compression_atr_lookback", 14))
        m15_comp_max = float(cfg.get("m15_compression_width_atr_max", 3.0))
        max_bars = int(cfg.get("max_bars_in_trade", 48))

        df = ctx.candles.completed_only().df
        needed = max(self.warmup_bars_required(), entry_len, structure_lookback, atr_len) + 3
        if len(df) < needed:
            return None

        # One position per instrument.
        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        close = df["close"]
        high = df["high"]
        low = df["low"]
        dc_high = donchian_high(high, entry_len)
        dc_low = donchian_low(low, entry_len)
        atr_series = atr(high, low, close, atr_len)

        last_close = float(close.iloc[-1])
        prior_dc_high = float(dc_high.iloc[-1])
        prior_dc_low = float(dc_low.iloc[-1])
        prior_atr = float(atr_series.iloc[-2])
        if not all(math.isfinite(v) for v in (last_close, prior_dc_high, prior_dc_low, prior_atr)):
            return None
        if prior_atr <= 0:
            return None

        side = m5_breakout_side(
            last_close=last_close,
            prior_donchian_high=prior_dc_high,
            prior_donchian_low=prior_dc_low,
        )
        if side is None:
            return None

        idx_t = df.index[-1]
        decision_dt = pd.Timestamp(idx_t).tz_convert(UTC).to_pydatetime()

        # HTF context (last completed bars only).
        h4_trend, h4_time, h4_block = aligned_h4_trend(context_frames["H4"], decision_dt)
        h1_trend, h1_time, h1_block = aligned_h1_trend(
            context_frames["H1"], decision_dt, slope_bars=h1_slope_bars
        )
        d1_regime, d1_time, d1_block = aligned_d1agg_regime(
            context_frames["D1AGG"], decision_dt, slope_bars=d1_slope_bars
        )
        if h4_block or h1_block or d1_block:
            return None

        wanted: Trend = "bullish" if side == "long" else "bearish"
        if h4_trend != wanted or h1_trend != wanted:
            return None
        if not d1agg_allows(d1_regime, side):
            return None

        # M15 setup (pullback OR compression).
        m15_df = context_frames["M15"].completed_only().df
        if len(m15_df) < max(m15_pullback_lookback, m15_comp_donch, m15_comp_atr) + 2:
            return None
        m15_high = m15_df["high"]
        m15_low = m15_df["low"]
        m15_ema_fast = ema(m15_df["close"].astype(float), 20)
        m15_dc_hi = donchian_high(m15_high, m15_comp_donch)
        m15_dc_lo = donchian_low(m15_low, m15_comp_donch)
        m15_atr = atr(m15_high, m15_low, m15_df["close"], m15_comp_atr)
        donch_width = float(m15_dc_hi.iloc[-1] - m15_dc_lo.iloc[-1])
        m15_atr_val = float(m15_atr.iloc[-1])
        setup, pullback, compression = m15_setup_present(
            side=side,
            high=m15_high,
            low=m15_low,
            ema_fast=m15_ema_fast,
            pullback_lookback=m15_pullback_lookback,
            donchian_width=donch_width,
            atr_value=m15_atr_val,
            compression_width_atr_max=m15_comp_max,
        )
        if not setup:
            return None

        structure_level = (
            float(donchian_low(low, structure_lookback).iloc[-1])
            if side == "long"
            else float(donchian_high(high, structure_lookback).iloc[-1])
        )
        if not math.isfinite(structure_level):
            return None
        stop = compute_stop(
            side=side,
            signal_close=last_close,
            prior_atr=prior_atr,
            atr_multiple=atr_multiple,
            structure_level=structure_level,
        )

        htf_times: dict[str, datetime] = {}
        if d1_time is not None:
            htf_times["d1agg"] = d1_time
        if h4_time is not None:
            htf_times["h4"] = h4_time
        if h1_time is not None:
            htf_times["h1"] = h1_time

        bar_iso = pd.Timestamp(idx_t).tz_convert(UTC).isoformat()
        signal_id = _stable_signal_id(
            self.name, self.version, ctx.instrument.name, EXECUTION_TIMEFRAME, bar_iso, side
        )
        provenance = ctx.config.get("data_provenance") or {}
        donchian_level = prior_dc_high if side == "long" else prior_dc_low

        return Signal(
            signal_id=signal_id,
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe=EXECUTION_TIMEFRAME,
            timestamp=decision_dt,
            side=side,
            entry_intent="market",
            stop_model=f"M5_max(ATR{atr_len}*{atr_multiple},donchian{structure_lookback}_opp)",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="hard_stop_or_time",
            campaign_id=CAMPAIGN_ID,
            decision_time=decision_dt,
            available_data_cutoff=decision_dt,
            source_candle_timestamp=decision_dt,
            htf_feature_times=htf_times or None,
            features={
                "m5_donchian_level": donchian_level,
                "m5_entry_channel_length": entry_len,
                "m15_pullback": pullback,
                "m15_compression": compression,
                "h1_trend": h1_trend,
                "h4_trend": h4_trend,
                "d1agg_regime": d1_regime,
                "atr_at_signal": prior_atr,
                "stop_distance": abs(last_close - stop),
                "structure_level": structure_level,
                "max_bars_in_trade": max_bars,
                "data_provenance": dict(provenance),
                "d1agg_source": provenance.get("d1agg_context"),
            },
            reason=(
                f"M5 Donchian {side} breakout: H4/H1 {wanted}, D1AGG {d1_regime}, "
                f"M15 setup(pullback={pullback},compression={compression})"
            ),
        )


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]

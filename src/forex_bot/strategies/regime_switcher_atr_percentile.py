"""Daily-ATR-percentile regime switcher — ``regime_switcher_atr_percentile 0.1.0-c012``.

CAMPAIGN_012 research candidate (the C3 daily-ATR-percentile regime
switcher selected by the
``research-new-candidate-strategy-discovery-003`` sprint).
**CANDIDATE SCAFFOLD ONLY — not approved for paper / demo / live
trading.** ``configs/approved_strategies.yaml`` remains
``approved: []``; CAMPAIGN_002 remains REJECT; CAMPAIGN_010 remains
REJECT; CAMPAIGN_011 remains REJECT (null-model anchor and only the
null baseline, not a trading candidate).

Hypothesis (binding — see
``docs/research/REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md``
§1): trend persistence on H4 OANDA practice majors is regime-
conditional. The strategy only fires when the prior completed day's
D1AGG ATR-14 is in the top 30 % of the trailing 60 completed days'
distribution (HIGH-VOL regime); direction comes from an H4 close-vs-close
trend sub-signal with an ATR-fraction floor; otherwise no signal.

Entry logic (R1-R8; binding — see
``docs/research/REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md``)
at the latest *completed* bar ``t`` taken from
``ctx.candles.completed_only().df``:

  R1. Warm-up: ``len(df) >= warmup_bars_required()`` (default 500).
  R2. No open position for ``ctx.instrument``.
  R3. Regime gate: compute the trailing D1AGG-ATR-14 percentile using
      only *aggregated* (completed + rollover-safe) daily candles
      emitted by ``aggregate_h4_to_d1``; HIGH-VOL iff
      ``reference >= percentile(trailing_60, threshold)``;
      fail-closed on insufficient or non-finite history.
  R4. Fail-closed on NaN / non-finite / zero ``prior_atr_h4`` (H4
      ATR at index ``-2``).
  R5. Trend sub-signal: ``move = close[t] - close[t-4]``; require
      ``abs(move) >= min_close_move_atr_fraction * prior_atr_h4``;
      side ``long`` if ``move > 0`` else ``short``.
  R6. Spread filter delegated to ``RiskEngine`` (not enforced here).
  R7. Stop placement: ``close[t] -/+ atr_stop_multiple * prior_atr_h4``.
      ``close[t]`` is read ONLY in R5 / R7; never for the regime
      feature.
  R8. Emit ``Signal`` with deterministic ``signal_id`` and
      ``exit_model="time_stop_only"``.

Implementation notes (binding):

* No use of ``random``, ``numpy.random``, ``secrets``, or Python's
  built-in ``hash()`` — the strategy is fully deterministic from
  price data. ``numpy.percentile`` is the only stochastic-looking
  call and it is purely functional.
* No import from ``forex_bot.broker`` / ``forex_bot.execution`` /
  ``forex_bot.loops`` (structural unit tests grep for these).
* No reference to CAMPAIGN_002 / ``trend_following`` / ``Donchian`` /
  ``EMA`` parameters (verified by source-grep).
* No reference to CAMPAIGN_010 / ``session_breakout`` / ``Asian`` /
  ``London`` parameters (verified by source-grep).
* No reference to CAMPAIGN_011 / ``random_entry_anchor`` /
  ``master_seed`` / ``entry_probability_per_bar`` parameters
  (verified by source-grep).
* Strategy module never mutates the strategy config dict.
* ``RegimeSwitcherAtrPercentileStrategy`` exposes no
  approval-shaped field / method.
"""

from __future__ import annotations

import hashlib
import math
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pandas as pd

from forex_bot.domain.candles import Candle
from forex_bot.domain.signals import Signal
from forex_bot.features import d1agg_htf
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import atr

# Back-compat aliases for unit tests.
_wilder_atr_over_d1agg = d1agg_htf.wilder_atr_over_d1agg
_compute_regime = d1agg_htf.compute_regime_label


def _df_to_completed_h4_candle_list(
    df: pd.DataFrame, instrument: str
) -> list[Candle]:
    """Rebuild ``Candle`` objects from a completed-only H4 DataFrame.

    The input ``df`` is the output of ``ctx.candles.completed_only().df``
    — already filtered to ``complete=True``. Each row carries bid_/ask_
    OHLC; we hand those back as ``Decimal`` to the aggregator. The
    aggregator validates that every input has ``granularity == "H4"``
    and ``complete=True``; both are enforced here by construction.

    No-lookahead rail: the function takes only the closed-bar DataFrame
    and the instrument name; it never reads the current incomplete bar.
    """
    candles: list[Candle] = []
    for ts, row in df.iterrows():
        # ``ts`` is the tz-aware UTC bar close timestamp (per CandleFrame
        # construction). Reconstruct a Candle whose ``time`` matches.
        bar_time: datetime = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
        candles.append(
            Candle(
                instrument=instrument,
                granularity="H4",
                time=bar_time,
                complete=True,
                volume=int(row.get("volume", 0) or 0),
                bid_o=_to_decimal(row.get("bid_open")),
                bid_h=_to_decimal(row.get("bid_high")),
                bid_l=_to_decimal(row.get("bid_low")),
                bid_c=_to_decimal(row.get("bid_close")),
                ask_o=_to_decimal(row.get("ask_open")),
                ask_h=_to_decimal(row.get("ask_high")),
                ask_l=_to_decimal(row.get("ask_low")),
                ask_c=_to_decimal(row.get("ask_close")),
            )
        )
    return candles


def _to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        if isinstance(value, float) and not math.isfinite(value):
            return None
    except TypeError:
        return None
    return Decimal(str(value))


class RegimeSwitcherAtrPercentileStrategy:
    """Daily-ATR-percentile regime switcher — research scaffold only.

    CANDIDATE SCAFFOLD ONLY — NOT APPROVED. See
    ``docs/research/REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md``
    for the binding R1-R8 specification, frozen parameters, and
    no-lookahead invariants. The future
    ``research-regime-switcher-atr-percentile-walk-forward-001``
    evidence sprint will run the full walk-forward + financing overlay
    + risk diagnostics + verifier corroboration; only that sprint can
    produce research evidence. Even a clean PASS produces a
    ``RESEARCH_PASS_UNAPPROVED`` candidate awaiting the verifier
    extension + a deliberate human approval action per
    ``STRATEGY_APPROVAL_PROCESS.md``.
    """

    name: str = "regime_switcher_atr_percentile"

    def __init__(self, version: str = "0.1.0-c012") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        # The R3 regime feature needs at least
        # ``daily_atr_lookback + regime_lookback_days + 1 = 75`` D1AGG
        # candles. With 6 well-formed H4 candles per OANDA trading day
        # and weekend gaps, that is roughly 75 × 6 / (5/7) ≈ 630 H4
        # candles in pure-weekday terms — but the aggregator drops
        # incomplete/ambiguous days, so we want a safety buffer.
        # Pinned at 500 per the implementation spec (matches the
        # discovery-003 design); the R3 fail-closed check provides a
        # stricter dynamic guard if the H4 history actually yields
        # fewer than 75 aggregated D1AGG candles.
        return 500

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        atr_len = int(cfg.get("atr_lookback", 14))
        atr_multiple = float(cfg.get("atr_stop_multiple", 2.0))
        timeframe = cfg.get("timeframe", "H4")
        daily_atr_len = int(cfg.get("daily_atr_lookback", 14))
        regime_lookback = int(cfg.get("regime_lookback_days", 60))
        regime_threshold = float(cfg.get("regime_percentile_threshold", 0.70))
        min_move_fraction = float(cfg.get("min_close_move_atr_fraction", 0.25))
        trend_lookback_h4 = int(cfg.get("trend_lookback_h4_bars", 4))

        # R1: sufficient warm-up.
        if len(df) < self.warmup_bars_required():
            return None

        # R2: block re-entry if a position already exists.
        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        # R3: regime gate via D1AGG ATR percentile (shared d1agg_htf helper).
        h4_candles = _df_to_completed_h4_candle_list(df, ctx.instrument.name)
        gate = d1agg_htf.regime_gate_from_h4_candles(
            h4_candles,
            instrument=ctx.instrument.name,
            daily_atr_len=daily_atr_len,
            regime_lookback=regime_lookback,
            regime_threshold=regime_threshold,
        )
        if gate is None:
            return None
        regime_label, reference_atr, pct_value, d1_htf_time, d1agg_count = gate
        if regime_label != "HIGH_VOL":
            return None
        htf_times: dict[str, datetime] = {}
        if d1_htf_time is not None:
            htf_times["d1agg_atr"] = d1_htf_time

        # R4: fail-closed on NaN / non-finite / zero H4 ATR.
        h4_atr_series = atr(df["high"], df["low"], df["close"], atr_len)
        prior_atr_h4 = float(h4_atr_series.iloc[-2])
        if not math.isfinite(prior_atr_h4) or prior_atr_h4 <= 0:
            return None

        # R5: trend sub-signal close[t] vs close[t-4].
        if len(df) < trend_lookback_h4 + 1:
            return None
        last_close = float(df["close"].iloc[-1])
        anchor_close = float(df["close"].iloc[-(trend_lookback_h4 + 1)])
        if not (math.isfinite(last_close) and math.isfinite(anchor_close)):
            return None
        move = last_close - anchor_close
        min_move = min_move_fraction * prior_atr_h4
        if abs(move) < min_move:
            return None
        side: str = "long" if move > 0 else "short"

        # R7: stop placement (close[t] is the stop reference; entry
        # decision was fully determined by R3 / R5 before close[t] was
        # consulted for stop placement).
        if side == "long":
            stop = last_close - atr_multiple * prior_atr_h4
        else:
            stop = last_close + atr_multiple * prior_atr_h4
        if stop == last_close:
            # Defense in depth — unreachable given prior_atr_h4 > 0 in R4.
            return None

        # R8: emit deterministic Signal.
        idx_t = df.index[-1]
        bar_timestamp_iso = pd.Timestamp(idx_t).tz_convert(UTC).isoformat()
        signal_id = _stable_signal_id(
            self.name,
            self.version,
            ctx.instrument.name,
            timeframe,
            bar_timestamp_iso,
            side,
        )

        decision_dt = pd.Timestamp(idx_t).tz_convert(UTC).to_pydatetime()
        return Signal(
            signal_id=signal_id,
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe=timeframe,
            timestamp=decision_dt,
            side=side,  # type: ignore[arg-type]
            entry_intent="market",
            stop_model=f"ATR{atr_len}*{atr_multiple}",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="time_stop_only",
            decision_time=decision_dt,
            htf_feature_times=htf_times or None,
            features={
                "d1agg_htf_time": d1_htf_time.isoformat() if d1_htf_time else None,
                "regime": "HIGH_VOL",
                "d1agg_atr_reference": float(reference_atr),
                "d1agg_atr_percentile_value": float(pct_value),
                "d1agg_count": d1agg_count,
                "trend_move": float(move),
                "min_move_threshold": float(min_move),
                "prior_atr_h4": float(prior_atr_h4),
                "last_close": float(last_close),
                "anchor_close": float(anchor_close),
                "regime_lookback_days": int(regime_lookback),
                "regime_percentile_threshold": float(regime_threshold),
            },
            reason=(
                f"Regime-conditional trend {side}: HIGH_VOL "
                f"(d1agg_atr {reference_atr:.5f} >= "
                f"P{int(regime_threshold * 100)} trailing-{regime_lookback} "
                f"{pct_value:.5f}); trend move {move:+.5f} >= "
                f"{min_move:.5f} threshold"
            ),
        )


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]

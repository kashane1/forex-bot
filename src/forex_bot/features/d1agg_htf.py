"""D1AGG features with shared ``htf_align`` provenance (CAMPAIGN_012 path)."""

from __future__ import annotations

import math
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import numpy as np
import pandas as pd

from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1
from forex_bot.domain.candles import Candle
from forex_bot.features.htf_align import align_last_completed
from forex_bot.strategies.indicators import atr


def wilder_atr_over_d1agg(d1_candles: list[Candle], length: int) -> list[float]:
    """Wilder ATR over D1AGG mid OHLC candles."""
    if length <= 0:
        raise ValueError("daily_atr_lookback must be > 0")
    rows: list[dict[str, float]] = []
    for c in d1_candles:
        mid_h = _mid(c.bid_h, c.ask_h)
        mid_l = _mid(c.bid_l, c.ask_l)
        mid_c = _mid(c.bid_c, c.ask_c)
        rows.append({"high": mid_h, "low": mid_l, "close": mid_c})
    if not rows:
        return []
    frame = pd.DataFrame(rows)
    series = atr(frame["high"], frame["low"], frame["close"], length)
    return [float(v) for v in series.tolist()]


def compute_regime_label(
    d1_atr_series: list[float],
    *,
    lookback_days: int,
    percentile_threshold: float,
) -> tuple[str, float, float] | None:
    """HIGH_VOL vs LOW_VOL from trailing D1AGG ATR window (R3 semantics)."""
    if lookback_days <= 0 or not (0.0 < percentile_threshold < 1.0):
        return None
    if len(d1_atr_series) < lookback_days + 1:
        return None
    reference = d1_atr_series[-1]
    if not math.isfinite(reference) or reference <= 0:
        return None
    trailing = d1_atr_series[-(lookback_days + 1) : -1]
    if len(trailing) != lookback_days:
        return None
    if not all(math.isfinite(v) and v > 0 for v in trailing):
        return None
    pct_value = float(np.percentile(trailing, percentile_threshold * 100))
    if not math.isfinite(pct_value):
        return None
    label = "HIGH_VOL" if reference >= pct_value else "LOW_VOL"
    return label, float(reference), pct_value


def d1agg_htf_frame(d1_candles: list[Candle], daily_atr_len: int) -> pd.DataFrame:
    """Build HTF frame with ATR series aligned to D1AGG bar close times."""
    atr_series = wilder_atr_over_d1agg(d1_candles, daily_atr_len)
    rows: list[dict[str, Any]] = []
    for candle, atr_val in zip(d1_candles, atr_series, strict=True):
        rows.append(
            {
                "time": candle.time,
                "complete": True,
                "atr": atr_val,
            }
        )
    return pd.DataFrame(rows)


def regime_gate_from_h4_candles(
    h4_candles: list[Candle],
    *,
    instrument: str,
    daily_atr_len: int,
    regime_lookback: int,
    regime_threshold: float,
) -> tuple[str, float, float, datetime | None, int] | None:
    """Regime gate using D1AGG aggregation (production-equivalent path)."""
    try:
        agg = aggregate_h4_to_d1(h4_candles, instrument=instrument)
    except ValueError:
        return None
    d1_candles = agg.candles
    if len(d1_candles) < daily_atr_len + regime_lookback + 1:
        return None
    d1_atr_series = wilder_atr_over_d1agg(d1_candles, daily_atr_len)
    regime_result = compute_regime_label(
        d1_atr_series,
        lookback_days=regime_lookback,
        percentile_threshold=regime_threshold,
    )
    if regime_result is None:
        return None
    label, reference, pct = regime_result
    last_d1_time = d1_candles[-1].time if d1_candles else None
    return label, reference, pct, last_d1_time, len(d1_candles)


def aligned_d1_atr_at_decision(
    h4_candles: list[Candle],
    decision_time: datetime,
    *,
    instrument: str,
    daily_atr_len: int,
) -> tuple[float | None, datetime | None, str | None]:
    """Last completed D1AGG ATR at ``decision_time`` via ``htf_align``."""
    try:
        agg = aggregate_h4_to_d1(h4_candles, instrument=instrument)
    except ValueError:
        return None, None, "HTF_UNAVAILABLE"
    d1_candles = agg.candles
    if not d1_candles:
        return None, None, "HTF_UNAVAILABLE"
    htf = d1agg_htf_frame(d1_candles, daily_atr_len)
    decisions = pd.DatetimeIndex([decision_time])
    aligned = align_last_completed(decisions, htf, ["atr"], prefix="d1agg")
    atr_val = aligned["d1agg_atr"].iloc[0]
    atr_time = aligned["d1agg_atr_time"].iloc[0]
    reason = aligned["d1agg_blocked_reason"].iloc[0]
    if pd.isna(atr_val):
        return None, None, reason
    ts = pd.Timestamp(atr_time).to_pydatetime() if pd.notna(atr_time) else None
    return float(atr_val), ts, reason


def _mid(bid: Decimal | None, ask: Decimal | None) -> float:
    if bid is None or ask is None:
        return float("nan")
    return float((bid + ask) / 2)

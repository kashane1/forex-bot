"""Synthetic weekly volatility / compression features from deduped H4 candles.

CAMPAIGN_017 research utilities. No native D1/W1 data. Weekly boundaries
are Monday 00:00 UTC (ISO week start). Incomplete current weeks are
excluded from compression labeling and breakout range selection.
"""

from __future__ import annotations

import math
from collections.abc import Iterable

import pandas as pd

from forex_bot.features.weekly_momentum import week_id, week_start_monday_utc


def aggregate_h4_to_weekly_ohlc(
    timestamps: pd.DatetimeIndex | Iterable[pd.Timestamp],
    opens: pd.Series,
    highs: pd.Series,
    lows: pd.Series,
    closes: pd.Series,
) -> pd.DataFrame:
    """Build weekly OHLC from H4 bars grouped by Monday-start UTC week.

    Returns a DataFrame indexed by week-start timestamps (UTC) with
    columns ``open``, ``high``, ``low``, ``close``, ``true_range``.
    """
    idx = pd.DatetimeIndex(timestamps)
    n = len(idx)
    if not (len(opens) == len(highs) == len(lows) == len(closes) == n):
        raise ValueError("OHLC series length mismatch")
    if n == 0:
        return pd.DataFrame(
            columns=["open", "high", "low", "close", "true_range"],
        )
    if not idx.is_monotonic_increasing:
        raise ValueError("timestamps must be monotonic increasing")

    frame = pd.DataFrame(
        {
            "open": opens.values,
            "high": highs.values,
            "low": lows.values,
            "close": closes.values,
        },
        index=idx,
    )
    week_starts = frame.index.map(week_start_monday_utc)
    grouped = frame.groupby(week_starts).agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
    )
    grouped.index = pd.DatetimeIndex(grouped.index, tz="UTC")
    grouped["true_range"] = grouped["high"] - grouped["low"]
    return grouped.sort_index()


def _percentile_threshold(values: pd.Series, percentile: float) -> float:
    if values.empty:
        return float("nan")
    return float(values.quantile(percentile / 100.0))


def label_weekly_compression(
    weekly: pd.DataFrame,
    *,
    compression_lookback_weeks: int,
    compression_percentile_threshold: float,
) -> pd.DataFrame:
    """Add ``is_compressed`` and ``compression_percentile_value`` columns.

    A completed week is compressed when its true range is at or below
    the ``compression_percentile_threshold`` percentile of the trailing
    ``compression_lookback_weeks`` weekly true-range values (inclusive).
    Weeks with fewer than ``compression_lookback_weeks`` of history are
    never labeled compressed.
    """
    if weekly.empty:
        out = weekly.copy()
        out["is_compressed"] = pd.Series(dtype=bool)
        out["compression_percentile_value"] = pd.Series(dtype=float)
        return out

    out = weekly.copy()
    flags: list[bool] = []
    pct_vals: list[float] = []
    tr_series = out["true_range"]
    for i in range(len(out)):
        if i + 1 < compression_lookback_weeks:
            flags.append(False)
            pct_vals.append(float("nan"))
            continue
        window = tr_series.iloc[i + 1 - compression_lookback_weeks : i + 1]
        if window.isna().any() or len(window) < compression_lookback_weeks:
            flags.append(False)
            pct_vals.append(float("nan"))
            continue
        threshold = _percentile_threshold(window, compression_percentile_threshold)
        current_tr = float(tr_series.iloc[i])
        pct_vals.append(threshold)
        flags.append(
            math.isfinite(current_tr)
            and math.isfinite(threshold)
            and current_tr <= threshold
        )
    out["is_compressed"] = flags
    out["compression_percentile_value"] = pct_vals
    return out


def completed_weeks_before(
    weekly: pd.DataFrame,
    as_of_ts: pd.Timestamp,
) -> pd.DataFrame:
    """Return only weeks strictly before the week containing ``as_of_ts``."""
    if weekly.empty:
        return weekly.copy()
    current_week = week_start_monday_utc(as_of_ts)
    return weekly.loc[weekly.index < current_week].copy()


def latest_completed_compressed_week(
    weekly_labeled: pd.DataFrame,
    as_of_ts: pd.Timestamp,
) -> dict[str, object] | None:
    """Most recent completed compressed week usable for breakout at ``as_of_ts``.

    Returns None if no completed compressed week exists. The returned week
    must be fully complete (strictly before the current ISO week).
    """
    completed = completed_weeks_before(weekly_labeled, as_of_ts)
    if completed.empty:
        return None
    compressed = completed[completed["is_compressed"]]
    if compressed.empty:
        return None
    row = compressed.iloc[-1]
    ws = compressed.index[-1]
    we = ws + pd.Timedelta(days=7)
    return {
        "compressed_week_start": ws,
        "compressed_week_end": we,
        "compressed_week_high": float(row["high"]),
        "compressed_week_low": float(row["low"]),
        "compression_percentile": float(row["compression_percentile_value"]),
        "weekly_true_range": float(row["true_range"]),
        "is_compressed": bool(row["is_compressed"]),
    }


def breakout_already_consumed(
    *,
    timestamps: pd.DatetimeIndex,
    closes: pd.Series,
    week_end: pd.Timestamp,
    current_index: pd.Timestamp,
    compressed_high: float,
    compressed_low: float,
    buffer: float,
) -> bool:
    """True if any prior completed bar after ``week_end`` already broke out."""
    mask = (timestamps > week_end) & (timestamps < current_index)
    if not mask.any():
        return False
    prior_closes = closes.loc[mask]
    long_break = (prior_closes > compressed_high + buffer).any()
    short_break = (prior_closes < compressed_low - buffer).any()
    return bool(long_break or short_break)


def compute_h4_atr_buffer(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    atr_lookback: int,
    breakout_buffer_atr_multiple: float,
) -> tuple[float | None, float | None]:
    """Return (atr_h4, breakout_buffer) at the last index without future bars."""
    from forex_bot.strategies.indicators import atr

    atr_series = atr(high, low, close, atr_lookback)
    if atr_series.empty:
        return None, None
    last_atr = float(atr_series.iloc[-1])
    if not math.isfinite(last_atr) or last_atr <= 0:
        return None, None
    return last_atr, breakout_buffer_atr_multiple * last_atr


__all__ = [
    "aggregate_h4_to_weekly_ohlc",
    "breakout_already_consumed",
    "completed_weeks_before",
    "compute_h4_atr_buffer",
    "label_weekly_compression",
    "latest_completed_compressed_week",
    "week_id",
    "week_start_monday_utc",
]

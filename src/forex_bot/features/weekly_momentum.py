"""Synthetic weekly momentum features from deduped H4 candles.

CAMPAIGN_016 research utilities. No native D1/W1 data. All weekly
boundaries are Monday 00:00 UTC (ISO week start). Incomplete current
weeks are excluded from momentum lookback calculations.
"""

from __future__ import annotations

import math
from collections.abc import Iterable

import numpy as np
import pandas as pd

VOLATILITY_FLOOR_DEFAULT = 1.0e-8


def week_start_monday_utc(ts: pd.Timestamp) -> pd.Timestamp:
    """Monday 00:00 UTC for the week containing ``ts``."""
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    weekday = ts.weekday()
    return (ts - pd.Timedelta(days=weekday)).normalize()


def week_id(ts: pd.Timestamp) -> tuple[int, int]:
    """Deterministic (iso_year, iso_week) key for Monday-start weeks."""
    ws = week_start_monday_utc(ts)
    iso = ws.isocalendar()
    return (int(iso.year), int(iso.week))


def aggregate_h4_to_weekly_closes(
    timestamps: pd.DatetimeIndex | Iterable[pd.Timestamp],
    closes: pd.Series,
) -> pd.Series:
    """Last H4 close per Monday-start UTC week.

    ``timestamps`` and ``closes`` must be aligned, monotonic, and equal
    length. Returns a series indexed by week-start timestamps (UTC).
    """
    if len(closes) == 0:
        return pd.Series(dtype=float)
    idx = pd.DatetimeIndex(timestamps)
    if len(idx) != len(closes):
        raise ValueError("timestamps and closes length mismatch")
    frame = pd.DataFrame({"close": closes.values}, index=idx)
    if not frame.index.is_monotonic_increasing:
        raise ValueError("timestamps must be monotonic increasing")
    week_starts = frame.index.map(week_start_monday_utc)
    grouped = frame.groupby(week_starts)["close"].last()
    grouped.index = pd.DatetimeIndex(grouped.index, tz="UTC")
    return grouped.sort_index()


def is_rebalance_bar(
    bar_ts: pd.Timestamp,
    prior_bar_ts: pd.Timestamp | None,
) -> bool:
    """True on the first H4 bar of a new Monday-start UTC week."""
    if prior_bar_ts is None:
        return False
    return week_id(bar_ts) != week_id(prior_bar_ts)


def _weekly_log_returns(weekly_closes: pd.Series) -> pd.Series:
    if len(weekly_closes) < 2:
        return pd.Series(dtype=float)
    prev = weekly_closes.shift(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = weekly_closes / prev
    returns = np.log(ratio)
    returns = returns.replace([np.inf, -np.inf], np.nan)
    return returns.dropna()


def weekly_return_over_weeks(
    weekly_closes: pd.Series,
    lookback_weeks: int,
    *,
    as_of_week_exclusive: pd.Timestamp | None = None,
) -> float | None:
    """Log return over ``lookback_weeks`` complete weeks ending before
    ``as_of_week_exclusive`` (default: exclude incomplete trailing week)."""
    if lookback_weeks < 1 or len(weekly_closes) < lookback_weeks + 1:
        return None
    usable = weekly_closes.sort_index()
    if as_of_week_exclusive is not None:
        ws = week_start_monday_utc(as_of_week_exclusive)
        usable = usable.loc[usable.index < ws]
    if len(usable) < lookback_weeks + 1:
        return None
    end = float(usable.iloc[-1])
    start = float(usable.iloc[-1 - lookback_weeks])
    if not (math.isfinite(end) and math.isfinite(start) and start > 0 and end > 0):
        return None
    return math.log(end / start)


def weekly_volatility(
    weekly_closes: pd.Series,
    lookback_weeks: int,
    *,
    as_of_week_exclusive: pd.Timestamp | None = None,
    volatility_floor: float = VOLATILITY_FLOOR_DEFAULT,
) -> float | None:
    """Sample stdev of weekly log returns over the last ``lookback_weeks``
    complete weeks. Returns None if insufficient data or vol <= floor."""
    usable = weekly_closes.sort_index()
    if as_of_week_exclusive is not None:
        ws = week_start_monday_utc(as_of_week_exclusive)
        usable = usable.loc[usable.index < ws]
    rets = _weekly_log_returns(usable)
    if len(rets) < lookback_weeks:
        return None
    window = rets.iloc[-lookback_weeks:]
    if window.isna().any():
        return None
    vol = float(window.std(ddof=1)) if len(window) > 1 else float(window.std())
    if not math.isfinite(vol) or vol <= volatility_floor:
        return None
    return vol


def vol_adjusted_momentum_score(
    weekly_closes: pd.Series,
    *,
    fast_weeks: int,
    slow_weeks: int,
    vol_weeks: int,
    blend_fast: float = 0.5,
    blend_slow: float = 0.5,
    as_of_week_exclusive: pd.Timestamp | None = None,
    volatility_floor: float = VOLATILITY_FLOOR_DEFAULT,
) -> dict[str, float | None]:
    """Compute fast/slow vol-adjusted momentum and blended score."""
    fast_ret = weekly_return_over_weeks(
        weekly_closes, fast_weeks, as_of_week_exclusive=as_of_week_exclusive,
    )
    slow_ret = weekly_return_over_weeks(
        weekly_closes, slow_weeks, as_of_week_exclusive=as_of_week_exclusive,
    )
    vol = weekly_volatility(
        weekly_closes,
        vol_weeks,
        as_of_week_exclusive=as_of_week_exclusive,
        volatility_floor=volatility_floor,
    )
    fast_adj: float | None = None
    slow_adj: float | None = None
    score: float | None = None
    if fast_ret is not None and vol is not None:
        fast_adj = fast_ret / vol
    if slow_ret is not None and vol is not None:
        slow_adj = slow_ret / vol
    if fast_adj is not None and slow_adj is not None:
        score = blend_fast * fast_adj + blend_slow * slow_adj
        if not math.isfinite(score):
            score = None
    return {
        "fast_return": fast_ret,
        "slow_return": slow_ret,
        "volatility": vol,
        "fast_return_vol_adjusted": fast_adj,
        "slow_return_vol_adjusted": slow_adj,
        "score": score,
    }


def rank_pairs_by_score(
    pair_scores: dict[str, float],
) -> list[tuple[str, float, int]]:
    """Rank pairs descending by score; alphabetic tiebreak.

    Returns list of ``(pair, score, rank)`` with rank 1 = best.
    """
    items = sorted(
        pair_scores.items(),
        key=lambda kv: (-kv[1], kv[0]),
    )
    return [(pair, score, rank + 1) for rank, (pair, score) in enumerate(items)]

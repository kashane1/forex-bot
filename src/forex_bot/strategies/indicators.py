"""Indicator helpers. Pure functions over numpy/pandas to ease testing.

All inputs are assumed to be *completed* candles. Strategies that explicitly
need intrabar logic must opt in elsewhere; this module never peeks ahead.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def ema(series: pd.Series, length: int) -> pd.Series:
    if length <= 0:
        raise ValueError("ema length must be > 0")
    return series.ewm(span=length, adjust=False, min_periods=length).mean()


def atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    if length <= 0:
        raise ValueError("atr length must be > 0")
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()


def donchian_high(high: pd.Series, length: int) -> pd.Series:
    """High of the previous `length` *completed* bars (not including the current bar)."""
    if length <= 0:
        raise ValueError("donchian length must be > 0")
    return high.shift(1).rolling(window=length, min_periods=length).max()


def donchian_low(low: pd.Series, length: int) -> pd.Series:
    if length <= 0:
        raise ValueError("donchian length must be > 0")
    return low.shift(1).rolling(window=length, min_periods=length).min()


def rsi(close: pd.Series, length: int = 14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0.0)
    down = (-delta).clip(lower=0.0)
    roll_up = up.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
    roll_down = down.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
    rs = roll_up / roll_down.replace(0, np.nan)
    return (100 - (100 / (1 + rs))).fillna(50.0)


def zscore(series: pd.Series, length: int) -> pd.Series:
    mean = series.rolling(window=length, min_periods=length).mean()
    std = series.rolling(window=length, min_periods=length).std(ddof=0)
    return (series - mean) / std.replace(0, np.nan)

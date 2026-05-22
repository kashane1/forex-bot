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


def adx(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    length: int = 14,
) -> pd.Series:
    """Wilder's Average Directional Index.

    ADX measures *trend strength* regardless of direction. The standard
    interpretation: ADX > 25 = a trend is present; ADX < 20 = range/chop.

    Implementation follows Wilder (1978):
      1. +DM / -DM from successive highs / lows.
      2. True Range.
      3. Wilder-smooth (EMA with alpha = 1/length) +DM, -DM, TR.
      4. +DI = 100 * smoothed(+DM) / smoothed(TR); -DI similarly.
      5. DX = 100 * |+DI - -DI| / (+DI + -DI).
      6. ADX = Wilder-smooth(DX).

    Like every indicator in this module it consumes *completed* candles
    only and never peeks ahead — each output value depends only on bars
    up to and including its own index.
    """
    if length <= 0:
        raise ValueError("adx length must be > 0")

    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = pd.Series(
        np.where((up_move > down_move) & (up_move > 0), up_move, 0.0),
        index=high.index,
    )
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0), down_move, 0.0),
        index=high.index,
    )

    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    alpha = 1.0 / length
    atr_smooth = tr.ewm(alpha=alpha, adjust=False, min_periods=length).mean()
    plus_dm_smooth = plus_dm.ewm(alpha=alpha, adjust=False, min_periods=length).mean()
    minus_dm_smooth = minus_dm.ewm(alpha=alpha, adjust=False, min_periods=length).mean()

    plus_di = 100.0 * plus_dm_smooth / atr_smooth.replace(0, np.nan)
    minus_di = 100.0 * minus_dm_smooth / atr_smooth.replace(0, np.nan)

    di_sum = (plus_di + minus_di).replace(0, np.nan)
    dx = 100.0 * (plus_di - minus_di).abs() / di_sum
    return dx.ewm(alpha=alpha, adjust=False, min_periods=length).mean()

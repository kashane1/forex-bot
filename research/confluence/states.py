"""Deterministic timeframe state calculations."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from forex_bot.strategies.indicators import adx, atr, ema, zscore  # noqa: E402
from research.confluence.models import H4Setup, TrendState  # noqa: E402


def resample_h4_to_d1(h4: pd.DataFrame) -> pd.DataFrame:
    """Aggregate H4 mid OHLC to synthetic D1 (UTC calendar day)."""
    if h4.empty:
        return h4.copy()
    o = h4["open"].resample("1D").first()
    h = h4["high"].resample("1D").max()
    low = h4["low"].resample("1D").min()
    c = h4["close"].resample("1D").last()
    out = pd.DataFrame({"open": o, "high": h, "low": low, "close": c}).dropna(how="all")
    return out


def aggregate_d1_from_h4(h4: pd.DataFrame, *, weeks: int = 5) -> pd.DataFrame:
    """Synthetic W1 from D1 resample."""
    d1 = resample_h4_to_d1(h4)
    if d1.empty:
        return d1
    return d1.resample(f"{weeks}D").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    ).dropna(how="all")


def compute_timeframe_state(
    frame: pd.DataFrame,
    *,
    ema_length: int = 50,
    adx_length: int = 14,
    adx_range_max: float = 20.0,
    slope_lookback: int = 5,
) -> TrendState:
    """Classify latest bar as trend_up, trend_down, range, or unknown."""
    if len(frame) < max(ema_length, adx_length) + slope_lookback:
        return "unknown"
    close = frame["close"]
    ema_series = ema(close, ema_length)
    adx_series = adx(frame["high"], frame["low"], close, length=adx_length)
    latest_adx = float(adx_series.iloc[-1])
    latest_close = float(close.iloc[-1])
    latest_ema = float(ema_series.iloc[-1])
    if pd.isna(latest_adx) or pd.isna(latest_ema):
        return "unknown"
    if latest_adx < adx_range_max:
        return "range"
    ema_slope = float(ema_series.iloc[-1] - ema_series.iloc[-1 - slope_lookback])
    if latest_close > latest_ema and ema_slope > 0:
        return "trend_up"
    if latest_close < latest_ema and ema_slope < 0:
        return "trend_down"
    return "range"


def compute_h4_setup(
    frame: pd.DataFrame,
    *,
    zscore_length: int = 20,
    zscore_threshold: float = 2.0,
    adx_length: int = 14,
    adx_range_max: float = 20.0,
) -> H4Setup:
    if len(frame) < zscore_length + 5:
        return "no_setup"
    close = frame["close"]
    zs = zscore(close, zscore_length)
    adx_series = adx(frame["high"], frame["low"], close, length=adx_length)
    latest_z = float(zs.iloc[-1]) if pd.notna(zs.iloc[-1]) else 0.0
    latest_adx = float(adx_series.iloc[-1]) if pd.notna(adx_series.iloc[-1]) else 0.0
    if latest_adx < adx_range_max and abs(latest_z) >= zscore_threshold:
        return "mean_reversion"
    if latest_adx >= adx_range_max:
        atr_series = atr(frame["high"], frame["low"], close, length=14)
        if len(frame) >= 25:
            recent_high = float(frame["high"].iloc[-21:-1].max())
            recent_low = float(frame["low"].iloc[-21:-1].min())
            if float(close.iloc[-1]) > recent_high:
                return "breakout"
            if float(close.iloc[-1]) < recent_low:
                return "breakout"
        if pd.notna(atr_series.iloc[-1]):
            return "pullback"
    return "no_setup"

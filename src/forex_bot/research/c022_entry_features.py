"""Read-only reconstruction of C022 entry-time features from materialized frames.

CAMPAIGN_022 persisted only the *categorical* H4 bias / H1-pullback-holds flags
to its signals, not the numeric decision-time indicator values. For a
winner/loser feature-separation study we reconstruct those numerics from the same
materialized M15/H1/H4 frames the campaign ran on, at each trade's **decision
bar** (the completed M15 bar that produced the signal — one M15 bar before the
``next_bar_open`` fill recorded as ``entry_time``).

This module changes no strategy logic, no parameter, and no verdict. It is a
faithful, **lookahead-safe approximation**: every indicator is causal and is read
at the last bar with ``time <= decision_time`` (HTF via ``align_last_completed``,
exactly as the strategy does). No bar at or after the fill is used for any
feature. The reconstructed ``recon_h4_bias`` is exported so the build step can
verify it agrees with the trade side (a built-in alignment sanity check).

Directional distance/slope features are **trend-aligned** (signed by side):
positive means "in the H4 trend direction", so long and short trades are
comparable. Normalizations are in ATR units of the same timeframe.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd

from forex_bot.domain.candles import CandleFrame
from forex_bot.features.htf_align import align_last_completed
from forex_bot.strategies.indicators import adx, atr, ema, rsi

__all__ = ["M15_BAR", "C022FeatureParams", "reconstruct_entry_features"]

M15_BAR = timedelta(minutes=15)


@dataclass(frozen=True)
class C022FeatureParams:
    """Frozen C022 indicator lengths (see configs/campaign_022_*.yaml)."""

    h4_ema_fast: int = 20
    h4_ema_slow: int = 50
    h4_ema_slope_bars: int = 3
    h4_adx_lookback: int = 14
    h1_ema_fast: int = 20
    h1_ema_slow: int = 50
    h1_rsi_lookback: int = 14
    h1_pullback_lookback: int = 6
    atr_lookback: int = 14
    m15_adx_lookback: int = 14


def _series(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.Series(df[col].to_numpy(dtype=float))


def _indicator_frame(
    frame: CandleFrame,
    *,
    ema_fast_len: int,
    ema_slow_len: int,
    atr_len: int,
    adx_len: int | None = None,
    rsi_len: int | None = None,
) -> pd.DataFrame:
    """Completed-bar frame with causal indicators, plus a ``time`` column for
    ``align_last_completed``. Mirrors the strategy's ``_htf_indicator_frame`` and
    adds ATR (for ATR-normalized distances)."""
    df = frame.completed_only().df
    if df.empty:
        return pd.DataFrame()
    close, high, low = _series(df, "close"), _series(df, "high"), _series(df, "low")
    out = pd.DataFrame(
        {
            "time": pd.to_datetime(df.index, utc=True).to_numpy(),
            "complete": True,
            "open": _series(df, "open").to_numpy(),
            "close": close.to_numpy(),
            "high": high.to_numpy(),
            "low": low.to_numpy(),
            "ema_fast": ema(close, ema_fast_len).to_numpy(),
            "ema_slow": ema(close, ema_slow_len).to_numpy(),
            "atr": atr(high, low, close, atr_len).to_numpy(),
        }
    )
    if adx_len is not None:
        out["adx"] = adx(high, low, close, adx_len).to_numpy()
    if rsi_len is not None:
        out["rsi"] = rsi(close, rsi_len, warmup_policy="nan").to_numpy()
    return out


def _finite(x: object) -> float | None:
    try:
        v = float(x)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _safe_div(num: float | None, den: float | None) -> float | None:
    if num is None or den is None or den == 0:
        return None
    return num / den


def reconstruct_entry_features(
    *,
    m15: CandleFrame,
    h1: CandleFrame,
    h4: CandleFrame,
    decision_time: datetime,
    side: str,
    params: C022FeatureParams = C022FeatureParams(),
) -> dict[str, object]:
    """Reconstruct numeric entry-time features at ``decision_time`` for one trade.

    ``decision_time`` is the decision-bar timestamp (``entry_time - one M15 bar``).
    ``side`` is 'long'/'short'. Returns a flat dict; any unrecoverable value is
    ``None`` (never fabricated). Distance/slope features are trend-aligned.
    """
    s = side.strip().lower()
    sign = 1.0 if s in {"long", "buy"} else -1.0
    dt = pd.Timestamp(decision_time)
    dt = dt.tz_localize("UTC") if dt.tzinfo is None else dt.tz_convert("UTC")
    feat: dict[str, object] = {}

    # ---- M15 decision bar -------------------------------------------------
    m15df = m15.completed_only().df
    m15_idx = pd.to_datetime(m15df.index, utc=True)
    m15_sel = m15df.loc[m15_idx <= dt]
    if not m15_sel.empty:
        close = _series(m15df, "close")
        high = _series(m15df, "high")
        low = _series(m15df, "low")
        opn = _series(m15df, "open")
        ema20 = ema(close, params.h4_ema_fast)  # 20
        ema50 = ema(close, params.h4_ema_slow)  # 50
        a = atr(high, low, close, params.atr_lookback)
        adx_s = adx(high, low, close, params.m15_adx_lookback)
        i = len(m15_sel) - 1  # decision bar positional index in full frame
        c = _finite(close.iloc[i])
        o = _finite(opn.iloc[i])
        e20 = _finite(ema20.iloc[i])
        e50 = _finite(ema50.iloc[i])
        atr_m15 = _finite(a.iloc[i])
        feat["atr_at_entry"] = atr_m15
        feat["m15_adx_at_entry"] = _finite(adx_s.iloc[i])
        feat["m15_reclaim_distance_atr"] = _safe_div(
            sign * (c - e20) if (c is not None and e20 is not None) else None, atr_m15
        )
        feat["m15_body_atr"] = _safe_div(
            abs(c - o) if (c is not None and o is not None) else None, atr_m15
        )
        feat["m15_close_dist_ema50_atr"] = _safe_div(
            sign * (c - e50) if (c is not None and e50 is not None) else None, atr_m15
        )
    else:
        for k in (
            "atr_at_entry", "m15_adx_at_entry", "m15_reclaim_distance_atr",
            "m15_body_atr", "m15_close_dist_ema50_atr",
        ):
            feat[k] = None

    # ---- H4 regime --------------------------------------------------------
    h4f = _indicator_frame(
        h4, ema_fast_len=params.h4_ema_fast, ema_slow_len=params.h4_ema_slow,
        atr_len=params.atr_lookback, adx_len=params.h4_adx_lookback,
    )
    feat.update(_h4_features(h4f, dt, sign, params))

    # ---- H1 pullback ------------------------------------------------------
    h1f = _indicator_frame(
        h1, ema_fast_len=params.h1_ema_fast, ema_slow_len=params.h1_ema_slow,
        atr_len=params.atr_lookback, rsi_len=params.h1_rsi_lookback,
    )
    feat.update(_h1_features(h1f, dt, sign, s, params))

    return feat


def _aligned_time(h4f: pd.DataFrame, dt: pd.Timestamp, prefix: str) -> pd.Timestamp | None:
    aligned = align_last_completed(
        pd.DatetimeIndex([dt]), h4f, ["close"], prefix=prefix
    )
    raw = aligned[f"{prefix}_close_time"].iloc[0]
    ts = pd.Timestamp(raw)
    if pd.isna(ts):
        return None
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


def _h4_features(
    h4f: pd.DataFrame, dt: pd.Timestamp, sign: float, params: C022FeatureParams
) -> dict[str, object]:
    keys = (
        "h4_adx_at_entry", "h4_bias_score", "h4_ema_slope_atr",
        "h4_close_dist_ema50_atr", "recon_h4_bias", "h4_feature_time",
    )
    if h4f.empty:
        return dict.fromkeys(keys, None)
    feat_time = _aligned_time(h4f, dt, "h4")
    if feat_time is None:
        return dict.fromkeys(keys, None)
    times = pd.to_datetime(h4f["time"], utc=True)
    hist = h4f.loc[times <= feat_time]
    if hist.empty:
        return dict.fromkeys(keys, None)
    row = hist.iloc[-1]
    close = _finite(row["close"])
    ema_fast = _finite(row["ema_fast"])
    ema_slow = _finite(row["ema_slow"])
    adx_val = _finite(row["adx"])
    atr_h4 = _finite(row["atr"])

    slope_bars = params.h4_ema_slope_bars
    slope = None
    slow_hist = hist["ema_slow"].dropna()
    if len(slow_hist) >= slope_bars + 1:
        slope = _finite(slow_hist.iloc[-1] - slow_hist.iloc[-(slope_bars + 1)])

    bias_score = None
    recon_bias = None
    if None not in (close, ema_fast, ema_slow) and slope is not None:
        bull = int(close > ema_slow) + int(ema_fast > ema_slow) + int(slope > 0)
        bear = int(close < ema_slow) + int(ema_fast < ema_slow) + int(slope < 0)
        bias_score = bull - bear
        recon_bias = "bullish" if bull >= 2 else ("bearish" if bear >= 2 else "neutral")

    return {
        "h4_adx_at_entry": adx_val,
        "h4_bias_score": bias_score,
        "h4_ema_slope_atr": _safe_div(sign * slope if slope is not None else None, atr_h4),
        "h4_close_dist_ema50_atr": _safe_div(
            sign * (close - ema_slow) if None not in (close, ema_slow) else None, atr_h4
        ),
        "recon_h4_bias": recon_bias,
        "h4_feature_time": feat_time.isoformat() if feat_time is not None else None,
    }


def _h1_features(
    h1f: pd.DataFrame, dt: pd.Timestamp, sign: float, side: str, params: C022FeatureParams
) -> dict[str, object]:
    keys = (
        "h1_rsi_at_entry", "h1_pullback_depth_atr", "h1_close_dist_ema50_atr",
        "h1_feature_time",
    )
    if h1f.empty:
        return dict.fromkeys(keys, None)
    feat_time = _aligned_time(h1f, dt, "h1")
    if feat_time is None:
        return dict.fromkeys(keys, None)
    times = pd.to_datetime(h1f["time"], utc=True)
    hist = h1f.loc[times <= feat_time]
    if hist.empty:
        return dict.fromkeys(keys, None)
    row = hist.iloc[-1]
    close = _finite(row["close"])
    ema_slow = _finite(row["ema_slow"])
    atr_h1 = _finite(row["atr"])
    rsi_val = _finite(row["rsi"])

    lookback = params.h1_pullback_lookback
    win = hist.iloc[-lookback:] if len(hist) >= lookback else hist
    depth = None
    if atr_h1:
        if side in {"long", "buy"}:
            dips = (win["ema_fast"] - win["low"]).dropna()
            if not dips.empty:
                depth = _safe_div(_finite(dips.max()), atr_h1)
        else:
            dips = (win["high"] - win["ema_fast"]).dropna()
            if not dips.empty:
                depth = _safe_div(_finite(dips.max()), atr_h1)

    return {
        "h1_rsi_at_entry": rsi_val,
        "h1_pullback_depth_atr": depth,
        "h1_close_dist_ema50_atr": _safe_div(
            sign * (close - ema_slow) if None not in (close, ema_slow) else None, atr_h1
        ),
        "h1_feature_time": feat_time.isoformat() if feat_time is not None else None,
    }

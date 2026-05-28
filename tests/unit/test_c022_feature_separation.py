"""Tests for C022 feature-separation labels and entry-feature reconstruction."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd

from forex_bot.domain.candles import CandleFrame
from forex_bot.research.c022_entry_features import (
    C022FeatureParams,
    reconstruct_entry_features,
)
from forex_bot.research.feature_separation import (
    FEATURE_DENYLIST,
    LABEL_NAMES,
    build_labels,
    entry_feature_columns,
)

# ---- label builder --------------------------------------------------------

def test_profitable_and_time_exit_labels():
    labels = build_labels(
        {"result_r": 1.2, "exit_reason": "time_stop", "mae_r": -0.2,
         "reached_plus_0_25r": True, "reached_plus_0_5r": True}
    )
    assert labels["profitable_trade"] is True
    assert labels["survived_to_time_exit"] is True
    assert labels["hard_stop_loss"] is False
    assert labels["reached_plus_0_5r"] is True
    assert labels["clean_winner"] is True  # profitable and MAE > -0.5R
    assert labels["straight_to_stop"] is False  # a time-exit did not go straight to stop


def test_hard_stop_straight_to_stop():
    labels = build_labels(
        {"result_r": -1.0, "exit_reason": "hard_stop", "mae_r": -1.0,
         "reached_plus_0_25r": False}
    )
    assert labels["profitable_trade"] is False
    assert labels["hard_stop_loss"] is True
    assert labels["survived_to_time_exit"] is False
    assert labels["straight_to_stop"] is True  # stopped, never reached +0.25R


def test_clean_winner_requires_shallow_mae():
    labels = build_labels(
        {"result_r": 0.8, "exit_reason": "time_stop", "mae_r": -0.7,
         "reached_plus_0_25r": True}
    )
    assert labels["profitable_trade"] is True
    assert labels["clean_winner"] is False  # MAE deeper than -0.5R


def test_missing_inputs_yield_none_not_fabricated():
    labels = build_labels({"result_r": None, "exit_reason": None, "mae_r": None})
    assert labels["profitable_trade"] is None
    assert labels["survived_to_time_exit"] is None
    assert labels["hard_stop_loss"] is None
    assert labels["clean_winner"] is None
    assert labels["straight_to_stop"] is None
    assert set(labels) == set(LABEL_NAMES)


def test_entry_feature_columns_excludes_outcomes():
    cols = [
        "instrument", "side", "h4_adx_at_entry", "h1_rsi_at_entry",
        "result_r", "mfe_r", "mae_r", "exit_reason", "bars_held",
        "entry_time", "recon_h4_bias",
    ]
    feats = entry_feature_columns(cols)
    assert "h4_adx_at_entry" in feats
    assert "instrument" in feats
    # No outcome / id / provenance leaks into features.
    for leaked in ("result_r", "mfe_r", "mae_r", "exit_reason", "bars_held",
                   "entry_time", "recon_h4_bias"):
        assert leaked not in feats
        assert leaked in FEATURE_DENYLIST


# ---- entry-feature reconstruction ----------------------------------------

def _frame(granularity: str, start: datetime, step: timedelta, n: int, *, base: float, drift: float) -> CandleFrame:
    times, rows = [], []
    price = base
    for k in range(n):
        times.append(start + step * k)
        o = price
        c = price + drift
        rows.append({"open": o, "high": max(o, c) + 0.0005, "low": min(o, c) - 0.0005,
                     "close": c, "complete": True})
        price = c
    df = pd.DataFrame(rows, index=pd.DatetimeIndex(times, tz="UTC"))
    return CandleFrame(instrument="EUR_USD", granularity=granularity, df=df)


def test_reconstruction_is_lookahead_safe_and_trend_aligned():
    # Strong uptrend on all frames; a long entry should see bullish recon bias
    # and positive trend-aligned distances. Frames sized so the H4 EMA50/ADX
    # warmup is satisfied before the decision time (>50 H4 bars).
    start = datetime(2022, 1, 1, tzinfo=UTC)
    m15 = _frame("M15", start, timedelta(minutes=15), 1700, base=1.10, drift=0.0003)
    h1 = _frame("H1", start, timedelta(hours=1), 500, base=1.10, drift=0.001)
    h4 = _frame("H4", start, timedelta(hours=4), 200, base=1.10, drift=0.003)
    decision_time = start + timedelta(hours=4) * 120  # H4 bar ~120 (>50 warmup)

    feat = reconstruct_entry_features(
        m15=m15, h1=h1, h4=h4, decision_time=decision_time, side="long",
        params=C022FeatureParams(),
    )
    assert feat["recon_h4_bias"] == "bullish"
    assert feat["h4_bias_score"] == 3
    assert feat["atr_at_entry"] is not None and feat["atr_at_entry"] > 0
    assert feat["h4_ema_slope_atr"] > 0  # trend-aligned positive in an uptrend
    assert feat["h4_close_dist_ema50_atr"] > 0
    # Feature provenance must not be after the decision time (no lookahead).
    assert pd.Timestamp(feat["h4_feature_time"]) <= pd.Timestamp(decision_time)
    assert pd.Timestamp(feat["h1_feature_time"]) <= pd.Timestamp(decision_time)


def test_short_side_flips_trend_alignment_sign():
    start = datetime(2022, 1, 1, tzinfo=UTC)
    m15 = _frame("M15", start, timedelta(minutes=15), 1700, base=1.30, drift=-0.0003)
    h1 = _frame("H1", start, timedelta(hours=1), 500, base=1.30, drift=-0.001)
    h4 = _frame("H4", start, timedelta(hours=4), 200, base=1.30, drift=-0.003)
    decision_time = start + timedelta(hours=4) * 120

    feat = reconstruct_entry_features(
        m15=m15, h1=h1, h4=h4, decision_time=decision_time, side="short",
        params=C022FeatureParams(),
    )
    assert feat["recon_h4_bias"] == "bearish"
    # Short in a downtrend is "in trend": trend-aligned slope should be positive.
    assert feat["h4_ema_slope_atr"] > 0
    assert feat["h4_close_dist_ema50_atr"] > 0

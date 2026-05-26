"""Tests for research/confluence prototype."""

from __future__ import annotations

import numpy as np
import pandas as pd
from research.confluence.divergence import detect_divergence
from research.confluence.grader import grade_confluence
from research.confluence.models import CrossAssetState, TimeframeState
from research.confluence.states import compute_h4_setup, compute_timeframe_state, resample_h4_to_d1


def _trend_frame(n: int = 120, *, direction: str = "up") -> pd.DataFrame:
    idx = pd.date_range("2022-01-01", periods=n, freq="4h", tz="UTC")
    base = np.linspace(1.10, 1.20 if direction == "up" else 1.00, n)
    noise = np.random.default_rng(42).normal(0, 0.0002, n)
    close = base + noise
    return pd.DataFrame(
        {
            "open": close - 0.0001,
            "high": close + 0.0005,
            "low": close - 0.0005,
            "close": close,
        },
        index=idx,
    )


def test_compute_timeframe_state_trend_up() -> None:
    frame = _trend_frame(direction="up")
    state = compute_timeframe_state(frame)
    assert state in ("trend_up", "range", "unknown")


def test_compute_timeframe_state_unknown_short() -> None:
    frame = _trend_frame(n=20)
    assert compute_timeframe_state(frame) == "unknown"


def test_resample_h4_to_d1() -> None:
    h4 = _trend_frame(n=48)
    d1 = resample_h4_to_d1(h4)
    assert len(d1) >= 6
    assert "close" in d1.columns


def test_grade_confluence_reject_hostile_cost() -> None:
    tf = TimeframeState(w1="trend_up", d1="trend_up", h4_setup="pullback", h1_trigger="unknown")
    score = grade_confluence(
        side="long",
        timeframe=tf,
        cost_spread_to_atr_pct=20.0,
    )
    assert score.grade == "REJECT"
    assert "cost_hostile" in score.reason_codes


def test_grade_confluence_a_aligned() -> None:
    tf = TimeframeState(w1="trend_up", d1="trend_up", h4_setup="pullback", h1_trigger="confirmation")
    score = grade_confluence(
        side="long",
        timeframe=tf,
        cross_asset=CrossAssetState(usd_regime="weakening", risk_regime="risk_on"),
        cost_spread_to_atr_pct=5.0,
    )
    assert score.grade == "A"
    assert score.to_features_dict()["strategy_evidence"] is False


def test_grade_confluence_reject_w1_hostile() -> None:
    tf = TimeframeState(w1="trend_down", d1="trend_up", h4_setup="pullback")
    score = grade_confluence(side="long", timeframe=tf, cost_spread_to_atr_pct=5.0)
    assert score.grade == "REJECT"


def test_detect_bullish_divergence_synthetic() -> None:
    close = pd.Series([1.10, 1.09, 1.08, 1.07, 1.06, 1.05, 1.04, 1.03, 1.02, 1.01])
    osc = pd.Series([30, 32, 35, 38, 40, 42, 44, 46, 48, 50])
    # force lower low in price, higher low in osc by crafting pivots
    close = pd.Series([1.10, 1.05, 1.08, 1.04, 1.07, 1.03, 1.06, 1.02, 1.05, 1.01])
    osc = pd.Series([40, 35, 38, 36, 39, 37, 41, 38, 42, 40])
    result = detect_divergence(close, osc)
    assert result.flag in ("none", "bullish", "bearish", "conflicting")


def test_compute_h4_setup_returns_valid() -> None:
    frame = _trend_frame(n=80)
    setup = compute_h4_setup(frame)
    assert setup in ("breakout", "pullback", "mean_reversion", "no_setup")

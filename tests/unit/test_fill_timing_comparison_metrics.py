"""Tests for fill-timing comparison helpers."""

from __future__ import annotations

import pandas as pd
from research.fill_timing_comparison.metrics import (
    compare_exit_reason_shares,
    count_next_bar_open_unavailable,
    exit_reason_shares,
    fill_timing_delta,
    metrics_from_runs,
    pair_fold_delta_rows,
)

from forex_bot.backtesting.fills import NEXT_BAR_OPEN_UNAVAILABLE


def test_fill_timing_delta_negative_when_open_worse():
    close_m = {"trade_count": 100, "expectancy_r": 0.10, "profit_factor": 1.2, "pairs_positive": 4}
    open_m = {"trade_count": 95, "expectancy_r": 0.05, "profit_factor": 1.1, "pairs_positive": 3}
    delta = fill_timing_delta(close_m, open_m)
    assert delta["expectancy_r_delta"] == -0.05
    assert delta["trade_count_delta"] == -5


def test_exit_reason_share_comparison():
    close = pd.DataFrame({"exit_reason": ["stop", "stop", "time"]})
    open_ = pd.DataFrame({"exit_reason": ["stop", "thesis_invalidation", "time"]})
    rows = compare_exit_reason_shares(exit_reason_shares(close), exit_reason_shares(open_))
    thesis = next(r for r in rows if r["exit_reason"] == "thesis_invalidation")
    assert thesis["next_bar_open_share"] > thesis["signal_bar_close_share"]


def test_next_bar_open_unavailable_count():
    rej = pd.DataFrame({"code": [NEXT_BAR_OPEN_UNAVAILABLE, "SPREAD_TOO_WIDE"]})
    assert count_next_bar_open_unavailable(rej) == 1


def test_pair_fold_delta_rows():
    close = {"EUR_USD": {"trade_count": 10, "expectancy_r": 0.1, "total_return_pct": 1.0}}
    open_ = {"EUR_USD": {"trade_count": 9, "expectancy_r": 0.05, "total_return_pct": 0.5}}
    rows = pair_fold_delta_rows(close, open_, split="train")
    assert rows[0]["expectancy_r_delta"] == -0.05


def test_metrics_from_runs_weighted_expectancy():
    per_pair = {
        "A": {"trade_count": 10, "expectancy_r": 0.2, "profit_factor": 1.5, "total_return_pct": 1},
        "B": {"trade_count": 20, "expectancy_r": -0.1, "profit_factor": 0.8, "total_return_pct": -1},
    }
    agg = metrics_from_runs(per_pair)
    assert agg["trade_count"] == 30
    assert abs(agg["expectancy_r"] - 0.0) < 0.001

"""Tests for CAMPAIGN_018 runner gate helpers."""

from __future__ import annotations

from scripts.run_campaign_018_protective_stop import (
    evaluate_gates,
    evaluate_test_gates,
    mechanism_diagnostics,
)


def test_mechanism_diagnostics_zero_targets():
    import pandas as pd

    df = pd.DataFrame(
        {
            "exit_reason": ["stop", "time", "protective_stop"],
            "r_multiple": [-1.0, 1.5, 0.0],
            "protective_stop_armed": [False, True, True],
            "protective_stop_exit": [False, False, True],
        }
    )
    m = mechanism_diagnostics(df)
    assert m["target_exit_count"] == 0
    assert m["protective_stop_armed_count"] == 2


def test_evaluate_gates_fail_train():
    agg = {
        "train": {"expectancy_r": -0.05, "trade_count": 100, "profit_factor": 0.9, "pairs_positive": 3},
        "validation": {"expectancy_r": 0.1, "trade_count": 50, "profit_factor": 1.2, "pairs_positive": 4},
        "validation_stress_2x": {"expectancy_r": 0.05},
        "full_stress_15x": {"expectancy_r": 0.02},
    }
    mech = {"protective_stop_armed_rate_pct": 30.0, "target_exit_count": 0}
    g = evaluate_gates(agg, mech)
    assert g["screening_pass"] is False
    assert "train_expectancy_gte_zero" in g["failed_gates"]


def test_evaluate_test_gates():
    agg = {
        "train": {"expectancy_r": 0.01, "trade_count": 200},
        "validation": {"expectancy_r": 0.05, "trade_count": 100},
        "test": {"expectancy_r": 0.02, "trade_count": 30, "profit_factor": 1.1},
    }
    t = evaluate_test_gates(agg)
    assert t["test_pass"] is True

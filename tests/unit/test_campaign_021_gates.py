"""CAMPAIGN_021 gate discipline unit tests."""

from __future__ import annotations

from forex_bot.research.campaign_021_gates import (
    apply_parity_to_gates,
    evaluate_train_gates,
    evaluate_validation_gates,
)


def test_train_fail_blocks_validation_path() -> None:
    gates = evaluate_train_gates({"expectancy_r": -0.01, "trade_count": 100})
    assert gates["train_gate_pass"] is False
    assert gates["validation_allowed"] is False
    assert gates["verdict"] == "REJECT"


def test_train_pass_allows_validation() -> None:
    gates = evaluate_train_gates({"expectancy_r": 0.01, "trade_count": 100})
    assert gates["train_gate_pass"] is True
    assert gates["validation_allowed"] is True


def test_validation_cannot_rescue_train_fail() -> None:
    agg = {
        "train": {"expectancy_r": -0.05, "trade_count": 200},
        "validation": {"expectancy_r": 0.10, "trade_count": 200, "profit_factor": 1.2, "pairs_positive": 5, "pairs_total": 7},
        "validation_stress_2x": {"expectancy_r": 0.05, "trade_count": 200},
    }
    gates = evaluate_validation_gates(agg)
    assert gates["train_gate_pass"] is False
    assert gates["screening_pass"] is False
    assert gates["verdict"] == "REJECT"


def test_test_lockbox_requires_parity() -> None:
    agg = {
        "train": {"expectancy_r": 0.02, "trade_count": 200},
        "validation": {
            "expectancy_r": 0.05,
            "trade_count": 200,
            "profit_factor": 1.1,
            "pairs_positive": 5,
            "pairs_total": 7,
        },
        "validation_stress_2x": {"expectancy_r": 0.01, "trade_count": 200},
    }
    gates = evaluate_validation_gates(agg)
    blocked = apply_parity_to_gates(gates, parity_pass=False)
    assert blocked["test_lockbox_allowed"] is False
    allowed = apply_parity_to_gates(gates, parity_pass=True)
    assert allowed["test_lockbox_allowed"] is True

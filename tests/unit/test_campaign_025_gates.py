"""Unit tests for CAMPAIGN_025 frozen precommit gates."""

from __future__ import annotations

from forex_bot.research.campaign_025_gates import (
    BEAT_NULL_MARGIN,
    C011_NULL_EXP_R,
    MIN_VALIDATION_PAIRS_POSITIVE,
    MIN_VALIDATION_TRADES,
    apply_parity_to_gates,
    evaluate_test_gates,
    evaluate_train_gates,
    evaluate_validation_gates,
)


def test_frozen_thresholds() -> None:
    assert MIN_VALIDATION_TRADES == 100
    assert MIN_VALIDATION_PAIRS_POSITIVE == 4
    assert C011_NULL_EXP_R == -0.0029154071495408797
    assert BEAT_NULL_MARGIN == 0.010


def test_train_gate_rejects_negative_expectancy() -> None:
    out = evaluate_train_gates({"expectancy_r": -0.01, "trade_count": 200})
    assert out["train_gate_pass"] is False
    assert out["verdict"] == "REJECT"


def test_train_gate_passes() -> None:
    out = evaluate_train_gates({"expectancy_r": 0.02, "trade_count": 200})
    assert out["train_gate_pass"] is True
    assert out["validation_allowed"] is True
    assert out["test_lockbox_allowed"] is False


def _good_validation_agg() -> dict:
    return {
        "train": {"expectancy_r": 0.01, "trade_count": 300},
        "validation": {
            "expectancy_r": 0.02,
            "profit_factor": 1.2,
            "trade_count": 150,
            "pairs_positive": 5,
            "pairs_total": 7,
        },
        "validation_stress_2x": {"expectancy_r": 0.005},
    }


def test_validation_screening_pass_but_parity_still_required() -> None:
    gates = evaluate_validation_gates(_good_validation_agg())
    assert gates["screening_pass"] is True
    # Parity is False until proven, so the lockbox stays closed.
    assert gates["checks"]["backtrader_parity_pass"] is False
    assert gates["test_lockbox_allowed"] is False
    with_parity = apply_parity_to_gates(gates, parity_pass=True)
    assert with_parity["test_lockbox_allowed"] is True
    without_parity = apply_parity_to_gates(gates, parity_pass=False)
    assert without_parity["verdict"] == "REJECT"


def test_validation_trade_floor_is_100() -> None:
    agg = _good_validation_agg()
    agg["validation"]["trade_count"] = 99
    gates = evaluate_validation_gates(agg)
    assert gates["checks"]["validation_trade_count_gte_100"] is False
    assert gates["screening_pass"] is False


def test_single_pair_review_only_flag_when_breadth_fails() -> None:
    agg = _good_validation_agg()
    agg["validation"]["pairs_positive"] = 1
    gates = evaluate_validation_gates(agg)
    assert gates["checks"]["validation_pairs_positive_gte_4_of_7"] is False
    assert gates["screening_pass"] is False
    assert gates["single_pair_review_only_allowed"] is True


def test_test_gate_max_status_is_promotion_review() -> None:
    out = evaluate_test_gates({"expectancy_r": 0.01, "profit_factor": 1.1, "trade_count": 40})
    assert out["verdict"] == "RESEARCH_PASS_PROMOTION_REVIEW_REQUIRED"

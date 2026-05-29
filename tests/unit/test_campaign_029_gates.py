"""Unit tests for CAMPAIGN_029 frozen gate evaluation."""

from __future__ import annotations

from forex_bot.research.campaign_029_gates import (
    C011_BEAT_THRESHOLD_R,
    classify,
    evaluate_train_gates,
    evaluate_validation_gates,
)


def _val(trades=150, exp=0.05, pf=1.3, exp2x=0.02):
    return {"trades": trades, "expectancy_r": exp, "profit_factor_net_pips": pf, "expectancy_r_cost_2x": exp2x}


def test_train_gate_catastrophic_on_negative_expectancy() -> None:
    tg = evaluate_train_gates({"trades": 200, "expectancy_r": -0.01})
    assert tg["catastrophic"] is True and tg["run_validation"] is False


def test_train_gate_catastrophic_on_tiny_sample() -> None:
    tg = evaluate_train_gates({"trades": 5, "expectancy_r": 0.5})
    assert tg["catastrophic"] is True


def test_train_gate_passes() -> None:
    tg = evaluate_train_gates({"trades": 200, "expectancy_r": 0.01})
    assert tg["passed"] and tg["run_validation"]


def test_validation_insufficient_sample() -> None:
    vg = evaluate_validation_gates(_val(trades=40))
    assert vg["classification"] == "INSUFFICIENT_SAMPLE"


def test_validation_reject_when_below_null_margin() -> None:
    # positive but below the C011 beat threshold → reject
    vg = evaluate_validation_gates(_val(exp=C011_BEAT_THRESHOLD_R - 0.001))
    assert vg["classification"] == "REJECT_VALIDATION_GATE"


def test_validation_pass_then_parity_gates_promotion() -> None:
    vg = evaluate_validation_gates(_val(exp=0.05))
    assert vg["classification"] == "PROMOTION_REVIEW_REQUIRED"


def test_classify_reject_train_blocks_validation() -> None:
    d = classify({"trades": 200, "expectancy_r": -0.02}, _val())
    assert d["classification"] == "REJECT_TRAIN_GATE"
    assert d["approved"] is False and d["test_lockbox_opened"] is False


def test_classify_promotion_requires_parity_pass() -> None:
    train = {"trades": 200, "expectancy_r": 0.02}
    assert classify(train, _val(), parity_status="NOT_RUN")["classification"] == "BLOCKED_PARITY"
    assert classify(train, _val(), parity_status="PASS")["classification"] == "PROMOTION_REVIEW_REQUIRED"


def test_classify_never_approves() -> None:
    d = classify({"trades": 200, "expectancy_r": 0.02}, _val(), parity_status="PASS")
    assert d["approved"] is False

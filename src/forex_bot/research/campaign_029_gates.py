"""CAMPAIGN_029 frozen gate evaluation (precommit §10) — pure, testable.

Applies the binding gates to train/validation summary blocks
(:func:`forex_bot.research.range_bar_execution.summarize_trades`). Never approves;
the maximum classification is ``PROMOTION_REVIEW_REQUIRED``.
"""

from __future__ import annotations

from typing import Any

# Frozen reference (precommit §10.6): C011 deduped null expectancy and the
# +0.010R margin a real edge must clear.
C011_NULL_EXP_R = -0.0029154071495408797
C011_BEAT_MARGIN_R = 0.010
C011_BEAT_THRESHOLD_R = C011_NULL_EXP_R + C011_BEAT_MARGIN_R  # ≈ +0.0070845928R

MIN_VALIDATION_TRADES = 100
MIN_TRAIN_TRADES = 30  # sanity floor below which train is non-informative
VALIDATION_PF_MIN = 1.05


def evaluate_train_gates(train: dict[str, Any]) -> dict[str, Any]:
    """Train gate (precommit §10.1) + a sample-sanity floor."""
    n = train.get("trades", 0)
    exp = train.get("expectancy_r")
    checks = {
        "train_trades_ge_30": n >= MIN_TRAIN_TRADES,
        "train_expectancy_ge_0": exp is not None and exp >= 0.0,
    }
    catastrophic = n < MIN_TRAIN_TRADES or (exp is not None and exp < 0.0)
    return {
        "checks": checks,
        "passed": all(checks.values()),
        "catastrophic": catastrophic,
        "run_validation": not catastrophic,
        "train_expectancy_r": exp,
        "train_trades": n,
    }


def evaluate_validation_gates(val: dict[str, Any]) -> dict[str, Any]:
    """Validation gates (precommit §10.2–10.6)."""
    n = val.get("trades", 0)
    if n < MIN_VALIDATION_TRADES:
        return {
            "checks": {"validation_trades_ge_100": False},
            "passed": False,
            "classification": "INSUFFICIENT_SAMPLE",
            "validation_trades": n,
        }
    exp = val.get("expectancy_r")
    pf = val.get("profit_factor_net_pips")
    exp2x = val.get("expectancy_r_cost_2x")
    pf_ok = isinstance(pf, (int, float)) and pf >= VALIDATION_PF_MIN
    checks = {
        "validation_trades_ge_100": True,
        "validation_expectancy_gt_0": exp is not None and exp > 0.0,
        "validation_pf_ge_1_05": pf_ok,
        "cost_stress_2x_expectancy_ge_0": exp2x is not None and exp2x >= 0.0,
        "beats_c011_null_by_0_010R": exp is not None and exp >= C011_BEAT_THRESHOLD_R,
    }
    return {
        "checks": checks,
        "passed": all(checks.values()),
        "classification": "PROMOTION_REVIEW_REQUIRED" if all(checks.values()) else "REJECT_VALIDATION_GATE",
        "validation_expectancy_r": exp,
        "validation_pf": pf,
        "c011_beat_threshold_r": C011_BEAT_THRESHOLD_R,
    }


def classify(
    train: dict[str, Any],
    val: dict[str, Any] | None,
    *,
    parity_status: str = "NOT_RUN",
    engine_ok: bool = True,
) -> dict[str, Any]:
    """Overall frozen classification. Never higher than PROMOTION_REVIEW_REQUIRED."""
    if not engine_ok:
        return {"classification": "BLOCKED_EXECUTION_ENGINE", "approved": False}
    tg = evaluate_train_gates(train)
    result: dict[str, Any] = {"train_gates": tg, "approved": False, "test_lockbox_opened": False}
    if tg["catastrophic"]:
        result["classification"] = "REJECT_TRAIN_GATE"
        result["validation"] = "NOT_RUN (train gate catastrophic)"
        return result
    if val is None:
        result["classification"] = "REJECT_TRAIN_GATE" if not tg["passed"] else "TRAIN_PASS_VALIDATION_PENDING"
        return result
    vg = evaluate_validation_gates(val)
    result["validation_gates"] = vg
    if vg["classification"] != "PROMOTION_REVIEW_REQUIRED":
        result["classification"] = vg["classification"]
        return result
    # validation passed → parity is the last gate before PROMOTION_REVIEW_REQUIRED
    if parity_status == "PASS":
        result["classification"] = "PROMOTION_REVIEW_REQUIRED"
    elif parity_status in ("NOT_RUN", "BLOCKED", "FAIL"):
        result["classification"] = "BLOCKED_PARITY"
    else:
        result["classification"] = "BLOCKED_PARITY"
    return result

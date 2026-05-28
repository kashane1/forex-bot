"""CAMPAIGN_021 gate evaluation — frozen precommit thresholds."""

from __future__ import annotations

from typing import Any

C011_NULL_EXP_R = -0.0029154071495408797
BEAT_NULL_MARGIN = 0.010
MIN_VALIDATION_TRADES = 150
MIN_VALIDATION_PAIRS_POSITIVE = 4
MIN_TRAIN_TRADES_SANITY = 30


def evaluate_train_gates(train: dict[str, Any]) -> dict[str, Any]:
    exp = train.get("expectancy_r")
    checks = {
        "train_expectancy_gte_zero": bool((exp if exp is not None else -999) >= 0),
        "train_trade_count_sanity": bool(train.get("trade_count", 0) >= MIN_TRAIN_TRADES_SANITY),
        "train_provenance_ok": bool(train.get("provenance_ok", True)),
    }
    passed = all(checks.values())
    failed = [k for k, v in checks.items() if not v]
    return {
        "train_gate_pass": passed,
        "checks": checks,
        "failed_gates": failed,
        "verdict": "TRAIN_PASS" if passed else "REJECT",
        "validation_allowed": passed,
        "test_lockbox_allowed": False,
    }


def evaluate_validation_gates(
    agg: dict[str, Any],
    *,
    comparison: dict[str, Any] | None = None,
) -> dict[str, Any]:
    train = agg.get("train", {})
    val = agg.get("validation", {})
    val2x = agg.get("validation_stress_2x", {})
    train_exp = train.get("expectancy_r")
    val_exp = val.get("expectancy_r")
    beat_null_threshold = C011_NULL_EXP_R + BEAT_NULL_MARGIN
    pairs_total = val.get("pairs_total") or 7
    min_pairs = MIN_VALIDATION_PAIRS_POSITIVE if pairs_total >= 7 else (pairs_total // 2 + 1)
    checks = {
        "train_expectancy_gte_zero": bool((train_exp if train_exp is not None else -999) >= 0),
        "validation_expectancy_gt_zero": bool((val_exp if val_exp is not None else -999) > 0),
        "validation_pf_gte_1_05": bool((val.get("profit_factor") or 0) >= 1.05),
        "validation_trade_count_gte_150": bool(val.get("trade_count", 0) >= MIN_VALIDATION_TRADES),
        "validation_pairs_positive_gte_4_of_7": bool(val.get("pairs_positive", 0) >= min_pairs),
        "validation_stress_2x_expectancy_gte_zero": bool(
            (val2x.get("expectancy_r") if val2x.get("expectancy_r") is not None else -999) >= 0
        ),
        "beat_null_vs_c011": bool((val_exp if val_exp is not None else -999) > beat_null_threshold),
        "backtrader_parity_pass": False,
    }
    train_pass = checks["train_expectancy_gte_zero"]
    screening_pass = train_pass and all(
        v for k, v in checks.items() if k not in ("backtrader_parity_pass", "train_expectancy_gte_zero")
    )
    failed = [k for k, v in checks.items() if not v]
    verdict = "REJECT"
    if not train_pass:
        verdict = "REJECT"
    elif screening_pass:
        verdict = "SCREENING_PASS"
    return {
        "screening_pass": screening_pass,
        "train_gate_pass": train_pass,
        "validation_gate_pass": screening_pass,
        "checks": checks,
        "failed_gates": failed,
        "beat_null_threshold": beat_null_threshold,
        "comparison": comparison or {},
        "test_lockbox_allowed": False,
        "verdict": verdict,
        "fill_timing": "next_bar_open",
    }


def apply_parity_to_gates(gates: dict[str, Any], *, parity_pass: bool) -> dict[str, Any]:
    out = dict(gates)
    checks = dict(out.get("checks", {}))
    checks["backtrader_parity_pass"] = parity_pass
    out["checks"] = checks
    failed = [k for k, v in checks.items() if not v]
    out["failed_gates"] = failed
    out["parity_pass"] = parity_pass
    if not parity_pass:
        out["screening_pass"] = False
        out["validation_gate_pass"] = False
        out["verdict"] = "REJECT"
        out["test_lockbox_allowed"] = False
    else:
        out["test_lockbox_allowed"] = bool(
            out.get("train_gate_pass") and out.get("validation_gate_pass") and parity_pass
        )
        if out["test_lockbox_allowed"]:
            out["verdict"] = "SCREENING_PASS"
    return out


def evaluate_test_gates(test: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "test_expectancy_gte_zero": bool((test.get("expectancy_r") or -999) >= 0),
        "test_pf_gte_1_0": bool((test.get("profit_factor") or 0) >= 1.0),
        "test_trade_count_gte_20": bool(test.get("trade_count", 0) >= 20),
    }
    passed = all(checks.values())
    return {
        "test_pass": passed,
        "checks": checks,
        "failed_gates": [k for k, v in checks.items() if not v],
        "verdict": "RESEARCH_PASS_PROMOTION_REVIEW_REQUIRED" if passed else "REJECT",
    }

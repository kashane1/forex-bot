"""Pin the CAMPAIGN_015 anti-overfit diagnostic classifier on a small
synthetic fixture.

These tests do not exercise real campaign data — they pin the binding
label logic (Phase 0 §11) so a future re-run of CAMPAIGN_015 (when
local OANDA H4 data becomes available) classifies cleanly without
silent drift."""

from __future__ import annotations

import math

from research.anti_overfit import (
    CAMPAIGN_015_CLASSIFIER_LABELS,
    DiagnosticInputs,
    classify_campaign_015,
)


def test_label_set_pinned():
    assert set(CAMPAIGN_015_CLASSIFIER_LABELS) == {
        "ROBUST_ABOVE_NULL",
        "ABOVE_NULL_BUT_FRAGILE",
        "SELECTED_CELL_ARTIFACT",
        "WITHIN_NULL",
        "WORSE_THAN_NULL",
        "BLOCKED",
    }


def test_blocked_input_short_circuits():
    out = classify_campaign_015(
        DiagnosticInputs(blocked=True, blocked_reasons=["database missing"])
    )
    assert out["label"] == "BLOCKED"
    assert "database missing" in out["reasons"][0]


def test_too_few_folds_short_circuits_to_blocked():
    out = classify_campaign_015(
        DiagnosticInputs(
            campaign_per_fold_expectancy_r=[0.10, 0.15],
            null_per_fold_expectancy_r=[0.0, 0.01],
        )
    )
    assert out["label"] == "BLOCKED"


def test_robust_above_null_path():
    """A campaign that meets the aggregate floor + every anti-overfit
    gate, with no cell driving all the gross R."""
    inputs = DiagnosticInputs(
        campaign_expectancy_r=0.12,
        campaign_return_pct=8.0,
        campaign_profit_factor=1.45,
        campaign_pairs_positive=6,
        campaign_total_trades=400,
        campaign_per_fold_expectancy_r=[0.08, 0.11, 0.14, 0.09, 0.13, 0.10, 0.12, 0.13],
        # Diversified gross R across pairs (each ~14% of total).
        campaign_pair_gross_positive_r={
            "EUR_USD": 15.0, "GBP_USD": 15.0, "USD_JPY": 14.0, "AUD_USD": 14.0,
            "USD_CAD": 14.0, "USD_CHF": 14.0, "NZD_USD": 14.0,
        },
        # Diversified gross R across folds (each ~12-13% of total).
        campaign_fold_gross_positive_r=[12.0, 13.0, 12.0, 13.0, 13.0, 12.0, 12.0, 13.0],
        campaign_trade_r_series=[0.1] * 400,
        campaign_total_cost_r=2.0,  # cost_dominance = 2/40 = 5%
        null_expectancy_r=-0.002,
        null_return_pct=-0.5,
        null_profit_factor=0.91,
        null_pairs_positive=3,
        null_per_fold_expectancy_r=[0.0, -0.01, 0.005, 0.0, -0.005, 0.0, 0.005, -0.005],
    )
    out = classify_campaign_015(inputs)
    assert out["label"] == "ROBUST_ABOVE_NULL"
    gates = out["anti_overfit_gates"]
    for ok in gates.values():
        assert ok, f"expected gate pass, got {gates}"


def test_above_null_but_fragile_when_t_stat_too_low():
    """Aggregate metrics meet the floor but per-fold expectancy is
    erratic — t-stat falls below 2.0."""
    inputs = DiagnosticInputs(
        campaign_expectancy_r=0.05,
        campaign_return_pct=2.0,
        campaign_profit_factor=1.10,
        campaign_pairs_positive=5,
        campaign_total_trades=300,
        # Per-fold expectancy alternates large + and - — high std, low t.
        campaign_per_fold_expectancy_r=[0.4, -0.3, 0.4, -0.3, 0.4, -0.3, 0.4, -0.3],
        campaign_pair_gross_positive_r={
            "EUR_USD": 15.0, "GBP_USD": 15.0, "USD_JPY": 14.0, "AUD_USD": 14.0,
            "USD_CAD": 14.0, "USD_CHF": 14.0, "NZD_USD": 14.0,
        },
        campaign_fold_gross_positive_r=[15.0, 12.0, 15.0, 12.0, 15.0, 12.0, 15.0, 12.0],
        campaign_trade_r_series=[0.05] * 300,
        campaign_total_cost_r=1.0,
        null_expectancy_r=0.0,
        null_return_pct=0.0,
        null_profit_factor=1.00,
        null_pairs_positive=3,
        null_per_fold_expectancy_r=[0.0] * 8,
    )
    out = classify_campaign_015(inputs)
    assert out["label"] == "ABOVE_NULL_BUT_FRAGILE"
    assert out["anti_overfit_gates"]["per_fold_t_stat_ge_2p0"] is False


def test_selected_cell_artifact_when_one_pair_drives_all_gross_r():
    """Aggregate metrics meet the floor but a single pair drives
    > 70% of gross positive R — classified SELECTED_CELL_ARTIFACT."""
    inputs = DiagnosticInputs(
        campaign_expectancy_r=0.08,
        campaign_return_pct=4.0,
        campaign_profit_factor=1.25,
        campaign_pairs_positive=4,
        campaign_total_trades=300,
        campaign_per_fold_expectancy_r=[0.08] * 8,
        # USD_JPY is 80% of all gross positive R.
        campaign_pair_gross_positive_r={
            "EUR_USD": 2.0, "GBP_USD": 2.0, "USD_JPY": 80.0, "AUD_USD": 4.0,
            "USD_CAD": 4.0, "USD_CHF": 4.0, "NZD_USD": 4.0,
        },
        campaign_fold_gross_positive_r=[12.0] * 8,
        campaign_trade_r_series=[0.08] * 300,
        campaign_total_cost_r=1.0,
        null_expectancy_r=0.0,
        null_return_pct=0.0,
        null_profit_factor=1.00,
        null_pairs_positive=3,
        null_per_fold_expectancy_r=[0.0] * 8,
    )
    out = classify_campaign_015(inputs)
    assert out["label"] == "SELECTED_CELL_ARTIFACT"
    assert out["metrics"]["pair_concentration"] > 0.70


def test_within_null_when_metrics_inside_null_band():
    """Campaign aggregates sit inside the CAMPAIGN_011 null band on
    every axis (expectancy ≈ 0, PF ≈ 1, return ≈ 0, pairs positive
    within ±1 of null)."""
    inputs = DiagnosticInputs(
        campaign_expectancy_r=0.001,
        campaign_return_pct=-0.2,
        campaign_profit_factor=0.99,
        campaign_pairs_positive=3,
        campaign_total_trades=400,
        campaign_per_fold_expectancy_r=[0.0, 0.005, -0.005, 0.0, 0.005, -0.005, 0.0, 0.0],
        campaign_pair_gross_positive_r={
            "EUR_USD": 5.0, "GBP_USD": 5.0, "USD_JPY": 5.0, "AUD_USD": 5.0,
            "USD_CAD": 5.0, "USD_CHF": 5.0, "NZD_USD": 5.0,
        },
        campaign_fold_gross_positive_r=[4.0] * 8,
        campaign_trade_r_series=[0.001] * 400,
        campaign_total_cost_r=1.0,
        null_expectancy_r=-0.001,
        null_return_pct=-0.3,
        null_profit_factor=0.92,
        null_pairs_positive=3,
        null_per_fold_expectancy_r=[0.001, 0.0, -0.001, 0.001, 0.0, -0.001, 0.001, 0.0],
    )
    out = classify_campaign_015(inputs)
    assert out["label"] == "WITHIN_NULL"


def test_worse_than_null_when_every_axis_is_worse():
    """Campaign is materially worse than the matched null on every
    binding axis (CAMPAIGN_014-style direction-of-trade
    falsification)."""
    inputs = DiagnosticInputs(
        campaign_expectancy_r=-0.15,
        campaign_return_pct=-30.0,
        campaign_profit_factor=0.05,
        campaign_pairs_positive=0,
        campaign_total_trades=720,
        campaign_per_fold_expectancy_r=[-0.15] * 8,
        campaign_pair_gross_positive_r={
            "EUR_USD": 1.0, "GBP_USD": 1.0, "USD_JPY": 1.0, "AUD_USD": 1.0,
            "USD_CAD": 1.0, "USD_CHF": 1.0, "NZD_USD": 1.0,
        },
        campaign_fold_gross_positive_r=[1.0] * 8,
        campaign_trade_r_series=[-0.15] * 720,
        campaign_total_cost_r=2.0,
        null_expectancy_r=-0.002,
        null_return_pct=-0.5,
        null_profit_factor=0.91,
        null_pairs_positive=3,
        null_per_fold_expectancy_r=[0.0] * 8,
    )
    out = classify_campaign_015(inputs)
    assert out["label"] == "WORSE_THAN_NULL"


def test_gate_values_finite_under_zero_variance():
    """Edge: if per-fold gap series has zero variance the t-stat goes
    to +inf or -inf but the classifier must still produce a valid
    label."""
    inputs = DiagnosticInputs(
        campaign_expectancy_r=0.10,
        campaign_return_pct=4.0,
        campaign_profit_factor=1.30,
        campaign_pairs_positive=5,
        campaign_total_trades=300,
        campaign_per_fold_expectancy_r=[0.10] * 8,
        campaign_pair_gross_positive_r={
            "EUR_USD": 4.0, "GBP_USD": 4.0, "USD_JPY": 4.0, "AUD_USD": 4.0,
            "USD_CAD": 4.0, "USD_CHF": 4.0, "NZD_USD": 4.0,
        },
        campaign_fold_gross_positive_r=[3.5] * 8,
        campaign_trade_r_series=[0.05] * 300,
        campaign_total_cost_r=1.0,
        null_expectancy_r=0.0,
        null_return_pct=0.0,
        null_profit_factor=1.00,
        null_pairs_positive=3,
        null_per_fold_expectancy_r=[0.0] * 8,
    )
    out = classify_campaign_015(inputs)
    assert out["label"] in CAMPAIGN_015_CLASSIFIER_LABELS
    # T-stat is +inf when std == 0 and mean > 0.
    t = out["metrics"]["per_fold_t_stat"]
    assert math.isinf(t) and t > 0


def test_classifier_never_imports_broker_or_lean():
    """Defense-in-depth grep on the classifier module."""
    from pathlib import Path
    path = Path(__file__).resolve().parent.parent.parent / "research" / "anti_overfit" / "campaign_015.py"
    text = path.read_text(encoding="utf-8")
    # Strip docstring/comments by looking at import lines only.
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith(("import ", "from "))
    ]
    joined = "\n".join(lines)
    assert "forex_bot.broker" not in joined
    assert "oandapyV20" not in joined
    assert "QuantConnect" not in joined
    assert "lean" not in joined.lower()

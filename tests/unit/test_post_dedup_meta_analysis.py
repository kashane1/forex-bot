"""Unit tests for post-dedup meta-analysis collector and archetype scripts."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.analyze_post_dedup_archetypes import (
    analyze_pair_archetypes,
    classify_findings,
)
from scripts.collect_post_dedup_campaign_metrics import (
    build_campaign_row,
    build_null_row,
    collect_metrics,
    render_md,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures/post_dedup_meta"


def _load(name: str) -> dict:
    with (FIXTURES / name).open(encoding="utf-8") as fh:
        return json.load(fh)


def test_build_null_row_has_gap_zero():
    null = _load("null_baseline_mini.json")
    row = build_null_row(null)
    assert row["gap_vs_deduped_null"] == 0.0
    assert row["role"] == "null_baseline"
    assert row["trade_count"] == 20


def test_build_campaign_row_gap_vs_null():
    null = _load("null_baseline_mini.json")
    gate = _load("gate_result_c015_mini.json")
    fold = _load("fold_detail_c015_mini.json")
    null_centre = null["aggregate"]["aggregate_expectancy_r"]
    row = build_campaign_row(
        "CAMPAIGN_015",
        gate,
        fold,
        {"anti_overfit_label": "WITHIN_NULL", "gap_vs_null_exp_r": -0.007},
        {"classification": "TOLERABLE_DRIFT"},
        null_centre,
    )
    assert row["base_exp_r"] == -0.01
    assert abs(row["gap_vs_deduped_null"] - (-0.007)) < 1e-9
    assert row["anti_overfit_label"] == "WITHIN_NULL"
    assert "TOLERABLE_DRIFT" in row["backtrader_status"]
    assert len(row["per_pair"]) == 2
    assert row["long_trades"] == 27  # 6+8 + 7+6


def test_collect_metrics_structure():
    null = _load("null_baseline_mini.json")
    gate = _load("gate_result_c015_mini.json")
    fold = _load("fold_detail_c015_mini.json")
    matrix = collect_metrics(
        null,
        {
            "CAMPAIGN_015": {
                "gate_result": gate,
                "fold_detail": fold,
                "anti_overfit": None,
                "backtrader": None,
            },
        },
    )
    assert matrix["schema_version"] == 1
    assert len(matrix["campaigns"]) == 2
    md = render_md(matrix)
    assert "CAMPAIGN_015" in md
    assert "Headline comparison" in md


def test_analyze_pair_archetypes_ranks():
    pair_matrix = {
        "EUR_USD": {"CAMPAIGN_015": -0.04, "CAMPAIGN_016": -0.06, "CAMPAIGN_017": -0.03},
        "GBP_USD": {"CAMPAIGN_015": 0.05, "CAMPAIGN_016": 0.02, "CAMPAIGN_017": 0.04},
    }
    result = analyze_pair_archetypes(pair_matrix, -0.003, 0.048)
    assert result["least_bad_pairs"][0]["pair"] == "GBP_USD"
    assert result["most_bad_pairs"][0]["pair"] == "EUR_USD"


def test_classify_findings_defaults_no_reliable():
    analysis = {
        "pair_analysis": analyze_pair_archetypes({}, -0.003, 0.048),
        "fold_regime_analysis": {
            "universal_fail_folds": [],
            "folds_with_meaningful_beat_null": [],
        },
        "side_and_exit_analysis": {
            "trade_csv_status": {"CAMPAIGN_015": "OK (1 files)"},
            "aggregate_long_exp_r": -0.05,
            "aggregate_short_exp_r": -0.08,
            "dominant_loss_driver": "stops_dominate",
        },
        "weekly_cost_drag": {
            "campaigns": [
                {
                    "campaign_id": "CAMPAIGN_015",
                    "base_exp_r": -0.01,
                    "cost_delta_exp_r": -0.015,
                    "trade_count": 50,
                },
            ],
        },
        "cell_beat_null": {"cell_count": 0, "cells": []},
    }
    cls = classify_findings(analysis)
    assert cls["primary_classification"] in {
        "NO_RELIABLE_ARCHETYPE",
        "COST_MODEL_DOMINATES",
        "DATA_TOO_SPARSE",
    }

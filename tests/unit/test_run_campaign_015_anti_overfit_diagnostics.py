"""Smoke tests for the CAMPAIGN_015 anti-overfit diagnostic wiring."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.run_campaign_015_anti_overfit_diagnostics import (
    diagnose,
    main,
    render_md,
)


def _toy_campaign_fold_detail() -> dict:
    return {
        "campaign_id": "CAMPAIGN_015",
        "strategy_name": "failed_breakout_reversal",
        "strategy_version": "0.1.0-c015",
        "config_hash": "deadbeef",
        "by_cost": {
            "base": {
                "aggregate": {
                    "aggregate_expectancy_r": 0.10,
                    "aggregate_return_pct": 5.0,
                    "profit_factor": 1.6,
                    "total_trades": 100,
                    "pairs_positive_count": 5,
                },
                "folds": [
                    {
                        "fold_index": 0,
                        "test_start": "2021-12-21",
                        "test_end": "2022-06-18",
                        "trade_count": 50,
                        "expectancy_r": 0.05,
                        "pair_runs": [
                            {
                                "instrument": "EUR_USD",
                                "trade_r_series": [1.0, -1.0, 0.5, -0.5, 1.0],
                            }
                        ],
                    },
                    {
                        "fold_index": 1,
                        "test_start": "2022-06-19",
                        "test_end": "2022-12-15",
                        "trade_count": 50,
                        "expectancy_r": 0.15,
                        "pair_runs": [
                            {
                                "instrument": "EUR_USD",
                                "trade_r_series": [2.0, -1.0, 1.0, -0.5, 1.5],
                            }
                        ],
                    },
                ],
            }
        },
    }


def _toy_null_fold_detail() -> dict:
    return {
        "campaign_id": "CAMPAIGN_011",
        "strategy_name": "random_entry_anchor",
        "config_hash": "abcdef0",
        "aggregate": {
            "aggregate_expectancy_r": -0.01,
            "aggregate_return_pct": -0.5,
            "profit_factor": 0.95,
            "total_trades": 600,
            "pairs_positive_count": 3,
        },
        "folds": [
            {
                "fold_index": 0,
                "test_start": "2021-12-21",
                "test_end": "2022-06-18",
                "trade_count": 100,
                "expectancy_r": -0.02,
            },
            {
                "fold_index": 1,
                "test_start": "2022-06-19",
                "test_end": "2022-12-15",
                "trade_count": 100,
                "expectancy_r": 0.0,
            },
        ],
    }


def test_diagnose_emits_per_fold_gap_and_a_valid_label():
    obj = diagnose(
        campaign_fd=_toy_campaign_fold_detail(),
        null_fd=_toy_null_fold_detail(),
    )
    assert obj["campaign_id"] == "CAMPAIGN_015"
    assert obj["approval_status"] == "NOT_APPROVED"
    assert obj["approved_strategies_yaml_state"] == "approved: []"
    assert obj["anti_overfit_label"] in {
        "ROBUST_ABOVE_NULL",
        "ABOVE_NULL_BUT_FRAGILE",
        "SELECTED_CELL_ARTIFACT",
        "WITHIN_NULL",
        "WORSE_THAN_NULL",
        "BLOCKED",
    }
    assert len(obj["per_fold_gap_series"]) == 2
    g0 = obj["per_fold_gap_series"][0]
    # fold 0: campaign 0.05 - null (-0.02) = +0.07
    assert g0["gap_r"] == pytest.approx(0.07, abs=1e-9)
    g1 = obj["per_fold_gap_series"][1]
    # fold 1: 0.15 - 0.0 = +0.15
    assert g1["gap_r"] == pytest.approx(0.15, abs=1e-9)


def test_diagnose_blocked_on_window_mismatch():
    null = _toy_null_fold_detail()
    null["folds"][0]["test_end"] = "1999-01-01"
    obj = diagnose(
        campaign_fd=_toy_campaign_fold_detail(),
        null_fd=null,
    )
    assert obj["anti_overfit_label"] == "BLOCKED"


def test_diagnose_blocked_on_fold_count_mismatch():
    null = _toy_null_fold_detail()
    null["folds"] = null["folds"][:1]
    obj = diagnose(
        campaign_fd=_toy_campaign_fold_detail(),
        null_fd=null,
    )
    assert obj["anti_overfit_label"] == "BLOCKED"


def test_render_md_includes_disclaimer_and_label():
    obj = diagnose(
        campaign_fd=_toy_campaign_fold_detail(),
        null_fd=_toy_null_fold_detail(),
    )
    md = render_md(obj)
    assert "does NOT approve" in md
    assert obj["anti_overfit_label"] in md
    assert "approved: []" in md


def test_diagnose_against_real_artifacts(tmp_path: Path):
    repo = Path(__file__).resolve().parents[2]
    cfd = repo / "research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json"
    nfd = repo / "backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json"
    if not (cfd.exists() and nfd.exists()):
        pytest.skip("real artifacts not present")
    rc = main(
        [
            "--campaign-fold-detail", str(cfd),
            "--null-fold-detail", str(nfd),
            "--out-json", str(tmp_path / "o.json"),
            "--out-md", str(tmp_path / "o.md"),
        ]
    )
    assert rc == 0
    obj = json.loads((tmp_path / "o.json").read_text())
    # The published 8 fold windows must line up.
    assert len(obj["per_fold_gap_series"]) == 8
    # Mean per-fold gap is comfortably positive in the real artifacts.
    assert obj["mean_per_fold_gap_r"] > 0.1
    # Label is one of the binding labels.
    assert obj["anti_overfit_label"] in {
        "ROBUST_ABOVE_NULL",
        "ABOVE_NULL_BUT_FRAGILE",
        "SELECTED_CELL_ARTIFACT",
        "WITHIN_NULL",
        "WORSE_THAN_NULL",
    }
    # Approval status invariant — diagnostic never approves.
    assert obj["approval_status"] == "NOT_APPROVED"


def test_main_blocks_on_missing_input(tmp_path: Path):
    rc = main(
        [
            "--campaign-fold-detail", str(tmp_path / "nope.json"),
            "--null-fold-detail", str(tmp_path / "nope2.json"),
            "--out-json", str(tmp_path / "o.json"),
            "--out-md", str(tmp_path / "o.md"),
        ]
    )
    assert rc == 2

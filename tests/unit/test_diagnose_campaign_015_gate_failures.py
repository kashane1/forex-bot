"""Unit tests for scripts/diagnose_campaign_015_gate_failures.py.

Diagnostic-only tooling — these tests pin the *math* and *labels*
the autopsy emits, so a future regression does not silently move
the diagnostic numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.diagnose_campaign_015_gate_failures import (
    autopsy,
    main,
    render_md,
)


def _fixture_gate_result() -> dict:
    return {
        "campaign_id": "CAMPAIGN_015",
        "strategy_name": "failed_breakout_reversal",
        "strategy_version": "0.1.0-c015",
        "config_hash": "deadbeef",
        "fold_count": 2,
        "verdict": "REJECT",
        "approval_status": "NOT_APPROVED",
        "by_cost": {
            "base": {
                "aggregate_expectancy_r": 0.10,
                "aggregate_return_pct": 5.0,
                "profit_factor": 2.0,
                "total_trades": 30,
                "fold_pass_rate": 0.5,
                "folds_passing": 1,
                "pairs_positive_count": 4,
                "single_pair_dominance_pct": 30.0,
                "median_per_fold_expectancy_r": 0.10,
                "trade_level_cumulative_r": 3.0,
                "aggregate_gates": {
                    "fold_pass_rate_ge_5_of_8": False,
                    "fold_count_ge_8": False,
                    "expectancy_r_min": True,
                    "profit_factor_min": True,
                    "trade_count_min_200": False,
                    "trade_count_max_800": True,
                    "pairs_positive_ge_4_of_7": True,
                    "single_pair_dominance_le_70pct": True,
                },
                "aggregate_pass": False,
                "expectancy_min_applied": 0.03,
                "profit_factor_min_applied": 1.05,
            },
            "2xcost": {
                "aggregate_expectancy_r": 0.05,
                "aggregate_return_pct": 2.0,
                "profit_factor": 1.2,
                "total_trades": 30,
                "fold_pass_rate": 0.0,
                "folds_passing": 0,
                "pairs_positive_count": 3,
                "single_pair_dominance_pct": 40.0,
                "median_per_fold_expectancy_r": 0.04,
                "trade_level_cumulative_r": 1.5,
                "aggregate_gates": {
                    "fold_pass_rate_ge_5_of_8": False,
                    "fold_count_ge_8": False,
                    "expectancy_r_min": True,
                    "profit_factor_min": True,
                    "trade_count_min_200": False,
                    "trade_count_max_800": True,
                    "pairs_positive_ge_4_of_7": False,
                    "single_pair_dominance_le_70pct": True,
                },
                "aggregate_pass": False,
                "expectancy_min_applied": 0.0,
                "profit_factor_min_applied": 1.0,
            },
        },
    }


def _fixture_fold_detail() -> dict:
    return {
        "by_cost": {
            "base": {
                "folds": [
                    {
                        "fold_index": 0,
                        "test_start": "2021-12-21",
                        "test_end": "2022-06-18",
                        "trade_count": 18,
                        "expectancy_r": -0.2,
                        "pairs_positive": 2,
                        "single_pair_dominance_pct": 32.0,
                        "gates": {
                            "trade_count_ge_30": False,
                            "expectancy_r_ge_0": False,
                            "pairs_positive_ge_3": False,
                            "single_pair_dominance_le_60pct": True,
                        },
                        "passes": False,
                        "pair_runs": [
                            {"instrument": "EUR_USD", "trade_count": 0, "expectancy_r": 0.0, "return_pct": 0.0},
                            {"instrument": "GBP_USD", "trade_count": 1, "expectancy_r": -1.0, "return_pct": -0.3},
                            {"instrument": "USD_JPY", "trade_count": 3, "expectancy_r": 0.1, "return_pct": 0.3},
                            {"instrument": "AUD_USD", "trade_count": 14, "expectancy_r": -0.4, "return_pct": -0.6},
                        ],
                    },
                    {
                        "fold_index": 1,
                        "test_start": "2022-06-19",
                        "test_end": "2022-12-15",
                        "trade_count": 28,
                        "expectancy_r": 0.4,
                        "pairs_positive": 5,
                        "single_pair_dominance_pct": 35.0,
                        "gates": {
                            "trade_count_ge_30": False,
                            "expectancy_r_ge_0": True,
                            "pairs_positive_ge_3": True,
                            "single_pair_dominance_le_60pct": True,
                        },
                        "passes": False,
                        "pair_runs": [
                            {"instrument": "EUR_USD", "trade_count": 2, "expectancy_r": 0.2, "return_pct": 0.1},
                            {"instrument": "GBP_USD", "trade_count": 9, "expectancy_r": 0.5, "return_pct": 1.5},
                            {"instrument": "USD_JPY", "trade_count": 11, "expectancy_r": 0.3, "return_pct": 1.2},
                            {"instrument": "AUD_USD", "trade_count": 6, "expectancy_r": 0.4, "return_pct": 0.6},
                        ],
                    },
                ]
            },
            "2xcost": {
                "folds": [
                    {
                        "fold_index": 0,
                        "test_start": "2021-12-21",
                        "test_end": "2022-06-18",
                        "trade_count": 18,
                        "expectancy_r": -0.25,
                        "pairs_positive": 2,
                        "single_pair_dominance_pct": 31.0,
                        "gates": {
                            "trade_count_ge_30": False,
                            "expectancy_r_ge_0": False,
                            "pairs_positive_ge_3": False,
                            "single_pair_dominance_le_60pct": True,
                        },
                        "passes": False,
                        "pair_runs": [
                            {"instrument": "EUR_USD", "trade_count": 0, "expectancy_r": 0.0, "return_pct": 0.0},
                            {"instrument": "GBP_USD", "trade_count": 1, "expectancy_r": -1.0, "return_pct": -0.3},
                            {"instrument": "USD_JPY", "trade_count": 3, "expectancy_r": 0.1, "return_pct": 0.3},
                            {"instrument": "AUD_USD", "trade_count": 14, "expectancy_r": -0.5, "return_pct": -0.8},
                        ],
                    },
                    {
                        "fold_index": 1,
                        "test_start": "2022-06-19",
                        "test_end": "2022-12-15",
                        "trade_count": 28,
                        "expectancy_r": 0.3,
                        "pairs_positive": 4,
                        "single_pair_dominance_pct": 35.0,
                        "gates": {
                            "trade_count_ge_30": False,
                            "expectancy_r_ge_0": True,
                            "pairs_positive_ge_3": True,
                            "single_pair_dominance_le_60pct": True,
                        },
                        "passes": False,
                        "pair_runs": [
                            {"instrument": "EUR_USD", "trade_count": 2, "expectancy_r": 0.15, "return_pct": 0.05},
                            {"instrument": "GBP_USD", "trade_count": 9, "expectancy_r": 0.4, "return_pct": 1.2},
                            {"instrument": "USD_JPY", "trade_count": 11, "expectancy_r": 0.25, "return_pct": 1.0},
                            {"instrument": "AUD_USD", "trade_count": 6, "expectancy_r": 0.3, "return_pct": 0.4},
                        ],
                    },
                ]
            },
        }
    }


def test_autopsy_identifies_failed_aggregate_gates():
    obj = autopsy(_fixture_gate_result(), _fixture_fold_detail())
    assert "fold_pass_rate_ge_5_of_8" in obj["by_cost"]["base"]["aggregate_gates_failed"]
    assert "trade_count_min_200" in obj["by_cost"]["base"]["aggregate_gates_failed"]
    assert "fold_count_ge_8" in obj["by_cost"]["base"]["aggregate_gates_failed"]
    # 2xcost loses pairs_positive_ge_4_of_7 in the fixture
    assert (
        "pairs_positive_ge_4_of_7"
        in obj["by_cost"]["2xcost"]["aggregate_gates_failed"]
    )


def test_autopsy_counts_trade_count_gate_failures():
    obj = autopsy(_fixture_gate_result(), _fixture_fold_detail())
    base = obj["by_cost"]["base"]
    # Both fixture folds fail trade_count_ge_30.
    assert base["per_fold_gate_failure_counts"]["trade_count_ge_30"] == 2
    assert obj["summary"]["every_fold_fails_trade_count_ge_30_base"] is True
    assert obj["summary"]["every_fold_fails_trade_count_ge_30_2xcost"] is True


def test_autopsy_counterfactual_fold_pass_count():
    obj = autopsy(_fixture_gate_result(), _fixture_fold_detail())
    base = obj["by_cost"]["base"]
    # Actual: 0/2 pass (both fail trade_count).
    assert base["folds_passing_actual"] == 0
    # Counterfactual without trade-count: fold 1 has all other gates true ⇒ 1.
    assert base["folds_passing_counterfactual_no_trade_count_gate"] == 1
    # Without trade-count AND pairs_positive: fold 0 still fails expectancy ⇒ still 1.
    assert base["folds_passing_counterfactual_no_trade_count_or_pairs_positive"] == 1


def test_autopsy_pair_fold_cell_distribution():
    obj = autopsy(_fixture_gate_result(), _fixture_fold_detail())
    dist = obj["by_cost"]["base"]["pair_fold_cell_distribution"]
    # fixture base: fold 0 = [0,1,3,14], fold 1 = [2,9,11,6] → cells:
    # 0:1, 1:1, 2-3:2 (3,2), 4-9:2 (9,6), 10+:2 (14,11)
    assert dist["0_trades"] == 1
    assert dist["1_trade"] == 1
    assert dist["2_to_3_trades"] == 2
    assert dist["4_to_9_trades"] == 2
    assert dist["10_or_more_trades"] == 2
    assert sum(dist.values()) == 8


def test_autopsy_summary_flags():
    obj = autopsy(_fixture_gate_result(), _fixture_fold_detail())
    s = obj["summary"]
    # Fold 0 fails expectancy_r_ge_0 despite aggregate being +0.10.
    assert s["any_fold_failed_expectancy_despite_positive_aggregate_base"] is True
    assert s["any_fold_failed_pairs_positive_base"] is True
    # Fixture single-pair dominance is always ≤60.
    assert s["any_fold_failed_single_pair_dominance_base"] is False
    assert s["all_folds_fail_actual"] is True


def test_autopsy_rejects_wrong_campaign():
    bad = _fixture_gate_result()
    bad["campaign_id"] = "CAMPAIGN_999"
    with pytest.raises(ValueError):
        autopsy(bad, _fixture_fold_detail())


def test_autopsy_rejects_wrong_strategy():
    bad = _fixture_gate_result()
    bad["strategy_name"] = "trend_following"
    with pytest.raises(ValueError):
        autopsy(bad, _fixture_fold_detail())


def test_render_md_includes_diagnostic_banner_and_no_approval():
    obj = autopsy(_fixture_gate_result(), _fixture_fold_detail())
    md = render_md(obj)
    assert "NON-GATING" in md
    assert "remains REJECT" in md
    assert "approved: []" in md
    # No table cell ever spells out "APPROVED" without NOT_.
    assert "NOT_APPROVED" in md


def test_main_runs_against_real_rehydrate_artifacts(tmp_path: Path):
    repo = Path(__file__).resolve().parents[2]
    gr = repo / "research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/gate_result.json"
    fd = repo / "research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json"
    if not gr.exists() or not fd.exists():
        pytest.skip("rehydrate artifacts not present in this checkout")
    out_json = tmp_path / "autopsy.json"
    out_md = tmp_path / "autopsy.md"
    rc = main(
        [
            "--gate-result", str(gr),
            "--fold-detail", str(fd),
            "--out-json", str(out_json),
            "--out-md", str(out_md),
        ]
    )
    assert rc == 0
    obj = json.loads(out_json.read_text())
    # The campaign of record.
    assert obj["campaign_id"] == "CAMPAIGN_015"
    assert obj["strategy_name"] == "failed_breakout_reversal"
    assert obj["runner_verdict"] == "REJECT"
    # All 8 base folds fail trade_count_ge_30.
    assert obj["summary"]["every_fold_fails_trade_count_ge_30_base"] is True
    # The published 0/8 fold-pass result.
    assert obj["by_cost"]["base"]["folds_passing_actual"] == 0


def test_main_blocks_on_missing_input(tmp_path: Path):
    out_json = tmp_path / "out.json"
    out_md = tmp_path / "out.md"
    rc = main(
        [
            "--gate-result", str(tmp_path / "nope.json"),
            "--fold-detail", str(tmp_path / "nope2.json"),
            "--out-json", str(out_json),
            "--out-md", str(out_md),
        ]
    )
    assert rc == 2
    assert not out_json.exists()
    assert not out_md.exists()

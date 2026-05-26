"""Unit tests for scripts/diagnose_campaign_015_concentration.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.diagnose_campaign_015_concentration import (
    _percentile,
    concentration,
    main,
    render_md,
)


def _toy_fold_detail() -> dict:
    """Two folds, two pairs each, ~10 trades total, hand-checkable R series."""
    return {
        "campaign_id": "CAMPAIGN_015",
        "strategy_name": "failed_breakout_reversal",
        "strategy_version": "0.1.0-c015",
        "config_hash": "deadbeef",
        "fold_gates": {
            "trade_count_min": 30,
            "expectancy_r_min": 0.0,
            "pairs_positive_min": 3,
            "single_pair_dominance_max_pct": 60.0,
        },
        "by_cost": {
            "base": {
                "folds": [
                    {
                        "fold_index": 0,
                        "expectancy_r": -0.10,
                        "trade_count": 4,
                        "pair_runs": [
                            {
                                "instrument": "EUR_USD",
                                "trade_count": 2,
                                "trade_r_series": [-1.0, 2.0],
                                "exit_reason_counts": {"stop": 1, "time": 1},
                                "rejection_counts": {},
                            },
                            {
                                "instrument": "GBP_USD",
                                "trade_count": 2,
                                "trade_r_series": [-1.0, -0.4],
                                "exit_reason_counts": {"stop": 2},
                                "rejection_counts": {"SPREAD_TOO_WIDE": 1},
                            },
                        ],
                    },
                    {
                        "fold_index": 1,
                        "expectancy_r": 0.50,
                        "trade_count": 6,
                        "pair_runs": [
                            {
                                "instrument": "EUR_USD",
                                "trade_count": 3,
                                "trade_r_series": [1.0, 2.0, -1.0],
                                "exit_reason_counts": {"time": 2, "stop": 1},
                                "rejection_counts": {},
                            },
                            {
                                "instrument": "GBP_USD",
                                "trade_count": 3,
                                "trade_r_series": [4.0, 0.5, -0.5],
                                "exit_reason_counts": {"time": 3},
                                "rejection_counts": {},
                            },
                        ],
                    },
                ]
            }
        },
    }


def test_percentile_basic():
    assert _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 0.0) == 1.0
    assert _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 1.0) == 5.0
    assert _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 0.5) == 3.0
    # 25th percentile of [1..5] via linear interpolation
    assert _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 0.25) == 2.0


def test_concentration_totals_match_by_hand():
    obj = concentration(_toy_fold_detail())
    b = obj["by_cost"]["base"]
    # All trade R: [-1,2,-1,-0.4, 1,2,-1, 4,0.5,-0.5] → sum = 5.6
    assert b["total_trades"] == 10
    assert b["total_r"] == pytest.approx(5.6, abs=1e-9)
    assert b["gross_positive_r"] == pytest.approx(9.5, abs=1e-9)
    assert b["gross_negative_r"] == pytest.approx(-3.9, abs=1e-9)
    assert b["implied_profit_factor"] == pytest.approx(9.5 / 3.9, abs=1e-9)


def test_concentration_per_fold_per_pair_per_cell():
    b = concentration(_toy_fold_detail())["by_cost"]["base"]
    # fold 0: -1+2-1-0.4 = -0.4; fold 1: 1+2-1+4+0.5-0.5 = 6.0
    assert b["per_fold_total_r"][0] == pytest.approx(-0.4)
    assert b["per_fold_total_r"][1] == pytest.approx(6.0)
    # EUR_USD: -1+2+1+2-1 = 3.0; GBP_USD: -1-0.4+4+0.5-0.5 = 2.6
    assert b["per_pair_total_r"]["EUR_USD"] == pytest.approx(3.0)
    assert b["per_pair_total_r"]["GBP_USD"] == pytest.approx(2.6)
    # cell fold_01_GBP_USD: 4+0.5-0.5 = 4.0 (top)
    assert b["per_cell_total_r"]["fold_01_GBP_USD"] == pytest.approx(4.0)


def test_concentration_top_trade_shares():
    b = concentration(_toy_fold_detail())["by_cost"]["base"]
    # Top positive trade is 4.0 (fold 1 GBP_USD)
    assert b["top_positive_trades"][0]["r"] == 4.0
    # total_r=5.6 ⇒ top1 share of total = 4.0/5.6
    assert b["top_1_positive_trade_share_of_total_r"] == pytest.approx(
        4.0 / 5.6
    )
    # gross_pos_r=9.5 ⇒ top1 share of gross positive = 4.0/9.5
    assert b["top_1_positive_trade_share_of_gross_positive_r"] == pytest.approx(
        4.0 / 9.5
    )
    # top 3 positives: 4, 2, 2 = 8.0
    assert b["top_3_positive_trade_share_of_total_r"] == pytest.approx(
        8.0 / 5.6
    )


def test_concentration_top_fold_pair_cell():
    b = concentration(_toy_fold_detail())["by_cost"]["base"]
    assert b["top_fold_index"] == 1
    assert b["top_pair"] == "EUR_USD"
    assert b["top_cell"] == "fold_01_GBP_USD"


def test_concentration_loo_by_fold_drops_negative_fold_helps():
    b = concentration(_toy_fold_detail())["by_cost"]["base"]
    by_drop = {row["dropped_fold"]: row for row in b["loo_by_fold"]}
    # Drop fold 0 (-0.4 R, 4 trades) → remaining = 6.0 R / 6 trades = +1.0
    assert by_drop[0]["remaining_total_r"] == pytest.approx(6.0)
    assert by_drop[0]["remaining_expectancy_r"] == pytest.approx(1.0)
    # Drop fold 1 (+6.0 R) → remaining = -0.4 / 4 = -0.1
    assert by_drop[1]["remaining_total_r"] == pytest.approx(-0.4)
    assert by_drop[1]["remaining_expectancy_r"] == pytest.approx(-0.1)


def test_concentration_loo_by_pair():
    b = concentration(_toy_fold_detail())["by_cost"]["base"]
    by_drop = {row["dropped_pair"]: row for row in b["loo_by_pair"]}
    # Drop EUR_USD (3.0 R) → remaining = 5.6 - 3.0 = 2.6
    assert by_drop["EUR_USD"]["remaining_total_r"] == pytest.approx(2.6)
    # Drop GBP_USD (2.6 R) → remaining = 5.6 - 2.6 = 3.0
    assert by_drop["GBP_USD"]["remaining_total_r"] == pytest.approx(3.0)


def test_concentration_distribution_bounds():
    b = concentration(_toy_fold_detail())["by_cost"]["base"]
    d = b["trade_r_distribution"]
    # Sorted R: [-1,-1,-1,-0.5,-0.4,0.5,1,2,2,4]; min=-1, max=4,
    # linear-interp median = (-0.4 + 0.5)/2 = 0.05
    assert d["min"] == -1.0
    assert d["max"] == 4.0
    assert d["median"] == pytest.approx(0.05)


def test_concentration_mean_vs_median_per_fold_expectancy():
    b = concentration(_toy_fold_detail())["by_cost"]["base"]
    # per-fold expectancy from fixture: fold 0 = -0.10, fold 1 = +0.50
    assert b["mean_per_fold_expectancy_r"] == pytest.approx(0.20)
    assert b["median_per_fold_expectancy_r"] == pytest.approx(0.20)
    # equal in 2-fold case
    assert b["mean_minus_median_per_fold_expectancy_r"] == pytest.approx(0.0)


def test_concentration_exit_reasons_aggregate():
    b = concentration(_toy_fold_detail())["by_cost"]["base"]
    assert b["exit_reason_counts"] == {"stop": 4, "time": 6}


def test_concentration_against_real_rehydrate_artifact(tmp_path: Path):
    repo = Path(__file__).resolve().parents[2]
    fd = repo / "research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json"
    if not fd.exists():
        pytest.skip("rehydrate artifacts not present in this checkout")
    out_json = tmp_path / "out.json"
    out_md = tmp_path / "out.md"
    rc = main(
        [
            "--fold-detail", str(fd),
            "--out-json", str(out_json),
            "--out-md", str(out_md),
        ]
    )
    assert rc == 0
    obj = json.loads(out_json.read_text())
    base = obj["by_cost"]["base"]
    # Sanity: matches the published 164 trades / +37.73 R rehydrate aggregate.
    assert base["total_trades"] == 164
    assert base["total_r"] == pytest.approx(37.726468665408945, abs=1e-9)
    # USD_CHF must be the dominant pair (>= 50% of total R).
    assert base["top_pair"] == "USD_CHF"
    assert base["top_pair_share_of_total_r"] >= 0.5
    # Top-5 trade share of total R >= 70% (concentration claim).
    assert base["top_5_positive_trade_share_of_total_r"] >= 0.7
    # Median trade R is negative — most trades lose.
    assert base["trade_r_distribution"]["median"] < 0.0


def test_main_blocks_on_missing_input(tmp_path: Path):
    rc = main(
        [
            "--fold-detail", str(tmp_path / "nope.json"),
            "--out-json", str(tmp_path / "o.json"),
            "--out-md", str(tmp_path / "o.md"),
        ]
    )
    assert rc == 2


def test_render_md_includes_diagnostic_banner():
    obj = concentration(_toy_fold_detail())
    md = render_md(obj)
    assert "Diagnostic only" in md
    # Banner must clearly say the tool does not approve anything.
    assert "does not approve any strategy" in md.lower()

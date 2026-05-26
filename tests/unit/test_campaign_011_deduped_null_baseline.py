"""Tests for CAMPAIGN_011 deduped canonical null-baseline rollup."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from research.null_baselines import (
    CANONICAL_CAMPAIGN_011_DEDUPED_JSON,
    load_campaign_011_deduped_null_baseline,
)
from scripts.promote_campaign_011_deduped_null_baseline import build_rollup

REPO_ROOT = Path(__file__).resolve().parents[2]
DEDUPED_DIR = REPO_ROOT / "backtests" / "CAMPAIGN_011_random_entry_anchor_deduped"


def test_canonical_null_baseline_json_exists() -> None:
    assert CANONICAL_CAMPAIGN_011_DEDUPED_JSON.is_file()


def test_load_campaign_011_deduped_null_baseline_schema() -> None:
    payload = load_campaign_011_deduped_null_baseline()
    assert payload["schema_version"] == 1
    assert payload["canonical"] is True
    assert payload["null_model"] is True
    assert payload["campaign_id"] == "CAMPAIGN_011"
    assert payload["strategy_name"] == "random_entry_anchor"
    assert payload["master_seed"] == 20260523
    assert payload["data_dedupe_policy"] == "keep_last"
    assert len(payload["per_fold"]) == 8
    assert len(payload["per_pair"]) == 7


def test_deduped_aggregate_metrics_pinned() -> None:
    payload = load_campaign_011_deduped_null_baseline()
    agg = payload["aggregate"]
    assert agg["total_trades"] == 1180
    assert agg["aggregate_expectancy_r"] == pytest.approx(-0.0029154071495408797)
    assert agg["pairs_positive_count"] == 3
    assert agg["folds_passing"] == 0


def test_supersedes_contaminated_headline() -> None:
    payload = load_campaign_011_deduped_null_baseline()
    sup = payload["supersedes"]
    assert sup["total_trades"] == 1177
    assert sup["aggregate_expectancy_r"] == -0.0024
    assert sup["integrity_status"] == "LIKELY_CONTAMINATED"


def test_build_rollup_matches_committed_fold_detail() -> None:
    if not (DEDUPED_DIR / "walk_forward" / "fold_detail.json").is_file():
        pytest.skip("local deduped CAMPAIGN_011 run not present")
    built = build_rollup(input_dir=DEDUPED_DIR, probe_dedupe=False)
    committed = json.loads(CANONICAL_CAMPAIGN_011_DEDUPED_JSON.read_text(encoding="utf-8"))
    assert built["aggregate"]["total_trades"] == committed["aggregate"]["total_trades"]
    assert built["aggregate"]["aggregate_expectancy_r"] == pytest.approx(
        committed["aggregate"]["aggregate_expectancy_r"]
    )
    assert [f["expectancy_r"] for f in built["per_fold"]] == [
        f["expectancy_r"] for f in committed["per_fold"]
    ]

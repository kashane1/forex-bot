"""Tests for campaign contamination audit inventory and classification."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from forex_bot.contamination_audit.classify import classify_campaigns
from forex_bot.contamination_audit.inventory import build_inventory

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "contamination_audit"


@pytest.fixture
def mini_repo(tmp_path: Path) -> Path:
    """Minimal repo layout for inventory/classification tests."""
    (tmp_path / "docs" / "research").mkdir(parents=True)
    (tmp_path / "configs").mkdir()
    (tmp_path / "backtests" / "CAMPAIGN_015_failed_breakout_reversal" / "walk_forward").mkdir(
        parents=True
    )
    (tmp_path / "backtests" / "CAMPAIGN_015_failed_breakout_reversal_deduped" / "walk_forward").mkdir(
        parents=True
    )
    (tmp_path / "backtests" / "CAMPAIGN_011_random_entry_anchor" / "walk_forward").mkdir(parents=True)

    manifest = {
        "generated": "2026-05-26",
        "campaigns": [
            {
                "campaign_id": "CAMPAIGN_011",
                "strategy_family": "random_entry_anchor",
                "data_source": "oanda-practice",
                "verdict": "REJECT",
                "report_path": "docs/research/CAMPAIGN_011_WALK_FORWARD_RESULT.md",
                "artifact_folder": "backtests/CAMPAIGN_011_random_entry_anchor",
                "key_metrics": {},
            },
            {
                "campaign_id": "CAMPAIGN_015",
                "strategy_family": "failed_breakout_reversal",
                "data_source": "oanda-practice",
                "verdict": "REJECT",
                "report_path": "docs/research/CAMPAIGN_015_DEDUPED_RERUN_RESULT.md",
                "artifact_folder": "backtests/CAMPAIGN_015_failed_breakout_reversal_deduped",
                "key_metrics": {"duplicate_rows_dropped": 64509},
            },
        ],
    }
    (tmp_path / "docs" / "research" / "EVIDENCE_MANIFEST.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    (tmp_path / "docs" / "research" / "CAMPAIGN_011_WALK_FORWARD_RESULT.md").write_text(
        """# CAMPAIGN_011 Walk-Forward Result
**Date:** 2026-05-23
Uses CandleRepo and data/campaign_002.sqlite3.
**Overall verdict: REJECT**
""",
        encoding="utf-8",
    )

    (tmp_path / "docs" / "research" / "CAMPAIGN_015_DEDUPED_RERUN_RESULT.md").write_text(
        """# CAMPAIGN_015 Deduped Rerun
**Date:** 2026-05-26
DEDUPED_INPUT keep_last
duplicate rows dropped: 64509
**Verdict:** REJECT
""",
        encoding="utf-8",
    )

    (tmp_path / "backtests" / "CAMPAIGN_015_failed_breakout_reversal" / "walk_forward" / "results.json").write_text(
        '{"verdict": "REJECT", "note": "stale contaminated"}',
        encoding="utf-8",
    )
    (tmp_path / "backtests" / "CAMPAIGN_015_failed_breakout_reversal_deduped" / "walk_forward" / "results.json").write_text(
        '{"verdict": "REJECT", "deduped": true}',
        encoding="utf-8",
    )

    (tmp_path / "configs" / "campaign_011_random_entry_anchor.yaml").write_text(
        "app:\n  database_path: ./data/campaign_002.sqlite3\n",
        encoding="utf-8",
    )

    (tmp_path / "docs" / "research" / "BACKTRADER_CAMPAIGN_011_FULL_WINDOW_COMPARISON_004.md").write_text(
        """# Backtrader comparison
CSV export from lean_parity/exports deduped.
Backtrader lane diagnostic only.
""",
        encoding="utf-8",
    )

    return tmp_path


def test_inventory_finds_campaign_artifacts(mini_repo: Path) -> None:
    inv = build_inventory(mini_repo)
    assert inv["artifact_count"] >= 5
    paths = {a["artifact_path"] for a in inv["artifacts"]}
    assert "docs/research/CAMPAIGN_011_WALK_FORWARD_RESULT.md" in paths
    assert any("deduped" in p for p in paths)


def test_inventory_marks_contaminated_campaign_015(mini_repo: Path) -> None:
    inv = build_inventory(mini_repo)
    stale = [
        a for a in inv["artifacts"]
        if "CAMPAIGN_015_failed_breakout_reversal/walk_forward" in a["artifact_path"]
        and "deduped" not in a["artifact_path"]
    ]
    assert stale
    assert stale[0]["recommended_contamination_status"] == "CONTAMINATED_SUPERSEDED"


def test_inventory_marks_null_baseline_campaign_011(mini_repo: Path) -> None:
    inv = build_inventory(mini_repo)
    c011 = [
        a for a in inv["artifacts"]
        if a.get("campaign_id") == "CAMPAIGN_011"
        and "WALK_FORWARD_RESULT" in a["artifact_path"]
    ]
    assert c011
    assert c011[0]["recommended_contamination_status"] == "NULL_BASELINE_REQUIRES_RERUN"


def test_classify_campaign_015_dedup_safe(mini_repo: Path) -> None:
    inv = build_inventory(mini_repo)
    data = classify_campaigns(inv)
    c015 = next(c for c in data["classifications"] if c["campaign_id"] == "CAMPAIGN_015")
    assert c015["evidence_integrity_status"] == "DEDUP_SAFE"
    assert c015["result_remains_valid"] is True
    assert c015["mark_superseded"] is True


def test_classify_campaign_011_requires_rerun(mini_repo: Path) -> None:
    inv = build_inventory(mini_repo)
    data = classify_campaigns(inv)
    c011 = next(c for c in data["classifications"] if c["campaign_id"] == "CAMPAIGN_011")
    assert c011["evidence_integrity_status"] == "NULL_BASELINE_REQUIRES_RERUN"
    assert c011["rerun_required"] is True


def test_classify_all_fifteen_campaigns(mini_repo: Path) -> None:
    inv = build_inventory(mini_repo)
    data = classify_campaigns(inv)
    assert len(data["classifications"]) == 15

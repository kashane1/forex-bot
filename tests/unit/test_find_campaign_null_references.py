"""Tests for scripts/find_campaign_null_references.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.find_campaign_null_references import (
    scan_all,
    scan_file,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "null_reference_scan"


def test_scan_file_detects_old_and_campaign_patterns() -> None:
    old = scan_file(FIXTURES / "old_null_reference.md")
    assert "campaign_011" in old.pattern_ids
    assert "campaign_012" in old.pattern_ids
    assert "old_null_expectancy" in old.pattern_ids
    assert "old_null_trades" in old.pattern_ids
    assert "old_null_json_path" in old.pattern_ids


def test_scan_file_detects_canonical_null_json() -> None:
    canonical = scan_file(FIXTURES / "canonical_null_reference.md")
    assert "canonical_null_json" in canonical.pattern_ids
    assert "campaign_014" in canonical.pattern_ids


def test_scan_all_on_repo_produces_inventory_structure() -> None:
    data, _matched = scan_all()
    assert data["schema_version"] == 1
    assert data["files_scanned"] > 0
    assert data["files_with_matches"] > 0
    assert "campaign_012" in data["pattern_counts"]
    assert data["campaign_file_hits"]["CAMPAIGN_012"] > 0


def test_main_writes_inventory_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import scripts.find_campaign_null_references as mod

    out_json = tmp_path / "inventory.json"
    out_md = tmp_path / "inventory.md"
    out_doc = tmp_path / "inventory_doc.md"
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(mod, "SCAN_ROOTS", [FIXTURES])
    monkeypatch.setattr(mod, "OUT_JSON", out_json)
    monkeypatch.setattr(mod, "OUT_MD", out_md)
    monkeypatch.setattr(mod, "OUT_DOC", out_doc)

    assert mod.main() == 0
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["files_with_matches"] >= 1
    assert out_md.exists()
    assert out_doc.exists()

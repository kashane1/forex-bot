"""Tests for the research-archive validator (Phase 4, infra-foundation-001).

The integration test proves the *real* committed archive passes every
check; the unit tests prove each check actually catches the failure it
is meant to catch (a non-empty registry, an approved campaign, an
approval verdict, a missing report, a broken index link, a planted
credential).
"""

from __future__ import annotations

import pytest

from forex_bot.research_archive import (
    check_artifact_folders_exist,
    check_diagnostic_artifacts,
    check_evidence_index_links,
    check_manifest_schema,
    check_no_approved_strategy,
    check_registry_empty,
    check_reports_exist,
    check_verdicts_non_approval,
    load_manifest,
    scan_files_for_credentials,
    validate_archive,
)

_CAMPAIGN_IDS = {f"CAMPAIGN_{n:03d}" for n in range(1, 18)}


def test_real_research_archive_passes_every_check():
    """The committed research archive is internally consistent."""
    result = validate_archive()
    failed = [c.name for c in result.checks if not c.ok]
    assert result.ok, f"failing checks: {failed}"


def test_real_manifest_has_all_seventeen_campaigns():
    manifest = load_manifest()
    campaigns = manifest["campaigns"]
    assert len(campaigns) == 17
    assert {c["campaign_id"] for c in campaigns} == _CAMPAIGN_IDS


def test_real_manifest_marks_every_campaign_unapproved():
    manifest = load_manifest()
    assert manifest["no_approved_strategy"] is True
    for entry in manifest["campaigns"]:
        assert entry["strategy_approved"] is False


def test_registry_empty_check_passes_on_empty(tmp_path):
    reg = tmp_path / "approved_strategies.yaml"
    reg.write_text("approved: []\n", encoding="utf-8")
    assert check_registry_empty(reg).ok is True


def test_registry_empty_check_catches_a_non_empty_registry(tmp_path):
    reg = tmp_path / "approved_strategies.yaml"
    reg.write_text("approved:\n  - trend_following\n", encoding="utf-8")
    assert check_registry_empty(reg).ok is False


def test_no_approved_check_catches_an_approved_campaign():
    bad = [{"campaign_id": "CAMPAIGN_X", "strategy_approved": True}]
    assert check_no_approved_strategy(bad).ok is False
    good = [{"campaign_id": "CAMPAIGN_X", "strategy_approved": False}]
    assert check_no_approved_strategy(good).ok is True


def test_verdict_check_rejects_an_approval_verdict():
    bad = [{"campaign_id": "CAMPAIGN_X", "verdict": "APPROVED"}]
    assert check_verdicts_non_approval(bad).ok is False
    good = [{"campaign_id": "CAMPAIGN_X", "verdict": "REJECT"}]
    assert check_verdicts_non_approval(good).ok is True


def test_manifest_schema_catches_missing_keys():
    incomplete = [{"campaign_id": "CAMPAIGN_X"}]
    assert check_manifest_schema(incomplete).ok is False


def test_reports_exist_check_catches_a_missing_report(tmp_path):
    entries = [{"campaign_id": "CAMPAIGN_X", "report_path": "backtests/NOPE.md"}]
    assert check_reports_exist(entries, repo_root=tmp_path).ok is False


def test_artifact_folder_check_catches_a_missing_folder(tmp_path):
    entries = [{"campaign_id": "CAMPAIGN_X", "artifact_folder": "backtests/nope"}]
    assert check_artifact_folders_exist(entries, repo_root=tmp_path).ok is False
    # A null artifact_folder is allowed (e.g. the diagnostics campaign).
    assert check_artifact_folders_exist(
        [{"campaign_id": "CAMPAIGN_Y", "artifact_folder": None}], repo_root=tmp_path,
    ).ok is True


def test_evidence_index_link_check_catches_a_broken_link(tmp_path):
    index = tmp_path / "EVIDENCE_INDEX.md"
    index.write_text("see [the report](./missing_report.md)\n", encoding="utf-8")
    assert check_evidence_index_links(index, repo_root=tmp_path).ok is False
    # And passes when the target exists.
    (tmp_path / "present.md").write_text("ok\n", encoding="utf-8")
    index.write_text("see [it](./present.md)\n", encoding="utf-8")
    assert check_evidence_index_links(index, repo_root=tmp_path).ok is True


def test_credential_scan_catches_a_planted_token(tmp_path):
    # An OANDA-token-shaped string (hex-hex), assembled from parts so the
    # test file itself carries no realistic-looking literal.
    fake_token = ("a1b2c3d4" * 4) + "-" + ("e5f6a7b8" * 4)
    planted = tmp_path / "leak.md"
    planted.write_text(f"token: {fake_token}\n", encoding="utf-8")
    assert scan_files_for_credentials([planted]).ok is False
    # A planted account-id shape is caught too.
    planted.write_text("account 101-001-23456789-001\n", encoding="utf-8")
    assert scan_files_for_credentials([planted]).ok is False


def test_credential_scan_passes_a_clean_file(tmp_path):
    clean = tmp_path / "clean.md"
    clean.write_text("config hash abcdef0123456789 — no credentials here\n", encoding="utf-8")
    assert scan_files_for_credentials([clean]).ok is True


def test_diagnostic_artifacts_check_passes_on_valid_entries(tmp_path):
    (tmp_path / "smoke.md").write_text("diagnostic\n", encoding="utf-8")
    entries = [
        {"artifact_id": "X", "path": "smoke.md", "strategy_evidence": False},
    ]
    assert check_diagnostic_artifacts(entries, repo_root=tmp_path).ok is True
    # An empty diagnostics list is fine.
    assert check_diagnostic_artifacts([], repo_root=tmp_path).ok is True


def test_diagnostic_artifacts_check_catches_a_missing_artifact(tmp_path):
    entries = [{"artifact_id": "X", "path": "nope.md", "strategy_evidence": False}]
    assert check_diagnostic_artifacts(entries, repo_root=tmp_path).ok is False


def test_diagnostic_artifacts_check_catches_a_strategy_evidence_claim(tmp_path):
    """A diagnostic artifact may never claim to be strategy evidence."""
    (tmp_path / "smoke.md").write_text("diagnostic\n", encoding="utf-8")
    entries = [{"artifact_id": "X", "path": "smoke.md", "strategy_evidence": True}]
    assert check_diagnostic_artifacts(entries, repo_root=tmp_path).ok is False
    # A missing flag is treated as a claim too — it must be explicitly false.
    entries = [{"artifact_id": "X", "path": "smoke.md"}]
    assert check_diagnostic_artifacts(entries, repo_root=tmp_path).ok is False


def test_real_manifest_diagnostic_artifacts_are_present_and_not_evidence():
    manifest = load_manifest()
    diagnostics = manifest.get("diagnostic_artifacts", [])
    assert diagnostics, "the manifest should declare diagnostic artifacts"
    assert all(d["strategy_evidence"] is False for d in diagnostics)
    assert check_diagnostic_artifacts(diagnostics).ok is True


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))

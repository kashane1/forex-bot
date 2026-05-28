"""Sanity checks for fill-timing comparison script contract."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/compare_fill_timing_reference_campaign.py"


def test_script_declares_infrastructure_only_flags():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "not_approved" in text
    assert "test_lockbox_opened" in text
    assert "strategy_evidence" in text
    assert "OandaBroker" not in text
    assert "CAMPAIGN_019" in text


def test_output_dir_under_research():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "research/fill_timing_reference_comparison" in text

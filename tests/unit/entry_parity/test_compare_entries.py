"""Tests for entry timestamp comparison."""

from __future__ import annotations

from research.entry_parity.compare_entries import compare_campaign_entries
from research.entry_parity.constants import REPO_ROOT


def test_c008_entry_comparison_runs():
    result = compare_campaign_entries("C008", repo_root=REPO_ROOT)
    assert result["bespoke_entry_count"] > 0
    assert result["backtrader_entry_count"] > 0
    assert result["common_entries"] > 0
    assert result["bespoke_only_entries"] > 0


def test_common_entries_subset_of_both():
    result = compare_campaign_entries("C008", repo_root=REPO_ROOT)
    assert result["common_entries"] <= result["bespoke_entry_count"]
    assert result["common_entries"] <= result["backtrader_entry_count"]

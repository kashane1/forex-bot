"""Tests for entry timestamp comparison."""

from __future__ import annotations

import pytest
from research.backtrader_exit_parity.constants import BESPOKE_TRADE_GLOBS
from research.entry_parity.compare_entries import compare_campaign_entries
from research.entry_parity.constants import REPO_ROOT


def _c008_bespoke_trades_present() -> bool:
    """The bespoke C008 trade CSVs are gitignored (regenerable, bulky) and absent
    from a fresh checkout / CI. Skip data-dependent assertions when they aren't
    on disk locally."""
    return any(
        next(REPO_ROOT.glob(BESPOKE_TRADE_GLOBS["C008"].format(split=split)), None)
        for split in ("train", "validation")
    )


_needs_c008_trades = pytest.mark.skipif(
    not _c008_bespoke_trades_present(),
    reason="local C008 bespoke trade CSVs absent (gitignored)",
)


@_needs_c008_trades
def test_c008_entry_comparison_runs():
    result = compare_campaign_entries("C008", repo_root=REPO_ROOT)
    assert result["bespoke_entry_count"] > 0
    assert result["backtrader_entry_count"] > 0
    assert result["common_entries"] > 0
    assert result["bespoke_only_entries"] > 0


@_needs_c008_trades
def test_common_entries_subset_of_both():
    result = compare_campaign_entries("C008", repo_root=REPO_ROOT)
    assert result["common_entries"] <= result["bespoke_entry_count"]
    assert result["common_entries"] <= result["backtrader_entry_count"]

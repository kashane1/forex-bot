"""Approval-entry schema & evaluation tests (Phase 5, infra-foundation-001).

Proves that the approved-strategy registry rejects malformed entries,
missing evidence reports, and out-of-bounds risk; that expired approvals
do not count; that a paper approval does not unlock the demo loop; that
a live approval needs the live gates; and that a valid, active entry
does approve its strategy. The committed registry stays empty.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml

from forex_bot.approval import (
    ApprovalError,
    StrategyNotApprovedError,
    approved_strategy_ids,
    assert_loop_strategies_approved,
    load_approval_registry,
)

# A real committed report — cited as evidence so the require_evidence
# check finds an existing file. (The entry itself is a synthetic test
# fixture; it does not assert anything about that campaign's verdict.)
_REAL_REPORT = "backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md"
_ON_DATE = date(2026, 6, 1)  # inside the fixture approval windows below


def _valid_entry(**overrides) -> dict:
    entry = {
        "strategy_id": "trend_following",
        "version": "0.1.0",
        "allowed_mode": "paper",
        "approved_by": "test-human",
        "approval_date": date(2026, 1, 1),
        "expiry_date": date(2027, 1, 1),
        "evidence_report": _REAL_REPORT,
        "max_risk_per_trade_pct": 0.25,
    }
    entry.update(overrides)
    return entry


def _write_registry(tmp_path: Path, entries: list) -> Path:
    reg = tmp_path / "approved_strategies.yaml"
    reg.write_text(yaml.safe_dump({"approved": entries}), encoding="utf-8")
    return reg


def test_committed_registry_loads_empty():
    assert load_approval_registry() == []


def test_a_valid_active_entry_approves_its_strategy(tmp_path):
    reg = _write_registry(tmp_path, [_valid_entry()])
    entries = load_approval_registry(reg)
    assert len(entries) == 1
    assert approved_strategy_ids("paper", registry_path=reg, on_date=_ON_DATE) == {
        "trend_following"
    }
    # The guard allows it — and no exception is the assertion.
    assert_loop_strategies_approved(
        "paper", ["trend_following"], registry_path=reg, on_date=_ON_DATE,
    )


def test_a_bare_string_entry_is_rejected(tmp_path):
    reg = _write_registry(tmp_path, ["trend_following"])
    with pytest.raises(ApprovalError):
        load_approval_registry(reg)


def test_a_missing_required_field_is_rejected(tmp_path):
    entry = _valid_entry()
    del entry["approved_by"]
    reg = _write_registry(tmp_path, [entry])
    with pytest.raises(ApprovalError):
        load_approval_registry(reg)


def test_an_unknown_field_is_rejected(tmp_path):
    reg = _write_registry(tmp_path, [_valid_entry(surprise="extra")])
    with pytest.raises(ApprovalError):
        load_approval_registry(reg)


def test_an_unknown_strategy_id_is_rejected(tmp_path):
    reg = _write_registry(tmp_path, [_valid_entry(strategy_id="made_up_strategy")])
    with pytest.raises(ApprovalError):
        load_approval_registry(reg)


def test_a_missing_evidence_report_is_rejected(tmp_path):
    reg = _write_registry(
        tmp_path, [_valid_entry(evidence_report="backtests/NO_SUCH_REPORT.md")]
    )
    with pytest.raises(ApprovalError, match="evidence_report"):
        load_approval_registry(reg)


def test_expiry_before_approval_is_rejected(tmp_path):
    reg = _write_registry(
        tmp_path,
        [_valid_entry(approval_date=date(2026, 1, 1), expiry_date=date(2025, 1, 1))],
    )
    with pytest.raises(ApprovalError):
        load_approval_registry(reg)


def test_out_of_bounds_max_risk_is_rejected(tmp_path):
    for bad in (0.0, 0.9, -0.1):
        reg = _write_registry(tmp_path, [_valid_entry(max_risk_per_trade_pct=bad)])
        with pytest.raises(ApprovalError):
            load_approval_registry(reg)


def test_an_expired_approval_does_not_count(tmp_path):
    """A schema-valid but expired entry approves nothing — the loop is
    still refused."""
    reg = _write_registry(
        tmp_path,
        [_valid_entry(approval_date=date(2023, 1, 1), expiry_date=date(2024, 1, 1))],
    )
    assert load_approval_registry(reg)  # it parses fine ...
    assert approved_strategy_ids("paper", registry_path=reg, on_date=_ON_DATE) == set()
    with pytest.raises(StrategyNotApprovedError):
        assert_loop_strategies_approved(
            "paper", ["trend_following"], registry_path=reg, on_date=_ON_DATE,
        )


def test_a_paper_approval_does_not_unlock_the_demo_loop(tmp_path):
    reg = _write_registry(tmp_path, [_valid_entry(allowed_mode="paper")])
    assert approved_strategy_ids("demo", registry_path=reg, on_date=_ON_DATE) == set()
    with pytest.raises(StrategyNotApprovedError):
        assert_loop_strategies_approved(
            "demo", ["trend_following"], registry_path=reg, on_date=_ON_DATE,
        )


def test_a_live_approval_is_rejected_unless_the_live_gates_pass(tmp_path):
    reg = _write_registry(tmp_path, [_valid_entry(allowed_mode="live")])
    # Without the live gates a live approval counts for nothing.
    assert approved_strategy_ids(
        "live", registry_path=reg, on_date=_ON_DATE, live_gates_ok=False,
    ) == set()
    # Only when the existing config-layer live gates have passed.
    assert approved_strategy_ids(
        "live", registry_path=reg, on_date=_ON_DATE, live_gates_ok=True,
    ) == {"trend_following"}


def test_an_empty_registry_blocks_every_loop(tmp_path):
    reg = _write_registry(tmp_path, [])
    for mode in ("paper", "demo", "live"):
        with pytest.raises(StrategyNotApprovedError):
            assert_loop_strategies_approved(
                mode, ["trend_following"], registry_path=reg, on_date=_ON_DATE,
            )

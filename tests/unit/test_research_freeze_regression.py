"""Research-freeze regression hardening
(Phase 5, infra-execution-fidelity-001).

Dedicated guards that fail if a future change weakens the research-only
freeze. Each test pins one freeze property:

  * the approved-strategy registry stays empty;
  * paper-loop / demo-loop refuse *before* building a broker;
  * live mode cannot bypass the approval registry;
  * the archive validator still catches a missing report and an
    approval claim.

Some overlap with test_approved_strategies.py / test_approval.py /
test_validate_research_archive.py is deliberate — these are
belt-and-suspenders regression anchors.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from forex_bot.approval import (
    APPROVED_STRATEGIES_PATH,
    StrategyNotApprovedError,
    approved_strategy_ids,
    assert_loop_strategies_approved,
    load_approval_registry,
)
from forex_bot.cli import app
from forex_bot.research_archive import (
    check_no_approved_strategy,
    check_registry_empty,
    check_reports_exist,
    check_verdicts_non_approval,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
runner = CliRunner()


def _load_freeze_script():
    path = REPO_ROOT / "scripts" / "check_research_freeze.py"
    spec = importlib.util.spec_from_file_location("check_research_freeze", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


freeze = _load_freeze_script()


def _registry_with_entry(tmp_path: Path, *, allowed_mode: str) -> Path:
    """A tmp approved-strategy registry holding one valid entry, with its
    evidence file present under tmp_path (the repo_root for the test)."""
    (tmp_path / "evidence.md").write_text("evidence", encoding="utf-8")
    reg = tmp_path / "approved.yaml"
    reg.write_text(
        "approved:\n"
        "  - strategy_id: trend_following\n"
        '    version: "0.1.0"\n'
        f"    allowed_mode: {allowed_mode}\n"
        "    approved_by: tester\n"
        "    approval_date: 2026-01-01\n"
        "    expiry_date: 2027-01-01\n"
        "    evidence_report: evidence.md\n"
        "    max_risk_per_trade_pct: 0.25\n",
        encoding="utf-8",
    )
    return reg


# --------------------------------------------------------------------------
# 1. The approved-strategy registry stays empty
# --------------------------------------------------------------------------


def test_committed_registry_is_empty():
    assert APPROVED_STRATEGIES_PATH.exists()
    assert load_approval_registry() == []
    assert check_registry_empty().ok is True


def test_registry_empty_check_catches_a_non_empty_registry(tmp_path):
    """If an approval entry were ever added by default, the check fails."""
    reg = tmp_path / "approved.yaml"
    reg.write_text("approved:\n  - trend_following\n", encoding="utf-8")
    assert check_registry_empty(reg).ok is False


# --------------------------------------------------------------------------
# 2 & 3. paper-loop / demo-loop refuse before building a broker
# --------------------------------------------------------------------------


def test_paper_loop_refuses_before_building_a_broker(paper_config_path, monkeypatch):
    """The paper-loop CLI must hit the approval guard before it ever
    constructs a broker."""
    built: list[bool] = []

    def _spy(_settings):
        built.append(True)
        raise AssertionError("broker built before the approval guard refused")

    monkeypatch.setattr("forex_bot.cli._build_broker", _spy)
    result = runner.invoke(
        app, ["paper-loop", "--config", str(paper_config_path), "--once"]
    )
    assert result.exit_code == 2, result.output
    assert not built, "paper-loop built a broker before the approval check"


def test_demo_loop_refuses_before_building_a_broker(practice_config_path, monkeypatch):
    """practice.yaml enables order submission, so the only thing stopping
    the demo-loop is the approval guard — and it must stop it before any
    broker is built."""
    built: list[bool] = []

    def _spy(_settings):
        built.append(True)
        raise AssertionError("broker built before the approval guard refused")

    monkeypatch.setattr("forex_bot.cli._build_broker", _spy)
    result = runner.invoke(
        app, ["demo-loop", "--config", str(practice_config_path), "--once"]
    )
    assert result.exit_code == 2, result.output
    assert not built, "demo-loop built a broker before the approval check"


# --------------------------------------------------------------------------
# 4. Live mode cannot bypass the approval registry
# --------------------------------------------------------------------------


def test_live_mode_refused_by_an_empty_registry(tmp_path):
    """Even with the config-layer live gates passed, an empty registry
    refuses a live loop."""
    empty = tmp_path / "approved.yaml"
    empty.write_text("approved: []\n", encoding="utf-8")
    with pytest.raises(StrategyNotApprovedError):
        assert_loop_strategies_approved(
            "live", ["trend_following"], registry_path=empty, live_gates_ok=True
        )


def test_a_paper_approval_does_not_grant_live(tmp_path):
    """An approval entry for paper mode must not approve live trading."""
    reg = _registry_with_entry(tmp_path, allowed_mode="paper")
    on = date(2026, 6, 1)
    assert approved_strategy_ids(
        "paper", registry_path=reg, on_date=on, repo_root=tmp_path
    ) == {"trend_following"}
    assert approved_strategy_ids(
        "live", registry_path=reg, on_date=on, repo_root=tmp_path, live_gates_ok=True
    ) == set()


def test_a_live_entry_still_requires_the_live_gates(tmp_path):
    """A live-mode entry is honoured only when live_gates_ok is True —
    the config-layer live gates cannot be skipped."""
    reg = _registry_with_entry(tmp_path, allowed_mode="live")
    on = date(2026, 6, 1)
    assert approved_strategy_ids(
        "live", registry_path=reg, on_date=on, repo_root=tmp_path, live_gates_ok=False
    ) == set()
    assert approved_strategy_ids(
        "live", registry_path=reg, on_date=on, repo_root=tmp_path, live_gates_ok=True
    ) == {"trend_following"}


# --------------------------------------------------------------------------
# 5 & 6. The archive validator catches a missing report / approval claim
# --------------------------------------------------------------------------


def test_archive_validator_catches_a_missing_report():
    missing = [{"campaign_id": "X", "report_path": "docs/research/__does_not_exist__.md"}]
    assert check_reports_exist(missing, repo_root=REPO_ROOT).ok is False


def test_archive_validator_catches_an_approved_strategy_flag():
    """A campaign claiming strategy_approved != false must be rejected."""
    assert check_no_approved_strategy(
        [{"campaign_id": "X", "strategy_approved": True}]
    ).ok is False
    # A missing flag is treated as a claim too — it must be explicitly false.
    assert check_no_approved_strategy([{"campaign_id": "X"}]).ok is False


def test_archive_validator_catches_an_approval_verdict():
    """A verdict that is not a known non-approval verdict must be rejected."""
    for verdict in ("APPROVE", "GO", "PROMOTE"):
        result = check_verdicts_non_approval(
            [{"campaign_id": "X", "verdict": verdict}]
        )
        assert result.ok is False, f"{verdict!r} should be rejected"
    # NO-GO is a legitimate non-approval verdict.
    assert check_verdicts_non_approval(
        [{"campaign_id": "X", "verdict": "NO-GO"}]
    ).ok is True


# --------------------------------------------------------------------------
# The check_research_freeze.py gate itself
# --------------------------------------------------------------------------


def test_freeze_gate_loops_refuse_check_passes():
    result = freeze.check_loops_refuse()
    assert result.ok is True


def test_freeze_gate_passes_on_the_current_repo():
    checks = freeze.run_freeze_checks()
    failed = [c.name for c in checks if not c.ok]
    assert not failed, f"research freeze gate FAILED: {failed}"

"""Tests for the local research-data preparation orchestrator
(Phase 5, infra-data-parity-001).

Cover the safe-by-construction properties: the plan is correctly
ordered, it invokes only data-prep / read-only scripts (never a loop or
an approval), a live environment is refused, and `--dry-run` executes
nothing.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = _REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


prepare = _load_script("prepare_local_research_data")

# The only scripts the orchestrator is ever allowed to invoke.
_ALLOWED_SCRIPTS = {
    "rehydrate_oanda_h4_store.py",
    "smoke_d1agg_next_open.py",
    "export_lean_parity_data.py",
    "check_research_freeze.py",
}


def test_build_plan_is_ordered():
    plan = prepare.build_plan(with_lean_export=False)
    names = [s.name for s in plan]
    assert names[0].startswith("rehydrate")
    assert "verify" in names[1]
    assert "smoke" in names[2]
    assert "freeze" in names[-1]


def test_build_plan_invokes_only_safe_scripts():
    for with_export in (False, True):
        for step in prepare.build_plan(with_lean_export=with_export):
            # command is [python, <script path>, *args]
            assert len(step.command) >= 2
            script = Path(step.command[1]).name
            assert script in _ALLOWED_SCRIPTS, f"unexpected script {script}"


def test_plan_never_invokes_a_loop_or_approval():
    """The orchestrator must not be able to start a loop or touch the
    approval registry."""
    for with_export in (False, True):
        for step in prepare.build_plan(with_lean_export=with_export):
            # No command token is the `bot` CLI (which can start a loop).
            assert "bot" not in [t.lower() for t in step.command]
            # The invoked script is not a loop / approval script.
            script = Path(step.command[1]).name.lower()
            assert "loop" not in script
            assert "approv" not in script
            # No argument references the approval registry.
            for arg in step.command[2:]:
                assert "approved_strategies" not in arg.lower()


def test_lean_export_step_is_opt_in():
    without = prepare.build_plan(with_lean_export=False)
    with_export = prepare.build_plan(with_lean_export=True)
    assert len(with_export) == len(without) + 1
    assert any("Lean-parity" in s.name for s in with_export)
    assert not any("Lean-parity" in s.name for s in without)


def test_rehydrate_step_is_the_only_one_needing_credentials():
    creds_steps = [
        s for s in prepare.build_plan(with_lean_export=True) if s.needs_credentials
    ]
    assert len(creds_steps) == 1
    assert creds_steps[0].name.startswith("rehydrate")


def test_live_environment_is_refused(monkeypatch):
    monkeypatch.setenv("OANDA_ENVIRONMENT", "live")
    assert prepare.live_environment_error() is not None


def test_practice_or_unset_environment_is_allowed(monkeypatch):
    monkeypatch.delenv("OANDA_ENVIRONMENT", raising=False)
    assert prepare.live_environment_error() is None
    monkeypatch.setenv("OANDA_ENVIRONMENT", "practice")
    assert prepare.live_environment_error() is None


def test_dry_run_executes_nothing(monkeypatch):
    def _boom(*_args, **_kwargs):
        raise AssertionError("--dry-run must not run any subprocess")

    monkeypatch.setattr(prepare.subprocess, "run", _boom)
    monkeypatch.delenv("OANDA_ENVIRONMENT", raising=False)
    assert prepare.main(["--dry-run"]) == 0
    assert prepare.main(["--dry-run", "--with-lean-export"]) == 0


def test_dry_run_refuses_a_live_environment(monkeypatch):
    monkeypatch.setenv("OANDA_ENVIRONMENT", "live")
    assert prepare.main(["--dry-run"]) == 2

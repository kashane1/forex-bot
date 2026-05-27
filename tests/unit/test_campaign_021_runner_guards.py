"""CAMPAIGN_021 runner guard tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from forex_bot.strategies.lower_timeframe_mtf_confluence_entry import (
    D1AGG_SOURCE_M1,
    validate_c021_data_provenance,
)

_REPO = Path(__file__).resolve().parents[2]
_RUNNER = _REPO / "scripts/run_campaign_021_ltf_mtf_confluence.py"
_GATE_MODULE = _REPO / "src/forex_bot/research/campaign_021_gates.py"


def test_runner_rejects_m1_d1agg_in_provenance() -> None:
    bad = {
        "execution_m15": "m1_derived",
        "context_h1": "m1_derived",
        "context_h4": "m1_derived",
        "d1agg_context": D1AGG_SOURCE_M1,
    }
    with pytest.raises(ValueError, match="rejects m1_derived_d1agg"):
        validate_c021_data_provenance(bad)


def test_runner_source_requires_next_bar_open() -> None:
    text = _RUNNER.read_text(encoding="utf-8")
    assert "next_bar_open" in text
    assert "signal_bar_close forbidden" in text or "SIGNAL_BAR_CLOSE" in text


def test_runner_blocks_validation_without_train_pass(tmp_path: Path, monkeypatch) -> None:
    import scripts.run_campaign_021_ltf_mtf_confluence as runner

    state_path = tmp_path / "gate_state.json"
    state_path.write_text(json.dumps({"train_gate_pass": False}), encoding="utf-8")
    monkeypatch.setattr(runner, "GATE_STATE_PATH", state_path)
    with pytest.raises(SystemExit, match="BLOCKED: validation requires train_gate_pass"):
        runner.require_train_pass_for_validation()


def test_runner_blocks_test_without_lockbox(tmp_path: Path, monkeypatch) -> None:
    import scripts.run_campaign_021_ltf_mtf_confluence as runner

    state_path = tmp_path / "gate_state.json"
    state_path.write_text(json.dumps({"test_lockbox_allowed": False}), encoding="utf-8")
    monkeypatch.setattr(runner, "GATE_STATE_PATH", state_path)
    with pytest.raises(SystemExit, match="BLOCKED: test lockbox"):
        runner.require_lockbox_allowed()


def test_approved_registry_empty() -> None:
    approved = yaml.safe_load(
        (_REPO / "configs/approved_strategies.yaml").read_text(encoding="utf-8")
    )
    assert approved["approved"] == []

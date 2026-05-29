"""CAMPAIGN_027 scaffold-runner guardrails.

Verifies the runner is preflight-only and safe:
  * refuses --train / --validation / --test / --backtest / --execute;
  * --validate-config accepts the frozen identity;
  * preflight writes no trade ledger and a strategy_evidence:false manifest;
  * sample-signals output is marked diagnostic-only with no approval flag.

Output is redirected to a tmp dir so committed preflight artifacts are untouched.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts/run_campaign_027_h4_filtered_zscore_reversion.py"


@pytest.fixture(scope="module")
def runner():
    spec = importlib.util.spec_from_file_location("run_c027", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def tmp_out(runner, tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "OUT_PREFLIGHT", tmp_path)
    return tmp_path


# ---- forbidden evidence modes are refused ----------------------------------

@pytest.mark.parametrize("flag", ["--train", "--validation", "--test", "--backtest", "--execute"])
def test_runner_refuses_evidence_modes(runner, flag):
    with pytest.raises(SystemExit) as exc:
        runner.main([flag])
    assert "REFUSED" in str(exc.value)


def test_validate_config_accepts_frozen_identity(runner):
    assert runner.main(["--validate-config"]) == 0


# ---- preflight writes no trade ledger, evidence:false ----------------------

def test_preflight_writes_no_trade_ledger(runner, tmp_out):
    runner.main(["--preflight-only"])
    written = {p.name for p in tmp_out.iterdir()}
    assert "preflight_result.json" in written
    assert "run_manifest.json" in written
    # no trade ledger / per-bar dump anywhere in the preflight output
    for name in written:
        assert "trade" not in name.lower()
        assert not name.endswith(".csv")
    manifest = json.loads((tmp_out / "run_manifest.json").read_text())
    assert manifest["strategy_evidence"] is False
    assert manifest["test_lockbox_opened"] is False
    assert manifest["full_evidence_run"] is False
    assert manifest["not_approved"] is True


def test_data_feature_preflight_scopes_to_train(runner, tmp_out):
    runner.main(["--data-feature-preflight"])
    report = json.loads((tmp_out / "data_feature_preflight.json").read_text())
    assert report["window"] == ["2020-01-01", "2022-12-31"]  # never the test lockbox
    assert report["strategy_evidence"] is False
    assert report["diagnostic_only"] is True


def test_sample_signals_marked_diagnostic_only(runner, tmp_out):
    runner.main([
        "--sample-signals-only", "--sample-pair", "EUR_USD",
        "--sample-start", "2021-01-01", "--sample-bars", "60",
    ])
    summary = json.loads((tmp_out / "sample_signal_summary.json").read_text())
    assert summary["diagnostic_only"] is True
    assert summary["full_evidence_run"] is False
    assert "approved" not in {k.lower() for k in summary} or summary.get("approved") is not True
    # long counts must be explicitly not-entered
    if summary.get("status") == "OK":
        assert "long_diagnostic_only_not_entered" in summary


def test_no_approval_flag_in_any_manifest(runner, tmp_out):
    runner.main(["--preflight-only"])
    manifest = json.loads((tmp_out / "run_manifest.json").read_text())
    assert manifest.get("approved") is not True
    assert manifest.get("promotion_eligible") is not True
    assert manifest.get("paper_demo_live_enabled") is not True


def test_assert_not_test_window_blocks_lockbox(runner):
    with pytest.raises(SystemExit) as exc:
        runner.assert_not_test_window("2025-06-01", "2025-12-31")
    assert "FAIL_IF_TEST_WINDOW" in str(exc.value)

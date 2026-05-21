"""CLI smoke test for `bot doctor`."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from forex_bot.cli import app

runner = CliRunner()


def test_doctor_reports_missing_creds_cleanly(paper_config_path: Path, monkeypatch, tmp_path):
    """`doctor` must run without OANDA env vars and report missing safely."""
    monkeypatch.delenv("OANDA_ACCOUNT_ID_PRACTICE", raising=False)
    monkeypatch.delenv("OANDA_ACCESS_TOKEN_PRACTICE", raising=False)
    result = runner.invoke(app, ["doctor", "--config", str(paper_config_path)])
    assert result.exit_code == 0, result.output
    assert "missing" in result.output.lower() or "missing" in result.stdout.lower()


def test_doctor_reports_present_with_creds(paper_config_path: Path, monkeypatch):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "001-001-7654321-001")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "abcdef1234567890")
    result = runner.invoke(app, ["doctor", "--config", str(paper_config_path)])
    assert result.exit_code == 0, result.output
    assert "present" in result.output.lower()


def test_doctor_refuses_invalid_config(tmp_path: Path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("not: a: valid: config", encoding="utf-8")
    result = runner.invoke(app, ["doctor", "--config", str(bad)])
    assert result.exit_code != 0


def test_doctor_refuses_live_example_template(live_example_config_path: Path):
    result = runner.invoke(app, ["doctor", "--config", str(live_example_config_path)])
    assert result.exit_code != 0
    assert "invalid" in result.output.lower() or "error" in result.output.lower()

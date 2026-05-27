"""Tests for read-only OANDA financing capture sprint 002."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from forex_bot.research.financing_overlay import (
    FinancingOverlayMode,
    resolve_rate_source,
)
from forex_bot.research.financing_reconciliation import (
    compare_to_synthetic_overlay,
)
from forex_bot.research.oanda_readonly import (
    LIVE_HOST_MARKER,
    ReadonlyEndpointDecision,
    assert_no_token_in_log_line,
    assert_readonly_get_url,
    validate_readonly_get_url,
)
from forex_bot.research.observed_financing_fixture import (
    empty_observed_fixture,
    validate_observed_fixture,
)

ROOT = Path(__file__).resolve().parents[2]
CAPTURE_SCRIPT = ROOT / "scripts" / "capture_oanda_observed_financing_readonly.py"


@pytest.fixture
def capture_mod():
    spec = importlib.util.spec_from_file_location("capture_oanda", CAPTURE_SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_allowed_transaction_endpoint() -> None:
    acct = "101-001-1234567-001"
    url = f"https://api-fxpractice.oanda.com/v3/accounts/{acct}/transactions"
    assert validate_readonly_get_url(url, acct) == ReadonlyEndpointDecision.ALLOW


def test_order_endpoint_rejected() -> None:
    acct = "101-001-1234567-001"
    url = f"https://api-fxpractice.oanda.com/v3/accounts/{acct}/orders"
    with pytest.raises(RuntimeError):
        assert_readonly_get_url(url, acct)


def test_trade_close_rejected() -> None:
    acct = "101-001-1234567-001"
    url = f"https://api-fxpractice.oanda.com/v3/accounts/{acct}/trades/123/close"
    with pytest.raises(RuntimeError):
        assert_readonly_get_url(url, acct)


def test_live_host_rejected() -> None:
    acct = "101-001-1234567-001"
    url = f"https://{LIVE_HOST_MARKER}/v3/accounts/{acct}/transactions"
    with pytest.raises(ValueError, match="live"):
        assert_readonly_get_url(url, acct)


def test_authorization_not_logged() -> None:
    with pytest.raises(ValueError):
        assert_no_token_in_log_line("Authorization: Bearer secret-token")


def test_fixture_rejects_raw_account_id() -> None:
    with pytest.raises(Exception):
        validate_observed_fixture(
            {
                "fixture_version": 1,
                "source": "oanda_practice_observed",
                "captured_at_utc": "2026-05-27T00:00:00+00:00",
                "account_id_hash": "101-001-1234567-001",
                "environment": "practice",
                "entries": [],
            }
        )


def test_empty_fixture_valid() -> None:
    fx = empty_observed_fixture(
        account_id_hash="a" * 64,
        captured_at_utc="2026-05-27T00:00:00+00:00",
        capture_window={"from": "2026-05-01T00:00:00Z", "to": "2026-05-14T00:00:00Z"},
    )
    validate_observed_fixture(fx.model_dump())


def test_capture_default_dry_run_no_network(capture_mod, tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("OANDA_ACCESS_TOKEN_PRACTICE", raising=False)
    monkeypatch.delenv("OANDA_ACCOUNT_ID_PRACTICE", raising=False)
    monkeypatch.setenv("OANDA_ENVIRONMENT", "practice")

    def boom(*_a, **_k):
        raise AssertionError("network called")

    monkeypatch.setattr(capture_mod, "_make_client", boom)
    rc = capture_mod.run(
        ["--output-dir", str(tmp_path), "--start-date", "2026-05-01", "--end-date", "2026-05-14"]
    )
    assert rc == 0
    status = json.loads((tmp_path / "capture_status.json").read_text())
    assert status["network_called"] is False


def test_execute_requires_credentials(capture_mod, tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("OANDA_ACCESS_TOKEN_PRACTICE", raising=False)
    monkeypatch.delenv("OANDA_ACCOUNT_ID_PRACTICE", raising=False)
    monkeypatch.setenv("OANDA_ENVIRONMENT", "practice")
    rc = capture_mod.run(
        [
            "--execute-readonly-capture",
            "--output-dir",
            str(tmp_path),
            "--start-date",
            "2026-05-01",
            "--end-date",
            "2026-05-14",
        ]
    )
    assert rc == 2


def test_observed_overlay_mode_unavailable_without_entries(tmp_path, monkeypatch) -> None:
    empty = empty_observed_fixture(
        account_id_hash="b" * 64,
        captured_at_utc="2026-05-27T00:00:00+00:00",
        capture_window={"from": "x", "to": "y"},
    )
    path = tmp_path / "observed_practice_financing.json"
    path.write_text(json.dumps(empty.model_dump()) + "\n", encoding="utf-8")
    monkeypatch.setattr(
        "forex_bot.research.financing_overlay.OBSERVED_PRACTICE_FIXTURE_PATH",
        path,
    )
    src, label, _, warnings = resolve_rate_source(FinancingOverlayMode.OBSERVED_PRACTICE_FIXTURE)
    assert src is None
    assert "zero entries" in " ".join(warnings).lower()


def test_reconciliation_inconclusive_without_data() -> None:
    result = compare_to_synthetic_overlay(None)
    assert result["conclusion"] == "synthetic_only_no_observed_data"

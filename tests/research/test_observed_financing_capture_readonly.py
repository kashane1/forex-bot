"""Tests for scripts/capture_observed_financing_readonly.py — no network."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "capture_observed_financing_readonly.py"


@pytest.fixture
def cap_module():
    spec = importlib.util.spec_from_file_location("capture_observed_financing_readonly", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _MockResponse:
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> Any:
        return self._payload


class _MockClient:
    def __init__(self, routes: dict[str, _MockResponse]) -> None:
        self._routes = routes
        self.calls: list[tuple[str, dict | None]] = []

    def get(self, url: str, **kwargs: Any) -> _MockResponse:
        self.calls.append((url, kwargs.get("params")))
        for prefix, resp in sorted(self._routes.items(), key=lambda kv: -len(kv[0])):
            if url.startswith(prefix):
                return resp
        return _MockResponse(404, {"error": "missing route"})


@pytest.fixture
def fixture_account_id() -> str:
    return "101-001-1234567-001"


@pytest.fixture
def fixture_token() -> str:
    return "fixture-token-not-real"


def _routes_empty(fixture_account_id: str) -> dict[str, _MockResponse]:
    base = f"https://api-fxpractice.oanda.com/v3/accounts/{fixture_account_id}"
    account = {
        "account": {
            "id": fixture_account_id,
            "currency": "USD",
            "tags": ["PRACTICE"],
        }
    }
    return {
        base: _MockResponse(200, account),
        f"{base}/summary": _MockResponse(200, {"account": {"currency": "USD"}}),
        f"{base}/transactions": _MockResponse(200, {"transactions": []}),
    }


def _routes_with_daily(
    fixture_account_id: str,
    payload_path: Path,
) -> dict[str, _MockResponse]:
    routes = _routes_empty(fixture_account_id)
    tx = json.loads(payload_path.read_text(encoding="utf-8"))
    base = f"https://api-fxpractice.oanda.com/v3/accounts/{fixture_account_id}"
    routes[f"{base}/transactions"] = _MockResponse(200, {"transactions": [tx]})
    return routes


def test_missing_credentials(cap_module, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OANDA_ACCESS_TOKEN_PRACTICE", raising=False)
    monkeypatch.delenv("OANDA_ACCOUNT_ID_PRACTICE", raising=False)
    monkeypatch.setenv("OANDA_ENVIRONMENT", "practice")
    rc = cap_module.run(["--output", str(tmp_path / "out")])
    assert rc == cap_module.EXIT_MISSING_CREDS
    status = json.loads((tmp_path / "out" / "observed_financing_capture_status.json").read_text())
    assert status["status"] == "BLOCKED_CREDENTIALS_MISSING"


def test_live_environment_refused(cap_module, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OANDA_ENVIRONMENT", "live")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "tok")
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "acct")
    rc = cap_module.run(["--output", str(tmp_path / "out")])
    assert rc == cap_module.EXIT_NOT_PRACTICE


def test_denylisted_url_refused(cap_module, fixture_account_id) -> None:
    client = _MockClient({})
    url = f"https://api-fxpractice.oanda.com/v3/accounts/{fixture_account_id}/orders"
    with pytest.raises(RuntimeError, match="denylisted"):
        cap_module._safe_get(client, url, fixture_account_id)


def test_empty_daily_financing(
    cap_module, tmp_path, monkeypatch, fixture_account_id, fixture_token,
) -> None:
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", fixture_token)
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", fixture_account_id)
    monkeypatch.setenv("OANDA_ENVIRONMENT", "practice")

    def factory(_token: str):
        return _MockClient(_routes_empty(fixture_account_id))

    rc = cap_module.run(["--output", str(tmp_path / "out")], client_factory=factory)
    assert rc == cap_module.EXIT_OK
    status = json.loads((tmp_path / "out" / "observed_financing_capture_status.json").read_text())
    assert status["status"] == "OBSERVED_FINANCING_EMPTY"


def test_successful_capture_writes_sanitized(
    cap_module, tmp_path, monkeypatch, fixture_account_id, fixture_token,
) -> None:
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", fixture_token)
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", fixture_account_id)
    monkeypatch.setenv("OANDA_ENVIRONMENT", "practice")
    fixture = REPO_ROOT / "tests/fixtures/observed_financing/daily_financing_one_position.json"

    def factory(_token: str):
        return _MockClient(_routes_with_daily(fixture_account_id, fixture))

    rc = cap_module.run(
        ["--output", str(tmp_path / "out"), "--from-iso", "2024-01-01T00:00:00Z", "--to-iso", "2024-12-31T00:00:00Z"],
        client_factory=factory,
    )
    assert rc == cap_module.EXIT_OK
    sanitized = json.loads((tmp_path / "out" / "observed_daily_financing_sanitized.json").read_text())
    assert sanitized["daily_financing_count"] == 1
    assert sanitized["synthetic"] is False
    blob = json.dumps(sanitized)
    assert fixture_account_id not in blob
    assert "001-001-FIXTURE-001" not in blob

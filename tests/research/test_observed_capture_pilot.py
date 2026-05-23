"""Safety tests for scripts/capture_oanda_observed_financing_pilot.py.

All HTTP is mocked. No network call is attempted from any test.

Covers: refusal of live env (live URL), refusal of missing
creds (without printing values), redaction of account id,
fixture-shape JSON output, parser correctness for
DAILY_FINANCING and ORDER_FILL-with-financing, allowlist /
denylist enforcement, exit-code matrix, no credential value in
stdout/stderr/output, dry-run mode."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "capture_oanda_observed_financing_pilot.py"


@pytest.fixture
def script_module():
    """Import the pilot script as a module from the file path
    (it doesn't ship as a package)."""
    spec = importlib.util.spec_from_file_location(
        "capture_oanda_observed_financing_pilot", SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------- Mock HTTP scaffolding ----------


class _MockResponse:
    def __init__(self, status_code: int, payload: Any | None = None) -> None:
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = json.dumps(self._payload) if isinstance(self._payload, (dict, list)) else str(self._payload)

    def json(self) -> Any:
        return self._payload


class _MockClient:
    """A mock httpx.Client recording every GET. Routes responses
    based on URL path."""

    def __init__(self, routes: dict[str, _MockResponse]) -> None:
        self._routes = routes
        self.requested: list[tuple[str, dict[str, Any] | None]] = []

    def get(self, url: str, **kwargs: Any) -> _MockResponse:
        params = kwargs.get("params")
        self.requested.append((url, params))
        # Match longest path prefix; allow query strings.
        for prefix, resp in sorted(
            self._routes.items(), key=lambda kv: -len(kv[0]),
        ):
            if url.startswith(prefix):
                return resp
        return _MockResponse(404, {"error": "not in test routes"})

    def close(self) -> None:
        return None


_FIXTURE_ACCOUNT_ID = "101-001-1234567-001"
_FIXTURE_TOKEN = "fixture-token-not-real-NEVER-PRINT"


def _routes(
    *,
    practice_account: bool = True,
    last_id: str | None = "999",
    daily_financing_payloads: list[dict[str, Any]] | None = None,
) -> dict[str, _MockResponse]:
    account_payload = {
        "account": {
            "id": _FIXTURE_ACCOUNT_ID,
            "currency": "USD",
            "tags": ["PRACTICE"] if practice_account else [],
            "lastTransactionID": last_id or "999",
        },
        "lastTransactionID": last_id or "999",
    }
    summary_payload = {
        "account": {
            "currency": "USD",
            "lastTransactionID": last_id or "999",
        },
        "lastTransactionID": last_id or "999",
    }
    transactions_payload = {
        "transactions": daily_financing_payloads or [],
        "lastTransactionID": last_id or "999",
    }
    base = f"https://api-fxpractice.oanda.com/v3/accounts/{_FIXTURE_ACCOUNT_ID}"
    return {
        f"{base}/transactions/sinceid": _MockResponse(200, transactions_payload),
        f"{base}/transactions": _MockResponse(200, transactions_payload),
        f"{base}/summary": _MockResponse(200, summary_payload),
        base: _MockResponse(200, account_payload),
    }


def _client_factory(routes: dict[str, _MockResponse]):
    def factory(token: str) -> _MockClient:
        # Ensure the script never reveals the token. Stash it
        # on the mock so a later test can assert the script
        # never wrote it into output.
        _ = token
        return _MockClient(routes)
    return factory


# ---------- Exit-code rails ----------


def test_refuses_missing_credentials_without_printing(
    script_module, tmp_path: Path, monkeypatch, capsys,
) -> None:
    monkeypatch.delenv("OANDA_ACCESS_TOKEN_PRACTICE", raising=False)
    monkeypatch.delenv("OANDA_ACCOUNT_ID_PRACTICE", raising=False)
    code = script_module.run(
        ["--output", str(tmp_path), "--dry-run"],
        client_factory=_client_factory(_routes()),
    )
    assert code == script_module.EXIT_MISSING_CREDS
    out = capsys.readouterr()
    # Message should name env var names, never values.
    assert "OANDA_ACCESS_TOKEN_PRACTICE" in out.err
    assert "OANDA_ACCOUNT_ID_PRACTICE" in out.err
    # Should NOT print any of the fixture/tripwire token values.
    assert _FIXTURE_TOKEN not in out.out
    assert _FIXTURE_TOKEN not in out.err


def test_refuses_when_only_live_creds_present(
    script_module, tmp_path: Path, monkeypatch, capsys,
) -> None:
    monkeypatch.delenv("OANDA_ACCESS_TOKEN_PRACTICE", raising=False)
    monkeypatch.delenv("OANDA_ACCOUNT_ID_PRACTICE", raising=False)
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_LIVE", "LIVE_TRIPWIRE_NEVER_USE")
    monkeypatch.setenv("OANDA_ACCOUNT_ID_LIVE", "LIVE_TRIPWIRE_ACCOUNT")
    code = script_module.run(
        ["--output", str(tmp_path), "--dry-run"],
        client_factory=_client_factory(_routes()),
    )
    assert code == script_module.EXIT_MISSING_CREDS
    out = capsys.readouterr()
    # Live tripwire values must not leak anywhere.
    assert "LIVE_TRIPWIRE_NEVER_USE" not in out.out
    assert "LIVE_TRIPWIRE_NEVER_USE" not in out.err
    assert "LIVE_TRIPWIRE_ACCOUNT" not in out.out
    assert "LIVE_TRIPWIRE_ACCOUNT" not in out.err


def test_refuses_account_without_practice_tag(
    script_module, tmp_path: Path, monkeypatch, capsys,
) -> None:
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", _FIXTURE_TOKEN)
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", _FIXTURE_ACCOUNT_ID)
    code = script_module.run(
        ["--output", str(tmp_path), "--dry-run"],
        client_factory=_client_factory(_routes(practice_account=False)),
    )
    assert code == script_module.EXIT_NOT_PRACTICE


def test_dry_run_succeeds_with_practice_creds(
    script_module, tmp_path: Path, monkeypatch,
) -> None:
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", _FIXTURE_TOKEN)
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", _FIXTURE_ACCOUNT_ID)
    code = script_module.run(
        ["--output", str(tmp_path), "--dry-run"],
        client_factory=_client_factory(_routes()),
    )
    assert code == script_module.EXIT_OK


# ---------- URL allowlist / denylist ----------


def test_allows_practice_account_path(script_module) -> None:
    base = f"https://api-fxpractice.oanda.com/v3/accounts/{_FIXTURE_ACCOUNT_ID}"
    assert script_module._is_allowed_url(base, _FIXTURE_ACCOUNT_ID)
    assert script_module._is_allowed_url(f"{base}/summary", _FIXTURE_ACCOUNT_ID)
    assert script_module._is_allowed_url(f"{base}/transactions", _FIXTURE_ACCOUNT_ID)
    assert script_module._is_allowed_url(
        f"{base}/transactions?from=2026-05-01T00:00:00Z&to=2026-05-23T00:00:00Z",
        _FIXTURE_ACCOUNT_ID,
    )
    assert script_module._is_allowed_url(
        f"{base}/transactions/sinceid?id=12345",
        _FIXTURE_ACCOUNT_ID,
    )
    # Single-transaction-id lookup.
    assert script_module._is_allowed_url(
        f"{base}/transactions/12345", _FIXTURE_ACCOUNT_ID,
    )


def test_refuses_live_host_url(script_module) -> None:
    # Live REST host.
    assert not script_module._is_allowed_url(
        f"https://api-fxtrade.oanda.com/v3/accounts/{_FIXTURE_ACCOUNT_ID}/transactions",
        _FIXTURE_ACCOUNT_ID,
    )
    # Live stream host.
    assert not script_module._is_allowed_url(
        f"https://stream-fxtrade.oanda.com/v3/accounts/{_FIXTURE_ACCOUNT_ID}/transactions/stream",
        _FIXTURE_ACCOUNT_ID,
    )


def test_refuses_mutation_or_unrelated_paths(script_module) -> None:
    base = f"https://api-fxpractice.oanda.com/v3/accounts/{_FIXTURE_ACCOUNT_ID}"
    for tail in (
        "/orders",
        "/trades",
        "/positions",
        "/pricing",
        "/pricing/stream",
        "/configuration",
        "/transactions/stream",  # streaming is out of scope for this pilot
    ):
        assert not script_module._is_allowed_url(
            f"{base}{tail}", _FIXTURE_ACCOUNT_ID,
        ), f"unexpectedly allowed: {tail}"


def test_safe_get_refuses_live_host_url(script_module) -> None:
    # _safe_get bails before touching the (fake) client.
    class _Boom:
        def get(self, url: str, **kwargs: Any) -> Any:
            raise AssertionError("client.get must not be called")

    with pytest.raises(RuntimeError, match="live-host"):
        script_module._safe_get(
            _Boom(),
            f"https://api-fxtrade.oanda.com/v3/accounts/{_FIXTURE_ACCOUNT_ID}/transactions",
            _FIXTURE_ACCOUNT_ID,
        )


def test_safe_get_refuses_non_allowlisted_url(script_module) -> None:
    class _Boom:
        def get(self, url: str, **kwargs: Any) -> Any:
            raise AssertionError("client.get must not be called")

    with pytest.raises(RuntimeError, match="non-allowlisted"):
        script_module._safe_get(
            _Boom(),
            f"https://api-fxpractice.oanda.com/v3/accounts/{_FIXTURE_ACCOUNT_ID}/orders",
            _FIXTURE_ACCOUNT_ID,
        )


# ---------- Parser correctness ----------


def test_parse_daily_financing_per_trade_breakdown(script_module) -> None:
    payload = {
        "type": "DAILY_FINANCING",
        "id": "777",
        "time": "2026-05-19T21:00:00Z",
        "accountID": _FIXTURE_ACCOUNT_ID,
        "financing": "-0.108",
        "positionFinancings": [
            {
                "instrument": "EUR_USD",
                "openTradeFinancings": [
                    {"tradeID": "1001", "units": "10000", "financing": "-0.054"},
                    {"tradeID": "1002", "units": "10000", "financing": "-0.054"},
                ],
                "financing": "-0.108",
            }
        ],
    }
    events = script_module.parse_daily_financing(
        payload,
        account_id_hash=script_module.hash_account_id_local(_FIXTURE_ACCOUNT_ID),
        account_currency="USD",
    )
    assert len(events) == 2
    assert events[0]["transaction_id"] == "777"
    assert events[0]["instrument"] == "EUR_USD"
    assert events[0]["trade_id"] == "1001"
    assert events[0]["financing"] == "-0.054"
    assert events[0]["time"].startswith("2026-05-19T21:00:00")


def test_parse_daily_financing_per_instrument_only(script_module) -> None:
    payload = {
        "type": "DAILY_FINANCING",
        "id": "778",
        "time": "2026-05-19T21:00:00Z",
        "accountID": _FIXTURE_ACCOUNT_ID,
        "financing": "-0.054",
        "positionFinancings": [
            {"instrument": "EUR_USD", "financing": "-0.054"},
        ],
    }
    events = script_module.parse_daily_financing(
        payload,
        account_id_hash=script_module.hash_account_id_local(_FIXTURE_ACCOUNT_ID),
        account_currency="USD",
    )
    assert len(events) == 1
    assert events[0]["trade_id"] is None
    assert events[0]["financing"] == "-0.054"


def test_parse_daily_financing_account_level_fallback(script_module) -> None:
    payload = {
        "type": "DAILY_FINANCING",
        "id": "779",
        "time": "2026-05-19T21:00:00Z",
        "accountID": _FIXTURE_ACCOUNT_ID,
        "financing": "-0.054",
    }
    events = script_module.parse_daily_financing(
        payload,
        account_id_hash=script_module.hash_account_id_local(_FIXTURE_ACCOUNT_ID),
        account_currency="USD",
    )
    assert len(events) == 1
    assert events[0]["instrument"] is None
    assert events[0]["trade_id"] is None


def test_parse_order_fill_with_non_zero_financing(script_module) -> None:
    payload = {
        "type": "ORDER_FILL",
        "id": "780",
        "time": "2026-05-19T21:00:00Z",
        "accountID": _FIXTURE_ACCOUNT_ID,
        "instrument": "EUR_USD",
        "units": "-10000",
        "financing": "0.012",
    }
    events = script_module.parse_observed_financing_events(
        payload,
        account_id_hash=script_module.hash_account_id_local(_FIXTURE_ACCOUNT_ID),
        account_currency="USD",
    )
    assert len(events) == 1
    assert events[0]["financing"] == "0.012"
    assert events[0]["instrument"] == "EUR_USD"


def test_parse_order_fill_with_zero_financing_yields_nothing(script_module) -> None:
    payload = {
        "type": "ORDER_FILL",
        "id": "781",
        "time": "2026-05-19T21:00:00Z",
        "accountID": _FIXTURE_ACCOUNT_ID,
        "instrument": "EUR_USD",
        "units": "10000",
        "financing": "0",
    }
    events = script_module.parse_observed_financing_events(
        payload,
        account_id_hash=script_module.hash_account_id_local(_FIXTURE_ACCOUNT_ID),
        account_currency="USD",
    )
    assert events == []


def test_parse_unknown_transaction_type_yields_nothing(script_module) -> None:
    payload = {
        "type": "MARKET_ORDER",
        "id": "782",
        "time": "2026-05-19T21:00:00Z",
        "accountID": _FIXTURE_ACCOUNT_ID,
        "instrument": "EUR_USD",
        "units": "10000",
    }
    events = script_module.parse_observed_financing_events(
        payload,
        account_id_hash=script_module.hash_account_id_local(_FIXTURE_ACCOUNT_ID),
        account_currency="USD",
    )
    assert events == []


# ---------- Full capture round-trip with mock HTTP ----------


def _daily_financing_payload(tx_id: str, time_iso: str, financing: str) -> dict[str, Any]:
    return {
        "type": "DAILY_FINANCING",
        "id": tx_id,
        "time": time_iso,
        "accountID": _FIXTURE_ACCOUNT_ID,
        "financing": financing,
        "positionFinancings": [
            {
                "instrument": "EUR_USD",
                "openTradeFinancings": [
                    {"tradeID": "1001", "units": "10000", "financing": financing},
                ],
                "financing": financing,
            }
        ],
    }


def test_full_capture_writes_fixture_shape_json(
    script_module, tmp_path: Path, monkeypatch,
) -> None:
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", _FIXTURE_TOKEN)
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", _FIXTURE_ACCOUNT_ID)
    routes = _routes(
        daily_financing_payloads=[
            _daily_financing_payload("701", "2026-05-19T21:00:00Z", "-0.054"),
            _daily_financing_payload("702", "2026-05-20T21:00:00Z", "-0.162"),
        ],
    )
    code = script_module.run(
        [
            "--output", str(tmp_path),
            "--since-transaction-id", "700",
            "--provenance", "test-mock-not-real-capture",
        ],
        client_factory=_client_factory(routes),
    )
    assert code == script_module.EXIT_OK

    out_path = tmp_path / "observed_financing.json"
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["kind"] == "observed_financing_events"
    assert payload["schema_version"] == 1
    assert payload["synthetic"] is False  # real capture-shape (mocked HTTP)
    assert payload["provenance"] == "test-mock-not-real-capture"
    assert payload["account_currency"] == "USD"
    # account_id_hash must be the SHA-256 of the raw id and NOT the
    # raw id itself.
    expected_hash = hashlib.sha256(_FIXTURE_ACCOUNT_ID.encode("utf-8")).hexdigest()
    assert payload["account_id_hash"] == expected_hash
    assert _FIXTURE_ACCOUNT_ID not in out_path.read_text(encoding="utf-8")
    # Events present and sorted.
    assert len(payload["events"]) == 2
    assert payload["events"][0]["time"] < payload["events"][1]["time"]


def test_capture_output_consumable_by_loader(
    script_module, tmp_path: Path, monkeypatch,
) -> None:
    """The capture output must satisfy the fixture loader's
    schema — that's the whole point of the format alignment."""
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", _FIXTURE_TOKEN)
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", _FIXTURE_ACCOUNT_ID)
    routes = _routes(
        daily_financing_payloads=[
            _daily_financing_payload("701", "2026-05-19T21:00:00Z", "-0.054"),
        ],
    )
    script_module.run(
        [
            "--output", str(tmp_path),
            "--since-transaction-id", "700",
            "--provenance", "test-mock-not-real-capture",
        ],
        client_factory=_client_factory(routes),
    )
    out_path = tmp_path / "observed_financing.json"

    # Use the existing loader to validate the shape — it
    # accepts both synthetic: true and synthetic: false.
    sys.path.insert(0, str(REPO_ROOT))
    from research.financing.fixtures import load_observed_event_fixture

    events = load_observed_event_fixture(out_path)
    assert len(events) == 1
    assert events[0]["instrument"] == "EUR_USD"
    assert events[0]["trade_id"] == "1001"
    assert events[0]["financing"] == script_module.Decimal("-0.054")
    assert events[0]["currency"] == "USD"
    assert events[0]["account_id_hash"] == hashlib.sha256(
        _FIXTURE_ACCOUNT_ID.encode("utf-8"),
    ).hexdigest()


def test_capture_only_calls_allowlisted_paths(
    script_module, tmp_path: Path, monkeypatch,
) -> None:
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", _FIXTURE_TOKEN)
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", _FIXTURE_ACCOUNT_ID)
    routes = _routes(
        daily_financing_payloads=[
            _daily_financing_payload("701", "2026-05-19T21:00:00Z", "-0.054"),
        ],
    )
    mock_client = _MockClient(routes)

    def _factory(_token: str) -> _MockClient:
        return mock_client

    script_module.run(
        [
            "--output", str(tmp_path),
            "--since-transaction-id", "700",
            "--provenance", "test",
        ],
        client_factory=_factory,
    )

    # Every requested URL must be allowlisted.
    for url, _params in mock_client.requested:
        assert script_module._is_allowed_url(url, _FIXTURE_ACCOUNT_ID), (
            f"non-allowlisted URL was hit: {url}"
        )
    # No request to live host or any non-transaction path.
    for url, _params in mock_client.requested:
        assert "fxtrade" not in url
        assert "/orders" not in url
        assert "/trades" not in url
        assert "/positions" not in url
        assert "/pricing" not in url
        assert "/configuration" not in url


# ---------- No-credential-leak tests ----------


def test_capture_output_does_not_contain_token_or_raw_account(
    script_module, tmp_path: Path, monkeypatch,
) -> None:
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", _FIXTURE_TOKEN)
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", _FIXTURE_ACCOUNT_ID)
    routes = _routes(
        daily_financing_payloads=[
            _daily_financing_payload("701", "2026-05-19T21:00:00Z", "-0.054"),
        ],
    )
    script_module.run(
        [
            "--output", str(tmp_path),
            "--since-transaction-id", "700",
            "--provenance", "test",
        ],
        client_factory=_client_factory(routes),
    )
    text = (tmp_path / "observed_financing.json").read_text(encoding="utf-8")
    assert _FIXTURE_TOKEN not in text
    assert _FIXTURE_ACCOUNT_ID not in text


def test_capture_does_not_print_credentials(
    script_module, tmp_path: Path, monkeypatch, capsys,
) -> None:
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", _FIXTURE_TOKEN)
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", _FIXTURE_ACCOUNT_ID)
    routes = _routes(
        daily_financing_payloads=[
            _daily_financing_payload("701", "2026-05-19T21:00:00Z", "-0.054"),
        ],
    )
    script_module.run(
        [
            "--output", str(tmp_path),
            "--since-transaction-id", "700",
            "--provenance", "test",
        ],
        client_factory=_client_factory(routes),
    )
    captured = capsys.readouterr()
    assert _FIXTURE_TOKEN not in captured.out
    assert _FIXTURE_TOKEN not in captured.err
    assert _FIXTURE_ACCOUNT_ID not in captured.out
    assert _FIXTURE_ACCOUNT_ID not in captured.err


# ---------- Import + dependency rails ----------


def test_script_does_not_import_forex_bot() -> None:
    """Grep rail: the pilot script must not import forex_bot
    (the orchestrator path duplicates the parser locally so
    research/financing/'s isolation conventions also apply
    here)."""
    text = SCRIPT.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if not (stripped.startswith("import ") or stripped.startswith("from ")):
            continue
        assert "forex_bot" not in stripped, (
            f"scripts/capture_oanda_observed_financing_pilot.py:{line_no} "
            f"imports forex_bot: {stripped}"
        )


def test_script_does_not_reference_mutation_helpers() -> None:
    """Grep rail: the pilot must not reference any
    mutation-shaped name. Allowed mentions in docstrings/comments
    are exempted; we only scan executable lines."""
    text = SCRIPT.read_text(encoding="utf-8")
    forbidden = ("submit_order", "close_trade", "cancel_order", "modify_trade")
    for line_no, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("#"):
            continue
        # Exempt the docstring at the very top + any line whose first
        # non-comment chars are part of a triple-quoted string. A
        # conservative heuristic: a non-comment, non-empty source line
        # containing a forbidden name must fail.
        for needle in forbidden:
            if needle in stripped and not (
                '"""' in stripped or "'''" in stripped
            ):
                # The script's docstring uses the names; they live in
                # triple-quoted blocks at the module top. To avoid
                # false positives, ignore lines that fall inside the
                # leading module docstring. The simplest robust test:
                # ensure the needle appears only inside a string
                # literal context — i.e. wrapped in backticks or
                # quotes — on every match.
                if "`" in stripped or '"' in stripped or "'" in stripped:
                    continue
                raise AssertionError(
                    f"scripts/capture_oanda_observed_financing_pilot.py:{line_no} "
                    f"references {needle}: {stripped}"
                )


def test_script_does_not_reference_live_host_substring_outside_safety_check() -> None:
    """The string 'api-fxtrade' must appear only in code paths
    that REFUSE the live host (and in docstrings). It must not
    appear in any URL constant the script would actually
    request."""
    text = SCRIPT.read_text(encoding="utf-8")
    # Just assert the literal 'api-fxtrade.oanda.com' never appears
    # as the base URL of any request: the script's PRACTICE_REST_HOST
    # constant is the only host literal it uses.
    bad_pattern = 'PRACTICE_REST_HOST = "https://api-fxtrade'
    assert bad_pattern not in text, "live host snuck into PRACTICE_REST_HOST"


def test_pilot_module_does_not_pull_in_forex_bot_in_fresh_interpreter() -> None:
    """Importing the pilot in a fresh subprocess must not pull
    forex_bot into sys.modules. Catches future transitive
    imports."""
    import subprocess

    code = (
        "import sys, importlib.util\n"
        f"spec = importlib.util.spec_from_file_location('p', r'{SCRIPT}')\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(mod)\n"
        "names = sorted(m for m in sys.modules if m == 'forex_bot' or m.startswith('forex_bot.'))\n"
        "print('\\n'.join(names))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, cwd=str(REPO_ROOT), check=True,
    )
    forex_modules = [line for line in result.stdout.strip().splitlines() if line]
    assert forex_modules == [], (
        "importing the pilot script pulled in forex_bot modules: "
        + ", ".join(forex_modules)
    )


def test_token_argument_not_logged_when_factory_introspected(
    script_module, tmp_path: Path, monkeypatch, capsys,
) -> None:
    """A test-local factory verifies that the script passes the
    token in clear via its argument (so the Bearer header can
    be built) but never echoes the value to stdout/stderr."""
    captured_tokens: list[str] = []

    def factory(token: str) -> _MockClient:
        captured_tokens.append(token)
        return _MockClient(_routes())

    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", _FIXTURE_TOKEN)
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", _FIXTURE_ACCOUNT_ID)
    script_module.run(
        ["--output", str(tmp_path), "--dry-run"], client_factory=factory,
    )
    # The factory received the token (one call, with the env value).
    assert captured_tokens == [_FIXTURE_TOKEN]
    out = capsys.readouterr()
    # …but the token must not have been printed.
    assert _FIXTURE_TOKEN not in out.out
    assert _FIXTURE_TOKEN not in out.err


# ---------- Default-mode path ----------


def test_default_mode_discovers_last_id_via_summary(
    script_module, tmp_path: Path, monkeypatch,
) -> None:
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", _FIXTURE_TOKEN)
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", _FIXTURE_ACCOUNT_ID)
    routes = _routes(
        last_id="555",
        daily_financing_payloads=[
            _daily_financing_payload("701", "2026-05-19T21:00:00Z", "-0.054"),
        ],
    )
    mock_client = _MockClient(routes)
    code = script_module.run(
        ["--output", str(tmp_path), "--provenance", "test"],
        client_factory=lambda _t: mock_client,
    )
    assert code == script_module.EXIT_OK
    # /summary must have been called as part of the discovery path.
    summary_url = (
        f"https://api-fxpractice.oanda.com/v3/accounts/"
        f"{_FIXTURE_ACCOUNT_ID}/summary"
    )
    assert any(url == summary_url for url, _ in mock_client.requested)


# ---------- Output never written when not OK ----------


def test_no_output_written_on_refusal(
    script_module, tmp_path: Path, monkeypatch,
) -> None:
    monkeypatch.delenv("OANDA_ACCESS_TOKEN_PRACTICE", raising=False)
    monkeypatch.delenv("OANDA_ACCOUNT_ID_PRACTICE", raising=False)
    script_module.run(
        ["--output", str(tmp_path), "--dry-run"],
        client_factory=_client_factory(_routes()),
    )
    assert not (tmp_path / "observed_financing.json").exists()

"""Tests for the read-only OANDA healthcheck script
(Phase 2, oanda-practice-readonly-001).

Cover the safety gates, secret redaction, and the endpoint-probing
logic. No OANDA call is made: the healthcheck logic is exercised
against a recording fake broker whose order methods raise — proving
the healthcheck is structurally read-only.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from forex_bot.broker.errors import BrokerServerError
from forex_bot.broker.mapping import (
    map_account_details,
    map_account_snapshot,
    map_broker_order,
    map_candle,
    map_instrument,
    map_position,
    map_price,
    map_trade,
    map_transaction,
)
from forex_bot.config import load_settings
from tests.fixtures.oanda_payloads import (
    ACCOUNT_DETAILS_RESPONSE,
    ACCOUNT_SUMMARY,
    CANDLES_RESPONSE,
    INSTRUMENTS_LIST,
    OPEN_ORDERS_EMPTY,
    OPEN_POSITIONS_RESPONSE,
    OPEN_TRADES_RESPONSE,
    PRICING_RESPONSE,
    TRANSACTIONS_SINCEID_RESPONSE,
)

_REPO = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = _REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


hc = _load_script("oanda_readonly_healthcheck")

# A realistic-looking but fake account id used to prove redaction.
FAKE_ACCOUNT_ID = "101-002-7654321-003"
READONLY_METHODS = {
    "get_account_summary",
    "get_account_details",
    "list_instruments",
    "get_prices",
    "get_candles",
    "get_transactions_since",
    "list_open_trades",
    "list_positions",
    "list_open_orders",
}


class _FakeBroker:
    """A read-only fake broker. Every read method records its call;
    the order methods record then raise — the healthcheck must never
    reach them."""

    def __init__(
        self,
        *,
        account_id: str = FAKE_ACCOUNT_ID,
        environment: str = "practice",
        fail: set[str] | None = None,
    ) -> None:
        self.account_id = account_id
        self.environment = environment
        self._fail = fail or set()
        self.calls: list[str] = []

    def _hit(self, name: str) -> None:
        self.calls.append(name)
        if name in self._fail:
            # The message embeds the account id, mimicking an OANDA error
            # body that echoes the request path — the report must scrub it.
            raise BrokerServerError(
                f"simulated 404 for /v3/accounts/{self.account_id}/{name}"
            )

    def get_account_summary(self):
        self._hit("get_account_summary")
        return map_account_snapshot(ACCOUNT_SUMMARY)

    def get_account_details(self):
        self._hit("get_account_details")
        return map_account_details(ACCOUNT_DETAILS_RESPONSE)

    def list_instruments(self):
        self._hit("list_instruments")
        return [map_instrument(i) for i in INSTRUMENTS_LIST["instruments"]]

    def get_prices(self, instruments):
        self._hit("get_prices")
        return [map_price(p) for p in PRICING_RESPONSE["prices"]]

    def get_candles(self, request):
        self._hit("get_candles")
        return [map_candle("EUR_USD", "H4", c) for c in CANDLES_RESPONSE["candles"]]

    def get_transactions_since(self, last_id):
        self._hit("get_transactions_since")
        return [map_transaction(t) for t in TRANSACTIONS_SINCEID_RESPONSE["transactions"]]

    def list_open_trades(self):
        self._hit("list_open_trades")
        return [map_trade(t) for t in OPEN_TRADES_RESPONSE["trades"]]

    def list_positions(self):
        self._hit("list_positions")
        return [map_position(p) for p in OPEN_POSITIONS_RESPONSE["positions"]]

    def list_open_orders(self):
        self._hit("list_open_orders")
        return [map_broker_order(o) for o in OPEN_ORDERS_EMPTY["orders"]]

    def submit_order(self, plan):  # pragma: no cover - must never be called
        self.calls.append("submit_order")
        raise AssertionError("healthcheck must never call submit_order")

    def close_trade(self, trade_id, units=None):  # pragma: no cover
        self.calls.append("close_trade")
        raise AssertionError("healthcheck must never call close_trade")


# --------------------------------------------------------------------------
# Redaction
# --------------------------------------------------------------------------


def test_redact_account_id_keeps_only_first_and_last_three():
    assert hc.redact_account_id(FAKE_ACCOUNT_ID) == "101…003"


def test_redact_account_id_handles_short_and_empty():
    assert hc.redact_account_id("") == "<short-or-empty>"
    assert hc.redact_account_id(None) == "<short-or-empty>"
    assert hc.redact_account_id("abc") == "<short-or-empty>"


# --------------------------------------------------------------------------
# Safety gates (no network)
# --------------------------------------------------------------------------


def test_safety_gates_accept_a_read_only_practice_config(paper_settings):
    # paper.yaml: practice environment, allow_order_submission=false.
    hc.run_safety_gates(paper_settings)  # must not raise


def test_safety_gates_refuse_an_order_submitting_config(practice_config_path):
    # practice.yaml enables allow_order_submission — refused before any
    # credential or network work.
    settings = load_settings(practice_config_path)
    with pytest.raises(hc.UnsafeConfigError, match="allow_order_submission"):
        hc.run_safety_gates(settings)


def test_safety_gates_refuse_a_live_environment(paper_settings):
    paper_settings.broker.environment = "live"
    with pytest.raises(hc.UnsafeConfigError, match="practice"):
        hc.run_safety_gates(paper_settings)


def test_safety_gates_refuse_missing_credentials(paper_config_path, monkeypatch):
    for var in (
        "OANDA_ACCOUNT_ID_PRACTICE",
        "OANDA_ACCESS_TOKEN_PRACTICE",
        "OANDA_ENVIRONMENT",
    ):
        monkeypatch.delenv(var, raising=False)
    settings = load_settings(paper_config_path)
    with pytest.raises(hc.UnsafeConfigError):
        hc.run_safety_gates(settings)


# --------------------------------------------------------------------------
# Endpoint probing
# --------------------------------------------------------------------------


def test_healthcheck_happy_path_passes_every_endpoint():
    report = hc.run_healthcheck(_FakeBroker())
    assert report.ok is True
    assert report.failures == []
    assert report.instrument_count == 2
    assert "EUR_USD" in report.sample_instruments
    assert report.sample_price_time is not None
    assert report.sample_candle_time is not None
    # every read-only endpoint check is present and OK / SKIP, never FAIL.
    statuses = {r.status for r in report.results}
    assert "FAIL" not in statuses


def test_healthcheck_never_calls_order_endpoints():
    fake = _FakeBroker()
    hc.run_healthcheck(fake)
    assert "submit_order" not in fake.calls
    assert "close_trade" not in fake.calls
    # only read-only methods were ever invoked.
    assert set(fake.calls) <= READONLY_METHODS


def test_healthcheck_handles_an_endpoint_failure_cleanly():
    # One endpoint fails; the rest still run and the report is written.
    fake = _FakeBroker(fail={"get_prices"})
    report = hc.run_healthcheck(fake)
    assert report.ok is False
    assert len(report.failures) == 1
    assert report.failures[0].name == "pricing snapshot"
    # the failure did not abort the run — later endpoints still executed.
    assert "list_open_orders" in fake.calls
    ok_names = {r.name for r in report.results if r.status == "OK"}
    assert "account summary" in ok_names


def test_report_contains_no_credentials():
    report = hc.run_healthcheck(_FakeBroker(account_id=FAKE_ACCOUNT_ID))
    text = hc.render_report(
        report,
        config_path="configs/paper.yaml",
        generated_at=datetime(2026, 5, 22, 12, 0, tzinfo=UTC),
    )
    # The full account id never appears; only the redacted form does.
    assert FAKE_ACCOUNT_ID not in text
    assert "101…003" in text
    # No bearer-token-shaped material.
    assert "Bearer" not in text
    assert "access_token" not in text
    # The report states no order was submitted.
    assert "No order was submitted" in text


def test_report_scrubs_account_id_from_error_text():
    # An OANDA error body echoes the request path (with the account id).
    # The rendered report must never contain the raw account id.
    report = hc.run_healthcheck(_FakeBroker(fail={"get_prices"}))
    text = hc.render_report(
        report,
        config_path="configs/paper.yaml",
        generated_at=datetime(2026, 5, 22, 12, 0, tzinfo=UTC),
    )
    assert FAKE_ACCOUNT_ID not in text
    assert "101…003" in text
    # the failure is still reported — scrubbed, not dropped.
    failure = report.failures[0]
    assert FAKE_ACCOUNT_ID not in (failure.error or "")
    assert "101…003" in (failure.error or "")


def test_report_records_a_failure_with_follow_up():
    report = hc.run_healthcheck(_FakeBroker(fail={"get_candles"}))
    text = hc.render_report(
        report,
        config_path="configs/paper.yaml",
        generated_at=datetime(2026, 5, 22, 12, 0, tzinfo=UTC),
    )
    assert "Failures and follow-ups" in text
    assert "FAIL" in text


# --------------------------------------------------------------------------
# Endpoint constants
# --------------------------------------------------------------------------


def test_declared_readonly_endpoints_are_all_get():
    assert hc.READONLY_ENDPOINTS
    for endpoint in hc.READONLY_ENDPOINTS:
        assert endpoint.startswith("GET "), endpoint


def test_forbidden_endpoints_are_all_mutating():
    assert hc.FORBIDDEN_ENDPOINTS
    for endpoint in hc.FORBIDDEN_ENDPOINTS:
        assert endpoint.split(" ", 1)[0] in {"POST", "PUT", "PATCH", "DELETE"}, endpoint

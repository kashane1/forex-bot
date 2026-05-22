"""HTTP-level tests with respx-mocked OANDA responses."""

from __future__ import annotations

from decimal import Decimal

import httpx
import pytest
import respx

from forex_bot.broker.errors import BrokerAuthError
from forex_bot.broker.oanda import OandaBroker
from forex_bot.clock import utcnow
from forex_bot.config import ConfigError
from forex_bot.domain.candles import CandleRequest
from forex_bot.domain.orders import OrderPlan
from tests.fixtures.oanda_payloads import (
    ACCOUNT_DETAILS_RESPONSE,
    ACCOUNT_SUMMARY,
    CANDLES_RESPONSE,
    INSTRUMENTS_LIST,
    OPEN_ORDERS_EMPTY,
    ORDER_FILL_RESPONSE,
    ORDER_REJECT_RESPONSE,
    PRICING_RESPONSE,
    TRANSACTIONS_SINCEID_RESPONSE,
)

ACCOUNT_ID = "001-001-1234567-001"
BASE = "https://api-fxpractice.oanda.com"


def _broker() -> OandaBroker:
    return OandaBroker(
        environment="practice",
        account_id=ACCOUNT_ID,
        access_token="test-token",
    )


@respx.mock
def test_get_account_summary():
    respx.get(f"{BASE}/v3/accounts/{ACCOUNT_ID}/summary").mock(
        return_value=httpx.Response(200, json=ACCOUNT_SUMMARY)
    )
    snap = _broker().get_account_summary()
    assert snap.account_id == ACCOUNT_ID
    assert snap.nav == Decimal("498.4500")


@respx.mock
def test_list_instruments():
    respx.get(f"{BASE}/v3/accounts/{ACCOUNT_ID}/instruments").mock(
        return_value=httpx.Response(200, json=INSTRUMENTS_LIST)
    )
    out = _broker().list_instruments()
    assert {i.name for i in out} == {"EUR_USD", "USD_JPY"}


@respx.mock
def test_get_candles_marks_complete_flag():
    respx.get(
        f"{BASE}/v3/accounts/{ACCOUNT_ID}/instruments/EUR_USD/candles"
    ).mock(return_value=httpx.Response(200, json=CANDLES_RESPONSE))
    out = _broker().get_candles(
        CandleRequest(instrument="EUR_USD", granularity="H4", price="BA", count=2)
    )
    assert len(out) == 2
    assert out[0].complete is True
    assert out[1].complete is False


@respx.mock
def test_get_prices_parses_bid_ask():
    respx.get(f"{BASE}/v3/accounts/{ACCOUNT_ID}/pricing").mock(
        return_value=httpx.Response(200, json=PRICING_RESPONSE)
    )
    quotes = _broker().get_prices(["EUR_USD"])
    assert len(quotes) == 1
    assert quotes[0].bid == Decimal("1.07990")


@respx.mock
def test_auth_error_raises():
    respx.get(f"{BASE}/v3/accounts/{ACCOUNT_ID}/summary").mock(
        return_value=httpx.Response(401, json={"errorMessage": "bad token"})
    )
    with pytest.raises(BrokerAuthError):
        _broker().get_account_summary()


@respx.mock
def test_submit_order_fill_returns_fill_result():
    respx.post(f"{BASE}/v3/accounts/{ACCOUNT_ID}/orders").mock(
        return_value=httpx.Response(201, json=ORDER_FILL_RESPONSE)
    )
    plan = OrderPlan(
        plan_id="p1",
        signal_id="s1",
        strategy_name="trend_following",
        strategy_version="0.1.0",
        instrument="EUR_USD",
        side="buy",
        units=Decimal("100"),
        stop_loss_price=Decimal("1.07810"),
        client_order_id="fbot-abc",
        config_hash="cfghash",
        created_at=utcnow(),
    )
    result = _broker().submit_order(plan)
    assert result.status == "FILLED"
    assert result.fill_price == Decimal("1.08015")


@respx.mock
def test_submit_order_400_returns_rejected_not_raise():
    respx.post(f"{BASE}/v3/accounts/{ACCOUNT_ID}/orders").mock(
        return_value=httpx.Response(400, json={"errorCode": "MARKET_HALTED"})
    )
    plan = OrderPlan(
        plan_id="p1",
        signal_id="s1",
        strategy_name="trend_following",
        strategy_version="0.1.0",
        instrument="EUR_USD",
        side="buy",
        units=Decimal("100"),
        stop_loss_price=Decimal("1.07810"),
        client_order_id="fbot-abc",
        config_hash="cfghash",
        created_at=utcnow(),
    )
    result = _broker().submit_order(plan)
    assert result.status == "REJECTED"
    assert result.error_code == "MARKET_HALTED"


@respx.mock
def test_submit_order_reject_transaction_returns_rejected():
    respx.post(f"{BASE}/v3/accounts/{ACCOUNT_ID}/orders").mock(
        return_value=httpx.Response(201, json=ORDER_REJECT_RESPONSE)
    )
    plan = OrderPlan(
        plan_id="p1",
        signal_id="s1",
        strategy_name="trend_following",
        strategy_version="0.1.0",
        instrument="EUR_USD",
        side="buy",
        units=Decimal("100"),
        stop_loss_price=Decimal("1.07810"),
        client_order_id="fbot-abc",
        config_hash="cfghash",
        created_at=utcnow(),
    )
    result = _broker().submit_order(plan)
    assert result.status == "REJECTED"


@respx.mock
def test_submit_order_refused_on_live_environment():
    broker = OandaBroker(
        environment="live",
        account_id=ACCOUNT_ID,
        access_token="live-token",
    )
    plan = OrderPlan(
        plan_id="p1",
        signal_id="s1",
        strategy_name="t",
        strategy_version="0",
        instrument="EUR_USD",
        side="buy",
        units=Decimal("100"),
        stop_loss_price=Decimal("1.07810"),
        client_order_id="fbot-abc",
        config_hash="c",
        created_at=utcnow(),
    )
    with pytest.raises(ConfigError):
        broker.submit_order(plan)


@respx.mock
def test_transactions_since_id():
    respx.get(
        f"{BASE}/v3/accounts/{ACCOUNT_ID}/transactions/sinceid"
    ).mock(return_value=httpx.Response(200, json=TRANSACTIONS_SINCEID_RESPONSE))
    txs = _broker().get_transactions_since("41")
    assert {t.transaction_id for t in txs} == {"42", "43"}


@respx.mock
def test_account_details_round_trip():
    respx.get(f"{BASE}/v3/accounts/{ACCOUNT_ID}").mock(
        return_value=httpx.Response(200, json=ACCOUNT_DETAILS_RESPONSE)
    )
    details = _broker().get_account_details()
    assert "200" in details.open_trade_ids
    assert "EUR_USD" in details.open_position_instruments


@respx.mock
def test_get_candles_count_only_omits_include_first():
    # A count-only request must NOT send `includeFirst` — real OANDA
    # returns HTTP 400 when `includeFirst` is sent without `from`.
    route = respx.get(
        f"{BASE}/v3/accounts/{ACCOUNT_ID}/instruments/EUR_USD/candles"
    ).mock(return_value=httpx.Response(200, json=CANDLES_RESPONSE))
    _broker().get_candles(
        CandleRequest(instrument="EUR_USD", granularity="H4", price="BA", count=2)
    )
    params = route.calls.last.request.url.params
    assert "includeFirst" not in params
    assert params["count"] == "2"


@respx.mock
def test_get_candles_with_from_includes_include_first():
    # When `from` is specified, `includeFirst` is meaningful and IS sent.
    route = respx.get(
        f"{BASE}/v3/accounts/{ACCOUNT_ID}/instruments/EUR_USD/candles"
    ).mock(return_value=httpx.Response(200, json=CANDLES_RESPONSE))
    _broker().get_candles(
        CandleRequest(
            instrument="EUR_USD",
            granularity="H4",
            price="BA",
            from_time=utcnow(),
            include_first=True,
        )
    )
    assert route.calls.last.request.url.params["includeFirst"] == "true"


@respx.mock
def test_list_open_orders_uses_pending_orders_endpoint():
    # OANDA v20 has no /openOrders route; pending orders live at
    # /pendingOrders (a /openOrders call 404s as an unrecognized endpoint).
    route = respx.get(
        f"{BASE}/v3/accounts/{ACCOUNT_ID}/pendingOrders"
    ).mock(return_value=httpx.Response(200, json=OPEN_ORDERS_EMPTY))
    out = _broker().list_open_orders()
    assert out == []
    assert route.called

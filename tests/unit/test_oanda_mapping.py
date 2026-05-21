"""Pure mapping tests: OANDA JSON → domain models."""

from __future__ import annotations

from decimal import Decimal

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
from tests.fixtures.oanda_payloads import (
    ACCOUNT_DETAILS_RESPONSE,
    ACCOUNT_SUMMARY,
    CANDLES_RESPONSE,
    INSTRUMENTS_LIST,
    OPEN_POSITIONS_RESPONSE,
    OPEN_TRADES_RESPONSE,
    PRICING_RESPONSE,
    TRANSACTIONS_SINCEID_RESPONSE,
)


def test_map_account_snapshot():
    snap = map_account_snapshot(ACCOUNT_SUMMARY)
    assert snap.account_id == "001-001-1234567-001"
    assert snap.currency == "USD"
    assert snap.nav == Decimal("498.4500")
    assert snap.open_trade_count == 1
    assert snap.last_transaction_id == "42"


def test_map_account_details_lists_trades_positions():
    details = map_account_details(ACCOUNT_DETAILS_RESPONSE)
    assert details.open_trade_ids == ["200"]
    assert details.open_position_instruments == ["EUR_USD"]
    assert details.snapshot.nav == Decimal("500.5000")


def test_map_instrument_keeps_metadata():
    inst = map_instrument(INSTRUMENTS_LIST["instruments"][0])
    assert inst.name == "EUR_USD"
    assert inst.pip_location == -4
    assert inst.display_precision == 5
    assert inst.margin_rate == Decimal("0.02")
    assert inst.minimum_trade_size == Decimal("1")
    assert inst.pip_size == Decimal("0.0001")


def test_map_candle_marks_complete_and_incomplete():
    candles = [
        map_candle("EUR_USD", "H4", c) for c in CANDLES_RESPONSE["candles"]
    ]
    assert len(candles) == 2
    assert candles[0].complete is True
    assert candles[1].complete is False
    assert candles[0].bid_c == Decimal("1.0805")
    assert candles[0].ask_c == Decimal("1.0807")


def test_map_price_extracts_bid_ask():
    quote = map_price(PRICING_RESPONSE["prices"][0])
    assert quote.bid == Decimal("1.07990")
    assert quote.ask == Decimal("1.08010")
    assert quote.tradeable is True


def test_map_trade_carries_stop_loss_order():
    trade = map_trade(OPEN_TRADES_RESPONSE["trades"][0])
    assert trade.trade_id == "200"
    assert trade.stop_loss_order_id == "201"


def test_map_position_signs_short_units_negative():
    pos = map_position(OPEN_POSITIONS_RESPONSE["positions"][0])
    assert pos.long_units == Decimal("100")
    assert pos.short_units == Decimal("0")
    assert pos.net_units == Decimal("100")
    assert not pos.is_flat


def test_map_transactions_round_trip():
    txs = [map_transaction(t) for t in TRANSACTIONS_SINCEID_RESPONSE["transactions"]]
    assert txs[0].transaction_id == "42"
    assert txs[1].pl == Decimal("0")


def test_map_broker_order_keeps_client_id():
    payload = {
        "id": "300",
        "instrument": "EUR_USD",
        "state": "PENDING",
        "type": "MARKET",
        "units": "100",
        "createTime": "2026-05-21T12:00:00.000000000Z",
        "clientExtensions": {"id": "fbot-abc"},
    }
    order = map_broker_order(payload)
    assert order.client_order_id == "fbot-abc"
    assert order.units == Decimal("100")

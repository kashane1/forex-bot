"""Pure functions that translate OANDA v20 JSON to domain objects."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from forex_bot.clock import parse_rfc3339, utcnow
from forex_bot.domain.account import AccountDetails, AccountSnapshot
from forex_bot.domain.candles import Candle, Granularity
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import Quote, SpreadSnapshot
from forex_bot.domain.orders import BrokerOrder
from forex_bot.domain.positions import Position, Trade
from forex_bot.domain.transactions import Heartbeat, Transaction


def _dec(value: Any, default: Decimal | None = None) -> Decimal | None:
    if value is None or value == "":
        return default
    return Decimal(str(value))


def map_instrument(payload: dict[str, Any]) -> Instrument:
    return Instrument(
        name=payload["name"],
        type=payload.get("type", "CURRENCY"),
        display_name=payload.get("displayName"),
        display_precision=int(payload["displayPrecision"]),
        pip_location=int(payload["pipLocation"]),
        trade_units_precision=int(payload["tradeUnitsPrecision"]),
        minimum_trade_size=_dec(payload.get("minimumTradeSize"), Decimal("1")) or Decimal("1"),
        maximum_order_units=_dec(payload.get("maximumOrderUnits")),
        maximum_position_size=_dec(payload.get("maximumPositionSize")),
        margin_rate=_dec(payload.get("marginRate"), Decimal("0.05")) or Decimal("0.05"),
        minimum_trailing_stop_distance=_dec(payload.get("minimumTrailingStopDistance")),
        maximum_trailing_stop_distance=_dec(payload.get("maximumTrailingStopDistance")),
    )


def map_account_snapshot(payload: dict[str, Any]) -> AccountSnapshot:
    summary = payload.get("account", payload)
    last_tx = summary.get("lastTransactionID") or payload.get("lastTransactionID")
    return AccountSnapshot(
        account_id=summary["id"],
        currency=summary["currency"],
        balance=Decimal(str(summary["balance"])),
        nav=Decimal(str(summary.get("NAV", summary.get("balance")))),
        margin_used=Decimal(str(summary.get("marginUsed", "0"))),
        margin_available=Decimal(str(summary.get("marginAvailable", "0"))),
        margin_closeout_percent=Decimal(str(summary.get("marginCloseoutPercent", "0"))),
        unrealized_pl=Decimal(str(summary.get("unrealizedPL", "0"))),
        pl=Decimal(str(summary.get("pl", "0"))),
        open_trade_count=int(summary.get("openTradeCount", 0)),
        open_position_count=int(summary.get("openPositionCount", 0)),
        pending_order_count=int(summary.get("pendingOrderCount", 0)),
        last_transaction_id=last_tx,
        time=utcnow(),
        raw=summary,
    )


def map_account_details(payload: dict[str, Any]) -> AccountDetails:
    snapshot = map_account_snapshot(payload)
    account = payload.get("account", payload)
    open_trades = [t["id"] for t in account.get("trades", []) if "id" in t]
    open_positions = [
        p["instrument"]
        for p in account.get("positions", [])
        if Decimal(str(p.get("long", {}).get("units", "0"))) != 0
        or Decimal(str(p.get("short", {}).get("units", "0"))) != 0
    ]
    pending_orders = [o["id"] for o in account.get("orders", []) if "id" in o]
    return AccountDetails(
        snapshot=snapshot,
        open_trade_ids=open_trades,
        open_position_instruments=open_positions,
        pending_order_ids=pending_orders,
    )


def map_candle(
    instrument: str,
    granularity: Granularity,
    payload: dict[str, Any],
) -> Candle:
    def comp(key: str, sub: str) -> Decimal | None:
        if key not in payload:
            return None
        return Decimal(str(payload[key][sub]))

    return Candle(
        instrument=instrument,
        granularity=granularity,
        time=parse_rfc3339(payload["time"]),
        complete=bool(payload.get("complete", False)),
        volume=int(payload.get("volume", 0)),
        bid_o=comp("bid", "o"),
        bid_h=comp("bid", "h"),
        bid_l=comp("bid", "l"),
        bid_c=comp("bid", "c"),
        ask_o=comp("ask", "o"),
        ask_h=comp("ask", "h"),
        ask_l=comp("ask", "l"),
        ask_c=comp("ask", "c"),
        mid_o=comp("mid", "o"),
        mid_h=comp("mid", "h"),
        mid_l=comp("mid", "l"),
        mid_c=comp("mid", "c"),
    )


def map_price(payload: dict[str, Any]) -> Quote:
    bids = payload.get("bids", [])
    asks = payload.get("asks", [])
    if not bids or not asks:
        raise ValueError(f"price payload missing bids/asks: {payload}")
    return Quote(
        instrument=payload["instrument"],
        time=parse_rfc3339(payload["time"]),
        bid=Decimal(str(bids[0]["price"])),
        ask=Decimal(str(asks[0]["price"])),
        tradeable=bool(payload.get("tradeable", True)),
        status=payload.get("status", "tradeable"),
    )


def map_spread_snapshot(quote: Quote, pip_size: Decimal) -> SpreadSnapshot:
    spread = quote.ask - quote.bid
    return SpreadSnapshot(
        instrument=quote.instrument,
        time=quote.time,
        bid=quote.bid,
        ask=quote.ask,
        spread_pips=(spread / pip_size).quantize(Decimal("0.01")),
    )


def map_broker_order(payload: dict[str, Any]) -> BrokerOrder:
    return BrokerOrder(
        broker_order_id=payload["id"],
        client_order_id=(payload.get("clientExtensions") or {}).get("id"),
        instrument=payload["instrument"],
        state=payload.get("state", "UNKNOWN"),
        type=payload.get("type", "UNKNOWN"),
        units=Decimal(str(payload.get("units", "0"))),
        price=_dec(payload.get("price")),
        time=parse_rfc3339(payload.get("createTime", "1970-01-01T00:00:00Z")),
        raw=payload,
    )


def map_trade(payload: dict[str, Any]) -> Trade:
    return Trade(
        trade_id=payload["id"],
        instrument=payload["instrument"],
        open_time=parse_rfc3339(payload["openTime"]),
        open_price=Decimal(str(payload["price"])),
        current_units=Decimal(str(payload["currentUnits"])),
        initial_units=Decimal(str(payload["initialUnits"])),
        state=payload.get("state", "OPEN"),
        stop_loss_order_id=(payload.get("stopLossOrder") or {}).get("id"),
        take_profit_order_id=(payload.get("takeProfitOrder") or {}).get("id"),
        trailing_stop_order_id=(payload.get("trailingStopLossOrder") or {}).get("id"),
        realized_pl=_dec(payload.get("realizedPL")),
        unrealized_pl=_dec(payload.get("unrealizedPL")),
        raw=payload,
    )


def map_position(payload: dict[str, Any]) -> Position:
    long_p = payload.get("long", {}) or {}
    short_p = payload.get("short", {}) or {}
    return Position(
        instrument=payload["instrument"],
        long_units=Decimal(str(long_p.get("units", "0"))),
        long_average_price=_dec(long_p.get("averagePrice")),
        short_units=Decimal(str(short_p.get("units", "0"))),
        short_average_price=_dec(short_p.get("averagePrice")),
        unrealized_pl=_dec(payload.get("unrealizedPL")),
        raw=payload,
    )


def map_transaction(payload: dict[str, Any]) -> Transaction:
    return Transaction(
        transaction_id=payload["id"],
        type=payload.get("type", "UNKNOWN"),
        account_id=payload.get("accountID", ""),
        time=parse_rfc3339(payload.get("time", "1970-01-01T00:00:00Z")),
        instrument=payload.get("instrument"),
        units=_dec(payload.get("units")),
        price=_dec(payload.get("price")),
        reason=payload.get("reason"),
        pl=_dec(payload.get("pl")),
        financing=_dec(payload.get("financing")),
        raw=payload,
    )


def is_heartbeat(payload: dict[str, Any]) -> bool:
    return payload.get("type") == "HEARTBEAT" or payload.get("type") == "PRICING_HEARTBEAT"


def map_heartbeat(payload: dict[str, Any]) -> Heartbeat:
    return Heartbeat(
        time=parse_rfc3339(payload["time"]),
        last_transaction_id=payload.get("lastTransactionID"),
    )

"""Order plans, broker orders, and broker order results."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

OrderSide = Literal["buy", "sell"]
OrderType = Literal["MARKET", "LIMIT", "STOP"]


class OrderPlan(BaseModel):
    """An approved plan to send to the broker. Only the executor reads this."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    plan_id: str
    signal_id: str
    strategy_name: str
    strategy_version: str
    instrument: str
    side: OrderSide
    order_type: OrderType = "MARKET"
    units: Decimal
    requested_price: Decimal | None = None
    stop_loss_price: Decimal
    take_profit_price: Decimal | None = None
    trailing_stop_pips: Decimal | None = None
    client_order_id: str
    config_hash: str
    created_at: datetime
    extras: dict[str, Any] = Field(default_factory=dict)


class BrokerOrder(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    broker_order_id: str
    client_order_id: str | None = None
    instrument: str
    state: str
    type: str
    units: Decimal
    price: Decimal | None = None
    time: datetime
    raw: dict[str, Any] = Field(default_factory=dict)


class BrokerOrderResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: Literal["FILLED", "PENDING", "CANCELLED", "REJECTED", "UNKNOWN"]
    broker_order_id: str | None = None
    client_order_id: str | None = None
    fill_transaction_id: str | None = None
    fill_price: Decimal | None = None
    filled_units: Decimal | None = None
    trade_opened_id: str | None = None
    last_transaction_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

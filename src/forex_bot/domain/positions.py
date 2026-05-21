"""Fills, trades, and positions returned by the broker."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Fill(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    fill_id: str
    trade_id: str | None = None
    instrument: str
    units: Decimal
    price: Decimal
    time: datetime
    pl: Decimal | None = None
    financing: Decimal | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class Trade(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    trade_id: str
    instrument: str
    open_time: datetime
    open_price: Decimal
    current_units: Decimal
    initial_units: Decimal
    state: str = "OPEN"
    stop_loss_order_id: str | None = None
    take_profit_order_id: str | None = None
    trailing_stop_order_id: str | None = None
    realized_pl: Decimal | None = None
    unrealized_pl: Decimal | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class Position(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    instrument: str
    long_units: Decimal = Decimal("0")
    long_average_price: Decimal | None = None
    short_units: Decimal = Decimal("0")
    short_average_price: Decimal | None = None
    unrealized_pl: Decimal | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

    @property
    def net_units(self) -> Decimal:
        return self.long_units + self.short_units  # short_units is negative

    @property
    def is_flat(self) -> bool:
        return self.long_units == 0 and self.short_units == 0

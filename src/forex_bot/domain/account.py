"""Account snapshot and account details."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AccountSnapshot(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    account_id: str
    currency: str
    balance: Decimal
    nav: Decimal
    margin_used: Decimal = Decimal("0")
    margin_available: Decimal = Decimal("0")
    margin_closeout_percent: Decimal = Decimal("0")
    unrealized_pl: Decimal = Decimal("0")
    pl: Decimal = Decimal("0")
    open_trade_count: int = 0
    open_position_count: int = 0
    pending_order_count: int = 0
    last_transaction_id: str | None = None
    time: datetime
    raw: dict[str, Any] = Field(default_factory=dict)


class AccountDetails(BaseModel):
    """Full account state used for reconciliation."""

    model_config = ConfigDict(extra="ignore")

    snapshot: AccountSnapshot
    open_trade_ids: list[str] = Field(default_factory=list)
    open_position_instruments: list[str] = Field(default_factory=list)
    pending_order_ids: list[str] = Field(default_factory=list)

"""Broker-side transactions and stream heartbeats."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Transaction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    transaction_id: str
    type: str
    account_id: str
    time: datetime
    instrument: str | None = None
    units: Decimal | None = None
    price: Decimal | None = None
    reason: str | None = None
    pl: Decimal | None = None
    financing: Decimal | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class Heartbeat(BaseModel):
    model_config = ConfigDict(extra="ignore")

    time: datetime
    last_transaction_id: str | None = None

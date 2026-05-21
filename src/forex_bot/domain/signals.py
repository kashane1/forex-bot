"""Strategy-emitted signals."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

SignalSide = Literal["long", "short", "flat"]
EntryIntent = Literal["market", "stop", "limit"]


class Signal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    signal_id: str
    strategy_name: str
    strategy_version: str
    instrument: str
    timeframe: str
    timestamp: datetime
    side: SignalSide
    entry_intent: EntryIntent = "market"
    confidence: float | None = None
    stop_model: str
    stop_price: Decimal
    take_profit_price: Decimal | None = None
    exit_model: str
    features: dict[str, Any] = Field(default_factory=dict)
    reason: str = ""

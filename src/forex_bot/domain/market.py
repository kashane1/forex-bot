"""Quotes, spreads, and aggregate market state used by risk/strategy."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class Quote(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    instrument: str
    time: datetime
    bid: Decimal
    ask: Decimal
    tradeable: bool = True
    status: str = "tradeable"

    @property
    def mid(self) -> Decimal:
        return (self.bid + self.ask) / 2

    @property
    def spread(self) -> Decimal:
        return self.ask - self.bid


class SpreadSnapshot(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    instrument: str
    time: datetime
    bid: Decimal
    ask: Decimal
    spread_pips: Decimal


class MarketState(BaseModel):
    """Aggregate of current data the risk engine and strategies consume."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    quote: Quote
    spread_snapshot: SpreadSnapshot
    instrument_metadata_version: str = ""

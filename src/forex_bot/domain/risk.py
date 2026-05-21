"""Risk decisions emitted by the risk engine."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RiskRejectionCode(StrEnum):
    OK = "OK"
    KILL_SWITCH = "KILL_SWITCH"
    TRADING_DISABLED = "TRADING_DISABLED"
    UNRECONCILED = "UNRECONCILED"
    DAILY_LOSS_LIMIT = "DAILY_LOSS_LIMIT"
    WEEKLY_LOSS_LIMIT = "WEEKLY_LOSS_LIMIT"
    DRAWDOWN_LIMIT = "DRAWDOWN_LIMIT"
    MAX_OPEN_POSITIONS = "MAX_OPEN_POSITIONS"
    MAX_PENDING_ORDERS = "MAX_PENDING_ORDERS"
    MAX_PER_INSTRUMENT = "MAX_PER_INSTRUMENT"
    CORRELATED_EXPOSURE = "CORRELATED_EXPOSURE"
    MISSING_STOP_LOSS = "MISSING_STOP_LOSS"
    SPREAD_TOO_WIDE = "SPREAD_TOO_WIDE"
    SPREAD_TO_ATR = "SPREAD_TO_ATR"
    NOT_TRADEABLE = "NOT_TRADEABLE"
    STALE_PRICE = "STALE_PRICE"
    MISSING_INSTRUMENT_METADATA = "MISSING_INSTRUMENT_METADATA"
    SESSION_BLOCKED = "SESSION_BLOCKED"
    MARGIN_BUFFER = "MARGIN_BUFFER"
    MIN_TRADE_SIZE = "MIN_TRADE_SIZE"
    UNITS_ROUNDED_TO_ZERO = "UNITS_ROUNDED_TO_ZERO"
    PIP_VALUE_UNAVAILABLE = "PIP_VALUE_UNAVAILABLE"
    INVALID_SIGNAL = "INVALID_SIGNAL"
    UNKNOWN_INSTRUMENT = "UNKNOWN_INSTRUMENT"


class RiskDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    signal_id: str
    decided_at: datetime
    approved: bool
    rejection_codes: list[RiskRejectionCode] = Field(default_factory=list)
    rejection_messages: list[str] = Field(default_factory=list)
    account_nav: Decimal | None = None
    instrument_metadata_version: str | None = None
    spread_pips: Decimal | None = None
    stop_distance_pips: Decimal | None = None
    raw_units: Decimal | None = None
    units: Decimal | None = None
    estimated_risk: Decimal | None = None
    estimated_margin: Decimal | None = None
    config_hash: str
    extras: dict[str, Any] = Field(default_factory=dict)

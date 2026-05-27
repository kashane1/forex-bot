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
    # Optional provenance (additive — old signals omit these).
    campaign_id: str | None = None
    strategy_run_id: str | None = None
    decision_time: datetime | None = None
    available_data_cutoff: datetime | None = None
    source_candle_timestamp: datetime | None = None
    htf_feature_times: dict[str, datetime] | None = None


def validate_signal_provenance(signal: Signal) -> list[str]:
    """Validate optional provenance fields on a signal."""
    from forex_bot.features.htf_align import validate_signal_provenance as _validate

    decision = signal.decision_time or signal.timestamp
    return _validate(
        decision_time=decision,
        available_data_cutoff=signal.available_data_cutoff,
        htf_feature_times=signal.htf_feature_times,
    )

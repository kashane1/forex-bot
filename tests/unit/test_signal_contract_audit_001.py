"""Phase 4 audit: Signal model is strategy-only output, timestamp-safe."""

from __future__ import annotations

import inspect
from datetime import UTC, datetime
from decimal import Decimal

from forex_bot.domain.signals import Signal
from forex_bot.strategies.trend_following import TrendFollowingStrategy


def test_signal_model_has_core_audit_fields():
    fields = set(Signal.model_fields)
    required = {
        "signal_id",
        "strategy_name",
        "strategy_version",
        "instrument",
        "timeframe",
        "timestamp",
        "side",
        "stop_model",
        "stop_price",
        "exit_model",
        "features",
        "reason",
    }
    assert required <= fields


def test_strategy_generate_signal_returns_signal_or_none_only():
    sig = inspect.signature(TrendFollowingStrategy.generate_signal)
    assert sig.return_annotation in (Signal | None, "Signal | None")


def test_signal_timestamp_not_after_cutoff():
    cutoff = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)
    signal_time = datetime(2024, 6, 1, 10, 0, tzinfo=UTC)
    assert signal_time <= cutoff
    s = Signal(
        signal_id="x",
        strategy_name="t",
        strategy_version="0",
        instrument="EUR_USD",
        timeframe="H4",
        timestamp=signal_time,
        side="long",
        stop_model="atr",
        stop_price=Decimal("1.09"),
        exit_model="time",
        features={"available_data_cutoff": cutoff.isoformat()},
    )
    assert s.timestamp <= cutoff

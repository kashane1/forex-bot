"""Additive signal provenance fields — backward compatible."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from forex_bot.domain.signals import Signal, validate_signal_provenance


def test_legacy_signal_construction_unchanged():
    s = Signal(
        signal_id="legacy",
        strategy_name="mean_reversion",
        strategy_version="0.1.0-c008",
        instrument="EUR_USD",
        timeframe="H4",
        timestamp=datetime(2024, 1, 2, 6, tzinfo=UTC),
        side="long",
        stop_model="atr",
        stop_price=Decimal("1.09"),
        exit_model="time",
    )
    assert s.campaign_id is None
    assert s.available_data_cutoff is None


def test_provenance_fields_optional():
    cutoff = datetime(2024, 1, 2, 6, tzinfo=UTC)
    decision = datetime(2024, 1, 2, 6, tzinfo=UTC)
    s = Signal(
        signal_id="p1",
        strategy_name="t",
        strategy_version="0",
        instrument="EUR_USD",
        timeframe="H4",
        timestamp=decision,
        side="long",
        stop_model="atr",
        stop_price=Decimal("1.09"),
        exit_model="time",
        campaign_id="CAMPAIGN_019",
        decision_time=decision,
        available_data_cutoff=cutoff,
        source_candle_timestamp=cutoff,
        htf_feature_times={"d1_atr": datetime(2024, 1, 1, 18, tzinfo=UTC)},
    )
    assert validate_signal_provenance(s) == []


def test_cutoff_before_decision_rejected():
    s = Signal(
        signal_id="p2",
        strategy_name="t",
        strategy_version="0",
        instrument="EUR_USD",
        timeframe="H4",
        timestamp=datetime(2024, 1, 2, 10, tzinfo=UTC),
        side="long",
        stop_model="atr",
        stop_price=Decimal("1.09"),
        exit_model="time",
        decision_time=datetime(2024, 1, 2, 10, tzinfo=UTC),
        available_data_cutoff=datetime(2024, 1, 2, 6, tzinfo=UTC),
    )
    assert "decision_time after available_data_cutoff" in validate_signal_provenance(s)[0]

"""Idempotency: same signal+config_hash+timestamp must produce same client_id."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from forex_bot.domain.signals import Signal
from forex_bot.risk.policy import _client_order_id


def _signal(ts: datetime, signal_id: str = "sig-1") -> Signal:
    return Signal(
        signal_id=signal_id,
        strategy_name="trend_following",
        strategy_version="0.1.0",
        instrument="EUR_USD",
        timeframe="H4",
        timestamp=ts,
        side="long",
        stop_model="ATR",
        stop_price=Decimal("1.07"),
        exit_model="trail",
    )


def test_same_signal_same_client_id_within_hour_bucket():
    ts = datetime(2026, 5, 21, 12, 0, tzinfo=UTC)
    a = _client_order_id(_signal(ts), "abcdef1234567890")
    b = _client_order_id(_signal(ts), "abcdef1234567890")
    assert a == b
    assert a.startswith("fbot-")


def test_different_config_hash_yields_different_id():
    ts = datetime(2026, 5, 21, 12, 0, tzinfo=UTC)
    a = _client_order_id(_signal(ts), "abcdef1234567890")
    b = _client_order_id(_signal(ts), "fedcba1234567890")
    assert a != b


def test_different_signal_yields_different_id():
    ts = datetime(2026, 5, 21, 12, 0, tzinfo=UTC)
    a = _client_order_id(_signal(ts, "sig-1"), "h")
    b = _client_order_id(_signal(ts, "sig-2"), "h")
    assert a != b


def test_different_hour_bucket_yields_different_id():
    a = _client_order_id(_signal(datetime(2026, 5, 21, 12, tzinfo=UTC)), "h")
    b = _client_order_id(_signal(datetime(2026, 5, 21, 13, tzinfo=UTC)), "h")
    assert a != b

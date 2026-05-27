"""Tests for shared HTF alignment module."""

from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from forex_bot.domain.signals import Signal, validate_signal_provenance
from forex_bot.features.htf_align import (
    HTF_STALE,
    HTF_UNAVAILABLE,
    align_last_completed,
)
from decimal import Decimal


def _htf_frame(rows: list[tuple]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["time", "complete", "atr"])


def test_no_future_htf_row_used():
    htf = _htf_frame(
        [
            (datetime(2024, 1, 8, 18, tzinfo=UTC), True, 1.0),
            (datetime(2024, 1, 9, 18, tzinfo=UTC), True, 2.0),
        ]
    )
    decisions = pd.DatetimeIndex([datetime(2024, 1, 9, 10, tzinfo=UTC)])
    out = align_last_completed(decisions, htf, ["atr"])
    assert out["htf_atr"].iloc[0] == 1.0
    assert out["htf_atr_time"].iloc[0] == pd.Timestamp("2024-01-08 18:00:00+00:00")


def test_incomplete_htf_excluded():
    htf = _htf_frame(
        [
            (datetime(2024, 1, 8, 18, tzinfo=UTC), True, 1.0),
            (datetime(2024, 1, 9, 18, tzinfo=UTC), False, 99.0),
        ]
    )
    decisions = pd.DatetimeIndex([datetime(2024, 1, 9, 20, tzinfo=UTC)])
    out = align_last_completed(decisions, htf, ["atr"])
    assert out["htf_atr"].iloc[0] == 1.0


def test_missing_htf_returns_unavailable():
    htf = _htf_frame([(datetime(2024, 1, 10, 18, tzinfo=UTC), True, 1.0)])
    decisions = pd.DatetimeIndex([datetime(2024, 1, 9, 10, tzinfo=UTC)])
    out = align_last_completed(decisions, htf, ["atr"])
    assert out["htf_blocked_reason"].iloc[0] == HTF_UNAVAILABLE


def test_stale_htf_when_max_staleness_configured():
    htf = _htf_frame([(datetime(2024, 1, 1, 18, tzinfo=UTC), True, 1.0)])
    decisions = pd.DatetimeIndex([datetime(2024, 1, 10, 10, tzinfo=UTC)])
    out = align_last_completed(
        decisions, htf, ["atr"], max_staleness=pd.Timedelta(days=5)
    )
    assert out["htf_blocked_reason"].iloc[0] == HTF_STALE
    assert bool(out["htf_is_stale"].iloc[0])


def test_signal_provenance_rejects_future_htf():
    sig = Signal(
        signal_id="x",
        strategy_name="t",
        strategy_version="0",
        instrument="EUR_USD",
        timeframe="H4",
        timestamp=datetime(2024, 1, 9, 10, tzinfo=UTC),
        side="long",
        stop_model="atr",
        stop_price=Decimal("1.09"),
        exit_model="time",
        decision_time=datetime(2024, 1, 9, 10, tzinfo=UTC),
        htf_feature_times={"d1_atr": datetime(2024, 1, 10, 18, tzinfo=UTC)},
    )
    assert validate_signal_provenance(sig)

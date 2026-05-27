"""Tests for engine-aligned risk windows."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pandas as pd
from research.backtrader_exit_parity.risk_windows import drawdown_pct, realized_windows


def test_realized_windows_monday_week():
    ts = pd.Timestamp("2021-03-10T13:00:00+00:00")  # Wednesday
    realized = [
        (datetime(2021, 3, 8, 9, 0, tzinfo=UTC), Decimal("10")),  # Monday — in week
        (datetime(2021, 3, 3, 9, 0, tzinfo=UTC), Decimal("-5")),  # prior week — out
    ]
    today, week = realized_windows(ts, realized)
    assert today == Decimal("0")
    assert week == Decimal("10")


def test_drawdown_pct_basic():
    points = [(datetime(2021, 1, 1, tzinfo=UTC), 500.0)]
    dd = drawdown_pct(points, 450.0)
    assert dd == Decimal("10.0")

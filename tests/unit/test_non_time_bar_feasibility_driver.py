"""Unit tests for the pure helpers in scripts/analyze_non_time_bar_feasibility.py.

The script is loaded by path (it lives in scripts/, not an installed package). Only
its pure, DB-free helpers are exercised here: session bucketing, spread-from-candle,
window span, and bar-geometry summarisation over synthetic bars.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "analyze_non_time_bar_feasibility.py"
_spec = importlib.util.spec_from_file_location("anbf_driver", _SCRIPT)
driver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(driver)


# --------------------------------------------------------------------------- #
# session_bucket
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "hour,expected",
    [
        (0, "tokyo"),
        (6, "tokyo"),
        (7, "london"),
        (11, "london"),
        (12, "london_ny_overlap"),
        (15, "london_ny_overlap"),
        (16, "new_york"),
        (20, "new_york"),
        (21, "rollover_late"),
        (23, "rollover_late"),
    ],
)
def test_session_bucket(hour, expected):
    assert driver.session_bucket(hour) == expected


# --------------------------------------------------------------------------- #
# spread_pips_from_candle (JPY pip handling)
# --------------------------------------------------------------------------- #


@dataclass
class _FakeCandle:
    time: datetime
    bid_c: Decimal | None
    ask_c: Decimal | None
    # geometry fields used by bar_geometry are added per-test as needed


def test_spread_pips_jpy():
    c = _FakeCandle(
        time=datetime(2022, 1, 1, tzinfo=UTC), bid_c=Decimal("130.000"), ask_c=Decimal("130.019")
    )
    assert driver.spread_pips_from_candle(c, "USD_JPY") == pytest.approx(1.9)


def test_spread_pips_default():
    c = _FakeCandle(
        time=datetime(2022, 1, 1, tzinfo=UTC), bid_c=Decimal("1.10000"), ask_c=Decimal("1.10008")
    )
    assert driver.spread_pips_from_candle(c, "EUR_USD") == pytest.approx(0.8)


def test_spread_pips_none_when_missing():
    c = _FakeCandle(time=datetime(2022, 1, 1, tzinfo=UTC), bid_c=None, ask_c=Decimal("1.1"))
    assert driver.spread_pips_from_candle(c, "EUR_USD") is None


def test_spread_pips_none_when_negative():
    c = _FakeCandle(
        time=datetime(2022, 1, 1, tzinfo=UTC), bid_c=Decimal("1.10010"), ask_c=Decimal("1.10000")
    )
    assert driver.spread_pips_from_candle(c, "EUR_USD") is None


# --------------------------------------------------------------------------- #
# window_days_from_span
# --------------------------------------------------------------------------- #


def test_window_days_from_span():
    a = datetime(2021, 1, 1, tzinfo=UTC)
    b = datetime(2021, 1, 11, tzinfo=UTC)
    assert driver.window_days_from_span(a, b) == pytest.approx(10.0)
    # zero span floors to a tiny positive number (never divides by zero downstream)
    assert driver.window_days_from_span(a, a) > 0


# --------------------------------------------------------------------------- #
# bar_geometry
# --------------------------------------------------------------------------- #


@dataclass
class _FakeBar:
    open_time: datetime
    close_time: datetime
    source_count: int
    overshoot_pips: float
    thresholds_crossed: int
    incomplete: bool = False


def _bar(minute_open, minute_close, *, hour=8, source=5, overshoot=0.5, crossed=1, incomplete=False):
    base = datetime(2022, 3, 1, hour, 0, tzinfo=UTC)
    return _FakeBar(
        open_time=base + timedelta(minutes=minute_open),
        close_time=base + timedelta(minutes=minute_close),
        source_count=source,
        overshoot_pips=overshoot,
        thresholds_crossed=crossed,
        incomplete=incomplete,
    )


def test_bar_geometry_empty():
    geo = driver.bar_geometry([])
    assert geo["bar_count"] == 0
    assert geo["multi_threshold_rate"] == 0.0
    assert geo["median_minutes_per_bar"] is None


def test_bar_geometry_basic():
    bars = [
        _bar(0, 10, source=10, overshoot=0.4, crossed=1),
        _bar(10, 30, source=20, overshoot=0.6, crossed=1),
        _bar(30, 90, source=60, overshoot=2.0, crossed=2),  # multi-threshold
    ]
    geo = driver.bar_geometry(bars)
    assert geo["bar_count"] == 3
    assert geo["median_minutes_per_bar"] == pytest.approx(20.0)
    assert geo["avg_m1_rows_per_bar"] == pytest.approx(30.0)
    assert geo["avg_overshoot_pips"] == pytest.approx(1.0)
    assert geo["multi_threshold_rate"] == pytest.approx(1 / 3, abs=1e-4)
    assert geo["session_distribution"] == {"london": 3}  # hour 8 = london


def test_bar_geometry_excludes_incomplete():
    bars = [_bar(0, 10), _bar(10, 20, incomplete=True)]
    geo = driver.bar_geometry(bars)
    assert geo["bar_count"] == 1
    assert geo["incomplete_final_bars"] == 1

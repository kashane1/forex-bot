from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]


def _load_script():
    path = _REPO / "scripts" / "validate_m1_canonical_store.py"
    spec = importlib.util.spec_from_file_location("validate_m1_canonical_store", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_script()


def _rows(start: datetime, count: int) -> list[dict]:
    rows = []
    for i in range(count):
        base = 1.1 + i / 10000
        rows.append(
            {
                "time_utc": start + timedelta(minutes=i),
                "complete": True,
                "volume": 1,
                "bid_o": base,
                "bid_h": base + 0.0002,
                "bid_l": base - 0.0001,
                "bid_c": base + 0.0001,
                "ask_o": base + 0.0002,
                "ask_h": base + 0.0004,
                "ask_l": base + 0.0001,
                "ask_c": base + 0.0003,
                "mid_o": base + 0.0001,
                "mid_h": base + 0.0003,
                "mid_l": base,
                "mid_c": base + 0.0002,
            }
        )
    return rows


def test_missing_minute_detected() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    rows = _rows(start, 5)
    del rows[2]
    report = validator.analyze_rows(rows, instrument="EUR_USD", start_utc=start, end_utc=start + timedelta(minutes=5))
    assert report["missing_minutes"] == 1


def test_duplicate_detected() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    rows = _rows(start, 2)
    rows.append(rows[1].copy())
    report = validator.analyze_rows(rows, instrument="EUR_USD", start_utc=start, end_utc=start + timedelta(minutes=2))
    assert report["duplicate_timestamps"] == 1


def test_incomplete_detected() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    rows = _rows(start, 5)
    rows[0]["complete"] = False
    report = validator.analyze_rows(rows, instrument="EUR_USD", start_utc=start, end_utc=start + timedelta(minutes=5))
    assert report["incomplete_candles"] == 1
    assert report["incomplete_aggregate_counts"]["M5"] == 1


def test_negative_spread_detected() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    rows = _rows(start, 1)
    rows[0]["ask_c"] = rows[0]["bid_c"] - 0.0001
    report = validator.analyze_rows(rows, instrument="EUR_USD", start_utc=start, end_utc=start + timedelta(minutes=1))
    assert report["negative_or_zero_spreads"] == 1


def test_aggregate_count_expected() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    report = validator.analyze_rows(_rows(start, 15), instrument="EUR_USD", start_utc=start, end_utc=start + timedelta(minutes=15))
    assert report["aggregate_counts"]["M5"] == 3
    assert report["aggregate_counts"]["M15"] == 1


def test_weekend_gap_not_missing() -> None:
    saturday = datetime(2024, 1, 6, tzinfo=UTC)
    report = validator.analyze_rows([], instrument="EUR_USD", start_utc=saturday, end_utc=saturday + timedelta(days=1))
    assert report["expected_m1_count"] == 0
    assert report["missing_minutes"] == 0

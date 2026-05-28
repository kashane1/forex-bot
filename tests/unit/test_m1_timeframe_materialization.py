from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from forex_bot.data.m1_timeframe_materialization import (
    MATERIALIZED_SOURCE,
    aggregation_config_hash,
    candle_to_record,
    verify_materialized_pair,
)
from forex_bot.data.postgres_candle_store import CandleRecord, PostgresCandleStore
from forex_bot.data.research_db import ResearchDatabaseConfig
from forex_bot.domain.candles import Candle
from forex_bot.research.campaign_021_loader import check_materialized_coverage


class _FakeCursor:
    def __init__(self, *, max_time=None, count=0, rows=None) -> None:
        self.max_time = max_time
        self.count = count
        self.rows = rows or []
        self.last_sql = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.last_sql = sql
        self._params = params

    def fetchone(self):
        if "MAX(time_utc)" in self.last_sql:
            return (self.max_time,)
        if "COUNT(*)" in self.last_sql:
            return (self.count,)
        return None

    def fetchall(self):
        return self.rows

    @property
    def description(self):
        return [
            ("instrument",),
            ("granularity",),
            ("time_utc",),
            ("complete",),
            ("volume",),
            ("bid_o",),
            ("bid_h",),
            ("bid_l",),
            ("bid_c",),
            ("ask_o",),
            ("ask_h",),
            ("ask_l",),
            ("ask_c",),
            ("mid_o",),
            ("mid_h",),
            ("mid_l",),
            ("mid_c",),
            ("spread_open",),
            ("spread_high",),
            ("spread_low",),
            ("spread_close",),
            ("source",),
            ("fetch_batch_id",),
            ("data_hash",),
            ("created_at_utc",),
            ("fetched_at_utc",),
        ]


class _FakeConn:
    def __init__(self, cursor: _FakeCursor) -> None:
        self.cursor_obj = cursor
        self.commits = 0

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.commits += 1

    def close(self):
        return None


def _store(cursor: _FakeCursor) -> PostgresCandleStore:
    return PostgresCandleStore(
        ResearchDatabaseConfig(url="postgresql://test/test", schema="market_data"),
        connector=lambda _url: _FakeConn(cursor),
    )


def _candle(ts: datetime) -> Candle:
    return Candle(
        instrument="EUR_USD",
        granularity="M15",
        time=ts,
        complete=True,
        volume=10,
        bid_o=Decimal("1.1000"),
        bid_h=Decimal("1.1005"),
        bid_l=Decimal("1.0995"),
        bid_c=Decimal("1.1002"),
        ask_o=Decimal("1.1002"),
        ask_h=Decimal("1.1007"),
        ask_l=Decimal("1.0997"),
        ask_c=Decimal("1.1004"),
        mid_o=Decimal("1.1001"),
        mid_h=Decimal("1.1006"),
        mid_l=Decimal("1.0996"),
        mid_c=Decimal("1.1003"),
    )


def test_aggregation_config_hash_is_stable():
    assert aggregation_config_hash() == aggregation_config_hash()


def test_candle_to_record_sets_fetch_batch_id():
    ts = datetime(2024, 1, 1, tzinfo=UTC)
    record = candle_to_record(_candle(ts), fetch_batch_id="run-1")
    assert record.fetch_batch_id == "run-1"
    assert record.granularity == "M15"


def test_max_candle_time_returns_utc():
    ts = datetime(2024, 6, 1, tzinfo=UTC)
    store = _store(_FakeCursor(max_time=ts))
    assert store.max_candle_time(
        instrument="EUR_USD", granularity="M15", source=MATERIALIZED_SOURCE
    ) == ts


def test_verify_materialized_pair_passes_when_rows_match(monkeypatch):
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = start + timedelta(minutes=15)
    candle = _candle(start)
    row = {
        "time_utc": start,
        "complete": True,
        "volume": 10,
        "bid_o": 1.1,
        "bid_h": 1.1005,
        "bid_l": 1.0995,
        "bid_c": 1.1002,
        "ask_o": 1.1002,
        "ask_h": 1.1007,
        "ask_l": 1.0997,
        "ask_c": 1.1004,
        "mid_o": 1.1001,
        "mid_h": 1.1006,
        "mid_l": 1.0996,
        "mid_c": 1.1003,
        "source": MATERIALIZED_SOURCE,
    }

    store = _store(_FakeCursor(rows=[(
        "EUR_USD", "M15", start, True, 10,
        row["bid_o"], row["bid_h"], row["bid_l"], row["bid_c"],
        row["ask_o"], row["ask_h"], row["ask_l"], row["ask_c"],
        row["mid_o"], row["mid_h"], row["mid_l"], row["mid_c"],
        None, None, None, None,
        MATERIALIZED_SOURCE, "run", "hash", start, start,
    )]))

    monkeypatch.setattr(
        "forex_bot.data.m1_timeframe_materialization.aggregate_m1_window",
        lambda *_args, **_kwargs: {"M15": [candle]},
    )
    report = verify_materialized_pair(
        store,
        "EUR_USD",
        from_utc=start,
        to_utc=end,
        targets=("M15",),
    )
    assert report["status"] == "PASS"


def test_check_materialized_coverage_fail_when_sparse():
    store = _store(_FakeCursor(count=10))
    report = check_materialized_coverage(
        store,
        "EUR_USD",
        from_dt=datetime(2024, 1, 1, tzinfo=UTC),
        to_dt=datetime(2024, 12, 31, tzinfo=UTC),
        min_m15=120,
    )
    assert report["status"] == "FAIL"


def test_upsert_materialized_preserves_native_h4():
    cursor = _FakeCursor()
    store = _store(cursor)
    record = CandleRecord(
        instrument="EUR_USD",
        granularity="H4",
        time_utc=datetime(2024, 1, 1, tzinfo=UTC),
        complete=True,
        volume=10,
        bid_o=1.1,
        bid_h=1.2,
        bid_l=1.0,
        bid_c=1.15,
        ask_o=1.1002,
        ask_h=1.2002,
        ask_l=1.0002,
        ask_c=1.1502,
        mid_o=1.1001,
        mid_h=1.2001,
        mid_l=1.0001,
        mid_c=1.1501,
        fetch_batch_id="mat-1",
    )
    count = store.upsert_materialized_candles(
        [record],
        source=MATERIALIZED_SOURCE,
        preserve_sources=frozenset({"oanda-practice"}),
    )
    assert count == 1
    assert "WHERE" in cursor.last_sql
    assert cursor._params is not None
    assert "oanda-practice" in cursor._params

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from forex_bot.data.postgres_candle_store import (
    CandleRecord,
    PostgresCandleStore,
    common_timestamp_intersection,
    compute_candle_data_hash,
    compute_spread_fields,
    schema_sql,
    validate_candle_record,
)
from forex_bot.data.research_db import ResearchDatabaseConfig


class _FakeCursor:
    def __init__(self) -> None:
        self.executed: list[tuple[str, object | None]] = []
        self.description = [("instrument",), ("granularity",), ("time_utc",), ("complete",), ("volume",)]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def executemany(self, sql, params_list):
        for params in params_list:
            self.execute(sql, params)

    def fetchall(self):
        return []


class _FakeConn:
    def __init__(self) -> None:
        self.cursor_obj = _FakeCursor()
        self.commits = 0

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.commits += 1

    def close(self):
        return None


def _candle() -> CandleRecord:
    return CandleRecord(
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
    )


def test_schema_sql_is_deterministic():
    a = schema_sql()
    b = schema_sql()
    assert a == b
    assert "market_data.candles" in a
    assert "fetch_batch_id TEXT" in a
    assert "data_hash TEXT" in a
    assert "created_at_utc TIMESTAMPTZ" in a


def test_compute_spread_fields():
    spreads = compute_spread_fields(_candle())
    assert spreads["spread_open"] == pytest.approx(0.0002)
    assert spreads["spread_close"] == pytest.approx(0.0002)


def test_compute_candle_data_hash_is_stable():
    assert compute_candle_data_hash(_candle()) == compute_candle_data_hash(_candle())
    changed = CandleRecord(**{**_candle().__dict__, "volume": 11})
    assert compute_candle_data_hash(changed) != compute_candle_data_hash(_candle())


def test_rejects_invalid_ohlc_before_db_write():
    bad = CandleRecord(**{**_candle().__dict__, "bid_h": 1.05})
    with pytest.raises(ValueError, match="bid OHLC"):
        validate_candle_record(bad)


def test_common_timestamp_intersection():
    start = datetime(2024, 1, 1, tzinfo=UTC)
    rows = {
        "EUR_USD": [{"time_utc": start}, {"time_utc": start + timedelta(hours=4)}],
        "GBP_USD": [{"time_utc": start + timedelta(hours=4)}],
    }
    out = common_timestamp_intersection(rows)
    assert out["count"] == 1
    assert out["start_utc"] == start + timedelta(hours=4)


def test_idempotent_upsert_uses_conflict_update():
    conn = _FakeConn()
    store = PostgresCandleStore(
        ResearchDatabaseConfig(url="postgresql://localhost:5432/forex_bot"),
        connector=lambda _url: conn,
    )
    written = store.upsert_candles([_candle()], source="oanda-practice")
    assert written == 1
    sql = conn.cursor_obj.executed[0][0]
    assert "ON CONFLICT (instrument, granularity, time_utc) DO UPDATE" in sql
    assert "fetch_batch_id" in sql
    assert "data_hash" in sql
    assert conn.commits == 1

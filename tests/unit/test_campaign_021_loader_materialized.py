"""CAMPAIGN_021 materialized loader tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from forex_bot.data.m1_timeframe_materialization import MATERIALIZED_SOURCE, STORAGE_GRANULARITY
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import ResearchDatabaseConfig
from forex_bot.research.campaign_021_loader import (
    ALLOW_LIVE_AGGREGATION_ENV,
    D1AGG_SOURCE,
    load_c021_frames,
)


class _CountCursor:
    def __init__(self, counts: dict[str, int]) -> None:
        self.counts = counts
        self.last_sql = ""
        self._params = None
        self.queries: list[tuple[str, object | None]] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.last_sql = sql
        self._params = params
        self.queries.append((sql, params))

    def fetchall(self):
        return []

    def fetchone(self):
        if "COUNT(*)" in self.last_sql and self._params:
            gran = self._params[1]
            if gran == "H4" and "source NOT IN" in self.last_sql:
                return (2,)
            return (self.counts.get(gran, 0),)
        return None

    @property
    def description(self):
        return [("c",)]


class _Conn:
    def __init__(self, cursor: _CountCursor) -> None:
        self.cursor_obj = cursor

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        return None

    def close(self):
        return None


def _store(counts: dict[str, int]) -> PostgresCandleStore:
    return PostgresCandleStore(
        ResearchDatabaseConfig(url="postgresql://test/test", schema="market_data"),
        connector=lambda _url: _Conn(_CountCursor(counts)),
    )


def test_load_c021_frames_fails_when_materialized_m15_missing():
    counts = {
        "M15": 10,
        "H1": 100,
        STORAGE_GRANULARITY["H4"]: 50,
    }
    store = _store(counts)
    with pytest.raises(SystemExit, match="materialized coverage FAIL"):
        load_c021_frames(
            store,
            "EUR_USD",
            from_dt=datetime(2020, 1, 1, tzinfo=UTC),
            to_dt=datetime(2022, 12, 31, tzinfo=UTC),
            allow_live_aggregation=False,
        )


def test_load_c021_frames_uses_native_h4_for_d1agg(monkeypatch):
    counts = {
        "M15": 200,
        "H1": 100,
        STORAGE_GRANULARITY["H4"]: 50,
    }
    cursor = _CountCursor(counts)
    store = _store(counts)
    monkeypatch.setattr(
        "forex_bot.research.campaign_021_loader._load_materialized_granularity",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        "forex_bot.research.campaign_021_loader._load_native_h4",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        "forex_bot.research.campaign_021_loader.aggregate_h4_to_d1",
        lambda h4, instrument: type("R", (), {"candles": h4})(),
    )
    frames = load_c021_frames(
        store,
        "EUR_USD",
        from_dt=datetime(2020, 1, 1, tzinfo=UTC),
        to_dt=datetime(2022, 12, 31, tzinfo=UTC),
        allow_live_aggregation=False,
    )
    assert frames.d1agg_source == D1AGG_SOURCE
    assert frames.m1_row_count == 0


def test_live_aggregation_requires_env(monkeypatch):
    counts = {"M15": 10, "H1": 0, STORAGE_GRANULARITY["H4"]: 0}
    store = _store(counts)
    monkeypatch.delenv(ALLOW_LIVE_AGGREGATION_ENV, raising=False)
    with pytest.raises(SystemExit, match="materialized coverage FAIL"):
        load_c021_frames(
            store,
            "EUR_USD",
            from_dt=datetime(2020, 1, 1, tzinfo=UTC),
            to_dt=datetime(2022, 12, 31, tzinfo=UTC),
        )

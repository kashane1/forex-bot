"""PostgreSQL candle-store helpers for local research data."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from forex_bot.data.research_db import DEFAULT_RESEARCH_SCHEMA, ResearchDatabaseConfig

_H4_STEP = timedelta(hours=4)


@dataclass(frozen=True)
class InstrumentRecord:
    instrument: str
    pip_location: int
    display_precision: int
    trade_units_precision: int
    minimum_trade_size: str
    margin_rate: str
    source: str
    updated_at_utc: datetime


@dataclass(frozen=True)
class CandleRecord:
    instrument: str
    granularity: str
    time_utc: datetime
    complete: bool
    volume: int
    bid_o: float | None = None
    bid_h: float | None = None
    bid_l: float | None = None
    bid_c: float | None = None
    ask_o: float | None = None
    ask_h: float | None = None
    ask_l: float | None = None
    ask_c: float | None = None
    mid_o: float | None = None
    mid_h: float | None = None
    mid_l: float | None = None
    mid_c: float | None = None
    fetch_batch_id: str | None = None
    data_hash: str | None = None


def schema_sql(schema: str = DEFAULT_RESEARCH_SCHEMA) -> str:
    return f"""
CREATE SCHEMA IF NOT EXISTS {schema};

CREATE TABLE IF NOT EXISTS {schema}.instruments (
  instrument TEXT PRIMARY KEY,
  pip_location INTEGER,
  display_precision INTEGER,
  trade_units_precision INTEGER,
  minimum_trade_size TEXT,
  margin_rate TEXT,
  source TEXT NOT NULL,
  updated_at_utc TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS {schema}.candles (
  instrument TEXT NOT NULL,
  granularity TEXT NOT NULL,
  time_utc TIMESTAMPTZ NOT NULL,
  complete BOOLEAN NOT NULL,
  volume BIGINT,
  bid_o DOUBLE PRECISION,
  bid_h DOUBLE PRECISION,
  bid_l DOUBLE PRECISION,
  bid_c DOUBLE PRECISION,
  ask_o DOUBLE PRECISION,
  ask_h DOUBLE PRECISION,
  ask_l DOUBLE PRECISION,
  ask_c DOUBLE PRECISION,
  mid_o DOUBLE PRECISION,
  mid_h DOUBLE PRECISION,
  mid_l DOUBLE PRECISION,
  mid_c DOUBLE PRECISION,
  spread_open DOUBLE PRECISION,
  spread_high DOUBLE PRECISION,
  spread_low DOUBLE PRECISION,
  spread_close DOUBLE PRECISION,
  source TEXT NOT NULL,
  fetch_batch_id TEXT,
  data_hash TEXT,
  created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
  fetched_at_utc TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (instrument, granularity, time_utc)
);

ALTER TABLE {schema}.candles
  ADD COLUMN IF NOT EXISTS fetch_batch_id TEXT,
  ADD COLUMN IF NOT EXISTS data_hash TEXT,
  ADD COLUMN IF NOT EXISTS created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now();

CREATE TABLE IF NOT EXISTS {schema}.ingestion_runs (
  run_id TEXT PRIMARY KEY,
  started_at_utc TIMESTAMPTZ NOT NULL,
  finished_at_utc TIMESTAMPTZ,
  source TEXT NOT NULL,
  instruments JSONB NOT NULL,
  granularity TEXT NOT NULL,
  start_utc TIMESTAMPTZ,
  end_utc TIMESTAMPTZ,
  status TEXT NOT NULL,
  candles_inserted INTEGER NOT NULL DEFAULT 0,
  candles_updated INTEGER NOT NULL DEFAULT 0,
  error TEXT
);

CREATE TABLE IF NOT EXISTS {schema}.data_quality_reports (
  report_id TEXT PRIMARY KEY,
  created_at_utc TIMESTAMPTZ NOT NULL,
  database_name TEXT NOT NULL,
  schema_name TEXT NOT NULL,
  granularity TEXT NOT NULL,
  start_utc TIMESTAMPTZ,
  end_utc TIMESTAMPTZ,
  status TEXT NOT NULL,
  summary_json JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_{schema}_candles_instrument_granularity_time
  ON {schema}.candles (instrument, granularity, time_utc);
CREATE INDEX IF NOT EXISTS idx_{schema}_candles_granularity_time
  ON {schema}.candles (granularity, time_utc);
CREATE INDEX IF NOT EXISTS idx_{schema}_candles_instrument_granularity
  ON {schema}.candles (instrument, granularity);
""".strip()


def validate_candle_record(candle: CandleRecord) -> None:
    for prefix in ("bid", "ask", "mid"):
        o = getattr(candle, f"{prefix}_o")
        h = getattr(candle, f"{prefix}_h")
        low = getattr(candle, f"{prefix}_l")
        c = getattr(candle, f"{prefix}_c")
        values = [v for v in (o, h, low, c) if v is not None]
        if not values:
            continue
        if len(values) != 4:
            raise ValueError(f"{prefix} OHLC must be complete when present for {candle.instrument}")
        if any(v <= 0 for v in values):
            raise ValueError(f"{prefix} OHLC must be positive for {candle.instrument}")
        if h < max(o, c) or low > min(o, c) or low > h:
            raise ValueError(f"{prefix} OHLC is invalid for {candle.instrument} at {candle.time_utc.isoformat()}")


def compute_spread_fields(candle: CandleRecord) -> dict[str, float | None]:
    def _spread(a: float | None, b: float | None) -> float | None:
        if a is None or b is None:
            return None
        return a - b

    return {
        "spread_open": _spread(candle.ask_o, candle.bid_o),
        "spread_high": _spread(candle.ask_h, candle.bid_h),
        "spread_low": _spread(candle.ask_l, candle.bid_l),
        "spread_close": _spread(candle.ask_c, candle.bid_c),
    }


def compute_candle_data_hash(candle: CandleRecord) -> str:
    """Return a deterministic provenance hash over the normalized candle row."""
    parts = (
        candle.instrument,
        candle.granularity,
        candle.time_utc.astimezone(UTC).isoformat(),
        candle.complete,
        candle.volume,
        candle.bid_o,
        candle.bid_h,
        candle.bid_l,
        candle.bid_c,
        candle.ask_o,
        candle.ask_h,
        candle.ask_l,
        candle.ask_c,
        candle.mid_o,
        candle.mid_h,
        candle.mid_l,
        candle.mid_c,
    )
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()


def common_timestamp_intersection(rows_by_instrument: dict[str, Sequence[dict[str, Any]]]) -> dict[str, Any]:
    timestamp_sets = {
        instrument: {row["time_utc"] for row in rows}
        for instrument, rows in rows_by_instrument.items()
        if rows
    }
    if not timestamp_sets:
        return {"count": 0, "start_utc": None, "end_utc": None}
    common = set.intersection(*timestamp_sets.values())
    if not common:
        return {"count": 0, "start_utc": None, "end_utc": None}
    ordered = sorted(common)
    return {"count": len(ordered), "start_utc": ordered[0], "end_utc": ordered[-1]}


def expected_timestamps(start_utc: datetime, end_utc: datetime, *, granularity: str) -> list[datetime]:
    if granularity != "H4":
        raise ValueError(f"Unsupported granularity for expected timestamps: {granularity}")
    cur = start_utc
    out: list[datetime] = []
    while cur <= end_utc:
        out.append(cur)
        cur += _H4_STEP
    return out


def connect_psycopg(url: str):
    import psycopg

    return psycopg.connect(url)


@dataclass
class PostgresCandleStore:
    config: ResearchDatabaseConfig
    connector: Callable[[str], Any] = connect_psycopg

    @contextmanager
    def connection(self):
        conn = self.connector(self.config.url)
        try:
            yield conn
        finally:
            close = getattr(conn, "close", None)
            if callable(close):
                close()

    def ensure_schema(self) -> None:
        statements = [stmt.strip() for stmt in schema_sql(self.config.schema).split(";") if stmt.strip()]
        with self.connection() as conn:
            with conn.cursor() as cur:
                for stmt in statements:
                    cur.execute(stmt)
            commit = getattr(conn, "commit", None)
            if callable(commit):
                commit()

    def upsert_candles(
        self,
        candles: Iterable[CandleRecord],
        *,
        source: str,
        fetched_at_utc: datetime | None = None,
    ) -> int:
        fetched_at = fetched_at_utc or datetime.now(UTC)
        sql = f"""
INSERT INTO {self.config.schema}.candles (
  instrument, granularity, time_utc, complete, volume,
  bid_o, bid_h, bid_l, bid_c,
  ask_o, ask_h, ask_l, ask_c,
  mid_o, mid_h, mid_l, mid_c,
  spread_open, spread_high, spread_low, spread_close,
  source, fetch_batch_id, data_hash, fetched_at_utc
) VALUES (
  %s, %s, %s, %s, %s,
  %s, %s, %s, %s,
  %s, %s, %s, %s,
  %s, %s, %s, %s,
  %s, %s, %s, %s,
  %s, %s, %s, %s
)
ON CONFLICT (instrument, granularity, time_utc) DO UPDATE SET
  complete = EXCLUDED.complete,
  volume = EXCLUDED.volume,
  bid_o = EXCLUDED.bid_o,
  bid_h = EXCLUDED.bid_h,
  bid_l = EXCLUDED.bid_l,
  bid_c = EXCLUDED.bid_c,
  ask_o = EXCLUDED.ask_o,
  ask_h = EXCLUDED.ask_h,
  ask_l = EXCLUDED.ask_l,
  ask_c = EXCLUDED.ask_c,
  mid_o = EXCLUDED.mid_o,
  mid_h = EXCLUDED.mid_h,
  mid_l = EXCLUDED.mid_l,
  mid_c = EXCLUDED.mid_c,
  spread_open = EXCLUDED.spread_open,
  spread_high = EXCLUDED.spread_high,
  spread_low = EXCLUDED.spread_low,
  spread_close = EXCLUDED.spread_close,
  source = EXCLUDED.source,
  fetch_batch_id = EXCLUDED.fetch_batch_id,
  data_hash = EXCLUDED.data_hash,
  fetched_at_utc = EXCLUDED.fetched_at_utc
"""
        rows = []
        for candle in candles:
            validate_candle_record(candle)
            spreads = compute_spread_fields(candle)
            rows.append(
                (
                    candle.instrument,
                    candle.granularity,
                    candle.time_utc,
                    candle.complete,
                    candle.volume,
                    candle.bid_o,
                    candle.bid_h,
                    candle.bid_l,
                    candle.bid_c,
                    candle.ask_o,
                    candle.ask_h,
                    candle.ask_l,
                    candle.ask_c,
                    candle.mid_o,
                    candle.mid_h,
                    candle.mid_l,
                    candle.mid_c,
                    spreads["spread_open"],
                    spreads["spread_high"],
                    spreads["spread_low"],
                    spreads["spread_close"],
                    source,
                    candle.fetch_batch_id,
                    candle.data_hash or compute_candle_data_hash(candle),
                    fetched_at,
                )
            )
        if not rows:
            return 0
        with self.connection() as conn:
            with conn.cursor() as cur:
                for row in rows:
                    cur.execute(sql, row)
            commit = getattr(conn, "commit", None)
            if callable(commit):
                commit()
        return len(rows)

    def upsert_materialized_candles(
        self,
        candles: Iterable[CandleRecord],
        *,
        source: str,
        fetched_at_utc: datetime | None = None,
        preserve_sources: frozenset[str] | None = None,
    ) -> int:
        """Upsert M1-materialized rows without overwriting preserved native sources."""
        fetched_at = fetched_at_utc or datetime.now(UTC)
        preserve = preserve_sources or frozenset()
        sql = f"""
INSERT INTO {self.config.schema}.candles (
  instrument, granularity, time_utc, complete, volume,
  bid_o, bid_h, bid_l, bid_c,
  ask_o, ask_h, ask_l, ask_c,
  mid_o, mid_h, mid_l, mid_c,
  spread_open, spread_high, spread_low, spread_close,
  source, fetch_batch_id, data_hash, fetched_at_utc
) VALUES (
  %s, %s, %s, %s, %s,
  %s, %s, %s, %s,
  %s, %s, %s, %s,
  %s, %s, %s, %s,
  %s, %s, %s, %s,
  %s, %s, %s, %s
)
ON CONFLICT (instrument, granularity, time_utc) DO UPDATE SET
  complete = EXCLUDED.complete,
  volume = EXCLUDED.volume,
  bid_o = EXCLUDED.bid_o,
  bid_h = EXCLUDED.bid_h,
  bid_l = EXCLUDED.bid_l,
  bid_c = EXCLUDED.bid_c,
  ask_o = EXCLUDED.ask_o,
  ask_h = EXCLUDED.ask_h,
  ask_l = EXCLUDED.ask_l,
  ask_c = EXCLUDED.ask_c,
  mid_o = EXCLUDED.mid_o,
  mid_h = EXCLUDED.mid_h,
  mid_l = EXCLUDED.mid_l,
  mid_c = EXCLUDED.mid_c,
  spread_open = EXCLUDED.spread_open,
  spread_high = EXCLUDED.spread_high,
  spread_low = EXCLUDED.spread_low,
  spread_close = EXCLUDED.spread_close,
  source = EXCLUDED.source,
  fetch_batch_id = EXCLUDED.fetch_batch_id,
  data_hash = EXCLUDED.data_hash,
  fetched_at_utc = EXCLUDED.fetched_at_utc
WHERE {self.config.schema}.candles.source NOT IN ({", ".join("%s" for _ in preserve) if preserve else "%s"})
"""
        if not preserve:
            # No preserved sources — behave like a normal upsert.
            return self.upsert_candles(candles, source=source, fetched_at_utc=fetched_at)
        rows = []
        for candle in candles:
            validate_candle_record(candle)
            spreads = compute_spread_fields(candle)
            rows.append(
                (
                    candle.instrument,
                    candle.granularity,
                    candle.time_utc,
                    candle.complete,
                    candle.volume,
                    candle.bid_o,
                    candle.bid_h,
                    candle.bid_l,
                    candle.bid_c,
                    candle.ask_o,
                    candle.ask_h,
                    candle.ask_l,
                    candle.ask_c,
                    candle.mid_o,
                    candle.mid_h,
                    candle.mid_l,
                    candle.mid_c,
                    spreads["spread_open"],
                    spreads["spread_high"],
                    spreads["spread_low"],
                    spreads["spread_close"],
                    source,
                    candle.fetch_batch_id,
                    candle.data_hash or compute_candle_data_hash(candle),
                    fetched_at,
                )
            )
        if not rows:
            return 0
        preserve_params = tuple(preserve)
        with self.connection() as conn:
            with conn.cursor() as cur:
                for row in rows:
                    cur.execute(sql, row + preserve_params)
            commit = getattr(conn, "commit", None)
            if callable(commit):
                commit()
        return len(rows)

    def max_candle_time(
        self,
        *,
        instrument: str,
        granularity: str,
        source: str | None = None,
    ) -> datetime | None:
        clauses = ["instrument = %s", "granularity = %s"]
        params: list[Any] = [instrument, granularity]
        if source is not None:
            clauses.append("source = %s")
            params.append(source)
        sql = (
            f"SELECT MAX(time_utc) FROM {self.config.schema}.candles "
            f"WHERE {' AND '.join(clauses)}"
        )
        with self.connection() as conn, conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            row = cur.fetchone()
        if not row or row[0] is None:
            return None
        return row[0].astimezone(UTC)

    def count_candles(
        self,
        *,
        instrument: str,
        granularity: str,
        source: str | None = None,
        start_utc: datetime | None = None,
        end_utc: datetime | None = None,
    ) -> int:
        clauses = ["instrument = %s", "granularity = %s"]
        params: list[Any] = [instrument, granularity]
        if source is not None:
            clauses.append("source = %s")
            params.append(source)
        if start_utc is not None:
            clauses.append("time_utc >= %s")
            params.append(start_utc)
        if end_utc is not None:
            clauses.append("time_utc <= %s")
            params.append(end_utc)
        sql = (
            f"SELECT COUNT(*) FROM {self.config.schema}.candles "
            f"WHERE {' AND '.join(clauses)}"
        )
        with self.connection() as conn, conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            row = cur.fetchone()
        return int(row[0]) if row else 0

    def query_candles(
        self,
        *,
        instrument: str,
        granularity: str,
        start_utc: datetime | None = None,
        end_utc: datetime | None = None,
        source: str | None = None,
        exclude_sources: Sequence[str] | None = None,
    ) -> list[dict[str, Any]]:
        clauses = ["instrument = %s", "granularity = %s"]
        params: list[Any] = [instrument, granularity]
        if start_utc is not None:
            clauses.append("time_utc >= %s")
            params.append(start_utc)
        if end_utc is not None:
            clauses.append("time_utc <= %s")
            params.append(end_utc)
        if source is not None:
            clauses.append("source = %s")
            params.append(source)
        if exclude_sources:
            placeholders = ", ".join("%s" for _ in exclude_sources)
            clauses.append(f"source NOT IN ({placeholders})")
            params.extend(exclude_sources)
        sql = (
            "SELECT instrument, granularity, time_utc, complete, volume, "
            "bid_o, bid_h, bid_l, bid_c, ask_o, ask_h, ask_l, ask_c, "
            "mid_o, mid_h, mid_l, mid_c, spread_open, spread_high, spread_low, spread_close, "
            "source, fetch_batch_id, data_hash, created_at_utc, fetched_at_utc "
            f"FROM {self.config.schema}.candles "
            f"WHERE {' AND '.join(clauses)} ORDER BY time_utc ASC"
        )
        with self.connection() as conn, conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
        return [dict(zip(colnames, row, strict=False)) for row in rows]

    def record_ingestion_run(
        self,
        *,
        run_id: str,
        started_at_utc: datetime,
        finished_at_utc: datetime | None,
        source: str,
        instruments_json: str,
        granularity: str,
        start_utc: datetime | None,
        end_utc: datetime | None,
        status: str,
        candles_inserted: int,
        candles_updated: int,
        error: str | None = None,
    ) -> None:
        sql = f"""
INSERT INTO {self.config.schema}.ingestion_runs (
  run_id, started_at_utc, finished_at_utc, source, instruments, granularity,
  start_utc, end_utc, status, candles_inserted, candles_updated, error
) VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (run_id) DO UPDATE SET
  finished_at_utc = EXCLUDED.finished_at_utc,
  status = EXCLUDED.status,
  candles_inserted = EXCLUDED.candles_inserted,
  candles_updated = EXCLUDED.candles_updated,
  error = EXCLUDED.error
"""
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        run_id,
                        started_at_utc,
                        finished_at_utc,
                        source,
                        instruments_json,
                        granularity,
                        start_utc,
                        end_utc,
                        status,
                        candles_inserted,
                        candles_updated,
                        error,
                    ),
                )
            commit = getattr(conn, "commit", None)
            if callable(commit):
                commit()

# M1 Canonical Data Store Design

## Selected Storage Approach

Use the existing local Postgres research store in `src/forex_bot/data/postgres_candle_store.py`. It already provides a durable candle table, OANDA-practice provenance, local-only configuration checks, and an idempotent upsert boundary. This sprint extends that schema for M1 provenance instead of creating SQLite files or committed raw exports.

If Postgres is not configured locally, ingestion stops as `BLOCKED_LOCAL_STORE`.

## Schema

Canonical raw candles are stored in `market_data.candles` unless a different local research schema is configured.

Required M1 row fields:

- `instrument`
- `granularity`, fixed to `M1` for canonical raw lower-timeframe ingestion
- `time_utc`, UTC timestamp
- `complete`
- `volume`
- `bid_o`, `bid_h`, `bid_l`, `bid_c`
- `ask_o`, `ask_h`, `ask_l`, `ask_c`
- `mid_o`, `mid_h`, `mid_l`, `mid_c`
- `spread_open`, `spread_high`, `spread_low`, `spread_close`
- `source`
- `fetch_batch_id`
- `data_hash`
- `created_at_utc`
- `fetched_at_utc`

`mid_*` may be broker-provided or derived for analysis, but bid/ask are the required source prices for spread-aware research.

## Indexes And Uniqueness

Primary uniqueness remains:

```text
instrument + granularity + time_utc
```

Indexes:

- `(instrument, granularity, time_utc)`
- `(granularity, time_utc)`
- `(instrument, granularity)`

## Dedupe Policy

The existing store uses idempotent upsert with keep-last semantics. Re-ingesting the same `(instrument, granularity, time_utc)` updates the candle, source, batch ID, row hash, and fetch timestamp. This matches the historical repository boundary where `CandleRepo.list` also dedupes on load.

## Timezone Policy

All stored and internal timestamps are UTC. Scripts accept ISO-8601 or `YYYY-MM-DD` date inputs, normalize to UTC, and emit redacted manifests with UTC ranges.

## Chunking And Resume Plan

M1 ingestion must never request unbounded history. The M1-specific script will:

- require `--start` and `--end`;
- split requests into safe time chunks;
- respect OANDA's maximum candle count per request;
- support `--max-chunks` for bounded smoke runs;
- use a per-run `fetch_batch_id`;
- write compact manifests only;
- resume by querying existing local rows for the requested instrument/time range before requesting missing chunks.

Large multi-year M1 ingestion is out of scope until chunking and local resume behavior have passed smoke validation.

## Data Quality Rules

The validator must report:

- missing minutes during expected trading sessions;
- duplicate timestamps;
- incomplete M1 candles;
- non-monotonic timestamps;
- incomplete bid/ask OHLC;
- negative or zero spread;
- extreme spread percentiles;
- weekend gaps separately from weekday/data gaps;
- first/last timestamp and row hash/provenance summary.

Missing source minutes are never price-filled.

## Secret Handling

Do not print or commit credentials, account IDs, Authorization headers, tokens, `.env` contents, or raw broker payloads. Manifests may include redacted store metadata and aggregate counts only.

## What Not To Commit

Do not commit SQLite databases, Postgres dumps, raw M1 exports, bulky candle data, raw broker JSON payloads, account identifiers, tokens, or private local output.

## Expected Smoke Test

If local practice read-only credentials and the Postgres store are configured, a future smoke may ingest at most a tiny bounded M1 window for one allowlisted instrument, aggregate it locally, run the validator, and commit only the compact result document. Otherwise the smoke records a blocked status.

## Approval Statement

This design produces no strategy evidence, no CAMPAIGN_021 run, and no approval. `configs/approved_strategies.yaml` remains `approved: []`.

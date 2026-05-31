# LOCAL_POSTGRES_OANDA_DATA_STORE_001 Plan

## Purpose

Build a reproducible local OANDA historical candle data store in the local PostgreSQL database `forex_bot`, using schema `market_data`, so `CAMPAIGN_015` and future walk-forward backtests can run without missing-data `BLOCKED` results.

This sprint is infrastructure only. The canonical research candle source will move from operator-local SQLite assumptions to operator-local PostgreSQL, while preserving the repo's existing safety posture and compatibility with legacy SQLite and CSV-based runners.

## Repo Audit Snapshot

- Working repo: `/Users/kashane/dev/forex-bot`
- Requested branch created: `infra-local-postgres-oanda-historical-data-store-001`
- Starting branch was `main`
- Working tree was clean before edits
- `configs/approved_strategies.yaml` remains `approved: []`
- Paper/demo/live refusal already exists in config, approval, loop, and executor layers
- Current canonical-in-practice candle paths are SQLite-shaped:
  - `data/campaign_002.sqlite3`
  - `data/oanda_h4_research.sqlite3`
  - `research/lean_parity/exports/campaign_002_h4/`
- Existing data/export code is centered on:
  - `src/forex_bot/data/db.py`
  - `src/forex_bot/data/repositories.py`
  - `scripts/rehydrate_oanda_h4_store.py`
  - `scripts/export_lean_parity_data.py`
  - `research/edge_discovery/real_data.py`
  - `research/backtrader_lane/data_adapter.py`

## Non-Goals

- No new strategy creation
- No strategy tuning
- No strategy approval
- No changes to strategy verdicts
- No changes to `configs/approved_strategies.yaml`
- No enabling paper, demo, or live loops
- No broker order submission
- No live OANDA access
- No fake or synthetic canonical data

## Safety Rules

- `configs/approved_strategies.yaml` must remain `approved: []`
- Paper/demo/live loops must remain blocked exactly as they are today
- No code in this sprint may import execution paths into the new Postgres ingestion/audit/export tooling
- OANDA access, if used, must be practice-only and read-only candle endpoints only
- If OANDA credentials are absent, emit `BLOCKED` docs/artifacts and stop cleanly
- If the PostgreSQL connection env var is absent or the database is unreachable, emit `BLOCKED` docs/artifacts and stop cleanly
- If fetched data is partial, mark the run `PARTIAL` and do not present it as canonical-ready for campaign use
- Never print or commit secrets
- Never commit `.env`
- Never commit large exports or SQLite stores

## Local-Only Data Policy

The PostgreSQL research store is operator-local infrastructure. It lives in the local PostgreSQL database `forex_bot`, not in git. Generated compatibility artifacts such as CSV exports and optional SQLite exports are reproducible local outputs and remain gitignored unless they are compact, credential-free manifests or summaries.

DataGrip is a database UI only. No script may depend on DataGrip metadata or config files.

## Connection and Credential Policy

- Required env var: `FOREX_BOT_RESEARCH_DATABASE_URL`
- Example local value: `postgresql://localhost:5432/forex_bot`
- Auth-bearing values are allowed locally, but must never be printed or committed
- Logs, errors, summaries, and blocked artifacts must redact passwords
- `.env.example` may contain only placeholder localhost values if that matches repo convention
- `.env` must never be committed

## Canonical Local Research Store

- Database: `forex_bot`
- Schema: `market_data`
- Canonical source for new research candle data: PostgreSQL
- Legacy compatibility only:
  - `data/campaign_002.sqlite3`
  - `data/oanda_h4_research.sqlite3`
  - `research/lean_parity/exports/campaign_002_h4/*.csv`

## PostgreSQL Schema

Planned schema and tables:

- `market_data.instruments`
- `market_data.candles`
- `market_data.ingestion_runs`
- `market_data.data_quality_reports`

Core requirements:

- Idempotent upsert on `(instrument, granularity, time_utc)`
- No duplicate candles
- Stored bid/ask/mid OHLC plus derived spread fields
- Query helpers by instrument, granularity, and time window
- Metadata and compact healthcheck helpers
- Common timestamp intersection helper across instruments

## Migration / Create-Schema Strategy

Use explicit schema-creation helpers in a new Postgres candle-store module rather than folding PostgreSQL into the existing SQLite operational `Database` wrapper.

Plan:

1. Add a narrow Postgres-specific module under `src/forex_bot/data/`
2. Add deterministic SQL/schema helpers for `market_data`
3. Add `scripts/preflight_research_db.py --create-schema` to create or verify schema/tables/indexes
4. Keep SQLite operational DB code untouched except where compatibility exports need adapters

This keeps the new research store isolated from the bot's existing SQLite operational persistence.

## Ingestion Strategy

Implement `scripts/ingest_oanda_candles_postgres.py` with these rules:

- Reads `FOREX_BOT_RESEARCH_DATABASE_URL`
- Reads OANDA credentials from env only
- Refuses live OANDA environments
- Uses read-only practice candle endpoints only
- Supports H4 first, seven-major default universe
- Supports explicit start/end UTC windows and incremental mode
- Stores only validated candles
- Excludes or clearly flags incomplete candles per policy
- Records each run in `market_data.ingestion_runs`
- Emits compact JSON summaries with redacted connection details
- Returns `BLOCKED` when env or credentials are absent
- Returns nonzero on unsafe config

## Audit Strategy

Implement `scripts/audit_postgres_candle_store.py` to produce compact JSON and Markdown summaries that answer whether the local Postgres store is usable as campaign input.

Checks:

- Candle counts by pair
- First/last timestamp by pair
- Duplicate timestamps
- Missing H4 slots
- Incomplete candles
- OHLC consistency violations
- Nonpositive prices
- Negative/zero spreads
- Spread spike anomalies
- Common timestamp intersection
- Pair coverage matrix
- Overall status: `PASS`, `PARTIAL`, `BLOCKED`, or `FAIL`

Outputs:

- `reports/data_quality/postgres_h4_audit_latest.json`
- `reports/data_quality/postgres_h4_audit_latest.md`

Only compact, credential-free summaries may be committed.

## Export Strategy

Postgres remains canonical. Existing runner needs will be met by exports from Postgres, not by keeping SQLite canonical.

Implement `scripts/export_postgres_research_candles.py` to generate:

1. Lean/Backtrader CSVs under `research/lean_parity/exports/campaign_002_h4/`
2. A compact export manifest with hashes, counts, first/last timestamps, source schema, query window, extraction time, and common intersection
3. Optional SQLite compatibility output at legacy paths only when needed by current runners

All bulky exports remain gitignored.

## Compatibility Strategy

New canonical source:

- PostgreSQL `forex_bot.market_data`

Legacy compatibility only:

- SQLite readers that currently assume `data/campaign_002.sqlite3` or `data/oanda_h4_research.sqlite3`
- CSV readers that currently assume `research/lean_parity/exports/campaign_002_h4/*.csv`

Planned compatibility approach:

1. Leave existing SQLite readers untouched where possible
2. Add an export adapter from Postgres to Lean-style CSV
3. Add an optional export adapter from Postgres to compatibility SQLite if a runner still requires a SQLite file
4. Do not make SQLite the write target for new canonical research data

This minimizes blast radius and preserves existing runner expectations while moving the source of truth to Postgres.

## How This Unblocks CAMPAIGN_015

`CAMPAIGN_015 failed_breakout_reversal` is currently blocked because the local historical candle store is missing or not available in the expected shape. This sprint removes that blocker by:

1. Establishing a reproducible local canonical H4 data store in PostgreSQL
2. Auditing coverage and common timestamp intersection across the seven-pair universe
3. Exporting compatibility artifacts for any runner that still expects SQLite or Lean-style CSV
4. Producing a clear preflight document showing whether `CAMPAIGN_015` can now run

No strategy verdict is produced in this sprint.

## How This Reduces LLM Token Usage

The new data-store workflow will favor compact machine-readable summaries instead of large ad hoc logs:

- Compact JSON for DB preflight
- Compact JSON for ingestion summaries
- Compact JSON + Markdown for audits
- Compact export manifests with counts, windows, hashes, and intersections

This keeps future investigation and campaign-preflight prompts small and evidence-dense instead of requiring large raw dumps or repeated schema spelunking.

## Implementation Phases

### Phase 0

- Audit repo state and current SQLite/export references
- Verify safety gates remain intact
- Write this plan
- Run requested validation baseline

### Phase 1

- Add optional Postgres dependency and env/config helper
- Add tests for blocked env, redaction, and schema defaulting

### Phase 2

- Implement `src/forex_bot/data/postgres_candle_store.py`
- Add schema creation, validation, upsert, querying, spread derivation, and intersection helpers
- Add unit tests and optional integration marker coverage

### Phase 3

- Implement `scripts/preflight_research_db.py`
- Add DataGrip/local setup doc

### Phase 4

- Implement OANDA practice read-only Postgres ingestion script
- Add blocked/unsafe behavior and parsing/idempotency tests

### Phase 5

- Implement Postgres audit script and stable report outputs

### Phase 6

- Implement Postgres export adapters for Lean CSV and optional SQLite compatibility

### Phase 7

- Execute local backfill only if local DB and OANDA credentials exist
- Otherwise emit blocked instructions and stop cleanly

### Phase 8

- Run `CAMPAIGN_015` preflight only if audit status is `PASS`
- Document runnable/unblocked status without producing a strategy verdict

### Phase 9

- Final validation, status checks, and compact sprint summary

## Validation Commands

Baseline and final validation commands for this sprint:

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```

Planned Postgres-specific commands:

```bash
python scripts/preflight_research_db.py --create-schema

python scripts/ingest_oanda_candles_postgres.py \
  --granularity H4 \
  --start 2020-01-01T00:00:00Z \
  --end 2026-05-25T00:00:00Z \
  --instruments EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF NZD_USD

python scripts/audit_postgres_candle_store.py \
  --granularity H4 \
  --out reports/data_quality/postgres_h4_audit_latest

python scripts/export_postgres_research_candles.py \
  --granularity H4 \
  --out research/lean_parity/exports/campaign_002_h4 \
  --sqlite-out data/campaign_002.sqlite3
```

## Expected First Review Files

- `docs/research/LOCAL_POSTGRES_OANDA_DATA_STORE_001_PLAN.md`
- `src/forex_bot/data/postgres_candle_store.py`
- `scripts/preflight_research_db.py`
- `scripts/ingest_oanda_candles_postgres.py`
- `scripts/audit_postgres_candle_store.py`
- `scripts/export_postgres_research_candles.py`

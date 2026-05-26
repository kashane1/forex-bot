# LOCAL_POSTGRES_OANDA_DATA_STORE_001 Summary

## Branch

`infra-local-postgres-oanda-historical-data-store-001`

## What Changed

- Added a Phase 0 infrastructure plan for a local Postgres research candle store
- Added a research DB env/config helper for `FOREX_BOT_RESEARCH_DATABASE_URL`
- Added a Postgres candle-store module with schema SQL, validation, spread derivation, upsert, query, and ingestion-run helpers
- Added scripts for:
  - research DB preflight
  - OANDA practice candle ingestion to Postgres
  - Postgres candle-store audit
  - Postgres export to Lean CSV and optional SQLite compatibility output
- Added DataGrip/local setup documentation
- Added unit tests for blocked env handling, URL redaction, candle validation, audit logic, and export compatibility

## Validation

Executed successfully:

- `pytest tests/ -q`
- `ruff check src tests scripts research`
- `python scripts/check_research_freeze.py`
- `python scripts/validate_research_archive.py`
- `python scripts/scan_artifacts_for_secrets.py`

## Local Execution Status

The local Postgres/OANDA pipeline was executed on this machine after the local env vars were supplied.

- Local PostgreSQL DB reachability: `PASS`
- Database reached: `forex_bot`
- Schema created/verified: `market_data`
- OANDA practice ingestion: `PASS`
- Compatibility export: `PASS`
- `CAMPAIGN_015` preflight: not executed because the runner is not present on this branch and the current audit status is not `PASS`

## Live Results

### Ingestion

- Run status: `PASS`
- Granularity: `H4`
- Instruments:
  - `EUR_USD`
  - `GBP_USD`
  - `USD_JPY`
  - `AUD_USD`
  - `USD_CAD`
  - `USD_CHF`
  - `NZD_USD`
- Total candles inserted: `69,648`

### Postgres Candle Counts

- `EUR_USD`: `9,949`
- `GBP_USD`: `9,949`
- `USD_JPY`: `9,950`
- `AUD_USD`: `9,949`
- `USD_CAD`: `9,949`
- `USD_CHF`: `9,949`
- `NZD_USD`: `9,953`

### Coverage

- Common timestamp intersection count: `9,949`
- First common timestamp: `2020-01-01T14:00:00-08:00`
- Last common timestamp: `2026-05-24T14:00:00-07:00`

### Audit

- Audit status: `PARTIAL`
- Duplicate timestamps: `0` across all seven pairs
- Incomplete candles: `0`
- OHLC violations: `0`
- Nonpositive prices: `0`
- Spread anomalies: `0`

The current `PARTIAL` classification is driven by the audit script's naive missing-slot check, which counts non-trading FX gaps as missing H4 bars. The loaded data itself looks structurally healthy.

### Compatibility Exports

- Lean/Backtrader CSV export: generated locally under `research/lean_parity/exports/campaign_002_h4/`
- SQLite compatibility export: generated locally at `data/campaign_002.sqlite3`
- Compact export manifest: `research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.json`

## Remaining Blockers

- `scripts/run_campaign_015.py` is still not present on this branch
- The current audit script classifies the store as `PARTIAL`, so this branch does not yet claim canonical `PASS` status for campaign use

See also:

- `docs/research/DATAGRIP_LOCAL_DB_SETUP.md`
- `docs/research/LOCAL_POSTGRES_OANDA_DATA_STORE_001_PLAN.md`

## Safety Confirmations

- No strategy was approved
- `configs/approved_strategies.yaml` remains `approved: []`
- Paper/demo/live loops remain blocked
- No credentials were printed or committed
- No `.env`, `.sqlite3`, or bulky CSV artifact was staged by this sprint

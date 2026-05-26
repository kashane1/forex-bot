# LOCAL_POSTGRES_OANDA_DATA_STORE_001 Blocked

## Status

`BLOCKED`

This repo now contains the local PostgreSQL research-store plumbing, but the actual local backfill was not executed on this machine because the required local environment variables were absent at execution time:

- `FOREX_BOT_RESEARCH_DATABASE_URL`
- `OANDA_ACCOUNT_ID_PRACTICE`
- `OANDA_ACCESS_TOKEN_PRACTICE`

No fake data was created. No strategy campaign was run. No strategy verdict changed.

## DataGrip / Postgres Checks

DataGrip is the UI only. The actual scripts use a normal PostgreSQL URL.

Expected local target:

- Data source: `local`
- Database: `forex_bot`
- Schema: `market_data`

Before retrying:

1. Confirm local PostgreSQL is running.
2. Confirm DataGrip can open `local -> forex_bot`.
3. If needed, set a local env var such as:

```bash
export FOREX_BOT_RESEARCH_DATABASE_URL=postgresql://localhost:5432/forex_bot
```

If local auth is required, use your own local username/password, but never commit it and never paste it into repo files.

## Exact Local Commands To Resume

### 1. Preflight the local Postgres DB

```bash
python scripts/preflight_research_db.py --create-schema
```

### 2. Ingest practice-only OANDA H4 candles into Postgres

```bash
python scripts/ingest_oanda_candles_postgres.py \
  --granularity H4 \
  --start 2020-01-01T00:00:00Z \
  --end 2026-05-25T00:00:00Z \
  --instruments EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF NZD_USD
```

### 3. Audit the Postgres candle store

```bash
python scripts/audit_postgres_candle_store.py \
  --granularity H4 \
  --out reports/data_quality/postgres_h4_audit_latest
```

### 4. Export compatibility artifacts for existing runners

```bash
python scripts/export_postgres_research_candles.py \
  --granularity H4 \
  --out research/lean_parity/exports/campaign_002_h4 \
  --sqlite-out data/campaign_002.sqlite3
```

## After the Backfill

If the audit comes back `PASS`, the next safe step is to run the `CAMPAIGN_015` preflight only, not the full campaign, and document whether the runner can use:

- the canonical Postgres store directly, or
- the generated compatibility SQLite / CSV exports

## Safety Confirmations

- `configs/approved_strategies.yaml` remains `approved: []`
- Paper/demo/live loops remain blocked
- No broker order submission path was enabled
- No live OANDA access was used
- No credentials were printed or committed

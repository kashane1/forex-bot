# OANDA H4 Data Rehydration

**Date:** 2026-05-22 · **Branch:** `infra-data-parity-001` · Phase 1

How to (re)build a local **real OANDA practice** H4 candle store for the
six major pairs. The store is the input for the six-pair D1AGG smoke
(Phase 2) and the Lean-parity export (Phase 3).

> The store is **local and gitignored**. It is never committed. Only the
> script, this doc, and tests are committed.

## Script

```bash
python scripts/rehydrate_oanda_h4_store.py            # fetch / top up
python scripts/rehydrate_oanda_h4_store.py --verify   # read-only summary
```

- **Fetch mode** (default) — fetches real OANDA practice H4 bid/ask
  candles for the six majors and upserts them into the store. Idempotent:
  re-running tops up missing candles.
- **Verify mode** (`--verify`) — read-only. Summarizes an existing store
  (per-pair counts, coverage, content hashes) and **needs no
  credentials**. Refuses a store whose candles are not real OANDA.

Options: `--config` (broker settings, default `configs/paper.yaml`),
`--db` (store path), `--from` / `--to` (window).

## Required environment

Fetch mode needs **OANDA practice** credentials, and only practice:

| env var | purpose |
|---|---|
| `OANDA_ACCOUNT_ID_PRACTICE` | practice account id |
| `OANDA_ACCESS_TOKEN_PRACTICE` | practice API token |

Put them in a local, gitignored `.env` (copy `.env.example`) or export
them in the shell. The script **refuses** to run if:

- the credentials are missing or look like placeholders;
- `OANDA_ENVIRONMENT` is set to anything other than `practice`;
- the configured env var names do not contain `PRACTICE`;
- a live token/account matches the practice one.

These are the existing practice-data environment guard
(`forex_bot.guards.assert_practice_data_environment`). The script never
uses live credentials and never prints an account id or token.

## Output store

| property | value |
|---|---|
| path | `data/oanda_h4_research.sqlite3` (gitignored) |
| instruments | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF |
| granularity | H4, bid/ask (`BA`) |
| window | 2020-01-01 → 2026-05-20 |
| candles | completed only (incomplete candles dropped) |

## Provenance and hashes

Every per-pair fetch records a row in the store's `data_sources` table:

- `source` = `oanda-practice`, `host`, the requested window;
- `candles_written`, `candles_dropped_incomplete`, `page_count`;
- `raw_sha256` — SHA-256 over the raw OANDA response bytes;
- `normalized_sha256` — SHA-256 over the normalized candle rows;
- `broker_account_id_redacted` — a redacted account id (never the raw id).

Verify the store at any time:

```bash
python scripts/rehydrate_oanda_h4_store.py --verify
```

It prints, per pair, the candle count, coverage window, and a
`content_hash` (a stable, fetch-order-independent SHA-256 over the
stored candles). Two stores with the same `content_hash` per pair hold
identical candle data. Provenance hashes are also queryable directly:

```sql
SELECT instrument, candles_written, raw_sha256, normalized_sha256
FROM data_sources WHERE campaign = 'h4_research_rehydration';
```

## What is and is not committed

| committed | not committed |
|---|---|
| `scripts/rehydrate_oanda_h4_store.py` | `data/oanda_h4_research.sqlite3` |
| this doc | any `data/*.sqlite3` store |
| `tests/unit/test_rehydrate_oanda_h4.py` | `.env` / credentials |

`data/` is gitignored (`/data/` in `.gitignore`, plus `*.sqlite3`). The
market-data store is large and account-derived; it is rebuilt locally
from this script, never version-controlled.

## If credentials are missing

The script stops with a clear `BLOCKER:` message and exits non-zero. It
**never** falls back to synthetic data. To proceed:

1. Create an OANDA practice account at <https://www.oanda.com/> and
   generate a practice API token.
2. Put `OANDA_ACCOUNT_ID_PRACTICE` and `OANDA_ACCESS_TOKEN_PRACTICE` in
   a local `.env` (copy `.env.example`).
3. Re-run `python scripts/rehydrate_oanda_h4_store.py`.

Until then, the data-dependent phases (six-pair D1AGG smoke, Lean-parity
export) remain blocked — by data availability, not by a code gap. The
tooling is in place and runs the moment a real store exists.

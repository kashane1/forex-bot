# OANDA H4 NZD_USD Rehydration Result — `infra-lean-parity-001` Phase 1

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-001`

> Real OANDA **practice** H4 bid/ask candles, completed candles only.
> No synthetic data. No credential value appears here.

## Status — NZD_USD newly fetched

NZD_USD was **not present** in the local H4 store before this sprint
(the `oanda-practice-readonly-001` rehydration deliberately covered only
the six majors). It was **newly fetched** here, bringing the local store
to the full seven-pair CAMPAIGN_002 H4 universe.

## Fetch parameters

| field | value |
|---|---|
| instrument | NZD_USD |
| date range | 2020-01-01 → 2026-05-20 |
| granularity | H4 |
| price components | BA (bid + ask) |
| OANDA host | `https://api-fxpractice.oanda.com` |
| completeness | completed candles only; incomplete dropped |
| local store | `data/oanda_h4_research.sqlite3` (gitignored — not committed) |

## Exact command

```bash
# .env sourced into the shell (practice credentials).
set -a && source .env && set +a

# Fetch NZD_USD only — idempotent upsert into the existing store; the
# six majors are untouched.
python scripts/rehydrate_oanda_h4_store.py --instruments NZD_USD
```

The `--instruments` option was added to
`scripts/rehydrate_oanda_h4_store.py` this phase so a single instrument
can be topped up without re-fetching the six-pair universe.

## Result

| field | value |
|---|---|
| completed H4 candles in store | **9935** |
| candles written (incl. page-overlap re-fetch) | 9938 |
| dropped incomplete | 0 |
| pages fetched | 4 |
| first timestamp | 2020-01-01T22:00:00+00:00 |
| last timestamp | 2026-05-19T21:00:00+00:00 |
| bid / ask availability | 9935 / 9935 |
| source | `oanda-practice` |

The candle count in the store (9935) is the count of unique completed
candles; the 9938 written includes a few page-boundary re-fetches that
the primary-key upsert deduplicates.

## Provenance hashes

| hash | prefix |
|---|---|
| `raw_sha256` | `829d9d315a19620a…` |
| `normalized_sha256` | `c8724ce78e4c601b…` |
| `content_hash` (recomputed from store) | `dac3dc41b16b244d…` |

`raw_sha256` is the SHA-256 of the concatenated raw OANDA response
bytes; `normalized_sha256` / `content_hash` are SHA-256 over the
normalized, time-sorted candle rows. All recorded in the `data_sources`
table of the local store.

## Safety statement

- The local store `data/oanda_h4_research.sqlite3` is **gitignored**
  (`/data/`, `*.sqlite3`) and is **not** committed. This document
  carries only counts, timestamps, and hash prefixes.
- NZD_USD candles are real OANDA **practice** data fetched read-only
  (`GET .../candles`). No synthetic fallback. No order was submitted.
- **No credential value** — account id or token — was printed, logged,
  or committed.

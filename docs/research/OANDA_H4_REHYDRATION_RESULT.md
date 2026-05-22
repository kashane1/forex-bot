# OANDA H4 Data Rehydration Result — `oanda-practice-readonly-001` Phase 4

**Generated:** 2026-05-22T20:29:45.649553+00:00 · **Branch:** `oanda-practice-readonly-001`

> Real OANDA **practice** H4 bid/ask candles, completed candles only. No synthetic data. No credential value appears here.

## Fetch parameters

| field | value |
|---|---|
| date range | 2020-01-01 → 2026-05-20 |
| granularity | H4 |
| price components | BA (bid + ask) |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF |
| OANDA host | https://api-fxpractice.oanda.com |
| completeness | completed candles only; incomplete dropped |
| local store | `data/oanda_h4_research.sqlite3` (gitignored — not committed) |

## Exact command

```bash
# .env sourced into the shell (practice credentials).
set -a && source .env && set +a
python scripts/rehydrate_oanda_h4_store.py
# read-only result doc (no OANDA call):
python scripts/rehydrate_oanda_h4_store.py --report docs/research/OANDA_H4_REHYDRATION_RESULT.md
```

## Instrument coverage

| instrument | candles | complete | first ts | last ts | pages | dropped | bid avail | ask avail |
|---|---|---|---|---|---|---|---|---|
| EUR_USD | 9931 | 9931 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | 4 | 0 | 9931 | 9931 |
| GBP_USD | 9931 | 9931 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | 4 | 0 | 9931 | 9931 |
| USD_JPY | 9932 | 9932 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | 4 | 0 | 9932 | 9932 |
| AUD_USD | 9931 | 9931 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | 4 | 0 | 9931 | 9931 |
| USD_CAD | 9931 | 9931 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | 4 | 0 | 9931 | 9931 |
| USD_CHF | 9931 | 9931 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | 4 | 0 | 9931 | 9931 |

**Total: 59587 completed H4 candles across 6 pairs.**

## Provenance hashes

Hashes are recorded in the `data_sources` table of the local store. `raw` is the SHA-256 of the concatenated raw OANDA response bytes; `normalized` / `content` are SHA-256 over the normalized, time-sorted candle rows.

| instrument | source | raw_sha256 | normalized_sha256 | content_hash |
|---|---|---|---|---|
| EUR_USD | oanda-practice | `564b332309fe2991…` | `f5d1d1b193020976…` | `c243674516673796…` |
| GBP_USD | oanda-practice | `f4f7717f76f405d7…` | `2c751fec8b0e9f6d…` | `7dabfe8095007635…` |
| USD_JPY | oanda-practice | `14c689d119c8ead2…` | `64836ea0f08e21c7…` | `f71d04e9a6c82809…` |
| AUD_USD | oanda-practice | `b566aed12c983b89…` | `7a19f3e957ea8ee5…` | `fa27466388fd0229…` |
| USD_CAD | oanda-practice | `d3c4b9c9f0b8c057…` | `dc04b583759ec5c6…` | `3b374b90c94e20e3…` |
| USD_CHF | oanda-practice | `1be5d18fce81d3e4…` | `11b0a134792a62a3…` | `64d0a4af0813b658…` |

## Safety statement

- The local store `data/oanda_h4_research.sqlite3` is **gitignored** (`/data/` and `*.sqlite3` in `.gitignore`) and is **not** committed. This document carries only counts, timestamps, and hash prefixes.
- All candles are real OANDA **practice** data fetched read-only (`GET .../candles`). No synthetic data. No order was submitted.
- **No credential value** — account id or token — was printed, logged, or committed.

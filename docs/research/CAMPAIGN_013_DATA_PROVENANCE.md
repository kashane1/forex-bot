# CAMPAIGN_013 Data Provenance — H4 OANDA-practice 7-pair store

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-walk-forward-001`
`strategy_evidence: false`

Phase 1 data-provenance record for CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`. **No new data
was fetched.** The CAMPAIGN_013 evidence sprint reuses the validated
H4 OANDA-practice store already used by CAMPAIGN_002 / CAMPAIGN_010 /
CAMPAIGN_011 / CAMPAIGN_012 (byte-for-byte identical candles).

> No backtest fired in this phase. No broker call. No credentials read.
> No `.env` accessed. No data fetched. No strategy approved.
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_011 is the **null baseline only**, not a trading candidate.

## 1. Data source

| dimension | value |
|---|---|
| `app.database_path` (from config) | `./data/campaign_002.sqlite3` |
| physical file | `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` (gitignored symlink) |
| size | 112 MB |
| origin | originally fetched by CAMPAIGN_002; reused unchanged by CAMPAIGN_010 / 011 / 012 / now CAMPAIGN_013 |
| data label | `oanda-practice` (runner-enforced) |
| committed bulky data | **none** (`*.sqlite3` gitignored; symlink target outside the repo tree) |

## 2. Provenance (per-pair H4)

The `data_sources` table records the original fetch metadata. All
values below were verified against the live SQLite store at the
Phase 1 timestamp.

| pair | completed H4 candles | first bar (UTC) | last bar (UTC) | source label | recorded `raw_sha256` prefix | recorded `normalized_sha256` prefix | recomputed `content_hash` prefix (Phase 1) |
|---|---:|---|---|---|---|---|---|
| EUR_USD | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `f56b30030f3abbd6…` | `f5d1d1b193020976…` | `61814c7198dfab37…` |
| GBP_USD | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `6ea9b168cf234d1d…` | `2c751fec8b0e9f6d…` | `7ae873bc2aaf1df3…` |
| USD_JPY | 9932 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `568f4c6104e1f73a…` | `64836ea0f08e21c7…` | `bd60d2889e1d82c7…` |
| AUD_USD | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `710f6aed5875367a…` | `7a19f3e957ea8ee5…` | `c484a1169bd9ba0c…` |
| USD_CAD | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `9fe3b74d78c5cc5a…` | `dc04b583759ec5c6…` | `14eb5235188af1a1…` |
| USD_CHF | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `46a0f6748c7dfc9c…` | `11b0a134792a62a3…` | `f5ebb07466c28b38…` |
| NZD_USD | 9935 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `c7c38eb2225dc801…` | `c8724ce78e4c601b…` | `899de5f8017e7d2f…` |
| **total** | **69,522** | | | | | | |

### 2.1 Verification against CAMPAIGN_010 / 011 / 012

**Recorded `raw_sha256` and `normalized_sha256` prefixes match
CAMPAIGN_010 / 011 / 012 verbatim** (see
[`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md),
[`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md),
and [`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md)
§2). This confirms:

- The same physical SQLite store backs all four real-edge sprints
  + the null model.
- No data has been touched since CAMPAIGN_010's evidence run.
- The CAMPAIGN_013 cross-pair rotation hypothesis is tested on
  **byte-for-byte identical candles** to CAMPAIGN_010's session
  breakout, CAMPAIGN_011's random-entry anchor, and CAMPAIGN_012's
  regime switcher — only the entry mechanism differs.

## 3. Instrument coverage

| pair | tier | H4 coverage | matches CAMPAIGN_010 / 011 / 012? |
|---|---|:---:|:---:|
| EUR_USD | majors | ✓ | ✓ |
| GBP_USD | majors | ✓ | ✓ |
| USD_JPY | majors | ✓ | ✓ |
| AUD_USD | commodity | ✓ | ✓ |
| USD_CAD | commodity | ✓ | ✓ |
| USD_CHF | safe-haven | ✓ | ✓ |
| NZD_USD | commodity | ✓ | ✓ |

7 / 7 pairs from the CAMPAIGN_013 frozen universe present,
byte-for-byte identical to CAMPAIGN_010 / 011 / 012.

## 4. Timeframe coverage

H4 is the binding execution timeframe for CAMPAIGN_013 (per
[`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
§2). No D1AGG aggregation is required for C6.

## 5. First / last timestamps

All 7 pairs span:

- **First H4 bar:** `2020-01-01 22:00:00 UTC`
- **Last H4 bar:** `2026-05-19 21:00:00 UTC`

NZD_USD has one additional bar; the difference is < 0.05 % and does
not affect fold structure. The cross-pair runner aligns all 7 pairs
to a common index (intersection); pairs with missing bars at a given
timestamp are absent from the index for that timestamp.

## 6. Gap summary

Per the CAMPAIGN_010 / 011 / 012 audits on the same store (no
re-audit needed; data is unchanged), the H4 universe has clean
coverage with weekend-only gaps; no anomalous weekday gaps that
would distort the fold structure. The runner aborts per-pair if a
fold's test window returns zero candles.

## 7. Commands run in Phase 1

| command | purpose | broker call? | credentials? |
|---|---|:---:|:---:|
| `python -c "import sqlite3; ..."` to query `candles` table | candle counts + first/last + content hash | **no** | **no** |
| `python -c "import sqlite3; ..."` to query `data_sources` table | recorded `raw_sha256` / `normalized_sha256` / `source` | **no** | **no** |

**No `fetch-candles` call. No OANDA HTTP request. No `.env` read.
No broker session opened. No account/order/trade/position/transaction
endpoint queried.** This phase is read-only against the existing
local SQLite store.

## 8. Comparison to CAMPAIGN_010 / 011 / 012

| dimension | CAMPAIGN_010 | CAMPAIGN_011 | CAMPAIGN_012 | CAMPAIGN_013 |
|---|---|---|---|---|
| physical SQLite store | same | same | same | **same** |
| recorded `raw_sha256` prefixes | as recorded | identical | identical | **identical** |
| recorded `normalized_sha256` prefixes | as recorded | identical | identical | **identical** |
| H4 candle counts per pair | as recorded | identical | identical | **identical** |
| span | 2020-01-01 → 2026-05-19 | identical | identical | **identical** |
| 7-pair universe | EUR/GBP/JPY/AUD/CAD/CHF/NZD | identical | identical | **identical** |
| data source label | `oanda-practice` | identical | identical | **identical** |

The entry-signal comparison across all four real-edge candidates
(CAMPAIGN_010 session breakout, CAMPAIGN_011 random null,
CAMPAIGN_012 regime switcher, CAMPAIGN_013 cross-pair rotation) is
**apples-to-apples on byte-for-byte identical candles**. Any
differences in metrics are due to the entry mechanism alone.

## 9. Local uncommitted files created

| path | committed? | reason |
|---|:---:|---|
| (none) | n/a | this phase only reads the existing store and writes this provenance doc |

## 10. Explicit statement: no bulky data committed

- `*.sqlite3` is gitignored (verified in `.gitignore`).
- The data symlink target is outside the repo tree.
- No CSV / Parquet / raw candle file was created or staged.
- No credential / `.env` / token was read or printed.

## 11. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md), [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md), [`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md) (sibling references — identical hashes)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

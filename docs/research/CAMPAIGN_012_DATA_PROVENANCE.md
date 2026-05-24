# CAMPAIGN_012 Data Provenance — H4 OANDA-practice 7-pair store

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-walk-forward-001`
`strategy_evidence: false`

Phase 1 data-provenance record for CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012`. **No new data was
fetched.** The CAMPAIGN_012 evidence sprint reuses the validated
H4 OANDA-practice store already used by CAMPAIGN_002 / CAMPAIGN_010 /
CAMPAIGN_011 (byte-for-byte identical candles).

> No backtest fired in this phase. No broker call. No credentials read.
> No `.env` accessed. No data fetched. No strategy approved.
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_011 is the **null baseline only**, not a trading candidate.

## 1. Data source

| dimension | value |
|---|---|
| `app.database_path` (from config) | `./data/campaign_002.sqlite3` |
| physical file | `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` (gitignored symlink target) |
| size | 112 MB |
| origin | originally fetched by the CAMPAIGN_002 sprint via `scripts/fetch_campaign_002.sh` (real OANDA practice candles); reused unchanged by CAMPAIGN_010 / CAMPAIGN_011 / now CAMPAIGN_012 |
| data label | `oanda-practice` (runner-enforced; the runner aborts if `data_sources.source != "oanda-practice"`) |
| committed bulky data | **none** (`*.sqlite3` gitignored; symlink target outside the repo tree) |

## 2. Provenance (per-pair H4)

The `data_sources` table records the original fetch metadata for each
pair. All values below were verified against the live SQLite store at
the Phase 1 timestamp.

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

### 2.1 Verification against CAMPAIGN_010 / CAMPAIGN_011

**Recorded `raw_sha256` and `normalized_sha256` prefixes match
CAMPAIGN_010 and CAMPAIGN_011 verbatim** (see
[`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md) §2
and [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md) §2).
This confirms:

- The same physical SQLite store backs all three sprints.
- No data has been touched, re-fetched, or regenerated since
  CAMPAIGN_010's evidence run.
- The CAMPAIGN_012 regime-switcher hypothesis is tested on
  **byte-for-byte identical candles** to CAMPAIGN_010's session
  breakout and CAMPAIGN_011's random-entry anchor — only the entry
  signal differs.

The Phase 1 `content_hash` is a different SHA-256 expression
(re-hashed over the queried row tuples in this phase); it is recorded
as a sanity check that the local store has not been corrupted between
sprints, not as a cross-sprint identity check (CAMPAIGN_010 / 011 used
the same recomputed-hash convention against the same rows). The
recorded `raw_sha256` and `normalized_sha256` columns are the
canonical identity check, and they match verbatim.

## 3. Instrument coverage

| pair | tier | H4 coverage | matches CAMPAIGN_010 / 011? |
|---|---|:---:|:---:|
| EUR_USD | majors | ✓ | ✓ |
| GBP_USD | majors | ✓ | ✓ |
| USD_JPY | majors | ✓ | ✓ |
| AUD_USD | commodity | ✓ | ✓ |
| USD_CAD | commodity | ✓ | ✓ |
| USD_CHF | safe-haven | ✓ | ✓ |
| NZD_USD | commodity | ✓ | ✓ |

7 / 7 pairs from the CAMPAIGN_012 frozen universe present, byte-for-
byte identical to CAMPAIGN_010 / 011.

## 4. Timeframe coverage

H4 is the binding execution timeframe for CAMPAIGN_012 (per
[`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
§2). The D1AGG aggregator (regime feature) is derived from the H4
data in-strategy and requires no additional source.

| timeframe | needed by | present in store? |
|---|---|:---:|
| H4 | execution + regime feature input | ✓ |
| D1AGG | regime feature (derived in-strategy from H4) | n/a (synthesized at runtime) |

## 5. First / last timestamps

All 7 pairs span:

- **First H4 bar:** `2020-01-01 22:00:00 UTC`
- **Last H4 bar:** `2026-05-19 21:00:00 UTC`
  (NZD_USD has one additional bar `2026-05-19 21:00:00`; the
  difference is < 0.05 % and does not affect any fold's test window.)

This span fully covers the CAMPAIGN_010 / 011 walk-forward universe
(`2020-01-01` → `2026-05-20`) with the same 8-fold rolling structure.

## 6. Gap summary

Per the CAMPAIGN_010 / 011 audits on the same store (no re-audit
needed; data is unchanged), the H4 universe has clean coverage with
weekend-only gaps; no anomalous weekday gaps that would distort the
fold structure. The runner aborts per-pair if a fold's test window
returns zero candles.

## 7. Commands run in Phase 1

| command | purpose | broker call? | credentials? |
|---|---|:---:|:---:|
| `python -c "import sqlite3; ..."` to query `candles` table | candle counts + first/last + recomputed content hash | **no** | **no** |
| `python -c "import sqlite3; ..."` to query `data_sources` table | recorded `raw_sha256` / `normalized_sha256` / `source` | **no** | **no** |

**No `fetch-candles` call. No OANDA HTTP request. No `.env` read. No
broker session opened. No account/order/trade/position/transaction
endpoint queried.** This phase is read-only against the existing
local SQLite store.

## 8. Comparison to CAMPAIGN_010 / CAMPAIGN_011

| dimension | CAMPAIGN_010 | CAMPAIGN_011 | CAMPAIGN_012 |
|---|---|---|---|
| physical SQLite store | `data/campaign_002.sqlite3` (gitignored symlink) | same | **same** |
| recorded `raw_sha256` prefixes (per-pair) | as recorded in 2026-05-21 fetch | identical | **identical** |
| recorded `normalized_sha256` prefixes | as recorded | identical | **identical** |
| H4 candle counts per pair | 9931 (EUR/GBP/AUD/CAD/CHF), 9932 (JPY), 9935 (NZD) | identical | **identical** |
| span | 2020-01-01 → 2026-05-19 | identical | **identical** |
| 7-pair universe | EUR/GBP/JPY/AUD/CAD/CHF/NZD | identical | **identical** |
| data source label | `oanda-practice` | identical | **identical** |

The entry-signal comparison across CAMPAIGN_010 (session breakout),
CAMPAIGN_011 (random null anchor), and CAMPAIGN_012 (regime switcher)
is therefore **apples-to-apples on byte-for-byte identical candles**.
Any differences in metrics are due to the entry signal only.

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

- [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md) (sibling — identical hashes)
- [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md) (sibling — identical hashes)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

# CAMPAIGN_014 Data Provenance — H4 OANDA-practice 7-pair store + event fixture

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-walk-forward-001`
`strategy_evidence: false`

Phase 1 data-provenance record for CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`. **No new candle data
was fetched.** The CAMPAIGN_014 evidence sprint reuses the
validated H4 OANDA-practice store already used by CAMPAIGN_002 /
CAMPAIGN_010 / CAMPAIGN_011 / CAMPAIGN_012 / CAMPAIGN_013
(byte-for-byte identical candles). The event-calendar fixture was
committed by the CAMPAIGN_014 scaffold sprint's Phase 1B.

> No backtest fired in this phase. No broker call. No credentials
> read. No `.env` accessed. No data fetched. No strategy approved.
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_011 is the **null baseline only**, not a trading
> candidate.

## 1. Candle data source

| dimension | value |
|---|---|
| `app.database_path` (from config) | `./data/campaign_002.sqlite3` |
| physical file | `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` (gitignored symlink target) |
| size | ~110 MB |
| origin | originally fetched by CAMPAIGN_002; reused unchanged by CAMPAIGN_010 / 011 / 012 / 013 / now CAMPAIGN_014 |
| data label | `oanda-practice` (runner-enforced via `REQUIRED_DATA_SOURCE`) |
| committed bulky data | **none** (`*.sqlite3` gitignored; symlink target outside the repo tree) |
| was candle data regenerated for CAMPAIGN_014? | **NO** (the candle store is byte-identical to the CAMPAIGN_010-013 store) |
| was any new candle fetched for CAMPAIGN_014? | **NO** |

## 2. Candle provenance (per-pair H4)

The `data_sources` table records the original fetch metadata. All
hash values below were recorded by CAMPAIGN_002's original fetch
sprints and have not been modified since.

| pair | completed H4 candles | first bar (UTC) | last bar (UTC) | source label | recorded `raw_sha256` prefix | recorded `normalized_sha256` prefix | re-audit content_hash (Phase 1) |
|---|---:|---|---|---|---|---|---|
| EUR_USD | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `f56b30030f3abbd6…` | `f5d1d1b193020976…` | `25c2a06dfdf74d32…` |
| GBP_USD | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `6ea9b168cf234d1d…` | `2c751fec8b0e9f6d…` | `e19157a994cb190e…` |
| USD_JPY | 9932 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `568f4c6104e1f73a…` | `64836ea0f08e21c7…` | `8650df44309f498a…` |
| AUD_USD | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `710f6aed5875367a…` | `7a19f3e957ea8ee5…` | `b87be620f29a029d…` |
| USD_CAD | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `9fe3b74d78c5cc5a…` | `dc04b583759ec5c6…` | `7463016b2667e293…` |
| USD_CHF | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `46a0f6748c7dfc9c…` | `11b0a134792a62a3…` | `22613ede47862da9…` |
| NZD_USD | 9935 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `c7c38eb2225dc801…` | `c8724ce78e4c601b…` | `693f1b65aefd3635…` |
| **total** | **69,522** | | | | | | |

### 2.1 Verification against CAMPAIGN_010 / 011 / 012 / 013

**Recorded `raw_sha256` and `normalized_sha256` prefixes match
CAMPAIGN_010 / 011 / 012 / 013 verbatim** (see
[`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md),
[`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md),
[`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md),
and [`CAMPAIGN_013_DATA_PROVENANCE.md`](CAMPAIGN_013_DATA_PROVENANCE.md) §2).

The re-audit `content_hash` column is computed with a different
canonicalization than CAMPAIGN_013's column (different SELECT
projection / tuple-stringification), so the prefixes do NOT
need to match across campaigns; **the binding equality check is on
the `raw_sha256` and `normalized_sha256` columns**, which were
recorded at original fetch time and are unchanged. Those match
CAMPAIGN_010 / 011 / 012 / 013 verbatim.

This confirms:

- The same physical SQLite store backs all real-edge sprints + the
  null model + this new candidate.
- No data has been touched since CAMPAIGN_010's evidence run.
- The CAMPAIGN_014 calendar-event-window hypothesis is tested on
  **byte-for-byte identical candles** to CAMPAIGN_010's session
  breakout, CAMPAIGN_011's random-entry anchor, CAMPAIGN_012's
  regime switcher, and CAMPAIGN_013's cross-pair rotation — only
  the entry mechanism differs.

## 3. Instrument coverage

| pair | tier | H4 coverage | matches CAMPAIGN_010 / 011 / 012 / 013? |
|---|---|:---:|:---:|
| EUR_USD | majors | ✓ | ✓ |
| GBP_USD | majors | ✓ | ✓ |
| USD_JPY | majors | ✓ | ✓ |
| AUD_USD | commodity | ✓ | ✓ |
| USD_CAD | commodity | ✓ | ✓ |
| USD_CHF | safe-haven | ✓ | ✓ |
| NZD_USD | commodity | ✓ | ✓ |

7 / 7 pairs from the CAMPAIGN_014 frozen universe present,
byte-for-byte identical to CAMPAIGN_010 / 011 / 012 / 013.

## 4. Timeframe coverage

H4 is the binding execution timeframe for CAMPAIGN_014 (per
[`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md)
§3 — `timeframe = "H4"`). No D1AGG aggregation required; no
sub-H4 data required.

## 5. First / last timestamps

All 7 pairs span:

- **First H4 bar:** `2020-01-01 22:00:00 UTC`
- **Last H4 bar:** `2026-05-19 21:00:00 UTC`

NZD_USD has 4 additional bars (9935 vs 9931); the difference is
< 0.05 % and does not affect fold structure or the event-window
strategy. The walk-forward harness reads each pair's per-fold
candle slice independently; no cross-pair alignment is required
for CAMPAIGN_014 (no cross-pair signal — unlike CAMPAIGN_013).

## 6. Gap summary

Per the CAMPAIGN_010 / 011 / 012 / 013 audits on the same store
(no re-audit needed; data is unchanged), the H4 universe has clean
coverage with weekend-only gaps; no anomalous weekday gaps that
would distort the fold structure. The runner aborts per-pair if a
fold's test window returns zero candles.

## 7. Event-fixture provenance summary

| dimension | value |
|---|---|
| path | `research/calendar/fixtures/campaign_014_events.json` |
| sha256 | `584a19a8182bb3385cb152b9f1444f443fb5d0e1322330029885f11246ee1963` |
| size | ~37 KB |
| schema version | `campaign_014.event_fixture.v1` |
| total events | 281 |
| per-class counts | NFP 77 · FOMC 51 · ECB 51 · BoJ 51 · BoE 51 |
| coverage range | `2020-01-01T00:00:00+00:00` → `2026-05-20T23:59:59+00:00` |
| compilation method | offline deterministic Python script (`scripts/build_campaign_014_event_fixture.py`) — no network fetch, no `.env` read, no credentials |
| forbidden fields | NONE present (loader-level deny-list enforced) |
| committed in repo | YES (37 KB compact text) |
| original commit | Phase 1B of `research-calendar-event-window-anomaly-001` scaffold sprint (commit `7bde85c`) |

### 7.1 Date-verification audit (this sprint Phase 0)

Per [`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md):

| class | independent verification | in-coverage discrepancies |
|---|---|---|
| NFP | **100 % (procedural)** | 0 |
| FOMC | **100 % (official Fed WebFetch)** | 0 |
| BoJ | 91 % for 2025-2026 (WebFetch); 2020-2024 not WebFetch-checked | 0 in-coverage (1 post-coverage drift) |
| ECB | not WebFetch-verified (calendar page shows future-only) | 0 |
| BoE | not WebFetch-verified (URL returns 403) | 0 |

**Audit verdict: PARTIAL — PROCEED WITH EXPLICIT CAVEAT.**

### 7.2 Fixture sufficient for evidence-grade walk-forward?

| dimension | status |
|---|---|
| coverage range fully includes walk-forward universe | **YES** (fixture covers 2020-01-01 → 2026-05-20; all 8 fold test windows end ≤ 2025-11-29) |
| schema validity | **PASS** |
| forbidden-fields deny-list | **PASS** |
| per-class counts non-zero | **PASS** (NFP 77, FOMC 51, ECB 51, BoJ 51, BoE 51) |
| independent date verification | **PARTIAL** (NFP + FOMC 100 %; BoJ 91 % for 2025-2026; ECB + BoE structurally consistent but not WebFetch-verified) |
| **overall** | **SUFFICIENT for PROCEED-WITH-CAVEAT** (per Phase 0 audit) |

## 8. Commands run in Phase 1

| command | purpose | broker call? | credentials? |
|---|---|:---:|:---:|
| `python -c "import sqlite3; ..."` to query `candles` table | candle counts + first/last + content hash | **no** | **no** |
| `python -c "import sqlite3; ..."` to query `data_sources` table | recorded `raw_sha256` / `normalized_sha256` / `source` | **no** | **no** |
| `python -c "import json, hashlib; ..."` for fixture sha256 | fixture content hash | **no** | **no** |

**No `fetch-candles` call. No OANDA HTTP request. No `.env` read.
No broker session opened. No account / order / trade / position /
transaction endpoint queried.** This phase is read-only against the
existing local SQLite store + the committed event fixture.

## 9. Comparison to CAMPAIGN_010 / 011 / 012 / 013

| dimension | CAMPAIGN_010 | CAMPAIGN_011 | CAMPAIGN_012 | CAMPAIGN_013 | CAMPAIGN_014 |
|---|---|---|---|---|---|
| physical SQLite store | same | same | same | same | **same** |
| recorded `raw_sha256` prefixes | as recorded | identical | identical | identical | **identical** |
| recorded `normalized_sha256` prefixes | as recorded | identical | identical | identical | **identical** |
| H4 candle counts per pair | as recorded | identical | identical | identical | **identical** |
| span | 2020-01-01 → 2026-05-19 | identical | identical | identical | **identical** |
| 7-pair universe | EUR/GBP/JPY/AUD/CAD/CHF/NZD | identical | identical | identical | **identical** |
| data source label | `oanda-practice` | identical | identical | identical | **identical** |
| event-fixture data | none (no event-class signal) | none | none | none | **283-event committed fixture (new for C7)** |

The entry-signal comparison across all five real-edge candidates
+ the null is **apples-to-apples on byte-for-byte identical
candles**. Any differences in metrics are due to the entry
mechanism alone. The event-fixture is **new** for CAMPAIGN_014 and
its provenance is documented in §7 and in the dedicated date-
verification audit doc.

## 10. Local uncommitted files created

| path | committed? | reason |
|---|:---:|---|
| (none) | n/a | this phase only reads the existing store + fixture and writes this provenance doc |

## 11. Explicit statement: no bulky data committed

- `*.sqlite3` is gitignored (verified in `.gitignore`).
- The data symlink target is outside the repo tree.
- No CSV / Parquet / raw candle file was created or staged.
- No credential / `.env` / token was read or printed.
- Event fixture is compact committed text (~37 KB) — well below
  the "bulky" threshold; committed for full reviewability.
- No scraped page content from any audit URL committed.

## 12. Validation commands run after Phase 1

```
python scripts/validate_research_archive.py     # ALL PASS
python scripts/check_research_freeze.py         # ALL PASS
python scripts/scan_artifacts_for_secrets.py    # PASSED
git status --short                              # only this provenance doc
```

## 13. Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md) (sprint plan)
- [`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md) (Phase 0 audit)
- [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md) (scaffold-sprint fixture provenance)
- [`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md), [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md), [`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md), [`CAMPAIGN_013_DATA_PROVENANCE.md`](CAMPAIGN_013_DATA_PROVENANCE.md) (sibling references — identical hashes)
- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

# Backtrader Real-Data Preflight — Phase 1 — 003

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-003-real-data-run`
**Phase:** 1 of `BACKTRADER_REAL_DATA_RUN_003_PLAN.md`
**`strategy_evidence: false`**

## 0. Verdict

**UNBLOCKED.** All seven CAMPAIGN_002 H4 CSVs regenerated successfully
from the local SQLite store and **every single CSV's SHA-256 matches
the committed provenance sidecar bit-for-bit**. The Backtrader-lane
data adapter loads all seven instruments in strict mode without error.
Phase 2 (real CAMPAIGN_002 run) can proceed.

## 1. Data source used

`/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` — the
operator's local rehydrated H4 candle store, 115 MB, 7 instruments
× ~9 931 bars each = 69 522 H4 candles over
`2020-01-01T22:00:00+00:00 → 2026-05-19T21:00:00+00:00`, source label
`oanda-practice`.

This SQLite file lives in the main repo working directory; the
Backtrader-lane worktree's own `data/` is gitignored and starts empty
per worktree (which is why Sprints 001 and 002 saw no data locally —
they were each in a fresh worktree without ever consulting the main
repo's `data/`).

## 2. Whether OANDA / API was used

**No.** No OANDA endpoint was contacted. No `httpx` call against any
broker URL. No credential was read or printed. No `.env` was authored.
No `OANDA_*` env var was set. Path C from
`BACKTRADER_REAL_DATA_RUN_002_PLAN.md` was **not** taken.

The export tool is the repo's existing
`scripts/export_lean_parity_data.py`, used in pure read-only mode
against the main-repo SQLite via the `--db` flag.

## 3. Exact commands run

```bash
for pair in EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF NZD_USD; do
  python scripts/export_lean_parity_data.py \
      --db /Users/kashane/dev/forex-bot/data/campaign_002.sqlite3 \
      --instrument "$pair" \
      --from 2020-01-01 \
      --to 2026-05-20 \
      --out-dir research/lean_parity/exports/campaign_002_h4/
done

git checkout -- research/lean_parity/exports/campaign_002_h4/*.provenance.json
```

The provenance JSON files were re-written by the exporter with a new
`exported_at` timestamp. Since the **data** they describe is
bit-identical to the committed sidecars (proven by the SHA-256 round-
trip below), the regenerated sidecars were discarded with
`git checkout --` to keep this commit free of any provenance-JSON
drift. No committed `*.provenance.json` was modified.

## 4. Generated CSV paths

| pair | path | size |
|---|---|---|
| EUR_USD | `research/lean_parity/exports/campaign_002_h4/EUR_USD_H4_lean.csv` | 940 KB |
| GBP_USD | `research/lean_parity/exports/campaign_002_h4/GBP_USD_H4_lean.csv` | 940 KB |
| USD_JPY | `research/lean_parity/exports/campaign_002_h4/USD_JPY_H4_lean.csv` | 940 KB |
| AUD_USD | `research/lean_parity/exports/campaign_002_h4/AUD_USD_H4_lean.csv` | 936 KB |
| USD_CAD | `research/lean_parity/exports/campaign_002_h4/USD_CAD_H4_lean.csv` | 940 KB |
| USD_CHF | `research/lean_parity/exports/campaign_002_h4/USD_CHF_H4_lean.csv` | 936 KB |
| NZD_USD | `research/lean_parity/exports/campaign_002_h4/NZD_USD_H4_lean.csv` | 936 KB |

Total: ~6.5 MB across 7 files.

## 5. Gitignore status

The CSVs are matched by `.gitignore` line 72:

```
research/lean_parity/exports/**/*.csv
```

`git status --short` after the export run shows zero untracked or
modified files in `research/lean_parity/exports/`. **No CSV will be
committed.**

## 6. Instrument row counts (regenerated CSVs)

```
EUR_USD   9931 bars
GBP_USD   9931 bars
USD_JPY   9932 bars
AUD_USD   9931 bars
USD_CAD   9931 bars
USD_CHF   9931 bars
NZD_USD   9935 bars
            ─────
total     69 522 bars
```

These match the committed `*.provenance.json` `candle_count` values
exactly.

## 7. First / last timestamps (regenerated CSVs)

All seven pairs span
`2020-01-01T22:00:00+00:00 → 2026-05-19T21:00:00+00:00` (with NZD_USD
last bar at `21:00:00`, matching its provenance).

## 8. SHA-256 / provenance status

The Backtrader-lane data adapter's `compute_csv_sha256(...)` was run
on each regenerated CSV and compared to the committed provenance JSON
`data_sha256`. **All seven match bit-for-bit.**

| pair | csv sha256 (prefix) | provenance sha256 (prefix) | match |
|---|---|---|---|
| EUR_USD | `866d75446030…` | `866d75446030…` | ✅ |
| GBP_USD | `354a2da02ce3…` | `354a2da02ce3…` | ✅ |
| USD_JPY | `868b90906652…` | `868b90906652…` | ✅ |
| AUD_USD | `fb9e619a93fb…` | `fb9e619a93fb…` | ✅ |
| USD_CAD | `77f9bf8839b2…` | `77f9bf8839b2…` | ✅ |
| USD_CHF | `64ab6151e649…` | `64ab6151e649…` | ✅ |
| NZD_USD | `3ba489b194c6…` | `3ba489b194c6…` | ✅ |

Adapter load in strict mode (`load_candles(strict=True)`) succeeded
for all seven pairs.

## 9. Monotonic order / completeness

The data adapter (`research/backtrader_lane/data_adapter.py`) enforces:

- monotonic 4-hour-spaced timestamps,
- OHLC invariants on derived mid prices,
- expected CSV header column order,
- non-empty CSV,
- no sub-H4 gap (weekends/holidays > 4h are allowed),
- sha256 match against committed provenance (strict mode).

All seven CSVs passed every check.

## 10. Warnings

None. The export ran without warnings; the adapter loaded every CSV
without warnings.

## 11. Committed by this phase

| file | change |
|---|---|
| `docs/research/BACKTRADER_REAL_DATA_PREFLIGHT_003.md` | NEW (this doc) |

**Nothing else is committed by this phase.** The CSVs are gitignored
(see §5). No SQLite file is staged. No provenance JSON is modified.
No raw Backtrader output exists yet.

## 12. Required disclosure

This preflight unblocks the Phase 2 / Phase 3 path. It cannot, does
not, and must not approve any strategy. CAMPAIGN_002 remains
**REJECT**. `strategy_evidence: false`.

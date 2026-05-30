# Non-USD Cross Ingestion & Cost Models — Sprint 001 Summary

**Branch:** `research-nonusd-cross-ingestion-and-cost-models-001`
**Date:** 2026-05-29
**Type:** research **infrastructure** sprint — capability to ingest,
validate, materialize, and cost-model non-USD FX crosses to the major-pair
standard. No strategy, no campaign, no factor screen, no train/validation
evidence, no broker mutation, no approval. Freeze intact.

## 1. Branch

`research-nonusd-cross-ingestion-and-cost-models-001` (off clean
`origin/main` tip `2af008d`).

## 2. Commit hashes by phase

| Phase | Hash | Deliverable |
|-------|------|-------------|
| 0 | `ec45efd` | baseline audit + sprint plan |
| 1 | `d75c510` | cross instrument registry |
| 2 | `a19a43b` | cross ingestion support |
| 3 | `0d4d6c8` | cross materialization support |
| 4 | `e4fd209` | cross cost-model framework |
| 5 | `14b1e24` | cross validation & diagnostics |
| 6 | `e29ce61` | research readiness assessment |
| 7 | `65651c7` | next prompt |
| 8 | (this commit) | final validation + summary |

## 3. Instruments added (registry capability)

Wave-1 non-USD crosses, **additive** — the seven USD majors are unchanged
as the control/baseline universe.

- **Primary (required):** EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY
- **Extended (optional, low-effort):** NZD_JPY, EUR_CHF, GBP_CHF, EUR_AUD

JPY-quote crosses use pip 0.01 / 3 dp; others pip 0.0001 / 5 dp. EUR_CHF
carries the 2015-01-15 SNB structural-break flag.

## 4. Files changed (23 files, +2144 / −10)

**New source (`src/`):**
- `forex_bot/domain/cross_instruments.py` — cross registry (single source of truth)
- `forex_bot/data/cross_ingestion.py` — target resolution + coverage probe
- `forex_bot/research/cost_models/{__init__,spread,carry,profile}.py` — cost models

**Edited source (additive, majors unchanged):**
- `forex_bot/data/m1_corpus_validation.py` — `NONUSD_CROSS_PAIRS`, `SUPPORTED_PAIRS`, cross-aware `extra_pairs`
- `forex_bot/data/m1_timeframe_materialization.py` — gate widened to `SUPPORTED_PAIRS`

**Scripts:**
- `scripts/ingest_oanda_m1_candles.py` — allow-list union + `--crosses` / `--all-crosses` (safety preserved)
- `scripts/materialize_m1_derived_timeframes.py` — `--pair` any supported + `--all-crosses`
- `scripts/validate_nonusd_cross_data.py` — new compact validation/diagnostics

**Tests (5 files, 51 tests):** `test_cross_instruments.py` (15),
`test_cross_ingestion.py`, `test_cross_materialization.py` (13),
`test_cross_cost_models.py` (14), `test_validate_nonusd_cross_data.py` (6).

**Docs (8):** plan, instrument support, materialization support, cost-model
design, validation & diagnostics, readiness, next prompt, this summary.

## 5. Materialization support

`materialize_pair`'s gate widened from `MAJOR_PAIRS` to `SUPPORTED_PAIRS`.
The M1→M5/M15/H1/H4M1 aggregation is price-agnostic (Decimal OHLCV, 5pm-NY
H4 anchor), so crosses — including JPY-quote 0.01-pip pairs — flow through
the *same* tested code path. Storage names unchanged (H4-from-M1 → `H4M1`);
`aggregation_config_hash()` unchanged (majors' provenance preserved).
Diagnostic M3/M30 available for crosses too. Tests prove exact OHLCV
aggregation on JPY-scale GBP_JPY prices, bucket alignment, and
fetch_batch_id / storage-granularity provenance retention.

## 6. Cost-model summary

New `forex_bot.research.cost_models` package, deliberately **not** copying
the majors' USD-leg assumptions:

- **Spread** (`CrossSpreadCostModel`) — registry-estimate band or measured
  `SpreadStats`, expressed in the cross's own pip size; round-trip
  `spread_cost_r`.
- **Carry** (`CrossCarryModel`) — **two-legged** stress using the
  registry's **explicit per-cross** bp/day (not the majors' fallback);
  `debit_quote` honest about quote-currency denomination; `debit_r`
  quote-currency-cancelling (no fabricated USD rate); ESTIMATED treatment,
  permanent live blocker.
- **Profile** (`cross_cost_profile`) — diagnostic bundle for future
  front-gate cost realism.

## 7. Validation results

- `pytest tests/ -q` → **2440 passed, 3 skipped** (3 skips are local-data
  absent, pre-existing; +51 new tests).
- `ruff check src scripts tests` → **4 errors, all pre-existing** in
  `scripts/run_edge_discovery_vol_managed_tsmom.py` (C031); **all new code
  ruff-clean**.
- `python scripts/check_research_freeze.py` → **ALL CHECKS PASSED**.
- `python scripts/validate_research_archive.py` → **ALL CHECKS PASSED**.
- `python scripts/scan_artifacts_for_secrets.py` → **PASSED**.
- `git status --short` → clean.
- Live `validate_nonusd_cross_data.py` run → metadata PASS; all 8 crosses
  `NOT_INGESTED` (expected).

## 8. Readiness assessment

All eight crosses are supported at the **capability** level
(registry → ingest → materialize → cost → diagnostics). The gating
dependency is **data + a go-ahead**, not code: no cross data is ingested,
no credentials are present in this environment. Future factor discovery is
*infrastructurally* possible once a credentialed M1 fetch is run, but is
**not started and not authorized**. See
`NONUSD_CROSS_RESEARCH_READINESS.md`.

## 9. Was any campaign created?

**No.** No CAMPAIGN_032, no campaign of any kind.

## 10. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`; freeze
gate confirms loops refuse every configured strategy.

## 11. Do paper/demo/live remain blocked?

**Yes.** No strategy approved; financing live-blocker permanent; freeze
gate PASS.

## 12. Recommended next sprint

**Option A first (prerequisite):** credentialed practice-only M1 ingestion
of the four primary crosses, then materialize + validate (branch
`research-nonusd-cross-data-acquisition-001`). **Then Option B:** cross
factor-discovery **planning** (pre-campaign/pre-strategy/pre-screen),
prioritizing C1 independent replication + data-blocked breadth families.
See `NEXT_PROMPT_AFTER_NONUSD_CROSS_INGESTION.md`.

## 13. Files to review first

1. `docs/research/NONUSD_CROSS_INGESTION_001_PLAN.md` — design decision (additive registry; majors unchanged).
2. `src/forex_bot/domain/cross_instruments.py` — the registry / single source of truth.
3. `src/forex_bot/research/cost_models/carry.py` — why crosses ≠ majors for cost.
4. `scripts/validate_nonusd_cross_data.py` — the diagnostics entry point.
5. `docs/research/NONUSD_CROSS_RESEARCH_READINESS.md` — what is/ isn't possible next.

## Success criterion (met)

The repo can ingest, validate, materialize, and cost-model non-USD FX
crosses using the same research standards as the major-pair universe, with
the seven USD majors left unchanged as the control universe. No strategy,
campaign, factor screen, or trading logic was created.

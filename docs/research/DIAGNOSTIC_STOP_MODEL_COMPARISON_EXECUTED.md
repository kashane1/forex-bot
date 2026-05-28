# Diagnostic Stop-Model Comparison (Execution Attempt) — STILL BLOCKED

**Date:** 2026-05-28 · **Sprint:** `infra-lifecycle-feature-capture-and-mfe-mae-execution-001`
**Status:** **NOT EXECUTED — gated on per-bar MFE/MAE, which is BLOCKED_LOCAL_DATA.**

> **Not an optimization sprint.** No "best" stop is selected or promoted. Any
> comparison, when produced, is **diagnostic sensitivity** only — never a verdict,
> never an edge, never a tradable recommendation. No C022 metric is rewritten and
> no C024 is created.

## Why still blocked

This phase runs **only if Phase 1 produced real MFE/MAE** (per the sprint plan).
Phase 1 re-attempted the reconstruction this sprint and again hit
**BLOCKED_LOCAL_DATA**: no reachable materialized M15 research store
(`FOREX_BOT_RESEARCH_DATABASE_URL` unset; local Postgres requires a password;
`data/bot.sqlite3` empty; no local candle corpora). See
`LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_PLAN.md` §"Local data
readiness" and `research/trade_lifecycle_diagnostics/c022_mfe_mae_summary.json`
(status `BLOCKED_LOCAL_DATA`).

Without the realized per-bar path, every stop family below is a counterfactual we
**cannot evaluate without fabricating outcomes** — which is forbidden.

## Stop families (designed, ready to execute once MFE/MAE exists)

| family | description | additional input still needed |
|---|---|---|
| baseline | C022 2.0× M15 ATR (−1R by construction) | none (it is the realized outcome) |
| ATR sensitivity | 1.5× / 2.0× / 2.5× / 3.0× ATR | **ATR-at-entry** (now capturable via the Phase 3/4 schema; absent in historical C022) |
| structure proxy | M15 swing low/high; H1 pullback low/high | swing detection + **H1 pullback geometry** (capturable going forward) |
| time-to-invalidation | no +0.25R / +0.5R within N bars | first-threshold bar index — **available** from `mfe_mae` once candles exist |
| reclaim failure | close back through reclaim level | **M15 reclaim level** (capturable going forward) |

The `time-to-invalidation` and `baseline` families need only the per-bar path
(Phase 1 unblocked). The ATR/structure/reclaim families additionally need the
signal-geometry fields the Phase 3 `lifecycle_features` schema and the Phase 4
`--emit-lifecycle-features` export now make capturable in **future** runs (they
cannot be recovered from the historical C022 CSVs).

## What changed this sprint that moves this forward

- Phase 3 added the capture schema (`atr_at_entry`, `h1_pullback_depth_atr`,
  `m15_reclaim_distance_atr`, MFE/MAE, threshold flags).
- Phase 4 wired an opt-in exporter so a future instrumented C022-style rerun emits
  those fields. Combined with a reachable M15 store, that closes every input gap
  for the full comparison.

## To execute later

1. Unblock local data (see plan §"exact command"): populate/point to a
   materialized M15 store and run Phase 1 reconstruction.
2. For ATR/structure/reclaim families, rerun a C022-style diagnostic export with
   `--emit-lifecycle-features` so ATR-at-entry and pullback/reclaim geometry exist.
3. Emit `research/trade_lifecycle_diagnostics/diagnostic_stop_model_comparison.json`
   and update this doc with results — each row labeled **diagnostic sensitivity**.

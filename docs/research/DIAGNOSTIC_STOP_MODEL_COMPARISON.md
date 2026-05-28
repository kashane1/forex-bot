# Diagnostic Stop-Model Comparison — DEFERRED (BLOCKED_LOCAL_DATA)

**Date:** 2026-05-28 · **Sprint:** `infra-trade-lifecycle-feature-capture-and-stop-diagnostics-001`
**Status:** **DEFERRED — blocked on per-bar MFE/MAE reconstruction.**

> **This is not an optimization sprint.** No "best" stop is selected or promoted.
> Any comparison produced here, now or later, is a **diagnostic sensitivity**
> analysis only — never a campaign verdict, never an edge claim, never a tuning
> result. No existing campaign metric is rewritten.

## Why deferred

The stop-model comparison requires the **realized per-bar path** of each trade
(to ask "would a different stop have survived / triggered, and what excursion
preceded it"). That path is produced by per-bar MFE/MAE reconstruction, which is
**BLOCKED_LOCAL_DATA** in this checkout — there is no reachable materialized M15
research store (see [`MFE_MAE_RECONSTRUCTION_FEASIBILITY.md`](MFE_MAE_RECONSTRUCTION_FEASIBILITY.md)
and `research/trade_lifecycle_diagnostics/c022_mfe_mae_summary.json`).

Producing stop-model numbers without that path would require fabricating
counterfactual outcomes — explicitly forbidden. So this phase records the
**design** and the **missing inputs**, and stops.

## Stop families designed (to run once MFE/MAE is available)

| family | description | extra input needed beyond MFE/MAE |
|---|---|---|
| **baseline** | C022 2.0× M15 ATR (frozen; −1R by construction) | none — already the realized outcome |
| **ATR sensitivity** | re-place stop at 1.5× / 2.0× / 2.5× / 3.0× ATR | **per-trade ATR at entry** (not currently exported) |
| **structure proxy** | M15 swing low/high; H1 pullback low/high if reconstructable | swing detection; **H1 pullback geometry not exported** → likely partial |
| **time-to-invalidation** | early-exit if no +0.25R/+0.5R within N bars | first-threshold bar index — **available** from `mfe_mae` once candles exist |
| **reclaim failure** | invalidate on close back through reclaim level | per-bar closes + **recorded reclaim level (not exported)** |

## Blocking inputs missing in current artifacts

1. **Per-bar M15 candles** for the trade windows (the path itself).
2. **Per-trade ATR at entry** — needed to express ATR-multiple stop variants.
3. **H1 pullback geometry** (pullback low/high) — needed for the structure stop.
4. **M15 reclaim level** — needed for the reclaim-failure model.

Items 2–4 are *signal-feature capture gaps* — exactly what the
[`TRADE_LIFECYCLE_IMPROVEMENT_ROADMAP.md`](TRADE_LIFECYCLE_IMPROVEMENT_ROADMAP.md)
requires future campaigns to record. Item 1 is data-availability only.

## How to complete this phase later

1. Make a populated materialized M15 store reachable and run Phase 5
   (`scripts/reconstruct_mfe_mae_for_campaign_trades.py`) — gives the realized
   path, `time-to-invalidation`, and the `baseline`.
2. For ATR-multiple and structure variants, first close the capture gaps
   (export ATR-at-entry and pullback/reclaim geometry in future campaign trade
   writers — see roadmap), since they cannot be recovered from current C022 CSVs.
3. Emit `diagnostic_stop_model_comparison.json` + this doc with results, each row
   explicitly labeled **diagnostic sensitivity**.

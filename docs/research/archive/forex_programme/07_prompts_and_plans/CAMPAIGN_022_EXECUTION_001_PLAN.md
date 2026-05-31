# CAMPAIGN_022 — Execution Sprint 001 Plan

**Date:** 2026-05-27
**Branch:** `research-campaign-022-h4-h1-pullback-resolution-execution-001`
**Status:** EXECUTION PLAN — parameters frozen at scaffold; this is NOT a tuning sprint

## Identity

| field | value |
|---|---|
| `campaign_id` | CAMPAIGN_022 |
| `strategy_name` | `h4_h1_pullback_resolution_entry` |
| `version` | `0.1.0-c022` |
| `promotion_eligible` | false |

## Frozen hypothesis (no changes permitted)

H4 sets directional bias; H1 must be in a **counter-trend pullback that holds**; M15 fires
when that pullback **resolves back** into the H4 direction. H1 is **not** required to agree
with H4. Top timeframe is **H4** — no D1 / D1AGG layer.

## Frozen execution rules

- Execution timeframe: **M15** (completed bars only), materialized `m1_derived`.
- Context: **H4 + H1** only, materialized `m1_derived`, joined via `align_last_completed`.
- **No D1 access. No D1AGG. No M5 refinement. No additional filters.**
- H4 bias: votes (`price>EMA50`, `EMA20>EMA50`, `EMA50 slope(3)>0`); bias if **≥2/3 AND H4 ADX(14) ≥ 20**.
- H1 holding pullback: (`low`≤EMA20 touch OR RSI(14) reset <45 long / >55 short) AND latest H1 close holds EMA50.
- M15 trigger: pullback touch + EMA20 reclaim; **M15 ADX(14) floor = 18**; optional `min_atr_pips` (empty).
- Stop: **2.0 × M15 ATR(14)** (prior bar). Time stop: **32** M15 bars. No TP, no trailing.
- Fill timing: **next_bar_open**; execution realism **conservative**; evidence **approval_bound**.

## Data provenance

| layer | source |
|---|---|
| M15 execution | `m1_materialized` (Postgres `market_data.candles`) |
| H1 context | `m1_materialized` |
| H4 context | `m1_materialized` (storage granularity `H4M1`) |
| D1 / D1AGG | **not loaded, not accessed** |

Local research Postgres only (`localhost`/`forex_bot`); prod DBs are refused by
`validate_research_database_url`. No cloud execution.

## Frozen splits (fixed pre-results; never changed after seeing any metric)

Materialized M1-derived coverage runs 2021-05-26 → 2026-05-26 for all seven majors.

| split | from | to |
|---|---|---|
| train | 2021-06-01 | 2023-12-31 |
| validation | 2024-01-01 | 2025-06-30 |
| test (lockbox) | 2025-07-01 | 2026-05-20 |

## Gate rules (frozen; mirror C020/C021 discipline)

**Train gate (binding first):**
- train expectancy ≥ 0 (`next_bar_open`). If < 0 → **REJECT**; no validation rescue; no test.

**Validation gates (all required to open lockbox):**
- validation expectancy > 0
- validation profit factor ≥ 1.05
- validation trade count ≥ **150** (documented lower acceptable, recorded honestly)
- ≥ **4 of 7** validation pairs positive
- 2× cost-stress validation expectancy ≥ 0
- beat C011 deduped null by **+0.010R** (null = −0.0029154R → threshold ≈ −0.0019R… i.e. val_exp > null + 0.010)
- **Backtrader parity PASS** required before the test lockbox opens

**Test (only if all above pass, run once, no retune before/after):**
- test expectancy ≥ 0; test PF ≥ 1.0; test trades ≥ 20
- Max status on success: RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED — **never approval**.

## No-retuning policy (hard)

One frozen parameter set in `configs/campaign_022_h4_h1_pullback_resolution.yaml`. No
sweeps. No gate softening after results. No validation rescue if train fails. No merging of
the C023 ADX-22 sibling threshold into C022.

## No-lookahead guarantees

- All H4/H1 features read at the `align_last_completed` bar; slope/pullback windows bounded
  to `time ≤ aligned_feature_time` (the C021 tail-slope leak is fixed and regression-tested).
- Context frames passed as full-range frames into `strategy_config`; temporal correctness is
  enforced solely by `align_last_completed` per decision bar.
- Per-pair data preflight asserts `lookahead_violations == 0` before any backtest.
- Each emitted signal records `htf_feature_times` (h4, h1); `validate_signal_provenance` must be empty.

## Comparison targets

- **C011 deduped null:** aggregate expectancy −0.0029154R (`research/null_baselines/campaign_011_deduped_null_baseline.json`). C022 validation must beat by +0.010R.
- **C020 (`multi_timeframe_confluence_pullback`):** REJECT — train −0.035R, validation +0.053R (all-green H4 confluence). Behavioral/structural comparison + expectancy delta.
- **C021 (`lower_timeframe_mtf_confluence_entry`):** scaffold only — **no executed evidence exists**. Comparison is structural/behavioral (all-green M15 stack vs C022 pullback-resolution); no numeric head-to-head is available, and none will be fabricated.

## Expected artifacts

Under `research/campaign_022/`:
- `train_metrics.json`, `validation_metrics.json`, `cost_stress_2x.json`
- `gate_result.json`, `hold_diagnostics.json`, `comparison_to_c011_null.json`
- `metrics_summary.json`, `run_manifest.json`, `evidence_status.json`
- per-pair/per-split trades + equity + metrics under `backtests/CAMPAIGN_022_h4_h1_pullback_resolution/`
- behavior diagnostics JSON (Phase 3), parity artifacts (Phase 4)

Docs: TRAIN_VALIDATION_RESULT, BEHAVIOR_DIAGNOSTICS, BACKTRADER_PARITY_RESULT,
GATE_DECISION, FINAL_INTERPRETATION, EXECUTION_001_SUMMARY.

## Validation commands

```
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```

## Safety invariants (must hold at every phase)

- `configs/approved_strategies.yaml` remains `approved: []`.
- paper/demo/live blocked; `trading_enabled: false`, `allow_order_submission: false`.
- no broker/executor modifications; no OANDA mutation/order APIs; no live trading; no cloud.
- no `.env` or DB artifacts committed; no secrets in artifacts.

## Phase 0 verification results (this commit)

- Branch created from frozen scaffold commit; ADX gate H4=20 / M15 floor=18 confirmed in YAML.
- `approved_strategies.yaml` = `approved: []`; freeze gate ALL CHECKS PASSED; secret scan PASSED.
- Materialized M1-derived data present: M15 790,438 / H1 180,455 / H4M1 33,483 rows across 7 majors, 2021-05-26 → 2026-05-26.
- No broker/executor files modified by this sprint.

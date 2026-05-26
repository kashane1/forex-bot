# CAMPAIGN_015 Deduped Rerun Result

**Branch:** `infra-canonical-candle-dedup-and-campaign015-rerun-001`
**Date:** 2026-05-26
**Input classification:** `DEDUPED_INPUT` (`keep_last`)
**Verdict:** `REJECT` — **NOT APPROVED**

> Prior contaminated bespoke evidence is **SUPERSEDED BY DEDUP RERUN**.
> See `CAMPAIGN_015_DUPLICATE_CANDLE_CONTAMINATION_MEMO.md`.

## Dedupe summary

| metric | value |
|---|---:|
| duplicate rows detected (preflight total) | 64,509 |
| duplicate rows dropped (preflight total) | 64,509 |
| dedupe policy | `keep_last` |
| fold-1 AUD_USD bars (before → after) | 2328 → 1166 |

## Deduped aggregate metrics (base / 2x cost)

| metric | contaminated (stale) | deduped (current) |
|---|---:|---:|
| aggregate exp_r | +0.2300 | **-0.0101** |
| 2x-cost exp_r | +0.1909 | **-0.0283** |
| total trades | 164 | **375** |
| fold pass count | 0 / 8 | **2 / 8** |
| pairs positive | — | **3 / 7** |
| profit factor (base) | — | 2.85 |
| runner verdict | REJECT | **REJECT** |

## Gate vector (base)

| gate | result |
|---|---|
| fold_pass_rate ≥ 5/8 | FAIL (2/8) |
| expectancy_r ≥ 0.03 | FAIL (-0.0101) |
| trade_count ≥ 200 | **PASS** (375) |
| pairs_positive ≥ 4/7 | FAIL (3/7) |
| profit_factor ≥ 1.05 | PASS |

## Per-fold trade counts (base)

`[38, 52, 55, 50, 47, 38, 48, 47]` — total 375.

## Artifacts

- `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/gate_result.json`
- `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/results.json`
- `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/preflight.json`

## Approval status

`configs/approved_strategies.yaml` remains `approved: []`. No paper / demo / live enablement.

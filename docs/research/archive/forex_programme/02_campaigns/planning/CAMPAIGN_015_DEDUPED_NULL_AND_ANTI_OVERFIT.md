# CAMPAIGN_015 Deduped Null and Anti-Overfit Diagnostics

**Branch:** `infra-canonical-candle-dedup-and-campaign015-rerun-001`
**Date:** 2026-05-26
**Anti-overfit label:** **`WITHIN_NULL`**

> Prior `ROBUST_ABOVE_NULL` label from contaminated bespoke data is
> **SUPERSEDED BY DEDUP RERUN**. Null comparison uses deduped
> CAMPAIGN_011 rerun (`backtests/CAMPAIGN_011_random_entry_anchor_deduped/`).

## Inputs

| lane | artifact |
|---|---|
| CAMPAIGN_015 deduped | `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/fold_detail.json` |
| CAMPAIGN_011 null deduped | `backtests/CAMPAIGN_011_random_entry_anchor_deduped/walk_forward/fold_detail.json` |

## Headline comparison

| metric | CAMPAIGN_015 deduped | CAMPAIGN_011 null deduped |
|---|---:|---:|
| aggregate exp_r | -0.0101 | -0.0029 |
| total trades | 375 | 1180 |
| gap mean R | -0.0029 | — |

## Anti-overfit gates

| gate | pass |
|---|---|
| loo_min_mean_gap ≥ 0.05 | FAIL |
| per_fold_t_stat ≥ 2.0 | FAIL |
| median_per_fold_expectancy ≥ 0 | FAIL |
| trade_level_cumulative_r > 0 | FAIL |
| pair_concentration ≤ 70% | PASS |
| fold_concentration ≤ 60% | PASS |
| cost_dominance ≤ 50% | PASS |

## Classification

**`WITHIN_NULL`** — aggregate floor not met; campaign edge is not
statistically distinguishable from the matched random-entry null on
deduped data. This **does not approve** the strategy.

Prior contaminated label `ROBUST_ABOVE_NULL` is invalidated.

## Artifacts

- `research/campaign_015/diagnostics/null_and_anti_overfit_deduped.json`
- `research/campaign_015/diagnostics/null_and_anti_overfit_deduped.md`

# CAMPAIGN_016 Weekly Cross-Sectional Momentum — Sprint Summary

**Date:** 2026-05-26 · **Branch:** `research-weekly-cross-sectional-momentum-001`
**Verdict:** **REJECT** · Anti-overfit: **WITHIN_NULL** · Backtrader: **BLOCKED** (non-blocking)

## Implementation

Strategy `weekly_cross_sectional_momentum_low_turnover 0.1.0-c016` implemented with:

- Synthetic weekly aggregation from deduped H4 (`src/forex_bot/features/weekly_momentum.py`)
- Cross-pair ranking strategy module
- Walk-forward runner with deduped preflight and base/2× cost lanes
- Null / anti-overfit diagnostics vs deduped CAMPAIGN_011 null

## Frozen settings (binding)

| parameter | value |
|---|---|
| fast / slow momentum weeks | 4 / 12 |
| blend | 0.5 / 0.5 |
| vol lookback weeks | 12 |
| rebalance | first H4 bar each Monday UTC week |
| selection | long rank-1, short rank-7 |
| stop | 2.5 × ATR(14) H4 |
| max hold | 42 H4 bars |
| risk per trade | 0.50% |

## Bespoke metrics

| metric | base | 2× |
|---|---:|---:|
| exp_r | **−0.0633** | **−0.0719** |
| PF | 0.98 | 0.92 |
| trades | **137** | 137 |
| folds pass | **3/8** | 3/8 |
| pairs positive | **4/7** | — |

Deduped input: 138,522 duplicate H4 rows dropped (`keep_last`).

## Null / anti-overfit

Gap vs null: **−0.0604 R**. Label **WITHIN_NULL** (aggregate floor not met; not ROBUST).

## Approval status

**No strategy approved.** Paper / demo / live **remain blocked**.

## Recommended next step

Return to **new candidate discovery** on deduped canonical data — do not retune CAMPAIGN_016 parameters. Consider retiring weekly cross-sectional momentum as a family unless a structurally different hypothesis is precommitted.

## Files to review first

1. `docs/research/CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_PRECOMMIT.md`
2. `backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/walk_forward/gate_result.json`
3. `docs/research/CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_INTERPRETATION.md`
4. `research/campaign_016/diagnostics/null_and_anti_overfit.json`

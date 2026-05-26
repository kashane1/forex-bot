# CAMPAIGN_017 Walk-Forward Result

**Date:** 2026-05-26 · **Branch:** `research-weekly-volatility-contraction-breakout-001`
**Verdict:** **REJECT** · `strategy_evidence: false`

## Summary

| metric | base | 2× cost |
|---|---:|---:|
| aggregate expectancy R | **−0.0227** | **−0.0283** |
| profit factor | 0.77 | 0.72 |
| total trades | **230** | 230 |
| folds passing | **3 / 8** | 3 / 8 |
| pairs positive | **4 / 7** | — |
| single-pair dominance (gross +R) | 38.4% | — |

**Deduped input:** `DEDUPED_INPUT`, policy `keep_last`, **71,733** duplicate rows dropped in preflight probe.

## Gate failures (base)

- `expectancy_r_min` — need ≥ 0.03 R; got −0.0227
- `profit_factor_min` — need ≥ 1.05; got 0.77
- `fold_pass_rate_ge_5_of_8` — need ≥ 5; got 3

## Gate passes (base)

- trade count 120–350 (230)
- pairs positive ≥ 4/7
- single-pair dominance ≤ 60%

## 2× cost

Failed `expectancy_r_min` (≥ 0.0) and `profit_factor_min` (≥ 1.0).

## Artifacts

- `backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/walk_forward/gate_result.json`
- `backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/walk_forward/fold_detail.json`
- `backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/walk_forward/preflight.json`

## Approval

**No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`.

# CAMPAIGN_020 — Gate Decision

**Date:** 2026-05-27  
**Verdict:** **REJECT**  
**Screening pass:** **false**  
**Test lockbox:** **not opened**

## Failed gates

1. **train_expectancy_gte_zero** — aggregate train expectancy **−0.035 R** under `next_bar_open`.
2. **backtrader_parity_pass** — no C020 Backtrader lane executed in this sprint (parity prerequisite unmet).

## Passed checks (did not override train failure)

- validation_expectancy_gt_zero (+0.053 R)
- validation_pf_gte_1_05 (1.1313)
- validation_trade_count_gte_80 (204)
- validation_pairs_positive_gte_2 (5 pairs)
- validation_stress_2x_expectancy_gte_zero (+0.049 R)
- beat_null_vs_c011 (threshold +0.0071 R)

## Decision

Train failure triggers **immediate REJECT** per execution prompt: no validation rescue, no parameter retuning, no test lockbox.

Maximum status remains **research-only / not approved**. `configs/approved_strategies.yaml` stays `approved: []`.

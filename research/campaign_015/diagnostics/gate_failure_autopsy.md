# CAMPAIGN_015 — Gate-Failure Autopsy

**Strategy:** `failed_breakout_reversal 0.1.0-c015`
**Config hash:** `17ddfd7eb87d93c502f148642c8ee883c66cb72bfa8ca72f981624a0dcfdd93c`
**Runner verdict:** **REJECT**
**Approval status:** **NOT_APPROVED** — `configs/approved_strategies.yaml` remains `approved: []`.

> Diagnostic only. Counterfactual fold-pass figures are NON-GATING; the runner verdict remains REJECT.

## base cost

Aggregate metrics:
- `aggregate_expectancy_r` = +0.2300
- `aggregate_return_pct` = 17.2600
- `profit_factor` = 107.5543
- `total_trades` = 164
- `fold_pass_rate` = 0.0000
- `folds_passing` = 0
- `pairs_positive_count` = 6
- `single_pair_dominance_pct` = 30.2126
- `median_per_fold_expectancy_r` = +0.2588
- `trade_level_cumulative_r` = +37.7265
- `expectancy_min_applied` = +0.0300
- `profit_factor_min_applied` = 1.0500

**Aggregate gates failed:** ['fold_pass_rate_ge_5_of_8', 'trade_count_min_200']
**Aggregate gates passed:** ['expectancy_r_min', 'fold_count_ge_8', 'pairs_positive_ge_4_of_7', 'profit_factor_min', 'single_pair_dominance_le_70pct', 'trade_count_max_800']

Per-fold:

| fold | trades | exp_R | pairs+ | spd% | trade_count_ge_30 | expectancy_r_ge_0 | pairs_positive_ge_3 | spd_le_60pct | passes | CF-pass (no trade-count) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 18 | -0.205 | 2 | 32.8 | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| 1 | 26 | +0.059 | 5 | 77.4 | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| 2 | 26 | +0.314 | 4 | 31.5 | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| 3 | 28 | +0.429 | 5 | 32.5 | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| 4 | 24 | +0.309 | 4 | 37.3 | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| 5 | 14 | +0.209 | 4 | 55.6 | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| 6 | 14 | +0.568 | 4 | 40.3 | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| 7 | 14 | +0.102 | 1 | 49.5 | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ |

**Per-fold gate failure counts:** {'expectancy_r_ge_0': 1, 'pairs_positive_ge_3': 2, 'single_pair_dominance_le_60pct': 1, 'trade_count_ge_30': 8}
**Folds passing (actual / gating):** 0 / 8
**Folds passing (counterfactual, NON-GATING, drop `trade_count_ge_30`):** 5 / 8
**Folds passing (counterfactual, NON-GATING, drop `trade_count_ge_30` AND `pairs_positive_ge_3`):** 6 / 8

Pair-fold cell trade-count distribution:
- `0_trades` = 9
- `1_trade` = 8
- `2_to_3_trades` = 21
- `4_to_9_trades` = 17
- `10_or_more_trades` = 1

## 2xcost cost

Aggregate metrics:
- `aggregate_expectancy_r` = +0.1909
- `aggregate_return_pct` = 15.9713
- `profit_factor` = 39.6926
- `total_trades` = 164
- `fold_pass_rate` = 0.0000
- `folds_passing` = 0
- `pairs_positive_count` = None
- `single_pair_dominance_pct` = None
- `median_per_fold_expectancy_r` = None
- `trade_level_cumulative_r` = None
- `expectancy_min_applied` = +0.0000
- `profit_factor_min_applied` = 1.0000

**Aggregate gates failed:** ['fold_pass_rate_ge_5_of_8', 'trade_count_min_200']
**Aggregate gates passed:** ['expectancy_r_min', 'fold_count_ge_8', 'pairs_positive_ge_4_of_7', 'profit_factor_min', 'single_pair_dominance_le_70pct', 'trade_count_max_800']

Per-fold:

| fold | trades | exp_R | pairs+ | spd% | trade_count_ge_30 | expectancy_r_ge_0 | pairs_positive_ge_3 | spd_le_60pct | passes | CF-pass (no trade-count) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 18 | -0.219 | 2 | 31.2 | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| 1 | 26 | +0.046 | 4 | 77.0 | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| 2 | 26 | +0.279 | 4 | 31.9 | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| 3 | 28 | +0.366 | 5 | 32.6 | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| 4 | 24 | +0.265 | 4 | 37.6 | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| 5 | 14 | +0.167 | 3 | 54.5 | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| 6 | 14 | +0.501 | 3 | 40.0 | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| 7 | 14 | +0.060 | 1 | 47.6 | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ |

**Per-fold gate failure counts:** {'expectancy_r_ge_0': 1, 'pairs_positive_ge_3': 2, 'single_pair_dominance_le_60pct': 1, 'trade_count_ge_30': 8}
**Folds passing (actual / gating):** 0 / 8
**Folds passing (counterfactual, NON-GATING, drop `trade_count_ge_30`):** 5 / 8
**Folds passing (counterfactual, NON-GATING, drop `trade_count_ge_30` AND `pairs_positive_ge_3`):** 6 / 8

Pair-fold cell trade-count distribution:
- `0_trades` = 9
- `1_trade` = 8
- `2_to_3_trades` = 21
- `4_to_9_trades` = 17
- `10_or_more_trades` = 1

## Summary

- Primary failing aggregate gates (base): `['fold_pass_rate_ge_5_of_8', 'trade_count_min_200']`
- Primary failing aggregate gates (2xcost): `['fold_pass_rate_ge_5_of_8', 'trade_count_min_200']`
- All folds fail in both cost regimes: True
- Every fold fails `trade_count_ge_30` (base): True
- Every fold fails `trade_count_ge_30` (2xcost): True
- Any fold failed expectancy_r_ge_0 despite positive aggregate (base): True
- Any fold failed pairs_positive_ge_3 (base): True
- Any fold failed single_pair_dominance_le_60pct (base): True

Counterfactual fold-pass counts shown below are non-gating and diagnostic only. They do NOT relax any pre-committed gate, and the runner verdict remains REJECT regardless.

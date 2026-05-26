# Post-Dedup Campaign Metric Matrix

**Generated:** 2026-05-26T17:26:25.629691+00:00

> Null centre exp_r = **-0.002915** · fold std = **0.0479**

> Descriptive only — does not approve any strategy.

## Headline comparison

| campaign | strategy | verdict | base exp_r | 2x exp_r | gap vs null | trades | fold pass | +pairs | PF | anti-overfit | Backtrader |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| CAMPAIGN_011 | random_entry_anchor | REJECT | -0.0029 | n/a | +0.0000 | 1180 | 0/8 | 3 | 0.894 | n/a | n/a |
| CAMPAIGN_015 | failed_breakout_reversal | REJECT | -0.0101 | -0.0283 | -0.0072 | 375 | 2/8 | 3 | 2.848 | WITHIN_NULL | TOLERABLE_DRIFT |
| CAMPAIGN_016 | weekly_cross_sectional_momentum_low_turnover | REJECT | -0.0633 | -0.0719 | -0.0604 | 137 | 3/8 | 4 | 0.982 | WITHIN_NULL | BLOCKED, non-decision-blocking |
| CAMPAIGN_017 | weekly_volatility_contraction_breakout | REJECT | -0.0227 | -0.0283 | -0.0198 | 230 | 3/8 | 4 | 0.770 | WITHIN_NULL | BLOCKED, non-decision-blocking |

## Per-campaign pair expectancy (base cost)

### CAMPAIGN_011 (null baseline)

| pair | trades | exp_r | folds + |
|---|---:|---:|---:|
| EUR_USD | 121 | -0.0407 | n/a |
| GBP_USD | 196 | 0.0842 | n/a |
| USD_JPY | 174 | 0.0000 | n/a |
| AUD_USD | 191 | -0.0354 | n/a |
| USD_CAD | 182 | -0.0102 | n/a |
| USD_CHF | 177 | 0.0220 | n/a |
| NZD_USD | 139 | -0.0741 | n/a |

### CAMPAIGN_015 — failed_breakout_reversal

| pair | trades | exp_r | folds + |
|---|---:|---:|---:|
| AUD_USD | 88 | 0.0323 | 6 |
| EUR_USD | 44 | -0.2439 | 2 |
| GBP_USD | 82 | 0.3248 | 6 |
| NZD_USD | 6 | -0.4514 | 0 |
| USD_CAD | 63 | -0.1134 | 4 |
| USD_CHF | 49 | -0.2626 | 3 |
| USD_JPY | 43 | 0.0044 | 5 |

### CAMPAIGN_016 — weekly_cross_sectional_momentum_low_turnover

| pair | trades | exp_r | folds + |
|---|---:|---:|---:|
| AUD_USD | 10 | 0.6532 | 6 |
| EUR_USD | 5 | 1.2242 | 3 |
| GBP_USD | 15 | -1.0000 | 0 |
| NZD_USD | 5 | 2.2406 | 5 |
| USD_CAD | 37 | -0.2639 | 2 |
| USD_CHF | 35 | -0.2233 | 4 |
| USD_JPY | 30 | 0.0019 | 5 |

### CAMPAIGN_017 — weekly_volatility_contraction_breakout

| pair | trades | exp_r | folds + |
|---|---:|---:|---:|
| AUD_USD | 40 | -0.2745 | 0 |
| EUR_USD | 28 | 0.0152 | 4 |
| GBP_USD | 35 | 0.0853 | 4 |
| NZD_USD | 31 | -0.1567 | 2 |
| USD_CAD | 34 | -0.2135 | 2 |
| USD_CHF | 37 | 0.3905 | 6 |
| USD_JPY | 25 | 0.0010 | 6 |


## Per-campaign fold expectancy (base cost)

### CAMPAIGN_011

| fold | window | trades | exp_r | pass |
|---:|---|---:|---:|:---:|
| 0 | 2021-12-21..2022-06-18 | 143 | -0.1039 | ✗ |
| 1 | 2022-06-19..2022-12-15 | 150 | -0.0239 | ✗ |
| 2 | 2022-12-16..2023-06-13 | 155 | 0.0391 | ✗ |
| 3 | 2023-06-14..2023-12-10 | 150 | -0.0060 | ✗ |
| 4 | 2023-12-11..2024-06-07 | 162 | 0.0147 | ✗ |
| 5 | 2024-06-08..2024-12-04 | 154 | -0.0028 | ✗ |
| 6 | 2024-12-05..2025-06-02 | 128 | 0.0541 | ✗ |
| 7 | 2025-06-03..2025-11-29 | 138 | 0.0068 | ✗ |

### CAMPAIGN_015

| fold | window | trades | exp_r | pass |
|---:|---|---:|---:|:---:|
| 0 | 2021-12-21..2022-06-18 | 38 | -0.0913 | ✗ |
| 1 | 2022-06-19..2022-12-15 | 52 | -0.0161 | ✗ |
| 2 | 2022-12-16..2023-06-13 | 55 | 0.0263 | ✓ |
| 3 | 2023-06-14..2023-12-10 | 50 | -0.1246 | ✗ |
| 4 | 2023-12-11..2024-06-07 | 47 | -0.0984 | ✗ |
| 5 | 2024-06-08..2024-12-04 | 38 | 0.2580 | ✓ |
| 6 | 2024-12-05..2025-06-02 | 48 | 0.0823 | ✗ |
| 7 | 2025-06-03..2025-11-29 | 47 | -0.0813 | ✗ |

### CAMPAIGN_016

| fold | window | trades | exp_r | pass |
|---:|---|---:|---:|:---:|
| 0 | 2021-12-21..2022-06-18 | 22 | -0.1183 | ✗ |
| 1 | 2022-06-19..2022-12-15 | 19 | -0.0544 | ✗ |
| 2 | 2022-12-16..2023-06-13 | 18 | 0.1596 | ✓ |
| 3 | 2023-06-14..2023-12-10 | 15 | 0.3735 | ✓ |
| 4 | 2023-12-11..2024-06-07 | 21 | 0.2612 | ✓ |
| 5 | 2024-06-08..2024-12-04 | 14 | -0.4051 | ✗ |
| 6 | 2024-12-05..2025-06-02 | 14 | -0.4908 | ✗ |
| 7 | 2025-06-03..2025-11-29 | 14 | -0.4608 | ✗ |

### CAMPAIGN_017

| fold | window | trades | exp_r | pass |
|---:|---|---:|---:|:---:|
| 0 | 2021-12-21..2022-06-18 | 20 | 0.1548 | ✓ |
| 1 | 2022-06-19..2022-12-15 | 23 | -0.0256 | ✗ |
| 2 | 2022-12-16..2023-06-13 | 38 | -0.1264 | ✗ |
| 3 | 2023-06-14..2023-12-10 | 32 | -0.0079 | ✗ |
| 4 | 2023-12-11..2024-06-07 | 37 | -0.0604 | ✗ |
| 5 | 2024-06-08..2024-12-04 | 24 | 0.2189 | ✓ |
| 6 | 2024-12-05..2025-06-02 | 19 | 0.3875 | ✓ |
| 7 | 2025-06-03..2025-11-29 | 37 | -0.3527 | ✗ |


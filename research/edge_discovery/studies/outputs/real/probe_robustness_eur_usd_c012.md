# Single-pair probe (Phase 2 robustness) — probe_robustness_eur_usd_c012

> Exploratory lab output. Not a strategy verdict; does not approve,
> promote, or change any campaign status. CAMPAIGN_012 remains REJECT;
> CAMPAIGN_011 remains the null model.

## Classification

- **Result:** `SELECTED_CELL_ARTIFACT`
- Material-gap floor: `+0.05` R
- Failed criteria:
  - `LOO_drops_below_floor`
  - `at_most_4_of_8_folds_positive`
  - `median_per_fold_expectancy_negative`
- Robust criteria met:
  - `at_least_5_folds_positive_gap`
  - `2x_cost_stress_above_floor`
  - `top_fold_share_at_or_below_40pct`

### Headline numbers

- n folds positive (candidate expectancy R > 0): **3 / 8**
- median per-fold candidate expectancy R: **`-0.0189`**
- mean gap R: **`+0.0950`**, SE: `0.0718`, t-stat: `1.323`
- LOO mean gap range: `[+0.0482, +0.1325]`; 0 of 8 LOO means below zero
- top fold share of |sum-of-absolute fold R|: **`0.342`**
- top fold signed share of total R: `+2.112`
- 2× cost-stress mean gap R: **`+0.0661`** (5 / 8 folds positive)
- neighbor pairs above floor (C012 vs C011, other 6 pairs): **1 / 7**
- neighbor candidates above floor on EUR_USD (C010/12/13/14 vs C011): **1 / 4**

## Leave-one-fold-out resamples

| dropped fold | LOO mean gap R |
|---:|---:|
| 0 | `+0.0977` |
| 1 | `+0.1325` |
| 2 | `+0.1267` |
| 3 | `+0.1118` |
| 4 | `+0.0919` |
| 5 | `+0.0644` |
| 6 | `+0.0869` |
| 7 | `+0.0482` |

## 2× cost-stress

- assumed EUR_USD stop pips: `50.0`
- average per-trade extra cost (R units): `0.02883`
- candidate stress mean R: `+0.0011`
- stress mean gap R: **`+0.0661`** (5 / 8 folds positive gap)
- stress median gap R: `+0.0681`

## Neighboring pairs (same candidate / same null)

| pair | C012 mean R | C012 median R | C011 null R | gap R | above floor? | n folds positive | total trades |
|---|---:|---:|---:|---:|:---:|---:|---:|
| EUR_USD | +0.0300 | -0.0189 | -0.0650 | **+0.0950** | ✓ | 3 | 479 |
| GBP_USD | -0.0487 | -0.0404 | +0.0756 | **-0.1243** |   | 0 | 555 |
| USD_JPY | +0.0004 | +0.0004 | +0.0000 | **+0.0004** |   | 6 | 624 |
| AUD_USD | -0.0928 | -0.1327 | -0.0415 | **-0.0514** |   | 1 | 551 |
| USD_CAD | -0.0633 | -0.0430 | -0.0069 | **-0.0564** |   | 1 | 584 |
| USD_CHF | -0.0500 | -0.0011 | +0.0269 | **-0.0769** |   | 4 | 542 |
| NZD_USD | -0.1097 | -0.1255 | -0.0986 | **-0.0111** |   | 1 | 391 |

## Neighboring candidates (same EUR_USD pair / same null)

| candidate | mean R | median R | null R | gap R | above floor? | n folds positive | total trades |
|---|---:|---:|---:|---:|:---:|---:|---:|
| CAMPAIGN_012_regime_switcher_atr_percentile | +0.0300 | -0.0189 | -0.0650 | **+0.0950** | ✓ | 3 | 479 |
| CAMPAIGN_010_session_breakout | -0.0685 | -0.0560 | -0.0650 | **-0.0036** |   | 2 | 310 |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | -0.0290 | -0.0057 | -0.0650 | **+0.0360** |   | 0 | 1412 |
| CAMPAIGN_014_calendar_event_window_anomaly | -0.2148 | -0.3081 | -0.0650 | **-0.1498** |   | 3 | 100 |

## Notes

- Classification is per SINGLE_PAIR_PROBE_001_PLAN.md §4.
- A classification of SELECTED_CELL_ARTIFACT means the cell does not survive the lab's anti-overfit screens and should NOT be promoted to further study.
- Lab output. Does not approve any strategy or change any campaign verdict.

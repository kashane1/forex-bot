# Post-Dedup Archetype Analysis

**Generated:** 2026-05-26T17:26:25.674540+00:00

> **Primary classification:** `PAIR_SPECIFIC_SIGNAL_WORTH_LAB`

> Exploratory labels do NOT approve strategies or justify retuning. Pair/fold cells that beat null may be noise given WITHIN_NULL aggregate labels.

## 1. Pair ranking (least bad → worst)

| pair | mean exp_r | C015 | C016 | C017 | +campaigns |
|---|---:|---:|---:|---:|---:|
| NZD_USD | 0.5441 | -0.4514 | 2.2406 | -0.1567 | 1/3 |
| EUR_USD | 0.3318 | -0.2439 | 1.2242 | 0.0152 | 2/3 |
| AUD_USD | 0.1370 | 0.0323 | 0.6532 | -0.2745 | 2/3 |
| USD_JPY | 0.0025 | 0.0044 | 0.0019 | 0.0010 | 3/3 |
| USD_CHF | -0.0318 | -0.2626 | -0.2233 | 0.3905 | 1/3 |
| GBP_USD | -0.1966 | 0.3248 | -1.0000 | 0.0853 | 2/3 |
| USD_CAD | -0.1969 | -0.1134 | -0.2639 | -0.2135 | 0/3 |

## 2. Fold / regime periods

- Universal fail folds (all campaigns negative, below null): [7]
- Folds with meaningful beat-null cell: 6

  - fold 0: CAMPAIGN_017 exp_r=0.1548 (gap vs null +0.2586)
  - fold 2: CAMPAIGN_016 exp_r=0.1596 (gap vs null +0.1205)
  - fold 3: CAMPAIGN_016 exp_r=0.3735 (gap vs null +0.3795)
  - fold 4: CAMPAIGN_016 exp_r=0.2612 (gap vs null +0.2465)
  - fold 5: CAMPAIGN_015 exp_r=0.2580 (gap vs null +0.2607)
  - fold 6: CAMPAIGN_017 exp_r=0.3875 (gap vs null +0.3335)

## 3. Long vs short (aggregate across trade CSVs)

- Long exp_r: -0.06280120235967517
- Short exp_r: 0.020097154168683035
- Less bad side: short
- Dominant loss driver: stops_dominate

### Exit reason mix

| reason | count | pct |
|---|---:|---:|
| stop | 374 | 50.4% |
| time | 355 | 47.8% |
| eod | 13 | 1.8% |

## 4. Weekly cost sensitivity

| campaign | base exp_r | 2x exp_r | Δ exp_r | trades |
|---|---:|---:|---:|---:|
| CAMPAIGN_015 | -0.0101 | -0.0283 | -0.0182 | 375 |
| CAMPAIGN_016 | -0.0633 | -0.0719 | -0.0087 | 137 |
| CAMPAIGN_017 | -0.0227 | -0.0283 | -0.0056 | 230 |

## 5. Cells beating null by ≥ 0.05R

Count: **10** (exploratory — may be noise)

- CAMPAIGN_015 fold 5: exp_r=0.2580 gap=+0.2607
- CAMPAIGN_015 GBP_USD: exp_r=0.3248 trades=82 gap=+0.3277
- CAMPAIGN_016 fold 2: exp_r=0.1596 gap=+0.1205
- CAMPAIGN_016 fold 3: exp_r=0.3735 gap=+0.3795
- CAMPAIGN_016 fold 4: exp_r=0.2612 gap=+0.2465
- CAMPAIGN_017 fold 0: exp_r=0.1548 gap=+0.2586
- CAMPAIGN_017 fold 5: exp_r=0.2189 gap=+0.2217
- CAMPAIGN_017 fold 6: exp_r=0.3875 gap=+0.3335
- CAMPAIGN_017 GBP_USD: exp_r=0.0853 trades=35 gap=+0.0882
- CAMPAIGN_017 USD_CHF: exp_r=0.3905 trades=37 gap=+0.3935

## 6. Classification labels

- Primary: `PAIR_SPECIFIC_SIGNAL_WORTH_LAB`
- All: `COST_MODEL_DOMINATES`, `PAIR_SPECIFIC_SIGNAL_WORTH_LAB`, `REGIME_SPECIFIC_SIGNAL_WORTH_LAB`, `SIDE_SPECIFIC_SIGNAL_WORTH_LAB`


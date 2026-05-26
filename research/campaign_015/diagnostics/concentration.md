# CAMPAIGN_015 — Concentration & Fragility Diagnostics

**Strategy:** `failed_breakout_reversal 0.1.0-c015`
**Config hash:** `17ddfd7eb87d93c502f148642c8ee883c66cb72bfa8ca72f981624a0dcfdd93c`

> Diagnostic only. Does NOT approve any strategy, does NOT relax any gate, does NOT revise the verdict.

## base cost

- total_trades = **164**
- total_r = **+37.7265**
- gross_positive_r = **+116.3688**
- gross_negative_r = **-78.6423**
- implied profit factor (from trade-R) = **1.4797**

### Top-trade concentration

| trade rank | fold | pair | R |
|---|---|---|---|
| 1 | 3 | USD_CAD | +6.2067 |
| 2 | 6 | USD_CHF | +5.9593 |
| 3 | 7 | USD_CHF | +5.9593 |
| 4 | 2 | GBP_USD | +5.9365 |
| 5 | 2 | EUR_USD | +5.0224 |

- Top-1 positive trade contributes **16.5%** of total R (and **5.3%** of gross positive R).
- Top-3 positive trades contribute **48.0%** of total R.
- Top-5 positive trades contribute **77.1%** of total R.

### Worst losers

| trade rank | fold | pair | R |
|---|---|---|---|
| 1 | 7 | USD_CHF | -1.2527 |
| 2 | 7 | USD_CHF | -1.2429 |
| 3 | 3 | USD_CHF | -1.1387 |
| 4 | 4 | USD_CHF | -1.1387 |
| 5 | 3 | USD_CHF | -1.1213 |

### Pair / fold / cell concentration

Per-pair total R:
- `AUD_USD` = +1.8478
- `EUR_USD` = +0.5156
- `GBP_USD` = +6.7381
- `NZD_USD` = -2.6028
- `USD_CAD` = +10.4632
- `USD_CHF` = +20.5645
- `USD_JPY` = +0.2001

Per-fold total R:
- fold 0 = -3.6890
- fold 1 = +1.5445
- fold 2 = +8.1581
- fold 3 = +12.0069
- fold 4 = +7.4054
- fold 5 = +2.9258
- fold 6 = +7.9531
- fold 7 = +1.4217

Top fold: fold **3** with R = **+12.0069** (**31.8%** of total R).
Top pair: **USD_CHF** with R = **+20.5645** (**54.5%** of total R).
Top pair-fold cell: **fold_06_USD_CHF** with R = **+9.3889** (**24.9%** of total R).

### Per-fold expectancy: mean vs median

- mean per-fold expectancy R = **+0.2230**
- median per-fold expectancy R = **+0.2588**
- mean − median gap = **-0.0357**

### Trade-R distribution

min=-1.2527 | p10=-1.0000 | p25=-1.0000 | median=-0.2541 | p75=+0.9086 | p90=+2.5662 | max=+6.2067

### Exit-reason mix

- `stop` = 79
- `time` = 85

### Leave-one-out by fold

| dropped fold | remaining trades | remaining total R | remaining expectancy R | remaining pairs+ |
|---|---|---|---|---|
| 0 | 146 | +41.4155 | +0.2837 | 6 |
| 1 | 138 | +36.1820 | +0.2622 | 5 |
| 2 | 138 | +29.5684 | +0.2143 | 4 |
| 3 | 136 | +25.7196 | +0.1891 | 4 |
| 4 | 140 | +30.3211 | +0.2166 | 6 |
| 5 | 150 | +34.8007 | +0.2320 | 6 |
| 6 | 150 | +29.7733 | +0.1985 | 6 |
| 7 | 150 | +36.3048 | +0.2420 | 6 |

### Leave-one-out by pair

| dropped pair | remaining trades | remaining total R | remaining expectancy R | fold-pass count after drop |
|---|---|---|---|---|
| AUD_USD | 140 | +35.8787 | +0.2563 | 0 |
| EUR_USD | 137 | +37.2108 | +0.2716 | 0 |
| GBP_USD | 123 | +30.9883 | +0.2519 | 0 |
| NZD_USD | 159 | +40.3292 | +0.2536 | 0 |
| USD_CAD | 141 | +27.2633 | +0.1934 | 0 |
| USD_CHF | 137 | +17.1620 | +0.1253 | 0 |
| USD_JPY | 147 | +37.5264 | +0.2553 | 0 |

## 2xcost cost

- total_trades = **164**
- total_r = **+31.3044**
- gross_positive_r = **+110.1537**
- gross_negative_r = **-78.8493**
- implied profit factor (from trade-R) = **1.3970**

### Top-trade concentration

| trade rank | fold | pair | R |
|---|---|---|---|
| 1 | 2 | GBP_USD | +5.7471 |
| 2 | 6 | USD_CHF | +5.6958 |
| 3 | 7 | USD_CHF | +5.6958 |
| 4 | 3 | USD_CAD | +5.5533 |
| 5 | 2 | EUR_USD | +4.8108 |

- Top-1 positive trade contributes **18.4%** of total R (and **5.2%** of gross positive R).
- Top-3 positive trades contribute **54.7%** of total R.
- Top-5 positive trades contribute **87.9%** of total R.

### Worst losers

| trade rank | fold | pair | R |
|---|---|---|---|
| 1 | 7 | USD_CHF | -1.2527 |
| 2 | 7 | USD_CHF | -1.2429 |
| 3 | 3 | USD_CHF | -1.1387 |
| 4 | 4 | USD_CHF | -1.1387 |
| 5 | 3 | USD_CHF | -1.1213 |

### Pair / fold / cell concentration

Per-pair total R:
- `AUD_USD` = +1.1020
- `EUR_USD` = -0.2935
- `GBP_USD` = +5.6751
- `NZD_USD` = -2.6615
- `USD_CAD` = +8.8078
- `USD_CHF` = +18.4816
- `USD_JPY` = +0.1928

Per-fold total R:
- fold 0 = -3.9462
- fold 1 = +1.1939
- fold 2 = +7.2462
- fold 3 = +10.2496
- fold 4 = +6.3653
- fold 5 = +2.3344
- fold 6 = +7.0195
- fold 7 = +0.8415

Top fold: fold **3** with R = **+10.2496** (**32.7%** of total R).
Top pair: **USD_CHF** with R = **+18.4816** (**59.0%** of total R).
Top pair-fold cell: **fold_06_USD_CHF** with R = **+8.8843** (**28.4%** of total R).

### Per-fold expectancy: mean vs median

- mean per-fold expectancy R = **+0.1831**
- median per-fold expectancy R = **+0.2160**
- mean − median gap = **-0.0329**

### Trade-R distribution

min=-1.2527 | p10=-1.0000 | p25=-1.0000 | median=-0.2733 | p75=+0.8653 | p90=+2.4672 | max=+5.7471

### Exit-reason mix

- `stop` = 79
- `time` = 85

### Leave-one-out by fold

| dropped fold | remaining trades | remaining total R | remaining expectancy R | remaining pairs+ |
|---|---|---|---|---|
| 0 | 146 | +35.2506 | +0.2414 | 5 |
| 1 | 138 | +30.1104 | +0.2182 | 5 |
| 2 | 138 | +24.0581 | +0.1743 | 4 |
| 3 | 136 | +21.0548 | +0.1548 | 4 |
| 4 | 140 | +24.9391 | +0.1781 | 5 |
| 5 | 150 | +28.9700 | +0.1931 | 5 |
| 6 | 150 | +24.2848 | +0.1619 | 6 |
| 7 | 150 | +30.4628 | +0.2031 | 6 |

### Leave-one-out by pair

| dropped pair | remaining trades | remaining total R | remaining expectancy R | fold-pass count after drop |
|---|---|---|---|---|
| AUD_USD | 140 | +30.2024 | +0.2157 | 0 |
| EUR_USD | 137 | +31.5979 | +0.2306 | 0 |
| GBP_USD | 123 | +25.6293 | +0.2084 | 0 |
| NZD_USD | 159 | +33.9659 | +0.2136 | 0 |
| USD_CAD | 141 | +22.4966 | +0.1596 | 0 |
| USD_CHF | 137 | +12.8227 | +0.0936 | 0 |
| USD_JPY | 147 | +31.1116 | +0.2116 | 0 |

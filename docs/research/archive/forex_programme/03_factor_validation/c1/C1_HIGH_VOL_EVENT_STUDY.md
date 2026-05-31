# C1 High-Volatility Event Study (Phase 2)

**Status:** RESULT (descriptive; no verdict, no positions, no trading logic)
**Date:** 2026-05-29
**Branch:** `research-c1-high-volatility-frontgate-001`
**Source:** committed C1 event panels `docs/research/c1_validation/{pair}_c1_events.csv`,
filtered by the **frozen** Phase-1 high-vol rule (event-bar H4 ATR ≥ within-pair
top tertile). Also written: `docs/research/c1_highvol_frontgate/{pair}_c1_hivol_events.csv`.

`C1_trend_cont_long`, high-vol subset, all sessions. Signed forward return
(**negative = reversion = favourable to the fade**); MFE/MAE are mean
favourable/adverse excursion magnitudes (pips); `hit(neg)` = fraction of events
with negative (reverting) return; `ret/ATR` = mean return ÷ mean H4-ATR
(volatility-adjusted). No positions, no stops, no PnL.

## 1. High-vol subset sizes & thresholds

| Pair | all C1_long | hi-vol thr (H4 ATR, pips) | hi-vol n | mean spread | mean H4 ATR |
|---|---|---|---|---|---|
| EUR_USD | 1595 | 39.64 | 532 | 1.633 | 49.4 |
| USD_JPY | 2145 | 54.07 | 715 | 1.827 | 65.3 |
| GBP_USD | 1585 | 46.72 | 528 | 2.114 | 63.4 |

## 2. Forward response by horizon

**EUR_USD (hi-vol n≈532)**
```
h    n    mean_ret  median    t     MFE    MAE   hit(neg)  ret/ATR
5   532   -0.640   -0.20   -3.43   1.83   2.50   0.532   -0.0130
10  532   -0.885   -0.40   -2.89   2.81   3.89   0.532   -0.0179
15  532   -1.095   -0.60   -2.91   3.66   5.01   0.543   -0.0222
30  531   -1.496   -0.60   -2.80   5.66   7.54   0.539   -0.0303
60  529   -1.777   -0.60   -2.57   8.29  10.87   0.531   -0.0360
```

**USD_JPY (hi-vol n≈715)**
```
h    n    mean_ret  median    t     MFE    MAE   hit(neg)  ret/ATR
5   715   -0.288   -0.40   -1.52   2.42   2.84   0.529   -0.0044
10  715   -0.262   -0.20   -0.96   3.86   4.27   0.509   -0.0040
15  714   -0.559   -0.50   -1.57   4.88   5.48   0.531   -0.0085
30  714   -1.223   -1.20   -2.42   7.09   8.54   0.550   -0.0187
60  712   -2.094   -0.65   -3.09  10.30  12.86   0.520   -0.0320
```

**GBP_USD (hi-vol n≈528)**
```
h    n    mean_ret  median    t     MFE    MAE   hit(neg)  ret/ATR
5   528   -0.546   -0.55   -2.25   2.28   2.95   0.557   -0.0086
10  528   -0.936   -0.70   -2.59   3.65   4.78   0.566   -0.0148
15  528   -1.212   -1.10   -2.79   4.65   6.01   0.564   -0.0191
30  528   -1.445   -1.15   -2.52   6.89   8.89   0.553   -0.0228
60  526   -1.258   -1.40   -1.58  10.64  12.89   0.548   -0.0198
```

## 3. Findings

1. **High-vol conditioning amplifies the reversion** (does add value vs the
   unconditional C1_long): 60-min mean goes EUR_USD −1.169 → **−1.78**, USD_JPY
   −1.136 → **−2.09**, GBP_USD −0.651 → **−1.26**. The Phase-1 "conditioning adds
   value" sub-condition is met on all three.
2. **But the reversion is shallow and skew-driven, not high-probability.** The
   60-min **median** is only −0.60 / −0.65 / −1.40 pip and **`hit(neg)` ≈
   0.52–0.55** — barely above a coin flip. The mean is more negative than the
   median: a minority of large reversions carries it. This is a weak directional
   bias, not a reliable fade.
3. **Adverse excursion exceeds favourable at every horizon** (e.g. EUR_USD 60-min
   MFE 8.29 vs MAE 10.87; USD_JPY 10.30 vs 12.86). A fade would, on average, sit
   through a *larger* adverse swing than the favourable one it is trying to
   capture — an execution liability even before cost.
4. **Magnitude vs spread is marginal.** The 60-min |mean| (1.78 / 2.09 / 1.26)
   only just exceeds (EUR/JPY) or sits below (GBP) the high-vol spread
   (1.63 / 1.83 / 2.11). Carried to Phase 3.

No trading logic, no positions, no stops were used; this is pure forward-response
measurement on the frozen high-vol subset.

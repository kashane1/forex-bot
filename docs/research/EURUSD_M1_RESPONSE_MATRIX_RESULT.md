# EUR_USD — M1/HTF Confluence Response Matrix (comparison pass)

**Status:** RESULT (descriptive; no verdict, no campaign, no strategy)
**Date:** 2026-05-29
**Branch:** `research-m1-htf-confluence-sampling-matrix-001`
**Pair:** EUR_USD · **M1 bars:** 1,843,476 · **Span:** 2021-05-27 → 2026-05-26 (~5.0y)
**Runner:** `scripts/run_m1_response_matrix.py --pair EUR_USD`
**Artifacts:** `docs/research/eur_usd_m1_response_matrix_summary.csv`,
`docs/research/eur_usd_m1_response_matrix_meta.json`

Same engine, same locked states/parameters as the USD_JPY pass. `mean_ret` = signed
forward mid move (pips) in the context direction; no trades; spread reported, not
charged. All numbers from the committed CSV.

## 1. Full matrix (t-stat and mean_ret by horizon)

```
state                     t5    t10    t15    t30    t60 |   r5     r15    r30    r60   |   n
A1_trend_cont_long       -1.13 -0.73 -1.73 -2.74 -3.00 | -0.047 -0.124 -0.291 -0.438 | 6255
A1_trend_cont_short      -1.70 -1.77 -1.61 -1.58 +0.18 | -0.069 -0.117 -0.154 +0.026 | 6305
A2_pullback_long         +0.24 -0.03 -1.22 -1.10 -0.48 | +0.010 -0.088 -0.113 -0.067 | 6116
A2_pullback_short        +1.65 +1.66 +1.82 +0.90 +0.23 | +0.063 +0.119 +0.085 +0.030 | 6303
A3_breakout_long         -1.39 -1.60 -2.53 -2.96 -2.30 | -0.071 -0.211 -0.337 -0.375 | 5670
A3_breakout_short        -1.55 -2.68 -1.28 -1.79 -2.39 | -0.070 -0.101 -0.196 -0.363 | 5756
A4_compression_long      +0.70 +0.24 -0.44 -0.63 +0.43 | +0.032 -0.035 -0.071 +0.067 | 2522
A4_compression_short     -1.12 -0.43 -1.71 -0.86 -0.44 | -0.057 -0.154 -0.107 -0.075 | 2491
B1_trend_cont_long       -1.94 -1.60 -1.96 -1.82 -2.97 | -0.137 -0.252 -0.339 -0.760 | 2400
B1_trend_cont_short      -2.27 -2.37 -2.11 -1.94 -0.97 | -0.157 -0.247 -0.343 -0.226 | 2531
B2_pullback_long         +0.15 -1.21 -1.66 -1.72 -2.02 | +0.010 -0.175 -0.267 -0.423 | 2661
B2_pullback_short        -0.81 -1.45 -1.14 -2.43 -1.54 | -0.041 -0.102 -0.327 -0.281 | 2968
B3_breakout_long         +0.29 +0.19 -1.34 -0.83 -1.80 | +0.025 -0.197 -0.162 -0.490 | 2318
B3_breakout_short        -1.52 -0.14 -1.02 -2.29 -1.83 | -0.116 -0.138 -0.411 -0.459 | 2351
C1_trend_cont_long       -3.25 -3.07 -3.47 -3.17 -3.65 | -0.281 -0.577 -0.745 -1.167 | 1592
C1_trend_cont_short      -2.47 -3.33 -2.81 -2.43 -1.26 | -0.200 -0.392 -0.518 -0.357 | 1781
C2_pullback_long         -0.50 -2.08 -2.33 -2.31 -3.34 | -0.040 -0.308 -0.442 -0.884 | 1694
C2_pullback_short        -1.14 -1.76 -1.18 -2.17 -0.65 | -0.070 -0.123 -0.358 -0.144 | 2071
```

Spread averaged 1.55–1.66 pips; trend-TF ATR ~7–37 pips across states.

## 2. Reading EUR_USD: a strong negative tilt, and one cross-pair match

EUR_USD's matrix is **dominated by negative t-stats** — most "bullish/aligned-up"
contexts are followed by *downward* moves. Two things are happening:

- A **regime/drift confound:** over 2021–2026 the USD was broadly strong, so EUR_USD's
  "above EMA50 / trend-up" episodes were largely *counter-trend bounces* that resumed
  down. Many negatives are that drift, not a microstructure law (Phase 5 tests this).
- **One signal lines up with USD_JPY in sign and magnitude:** **`C1_trend_cont_long`**
  is t = −3.25 / −3.47 / −3.65 (5/15/60 min), mean_ret −0.281 → **−1.167 pips at 60
  min** — the *same sign and nearly the same magnitude* as USD_JPY's `C1_trend_cont_long`
  (−1.137). Multi-timeframe bullish alignment is followed by a short-horizon decline on
  **both** pairs. `C1_trend_cont_short` is also strongly negative on EUR_USD (t −3.33 at
  10 min), i.e. multi-TF bearish alignment reverts *up* — a symmetric "fade the full
  alignment" pattern, though the short side is EUR-only (weak on USD_JPY).

## 3. Cross-pair comparison vs USD_JPY

| Dimension | USD_JPY | EUR_USD | Consistent (same sign)? |
|---|---|---|---|
| Sample counts | 1.2k–6.8k | 1.6k–6.3k | Yes (same corpus/states) |
| **`C1_trend_cont_long`** | t −3.56, ret −1.137 @60m | t −3.65, ret −1.167 @60m | **Yes — same sign & magnitude** |
| `A2_pullback_long` | t **+**2.9 (continuation) | t −1.1 (within noise) | **No** — USD_JPY-only |
| `B3_breakout_long` | t **+**2.7 @15m | t −1.3 @15m | **No** — sign flips |
| `A3_breakout_long` | t **+**1.9 @60m | t **−**2.3 @60m | **No** — sign flips (drift) |
| Trend-cont longs `A1`/`B1` | mildly negative | strongly negative | Same sign, EUR stronger |
| Spread | ~1.76 pip | ~1.61 pip | `C1_long` cost-defeated on **both** |

### State stability

Only **`C1_trend_cont_long` replicates cleanly across pairs** — same (negative) sign,
similar magnitude, both growing with horizon. The USD_JPY *continuation* cells
(`A2_pullback_long`, `B3_breakout_long`) do **not** carry to EUR_USD, and the breakouts
(`A3`) actively **flip sign** — the signature of a USD-regime drift confound rather than
a universal effect. By the cross-pair-replication bar, the matrix collapses to **one
candidate: fade multi-timeframe bullish alignment (`C1_long`).**

## 4. Spread awareness (both pairs)

For the cross-pair candidate `C1_trend_cont_long`, the 60-min reversion is ~1.14 pips
(USD_JPY) / ~1.17 pips (EUR_USD), against spreads of ~1.76 and ~1.61. The effect is
**below spread on both pairs** (~0.65× USD_JPY, ~0.72× EUR_USD) — a real, cross-pair,
null-surviving *factor* that is **not** an edge as measured. (An earlier draft of this
doc mis-stated the EUR_USD spread as ~0.66 pip and therefore wrongly claimed the effect
cleared cost on EUR_USD; the committed CSV shows EUR_USD spread ~1.61 pip, so `C1_long`
is cost-defeated on both pairs.)

States carried into the Phase-5 null comparison: `C1_trend_cont_long` (the candidate),
with `A1_trend_cont_long` (trend-continuation control) and `A3_breakout_long` /
`A3_breakout_short` (the sign-flipping breakout pair) as cross-pair controls.

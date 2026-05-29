# USD_JPY — M1/HTF Confluence Response Matrix (discovery pass)

**Status:** RESULT (descriptive; no verdict, no campaign, no strategy)
**Date:** 2026-05-29
**Branch:** `research-m1-htf-confluence-sampling-matrix-001`
**Pair:** USD_JPY · **M1 bars:** 1,844,454 · **Span:** 2021-05-27 → 2026-05-26 (~5.0y)
**Engine:** `src/forex_bot/research/m1_response_matrix.py`
**Runner:** `scripts/run_m1_response_matrix.py --pair USD_JPY`
**Artifacts:** `docs/research/usd_jpy_m1_response_matrix_summary.csv`,
`docs/research/usd_jpy_m1_response_matrix_meta.json`

> `mean_ret` is the **signed forward mid move in pips** in the state's context
> direction. No trades; spread reported, not charged. A positive `mean_ret` on a
> `_short` state means price moved *down* (with the short context). All numbers
> below come from the committed CSV artifact.

## 1. Full matrix (t-stat and mean_ret by horizon)

Events de-overlapped by rising-edge + 60-min cooldown (≤60-min windows of
consecutive events do not overlap → near-independent). `t` = t-stat of mean signed
forward return; `r` = mean signed return (pips).

```
state                     t5    t10    t15    t30    t60 |   r5     r15    r30    r60   |   n
A1_trend_cont_long       -0.43 -1.24 -1.00 -0.73 +0.34 | -0.024 -0.101 -0.103 +0.070 | 6669
A1_trend_cont_short      -0.94 -1.78 -0.67 +0.19 +1.05 | -0.078 -0.098 +0.038 +0.282 | 5651
A2_pullback_long         +2.17 +2.05 +2.91 +2.81 +2.72 | +0.111 +0.268 +0.359 +0.537 | 6790
A2_pullback_short        +1.48 +0.34 +0.54 -0.40 +0.05 | +0.104 +0.063 -0.071 +0.013 | 5473
A3_breakout_long         +0.46 -0.44 +0.14 +0.90 +1.89 | +0.030 +0.015 +0.135 +0.403 | 6389
A3_breakout_short        -2.10 -0.86 -0.38 -0.24 +0.57 | -0.204 -0.064 -0.056 +0.175 | 4877
A4_compression_long      -0.34 -0.57 -0.48 -0.54 +0.87 | -0.023 -0.062 -0.092 +0.227 | 3341
A4_compression_short     -0.07 +0.31 -0.22 -1.39 +0.02 | -0.006 -0.035 -0.334 +0.008 | 2456
B1_trend_cont_long       -1.40 -0.30 -0.99 -1.38 -1.85 | -0.124 -0.150 -0.293 -0.553 | 2690
B1_trend_cont_short      +0.20 -0.12 +0.21 -0.82 +0.06 | +0.033 +0.051 -0.277 +0.032 | 2020
B2_pullback_long         -0.76 -0.02 -0.63 -0.11 -0.65 | -0.085 -0.113 -0.025 -0.204 | 3321
B2_pullback_short        -0.21 -0.93 -0.25 -0.15 +0.11 | -0.026 -0.047 -0.039 +0.043 | 2487
B3_breakout_long         +1.31 +2.63 +2.72 +1.43 +1.95 | +0.120 +0.417 +0.312 +0.602 | 2909
B3_breakout_short        -0.80 -0.48 -0.40 +0.32 +0.32 | -0.150 -0.119 +0.132 +0.180 | 1823
C1_trend_cont_long       -1.69 -0.70 -1.20 -2.90 -3.56 | -0.153 -0.199 -0.682 -1.137 | 2143
C1_trend_cont_short      -0.15 -0.55 +0.24 -0.54 -0.39 | -0.034 +0.075 -0.251 -0.272 | 1155
C2_pullback_long         +0.50 +1.47 +1.05 +0.36 -0.64 | +0.039 +0.148 +0.074 -0.195 | 2602
C2_pullback_short        +0.44 +0.39 +0.75 -0.07 +0.31 | +0.083 +0.208 -0.025 +0.173 | 1442
```

Spread averaged 1.72–1.90 pips; trend-TF ATR (volatility) ~10–45 pips across states
(H4-ATR for Family C ≈ 45 pips).

## 2. Which states appear strongest?

Three cells reach |t| ≥ 2.5, pointing in two opposite directions:

1. **`A2_pullback_long` (positive, continuation):** t = +2.17 / +2.91 / +2.81 /
   +2.72 across 5/15/30/60 min; mean_ret +0.111 → +0.537 pips. After an M5
   pullback inside an M15 uptrend, USD_JPY tends to **resume upward** — the
   textbook "buy-the-dip in a trend" effect, and the strongest *continuation* cell.
2. **`B3_breakout_long` (positive):** t peaks +2.72 at 15 min (+0.417 pips).
3. **`C1_trend_cont_long` (negative, reversion):** t = −2.90 / −3.56 at 30/60 min;
   mean_ret −0.682 → **−1.137 pips at 60 min**. When *all three* timeframes are
   bullish-aligned (H4 + H1 trend-up and M15 above EMA50 — an extended up-move),
   the next hour tends to **revert down**. This is the largest-magnitude cell in
   the whole matrix and the cleanest *mean-reversion-after-extension* signal.

So USD_JPY shows **continuation after a shallow pullback** (`A2_long`) but
**reversion after full multi-TF extension** (`C1_long`) — a coherent
over-extension story (mild dips resume; fully-stretched alignment fades).

## 3. Which states appear random?

Most other states sit at |t| < 1.5 across horizons (`A4_compression_*`,
`B2_*`, `C2_short`, the trend-cont shorts). Several trend-continuation *longs*
(`A1`, `B1`) are mildly negative — consistent with the same over-extension
reversion seen sharply in `C1_long`, but weaker at the M5/M15 structure level.

## 4. Which states have enough samples?

All 18 signed states have n between 1,155 and 6,790. Family-C and short states are
smallest (`C1_short` n=1,155) but still usable; the headline `C1_long` has
n=2,143 and `A2_pullback_long` n=6,790. Sample size is not a limiter, though the
smaller Family-C cells warrant the Phase-5 null check before any claim.

## 5. Which states survive spread awareness?

The two largest effects, in pips: `C1_trend_cont_long` −1.137 and
`A2_pullback_long` +0.537 at 60 min, against ~1.76 pip spread. Even the biggest
(`C1_long`, ~1.14 pips) is **below** the USD_JPY round-trip spread (~0.65×) — not
tradable as-is. (The same `C1_long` effect is likewise cost-defeated on EUR_USD,
~1.17 pips vs ~1.61 spread, ~0.72× — see the comparison pass.) As with prior
efforts, statistical signal exists below cost.

Candidates carried into the Phase-5 null comparison: `C1_trend_cont_long`
(reversion), `A2_pullback_long` and `B3_breakout_long` (continuation), plus the
breakouts `A3_breakout_long` / `A3_breakout_short` for cross-pair contrast.

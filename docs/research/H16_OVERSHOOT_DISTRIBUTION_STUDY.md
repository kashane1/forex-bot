# H16 — overshoot distribution study (Phase 2)

**Sprint:** `research-non-time-bar-overshoot-frontgate-001` · Phase 2
**Window:** C029 train `2021-05-27 → 2023-12-31` (lockbox untouched).
**Bars:** 30-pip range bars (mid). **Pairs:** USD_JPY (4,403 bars), GBP_USD (3,853),
EUR_USD (2,132).
**Artifacts:** [`research/h16_overshoot_frontgate/distribution_study.json`](../../research/h16_overshoot_frontgate/distribution_study.json),
[`h16_screen_matrix.csv`](../../research/h16_overshoot_frontgate/h16_screen_matrix.csv).

> Conditional-distribution measurement only — no positions, PnL, signals, or campaign.

---

## 1. Overshoot distribution (pips beyond the 30-pip threshold at completion)

| pair | mean | median | p75 | p95 | quartile edges (Q1/Q2/Q3) | top-5% edge |
|---|---:|---:|---:|---:|---|---:|
| USD_JPY | 4.64 | 1.7 | 4.4 | 15.9 | 0.6 / 1.7 / 4.4 | 15.9 |
| GBP_USD | 3.25 | 1.4 | 3.2 | 11.4 | 0.5 / 1.4 / 3.2 | 11.4 |
| EUR_USD | 2.72 | 1.2 | 2.8 | 9.4 | 0.4 / 1.2 / 2.8 | 9.5 |

## 2. Answers to the Phase-2 questions

1. **Are large overshoots actually rare?** **Yes.** The distribution is strongly
   right-skewed (mean ≫ median). The median completion overshoots its threshold by only
   ~1.2–1.7 pips, while the top 5% overshoot by ≥ ~9–16 pips. Large overshoots are a
   genuine, infrequent tail.
2. **Do they cluster?** **Mildly.** Lag-1 autocorrelation of overshoot is 0.07 (EUR),
   0.19 (GBP), 0.18 (USD_JPY); P(next is extreme | current is extreme) vs base rate has
   lift 1.21 / 1.38 / 1.52. Consistent with ordinary volatility clustering — not a
   strong standalone structure.
3. **Concentrated in specific sessions?** **Yes, mildly.** Mean overshoot is largest in
   the **rollover_late** and **london_ny_overlap** sessions (e.g. USD_JPY rollover 5.84,
   overlap 5.38 vs Tokyo 4.58, NY 3.72). The biggest overshoots skew toward the
   **illiquid rollover** window and the volatile London/NY overlap.
4. **Associated with spread expansion?** **Yes — and this is adverse for the thesis.**
   The mean spread in the **extreme** overshoot bucket is materially wider than in the
   **small** bucket: USD_JPY 2.74 vs 1.83 pips, GBP 2.76 vs 2.02, EUR 1.86 vs 1.50.
   Cost is **worst exactly when overshoot is largest** — precisely the bars H16 would
   want to fade.
5. **News-like behaviour?** **Mildly.** The extreme bucket has a slightly elevated mean
   `thresholds_crossed` (USD_JPY 1.15 vs 1.0 elsewhere), i.e. some extreme completions
   are single-candle jumps (gap/news-like). Not dominant.
6. **Stable enough to study?** **Yes.** Thousands of bars per pair; quartile structure
   is consistent across pairs.

## 3. Implication for the rest of the screen

The geometry is **studiable** (rare, mildly clustered tail) but the cost picture is
already unfavourable: large overshoots arrive with **wider spreads** and in **less
liquid sessions**. For H16 to survive, the post-overshoot **reversion** measured in
Phase 3 would need to be both directionally real and large enough to beat that elevated
cost (Phase 4) and a shuffle null (Phase 5).

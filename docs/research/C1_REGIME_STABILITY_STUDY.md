# C1 Regime Stability Study (Phase 2)

**Status:** RESULT (descriptive; no verdict, no campaign, no strategy)
**Date:** 2026-05-29
**Branch:** `research-c1-factor-validation-001`
**Artifacts:** `docs/research/c1_validation/{pair}_c1_events.csv` (per-event panel
with `year`, `quarter`, `session`, `volatility` = H4 ATR pips, `ext_signed` =
direction × distance above EMA50 in ATR).

All figures read from the committed panels. Focus is **C1_trend_cont_long** at
the **60-min** horizon (the prior sprint's headline). "POOLED-7" stacks all seven
majors' events; tertiles are assigned **within each pair** so a pooled tertile is
not just a pair-size effect. A negative mean = reversion against the alignment.
(A handful of events with undefined early-window ATR — 14 of ~11,400 — fall in a
`nan` covariate bucket and are ignored.)

## 1. By calendar year (POOLED-7)

```
year      n   mean60    t60   pneg
2021    562   -0.936  -2.05  0.536
2022   2240   -0.301  -0.92  0.499
2023   2430   -1.026  -3.85  0.529
2024   2529   -0.863  -3.87  0.529
2025   2590   -0.548  -2.34  0.500
2026   1063   +0.123  +0.42  0.488   (partial year; corpus ends 2026-05-26)
```

Negative in **5 of 6** calendar years and significant (t ≤ −2) in **four**
(2021, 2023, 2024, 2025). 2022 is weakly negative (t −0.92); 2026 is a ~5-month
stub that ticks slightly positive but is small and insignificant. **The factor is
persistent across years, not the product of a single episode.** On the two strong
pairs the yearly sign is likewise mostly negative (EUR_USD negative every year,
significant 2021/2024; USD_JPY negative in 5/6, significant 2024/2025).

## 2. By trading session (POOLED-7)

```
session     n   mean60    t60   pneg
london   2925   -0.864  -3.94  0.521
ny       4570   -0.688  -3.03  0.512
offhours  681   -0.625  -2.23  0.517
tokyo    3238   -0.329  -2.04  0.507
```

Negative and significant in **all four** sessions; strongest in the liquid
**London and NY** windows. Not a single-session artifact.

## 3. By volatility regime — within-pair H4-ATR tertiles (POOLED-7)

```
tertile    n   mean60    t60   pneg    vol(pips)  spread
low     3806   -0.379  -2.53  0.504      26.9      1.737
mid     3798   -0.524  -2.79  0.520      36.5      1.724
high    3796   -0.975  -3.78  0.516      51.5      1.799
```

The reversion **grows monotonically with volatility** — it is roughly 2.5× larger
in the top ATR tertile than the bottom. This is a clean, sensible gradient (bigger
swings overshoot and revert more), and it is the single strongest sub-regime
(t −3.78). **Caveat for Phase 5:** spread also rises in the high-vol tertile
(1.80 vs 1.74), so even the −0.975-pip high-vol reversion stays well below its
~1.80-pip spread.

## 4. By extension regime — within-pair `ext_signed` tertiles (POOLED-7)

`ext_signed` is how far price sits above EMA50 (in ATR) on the slow leg, in the
alignment's direction — i.e. *how stretched* the multi-TF alignment is.

```
tertile    n   mean60    t60   pneg    mean ext (ATR)
low     3805   -0.562  -2.73  0.514       0.70
mid     3798   -0.599  -2.92  0.509       1.83
high    3797   -0.717  -3.59  0.516       3.55
```

The reversion **grows monotonically with extension** (−0.56 → −0.60 → −0.72;
t −2.73 → −2.92 → −3.59). This is direct support for the **over-extension
mechanism** the prior sprint hypothesised: the more stretched the alignment, the
larger the subsequent fade — not a single arbitrary threshold. The gradient is
**mild**, though, and *per-pair* it is noisy (EUR_USD is actually flat-to-inverted
across extension tertiles; USD_JPY is non-monotone but strongest in the top
tertile). So the monotonicity is a pooled, population-level property, not a sharp
per-pair lever.

## 5. Answers to the Phase-2 questions

- **Persistent?** **Yes.** Same negative sign in 5/6 years, all 4 sessions, and
  all 3 volatility and extension tertiles. There is no single year, session, or
  bucket whose removal would flip the result.
- **Episodic?** **No.** It is not driven by one regime window; 2022 is the only
  soft year and even it is correctly signed.
- **Concentrated?** **Mildly, and sensibly** — in **high-volatility** and
  **high-extension** states, with monotone gradients in both. That concentration
  is *consistent with a real overshoot-reversion factor* rather than a fluke: the
  effect is largest exactly where an over-extension story predicts it should be.
  But the concentration does **not** rescue tradeability — high-vol states also
  carry wider spreads (Phase 5).

## 6. Takeaway

C1_long behaves like a **stable, persistent, volatility- and extension-scaled
mean-reversion factor**, not an episodic artifact. The regime evidence pushes
**toward "real factor"** and away from "sample-selection / mirage." Whether the
high-vol / high-extension concentration can ever clear cost is deferred to
Phase 5; whether the magnitude pattern survives the USD-leg dissection is Phase 3.

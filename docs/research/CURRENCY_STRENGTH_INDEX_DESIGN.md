# Currency-Strength Index — Construction Design (Phase 2)

**Sprint:** `research-currency-strength-factor-validation-001` · Phase 2
**Status:** construction (factor only — **no trades, no signals, no entry/exit,
no PnL**). Implements the frozen protocol. Code is import-isolated under
`research/edge_discovery/currency_strength.py`; runner
`scripts/run_currency_strength_factor.py`.
**Date:** 2026-05-30.

This phase **builds the factor and its descriptive measures** (strength score,
ranking, dispersion, spread) and a collinearity diagnostic. It does **not**
measure forward response (Phase 3) or decide anything.

---

## 1. Strength-index definition (as built)

**Synthetic per-currency cumulative log-index** (average-of-pairs, protocol §3):
for currency `c`,
```
CC_c(t) = mean over instruments i containing c of [ sign_ci * ln(mid_close_i(t)) ]
          sign_ci = +1 if c is the base leg of i, -1 if the quote leg
strength_c(t) = CC_c(t) - CC_c(t - L)     (L = 48 M5 bars = 4h look-back)
```
Because the instrument set and signs are fixed per currency, `CC_c` is a valid
synthetic currency index and both the look-back strength and the forward response
(Phase 3) are exact signed average-of-pairs aggregations of it. Equal-weight, no
vol-scaling, no winsorization (frozen primary).

## 2. Derived measures (as built)

- **Ranking:** currencies sorted by `strength_c(t)` each bar; rank 1 = strongest,
  rank 8 = weakest (`rank_panel`).
- **Change-in-strength:** `Δstrength_c(t) = strength_c(t) − strength_c(t−12)`
  (1h) → top-1 = rapidly strengthening, bottom-1 = rapidly weakening.
- **Dispersion:** cross-sectional std of the 8 strengths each bar.
  **Mean dispersion = 0.001773** (log-return units over the 4h window).
- **Spread:** max−min strength each bar. **Mean spread = 0.005263.**

## 3. Panel facts (from `construction_meta.json`)

- 15 instruments, M5 materialized mid closes, source `m1_materialized`.
- **Common aligned M5 bars: 304,014** (inner-join across all 15), span
  2021-05-27 → 2026-05-26.
- **Events: 25,330** (hourly decimation, every 12 M5 bars, after warm-up).

## 4. Leg multiplicity — CORRECTION NOTE (transparency)

The frozen protocol §1 annotated per-currency leg counts as "USD 7, EUR 6, GBP 4,
JPY 5, AUD 4, NZD 3, CHF 3, CAD 1." Building the index from the actual 15-
instrument list, the **true counts** (emitted authoritatively in
`construction_meta.json`) are:

```
USD 7, EUR 5, GBP 4, JPY 5, AUD 3, NZD 2, CHF 3, CAD 1   (total legs = 30)
```

i.e. the protocol's descriptive annotation over-counted **EUR (5 not 6), AUD (3
not 4), NZD (2 not 3)**. **This is a documentation miscount in a descriptive
annotation, not a parameter** — the construction always derives signs/counts from
the frozen instrument list, never from the annotation, so **no computation is
affected**. It was caught during Phase-2 construction on *synthetic* data, before
any real-data response review. Per the "no silent edits to the frozen protocol"
discipline, the protocol file is left as-committed and this correction is logged
here; the authoritative counts live in the meta JSON. CAD remains the
pre-registered weak link (1 instrument → CAD strength ≡ −USD_CAD return).

## 5. Collinearity / breadth diagnostic (from `collinearity.json`)

PCA of the standardized 8-currency strength panel:

- **PCA variance ratios:** `[0.472, 0.217, 0.131, 0.086, 0.046, 0.034, 0.014,
  0.000]`. (The last is 0 because the 8 strengths are linearly dependent — the
  signed average-of-pairs construction makes the cross-currency sum ≈ 0, so the
  panel has rank 7. Expected and harmless.)
- **PC1 explains 47%** and its loadings are a **risk-on/off axis**, NOT a USD
  axis: `USD +0.365, JPY +0.351, CHF +0.082` (havens) vs `NZD −0.475, AUD −0.448,
  CAD −0.402, GBP −0.366, EUR −0.125` (risk/commodity). PC2 (22%) and PC3 (13%)
  add further independent structure.
- **Mean |off-diagonal correlation| = 0.376** — moderate, not degenerate.

**Reading (breadth hypothesis H2):** the strength vector is **genuinely
multi-currency** — PC1 is a haven-vs-risk dimension with USD as just one of
several comparable loadings, and >1 PC carries material variance. The factor is
**not reducible to the USD axis** that the pre-registered failure-mode (b) worried
about. **H2 (breadth) holds.** Whether it carries *forward-predictive* information
(H1) is the Phase-3 question — breadth of construction ≠ predictive existence.

## 6. What was NOT built

No signal, no trade rule, no entry/exit, no position, no PnL, no cost model use,
no approval. Construction + descriptive measures only.

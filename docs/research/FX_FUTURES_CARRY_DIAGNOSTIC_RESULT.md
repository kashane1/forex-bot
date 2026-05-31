# FX Futures Carry Diagnostic — Result (Phase 3)

**Sprint:** `research-fx-futures-carry-diagnostic-001`
**Type:** Diagnostic result. The FROZEN carry factor, futures returns substituted. No optimization, no parameter changes, no strategy.
**Date:** 2026-05-31
**Artifacts:** `research/fx_futures/diagnostic/primary.json`, `deep.json` (all numbers below are emitted directly from these files).

---

## 0. What was measured

The **frozen** carry factor (currency HML-3: long top-3 / short bottom-3 by OECD 3M interbank rate, lag-1, dollar-neutral, monthly rebalance; horizons 1/3/6/12 m; primary cell = HML-3 total, 3 m; seed 20260531) — run unchanged, with the **futures continuous price series substituted for the spot mid**.

**Venue identity (decisive):** in futures the rate differential is embedded in the **basis** and converges *into* the price; there is **no nightly accrual handed out** and financing = 0. Therefore **futures total return = futures price return** — exactly the **spot-predictive component** in isolation, which the spot study measured as statistically zero (t ≈ 0.1). The diagnostic asks: *does ranking currencies by carry predict subsequent futures price moves?*

Two runs:
- **PRIMARY** — cached frozen signal **including JPY**, intersected with the futures window (signal 2021-05 → 2026-05). Apples-to-apples with the spot study, futures prices substituted.
- **DEEP** — live FRED signal, **JPY-excluded** (its FRED series is retired), over ~24 years. Breadth-and-history robustness.

---

## 1. Gross carry relationship (futures price return)

### PRIMARY (incl. JPY, window 2021-05-01 → 2026-05-01, rank stability 0.984)

| Horizon | Mean | NW-HAC t | Sign consistency | n |
|--------:|-----:|---------:|-----------------:|--:|
| 1 m | +0.000291 | +0.16 | 0.610 | 59 |
| 3 m (primary) | **+0.000426** | **+0.09** | 0.596 | 57 |
| 6 m | +0.000071 | +0.01 | 0.574 | 54 |
| 12 m | -0.003444 | -0.29 | 0.458 | 48 |

### DEEP (ex-JPY, window 2001-01-01 → 2026-04-01, 304 months, 6 currencies)

| Horizon | Mean | NW-HAC t | Sign consistency | n |
|--------:|-----:|---------:|-----------------:|--:|
| 1 m | -0.001338 | -1.35 | 0.467 | 302 |
| 3 m | -0.004116 | -1.65 | 0.445 | 301 |
| 6 m | -0.008718 | -1.88 | 0.413 | 298 |
| 12 m | -0.015975 | -1.94 | 0.380 | 292 |

**Reading:** the PRIMARY futures carry price return is **economically and statistically zero** — the 3-month cell is +0.000426 (+0.043 %/qtr) with **t = +0.09**, indistinguishable from zero; sign consistency ~0.5. The DEEP ex-JPY run over ~24 years is consistently **negative** (3-month -0.004116, t = -1.65), i.e. ranking by carry mildly *anti*-predicts futures price over the long sample, with |t| still < 2. Neither run shows carry meaningfully and favourably predicting futures price at any horizon.

---

## 2. Predictive component vs the spot study (the core comparison)

| Quantity (HML-3, 3 m) | Spot study (`carry-factor-validation-001`) | This futures diagnostic (PRIMARY) |
|----------|--------------------------------------------|--------------------------|
| **Total** | **+0.74 %/qtr**, t = 1.68 | **+0.043 %/qtr**, t = +0.09 |
| **Spot-predictive (price-only) leg** | ≈ 0, t = 0.10 | *(this IS the futures total)* same cell |
| Source of the spot positive total | mechanical accrual (~94 % of total) | **absent** — accrual is in the basis, not paid out |

This is the venue study's prediction **confirmed**: the futures total return (the price-only, financing-free quantity) essentially equals the spot study's spot-predictive leg (≈0). Strip the mechanical accrual — which futures does by construction — and the carry "premium" is gone. Futures did not reveal a hidden tradable carry edge; it confirmed the spot premium *was* the accrual, with no predictive residual underneath.

---

## 3. Persistence (signal structure)

Rank stability (mean month-over-month Spearman of the carry ranking): **0.984** (PRIMARY), **0.989** (DEEP) — the same near-static tilt found in spot (0.984). The signal persists strongly; it is a constant level tilt, **not** a dynamic timing signal. Persistence of the *signal* does not translate into predictability of *price*.

---

## 4. Cross-sectional consistency (single-name dependence)

Leave-one-currency-out, PRIMARY primary cell (h3, futures price return):

| Removed | Mean (h3) |
|---------|----------:|
| full | +0.000426 |
| drop AUD | -0.001080 |
| drop CAD | +0.001300 |
| drop CHF | +0.004334 |
| drop EUR | +0.001344 |
| drop GBP | +0.000149 |
| drop JPY | -0.004687 |
| drop NZD | +0.002160 |

As in spot, **JPY dominates**: removing it moves the (already near-zero) PRIMARY mean to -0.004687. The tiny reading is a JPY artifact, not a broad cross-sectional property — the same JPY-concentration the spot study found.

---

## 5. Summary

- PRIMARY futures carry price return is **≈ 0 at every horizon** (h3 +0.043 %/qtr, t = +0.09), sign consistency ~0.5.
- It is the spot-predictive component in isolation, and it is **statistically zero** — confirming, on a fair financing-free venue, the spot study's finding that carry's predictive leg is null.
- The DEEP ex-JPY ~24-year run is consistently negative (anti-predictive) and also insignificant (|t| < 2), corroborating the null.
- Signal is a persistent static tilt; the effect is JPY-concentrated.
- Null comparison (Phase 4) tests whether either reading separates favourably from chance. (It does not.)

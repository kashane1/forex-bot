# FX Futures Carry — Null Comparison (Phase 4)

**Sprint:** `research-fx-futures-carry-diagnostic-001`
**Type:** Null/benchmark comparison for the frozen carry factor on futures returns. No optimization.
**Date:** 2026-05-31
**Artifacts:** `research/fx_futures/diagnostic/primary.json`, `deep.json` (`nulls` blocks; numbers emitted directly).

All nulls are computed **price-only** (futures total = price return, financing = 0), **2000 draws, seed 20260531**. The generic null / matched-Z / Holm machinery is the **unmodified** `research.carry.carry_factor` code used in the spot study — same bar, no new thresholds. The frozen front-gate bar: an effect must reach **matched-Z ≥ 2 against every null** and survive Holm.

## 1. The four benchmarks

1. **Randomized ranks** — permute asset→carry-value each month. Tests whether the carry identity beats a random ranking.
2. **Shuffled timestamp** — permute the signal's months. Tests for timing content.
3. **Matched random (shuffled contracts)** — random long/short baskets of size 3 each month.
4. **Unconditional baseline** — equal-weight long all currencies vs USD.

## 2. PRIMARY (incl. JPY, primary cell h3, observed mean = +0.000426)

| Null | Null mean | Matched Z | one-sided p (obs ≥ null) |
|------|----------:|----------:|-------------------------:|
| Randomized ranks | -0.000133 | **+0.21** | 0.423 |
| Shuffled timestamp | +0.000491 | **-0.09** | 0.536 |
| Matched random | +0.000000 | **+0.15** | 0.430 |

Unconditional baseline mean: -0.004649.

**Holm–Bonferroni:** randomized_ranks no-reject (p=0.423); matched_random no-reject (p=0.430); shuffled_timestamp no-reject (p=0.536).

**Reading:** every matched Z is small (max magnitude 0.21), **nowhere near the frozen Z ≥ 2 bar**; all one-sided p ≈ 0.4–0.6; **Holm rejects nothing**. The carry ranking is statistically indistinguishable from a random ranking, a time-shuffled signal, and a random basket. No favourable separation from chance.

## 3. DEEP (ex-JPY, h3, ~24 y, observed mean = -0.004116)

| Null | Null mean | Matched Z | one-sided p (obs ≥ null) |
|------|----------:|----------:|-------------------------:|
| Randomized ranks | +0.000044 | **-2.98** | 0.999 |
| Shuffled timestamp | -0.001521 | **-2.83** | 0.997 |
| Matched random | +0.000009 | **-3.00** | 0.998 |

Unconditional baseline mean: +0.002814.

**Reading:** over 24 years and ex-JPY, the observed carry mean is **negative and BELOW every null** (all matched Z < 0, one-sided p ≈ 1.00), and the **unconditional baseline (+0.0028) is positive** while carry is negative — i.e. carry-ranking *detracts* over the deep window. It reaches positive separation against no null.

## 4. Verdict on nulls

Across every benchmark and both windows, the frozen carry factor on futures price returns never reaches favourable matched-Z, let alone the frozen **Z ≥ 2** bar; fails Holm at every cell; and (deep) is below even the unconditional baseline. This is the **unambiguous null outcome**, feeding the Phase-5 binary verdict.

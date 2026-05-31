# Cross Relative-Value — Robustness Review (Phase 6)

**Sprint:** `research-cross-relative-value-factor-validation-001` · Phase 6
**Status:** RESULT (descriptive; verdict deferred to Phase 7). The three frozen
robustness axes (protocol §12) — **nearby normalization, nearby relationship
definitions, nearby deviation thresholds** — are tested. Stability check, not
optimization. Figures from committed `robustness.csv` + `shared_leg_spreads.csv`.
The reported z is the **conservative randomized-relationships** pooled null.
**Date:** 2026-05-30.

---

## 1. Nearby normalization (lookback 24 / 96; robust median-MAD z)

```
variant      5min z   15min z  30min z  60min z  240min z
lookback_24    7.63     4.80     2.23    -0.60     1.13
lookback_96   11.34     5.66     5.40     4.68     5.82
robust_z       9.74     8.04     5.62     5.36     6.56
```

- The reversion **persists under every normalization** — the existence is not an
  artifact of the primary L=48 or of mean/std z.
- **Lookback 24 (2h) collapses at 60 min** (z −0.60): a shorter normalization
  window leaves the true-vs-false-triangle *excess* concentrated at short horizons
  only — reinforcing that much of the randomized-relationships advantage is fast
  (microstructure). Lookback 96 (8h) and robust-z keep clearing at all horizons
  (driven by the JPY complex's genuine slow reversion).

## 2. Nearby deviation thresholds (|z| ≥ 1.5 / 2.5)

```
variant      5min z   15min z  30min z  60min z  240min z
thresh_1.5   10.42     5.75     4.57     4.19     3.59
thresh_2.5    7.99     5.69     4.08     2.13     3.68
```

Clears |z| ≥ 2 at essentially every horizon for both nearby thresholds — the
reversion is **not a knife-edge of the |z| ≥ 2 cut**. Larger deviations (2.5)
revert by more in absolute bp (Phase 3 pattern) but the null-separation is similar.
**Robust across thresholds.**

## 3. Nearby relationship definition — shared-leg cointegration spreads

The secondary family (pre-named shared-leg spreads, hedge-ratio β) is the key
*contrast*:

```
spread            beta   half_life_bars   60min rev_bp   240min rev_bp
EUR_JPY~GBP_JPY   1.000     7,413           0.465          0.469
EUR_JPY~AUD_JPY   1.228    23,258           0.130         -0.356
GBP_JPY~AUD_JPY   1.198    26,797           0.130         -0.221
AUD_JPY~NZD_JPY   1.303    20,704           0.735          0.625
```

- **Shared-leg spreads do NOT mean-revert at tradeable horizons.** Their AR(1)
  half-lives are **7,000–27,000 bars** (weeks–months) — effectively
  **non-stationary / random-walk**. Two of the four actually **diverge** at 240
  min (negative reversion).
- This is the **C028 failure mode reconfirmed** (half-life ≫ hold), and it is an
  important *positive* robustness finding: the genuine reversion is **specific to
  the no-arbitrage triangle**, NOT a generic property of any shared-leg cross
  combination. The triangle is pinned by no-arbitrage; the cointegration spread is
  not pinned and does not revert.

## 4. Reading

- **Existence is robust** to normalization, threshold, and (within the triangular
  family) is instrument-universal — the reversion is a stable, real structure.
- **The shorter-lookback collapse at 60 min** and the **front-loaded randomized-
  relationships z** both localize a large share of the effect in the short-horizon
  microstructure band; the durable long-horizon component is the JPY complex.
- **The shared-leg contrast** shows the genuine reversion is a no-arbitrage
  property, not a cointegration edge — and that the cointegration-spread RV idea
  (C028/S4-secondary) remains null (half-life ≫ hold).

---

## 5. Phase-6 reading (no verdict here)

The triangular reversion is **robustly real** across normalization and threshold
neighbours and is no-arb-specific (the shared-leg cointegration alternative does
not revert). But the robustness evidence also **sharpens the §11 picture**: the
short-lookback 60-min collapse and the horizon decay of the conservative null
concentrate much of the effect in the microstructure band, with a genuine slow
component only in the JPY complex. Phase 7 applies the frozen verdict map weighing
"real and robust" against "confined to the no-arb/microstructure band."

# Currency-Strength Factor — Null Comparison (Phase 5)

**Sprint:** `research-currency-strength-factor-validation-001` · Phase 5
**Status:** RESULT (descriptive; verdict deferred to Phase 7). Four frozen nulls
(protocol §10), **200 seeds** each, fixed seed sequence. Figures from committed
`docs/research/currency_strength/nulls.csv`.
**Date:** 2026-05-30.

The decisive statistic is `z = (observed_conditional_mean − null_mean) /
null_std` per **condition × horizon × null** (4 × 5 × 4 = **80 cells**). Frozen
bar: **|z| ≥ 2** to "clear"; isolated |z|≈2 over 80 cells is the
multiple-comparison **noise expectation**.

The four nulls (each breaks a different part of the strength→forward-return link):
- **Unconditional** — bootstrap over all currency-bars (is there just drift?).
- **Randomized ranks** — random currency instead of the ranked one.
- **Shuffled currencies** — permute currency identity vs its own forward return.
- **Matched timestamps** — **session-matched** random bars + random currency.

---

## 1. Matched-Z by condition × horizon, all four nulls

```
--- matched_timestamps (session-matched) ---   max|z| = 1.58
                    5     15    30    60    240
rapid_strengthen  -0.17  0.25 -0.18  0.13  1.04
rapid_weaken      -0.00 -1.58 -1.02 -0.88 -0.57
strongest         -0.10  0.62 -0.68  0.14 -0.19
weakest           -0.54  0.69  0.67 -0.50  0.07

--- randomized_ranks ---                        max|z| = 1.65
                    5     15    30    60    240
rapid_strengthen  -0.23  0.12 -0.26  0.33  1.13
rapid_weaken      -0.07 -1.65 -1.13 -0.68 -0.46
strongest         -0.19  0.51 -0.69  0.31 -0.05
weakest           -0.61  0.55  0.67 -0.29  0.19

--- shuffled_currencies ---                     max|z| = 1.17
                    5     15    30    60    240
rapid_strengthen  -0.13  0.05 -0.10  0.09  1.07
rapid_weaken      -0.07 -1.17 -1.11 -0.72 -0.63
strongest         -0.12  0.39 -0.60  0.13  0.07
weakest           -0.58  0.61  0.57 -0.72  0.13

--- unconditional ---                           max|z| = 1.53
                    5     15    30    60    240
rapid_strengthen  -0.20  0.26 -0.21  0.14  0.99
rapid_weaken      -0.01 -1.53 -0.97 -0.76 -0.48
strongest         -0.12  0.61 -0.61  0.16 -0.03
weakest           -0.59  0.68  0.61 -0.41  0.16
```

---

## 2. Do observed effects exceed null expectations?

**No — not in a single cell.**

- **Cells clearing |z| ≥ 2: 0 of 80.** The **global maximum |z| across all
  conditions, horizons, and all four nulls is 1.65** (randomized_ranks,
  rapid_weaken, 15 min).
- The four nulls **agree** with each other to within ~0.3 Z everywhere — the
  observed conditional means are statistically identical to randomized-rank,
  shuffled-currency, session-matched, and unconditional baselines alike. There is
  no part of the strength→return link whose removal changes the result, because
  there is no link.
- The largest tilt — `rapid_weaken` at 15–30 min (z ≈ −1.5 to −1.65) — is **below
  the |z| ≥ 2 bar**, does not persist to 60/240 min, and is the single most
  extreme of 80 cells (exactly where the noise maximum is expected to land).
- The **unconditional baseline is ≈ 0** (drift is negligible), and the conditional
  means sit on top of it — strength conditioning adds nothing over "pick a random
  currency at a random matched time."

## 3. Is replication/existence statistically meaningful?

**No.** A real cross-sectional factor would clear |z| ≥ 2 on **multiple coherent
cells under all four nulls** (e.g. strongest continues across 30/60/240 min). Here
**zero cells clear under any null**, the maximum is a lone sub-threshold
`rapid_weaken` blip, and it fails to persist. By the frozen multiple-comparison
rule, **0/80 clearing = no factor**: the observed effects are indistinguishable
from every null.

---

## 4. Phase-5 reading (no verdict here)

Cross-implied currency strength does **not** exceed null expectations on **any**
condition, horizon, or null — global max |z| = 1.65, **0/80 cells clear |z| ≥ 2**,
and all four nulls coincide. The factor is **statistically indistinguishable from
random** at the existence level. Combined with Phase 3 (near-zero means) and Phase
4 (no consistent sub-population), the null comparison is decisive for the verdict.
Phase 6 confirms the same under nearby lookback/aggregation definitions.

# C1 Cross-Replication — Null Comparison (Phase 3)

**Sprint:** `research-c1-cross-replication-screen-001` · Phase 3
**Status:** RESULT (descriptive; verdict deferred to Phase 5). Same null
methodology as the original C1 majors validation (frozen in the protocol §7).
All figures read directly from the committed `{cross}_c1_nulls.csv`.
**Date:** 2026-05-30.

The null framework has three reference points, identical to the majors run:
1. **Unconditional / random-placement baseline** (`rand_null_mean`) — what a
   random event of the same count earns; the "is the pair just drifting?" check.
2. **Random-null Z** (`rand_z`) — observed vs the random-placement distribution.
3. **Session-matched null** (`matched_null_mean/std`, `matched_z`) — pseudo-events
   drawn to match the C1 events' session/time-of-day mix, removing intraday
   structure as a confound. **`matched_z` is the decisive statistic** (as on the
   majors). 60 seeds.

---

## 1. C1_long — observed vs random-null vs matched-null

```
cross      h     obs   randMu  randZ   mNull   mStd     mZ
EUR_GBP   30   0.027  -0.009   0.27   0.017  0.119   0.09
EUR_GBP   60  -0.059  -0.026  -0.19  -0.010  0.157  -0.31
EUR_JPY   30  -0.421   0.091  -1.91   0.158  0.256  -2.26
EUR_JPY   60   0.162   0.130   0.08   0.218  0.390  -0.14
GBP_JPY   30  -0.416   0.180  -1.67   0.080  0.338  -1.47
GBP_JPY   60  -0.071   0.239  -0.62   0.179  0.391  -0.64
AUD_JPY   30  -0.125   0.033  -0.74   0.074  0.221  -0.90
AUD_JPY   60   0.045   0.128  -0.30   0.129  0.317  -0.27
NZD_JPY   30   0.121   0.018   0.55   0.054  0.193   0.35
NZD_JPY   60  -0.034   0.006  -0.15   0.109  0.257  -0.56
EUR_CHF   30  -0.028  -0.015  -0.08  -0.032  0.137   0.04
EUR_CHF   60  -0.089  -0.052  -0.20  -0.057  0.191  -0.17
GBP_CHF   30  -0.491  -0.009  -2.34  -0.066  0.206  -2.06
GBP_CHF   60  -0.774  -0.025  -2.61  -0.057  0.257  -2.79
EUR_AUD   30  -0.342  -0.033  -1.18  -0.045  0.255  -1.17
EUR_AUD   60  -0.328  -0.109  -0.60  -0.019  0.408  -0.76
```

---

## 2. Do observed effects exceed null expectations?

**Counting cells that clear |matched-Z| ≥ 2.0 (the frozen null-separation bar):**

| Horizon | Cross cells clearing |mZ|≥2 | Which |
|---------|-----------------------------|-------|
| 30 min | **2 / 8** | EUR_JPY (−2.26), GBP_CHF (−2.06) |
| 60 min | **1 / 8** | GBP_CHF (−2.79) |

- **Among the 4 REQUIRED crosses: exactly one cell clears the null, ever** —
  EUR_JPY at 30 min (−2.26). And that effect **does not survive to 60 min** (mZ60
  −0.14, sign flips positive). On the majors the effect *strengthened* 30→60; here
  the one required pair that clears at 30 min *reverses*.
- **GBP_CHF (optional) is the only pair clearing at 60 min** (mZ60 −2.79). It is a
  **single pair out of 8**. The pre-registered multiple-comparison rule (protocol
  §6) treats a lone clearing pair as **selection noise**: at |Z|≈2 over 8×2 = 16
  cells, ~0.7 false positives are expected by chance, so 1–2 isolated hits are
  exactly the null expectation.
- The **random-null Z** tells the same story: only EUR_JPY-30 (−1.91), GBP_CHF-30
  (−2.34) and GBP_CHF-60 (−2.61) are notable; everything else sits near zero.
- **Unconditional drift check:** `rand_null_mean` is ≈0 on every cross (|·| < 0.24
  pips), so the pairs are not simply drifting; but the **observed** C1 means are
  also ≈ the matched-null means on every required pair at 60 min — i.e. C1 events
  on the required crosses earn **what a session-matched random event earns.**

## 3. Is replication statistically meaningful?

**No — not on the required universe, and not cross-wide.**

- On the majors, EUR_USD and USD_JPY cleared |mZ60| ≈ 3.5–4.2 — two independent,
  liquid, *required-equivalent* pairs with a coherent strengthening profile. That
  is what "statistically meaningful replication" looked like.
- On the crosses, **zero required pairs clear |mZ| ≥ 2 at 60 min**, the single
  required 30-min hit (EUR_JPY) **reverses** by 60 min, and the only 60-min hit is
  **one optional pair** consistent with multiple-comparison noise.
- The matched-null standard deviations (0.12–0.41 pips) are *larger* than the
  observed C1 means on every required pair at 60 min, so the observed effects are
  **inside one standard deviation of the matched null** — statistically
  indistinguishable from "a session-matched random event."

## 4. Contrast with the majors null result (for the record)

| | Majors (EUR_USD / USD_JPY) | Required crosses |
|---|---|---|
| C1_long 60-min sign | negative 7/7 | 2/4 negative, magnitudes ≈0 |
| |mZ60| on liquid pairs | 4.21 / 3.55 | ≤ 0.64 |
| 30→60 behavior | **strengthens** | EUR_JPY **reverses** |
| Pairs clearing null (60m) | 2 (independent, required) | 0 required; 1 optional (noise) |

---

## 5. Phase-3 reading (no verdict here)

The observed cross effects **do not exceed null expectations** on the required
universe: the required crosses earn matched-null-equivalent returns at 60 min,
the lone required 30-min signal (EUR_JPY) is non-persistent, and the single
60-min null-clearing pair (GBP_CHF) is an isolated optional hit indistinguishable
from multiple-comparison noise. Replication is **not statistically meaningful**
by the frozen criteria. Phase 4 checks whether even the weak 30-min JPY-quote
tilt is stable across years/sessions/vol (without changing the factor); Phase 5
applies the frozen verdict map.

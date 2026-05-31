# C1 Cross-Replication — Result (Phase 2)

**Sprint:** `research-c1-cross-replication-screen-001` · Phase 2
**Status:** RESULT (descriptive; verdict deferred to Phase 5). Frozen `BASELINE`
spec applied unchanged to the 8 crosses. Every figure read **directly from the
committed CSVs** under `docs/research/c1_validation/` (artifact-first).
**Date:** 2026-05-30.

**Run:** `scripts/run_c1_factor_validation.py --pairs
EUR_GBP,EUR_JPY,GBP_JPY,AUD_JPY,NZD_JPY,EUR_CHF,GBP_CHF,EUR_AUD --null-seeds 60`
(local research-DB read authorized by the user; no trading APIs, no broker
credentials, no orders). Window 2021-05-26 → 2026-05-26, identical to the majors.
Cross artifacts: `{cross}_c1_events.csv`, `{cross}_c1_nulls.csv`,
`c1_cross_validation_meta.json`, `c1_cross_robustness.csv`. The majors' shared
`c1_robustness.csv` / `c1_validation_meta.json` were preserved (cross outputs
written to `c1_cross_*` names to avoid clobbering provenance).

The C1 definition was **not changed** in any way; only the instrument list
differs from the original majors run. No post-hoc adjustment was made.

---

## 1. C1_trend_cont_long — signed forward response by cross

(`mean30/60` = mean signed return in pips at 30/60 min; negative = reverts
*against* the bullish confluence — the C1 effect. `t` = parametric t-stat;
`pneg60` = P(signed return<0) at 60 min; `spr` = mean spread (pips);
`mZ30/60` = **session-matched null Z** — the decisive statistic.)

```
cross    req     n    mean30   t30   mean60   t60  pneg60  spr    mZ30   mZ60
EUR_GBP   Y   1361    0.027   0.17  -0.059  -0.27   0.518  1.63   0.09  -0.31
EUR_JPY   Y   2064   -0.421  -1.60  +0.162   0.44   0.481  2.41  -2.26  -0.14
GBP_JPY   Y   2224   -0.416  -1.37  -0.071  -0.17   0.490  3.72  -1.47  -0.64
AUD_JPY   Y   2076   -0.125  -0.66  +0.045   0.16   0.491  2.23  -0.90  -0.27
NZD_JPY   o   1916    0.121   0.69  -0.034  -0.13   0.491  2.71   0.35  -0.56
EUR_CHF   o   1298   -0.028  -0.16  -0.089  -0.41   0.486  1.98   0.04  -0.17
GBP_CHF   o   1733   -0.491  -2.45  -0.774  -2.78   0.521  2.61  -2.06  -2.79
EUR_AUD   o   1617   -0.342  -1.01  -0.328  -0.72   0.520  3.24  -1.17  -0.76
```

**Majors reference (C1_long, from committed `C1_CROSS_PAIR_STUDY.md`):**
EUR_USD mean60 **−1.169** mZ60 **−4.21**; USD_JPY **−1.136** / **−3.55**;
GBP_USD −0.651 / −1.85; then NZD/AUD/CHF/CAD within-null. 60-min sign **negative
on 7/7 majors**, strengthening from 30→60 on the two significant pairs.

## 2. C1_trend_cont_short (the mirror) — signed forward response by cross

```
cross    req     n    mean30   t30   mean60   t60  pneg60  spr    mZ30   mZ60
EUR_GBP   Y   1852   -0.164  -1.50  -0.038  -0.25   0.500  1.67  -1.51  -0.06
EUR_JPY   Y   1266   -0.572  -1.19  -1.324  -2.02   0.530  2.43  -1.29  -2.05
GBP_JPY   Y   1317   -0.103  -0.21  -0.193  -0.26   0.527  3.76   0.24   0.36
AUD_JPY   Y   1411   -0.448  -1.45  -0.556  -1.30   0.540  2.32  -1.70  -1.31
NZD_JPY   o   1449   -0.213  -0.85  +0.217   0.60   0.508  2.77  -0.75   0.94
EUR_CHF   o   1805   -0.392  -2.76  -0.260  -1.34   0.519  1.85  -3.08  -1.67
GBP_CHF   o   1848    0.177   0.95  +0.008   0.03   0.519  2.66   0.95  -0.11
EUR_AUD   o   1834   -0.594  -2.31  -0.686  -1.89   0.512  3.27  -2.13  -1.94
```

---

## 3. Answers to the Phase-2 questions

### Which crosses replicate?

Using the frozen per-pair criteria (C1_long 60-min **negative** AND clears the
matched null at 30 or 60 min, |mZ| ≥ 2):

- **None of the 4 REQUIRED crosses replicates cleanly.** EUR_JPY clears the null
  at **30 min** (mZ30 −2.26, correctly negative) but its sign **flips positive**
  by 60 min (+0.162) — the opposite of the majors, where the effect *strengthened*
  from 30→60. EUR_GBP, GBP_JPY, AUD_JPY are all within-null (|mZ| < 2 at both
  horizons) and two of them (EUR_GBP, AUD_JPY → wait, EUR_GBP −0.059 is negative;
  AUD_JPY +0.045) sit at essentially zero.
- **One OPTIONAL cross, GBP_CHF, is the only pair clearing the null at 60 min**
  (mean60 −0.774, mZ60 −2.79; also mZ30 −2.06). It is a **single pair out of 8**
  → under the pre-registered multiple-comparison rule (§6 of the protocol) a lone
  pair is treated as **selection noise, not replication.**

### Which do not?

EUR_GBP, GBP_JPY, AUD_JPY, NZD_JPY, EUR_CHF, EUR_AUD are within-null at 60 min
(|mZ60| ≤ 0.76). EUR_JPY does not replicate the *60-min* effect (sign flips).
GBP_CHF clears the null but as an isolated pair (noise).

### Does sign remain stable?

**No — the majors' hallmark sign-universality breaks.** On majors C1_long was
**negative 7/7** at 60 min. On crosses, the 60-min sign is **2/4 positive on the
required set** (EUR_JPY +0.162, AUD_JPY +0.045) and 6/8 negative overall — but the
"negatives" are mostly indistinguishable from zero (|mean60| < 0.1 on 4 of them).
There is a **weak negative 30-min tilt on the JPY-quote crosses** (EUR_JPY −0.421,
GBP_JPY −0.416, AUD_JPY −0.125 all negative at 30 min) that **does not persist to
60 min** — the reverse of the majors' 30→60 strengthening.

### Does the effect weaken materially?

**Yes — by roughly an order of magnitude.** The two significant majors had
|mean60| ≈ 1.1–1.2 pips with |mZ60| 3.5–4.2. The required crosses have |mean60|
≈ 0.04–0.16 pips with |mZ60| ≤ 0.64. The cross effect is **~10× smaller** and
sits inside the null band on every required pair at 60 min. Even GBP_CHF's
−0.774 / −2.79 is below the strongest majors and is a single optional pair.

---

## 4. Descriptive summary (no verdict here)

- The **signature majors result** — C1_long sign-universal negative, strengthening
  to 60 min, strongly null-clearing on the liquid pairs — **does not appear on the
  required crosses.**
- A **weak, horizon-inconsistent 30-min reversion tilt** exists on the JPY-quote
  crosses (EUR_JPY/GBP_JPY/AUD_JPY negative at 30 min; EUR_JPY clears null at 30
  but reverses by 60).
- The **only convincing 60-min null-clearing pair (GBP_CHF) is a single optional
  cross** → selection noise by the frozen rule.
- The short-side mirror shows the same shape: scattered, EUR_JPY/EUR_AUD-leaning
  negative, GBP_JPY/NZD_JPY/GBP_CHF not — no coherent cross-wide effect.

Phase 3 formally compares these observations to the unconditional and
session-matched nulls; Phase 4 checks year/session/vol stability; Phase 5 applies
the **frozen verdict map** mechanically. **Tradability is not evaluated anywhere
(out of scope); cost columns are descriptive only.**

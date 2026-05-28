# USD_JPY London Compression-Continuation — Robustness & Falsification

**Sprint:** `usdjpy-london-compression-continuation-confirmation-001` · **Phase 3**
**Source:** `research/usdjpy_london_compression_continuation/confirmation_summary.json`
(+ supplementary long/short and session-purity checks).

> DIAGNOSTIC ONLY. These checks falsify, they do not endorse. TEST sealed throughout.

The eleven required robustness/falsification checks, against the locked lead:

### 1. Train vs validation stability
At **no-stop base cost** both splits are positive (h16 +1.04/+3.04, h32 +2.21/+6.12),
but the validation magnitude is 2–3× train and **neither survives realism** (below). The
sign is *not* stable once stops/conservative cost/years are considered. **Fragile.**

### 2. h16 vs h32 consistency
Both horizons are positive only at no-stop. Both go **strongly negative with any stop**
(h16 −3.2 to −5.9; h32 −2.7 to −7.7 per split). Consistent — consistently fails. **Fail.**

### 3. Long vs short (no-stop, base)
Both directions positive at no-stop base (h32 long +4.4 / short +3.5; h16 long +0.96 /
short +3.08), so the no-stop number is not a one-sided artifact — but this does not
rescue it, because the stop test kills both directions. **Not decisive either way.**

### 4. Year-by-year robustness (base cost)
The decisive falsifier. No-stop base, mean pips/trade by year:

| year (split) | h16 | h32 |
|---|---|---|
| 2021 (train) | **−4.10** | **−4.57** |
| 2022 (train) | +4.12 | +7.85 |
| 2023 (train) | +0.07 | −1.48 |
| 2024 (val) | +6.15 | +8.57 |
| 2025 (val) | **−5.61** | −0.60 |

The "edge" lives almost entirely in **2022 and 2024** (strong USD_JPY trend years) and is
**negative or flat in 2021, 2023, 2025**. The sign is **not** consistent across years
within either split → a trend-regime exposure, not a stable effect. **Fail (kill #8).**

### 5. Exclude extreme-spread periods
Not separately needed: the cost variants already stress this — the **conservative** cost
(p90 London spread 1.9 + 2.0 slippage = 5.8 round-trip) flips h16 train **negative**
(−0.65) and leaves the rest thin. The effect does not have spread headroom. **Fail at
conservative cost (kill #2).**

### 6. Rollover / off-hours contamination
**None possible by construction:** the locked definition is London-session-only; the
simulated trades contain exactly one session bucket (`london`) — verified. Rollover and
off-hours (the cost-toxic buckets) are excluded. **Clean.**

### 7. Dependence on a few outlier trades
Dropping the top-5 trades by |pips| leaves the no-stop base means positive (h16 trimmed
+1.84/+2.72; h32 +3.82/+5.71), so it is **not** literally 5 outliers — but the year
breakdown (#4) shows it is a **whole-regime** concentration (2022/2024), which is the
more dangerous form of non-robustness. **Fail via regime concentration.**

### 8. Concentration in a tiny sample
No — n ≈ 690–850 per split (≥ the 150 floor). Sample size is adequate; the problem is not
sample size but realism and regime dependence. **Pass (sample), irrelevant to verdict.**

### 9. Survives base and conservative cost
- Base, no-stop: positive (but fails stops/haircut/years).
- **Conservative, no-stop: h16 train −0.65** (fail); h32 train +0.33 (marginal),
  val +4.26. The margin is gone. **Fail (kill #2).**

### 10. Stop model reduces or destroys the effect
**Destroys it.** Every predeclared intrabar protective stop (range 1.0×, range 1.5×,
ATR 1.0×) turns the lead **strongly negative on both splits at both horizons** (−2.7 to
−7.7 pips/trade). The no-stop "profit" is entirely held-through-adverse-excursion risk.
**Fail (kill #3, decisive).**

### 11. TEST not touched
Confirmed. The simulator hard-bounds the load to `< 2025-07-01`; no 2025-07+ data was
read. **Clean.**

---

## Multiple-testing haircut

The lead was 1 of 12 cells (6 sessions × 2 horizons) searched in the prior sprint.
Bonferroni ×12 on per-trade net pips (base cost, no stop):

- h16: train adjusted-p = 1.0, val adjusted-p = 0.977 → **fails both splits.**
- h32: train adjusted-p = **1.0** (not significant), val adjusted-p = 0.041 → **fails on
  train.**
- Only h32 at the *optimistic* (unrealistic) cost passes the haircut on both splits.

**The haircut removes significance** in every realistic configuration. **Fail (kill #6).**

---

## Summary

| check | result |
|---|---|
| train/val stability | fragile |
| h16/h32 consistency | consistently fails under realism |
| long/short | both positive at no-stop only (not decisive) |
| year robustness | **FAIL** — trend-regime artifact (2022/2024) |
| extreme spread | **FAIL** — no headroom at conservative cost |
| rollover/off-hours contamination | clean (London-only) |
| outlier dependence | regime-concentrated (fail) |
| tiny-sample | pass (n adequate) |
| base/conservative cost | **FAIL** at conservative (h16 train −0.65) |
| stop model | **FAIL (decisive)** — every stop turns it −3 to −8 |
| TEST untouched | clean |
| multiple-testing haircut | **FAIL** — removes significance in realistic configs |

The lead fails the great majority of falsification checks, including all of the decisive
ones (stops, conservative cost, haircut, year robustness). Proceed to the readiness
decision (`USDJPY_LONDON_COMPRESSION_CONTINUATION_READINESS_DECISION.md`).

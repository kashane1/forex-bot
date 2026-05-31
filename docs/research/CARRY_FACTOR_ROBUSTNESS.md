# Carry Factor — Robustness (Phase 6)

**Sprint:** `research-carry-factor-validation-001` · Phase 6
**Type:** robustness (stability of the primary result to nearby specs) — **not**
optimization. The verdict is **not** re-selected from the best cell. Figures from
`research/carry/factor_validation/carry_factor_validation.json`. Gross only.
**Date:** 2026-05-31.

All cells are the **3-month total gross mean** of the primary (currency) layer unless
noted. Primary = currency HML-3, lag-1, rate-level, equal-weight = **+0.00745**.

---

## 1. Robustness grid

| Axis | Spec | 3m total mean | vs primary |
|---|---|---:|---|
| **Basket size k** | HML-2 | +0.00590 | weaker, same sign |
| | **HML-3 (primary)** | **+0.00745** | — |
| **Weighting** | rank-weighted | +0.00619 | weaker, same sign |
| **Implementation lag** | lag 0m | +0.00754 | ≈ primary |
| | **lag 1m (primary)** | +0.00745 | — |
| | lag 2m | +0.00705 | ≈ primary |
| **Ranking variable** | rate level (primary) | +0.00745 | — |
| | **rate *change* (carry momentum)** | **−0.00137** | **sign flips — negative** |
| **Instrument layer** | HML-3 | +0.01569 | larger (JPY-cross concentration) |
| | HML-4 | +0.01325 | larger |
| | HML-5 | +0.01418 | larger |

## 2. What is robust

- **Sign and rough magnitude are stable** to basket size (k=2/3), weighting (equal vs
  rank), and implementation lag (0/1/2 months) — all land in **+0.0059…+0.0075**. The
  static carry tilt is not an artifact of one knob setting, and the 1-month lag (chosen
  for lookahead safety) costs essentially nothing vs lag-0, so the result is not a
  look-ahead artifact either.
- The instrument layer keeps the sign (larger, but for the non-independent reason in
  Phase 4 — it is more concentrated short-JPY, not broader).

## 3. What is fragile (the decision-relevant failures)

- **Carry-momentum ranking flips the sign to −0.00137.** Ranking currencies by the
  *change* in their rate (instead of the level) earns a small **negative** gross return.
  This confirms Phase 3/5: the premium lives **only** in the static *level* tilt; there is
  **no** dynamic/timing version of carry that works here. A factor whose only working form
  is the constant tilt is, by construction, untimed and risk-premium-like — not an alpha
  signal.
- Combined with the **drop-JPY → +0.0003** result (Phase 4), the "robust" magnitude is
  robust *only because every nearby spec keeps the same dominant JPY short*. The
  robustness is the robustness of one bet, re-expressed.

## 4. Robustness verdict

The primary result is **specification-robust in sign/magnitude across the *static-level*
neighbourhood** (k, weighting, lag) — it is **not** a single-cell fluke or a lookahead
artifact. But it is **not robust across the mechanism**: it vanishes without JPY and
**reverses** under the only dynamic ranking tried. The stability is the stability of a
static, single-name tilt — consistent with *real-but-weak*, and inconsistent with a
robust, broad, timeable factor that would merit front-gate status.

(Robustness only — no spec here was selected to maximise the result; the primary cell was
fixed in the Phase-1 protocol before any return was computed.)

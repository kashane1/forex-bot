# Carry Factor — Null Comparison (Phase 5)

**Sprint:** `research-carry-factor-validation-001` · Phase 5
**Type:** matched-null separation for the **primary cell** (currency HML-3, total gross
return, 3-month horizon). 2000 draws each, seed 20260531. Figures from
`research/carry/factor_validation/carry_factor_validation.json`. Gross only.
**Date:** 2026-05-31.

Observed primary mean = **+0.007445**. Each null preserves the realised return panel and
breaks only the carry→return link (protocol §8). The factor must beat **all four**.

---

## 1. Results

| Null | Null mean | matched-Z | one-sided p | Beats null? |
|---|---:|---:|---:|---|
| **Randomized carry ranks** | −0.00014 | **+2.78** | 0.0035 | ✅ yes |
| **Matched random baskets** | +0.00000 | **+2.68** | 0.0025 | ✅ yes |
| **Shuffled-timestamp carry** | +0.00689 | **+0.72** | 0.2395 | ❌ **no** |
| **Unconditional (long non-USD vs USD)** | −0.00822 | — (Δ=+0.0157) | — | ✅ yes |

**The primary cell clears three of four nulls but fails the shuffled-timestamp null.**

## 2. What each result means

- **Randomized ranks (Z=2.78, beats):** permuting which currency gets which rank destroys
  the carry information; the real book earns +0.74% where random rank-assignment earns
  ≈0. So *the identity of the long/short legs matters* — the book is not just a random
  dollar-neutral basket.
- **Matched random baskets (Z=2.68, beats):** random equal-size long/short baskets earn
  ≈0; the carry-chosen baskets earn more. Same message — carry selection ≠ random
  selection.
- **Unconditional baseline (beats by +0.0157):** the carry-naive "long all non-USD vs USD"
  book actually *lost* (−0.82%) over the window; carry-sorting adds materially over not
  sorting.
- **Shuffled-timestamp (Z=0.72, FAILS):** permuting the *months* of the carry signal
  leaves the HML mean almost unchanged (null mean +0.00689 ≈ observed +0.00745). The
  observed result is **inside** this null.

## 3. Why the shuffled-timestamp failure is a *characterisation*, not a refutation

The carry ranking has month-over-month Spearman **0.984** — it is nearly static (Phase
2/3). Permuting its timestamps therefore re-assigns essentially the **same** long-JPY-
funded / short-funders book to different months; the portfolio barely changes, so its
mean return barely changes. The shuffled-timestamp null does not (and for a near-static
signal *cannot*) distinguish the real book from itself.

The honest interpretation is precise:

> The carry premium here carries **no timing information** — it is a **constant
> cross-sectional tilt**, not a signal that says *when* to be on. Beating the
> randomized/matched nulls but not the shuffled-timestamp null is the statistical
> signature of a **static risk-premium tilt**, which is exactly what the academic carry
> factor is. It is not evidence of spuriousness; it is evidence of *staticness*.

This matters for the verdict two ways: (a) it rules out any *timing* edge, and (b) under
the protocol's pre-registered bar ("must clear matched-Z ≥ 2 against **every** null"), the
primary cell **does not meet the FRONT_GATE_CANDIDATE threshold** — by our own frozen
rule, before any post-hoc reasoning.

## 4. Multiple-comparison control across the horizon family

Holm–Bonferroni on the randomized-ranks p-values for currency HML-3 total across the four
horizons:

| Horizon | p (randomized null) | Holm threshold | Reject null? |
|---:|---:|---:|---|
| 6m | 0.0000 | 0.0125 | ✅ |
| 12m | 0.0000 | 0.0167 | ✅ |
| 3m | 0.0020 | 0.0250 | ✅ |
| 1m | 0.0630 | 0.0500 | ❌ |

Versus the *randomized* null the 3/6/12-month cells survive Holm adjustment. But this is
the **weak** null — it is beaten by the mechanical accrual term (random ranks don't
harvest the rate gap; the real book does). Surviving it confirms *"booking real rate
differentials beats booking random ones,"* which is mechanically guaranteed and is **not**
the predictive question.

## 5. Net null reading

- Carry-selection beats **random/identity** nulls and the unconditional baseline → there
  is a genuine, carry-specific gross tilt.
- It does **not** separate from the **timing** null → the tilt is static, with no
  time-varying alpha; and by the frozen all-nulls bar it falls short of the front-gate
  threshold.
- The nulls it beats are beaten via the **accrual** term (the part financing reclaims),
  not via spot prediction (which Phase 3 showed is null).

→ Consistent with a real-but-weak static premium, not a front-gate factor. Phase 6 checks
robustness; Phase 7 renders the verdict.

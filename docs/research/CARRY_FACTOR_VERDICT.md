# Carry Factor — Verdict (Phase 7)

**Sprint:** `research-carry-factor-validation-001` · Phase 7
**Type:** factor verdict. One label, chosen from the frozen taxonomy. Gross only — this
verdict makes **no** tradability claim and authorizes **no** strategy.
**Date:** 2026-05-31.

---

# Verdict: `FACTOR_REAL_BUT_WEAK`

A **genuine gross cross-sectional carry premium exists** in the research universe over
2021–2026 — it is correctly signed, positive in every year and regime, robust across
basket size / weighting / lag, and it separates from the carry-*identity* nulls
(randomized ranks Z=2.78, matched random Z=2.68) and beats the carry-naive unconditional
baseline by +1.57%/quarter. **But it is too weak, too narrow, and too purely mechanical
to be a front-gate candidate.**

## 1. Why `REAL` (it is not noise)

- Primary cell (currency HML-3, total, 3m) mean **+0.74%/quarter**, sign-consistent
  (0.70), positive every year (+0.04%…+2.60%) and every rate/risk regime.
- Beats randomized-rank and matched-random nulls after Holm adjustment at 3/6/12m, and
  beats the unconditional baseline → the long/short **identity** carries real information.
- Sign/magnitude stable across k∈{2,3}, equal/rank weighting, and lag∈{0,1,2}m — not a
  single-cell or lookahead artifact.

## 2. Why `WEAK` (it cannot graduate)

1. **No predictive power — the premium is mechanical accrual, not forecasting.** The
   spot-only leg (the genuine UIP-failure edge) is **statistically zero at every horizon**
   (t = 0.12 / 0.10 / 0.01 / −0.27), negative at 12m. ~94% of the 3m total is just the
   booked interbank rate differential. The sprint's actual question — *statistically
   meaningful gross **predictive** power* — is answered **no** for the spot-predictive
   component.
2. **Marginal significance.** Primary 3m NW-HAC t = **1.68** (<2). Only the 12m total
   clears t=2, on ~**4 independent** windows — the least trustworthy cell.
3. **Single-name dependence.** Drop-JPY collapses the premium **+0.0075 → +0.0003**. It is
   the 2022–26 yen short, not a broad cross-section; the high-yield longs did not
   appreciate and the other funder (CHF) contradicts the carry sign.
4. **No timing content.** Fails the shuffled-timestamp null (Z=0.72) and the carry-
   *momentum* ranking flips negative (−0.0014): the effect lives **only** in the static
   level tilt. A constant, untimed tilt is a risk premium, not an alpha signal.
5. **Crash-untested.** The window holds one carry regime and **no** carry crash — the very
   risk that defeats carry is unsampled, so even the static premium is optimistically
   measured.

## 3. Why not the other two labels

- **Not `FACTOR_FRONT_GATE_CANDIDATE`:** by the **frozen** Phase-1 bar it must clear
  matched-Z ≥ 2 against **every** null and survive robustness; it fails the shuffled-
  timestamp null, has a null spot-predictive leg, depends on one currency, and reverses
  under the only dynamic spec. It does **not** merit financing-aware evaluation as a
  *strategy* (see Phase 8). Front-gate is off the table by pre-registration, not
  post-hoc.
- **Not `FACTOR_REJECTED`:** the premium is not noise and not unstable — it is correctly
  signed, consistent across years/regimes/specs, and beats the identity and unconditional
  nulls. Calling it rejected would understate a genuine (if mechanical and narrow) gross
  effect, and would mis-describe carry, which is a real economic risk premium.

`REAL_BUT_WEAK` is the honest middle: a real gross premium that **survives validation and
the discriminating nulls but lacks the magnitude, breadth, predictive content, and timing
robustness** to be a tradable-edge candidate.

## 4. The economic crux (governs Phase 8)

The part of the premium that is positive (**accrual** of the rate gap) is **exactly** the
part a retail broker reclaims as financing — the prior C031 result put OANDA financing at
**≈4× spread**, i.e. a large fraction of the very differential being booked. The part that
would *survive* financing (a **spot-predictive residual**) is **absent** (Phase 3). So the
gross premium is, to first order, the financing charge in disguise.

> A gross premium that is entirely the to-be-charged accrual, with no spot-predictive
> residual underneath, is the textbook setup for `FINANCING_DEFEATED` once real costs are
> applied — the C031 / S4 failure mode.

## 5. Hard-rule compliance

No campaign created. No strategy, entry/exit, or front gate created. Nothing approved.
Paper/demo/live remain blocked. No broker API called; no OANDA financing data used. Carry
evaluated **gross only**; definitions unchanged after data review. `approved: []`.

# Carry Factor — Response Study (Phase 3)

**Sprint:** `research-carry-factor-validation-001` · Phase 3
**Type:** gross forward-return response. All figures read from
`research/carry/factor_validation/carry_factor_validation.json` (seed 20260531).
Gross only — no cost, no financing, no approval.
**Date:** 2026-05-31.

Measures the forward return of the frozen carry exposures (Phase 2) at the
pre-registered horizons. Per the protocol the **primary metric** is the **total gross
return** (spot + accrued interbank carry) and the **secondary** is **spot-only** (the
pure UIP-failure component). The decisive cell is **currency HML-3, total, 3-month**.

---

## 1. Headline — currency HML-3 (the primary book)

| Horizon | Total mean | NW-HAC *t* | Sign-consistency | n (indep.) | **Spot-only mean** | Spot *t* | Carry accrual |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1m | +0.00256 | +1.39 | 0.66 | 59 (59) | **+0.00023** | +0.12 | +0.00233 |
| **3m** | **+0.00745** | **+1.68** | **0.70** | 57 (19) | **+0.00046** | **+0.10** | +0.00699 |
| 6m | +0.01412 | +1.79 | 0.69 | 54 (9) | +0.00012 | +0.01 | +0.01400 |
| 12m | +0.02443 | +2.30 | 0.69 | 48 (4) | **−0.00335** | −0.27 | +0.02777 |

*(Total return per holding period, log units; "n (indep.)" is the overlapping count and
the non-overlapping count that bounds power.)*

## 2. The decisive reading: the premium is **mechanical accrual, not prediction**

Decompose every cell into its two components:

- **Carry accrual** (booking the interbank rate differential) is the entire premium:
  at 3m it is **+0.00699 of the +0.00745 total (94%)**; at 12m the accrual is +0.02777
  while the total is only +0.02443.
- **Spot-only** return — the part the market is *not* mechanically handing you, i.e. the
  genuine *predictive* edge H1 asks about — is **statistically zero at every horizon**:
  means +0.00023, +0.00046, +0.00012, **−0.00335**, with NW-HAC *t* of **+0.12, +0.10,
  +0.01, −0.27**. At the 12-month horizon it is **negative**: high-carry currencies, far
  from appreciating, drift slightly *down*.

> **High carry does not forecast spot direction in this universe/window.** The gross
> carry "premium" is the accounting accrual of the rate gap; it is not predictive power.

This is the single most important result of the sprint and it directly governs the
verdict: the quantity that is positive (accrual) is precisely the quantity a real broker
charges back as financing (the C031 ≈4× wall), and the quantity that would *survive*
financing (a spot-predictive residual) is **absent**.

## 3. Significance & persistence

- The primary 3-month cell's total NW-HAC *t* = **1.68** — it does **not** clear the
  conventional |t|≥2 bar. Only the 12-month total clears it (*t*=2.30), and that horizon
  has just **~4 independent** (non-overlapping) windows — the weakest, most
  overlap-inflated cell, so its significance is the least trustworthy, not the most.
- **Sign consistency** is steady (0.66–0.70 of rebalances positive) — the book is
  *usually* up, consistent with a real but small static premium.
- **Persistence:** month-over-month carry-rank Spearman is **0.984** — the signal is
  almost perfectly static. The "premium" is therefore a *constant tilt*, not a
  time-varying signal (this is why the timing null in Phase 5 is degenerate).

## 4. Scheme & layer variants (corroboration, not the verdict)

3-month total mean across constructions (full grid in Phase 6):

| Construction | 3m total mean |
|---|---:|
| Currency HML-3 (primary) | +0.00745 |
| Currency HML-2 | +0.00590 |
| Currency rank-weighted | +0.00619 |
| Instrument HML-4 | +0.01325 |
| Unconditional (long non-USD vs USD) | **−0.00822** |

Carry-sorting adds **+0.0157** over the carry-naive "long-everything-vs-USD" baseline at
3m — so the *sorting* is not vacuous. The instrument layer shows a larger number only
because it concentrates the same short-JPY exposure (JPY-crosses dominate its longs); it
is not independent confirmation.

## 5. Honest limitations (pre-registered)

- ~60 monthly observations; the longer horizons have **single-digit independent windows**
  → low power, and overlapping returns inflate naive significance (corrected here with
  NW-HAC and reported as independent counts).
- The window contains **one** carry regime (the 2022–26 USD-strong / yen-weak era) and
  **no** carry crash — the property most likely to defeat carry is under-sampled.
- Gross only: **no** spread/financing charged. A positive gross total is *un-tradable on
  its own* and is reported as such.

→ Phase 4 tests whether even this accrual-driven, marginally-significant premium is
*broad* or the artifact of a single currency/episode.

# Programme Lessons Learned

**Sprint:** `research-cross-factor-programme-synthesis-001` · Phase 2
**Type:** retrospective synthesis. Docs-only.
**Date:** 2026-05-30.

What the whole programme taught us — assumptions that proved wrong, assumptions
that held, and the recurring failure / cost / data patterns. Grounded in the
Phase-1 inventory.

---

## 1. Assumptions that proved WRONG

1. **"Breadth (non-USD crosses) might unlock an edge."** It did unlock genuine
   *structure* (S2 showed a real multi-currency field; S4 found real no-arb
   reversion) — but **every effect remained sub-cost-band.** Breadth was not the
   binding constraint; assuming it might be was wrong. **Cost is the wall.**
2. **"The one genuine factor (C1) reflects a real market mechanism."** C1 was
   sign-universal on 7 USD majors, which *looked* like a robust law. The cross
   replication showed its significant magnitude was a **USD-regime artifact** that
   did **not** generalize. Sign-universality across collinear instruments is **not**
   evidence of generality.
3. **"Cross-sectional currency strength should carry directional information."** A
   reasonable prior (currency-strength meters are widely used). S2 showed the
   strength vector is real and breadth-diverse but **carries no forward
   predictability** — strength *persists* (mechanically) yet does not *predict*.
4. **"Relative-value/cointegration spreads between related crosses should revert."**
   The shared-leg cointegration spreads turned out **non-stationary** (half-life
   7k–27k bars). Only the **no-arbitrage triangle** reverts — and only within the
   cost band. Economic relatedness ≠ tradeable cointegration.
5. **"A better clock (range/volatility bars) might surface an edge time bars
   missed."** It did not — alt bars are a *sampling* choice, not an edge source
   (H16/H03/C029). No public OOS non-time-bar spot-FX edge was found in the
   literature either.

## 2. Assumptions that proved CORRECT

1. **"This venue is structurally cost-defeated."** Stated in the majors-era corpus
   review; **every** subsequent result confirmed it, including on the cheaper-where-
   tightest crosses. The two-sided squeeze (spread wall for fast, financing wall for
   slow) held universally.
2. **"Pre-registration + matched-null + cost-realism gates are essential."** They
   repeatedly caught would-be false positives (C028 selection noise; S4's no-arb
   artifact test correctly down-graded a real-looking reversion to within-band).
   The discipline worked exactly as designed.
3. **"Crosses add breadth, not cost/history/microstructure relief."** Pre-stated in
   the cross feasibility study; the measured cost baseline and S1–S5 confirmed it
   precisely.
4. **"Replication on non-collinear data is the right test for a discovered factor."**
   It cleanly resolved the C1 residual-USD question (→ artifact). Independent
   replication is decisive.
5. **"The platform is not the bottleneck."** Infra/parity/lab work was sound; the
   project was never again code-blocked. Correct.

## 3. Recurring failure modes

- **Cost-defeat of genuine gross effects.** The single most common outcome: an
  effect exists gross (C1, C029, S4) but is smaller than the round-trip spread.
- **Within-null / no-effect.** Directional and cross-sectional *prediction*
  (S2/S3/H16/H03/C016) simply is not present at intraday horizons on this venue.
- **USD-regime artifacts masquerading as factors.** C1's magnitude; C016/C031
  collapsing to "a structural USD bet." Collinearity inflates apparent robustness.
- **Selection noise from best-of-N.** C028 (spread mining) — fixed in S4 by
  pre-naming economically-motivated relationships.
- **Microstructure/staleness mistaken for reversion.** S4's non-JPY triangles
  (half-life ≤1 bar) — caught by the pre-registered artifact test.

## 4. Recurring cost issues

- **Spread wall (fast signals):** gross edges of 1–3 pips vs same-order round-trip
  cost. Crosses are **wider + fatter-tailed** than majors, so this wall is *higher*,
  not lower.
- **Financing wall (slow signals):** C031 found financing ≈**4× spread**; overnight
  carry-style holding is expensive on this retail venue.
- **Slippage worst where signal is strongest:** wide-spread high-vol bars carry both
  the biggest moves and the biggest costs.
- **Sub-cost-band genuine structure:** S4's reversion is ~**10× inside** the no-arb
  spread band — real structure that retail costs swallow whole.

## 5. Recurring data limitations

- **~5–6.4 years only:** underpowers slow / regime / macro signals (C031, macro
  context).
- **Tick-count "volume" is a proxy:** true microstructure (order flow, L2) is
  absent — participation/imbalance hypotheses are not honestly testable.
- **No real financing/rate leg (until now partially):** carry was **data-blocked**
  for the entire programme; only the cross expansion added real carry *pairs*, and
  real *swap rates* are still un-ingested.
- **Single venue, single vendor:** all spreads/financing are OANDA practice; no
  cross-venue or institutional-cost comparison.
- **Mid-price, retail spreads:** the cost band that defeats every genuine effect is
  a *retail* band; institutional execution is a different regime (relevant to S4).

## 6. The meta-lesson

**The programme's bottleneck migrated and then stabilized on cost.** Early on it
looked like *idea quality* (try more families); the cross expansion proved it was
not — genuine structure exists (S2 field, S4 no-arb factor) and is still sub-cost.
The binding constraints are now precisely identified: **retail transaction cost**,
**missing financing data** (for the one untested mechanism), and **single-venue /
short-history / no-true-microstructure** data limits. Future effort should attack a
**constraint** (a different return source that bypasses spread capture, or a
different cost/data regime) — **not** mine another family on the same venue.

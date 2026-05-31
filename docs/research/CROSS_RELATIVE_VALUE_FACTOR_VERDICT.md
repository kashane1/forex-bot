# Cross Relative-Value — Factor Verdict (Phase 7)

**Sprint:** `research-cross-relative-value-factor-validation-001` · Phase 7
**Type:** verdict. The **frozen verdict map** (protocol §14) is applied
mechanically to the Phase 2–6 evidence, including the §11 no-arb/microstructure
artifact test. The factor definition was never altered after results were observed.
**Date:** 2026-05-30.

---

## Verdict

# `FACTOR_REAL_BUT_WEAK`

Cross triangular no-arbitrage relative-value structure **genuinely exists** and its
deviations **revert** — strongly, broadly, stably, and far beyond all four nulls.
But the reversion is **confined to the no-arbitrage / microstructure band**:
≈0.4–0.5 bp against a ≈5 bp triangle cost band (~10× inside), front-loaded into the
first 5 minutes, with 4 of 8 relationships reverting in ≤1 bar (stale-quote
signature). It is the programme's **first real factor** — and it is **too weak
(within-band) to merit a front-gate screen.**

---

## How the frozen criteria resolve

### Not `FACTOR_REJECTED`
- **Not within null:** 20/20 null cells clear |z| ≥ 2; the conservative
  randomized-relationships null clears at every horizon (Phase 5). Decisively real.
- **Not sign-incoherent / single-relationship:** all 8 relationships revert
  positively at every horizon, P(reverts) 0.87–0.98, stable across all years and
  sessions (Phase 4). The broadest, most stable effect the programme has produced.
- **Not *entirely* a ≤1-bar artifact:** the 4 JPY crosses have genuine multi-bar
  AR(1) half-lives (4.8–9.6 bars) and *progressive* reversion over horizons
  (Phase 2/3). So the REJECTED "entirely instantaneous / half-life ≤1 bar"
  criterion is not met.

### Not `FACTOR_FRONT_GATE_CANDIDATE`
The candidate bar requires passing the **§11 artifact test** (progressive reversion
over horizons, half-life > 1 bar, **not confined to the no-arb band**). It fails on
the third clause, decisively, and partly on the first:
- **Confined to the no-arb band:** residual std 0.23–0.81 bp and reversion
  ≈0.4–0.5 bp are **~6–25× inside** the triangle's summed-spread band (4.25–7.18
  bp). The entire phenomenon lives an order of magnitude **within** the
  transaction-cost band (Phase 2 §4).
- **Front-loaded horizon profile:** ~78% of the pooled reversion is realized in the
  first 5-min bar; the conservative randomized-relationships z is largest at 5 min
  (9.48) and decays to ~2.6 by 60 min (Phase 5 §3); the 2-h-lookback variant
  collapses at 60 min (Phase 6 §1) — a large microstructure/stale-quote component.
- **Half-life ≤1 bar on 4/8:** the non-JPY relationships (EUR_GBP, EUR_CHF,
  GBP_CHF, EUR_AUD) are essentially 1-bar staleness.

### Therefore `FACTOR_REAL_BUT_WEAK`
The protocol's REAL_BUT_WEAK clause — *"genuine null-separated reversion exists
somewhere stable but … is confined to the no-arb/microstructure band"* — is the
**exact** description: the reversion is genuine and null-separated (overwhelmingly),
stable (especially the JPY complex with real 5–10 bar half-lives), yet universally
confined within the no-arb cost band. This is a real factor that is weak in the
specific, pre-registered sense of living inside the band.

---

## What this verdict asserts / does not assert

**Asserts:**
- Cross relative-value structure **is real** — triangular no-arbitrage consistency
  holds, and its deviations revert genuinely (beyond a wrong-triangle null), broadly
  and stably. After three null/rejected families (C1 cost-defeat + cross-replication
  failure, currency strength), this is the **first factor that genuinely exists** on
  this corpus.
- The reversion is a **no-arbitrage property**, not a generic shared-leg effect: the
  shared-leg cointegration spreads do **not** revert (half-life ≫ hold — C028
  reconfirmed; Phase 6 §3). The genuine reversion is specific to the pinned triangle.

**Does NOT assert:**
- **Anything tradable.** Tradability was out of scope and not computed. But the
  existence study itself reveals the structure is **~10× inside the cost band** — a
  *future* front-gate screen would face that wall (C028's two-/three-leg cost
  failure mode), which is exactly why this is REAL_BUT_WEAK and **not** a front-gate
  candidate. No cost gate set this verdict; the §11 *scale* evidence did.
- **That the JPY-complex slow component is exploitable.** It is genuine (multi-bar
  half-life) but still sub-band in magnitude; it is the part most worth a future
  *thesis*, not a present claim.

## Relationship to the programme

This is the **first non-rejected factor** in the entire research programme — a
meaningful scientific result. It also **closes the loop honestly**: even where real
relative-value structure exists, it is sub-cost-band on this corpus, consistent with
the standing finding that the venue is structurally cost-defeated. The cross data
delivered a genuine factor; the factor is just too small to trade here.

## Boundaries (unchanged)

No campaign created. No strategy approved (`approved: []`). No entry/exit logic, no
trading system, no front gate built, no train/validation/test. Paper/demo/live
remain blocked. No trading-API calls. **Definition not altered after results.**
Phase 8 records the next step and validation.

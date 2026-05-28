# USD_JPY-only C024 Readiness Decision

**Date:** 2026-05-28 · **Sprint:** `research-usdjpy-m15-microstructure-confirmation-diagnostic-001`
**Type:** diagnostic decision memo. Approves nothing, changes no verdict, tunes nothing,
creates no campaign, claims no edge. No CAMPAIGN_024 is created here.

Inputs:
[`USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_RESULT.md`](USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_RESULT.md),
`research/usdjpy_microstructure_diagnostic/analysis_summary.json`,
[`NEXT_THESIS_SELECTION_DECISION.md`](NEXT_THESIS_SELECTION_DECISION.md) §5.

---

## Decision

### `NOT_READY`

No **live** USD_JPY M15 microstructure-confirmation primitive separates winners from
losers with a material, train/validation-stable effect that beats the (inert) C022
EMA20-reclaim trigger. There is therefore **no evidential basis** for a USD_JPY-only
C024 entry-confirmation campaign.

## Evidence against readiness

The five-/seven-part bar requires a primitive that (1) separates in **both** splits,
(2) is **live-usable** without lookahead, (3) has plausible logic, (4) reduces
straight-to-stop, (5) preserves sample, (6) is not cost/session overfit, and (7) can
be precommitted without threshold mining. Against the USD_JPY evidence (306 trades;
train 133, validation 173; win rate 0.346 / 0.405):

- **Baseline is inert (as expected).** The old EMA-reclaim trigger
  `reclaim_distance_atr` is at AUC 0.539 train / 0.486 validation — **not even
  direction-stable**, min|AUC−0.5| = 0.014. The bar to beat is essentially "show any
  real, stable separation."

- **No live primitive clears the negligibility floor.** Continuous-score winner AUCs
  for the live detectors:
  - `reclaim_plus_impulse` 0.491 / 0.433 (stable, effect 0.009 — negligible),
  - `reclaim_plus_micro_swing_break` 0.470 / 0.486 (stable, 0.014 — negligible),
  - `range_expansion_after_compression` 0.484 / 0.383 (stable, 0.016 — negligible),
  - `liquidity_sweep_plus_displacement` 0.465 / 0.583 — **direction-unstable** (flips
    sides of 0.5 across splits), high overfit risk.

  The best stable live effect (0.016) is **far below the 0.05 floor** and barely
  exceeds the inert baseline. **Criterion (1) fails for every live primitive.**

- **The one stable boolean lift is fragile and self-contradictory.**
  `liquidity_sweep_plus_displacement` *present* shows a same-signed win-rate lift
  (+0.10 train / +0.14 validation), but: its continuous AUC is **unstable**; it is
  present on **81%** of trades so the "absent" comparison group is tiny (23 train /
  34 validation) and fragile; and it produces **no straight-to-stop reduction**
  (−0.02 / −0.01). A lift that is real would be expected to cut the straight-to-stop
  rate; it does not. This fails **(4)** and is too fragile for **(5)/(7)**.

- **The only above-floor separators are post-entry — not live-usable.**
  `reclaim_plus_retest_hold` reaches AUC 0.611 / 0.552 (effect 0.052, just above the
  floor) but it **inspects post-entry bars** (`uses_post_decision=True`): it describes
  trades that, after entry, held their retest — partly tautological with winning and
  **cannot gate a live entry**. `failed_reclaim_or_trap` is likewise post-entry and
  mechanically associated with losing (present → win-rate −0.17 / −0.26, more stops,
  more straight-to-stop). Both fail **(2)** by construction.

- **Logic / overfit.** Even where a number looks suggestive, it appears on a single
  small pair; under the §1a/§5 single-pair note a large effect is a reason for *more*
  scrutiny, not less. Nothing here would survive a clean OOS USD_JPY lockbox, and
  selecting any cut from this dataset would be threshold mining **(7)**.

## What this means for the family

This **sharpens, on USD_JPY specifically**, the C022 conclusion that the failure is an
entry-signal-quality failure. Replacing the M15 EMA-reclaim trigger with stronger
*live* microstructure confirmations (impulse, micro-swing break, sweep+displacement,
range expansion) does **not** recover winner/loser separation on USD_JPY. The
separation that exists is post-entry (retest-hold / trap), which confirms the
*behavioral* story (winners hold their reclaim; losers trap) but offers **no live
entry filter**.

## Recommendation

**Deprioritize USD_JPY M15 microstructure confirmation as an entry-edge lane.** It
joins the retired pullback family as "diagnosed, no live entry edge found." Do **not**
open a USD_JPY-only C024 on this evidence.

Options for a future sprint (each a *fresh, pre-committed* diagnostic, not a campaign):

1. **Different question, same pair:** USD_JPY is near-flat, not positive — investigate
   whether a *non-entry* lever (e.g. cost/session tradeability filtering, or
   trade-management using the post-entry retest-hold/trap signal as an *exit/early-
   invalidation* rule rather than an entry) changes net expectancy. This treats the
   post-entry signals honestly as management diagnostics, never as entry alpha.
2. **Different lane entirely** (per the options doc): a structurally different thesis,
   not another confirmation overlay on the same reclaim entry.
3. **Stop here:** record USD_JPY microstructure confirmation as closed and keep the
   research freeze, pending a genuinely new external thesis.

The recommended default is **(3) stop / record-closed**, with **(1)** as the only
USD_JPY follow-up worth considering — and only because it reframes the post-entry
signal as *management*, explicitly not as the entry edge this sprint failed to find.

## What is NOT being done (hard rules upheld)

- No CAMPAIGN_024 created; no thesis numbers or thresholds drafted as parameters.
- No C023 execution; no C022 retune; no verdict changed; no historical metric rewritten.
- No strategy approved; `configs/approved_strategies.yaml` remains `approved: []`.
- No paper/demo/live; no broker/executor/order/live changes; no OANDA calls.
- USD_JPY is **not** presented as proven edge. A future USD_JPY C024 would require a
  fresh, pre-committed, out-of-sample-validated thesis clearing the full §5 bar — which
  this evidence does not provide.

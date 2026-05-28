# Lifecycle Feature Capture & MFE/MAE Execution 001 — Conclusions

**Date:** 2026-05-28 · **Sprint:** `infra-lifecycle-feature-capture-and-mfe-mae-execution-001`
**Type:** diagnostics / infrastructure. Approves nothing, changes no verdict, tunes nothing.

> **Update (data unblocked).** A read-only local materialized M15 store became
> reachable (env via a gitignored `.env` symlink). Phases 1 and 5 were **executed**
> against real candles — the conclusions below are now evidence-backed, not gated.
> Still: no verdict/metric changed, nothing approved, no OANDA calls, mid OHLC only.

## 1. Was MFE/MAE reconstruction completed or still blocked?

**Completed.** Reconstructed **2311 / 2396** base train+validation trades from local
materialized M15 (85 dropped at data edges with zero in-window bars; no fabrication).
See `CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md` / `c022_mfe_mae_summary.json`.

## 2. Straight-to-stop vs first reaching favorable?

**Mixed, leaning "many never get going."** Of hard-stopped trades: **45.9% never
reached +0.25R** before being stopped (effectively straight-to-stop), while 54.1%
reached +0.25R, 36.6% reached +0.5R, and 16.3% reached +1.0R first (mean MFE before
stop +0.47R). So a large plurality are dead on arrival; a meaningful minority showed
promise and gave it back.

## 3. Is the 2× ATR stop too tight, too loose, or inconclusive?

**Not the lever — effectively "neither helps."** The executed stop-model sweep
(fixed entries, exit varied) holds expectancy in a tight **negative** band across
1.5×/2.0×/2.5×/3.0× ATR (≈ −0.05 to −0.08R); wider stops just enlarge `mean_loss_r`
without lifting expectancy, tighter stops cut losses but also winners. Independently,
time-exit winners rarely approach the stop (only **4.7%** ever touch −0.9R), so the
stop is **not** cutting live winners. The 2× ATR stop is not meaningfully too tight
or too loose — stop distance is not where the edge is lost.

## 4. Is a structure stop worth pre-committing later?

**No, on current evidence.** Since no ATR-multiple variant lifts expectancy toward
zero and winners don't approach the stop, there is no signal that a structure-based
stop would help. (The Phase 3/4 capture still makes it testable later if a *new*
entry shows different path behavior — but nothing justifies it now.)

## 5. Is an early-invalidation exit worth pre-committing later?

**No, on current evidence.** The executed `time-to-invalidation` variants
(no +0.25R by 8 bars; no +0.5R by 8/12 bars) all land at ≈ −0.06 to −0.07R — still
negative, not materially better than baseline. Cutting non-starters earlier reduces
time-in-market but does not create an edge. Not worth a campaign on its own.

## 6. Is the bigger issue entry timing rather than stop placement?

**Yes — now strongly evidenced.** The decisive result: even the **cost-free** mid
baseline (no spread/slippage) is already **−0.073R**, and *no* exit rule (any ATR
multiple, any invalidation horizon) crosses zero. Removing cost and re-shaping the
stop both fail to reach break-even. Combined with the realized 32.6% win vs ~39%
breakeven, uniform negativity across all 7 pairs and both sides, and the Phase 2
finding that true JPY/CAD losses are *larger* than recorded — the edge is missing at
**entry**, not at the stop. Stop geometry is a second-order knob on a population with
no entry edge.

## 7. Should C023 (ADX22) execute now or remain deferred?

**Defer.** Unchanged from prior sprint. A single ADX-threshold bump (20→22) on a
strategy that fails broadly across all pairs is very unlikely to manufacture an
edge, and running it now would spend a campaign slot ahead of the MFE/MAE evidence
that should drive the next design.

## 8. Is the project ready for C024?

**Not as a stop/exit campaign, and not yet as an entry campaign without a new
hypothesis.** The lifecycle failure point is now *verified* — it is **entry edge**,
not stop placement (cost-free baseline still negative; no exit rule clears zero). So
the project is ready to **stop investigating exits** and is ready to *design* an
entry-focused C024 — but only once that design rests on a signal feature shown to
separate winners from losers, which the C022 artifacts do not yet contain. C024 must
not be a re-skinned C022 entry or a stop tweak.

## 9. What must happen before C024 is designed?

1. ~~Unblock local M15 data / run reconstruction~~ — **done this sprint.**
2. ~~Execute the stop-model comparison~~ — **done; exits are not the lever.**
3. **Capture entry signal features** that can be tested for winner/loser separation:
   run an instrumented C022-style diagnostic export (`--emit-lifecycle-features`) so
   H4 ADX, H1 pullback depth, M15 reclaim distance, ATR-at-entry, session/regime are
   recorded per trade, then test which (if any) actually predicts MFE/MAE outcome.
4. **Adopt the pair-agnostic `price_based_r`** convention in future writers (the
   Phase 2 fix) so per-pair R is comparable.
5. Only if a feature shows real separation → design C024 around *that* entry filter.
   If none separates, the honest conclusion is the pullback-resolution family has no
   recoverable entry edge and should be retired, not re-tuned.

## 10. If/when designing C024, what should it focus on?

An **entry-quality** hypothesis, pre-registered, justified by a signal feature with
demonstrated winner/loser separation in the captured lifecycle features — **not** a
stop change (proven second-order this sprint) and **not** another intuition-driven
entry variant. Name the confirming measurement in advance. Exactly one change.

## Recommended stance

- **C023 remains deferred** (an ADX tweak cannot fix an entry-edge problem).
- **C024 is not a stop/exit campaign** — exits are proven second-order. It may be an
  entry-feature campaign *only* once a separating feature is found (step #3 above);
  otherwise retire the family rather than re-tune it.
- The next campaign must rest on a **verified, feature-level** entry edge, not
  intuition.

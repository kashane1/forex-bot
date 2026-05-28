# Lifecycle Feature Capture & MFE/MAE Execution 001 — Conclusions

**Date:** 2026-05-28 · **Sprint:** `infra-lifecycle-feature-capture-and-mfe-mae-execution-001`
**Type:** diagnostics / infrastructure. Approves nothing, changes no verdict, tunes nothing.

## 1. Was MFE/MAE reconstruction completed or still blocked?

**Still BLOCKED_LOCAL_DATA.** The reconstruction was re-attempted this sprint and
again could not run: no reachable materialized M15 store
(`FOREX_BOT_RESEARCH_DATABASE_URL` unset, local Postgres needs a password,
`data/bot.sqlite3` empty, no local candle corpora). No excursion numbers were
produced or fabricated. The reconstruction *logic* remains implemented and
unit-tested (`src/forex_bot/research/mfe_mae.py`, 11 synthetic-candle tests); only
the data is missing here.

## 2. If completed: straight-to-stop vs first reaching favorable?

**Unanswerable this sprint** (blocked, per #1). This is the single highest-value
question and the explicit gate for any stop-related campaign. The tooling to
answer it the moment a populated M15 store is reachable is in place.

## 3. Is the 2× ATR stop too tight, too loose, or inconclusive?

**Inconclusive** on path evidence — and that is the honest state. Realized-outcome
diagnostics (prior sprint, reproduced exactly) show 60% hard-stop @ −0.86R vs 40%
time-exit @ +0.96R, which is *consistent with* either "stop too tight" or "entries
go straight to the stop". The two are only separable with MFE/MAE. No stop verdict
should be asserted until then.

## 4. Is a structure stop worth pre-committing later?

**Not yet.** Only if MFE/MAE later shows stopped trades had meaningful favorable
excursion *before* being stopped (i.e. the stop cut live winners). The Phase 3
schema + Phase 4 exporter now make the H1/M15 structure geometry capturable, so the
question becomes answerable in a future instrumented run.

## 5. Is an early-invalidation exit worth pre-committing later?

**Most promising of the stop-side ideas, but still gated.** `time-to-invalidation`
(cut trades that never reach +0.25R/+0.5R within N bars) needs only the per-bar
path — no extra signal capture — so it is the cheapest to evaluate once Phase 1 is
unblocked. It is *not* justified to pre-commit now without that evidence.

## 6. Is the bigger issue entry timing rather than stop placement?

**Most likely yes — entry edge, not stop placement** (carried from the prior
sprint's roadmap and reinforced here). Win rate 32.6% vs ~39% breakeven, uniformly
negative across all 7 pairs, worsening out-of-sample and under cost stress. The
Phase 2 R-convention audit further shows the true USD_JPY/USD_CAD losses are
*larger* than recorded — so corrected aggregates would be **more** negative, not
less. None of that points to a stop tweak rescuing the system; it points to weak
entry-edge. Confirmation still requires MFE/MAE to rule out the too-tight-stop
alternative.

## 7. Should C023 (ADX22) execute now or remain deferred?

**Defer.** Unchanged from prior sprint. A single ADX-threshold bump (20→22) on a
strategy that fails broadly across all pairs is very unlikely to manufacture an
edge, and running it now would spend a campaign slot ahead of the MFE/MAE evidence
that should drive the next design.

## 8. Is the project ready for C024?

**No.** The lifecycle failure point is still not *verified* (MFE/MAE blocked), and
the historical R convention was just shown to be inconsistent for USD-base pairs.
Designing C024 now would be intuition, not evidence.

## 9. If not ready, what must happen first?

1. **Unblock local M15 data** and run Phase 1 reconstruction (exact command in the
   plan) — answer #2/#3.
2. **Run one instrumented C022-style diagnostic export** with
   `--emit-lifecycle-features` so ATR-at-entry + H1 pullback + M15 reclaim geometry
   exist for the stop-model comparison (Phase 5).
3. **Adopt the pair-agnostic `price_based_r`** convention for all future trade
   writers so per-pair R is comparable (fixes the Phase 2 quirk going forward).
4. With that evidence, **classify the failure** as entry-edge vs stop-geometry.

## 10. If ready, what should C024 focus on?

Only after #9: design C024 around the **verified** failure point. If MFE/MAE shows
trades go straight to the stop → the problem is entry selection, and C024 should be
an *entry-quality* hypothesis (e.g. setup-quality filter justified by a signal
feature that actually separates winners), **not** a stop tweak. If instead MFE/MAE
shows winners were stopped before paying → a single pre-registered stop change
(early-invalidation or a specific ATR multiple) becomes a legitimate campaign. Pick
exactly one, pre-registered, with the confirming measurement named in advance.

## Recommended stance (unchanged default)

- **C023 remains deferred.**
- **C024 remains blocked** until MFE/MAE evidence and consistent R capture exist.
- The next campaign must be designed around a **verified** lifecycle failure, not
  intuition.

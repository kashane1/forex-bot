# Trade Lifecycle Improvement Roadmap

**Date:** 2026-05-28 · **Sprint:** `infra-trade-lifecycle-feature-capture-and-stop-diagnostics-001`
**Type:** diagnostics-derived roadmap. Approves nothing, changes no verdict, tunes nothing.

This roadmap is grounded in the realized-outcome diagnostics reproduced this
sprint (`stop_exit_summary.{json,md}`) and the inventory of what trade data
actually exists (`TRADE_LIFECYCLE_ARTIFACT_INVENTORY.md`). Where evidence is
missing it says so rather than guessing.

## 1. What is the most likely biggest failure?

**Most likely: entry timing / absence of a reliable edge — *not* stop placement.**

Realized C022 evidence (base, train+val, 2396 trades, exactly reproduced):

- Win rate **32.6%** vs breakeven **~39.0%** — a ~6-point edge deficit. With the
  realized +1.24 / −0.79 payoff, the system needs ~39% wins and only gets ~33%.
- Hard-stop exits **60.1%** at mean **−0.86R**; time-stop exits **39.9%** at mean
  **+0.96R**. Survivors *do* pay — but too few survive.
- **42.3%** of trades lose ≥0.9R; large wins (≥+1.0R) are only **14.9%**.
- Pattern holds across all 7 pairs (every train pair negative) and worsens out of
  sample (val −0.166R) and under cost stress (−0.247R). This is **not** a
  pair-specific or cost-specific artifact — it is systemic.

A high stop-share with profitable survivors is *consistent with two stories*:
(a) the stop is too tight and cuts winners, or (b) entries are simply timed into
noise that mostly fails. We **cannot yet distinguish these** without per-bar
MFE/MAE (do stopped trades first travel favorably, or go straight to the stop?).
That distinction is the single highest-value missing measurement — but the broad,
uniform, cross-pair negativity and the worsening out-of-sample/cost behavior lean
toward **(b): weak/absent edge in the entry**, with stop geometry a secondary
contributor at most. Tightening or widening a stop on a population that wins only
33% of the time does not manufacture an edge.

> Honesty note surfaced this sprint: C022's committed `r_multiple` for **USD_JPY
> and USD_CAD** losses is recorded smaller than −0.9R (near-full-loss share = 0
> for those pairs while hard-stop share is ~0.6). Their aggregate expectancy still
> matches the published campaign (−0.0017 / −0.0512), so the loader is faithful —
> but this R-scaling inconsistency must be verified before any per-pair stop-loss
> claim is trusted. Logged as a capture-quality gap (§2).

## 2. Lifecycle fields every future campaign MUST record

Current trade writers export entry/exit time+price, stop price, R, bars-held,
spread, exit reason — enough for realized aggregates but **not** for diagnosing
*why*. Future campaigns must additionally record, per trade:

1. **MFE_r and MAE_r** (full path max favorable / adverse excursion in R).
2. **Threshold-before-stop flags**: reached +0.25R/+0.5R/+1.0R before the stop;
   touched −0.5R/−0.9R; and the bar index of each first crossing.
3. **ATR at entry** (the stop's ATR multiple in price) — required for any ATR
   stop-sensitivity analysis.
4. **Signal features at entry**: H4 ADX, H1 pullback depth (ATR units), M15
   reclaim distance (ATR units) — so failures can be sliced by setup quality.
5. **Session bucket and volatility regime** at entry.
6. A **verified, consistent R convention** across all instruments (fix the
   JPY/CAD R-scaling inconsistency noted in §1 at the writer, not downstream).

The schema in `src/forex_bot/research/trade_lifecycle.py` already has optional
slots for all of these — future writers should populate them.

## 3. What should be required before CAMPAIGN_024?

- A trade writer that emits the §2 fields (MFE/MAE + signal features + ATR +
  session/regime) for **every** trade.
- A populated, reachable materialized M15 store so MFE/MAE can be reconstructed /
  captured (this sprint was BLOCKED_LOCAL_DATA on exactly this).
- A pre-registered hypothesis that names the **specific lifecycle failure point**
  C024 intends to fix, with the measurement that would confirm/deny it — not
  another entry variant chosen by intuition.

## 4. Should C023 (ADX22) be executed now or deferred?

**Defer.** C023 is a single-knob sibling of C022 (`h4_adx_min` 20→22) and C022
fails *broadly* (all 7 pairs negative, train gate failed decisively). A small ADX
threshold bump is very unlikely to convert a −0.10R train expectancy into a
positive edge, and running it now would consume a campaign slot without first
capturing the MFE/MAE that would explain *whether* the entry can work at all.
Execute C023 only if, after MFE/MAE capture, the evidence specifically implicates
weak-trend (low-ADX) entries as the dominant failure — i.e. let the diagnostic,
not the existing scaffold, justify the run.

## 5. What stop models deserve pre-committed campaigns later?

Only *after* MFE/MAE reconstruction shows stopped trades had **meaningful
favorable excursion before being stopped** (i.e. story (a) in §1). If so, the
ranked candidates — each as a **pre-registered** test, never a post-hoc pick:

1. **Time-to-invalidation early exit** (cut trades that fail to reach +0.25R/+0.5R
   within N bars) — computable from the existing `mfe_mae` module, lowest new-data
   cost.
2. **ATR-multiple widening (2.5×/3.0×)** — only if MFE shows winners were stopped
   before paying; requires ATR-at-entry capture.
3. **Structure-based stop** (swing/pullback low) — requires pullback geometry
   capture.

If MFE/MAE instead shows stopped trades went **straight to the stop with little
favorable excursion**, no stop model deserves a campaign — the problem is entry.

## 6. What entry refinements are justified by evidence *today*?

**None yet, beyond data capture.** The only evidence-justified next action is to
instrument future campaigns (§2) and capture MFE/MAE. Proposing a new entry filter
now would be intuition, not evidence. The realized data says "entries win ~33% and
that is below breakeven across all pairs" — it does **not** yet say which entry
refinement fixes that.

## 7. What must remain forbidden as likely overfit / tuning?

- Picking a "best" stop multiple **after** seeing per-trade outcomes and presenting
  it as an edge (the explicit anti-rule of this sprint).
- Re-running C022 with adjusted parameters and reporting an improved metric as a
  verdict.
- Per-pair stop/threshold tuning to rescue the one near-zero pair (USD_JPY).
- Softening any gate, opening the test lockbox, or treating a diagnostic
  sensitivity result as campaign evidence.

## Recommended stance

- **Do not** execute C023 immediately just because the scaffold exists (§4).
- **Do not** create CAMPAIGN_024 yet (§3).
- **First** make future campaigns capture MFE/MAE, signal features, ATR, and stop
  geometry, and fix the R-convention inconsistency (§2).
- **Then** design C024 around the *verified* failure point — most likely entry
  edge, with stop geometry tested only if MFE/MAE implicates it.

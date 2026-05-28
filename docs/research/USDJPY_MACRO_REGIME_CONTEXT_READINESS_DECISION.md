# USD_JPY Macro-Regime Context — Readiness Decision

**Sprint:** `usdjpy-macro-regime-context-tradeability-001` · **Phase 4**
**Inputs:** Phase 2 result + Phase 3 robustness/latency-independence.

> No campaign created. C024 **not** created. C023 **not** executed. No strategy
> implemented. No verdict changed. `configs/approved_strategies.yaml` = `approved: []`.
> Paper/demo/live remain blocked. TEST window untouched.

---

## Classification

# `PAUSE_STRATEGY_RESEARCH`

Slow macro/rates/calendar context is **lookahead-safe and latency-independent** (it meets
those framing requirements cleanly), but it provides **no robust, identifiable, actionable
tradeability-conditioning or no-trade signal** for USD/JPY beyond mechanical volatility
effects the session atlas already captures. There is nothing here to carry into a precommit
design, so strategy research remains paused.

---

## Evaluation against the eight slow-regime readiness gates (framing doc §7)

A future precommit-design sprint is allowed only if **all eight** hold. Result:

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | slow-regime based | PASS | daily/weekly features only |
| 2 | lookahead-safe | PASS | unit-tested as-of join; schedule-only calendar |
| 3 | latency-independent | PASS | effects identical at 1-day vs 7-day lag |
| 4 | not news-reactive | PASS | no intrabar/outcome reaction; calendar dates only |
| 5 | not speed-competitive | PASS | no latency edge assumed or used |
| 6 | supported on **both** train and validation (no TEST) | **FAIL** | no conditioning effect is both consistent **and** non-mechanical; rate-regime is non-identifiable (collinear with split) |
| 7 | tradeability conditioning / no-trade filter, not a macro entry | **FAIL (no signal)** | raw spread flat, whipsaw ~0.50 everywhere; no macro no-trade filter beyond the session/rollover one |
| 8 | structurally distinct from prior failed families | PASS | slow regime context, not indicator confluence |

Gates 1–5 and 8 pass (the *method* is sound and honest), but gates 6 and 7 — the ones that
require an actual, identifiable, both-splits tradeability signal — **fail**. The framing
sound-ness does not rescue an absent signal.

---

## Why each alternative label was rejected

- **`READY_FOR_PRECOMMIT_DESIGN`** — rejected: there is no actionable conditioning to
  design around. Raw spread is invariant to macro context, chop is unconditioned, and the
  only real effect (event-driven vol level) is mechanical, direction-blind, and already in
  the session atlas.
- **`MORE_DIAGNOSTICS_REQUIRED`** — rejected for the *current* data: the binding blockers
  are structural, not measurement gaps that another pass would close — (a) the
  rate-differential regime is **collinear with the 2021–2025 period** and cannot be
  identified without a multi-cycle history + a JP rate leg, and (b) whipsaw/spread show a
  clean null. More slicing of the same data would invite threshold-mining. (If new data
  arrives — see below — a *fresh* sprint, not this one, could revisit.)
- **`NOT_READY`** (hold open) — the practical state is indistinguishable from PAUSE given
  the standing context (no internal price-structure lead survives either; the macro lane
  now also returns null). PAUSE is the honest, decisive label.

---

## What this establishes (useful negative results)

1. **USD/JPY raw spread is invariant to slow macro context** — so a macro cost filter adds
   nothing to the existing session/rollover filter. (Reaffirms the session/rollover
   no-trade overlay as the only validated cost filter.)
2. **Chop/whipsaw is not conditioned by slow macro regime** (~0.50 everywhere).
3. **Event windows** only carry a mechanical vol-level effect (post-event vol up,
   pre-event vol down), which is direction-blind and time-of-day-redundant.
4. **Rate-differential regime conditioning is not testable** on 2021–2025 USD/JPY data
   (regime collinear with the period; JP leg absent) — a hard data limitation, now
   documented so it is not re-attempted blindly.

These are genuine, lookahead-safe negative results — they narrow the search honestly.

---

## Recommended direction after the (continued) pause

Strategy research stays paused. The only directions that are *not* re-mining exhausted
data are **data-acquisition infrastructure** (each a separate, later, non-strategy sprint):

1. **Multi-cycle + JP-rate-leg data** so a rate-differential regime could one day be
   *identified* rather than confounded with the 2021–2025 period (requires a verified JP
   rate series and a longer history than the current M15 corpus).
2. **A verified economic-event calendar** (US CPI + BOJ, currently deferred) — though, given
   the event effect found here is mechanical/vol-only, this is low-priority.
3. Otherwise, **hold / freeze** until a genuinely new, externally-sourced, structurally
   distinct thesis with a mechanism appears.

No campaign, no C024, no approval follows from this decision.

---

## Explicit statement

This decision creates **no** campaign, **no** C024, executes **no** C023, implements
**no** strategy, changes **no** verdict, approves **no** strategy, and leaves
paper/demo/live blocked and the TEST window sealed. Verdict: **`PAUSE_STRATEGY_RESEARCH`.**

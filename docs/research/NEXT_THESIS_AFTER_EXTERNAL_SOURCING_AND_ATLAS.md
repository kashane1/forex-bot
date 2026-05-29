# Next Thesis After External Sourcing & Atlas — Decision

**Sprint:** `external-thesis-sourcing-and-session-atlas-001` · **Phase 4**
**Inputs:** Phase 1 framework, Phase 2 atlas, Phase 3 scorecard.

> No campaign is created. C024 is **not** created. C023 is **not** executed. No strategy
> is implemented. No verdict changes. `approved_strategies.yaml` remains `approved: []`.
> Paper/demo/live remain blocked. This document records a *direction decision* only.

---

## Classification

# `MORE_DIAGNOSTICS_REQUIRED`

**Single thesis carried forward:** Candidate **#5 — intraday volatility-compression →
range-expansion (USD_JPY, M15)**, to be tested first by a *focused, precommitted
diagnostic*, **not** a campaign design.

**Standing overlay adopted now (not a strategy):** Candidate **#9 — no-trade
cost/spread filter** (never trade the rollover bar; deprioritize thin off-hours). This
is a constraint to bake into any future design; it cannot earn edge on its own, so it
does not count as the selected thesis.

---

## Why not `READY_FOR_PRECOMMIT_DESIGN`

Thesis #5 clears every Phase-1 hard gate (distinct, mechanistic, data-available,
codable, plausibly cost-surviving) and is the only candidate whose core requirement
aligns with where the atlas actually has structure. But there is one unresolved item
that makes a full precommit *campaign design* premature:

- The atlas shows volatility expansion is **predictable in timing/state**
  (range-expansion probability rises monotonically low→mid→high vol: 0.29 → 0.50 → 0.71,
  and tracks the hour-of-day curve), **but it does not demonstrate a monetizable,
  cost-surviving way to convert that into PnL.** Forward-return *direction* is a coin
  flip everywhere (continuation ≈ reversion ≈ 0.49), and MFE:MAE after arbitrary entries
  is < 1.0.

Designing a precommitted campaign now would mean guessing the monetization mechanism
(direction-agnostic straddle-like? expansion-conditioned execution? expansion + an
*independent* direction input?) without evidence that any of them survives the ~1.6 pip
spread. That is precisely the "design in the dark / threshold-mine a knob" failure mode
this whole sprint was created to stop. So the honest next step is a **narrow diagnostic
that answers the monetization question**, after which a precommit design is either
justified or the thesis is retired.

## Why not `PAUSE_STRATEGY_RESEARCH`

A pure pause is not warranted this round because, for the first time in the post-C022
thread, we have a candidate (#5) that is *structurally distinct from every failed family*
**and** *positively supported by the atlas on its core variable (volatility)* **and**
low-parameter. That is a materially better starting point than re-mining the retired
trend/pullback family. Pausing remains the fallback if the Phase-A diagnostic below
comes back null.

---

## Selection check (Phase-4 criteria) for thesis #5

| # | Criterion | Met? | Note |
|---|---|---|---|
| 1 | Structurally distinct from C022/C023 & failed families | **Yes** | Volatility-state thesis, not indicator confluence / direction prediction. |
| 2 | Support from the USD_JPY atlas | **Partial** | Strong on the *volatility* leg (monotonic regime/hour structure); **silent** on monetization/direction — the exact gap the diagnostic must close. |
| 3 | Objectively codable | **Yes** | Vol-regime / range-percentile state is deterministic from M15. |
| 4 | Sufficient sample size | **Yes** | Every bar carries a vol state; compression episodes are frequent. |
| 5 | Not a threshold-mined prior signal | **Yes** | Low-parameter, robust, monotonic construct; not a knob on a rejected family. |
| 6 | Plausible reason to survive costs | **Conditional** | Expansion coincides with tight-spread active sessions; *but* must be shown net of ~1.6 pip — this is what the diagnostic tests. |

Criteria 2 and 6 are "partial/conditional," which is exactly why the classification is
`MORE_DIAGNOSTICS_REQUIRED` rather than `READY_FOR_PRECOMMIT_DESIGN`.

---

## Precommitted diagnostic spec (for the NEXT sprint — not run here)

The next sprint should run a **read-only, no-strategy diagnostic** (not a campaign, not
C024) that answers a single question:

> **Does an intraday volatility-compression → expansion state on USD_JPY produce a
> cost-surviving, objectively-defined trade structure — and if so, does it need a
> direction input or can it be direction-agnostic?**

Pre-commit these before looking at results:

1. **State definition (fixed in advance):** "compression" = trailing rolling
   ATR/range percentile below a fixed low threshold; "expansion" = subsequent realized
   range exceeding a fixed multiple of the compressed range. Thresholds fixed *before*
   measurement; report sensitivity, do not optimize.
2. **Three candidate monetizations, measured side by side, all net of the measured
   session spread + a slippage allowance:**
   - (a) direction-agnostic post-compression excursion (does |MFE| meaningfully exceed
     |MAE| *and* the round-trip cost after a compression flag?);
   - (b) expansion conditioned on an *independent* simple direction proxy;
   - (c) fade of the first expansion leg (ties to the false-breakout structure).
3. **Cost model:** use the Phase-2 atlas spread distribution by session (median + p90),
   plus the repo's existing slippage convention; apply the #9 rollover/off-hours filter.
4. **Windows:** train+validation only; **TEST lockbox 2025-07+ stays sealed.**
5. **Kill criteria (precommitted):** if none of (a)/(b)/(c) clears cost by a
   pre-stated margin on *both* train and validation, the thesis is **retired** and the
   recommendation flips to `PAUSE_STRATEGY_RESEARCH`.
6. **No optimization loop:** report results at the fixed thresholds + a small,
   pre-declared robustness grid. No threshold mining; no "best cell" selection.

Only if that diagnostic returns a cost-surviving, robust structure does a *subsequent*
sprint design a precommitted campaign (and only then is a new campaign number even
discussed).

---

## Infrastructure backlog surfaced (not this sprint)

- **Economic-calendar overlay** (for thesis #7) — no event-time calendar exists in the
  research DB; sourcing/ingesting one is a standalone infra task.
- **Maintained rates/risk overlay aligned to the candle timeline** (for thesis #8) —
  FRED cache exists (DGS2/DGS10/VIX/SP500) but is not a maintained, timeline-aligned
  research feature.

Both are recorded so they are not re-discovered later; neither is started here.

---

## Explicit statement

This decision creates **no** campaign, **no** C024, executes **no** C023, implements
**no** strategy, changes **no** verdict, approves **no** strategy. The carried-forward
thesis (#5) advances only to a *precommitted diagnostic* in a future sprint, gated by
the kill criteria above. See `NEXT_SPRINT_PROMPT_AFTER_EXTERNAL_THESIS_AND_SESSION_ATLAS.md`
(Phase 5) for the drafted next-sprint prompt.

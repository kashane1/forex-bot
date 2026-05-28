# USD_JPY London Compression-Continuation — Readiness Decision

**Sprint:** `usdjpy-london-compression-continuation-confirmation-001` · **Phase 4**
**Inputs:** Phase 2 confirmation result + Phase 3 robustness/falsification.

> No campaign created. C024 **not** created. C023 **not** executed. No strategy
> implemented. No verdict changed. `configs/approved_strategies.yaml` = `approved: []`.
> Paper/demo/live remain blocked. TEST window untouched.

---

## Classification

# `PAUSE_STRATEGY_RESEARCH`

The single surviving lead from the entire compression/expansion line of inquiry — the
post-compression **London-session breakout continuation** — **fails its overfit-hardened
confirmation decisively.** Per the sprint mandate ("if the lead fails confirmation,
classify as `PAUSE_STRATEGY_RESEARCH`") and the locked kill criteria, strategy research on
this thesis family is paused.

---

## Evaluation against the eight strict precommit gates

A future precommit-design sprint is allowed only if **all eight** hold. Result:

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | train **and** validation positive after **base** cost | PASS (no-stop only) | h16 +1.04/+3.04, h32 +2.21/+6.12 — but only with no protective stop |
| 2 | conservative cost does not flip either split negative | **FAIL** | h16 no-stop conservative train **−0.65** |
| 3 | intrabar stop model does not destroy the edge | **FAIL (decisive)** | every stop → −2.7 to −7.7 pips both splits, both horizons |
| 4 | sample size adequate | PASS | n ≈ 690–850/split (≥150 floor) |
| 5 | year/half-split robustness acceptable | **FAIL** | positive only in trend years 2022/2024; negative-flat 2021/2023/2025 |
| 6 | effect not dominated by outliers | **FAIL** | not 5 trades, but a whole-regime (trend-year) concentration |
| 7 | TEST not touched | PASS | hard-bounded to < 2025-07-01 |
| 8 | structurally distinct from C022/C023/microstructure | PASS | volatility-state + session break-continuation, not indicator confluence |

**Four gates fail (2, 3, 5, 6), including the decisive stop gate.** Not eligible for
precommit design.

---

## Why each alternative label was rejected

- **`READY_FOR_PRECOMMIT_DESIGN`** — rejected: fails gates 2, 3, 5, 6. The apparent edge
  exists only with no protective stop, non-conservative cost, no multiple-testing
  correction, and favorable-year selection. Designing a campaign on it would institutionalize
  an overfit, unbounded-risk, trend-beta artifact.
- **`MORE_DIAGNOSTICS_REQUIRED`** — rejected: the confirmation was the precommitted,
  overfit-hardened test the lead was promised. It failed on multiple independent, decisive
  axes (not a measurement gap). Spending more diagnostics here would be searching for a
  configuration that "works" — i.e. the threshold-mining this program forbids.
- **`NOT_READY`** (and hold open) — too weak. The whole compression/expansion family has
  now been tested end-to-end: broad thesis falsified (clustering, direction null), and the
  one lead it produced is falsified under realism. There is no remaining sanctioned
  internal lead. A clean PAUSE is the honest state.

---

## What this closes

- The **intraday volatility-compression → expansion** thesis (the top external-sourcing
  candidate, #5) is now **fully explored and exhausted** as an internal data lead: broad
  thesis falsified for tradability (prior sprint), and its only sub-lead (London
  continuation) falsified under realistic costs + protective stops + multiple testing +
  year robustness (this sprint).
- Combined with the retired C022/C023 pullback family and the closed USD_JPY
  microstructure entry/management lanes, **no internal USD_JPY price-structure lead
  currently survives a hardened test.**

## Recommended direction after the pause

Strategy research is paused. The two defensible non-strategy directions (neither started
here, neither a campaign) are:

1. **Build the missing external-data overlays** that the atlas scorecard flagged as
   *blocked for lack of data*, so genuinely different theses (#7 macro/calendar windows,
   #8 carry/rates/risk-off regime) become testable in future: a maintained economic-event
   calendar and a timeline-aligned rates/risk feature (FRED DGS2/DGS10/VIX/SP500 exist
   but are not maintained research features). This is **infrastructure**, not a strategy.
2. **Hold / freeze** strategy research entirely until a genuinely new, externally-sourced,
   structurally-distinct thesis with a mechanism appears — re-entering the
   external-thesis-sourcing framework rather than mining USD_JPY price structure further.

Either is a separate, later, separately-scoped sprint. **No campaign, no C024, no
approval** follows from this decision.

---

## Explicit statement

This decision creates **no** campaign, **no** C024, executes **no** C023, implements
**no** strategy, changes **no** verdict, approves **no** strategy, and leaves
paper/demo/live blocked and the TEST window sealed. Verdict: **`PAUSE_STRATEGY_RESEARCH`.**

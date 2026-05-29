# USD_JPY Volatility-Compression → Expansion — Readiness Decision

**Sprint:** `usdjpy-volatility-compression-expansion-diagnostic-001` · **Phase 5**
**Inputs:** Phase 3 result + Phase 4 monetization diagnostic.

> No campaign created. C024 **not** created. C023 **not** executed. No strategy
> implemented. No verdict changed. `configs/approved_strategies.yaml` = `approved: []`.
> Paper/demo/live remain blocked. TEST window untouched. This records a *direction
> decision* only.

---

## Classification

# `MORE_DIAGNOSTICS_REQUIRED`

- The **broad** intraday volatility-compression → range-expansion thesis is **NOT_READY**
  / effectively falsified for tradability: compression predicts *smaller* absolute future
  range (vol clustering), direction is null, and every aggregate monetization (continuation
  / fade / active-session) **loses on train** net of an optimistic cost.
- **But** the diagnostic honestly surfaced **one mechanistically-grounded lead** —
  *post-compression London-session breakout continuation* — that is positive on **both
  splits at both horizons**. Under the anti-overfit framework this is not an edge; it is a
  single hypothesis that earns **at most one** precommitted, overfit-hardened,
  realistic-cost confirmation before any precommit-design is even discussed.

So the thesis as posed is not ready, and a pure PAUSE would discard a real both-splits
lead — hence `MORE_DIAGNOSTICS_REQUIRED`, narrowly scoped to the London cell, with a
hard kill if it fails realistic costs.

---

## Evaluation against the seven precommit gates

A future precommit-design sprint is allowed only if **all seven** hold. Status now:

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | Compression predicts expansion in **both** train & validation | **FAIL (broad)** | Absolute range ratio < 1 every horizon/split (clustering). Only *relative* (range/ATR) expansion exists; not tradable on its own. |
| 2 | Effect large enough to survive costs | **FAIL (broad) / UNPROVEN (London)** | Aggregate M2/M3/M4 negative on train. London cell +1–6 pips only under an *optimistic* 4.4-pip cost + level-fill + no intrabar stop. |
| 3 | Plausible live-usable monetization path | **PARTIAL** | Broad: none. London continuation: a coherent Tokyo-compression→London-open break-continuation path exists, but unproven under realistic execution. |
| 4 | Sufficient sample size | **PASS (overall) / MARGINAL (London)** | 13,768 compressed bars; London cell n≈700–850/split. |
| 5 | Not a threshold-mined prior signal | **AT RISK** | London was selected post-hoc from 12 session×horizon cells — multiple-comparisons risk. Must be precommitted, not declared. |
| 6 | Session/cost constraints clear | **PASS** | Rollover/off-hours cost-hostile (M5: 32.4% of compressed bars); active-session + no-rollover overlay reaffirmed. |
| 7 | Structurally distinct from C022/C023/microstructure family | **PASS** | Volatility-state + session-conditioned break continuation; not indicator-confluence/pullback. |

Gates 1, 2, 5 are not satisfied for the broad thesis; gates 2, 3, 5 are unproven for the
London lead. **No gate-complete thesis exists → not `READY_FOR_PRECOMMIT_DESIGN`.**

---

## Why not each other label

- **`READY_FOR_PRECOMMIT_DESIGN`** — rejected: the broad thesis fails gates 1/2/5 and the
  London lead is post-hoc + optimistic-cost (gates 2/3/5 unproven). Designing a campaign
  now would be threshold-mining a single multiple-tested cell.
- **`NOT_READY`** (full stop) — too strong: it would ignore a genuine both-splits,
  mechanistically-coherent lead. NOT_READY is the correct status of the *broad* thesis,
  but the lead justifies one more narrow look.
- **`PAUSE_STRATEGY_RESEARCH`** — rejected as the immediate default: there is a concrete,
  testable next question. (Pause becomes the recommendation if the narrow confirmation
  below comes back null.)

---

## Precommitted next diagnostic (for a FUTURE sprint — not run here)

A **read-only, no-strategy** confirmation of the single London lead, precommitted before
looking at results, designed to kill the multiple-comparisons / optimistic-cost concerns:

1. **Fix the hypothesis in advance:** post-compression (≥3/4 percentile features ≤ 0.20)
   first prior-range-break **continuation**, **London session only**, horizons {16, 32}.
   No other sessions, cuts, or horizons re-scanned (those were the multiple comparisons).
2. **Realistic execution:** model breakout-stop entry **with slippage**, an explicit
   protective stop (so trades can be stopped out **intrabar** before the horizon), and the
   measured London spread (not a flat optimistic 4.4). Report expectancy under this model.
3. **Multiple-testing honesty:** state that London was 1-of-12 cells; require a margin
   that survives a Bonferroni-style haircut, on both train and validation.
4. **Robustness, not optimization:** report the predeclared cut grid {0.10, 0.20, 0.30}
   and both horizons; **no** search for a better cut/horizon/stop.
5. **Kill criteria (precommitted):** if expectancy is not clearly > 0 net of realistic
   costs on **both** train and validation under the multiple-testing haircut, **retire the
   thesis** and move to `PAUSE_STRATEGY_RESEARCH`.
6. **TEST stays sealed** — opened only later for a single final confirmation of a fully
   precommitted campaign, never for exploration.

Only if that confirmation passes does a *subsequent* sprint design a precommitted campaign
(and only then is a campaign number discussed). This sprint creates none.

---

## Explicit statement

This decision creates **no** campaign, **no** C024, executes **no** C023, implements
**no** strategy, changes **no** verdict, approves **no** strategy, and leaves
paper/demo/live blocked and the TEST window sealed. The London-continuation lead advances
only to a *precommitted, overfit-hardened, read-only confirmation* in a future sprint,
gated by the kill criteria above.

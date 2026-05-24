# Turnover-Amplification Anti-Pattern (Discovery-005)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-005`
`strategy_evidence: false`

Phase 2 of discovery-005. Codifies the **turnover-amplification anti-
pattern** as a first-class, binding guardrail for every future
candidate proposal. The pattern is *empirically visible* in the
CAMPAIGN_011 → CAMPAIGN_012 → CAMPAIGN_013 sequence: each campaign
added a turnover-amplifying filter on top of a negative-edge entry
direction and produced materially worse results.

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.
> This doc adds a binding anti-pattern; it does not edit any campaign
> verdict.

## 1. The empirical slope (binding evidence)

Three real, executed walk-forward evidence sprints over the same
universe (7-pair OANDA practice H4 majors, 2020-01-01 → 2026-05-20,
8 folds rolling/frozen, same cost model, same inherited gates):

| campaign | filter shape | trades (8-fold) | aggregate expectancy R | aggregate PF | aggregate return % | pairs_positive |
|---|---|---:|---:|---:|---:|---:|
| **CAMPAIGN_011** (null model) | none — PRNG entry at `entry_probability = 0.05` per H4 bar per pair | **1,177** | **−0.0024** | **0.91** | **−0.53 %** | 3 / 7 |
| **CAMPAIGN_012** (regime switcher) | D1AGG ATR-percentile ≥ 0.70 HIGH-VOL gate amplifies the H4 trend-trigger qualifying-bar set | **3,726** | **−0.0521** | **0.034** | **−43.52 %** | 1 / 7 |
| **CAMPAIGN_013** (cross-pair rotator) | 8-currency strength rank-gap ≥ 4/7 fires on a much wider H4-bar slice across all 7 pairs simultaneously | **7,940** | **−0.0564** | **0.000** | **−113.36 %** | 1 / 7 |

The slope is **monotonic in trade count** on every binding axis:

- Trade count: 1,177 → 3,726 → 7,940 (×3.2 → ×6.7 vs null)
- Aggregate return %: −0.53 → −43.52 → −113.36 (×82 → ×214 worse vs null)
- Aggregate expectancy R: −0.0024 → −0.0521 → −0.0564 (×22 → ×24 worse vs null)
- Aggregate profit factor: 0.91 → 0.034 → 0.000 (decreasing monotonically toward zero)

The pattern is **NOT** that more trades necessarily produces worse
results in general. The pattern is **specific**:

> **On the 7-pair OANDA practice H4 universe, under the inherited
> cost model (ESTIMATED + conservative-stress financing, ATR-2
> stops, 6-bar max hold, 1-position-per-pair), adding a turnover-
> amplifying filter to a negative-edge entry direction has produced
> materially worse — not better — results in every case so far.**

The "negative-edge entry direction" is the H4 close-vs-close /
ranked-currency direction signal underlying CAMPAIGN_012 (trend) and
CAMPAIGN_013 (rotator). These directions have been shown to be no
better than random by CAMPAIGN_011's null floor; layering a filter
that *amplifies* their firing rate compounds spread + slippage cost
without offsetting edge.

## 2. What this pattern does and does not prove

### 2.1 What it DOES prove (binding)

- On the **current universe + cost model**, **high-turnover** H4
  major-pair entries are **highly vulnerable** to spread / slippage /
  financing costs. The cost-per-trade is roughly fixed; without an
  edge, more trades means more cumulative cost.
- Adding **turnover-amplifying filters** (regime gate that "selects
  hot bars", cross-sectional rank gate that "picks pairs to trade")
  on top of an **already-rejected entry direction** has, in every
  measured instance to date, produced materially **worse** results
  than the un-filtered random baseline. Both filters were
  pre-committed before any backtest, so the result is not a fishing
  artifact — it is a real, measured directional finding.
- A candidate whose proposal **assumes** more trades = more
  diversification = more positive expected value **must** explain
  why it does not fit the slope above. The default prior is now
  that turnover amplification on H4 majors hurts.

### 2.2 What it does NOT prove

- It does **not** prove that **all** low-turnover strategies work.
  Low turnover is necessary but not sufficient — a low-turnover
  candidate with negative per-trade expectancy will still reject;
  it will just reject closer to the null floor.
- It does **not** prove that **all** high-turnover strategies fail
  in **every** market or **every** universe. A different timeframe
  (D1, weekly) or a different cost model (institutional rates) or a
  different universe (e.g. crypto with tighter percentage spreads on
  some assets) might support higher-turnover signals. The pattern
  applies to the **inherited research configuration**, not to forex
  trading universally.
- It does **not** justify **curve-fitting a lower trade count after
  seeing results.** Picking a stricter threshold for a *rejected*
  candidate so it would have placed fewer trades is Pattern G
  (result-driven family selection) + Pattern H (same gate, different
  threshold) — both already forbidden by the base guardrails +
  discovery-004 addendum.
- It does **not** mean "any future high-turnover proposal is
  rejected sight unseen". It means the candidate must explicitly
  pre-declare its turnover budget and explain why net edge survives
  costs — see §4 below.

## 3. Why the slope is causal, not coincidental

A reasonable reader might ask whether the three data points are
sufficient to establish a binding pattern. The answer is yes,
because **each campaign's pre-commit was independent**, the
universe + cost model were identical, and the mechanism is
**economically grounded**:

| reason the slope is causal | detail |
|---|---|
| **shared universe + cost model** | all three campaigns ran on the same 7-pair OANDA practice H4 store, same ATR stops, same 6-bar max hold, same spread / slippage assumptions, same financing source (ESTIMATED + conservative stress) — the only variable is the entry filter |
| **cost-per-trade is roughly fixed** | the engine applies a per-trade spread cost based on the pair's typical bid/ask + slippage; this is approximately constant across the three campaigns. Trade count multiplies this cost linearly |
| **entry direction has been independently falsified** | CAMPAIGN_002's trend-following REJECT (−0.085 R) establishes that *within-pair* H4 directional momentum is not edge-bearing on this universe; CAMPAIGN_011's PRNG REJECT (−0.0024 R) establishes that *random* H4 directional entries are at the cost-floor; CAMPAIGN_012's regime-gated H4 trend was strictly worse than both; CAMPAIGN_013's cross-pair rank-direction was worse still. **Direction itself is the rejected component**; turnover amplifies the cost without changing the direction |
| **independent pre-commits** | each campaign's frozen parameters were pre-committed before any backtest fired (per `*_PRECOMMIT_CHECKLIST.md` for CAMPAIGN_010 / 011 and `*_IMPLEMENTATION_SPEC.md` + `CAMPAIGN_NN_*_PLAN.md` for CAMPAIGN_012 / 013). The slope was not produced by sweeping; it was produced by three independent honest experiments |
| **monotonic across multiple axes** | the slope holds on trade count, aggregate return, profit factor, and pairs_positive simultaneously. A spurious or single-axis pattern would not align on every binding axis |

This is enough evidence to make the pattern a **first-class anti-
pattern** binding all future candidate proposals on this universe
under this cost model.

## 4. Turnover-budget requirement for future candidates (binding)

Any future candidate proposed by any subsequent discovery sprint
**must** include the following in its scaffold-sprint pre-commit
checklist (`<CAMPAIGN_NN>_PRECOMMIT_CHECKLIST.md`):

### 4.1 Pre-declared expected trade-count range

- The proposal must state an **expected trade-count budget** for the
  full 8-fold walk-forward (e.g. "expected 200 – 600 trades over 4
  years; lower bound from minimum-trade-count gate; upper bound from
  the candidate's signal-rate model").
- The proposal must state **how that range was derived** (e.g. "from
  the candidate's signal-rate model: expected 1 firing per pair per
  month × 7 pairs × 48 months × 50 % qualification rate = 168
  trades"; or "from historical event-density on the calendar
  fixture").
- The proposal must explicitly note the **comparison to CAMPAIGN_011 /
  012 / 013** trade counts (1,177 / 3,726 / 7,940 respectively).

### 4.2 Pre-declared why signal frequency should be low enough to survive costs

- The proposal must articulate **why** the expected trade count is
  reasonable given the inherited cost model (e.g. "expected per-trade
  expectancy ≥ 0.10 R based on the hypothesis's first-principle
  analysis; per-trade cost ≈ 0.03 R; net expectancy ≈ 0.07 R; even
  at the upper trade-count bound, aggregate expectancy ≈ 0.07 R ≥
  0.05 R gate").
- The proposal must explicitly disclaim that **adding turnover-
  amplifying filters to rescue an under-performing candidate is
  forbidden** (i.e. if the candidate underperforms in screening, the
  response is REJECT, not "loosen the gate to fire more trades").

### 4.3 Pre-declared rejection if raw signal rate explodes relative to null

- If the candidate's actual trade count exceeds the upper bound of
  its pre-declared range **AND** the aggregate expectancy is not
  meaningfully positive, the evidence sprint must classify the
  candidate as **REJECT (turnover amplification)** in addition to
  the inherited gate verdict. This is a binding new sub-classification.
- "Meaningfully positive" here means at least at the CAMPAIGN_011
  meaningful-improvement margin: aggregate expectancy ≥ +0.05 R
  (i.e. ≥ +0.0524 above CAMPAIGN_011 null).

### 4.4 Pre-declared no `max_open_positions` relaxation, no risk-limit relaxation

- The candidate **may not** rescue a trade-count overshoot by
  loosening `max_open_positions`, risk per trade, max risk per pair,
  drawdown limits, or any other risk-engine setting.
- The candidate **may not** add a portfolio-wide `max_open_positions`
  cap *after* observing CAMPAIGN_013's results in order to claim
  turnover would be reduced.
- The candidate **may not** restrict to a sub-universe of pairs to
  rescue trade-count overshoot. Universe is part of family identity
  (per `REJECTED_FAMILY_OVERFIT_GUARDRAILS.md` §3).

## 5. Disqualified patterns (binding)

The following are now **binding disqualifying patterns** for any
future candidate proposal, in addition to Patterns A–G (base
guardrails) and Patterns H–L (discovery-004 addendum):

### 5.1 Pattern M — "high-frequency H4 firehose entries"

**Disqualified.** A candidate whose expected trade count is **≥ 2 ×
CAMPAIGN_013's count** (i.e. ≥ ~16,000 trades over 4 years on the
7-pair universe) is disqualified at the shortlist stage unless it
brings a **strong first-principles** edge argument that explicitly
quantifies why per-trade expectancy survives 6.7+ × the null trade
density.

**Why disqualified.** The slope above shows that even at 6.7 × null
density, aggregate return is −113.36 %. Doubling that without an
order-of-magnitude better per-trade edge is mathematically
guaranteed to produce a worse result; proposing it is asking the
reviewer to ignore the empirical slope.

**Legitimate alternative.** A lower-frequency candidate (≤ ~2,000
trades over 4 years; closer to or below CAMPAIGN_011's null trade
count) with the **same** per-trade expectancy bar.

### 5.2 Pattern N — "broad simultaneous multi-pair entries without portfolio-level edge proof"

**Disqualified.** A candidate that **routinely** opens positions in
≥ 3 pairs simultaneously **without** an explicit hypothesis that
*portfolio*-level (cross-correlated) PnL is edge-bearing is
disqualified.

**Why disqualified.** CAMPAIGN_013 routinely had simultaneous
positions across multiple pairs (~40 % of trades; see
`CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md` §7.4). Each
simultaneous signal paid full per-pair cost; the multi-pair entries
did not produce positive portfolio-level expectancy because the
per-pair signal was the underlying rejected component. A candidate
proposing simultaneous-multi-pair entries must include a
*portfolio-level* expectancy hypothesis (e.g. "we expect long-vol
on EUR + JPY simultaneously around event windows because the
straddle structure exploits correlation"), not just sum per-pair
signals.

**Legitimate alternative.** A single-pair / single-instrument
candidate (most of the 7 implemented strategies fit this), OR a
genuinely paired/structured candidate after the `infra-engine-
paired-entry-support-001` infrastructure unblock.

### 5.3 Pattern O — "adding filters that increase turnover while preserving rejected signal core"

**Disqualified.** A candidate that **inherits** any of CAMPAIGN_002 /
010 / 012 / 013's underlying entry direction (within-pair H4 trend,
H4 session-breakout direction, regime-gated H4 trend, cross-pair
rank direction) and adds a *new* filter that *increases* the
qualifying-bar set is disqualified.

**Why disqualified.** This is the explicit CAMPAIGN_011 → 012 → 013
slope shape. Adding a filter that *narrows* the qualifying-bar set
on the same signal core is also disqualified (per Pattern G /
Pattern H / Pattern K — result-driven narrowing of a rejected
direction), but turnover-amplifying additions are now their own
explicit disqualifier.

**Legitimate alternative.** A candidate whose entry **direction** is
genuinely new (not within-pair H4 trend, not H4 session-breakout, not
regime-gated H4 trend, not cross-pair rank).

### 5.4 Pattern P — "pair-only survivor selection from rejected campaigns"

**Disqualified.** A candidate that proposes trading **only** the
pair(s) that produced the least-negative per-pair result in any of
CAMPAIGN_002 / 010 / 012 / 013 (USD_JPY in all three of CAMPAIGN_011 /
012 / 013; GBP_USD in CAMPAIGN_011; USD_CHF in CAMPAIGN_011).

**Why disqualified.** These per-pair "winners" are at the random-walk
floor (USD_JPY's literally +0.0000 R across multiple campaigns is the
canonical example). Selecting them is result-driven family selection
(Pattern G) + per-pair tuning (Pattern D from base guardrails) +
fitting to noise within a REJECT aggregate (Pattern L from discovery-
004 addendum). A pair-only candidate is also implicitly **changing
the universe** (per `REJECTED_FAMILY_OVERFIT_GUARDRAILS.md` §3,
"universe is part of family identity"), requiring its own discovery
hypothesis.

**Legitimate alternative.** A candidate with a hypothesis that
*independently* implies a sub-universe (e.g. a carry candidate that
inherently trades only the pairs with the largest rate differentials —
but only after the infra-A MODELED financing unblock), proposed via
its own discovery sprint, with an explicit non-result-driven
universe choice.

### 5.5 Pattern Q — "cost-insensitive signal design"

**Disqualified.** A candidate proposal that does not explicitly
include a section on **per-trade cost handling** (spread, slippage,
financing) and how the expected per-trade expectancy survives those
costs is disqualified at the shortlist stage.

**Why disqualified.** CAMPAIGN_002 / 010 / 012 / 013 collectively
demonstrate that ignoring per-trade cost — even when each campaign's
gross signal looked plausible in isolation — produces REJECT after
costs. A proposal that does not directly address costs is *implicitly*
assuming a cost-insensitive signal; the empirical record says this
assumption is wrong on this universe.

**Legitimate alternative.** A proposal that includes:

- expected spread bp at trade entry (per pair, from existing
  fixtures)
- expected slippage bp (from the existing `FillModel` documentation)
- expected financing bp/day at hold (from ESTIMATED +
  conservative-stress source)
- expected per-trade gross expectancy
- expected per-trade net expectancy after the above
- expected aggregate net expectancy at the lower / mid / upper
  trade-count budget

## 6. How this pattern integrates with the base guardrails + discovery-004 addendum

| existing pattern | relation to turnover amplification |
|---|---|
| Pattern A (test-window leakage) | independent; the turnover-amplification slope is observational, not a window selection |
| Pattern B (filter-set tuning to losing trades) | adjacent; narrowing a filter to losing trades is forbidden, just as adding a filter to amplify turnover is — both are "tuning a rejected component" |
| Pattern C (parameter ranges spanning prior best-fit) | adjacent; sweeping a parameter to find a better trade count is forbidden, just as proposing a new amplifier is |
| Pattern D (implicit per-pair tuning) | reinforces Pattern P (pair-only survivor selection) |
| Pattern E (pick the best fold) | adjacent; turnover amplification interacts with fold-noise picking — the cost slope dominates the per-fold signal |
| Pattern F (rejection-criterion drift) | reinforces §4.3 (pre-declared rejection if raw signal rate explodes) |
| Pattern G (result-driven family selection) | reinforces Pattern P (no pair-only rescue) + Pattern O (no filter rescue) |
| Pattern H (same regime gate, different threshold) | special case of Pattern O for CAMPAIGN_012 |
| Pattern I (same trend filter, different lookback) | special case of Pattern O for CAMPAIGN_002 / 010 / 012 |
| Pattern J (same daily-ATR-percentile, different cutoff) | special case of Pattern O for CAMPAIGN_012 |
| Pattern K (rescue rejected regime switcher with session/pair/day filters) | special case of Pattern O for CAMPAIGN_012 + CAMPAIGN_010 stack |
| Pattern L (pick new family because it fixes a CAMPAIGN_012 per-fold artifact) | reinforces Pattern P for CAMPAIGN_012 / 013 |
| **Pattern M (high-frequency H4 firehose)** | **new (this addendum)** |
| **Pattern N (broad simultaneous multi-pair entries)** | **new (this addendum)** |
| **Pattern O (turnover-amplifying filter on rejected core)** | **new (this addendum); the headline pattern** |
| **Pattern P (pair-only survivor selection)** | **new (this addendum); specializes Pattern G** |
| **Pattern Q (cost-insensitive signal design)** | **new (this addendum)** |

(Pattern N–Q are the formal Phase 3 additions to the rejected-
family overfit guardrails; Pattern M codifies the upper-bound shape
of Pattern O.)

## 7. How discovery-005 itself must use this anti-pattern

The remaining phases of this sprint (Phase 4 reassessment, Phase 5
shortlist, Phase 6 selection, Phase 7 design) **must** explicitly
apply this anti-pattern:

- **Phase 4 reassessment** must score each path's expected turnover
  budget and its relation to the null trade count.
- **Phase 5 shortlist** must disqualify any proposal that trips
  Pattern M / N / O / P / Q.
- **Phase 6 selection** must explicitly cite which Patterns M–Q the
  selected path does **not** trip and why.
- **Phase 7 design** must include §4.1–4.4 (turnover budget,
  rationale, rejection rule, no-rescue) for a candidate path; or
  state explicitly "infrastructure paths do not trip Pattern M–Q"
  for an infra path.

## 8. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 875 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |

## 9. Cross-links

- [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md) (Phase 1 of this sprint)
- [`CAMPAIGN_013_EVIDENCE_SUMMARY.md`](CAMPAIGN_013_EVIDENCE_SUMMARY.md) (CAMPAIGN_013 numbers)
- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md) (CAMPAIGN_012 closeout)
- [`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md) (CAMPAIGN_012 numbers)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (CAMPAIGN_011 null baseline)
- [`CAMPAIGN_011_EVIDENCE_SUMMARY.md`](CAMPAIGN_011_EVIDENCE_SUMMARY.md) (CAMPAIGN_011 numbers)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) (Patterns A–G)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) (Patterns H–L)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (Phase 3 — to be written; integrates Patterns M–Q)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md) (Phase 0)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)

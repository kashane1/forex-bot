# Rejected-Family Overfit Guardrails

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-002`
`strategy_evidence: false`

Cross-cutting anti-overfit guardrails for every future candidate
proposal, derived from the cumulative experience of six
**rejected** campaigns (CAMPAIGN_002, CAMPAIGN_003, CAMPAIGN_004,
CAMPAIGN_007, CAMPAIGN_008, CAMPAIGN_009) plus the most recent
**CAMPAIGN_010**. **This document does not approve any strategy.**
It is the binding rule book any candidate proposal must satisfy
to clear the shortlist stage; it tightens the existing
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
§12 disqualifiers with concrete examples from each rejected
campaign.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`.

## 1. The 5 rejected families (the "do not revive" list)

| family | campaign labels | core entry mechanic | failure mode |
|---|---|---|---|
| **Trend-following** | CAMPAIGN_002, CAMPAIGN_003 | EMA-50/200 crossover + Donchian-20 break (CAMPAIGN_003 adds ADX-14 > 25 gate) | Negative expectancy on real H4 majors after costs (CAMPAIGN_002 −0.085 R; CAMPAIGN_003 −0.071 R). Random-entry baseline (CAMPAIGN_005) is −0.095 R; trend was no better. |
| **Volatility breakout** | CAMPAIGN_004 | ATR-percentile compression → Donchian-20 break | Negative expectancy (−0.163 R), the worst of the trend/breakout family — compressed-regime breakouts fade on H4 majors. |
| **Pullback continuation** | CAMPAIGN_007 | EMA pullback + continuation entry | Negative expectancy on screening splits (train −0.164 R, validation −0.166 R); test window never opened. |
| **Mean reversion** | CAMPAIGN_008, CAMPAIGN_009 | Z-score extreme reversion (c008) + midline-target exit (c009) | Train fold failed by a single gate for c008 (−0.017 R), and by a wider margin for c009 (−0.062 R). Validation was positive in both (~+0.17 R) but unconfirmed under pre-committed train gate. |
| **Session breakout** | CAMPAIGN_010 | Asian-range / London-open H4 breakout, continuation hypothesis | Negative expectancy on rolling walk-forward (−0.041 R aggregate, 0/8 folds pass, 1/7 pairs positive); financing strictly worsens. |

The common thread: **on H4 OANDA majors after costs, directional
entry signals do not generate a positive-expectancy edge under
pre-committed walk-forward gates.** Every parameter-tweak attempt
to date has failed by either (a) a wider margin on the same gate
or (b) flipping which gate fails.

## 2. The 5 disqualifying overfitting patterns (re-stated and tightened)

For each pattern from
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
§12, the concrete examples below illustrate what would fail the
shortlist gate going forward. **Any new proposal that fits any of
the "illegitimate" rows is rejected at shortlist stage.**

### 2.1 Pattern A — test-window leakage in design

| illegitimate | "USD_JPY ranged +46 % over 2020–2026 (per CAMPAIGN_005 always-long diagnostic). We propose a USD_JPY-only carry strategy because the period had a structural drift." |
|---|---|
| **why it fails** | Cites a specific 2020–2026 statistic as motivation for the candidate's universe choice. Any positive result on USD_JPY in 2020–2026 will be partly the documented drift, not a generalizable edge. |
| **legitimate alternative** | "Carry-aware long-only overlay on all 7 pairs (C2)" with universe **selected from the protocol's whitelist**, not from prior-window statistics. |

### 2.2 Pattern B — filter-set tuning to a prior campaign's losing trades

| illegitimate (CAMPAIGN_002 case) | "CAMPAIGN_002 lost on USD_CHF Donchian breaks during the SNB-floor era. Skip USD_CHF before 2015." |
|---|---|
| illegitimate (CAMPAIGN_010 case) | "CAMPAIGN_010 lost on AUD_USD and USD_CAD; restrict the new candidate to EUR_USD / GBP_USD / USD_JPY / USD_CHF." |
| illegitimate (CAMPAIGN_008/009 case) | "Mean reversion c008/c009 lost on the train fold; raise the z-score threshold from 2.0 to 2.5 to filter out the train-fold losers." |
| **why it fails** | Each "skip" or "filter" was motivated by a specific losing-trade subset of a rejected campaign. The strategy is being shaped *by* the failure, not designed independently. |
| **legitimate alternative** | A new strategy whose universe / parameters are pre-stated *before* viewing any rejected campaign's per-pair / per-fold breakdown. |

### 2.3 Pattern C — parameter ranges spanning prior best-fit values

| illegitimate (any prior campaign) | "Try `atr_stop_multiple ∈ {1.5, 2.0, 2.5}` — CAMPAIGN_002 / CAMPAIGN_004 / CAMPAIGN_010 all used 2.0; we'll sweep around that to find a better fit." |
|---|---|
| **why it fails** | Sweeping around a previously-failed value is parameter search disguised as "exploration"; the only correct response to a rejected parameter value is a different family, not a different value. |
| **legitimate alternative** | A new family with `atr_stop_multiple` chosen from independent reasoning (e.g. risk-budget normalization), then frozen — single value, no sweep. |

### 2.4 Pattern D — implicit per-pair tuning

| illegitimate (CAMPAIGN_010 case) | "session_breakout v0.2 with `min_atr_pips = {EUR_USD: 5.0, GBP_USD: 7.5, USD_JPY: 8.0, ...}` because the v0.1 result was uneven across pairs." |
|---|---|
| **why it fails** | The per-pair map's values are visibly derived from CAMPAIGN_010's per-pair output. Even if the proposal claims they came from "instrument-specific volatility characteristics", the values' source is the rejected campaign. |
| **legitimate alternative** | A single parameter set across all 7 pairs (no per-pair overrides). If a pair structurally cannot trade (e.g. NZD_USD's narrow effective universe in CAMPAIGN_010), drop it via the protocol's "universe is part of the family identity" route — a different universe is a different candidate, not a per-pair override. |

### 2.5 Pattern E — "pick the best fold"

| illegitimate | "CAMPAIGN_010 fold 6 (2024-12-05 → 2025-06-02) was marginally positive. The new candidate uses the same parameters but only trades 2024-12 → 2025-06 windows seasonally." |
|---|---|
| **why it fails** | The "winning" fold was identified post-hoc; using its date range as a feature is the canonical pick-the-best-fold pattern. |
| **legitimate alternative** | A seasonal hypothesis that is **pre-stated** and **theoretically motivated** (e.g. "year-end carry-trade unwind" with macro rationale), evaluated under walk-forward over the full universe — not a "trade only the fold that worked" rule. |

### 2.6 Pattern F — rejection-criterion drift

| illegitimate | "If the train fold expectancy is between −0.02 and 0.00 R, treat it as 'noise-floor' and proceed to validation anyway." |
|---|---|
| **why it fails** | The pre-commit gates are immutable. Any "graceful degradation" rule is just gate-relaxation in disguise. CAMPAIGN_008 was rejected by a single gate (train −0.017 R against ≥ 0 gate); the protocol correctly REJECTED it. Loosening that rule retroactively for any candidate would invalidate the entire screening discipline. |
| **legitimate alternative** | If a candidate's gates feel too strict, **change the gates in the pre-commit before any backtest** and document why; never adjust gates mid-evaluation. |

### 2.7 Pattern G — result-driven family selection

| illegitimate | "Now that CAMPAIGN_010 has failed, let's pick a new family that **looks like it would have made money** in the windows CAMPAIGN_010 lost. Candidate proposed: short-only on session_breakout's losing days." |
|---|---|
| **why it fails** | The new family is shaped by the inverse of a rejected family's losing days. Selection is post-hoc; the "edge" is the artifact of an in-sample look at CAMPAIGN_010's losses. |
| **legitimate alternative** | Family selection from the **distinctness rubric** (≥ 3 of 6 dimensions vs every prior rejected family), with no reference to CAMPAIGN_010's per-day, per-fold, or per-pair output beyond "this family is rejected". |

## 3. Universe-level guardrails

| guardrail | rule |
|---|---|
| **Universe is part of family identity.** | Changing from "7 pairs" to "6 pairs" (drop NZD_USD) is a different candidate, requiring its own discovery + pre-commit. It cannot be motivated by "NZD_USD had few trades in CAMPAIGN_010". |
| **Single parameter set across all pairs.** | Any per-pair override (parameter map keyed by instrument) is implicit per-pair tuning unless it is the candidate's primary edge (e.g. "carry rate" is naturally per-pair; "ATR multiple" is not). |
| **No "skip-X" universe filters motivated by prior losses.** | "Skip pair X because CAMPAIGN_002 / 004 / 007 / 010 lost on X" is filter-set tuning. |

## 4. Stop / exit / timeframe guardrails

| guardrail | rule |
|---|---|
| **ATR-multiple stops in `[1.0, 3.0]`.** | Anything outside this range needs an independent theoretical justification (e.g. "risk-budget normalization on volatility-regime X"). Inside the range, any specific value (2.0, 1.5, 2.5) is allowed only if frozen *before* any backtest. |
| **Time stop in `[1 H4 bar, 30 H4 bars]`.** | Outside this range needs justification. A time stop chosen specifically to "give CAMPAIGN_010-style trades more room" (e.g. 12 H4 bars instead of 6) is illegitimate. |
| **Trailing stop is opt-in v1 = none.** | Adding a trailing stop to a v1 design is allowed only if it is the candidate's primary edge (not an "improvement" on a rejected family's exit logic). |
| **Single-position-per-instrument** (engine-enforced). | Any straddle / pyramid / hedge structure requires a separate engine-extension sprint before the candidate can be evaluated. |

## 5. Data / financing guardrails

| guardrail | rule |
|---|---|
| **No new data source assumed.** | The 7-pair H4 OANDA practice store at `data/campaign_002.sqlite3` is the **only** authorized data source for any candidate this discovery sprint authorizes. New sources (D1 close, news events, intermarket data) require their own data-foundation sprint. |
| **No MODELED financing assumed.** | `default_stress_rate_source()` (conservative-stress, debit-only both sides) is the **only** authorized financing source. MODELED remains refused at four layers. A candidate whose headline result depends on MODELED financing is structurally blocked until a separate credentialed-pilot sprint lifts the MODELED layer. |
| **No new external dependency.** | No new pip-install, no new wheel, no new system library. |

## 6. Selection-process guardrails

| guardrail | rule |
|---|---|
| **Pre-commit before any code.** | Every candidate must have a `<CAMPAIGN_NN>_PRECOMMIT_CHECKLIST.md` with frozen parameters and gate vector *before* the future scaffold sprint adds a strategy module. |
| **Pre-commit before any run.** | The walk-forward plan, financing source, and per-fold + aggregate gates are committed before any backtest. The runner asserts the loaded YAML's parameter set matches the pre-commit verbatim. |
| **No re-running with altered parameters to improve results.** | If a fold fails due to a code / data bug, fix it; do not tune signal logic. CAMPAIGN_009 was REJECT and stayed REJECT — the freeze cannot "give it another chance". |
| **No post-hoc family selection.** | The Phase 3 "next preferred candidate" decision is made *before* any new backtest. Sliding the choice after seeing additional evidence is the §12.G pattern. |

## 7. Verifier-coverage guardrails

| guardrail | rule |
|---|---|
| **Independent corroboration is a paper-promotion gate, not a research-pass gate.** | A candidate can be REJECTED without verifier coverage; it cannot be PROMOTED without it. Item 5 of the six-evidence ladder is binding only for paper. |
| **Verifier extensions are sprint-scoped.** | Adding `session_breakout`, `random_entry`, or any other family to the free / local verifier is a separately-authorized sprint per `infra-free-local-parity-verifier-<FAMILY>-NNN`. It cannot be smuggled in as a side-effect of a candidate scaffold or evidence sprint. |

## 8. Approval-process guardrails

| guardrail | rule |
|---|---|
| **`configs/approved_strategies.yaml` only changes via a deliberate human edit.** | Per [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md). No automated promotion path exists. |
| **`live-loop` does not exist.** | Adding a `live-loop` command requires its own sprint and a separate approval; this protocol does not authorize it. |
| **No paper-loop / demo-loop enablement.** | Even after approval, paper-loop and demo-loop require the strategy to be in the registry AND the loop to be deliberately launched. Neither happens by accident. |

## 9. "Soft signs" the proposal is overfitting

These are **warning signs**, not automatic rejections, but a
shortlist proposal exhibiting two or more should be reconsidered:

- The proposal cites *specific* prior campaign metrics (per-pair,
  per-fold, per-window).
- The proposal's "expected edge" is small (e.g. "0.10 R per
  trade") and structurally similar to the gates' minimum
  threshold.
- The proposal's universe excludes a specific pair "because
  liquidity".
- The proposal's timeframe is a non-standard variant chosen to
  "avoid the noise floor" identified in CAMPAIGN_005.
- The proposal's exit logic includes a "graceful failure" rule
  ("if drawdown > X, switch to flat").

## 10. How to use this document

| reader | how to use |
|---|---|
| The Phase 2 reassessment in this sprint | Apply §§1–9 to every C2–C5 score; any candidate that trips §§2.A–2.G is dropped from the shortlist. |
| The Phase 3 "next preferred candidate" decision | The selected candidate must explicitly cite the relevant §§2 patterns *it does not exhibit*. |
| The future scaffold sprint | Read this file before writing the strategy module; if any rule it would adopt trips §§2–7, redesign before coding. |
| The future evidence sprint | Read this file before running any backtest; if any per-pair / per-fold result tempts a parameter change, the answer is "no — REJECT or PASS as committed". |
| The human approval action (if it ever happens) | This file plus [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md) is the audit trail showing the candidate was not curve-fit. |

## 11. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
  §12 (the original disqualifier list)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
  (CAMPAIGN_010-specific cooldown rule)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
  (the prior shortlist that C2-C5 came from)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)

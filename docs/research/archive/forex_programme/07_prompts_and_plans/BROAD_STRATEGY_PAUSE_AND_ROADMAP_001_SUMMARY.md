# Broad Strategy Pause and Roadmap — Sprint 001 Summary

**Date:** 2026-05-26  
**Branch:** `research-broad-strategy-pause-and-roadmap-001`  
**Base:** `research-post-dedup-failure-meta-analysis-001`

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_018 was **not** created.

---

## 1. Sprint outcome

Formally **paused** broad seven-pair pattern strategy campaigns after post-dedup failure meta-analysis. Documented re-entry gates, compared eight non-strategy workstreams, and selected **`infra-observed-cost-and-spread-regime-diagnostics-001`** as the next sprint.

---

## 2. Commits by phase

| phase | description | commit |
|---:|---|---|
| 0 | Truth audit + plan | `fab5451` |
| 1 | Broad strategy search pause memo | `5dfb2ca` |
| 2 | Archive status updates | `4313569` |
| 3 | Non-strategy workstream options | `68d6a3d` |
| 4 | Next workstream decision | `5414528` |
| 5 | Next sprint prompt | `9de9e3b` |
| 6 | This summary + final validation | (this commit) |

---

## 3. Why broad strategy search is paused

Three dedup-safe broad pattern families (CAMPAIGN_015 failed breakout reversal, CAMPAIGN_016 weekly cross-sectional momentum, CAMPAIGN_017 weekly volatility contraction breakout) are all **REJECT** with anti-overfit **WITHIN_NULL** versus the canonical deduped null (CAMPAIGN_011, exp_r **−0.0029 R**). Post-dedup meta-analysis found **NO_RELIABLE_ARCHETYPE** — no pair, fold, side, or exit dimension survives at tradable magnitude. All candidates **worsen under 2× cost**. Another broad campaign (CAMPAIGN_018) would repeat a known failure mode without a new falsifiable hypothesis.

---

## 4. Campaigns included

| campaign | role | base exp_r | verdict | anti-overfit |
|---|---|---:|---|---|
| CAMPAIGN_011 | deduped null baseline | −0.0029 | REJECT (null anchor) | n/a |
| CAMPAIGN_015 | failed_breakout_reversal | −0.0101 | REJECT | WITHIN_NULL |
| CAMPAIGN_016 | weekly_cross_sectional_momentum | −0.0633 | REJECT | WITHIN_NULL |
| CAMPAIGN_017 | weekly_volatility_contraction_breakout | −0.0227 | REJECT | WITHIN_NULL |

---

## 5. Re-entry gates (summary)

Full detail: [`BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md`](BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md) §7.

**Structural (≥1):** new external data · new market-structure thesis · observed-cost/financing model · extended history · different validated timeframe · independent academic/institutional thesis.

**Pre-registration (all):** new falsifiable hypothesis (not C015–C017 retune) · expected beat-null **≥ 0.05 R** with minimum trade count · DEDUPED_INPUT only · Backtrader path defined or scoped diagnostic · human decision memo (still no `approved_strategies.yaml` edit).

**Anti-pattern:** must not be another indicator variant on the same H4 seven-pair template without structural edge.

---

## 6. Non-strategy workstreams compared

Eight options scored in [`NON_STRATEGY_WORKSTREAM_OPTIONS_AFTER_PAUSE.md`](NON_STRATEGY_WORKSTREAM_OPTIONS_AFTER_PAUSE.md):

1. Observed transaction-cost model — **P0**
2. Observed financing / rollover — P1
3. Spread-regime & session diagnostics — **P0**
4. Data expansion — P2
5. Broker fill/slippage replay — P3
6. Backtrader parity hardening — P2
7. Portfolio/risk simulator — P3
8. Stop all research — deferred

---

## 7. Selected next workstream

**`infra-observed-cost-and-spread-regime-diagnostics-001`**

Combines observed transaction-cost distributions and spread-regime/session diagnostics on local deduped H4 bid/ask data.

Decision record: [`NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md`](NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md).  
Agent prompt: [`NEXT_SPRINT_PROMPT_AFTER_BROAD_STRATEGY_PAUSE.md`](NEXT_SPRINT_PROMPT_AFTER_BROAD_STRATEGY_PAUSE.md).

---

## 8. Why selected

Strategies fail at or below null and degrade under 2× cost — before more entries, the project needs a **descriptive cost atlas** (spread, spread/ATR, session, weekday, vol regime) to judge whether certain windows are structurally untradeable. This sprint is fully local for phase 1, does not require broker order APIs, and carries low overfitting risk because it produces **gating recommendations only**, not campaigns.

---

## 9. Safety checks

| check | result |
|---|---|
| CAMPAIGN_018 created | **no** |
| Strategy approved | **no** — `approved: []` |
| Paper / demo / live | **blocked** — freeze gate PASS |
| pytest | 1565 passed |
| ruff | All checks passed |
| research freeze | ALL CHECKS PASSED |
| archive validation | ALL CHECKS PASSED |
| secret scan | PASSED |
| .env / credentials / SQLite / bulky dumps staged | **none** |

---

## 10. Files to review first

1. [`BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md`](BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md) — pause rationale and re-entry gates
2. [`NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md`](NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md) — selected sprint
3. [`NEXT_SPRINT_PROMPT_AFTER_BROAD_STRATEGY_PAUSE.md`](NEXT_SPRINT_PROMPT_AFTER_BROAD_STRATEGY_PAUSE.md) — copy-paste next agent prompt
4. [`POST_DEDUP_FAILURE_META_ANALYSIS_001_SUMMARY.md`](POST_DEDUP_FAILURE_META_ANALYSIS_001_SUMMARY.md) — evidence inputs
5. [`NON_STRATEGY_WORKSTREAM_OPTIONS_AFTER_PAUSE.md`](NON_STRATEGY_WORKSTREAM_OPTIONS_AFTER_PAUSE.md) — full option comparison

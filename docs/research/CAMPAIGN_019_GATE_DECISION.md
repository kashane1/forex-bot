# CAMPAIGN_019 — Gate Decision

**Date:** 2026-05-27  
**Branch:** `research-campaign-019-thesis-invalidation-execution-001`

---

## Inputs

| Source | Result |
|---|---|
| `research/campaign_019/gate_result.json` | screening_pass: **false**, verdict: **REJECT** |
| Backtrader parity | **CLOSE_MATCH** / ±1 trade — **PASS** |

---

## Screening decision

**FAIL** — 3 of 12 binding gates failed:

- train expectancy ≥ 0
- train expectancy ≥ C008 deduped train (−0.025 R)
- full stress_15x expectancy ≥ 0

9 gates passed including validation expectancy (+0.0962 R), beat-null vs C011, thesis_invalidation
mechanism active (12.6%), zero target/protective exits, validation PF ≥ 1.05, and 2× cost stress.

---

## Test lockbox decision

**CLOSED** — screening failure blocks test per precommit. Test window **not executed**.

---

## Final campaign classification

| Field | Value |
|---|---|
| Verdict | **REJECT** |
| Hypothesis | **Falsified on train** (primary binding gate) |
| Backtrader parity | PASS |
| Test lockbox | NOT OPENED |
| Strategy approved | **false** |
| Max status reached | REJECT (not RESEARCH_PASS) |

---

## No approval statement

CAMPAIGN_019 does not enter `configs/approved_strategies.yaml`. No paper/demo/live enablement.

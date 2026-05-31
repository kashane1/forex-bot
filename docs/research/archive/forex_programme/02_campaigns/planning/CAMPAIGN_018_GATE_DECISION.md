# CAMPAIGN_018 Gate Decision

**Date:** 2026-05-27  
**Branch:** `research-campaign-018-protective-stop-execution-001`

> **Gate decision memo** — precommitted rules applied without modification.

---

## Screening outcome

| field | value |
|---|---|
| screening_pass | **false** |
| verdict | **REJECT** |
| test_window_opened | **false** |

---

## Failed gates

| gate | required | observed |
|---|---|---|
| train_expectancy_gte_zero | ≥ 0 | **−0.119 R** |
| full_stress_15x_expectancy_gte_zero | ≥ 0 | **negative** (full-window aggregate) |

---

## Passed gates

validation exp > 0 (+0.194), PF ≥ 1.05 (1.58), 6/6 pairs, 142 trades, 2× stress +0.178, beat-null vs C011, mechanism active (53.3%), zero targets.

---

## Test lockbox

**Closed.** See [`CAMPAIGN_018_TEST_LOCKBOX_NOT_OPENED.md`](CAMPAIGN_018_TEST_LOCKBOX_NOT_OPENED.md).

---

## Classification

**REJECT** — binding train gate failure. Not REVISE / RESEARCH_PASS (screening did not pass).

---

## No approval

Passing validation alone is insufficient. No registry update. No paper/demo/live.

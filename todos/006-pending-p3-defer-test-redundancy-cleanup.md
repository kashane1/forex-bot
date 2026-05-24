---
status: pending
priority: p3
issue_id: 006
tags: [code-review, sprint:infra-exit-fidelity-001, tests, simplification, deferred]
dependencies: []
---

# (Deferred) Reduce gap-fill test redundancy now that property test exists

## Problem Statement

The code-simplicity-reviewer flagged that the gap-fill test surface has 48 cases across 3 parametrized tests (`test_gap_fill_matrix` × 16, `test_policy_none_disables_gap_fill` × 16, `test_gap_fill_invariants` × 16). The property test (`test_gap_fill_invariants`) asserts the core invariants — fills at bar-open, distance is non-negative, none-policy disables gap-fill — across its own 16-case grid. It strictly subsumes the matrix tests for invariant checking.

The architecture-strategist explicitly defended the matrix for "audit-trail bait" (a researcher searching for "did anyone test short-side TP gap-fill under next_bar_open with the risk engine?" can find the named case). So this is a real trade-off, not a clear cleanup.

## Findings

- **tests/unit/test_gap_fill.py** — `test_gap_fill_matrix` + `test_policy_none_disables_gap_fill` + `test_gap_fill_invariants` = 48 cases. ~0.4s of total test runtime (negligible).
- The 16-case matrix gives diagnostic test IDs (e.g. `long-stop-sbc-norisk`) — valuable for triage when a failure occurs.

## Proposed Solutions

### Option A (defer): keep all 48 cases

- **Pros**: audit-trail; diagnostic IDs; no risk of losing coverage.
- **Cons**: ~80 LOC of test boilerplate; 32 cases that the property test would catch.
- **Effort**: 0.
- **Risk**: None.

### Option B: drop `test_gap_fill_matrix` + `test_policy_none_disables_gap_fill`, keep property test + add a 4-case smoke

- **Pros**: −28 tests, −~120 LOC.
- **Cons**: loses the named test IDs (`pytest -k "long-stop"` no longer surfaces specific scenarios).
- **Effort**: Small (20 min).
- **Risk**: Lose audit-trail value.

### Recommended Action: DEFER. Revisit when/if test runtime becomes a problem or when a future sprint touches the gap-fill test module for unrelated reasons.

## Acceptance Criteria

(N/A — deferred. Reopen when triggered.)

## Work Log

- 2026-05-24: created from code-simplicity-reviewer item 1. Deferred per architecture-strategist's audit-trail rationale.

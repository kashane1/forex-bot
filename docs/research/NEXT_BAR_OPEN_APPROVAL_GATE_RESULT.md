# next_bar_open — Approval / Promotion Gate Result

**Sprint:** `infra-next-bar-open-policy-and-htf-align-migration-001` · **Date:** 2026-05-27

## Scope

Promotion-readiness checks for **execution realism metadata** only. Does not modify paper/demo/live loops, broker construction, or OANDA APIs.

## Implementation

| Component | Behavior |
|-----------|----------|
| `execution_realism.promotion_readiness_errors()` | Blocks: missing metadata, `promotion_eligible: false`, unknown/missing `fill_timing`, `signal_bar_close` (with or without justification), non-conservative `execution_realism` |
| `execution_realism.is_promotion_ready()` | Convenience wrapper |
| `approval.execution_realism_promotion_blockers()` | Same checks, exposed for promotion review workflows |
| `configs/approved_strategies.yaml` | **Unchanged — `approved: []`** |
| `approval.assert_loop_strategies_approved()` | **Unchanged** — still refuses all unapproved strategies |

## Test outcomes

- Missing `fill_timing` → blocks promotion readiness
- `signal_bar_close` + `approval_bound` → fails at parse time
- `signal_bar_close` + `diagnostic` + justification → passes parse, **not** promotion-ready
- `next_bar_open` + `approval_bound` → no execution-realism blockers (other gates still apply)
- Registry load → empty list

## Explicit non-goals

- Did **not** enable paper/demo/live
- Did **not** add approved strategies
- Did **not** call OANDA mutation endpoints
- Did **not** change executor fill path defaults

## No-approval statement

`next_bar_open` metadata is necessary but **not sufficient** for approval. All strategies remain unapproved.

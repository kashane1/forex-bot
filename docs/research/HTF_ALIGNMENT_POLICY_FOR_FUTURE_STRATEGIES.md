# HTF Alignment Policy — Future Strategies

**Date:** 2026-05-27 · **Sprint:** `infra-next-bar-open-policy-and-htf-align-migration-001`

## Required alignment helper

Future HTF strategies (D1 / H4 / D1AGG gates on faster execution bars) must use:

```python
from forex_bot.features.htf_align import align_last_completed
```

or the approved D1AGG wrapper `forex_bot.features.d1agg_htf` (which calls `align_last_completed` internally).

**Exception:** weekly / completed-period strategies may use completed-week compression helpers if documented in precommit (C016/C017 pattern).

## Rules

1. **No native OANDA D1** for research where **D1AGG** is required (H4→daily aggregation contract).
2. **Incomplete HTF bars** must never drive signals (`complete=True` only).
3. **No future HTF values** — aligned feature time ≤ decision time; record `htf_feature_time` / `htf_feature_times` on signals where practical.
4. **Exact timestamp joins** are suspect unless `complete` flag proves bar availability.
5. **HTF_UNAVAILABLE / HTF_STALE** — handle explicitly; do not silently forward-fill from incomplete bars.
6. **RSI / indicators** — prefer `warmup_policy="nan"` for new code.

## Fill timing (paired policy)

Approval-bound precommits must also declare fill timing per [`FILL_TIMING_APPROVAL_BOUND_POLICY.md`](FILL_TIMING_APPROVAL_BOUND_POLICY.md):

- Default: `fill_timing: next_bar_open`
- `signal_bar_close` only for diagnostic / legacy / upper-bound with `promotion_eligible: false`

## Precommit checklist additions

Add to future campaign precommits:

- [ ] HTF alignment module (`htf_align` or justified exception)
- [ ] D1AGG vs native D1 declaration
- [ ] `fill_timing` + `evidence_use` + `promotion_eligible`
- [ ] Multi-day strategies: `financing_treatment` / observed vs modeled declaration

## Reference

- Module result: [`SHARED_HTF_ALIGN_MODULE_RESULT.md`](SHARED_HTF_ALIGN_MODULE_RESULT.md)
- Migration: [`HTF_ALIGN_MIGRATION_RESULT.md`](HTF_ALIGN_MIGRATION_RESULT.md)
- MTF audit: [`MTF_ALIGNMENT_AUDIT_RESULT.md`](MTF_ALIGNMENT_AUDIT_RESULT.md)

## No-approval statement

Policy only. No strategy approved.

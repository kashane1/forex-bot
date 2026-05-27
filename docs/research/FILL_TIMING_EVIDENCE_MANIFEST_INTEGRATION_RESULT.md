# Fill Timing — Evidence Manifest Integration Result

**Sprint:** `infra-next-bar-open-policy-and-htf-align-migration-001` · **Date:** 2026-05-27

## Artifacts updated

| Artifact | Changes |
|----------|---------|
| `docs/research/EVIDENCE_MANIFEST.json` | Top-level `execution_realism_policy`; CAMPAIGN_019 campaign entry: `fill_timing`, `execution_realism`, `evidence_use`, `promotion_eligible`, `fill_timing_justification`, `next_bar_open_validation_expectancy_r` |
| `docs/research/FILL_TIMING_APPROVAL_BOUND_POLICY.md` | Canonical policy doc |
| `docs/research/EVIDENCE_INDEX.md` | Infrastructure sprint cross-links (phase 9) |
| `docs/research/STRATEGY_STATUS.md` | C019 fill-timing note (phase 9) |

## Manifest fields (campaign entries)

Future campaign entries should include when known:

```json
"fill_timing": "next_bar_open",
"execution_realism": "conservative",
"evidence_use": "approval_bound",
"promotion_eligible": false,
"fill_timing_justification": null
```

## C019 recording (no verdict change)

- **Committed run:** `signal_bar_close`, validation +0.0962 R — **optimistic upper bound**
- **Comparison:** `next_bar_open` validation +0.0175 R (~−0.079 R delta)
- **Verdict:** REJECT unchanged
- **Future approval-bound campaigns:** require `next_bar_open` unless justified

## Schema checks

`scripts/validate_research_archive.py` → `check_execution_realism_policy()` passes when policy block declares `next_bar_open` default.

## No-approval statement

No historical verdict rewritten to PASS. No strategy added to `approved_strategies.yaml`.

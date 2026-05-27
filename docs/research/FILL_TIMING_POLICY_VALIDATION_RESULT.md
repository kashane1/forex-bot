# Fill Timing Policy — Validation Result

**Sprint:** `infra-next-bar-open-policy-and-htf-align-migration-001` · **Date:** 2026-05-27

## Code paths changed

| Path | Change |
|------|--------|
| `src/forex_bot/research/execution_realism.py` | New — `ExecutionRealismMetadata`, enums, `parse_research_metadata`, `promotion_readiness_errors`, `validate_campaign_yaml_metadata`, `legacy_mode_metadata`, `classify_historical_campaign` |
| `src/forex_bot/research_archive.py` | `check_execution_realism_policy()` in `validate_archive()` |
| `src/forex_bot/approval.py` | `execution_realism_promotion_blockers()` re-export for promotion review |

## Fields added (metadata contract)

- `fill_timing`, `execution_realism`, `evidence_use`, `promotion_eligible`, `fill_timing_justification`
- Optional YAML block `research_metadata` (validated when present; **not** merged into `Settings` — avoids breaking `load_settings`)

## Compatibility behavior

- Campaign YAML **without** `research_metadata`: loads unchanged; `validate_campaign_yaml_metadata({})` returns no errors.
- Manifest `execution_realism_policy` block: when present, `approval_bound_fill_timing_default` must be `next_bar_open`.
- Historical C019: fill-timing fields on manifest campaign entry only (not in campaign YAML).

## Tests added

`tests/unit/test_execution_realism_policy.py`:

- approval-bound + `next_bar_open` → promotion readiness OK
- approval-bound + `signal_bar_close` → pydantic validation error
- diagnostic + `signal_bar_close` → not promotion-ready
- legacy empty YAML compat
- unknown fill_timing blocks promotion
- approved registry empty

## Remaining gaps

- Precommit YAML templates not yet uniformly updated with `research_metadata` block (documented in policy + HTF template phase).
- No automatic scan of all `backtests/*/summary.json` `fill_timing` fields into manifest (manual C019 + policy block only).
- Loop / broker paths unchanged — promotion gate is metadata-only.

## No-approval statement

Infrastructure only. No strategy approved.

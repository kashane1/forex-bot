---
status: complete
priority: p2
issue_id: 003
tags: [code-review, sprint:infra-exit-fidelity-001, hash-regression, data-integrity]
dependencies: []
---

# Extend pre-sprint hash snapshot to cover campaign_003 and campaign_006

## Problem Statement

The data-integrity-guardian review confirmed the hash invariant holds for the 3 pinned configs (campaign_001, campaign_004, campaign_009) — but flagged that `campaign_003_controlled_adx` (hash `3ce2c5242f5d6ec8`) and `campaign_006_daily_trend` (hash `e2414cc376431d70`) have unique hashes NOT pinned anywhere. A future refactor that touches those specific parameter values could silently drift their hashes without tripping the regression test.

(`campaign_002` collides with 001 and `campaign_008` collides with 009, so they are implicitly covered. `campaign_007` fails to build strategies — pre-existing, unrelated.)

## Findings

- **tests/fixtures/pre_sprint_config_hashes.json** — currently 3 pinned hashes.
- **scripts/snapshot_pre_sprint_hashes.py:50-54** — `PINNED` list has 3 entries; needs `("campaign_003_controlled_adx", "configs/campaign_003_controlled_adx.yaml")` and `("campaign_006_daily_trend", "configs/campaign_006_daily_trend.yaml")`.
- **tests/unit/test_ambiguous_exit.py:518-536** — `test_strategy_config_hash_input_types_are_repr_stable` also iterates a hard-coded 3-config list; will need the same extension.

## Proposed Solutions

### Option A (recommended): extend PINNED + regenerate snapshot + update type-stability test

1. Add the 2 missing configs to `PINNED` in `scripts/snapshot_pre_sprint_hashes.py`.
2. Run `python scripts/snapshot_pre_sprint_hashes.py` to regenerate the fixture. The `_doc` header stays the same; only the hash entries grow.
3. Update `test_strategy_config_hash_input_types_are_repr_stable` to import `PINNED` from the script (DRY) and iterate it instead of hard-coding 3.

- **Pros**: closes the coverage gap before any code change makes it impossible to baseline; turns a 3-of-8 cover into a 5-of-8 (the remaining 3 are duplicates by hash or untestable).
- **Cons**: snapshot fixture is touched (but legitimately so — adding entries, not changing existing ones).
- **Effort**: Small (10 min).
- **Risk**: None if done now; HIGH if deferred past any future engine refactor.

### Recommended Action: Option A, do it before any other engine refactor.

## Acceptance Criteria

- [ ] `scripts/snapshot_pre_sprint_hashes.py` `PINNED` list has 5 entries
- [ ] `tests/fixtures/pre_sprint_config_hashes.json` has 5 hash entries + the unchanged `_doc` header
- [ ] `test_strategy_config_hash_input_types_are_repr_stable` iterates the same 5 configs (imports `PINNED` from the script)
- [ ] Existing 3 hashes are byte-identical (only adding, never changing)
- [ ] `pytest tests/` green
- [ ] `test_snapshot_doc_guardrail` still passes (the `_doc` warning string is preserved verbatim)

## Work Log

- 2026-05-24: created from data-integrity-guardian caveat #1 + #2.
- 2026-05-24: **resolved**. Added campaign_003 + campaign_006 to PINNED (now 5 configs). Regenerated `tests/fixtures/pre_sprint_config_hashes.json` — 3 existing hashes byte-identical. New hashes: campaign_003=`3ce2c5242f5d6ec8`, campaign_006=`e2414cc376431d70`. Updated `test_strategy_config_hash_input_types_are_repr_stable` to import `PINNED` from the script (auto-extends). pytest 792 passed, ruff clean.

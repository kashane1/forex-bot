# next_bar_open Policy and HTF Align Migration — Summary

**Branch:** `infra-next-bar-open-policy-and-htf-align-migration-001`  
**Base:** `infra-observed-financing-capture-readonly-002` @ `cbead73`  
**Date:** 2026-05-27  
**Sprint type:** infrastructure / policy only

## 1. Branch name

`infra-next-bar-open-policy-and-htf-align-migration-001`

## 2. Commit hashes by phase

| Phase | Commit | Subject |
|-------|--------|---------|
| 0 | `18ef5c5` | Phase 0 plan |
| 1 | `12c331b` | fill_timing approval-bound policy |
| 2 | `350be88` | execution realism metadata validation |
| 3 | `2f449e6` | evidence manifest integration |
| 4 | `5118c62` | promotion gate helpers |
| 5 | `db7376c` | HTF migration design |
| 6 | `0c4222f` | regime_switcher → d1agg_htf |
| 7 | `c1b8d11` | HTF policy for future strategies |
| 8 | `e0e4430` | campaign validity impact memo |
| 9 | `e646b97` | evidence index and backlog |
| 10 | `TBD` | final summary (this commit) |

## 3. Files changed by phase

| Phase | Primary paths |
|-------|----------------|
| 0 | `docs/research/NEXT_BAR_OPEN_POLICY_AND_HTF_ALIGN_MIGRATION_001_PLAN.md` |
| 1 | `docs/research/FILL_TIMING_APPROVAL_BOUND_POLICY.md` |
| 2 | `src/forex_bot/research/execution_realism.py`, `src/forex_bot/research_archive.py`, `tests/unit/test_execution_realism_policy.py`, `docs/research/FILL_TIMING_POLICY_VALIDATION_RESULT.md` |
| 3 | `docs/research/EVIDENCE_MANIFEST.json`, `docs/research/FILL_TIMING_EVIDENCE_MANIFEST_INTEGRATION_RESULT.md`, `docs/research/STRATEGY_STATUS.md` |
| 4 | `src/forex_bot/approval.py`, `docs/research/NEXT_BAR_OPEN_APPROVAL_GATE_RESULT.md` |
| 5 | `docs/research/HTF_ALIGN_MIGRATION_DESIGN.md` |
| 6 | `src/forex_bot/features/d1agg_htf.py`, `src/forex_bot/strategies/regime_switcher_atr_percentile.py`, `tests/unit/test_d1agg_htf_migration.py`, `tests/unit/test_regime_switcher_atr_percentile.py`, `docs/research/HTF_ALIGN_MIGRATION_RESULT.md` |
| 7 | `docs/research/HTF_ALIGNMENT_POLICY_FOR_FUTURE_STRATEGIES.md`, `docs/research/CAMPAIGN_012_PRECOMMIT_CHECKLIST.md` |
| 8 | `docs/research/CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_NEXT_BAR_OPEN_POLICY_AND_HTF_MIGRATION.md` |
| 9 | `docs/research/EVIDENCE_INDEX.md`, `docs/research/FUTURE_RESEARCH_BACKLOG.md` |
| 10 | `docs/research/NEXT_BAR_OPEN_POLICY_AND_HTF_ALIGN_MIGRATION_001_SUMMARY.md` |

## 4. Baseline validation result

At sprint start (post-`cbead73`): pytest **1772 passed** after reverting invalid `research_metadata` on C019 YAML (Settings forbids extra fields). Final: pytest **1773 passed**, ruff clean, `check_research_freeze.py` OK, `validate_research_archive.py` OK, `scan_artifacts_for_secrets.py` OK.

## 5. Fill timing policy summary

- Approval-bound / promotion-review evidence must use **`next_bar_open`** unless justified.
- **`signal_bar_close`** = optimistic upper bound / diagnostic; **`promotion_eligible: false`**.
- C019 validation: +0.0962 R (close) vs +0.0175 R (open); Δ **~−0.079 R**.

## 6. Config/schema validation changes

- `ExecutionRealismMetadata` in `execution_realism.py`
- Optional `research_metadata` YAML block validated separately (not in `Settings`)
- Manifest `execution_realism_policy` requires `approval_bound_fill_timing_default: next_bar_open`

## 7. Evidence manifest/status integration

- C019 manifest fields: `fill_timing`, `execution_realism`, `evidence_use`, `promotion_eligible`, `next_bar_open_validation_expectancy_r`
- `STRATEGY_STATUS.md` C019 fill-timing note
- Sprint block `next_bar_open_policy_and_htf_align_migration_001` in manifest

## 8. Approval/promotion gate changes

- `promotion_readiness_errors()` / `approval.execution_realism_promotion_blockers()`
- **No** change to loop broker construction or `approved_strategies.yaml`

## 9. htf_align migration target selected

**Regime switcher D1AGG** (`regime_switcher_atr_percentile`) via `d1agg_htf` + `htf_align.align_last_completed()`.

## 10. htf_align migration result

Fixture-equivalent ATR/regime; **no** `BLOCKED_BEHAVIOR_CHANGE_RISK`. Additive `htf_feature_times` on signals.

## 11. HTF policy/template updates

- [`HTF_ALIGNMENT_POLICY_FOR_FUTURE_STRATEGIES.md`](HTF_ALIGNMENT_POLICY_FOR_FUTURE_STRATEGIES.md)
- CAMPAIGN_012 precommit §17 infrastructure template

## 12. C019 impact

**Verdict unchanged: REJECT.** Validation uplift interpreted as partly optimistic.

## 13. Impact on prior signal_bar_close campaigns

Not auto-invalidated; treat validation uplifts as **upper-bound** where timing was `signal_bar_close`. No mass rerun.

## 14. Impact on prior HTF campaigns

C012 artifacts not rerun; code path refactored only. Weekly C016/C017 unchanged.

## 15. Whether any rerun is required

**No** for verdicts. Optional future sensitivity reruns documented in validity memo.

## 16. CAMPAIGN_020 created?

**No.**

## 17. Any strategy approved?

**No.** `approved: []`.

## 18. Paper/demo/live blocked?

**Yes.**

## 19. Executor/broker behavior changed?

**No** (policy/readiness metadata only).

## 20. OANDA mutation APIs called?

**No.**

## 21. Live environment used?

**No.**

## 22. Credentials/secrets printed or committed?

**No.**

## 23. Raw transactions/account IDs committed?

**No.**

## 24. Tests added

- `tests/unit/test_execution_realism_policy.py` (8 tests)
- `tests/unit/test_d1agg_htf_migration.py` (2 tests)

## 25. Validation commands run

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```

## 26. Remaining WARN/BLOCKED items

- Observed financing capture: **BLOCKED_READONLY_CREDENTIALS** / await human overnight sample
- Broad strategy search: **PAUSED**
- Legacy campaigns lack uniform `research_metadata` in YAML (manifest/policy only)
- Confluence / weekly HTF paths not migrated

## 27. Recommended next sprint

`practice-overnight-sample-and-capture-execute` — human practice hold, then read-only financing capture execute.

## 28. Files to review first

1. [`FILL_TIMING_APPROVAL_BOUND_POLICY.md`](FILL_TIMING_APPROVAL_BOUND_POLICY.md)
2. [`src/forex_bot/research/execution_realism.py`](../../src/forex_bot/research/execution_realism.py)
3. [`HTF_ALIGN_MIGRATION_RESULT.md`](HTF_ALIGN_MIGRATION_RESULT.md)
4. [`src/forex_bot/features/d1agg_htf.py`](../../src/forex_bot/features/d1agg_htf.py)
5. [`CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_NEXT_BAR_OPEN_POLICY_AND_HTF_MIGRATION.md`](CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_NEXT_BAR_OPEN_POLICY_AND_HTF_MIGRATION.md)
6. [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json) — `execution_realism_policy` + C019 fields

---

## Compact table

| Area | Previous Status | Action Taken | New Status | Tests Added | Prior Campaign Impact | Future Rule |
|------|-----------------|--------------|------------|-------------|----------------------|-------------|
| Fill timing policy | WARN; informal | Canonical policy + `execution_realism.py` | Mechanical for new approval-bound evidence | 8 policy tests | C019 tagged upper-bound; verdicts unchanged | `next_bar_open` default |
| Manifest | No fill_timing fields | C019 + policy block | Exposed in manifest/index | archive check | Legacy campaigns unchanged | Declare `fill_timing` on new entries |
| Promotion gate | None | `promotion_readiness_errors` | Blocks optimistic/missing timing | included above | None approved | `signal_bar_close` not promotion-ready |
| HTF align | Module only | `d1agg_htf` + regime_switcher | Shared path for D1AGG gate | 2 equivalence tests | C012 not rerun | Use `htf_align` or justify |
| Weekly HTF | Separate helpers | Documented exception | Unmigrated | — | C016/C017 unchanged | Completed-week semantics |
| Observed financing | BLOCKED | Unchanged this sprint | Still blocked | — | — | Await practice sample |
| Approval registry | `[]` | Verified empty | `[]` | registry test | — | Human-only approval |
| Broker/loops | Frozen | No change | Frozen | — | — | No trading |

## No-approval statement

Infrastructure and policy only. No strategy approved. No CAMPAIGN_020. C019 remains REJECT.

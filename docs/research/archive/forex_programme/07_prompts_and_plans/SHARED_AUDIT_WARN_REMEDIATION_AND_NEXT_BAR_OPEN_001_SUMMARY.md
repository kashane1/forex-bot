# Shared Audit WARN Remediation and next_bar_open — Summary

**Branch:** `infra-shared-audit-warn-remediation-and-next-bar-open-001`  
**Base:** `infra-shared-signal-and-mtf-confluence-audit-001` @ `1349488`  
**Date:** 2026-05-27

## 1. Branch name

`infra-shared-audit-warn-remediation-and-next-bar-open-001`

## 2. Commit hashes by phase

| Phase | Commit |
|-------|--------|
| 0–11 | `4e43b0f` |

## 3. Files changed by phase

| Phase | Key paths |
|-------|-----------|
| 0 | `SHARED_AUDIT_WARN_REMEDIATION_AND_NEXT_BAR_OPEN_001_PLAN.md` |
| 1 | `NEXT_BAR_OPEN_REFERENCE_COMPARISON_DESIGN.md` |
| 2 | `scripts/compare_fill_timing_reference_campaign.py`, `research/fill_timing_comparison/`, tests |
| 3 | `research/fill_timing_reference_comparison/*.json`, `NEXT_BAR_OPEN_REFERENCE_COMPARISON_RESULT.md` |
| 4 | `src/forex_bot/features/htf_align.py`, `SHARED_HTF_ALIGN_MODULE_RESULT.md` |
| 5 | `indicators.py` RSI policy, `RSI_WARMUP_POLICY_REMEDIATION_RESULT.md` |
| 6 | `domain/signals.py`, `SIGNAL_PROVENANCE_FIELDS_REMEDIATION_RESULT.md` |
| 7–8 | Financing scope + parity docs |
| 9–10 | Validity memo, `EVIDENCE_*`, `FUTURE_RESEARCH_BACKLOG.md` |
| 11 | This summary |

## 4. Baseline validation

| Check | Result |
|-------|--------|
| `pytest tests/ -q` | 1744 passed (after manifest/summary committed) |
| `ruff check` | All checks passed |
| Research freeze / archive | PASS after summary artifact present |

## 5. Audit WARN items addressed

| WARN | Action | New status |
|------|--------|------------|
| Fill timing optimistic | C019 dual-mode comparison | **Remediated** — policy: require `next_bar_open` for approval-bound |
| No shared MTF adapter | `htf_align` module | **Remediated** — migration deferred |
| RSI fillna(50) | `warmup_policy` parameter | **Remediated** — default legacy |
| Signal provenance | Optional fields + validator | **Remediated** — export wiring deferred |
| Financing partial | Next-scope doc | **WARN** remains |
| Parity schema | Documented | **WARN** remains (Lean retired) |

## 6. WARN items remaining

- Financing overlay for multi-day/weekly holds
- Lean parity (retired)
- HTF adapter not yet adopted by production strategies
- Trade CSV provenance columns not added

## 7. Reference campaign

**CAMPAIGN_019** (`mean_reversion_thesis_invalidation 0.1.0-c019`)

## 8. signal_bar_close metrics (portfolio)

| Split | Trades | Expectancy R | PF | Pairs + |
|-------|--------|--------------|-----|---------|
| Train | 219 | −0.072 | 0.927 | 3/6 |
| Validation | 138 | +0.0962 | 1.142 | 6/6 |

## 9. next_bar_open metrics (portfolio)

| Split | Trades | Expectancy R | PF | Pairs + |
|-------|--------|--------------|-----|---------|
| Train | 217 | −0.0378 | 0.988 | 4/6 |
| Validation | 133 | +0.0175 | 1.056 | 4/6 |

## 10. Fill-timing delta summary

| Split | Δ trades | Δ expectancy R |
|-------|----------|----------------|
| Train | −2 | +0.034 |
| Validation | −5 | **−0.079** |

Validation uplift under `signal_bar_close` was **materially optimistic**.

## 11. Upper-bound evidence?

**Yes** for validation-split `signal_bar_close` campaigns (including C019 validation narrative). Train split mixed.

## 12. Future approval-bound: require next_bar_open?

**Yes** — unless precommit documents explicit justification.

## 13. htf_align summary

`align_last_completed()` with `HTF_UNAVAILABLE` / `HTF_STALE` and provenance columns. Tests in `test_htf_align.py`.

## 14. HTF migration status

**Not migrated** in production strategies (document-only recommendation).

## 15. RSI warmup policy

Default `neutral_fill` (legacy); new code should use `warmup_policy="nan"`.

## 16. Signal provenance fields

Six optional fields + `validate_signal_provenance()`.

## 17. Financing/cost scope

`OBSERVED_COST_FINANCING_OVERLAY_NEXT_SCOPE.md` — next sprint `infra-observed-cost-financing-overlay-local-first-001`.

## 18. Parity/export schema

Documented; no Lean run; provenance export deferred.

## 19. Campaign validity update

See `CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_WARN_REMEDIATION.md`. **C019 REJECT unchanged.**

## 20. Tests added

~20 tests across fill-timing metrics, htf_align, RSI policy, signal provenance, script contract.

## 21. Validation commands

`pytest`, `ruff`, `check_research_freeze.py`, `validate_research_archive.py`, `scan_artifacts_for_secrets.py`

## 22. CAMPAIGN_020 created?

**No.**

## 23. Strategy approved?

**No.**

## 24. Paper/demo/live blocked?

**Yes.**

## 25. Executor/broker behavior changed?

**No** (infrastructure + optional model fields only).

## 26. OANDA order APIs called?

**No.**

## 27. Credentials/secrets committed?

**No.**

## 28. SQLite/raw/bulky artifacts staged?

**No** (comparison uses local DB read-only; compact JSON/CSV only).

## 29. C019 requires rerun?

**Not for verdict.** Optional for validation narrative under `next_bar_open`.

## 30. Remaining blockers

- Financing for multi-day strategies
- HTF adapter adoption in strategies
- Export provenance wiring

## 31. Recommended next sprint

`infra-observed-cost-financing-overlay-local-first-001`

## 32. Review first

1. `NEXT_BAR_OPEN_REFERENCE_COMPARISON_RESULT.md`
2. `CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_WARN_REMEDIATION.md`
3. `research/fill_timing_reference_comparison/fill_timing_delta.json`
4. `src/forex_bot/features/htf_align.py`
5. `scripts/compare_fill_timing_reference_campaign.py`

## Explicit non-approval

This sprint does **not** approve any strategy.

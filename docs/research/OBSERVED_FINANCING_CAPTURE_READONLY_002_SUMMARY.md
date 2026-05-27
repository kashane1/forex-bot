# Observed Financing Capture Read-Only — Summary 002

**Branch:** `infra-observed-financing-capture-readonly-002`  
**Base:** `infra-observed-cost-financing-overlay-local-first-001` @ `5b83e2b`  
**Date:** 2026-05-27

## 1. Branch name

`infra-observed-financing-capture-readonly-002`

## 2. Commit hashes by phase

| Phase | Commit |
|-------|--------|
| 0 | `4e66f4c` |
| 1–2 | `19bc872` |
| 3 | `f374ec1` |
| 4 | `bf92701` |
| 5–7 | `0107a0e` |
| 8–9 | `5ef8cca` |

## 3. Files changed by phase

| Phase | Key paths |
|-------|-----------|
| 0 | `OBSERVED_FINANCING_CAPTURE_READONLY_002_PLAN.md` |
| 1–2 | `oanda_readonly.py`, `observed_financing_fixture.py`, `OANDA_READONLY_ENDPOINT_SAFETY_REVIEW.md`, `OBSERVED_FINANCING_FIXTURE_SCHEMA.md`, tests |
| 3 | `capture_oanda_observed_financing_readonly.py`, `OBSERVED_FINANCING_CAPTURE_SCRIPT_RESULT.md` |
| 4 | `OBSERVED_FINANCING_CAPTURE_BLOCKED.md`, `OBSERVED_FINANCING_CAPTURE_READONLY_RESULT.md` |
| 5–6 | `financing_reconciliation.py`, reconciliation + overlay reference docs, `research/observed_financing_capture_readonly/` |
| 7 | `CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_OBSERVED_FINANCING_CAPTURE.md` |
| 8 | `EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`, `FUTURE_RESEARCH_BACKLOG.md` |
| 9 | This summary |

## 4. Baseline validation

1764 pytest passed; research freeze PASS; archive PASS; secret scan PASS.

## 5. Read-only endpoint safety review

See `OANDA_READONLY_ENDPOINT_SAFETY_REVIEW.md` — GET allowlist on practice host; mutation paths denied.

## 6. Forbidden endpoints

Live host; POST/PUT orders; trade/position close; pendingOrders/openTrades streams; configure/funding.

## 7. Practice credentials present?

**No** in sprint runner environment.

## 8. Live environment refused?

**Yes** — enforced in code and tests.

## 9. Read-only capture ran?

**No** (execute blocked). Dry-run **yes**.

## 10. Capture date range

2026-05-01 → 2026-05-14 (planned); placeholder fixture 2026-05-13 → 2026-05-27.

## 11. Transaction count

0 (no execute).

## 12. Financing transaction count

0.

## 13. Unknown transaction type count

0.

## 14. Sanitized fixture path

`research/observed_financing_capture_readonly/observed_practice_financing.json`

## 15. Raw local uncommitted path

`research/financing/observed/raw/` (gitignored; only on successful execute)

## 16. Fixture schema validation

PASS — Pydantic `ObservedFinancingFixture` + unit tests.

## 17. Observed vs synthetic reconciliation

Inconclusive — no observed entries; synthetic drag ~0.04–0.08R on reference ledgers documented.

## 18. Sufficient for rate inference?

**No.**

## 19. Observed overlay on reference ledgers?

**No** — `OBSERVED_FIXTURE_EMPTY_OR_SPARSE`.

## 20–21. Campaign/pair observed deltas

N/A (overlay not run).

## 22. C019 interpretation

Unchanged REJECT; financing capture empty does not upgrade evidence.

## 23. Weekly/multi-day evidence

Still requires observed financing before promotion review; gross R remains optimistic.

## 24. Future promotion review requires observed financing?

**Yes** where hold duration material (multi-day/weekly).

## 25. CAMPAIGN_020 created?

**No.**

## 26. Strategy approved?

**No.**

## 27. Paper/demo/live blocked?

**Yes.**

## 28. Executor/broker behavior changed?

**No** (no calls to `OandaBroker` mutation methods).

## 29. OANDA mutation APIs called?

**No.**

## 30. Live environment used?

**No.**

## 31. Credentials/secrets printed or committed?

**No.**

## 32. Raw transactions/account IDs committed?

**No.**

## 33. Tests added

`tests/unit/test_oanda_readonly_capture_002.py` (11 tests).

## 34. Validation commands

`pytest`, `ruff`, `check_research_freeze`, `validate_research_archive`, `scan_artifacts_for_secrets`.

## 35. Remaining WARN/BLOCKED

- `BLOCKED_READONLY_CREDENTIALS` for execute in automation
- Practice account `OBSERVED_FINANCING_EMPTY` historically
- Observed→rate-table bridge not built
- Fill-timing `next_bar_open` policy still applies

## 36. Recommended next sprint

Human practice overnight sample + local `--execute-readonly-capture` with secret scan; then observed-vs-synthetic rate bridge if entries > 0.

## 37. Review first

1. `OBSERVED_FINANCING_CAPTURE_BLOCKED.md`
2. `scripts/capture_oanda_observed_financing_readonly.py`
3. `OANDA_READONLY_ENDPOINT_SAFETY_REVIEW.md`
4. `OBSERVED_VS_SYNTHETIC_FINANCING_RECONCILIATION.md`
5. `research/observed_financing_capture_readonly/insufficiency_report.json`

## Compact table

| Capture Status | Date Range | Transactions | Financing Txns | Fixture Valid | Observed Overlay Ran | Synthetic vs Observed | Campaign Impact | Follow-up |
|----------------|------------|--------------|----------------|---------------|----------------------|----------------------|-----------------|-----------|
| BLOCKED_READONLY_CREDENTIALS (execute) | 2026-05-01–14 | 0 | 0 | Yes (empty) | No | Inconclusive | No verdict change | Local creds + overnight sample |

## No-approval statement

No strategy approved. Diagnostic infrastructure only.

# Observed Financing Capture Read-Only — Summary

**Date:** 2026-05-27  
**Branch:** `infra-observed-financing-capture-readonly-001`  
**Sprint ID:** `OBSERVED_FINANCING_CAPTURE_READONLY_001`

> **Infrastructure sprint complete** — `strategy_evidence: false`. Capture: **OBSERVED_FINANCING_EMPTY**.

---

## 1. Branch name

`infra-observed-financing-capture-readonly-001`

---

## 2. Commit hashes by phase

| phase | commit |
|---|---|
| 0–2 | `74e2cf0` |
| 3–6 | `d505290` |
| 7–8 | *(this commit)* |

---

## 3. Files changed by phase

| phase | key files |
|---|---|
| 0–2 | plan, `observed.py`, capture script, fixtures, tests |
| 3–6 | preflight, result, reconciliation, readiness docs, `research/financing/observed/*.json` |
| 7–8 | EVIDENCE_INDEX, MANIFEST, BACKLOG, this summary |

---

## 4. Credential presence (yes/no)

| credential | present |
|---|---|
| `OANDA_ACCOUNT_ID_PRACTICE` | **yes** |
| `OANDA_ACCESS_TOKEN_PRACTICE` | **yes** |
| Environment practice | **yes** |

---

## 5. Endpoint allowlist used

`GET /v3/accounts/{id}`, `/summary`, `/transactions`, `/transactions/sinceid`, `/transactions/idrange`, `/transactions/{numeric_id}` on `api-fxpractice.oanda.com` only.

---

## 6. Endpoint denylist result

**PASS** — orders, trades, positions, stream, configure, funding, live host all refused.

---

## 7. API call made?

**Yes** — read-only transaction range fetch after dry-run.

---

## 8. All API calls read-only GET?

**Yes**

---

## 9. Order/trade/position mutation called?

**No**

---

## 10. Capture date range

2025-11-28 → 2026-05-27 UTC (180 days)

---

## 11. DAILY_FINANCING count

**0**

---

## 12. Instruments observed

*(none)*

---

## 13. Total observed financing by instrument

*(none — empty capture)*

---

## 14. Sanitization status

Parser + capture script redact account/user/request IDs; hash account at file level; redact trade/tx IDs. No raw account ID in committed artifacts. Raw dir gitignored.

---

## 15. Observed schema reconciliation status

Bridge required: observed point charges → `TableRateSource` for overlay. Documented in reconciliation JSON. **Not implemented** (no data to reconcile).

---

## 16. MODELED readiness decision

**Not ready.** Empty observed capture; engine PnL remains UNMODELED; synthetic diagnostic still authoritative.

---

## 17. Campaign verdict changed?

**No**

---

## 18. New strategy campaign?

**No**

---

## 19. Strategy approved?

**No** — `approved: []`

---

## 20. Paper/demo/live blocked?

**Yes**

---

## 21. Executor/broker changed?

**No**

---

## 22. Archive/freeze validation

Run after this commit.

---

## 23. Remaining blockers

- Zero DAILY_FINANCING on practice account (no overnight holds under freeze)
- Observed-to-modeled bridge not built
- Engine PnL still UNMODELED
- MODELED treatment refused

---

## 24. Recommended next sprint

**`infra-practice-overnight-financing-sample-collection-001`** — capture infrastructure works; need non-empty DAILY_FINANCING samples via controlled overnight holds or broker transaction import.

---

## 25. Files to review first

1. [`OBSERVED_FINANCING_CAPTURE_RESULT.md`](OBSERVED_FINANCING_CAPTURE_RESULT.md)
2. [`OBSERVED_FINANCING_READINESS_DECISION.md`](OBSERVED_FINANCING_READINESS_DECISION.md)
3. [`research/financing/observed/observed_financing_capture_status.json`](../../research/financing/observed/observed_financing_capture_status.json)
4. [`scripts/capture_observed_financing_readonly.py`](../../scripts/capture_observed_financing_readonly.py)
5. [`research/financing/observed.py`](../../research/financing/observed.py)
6. [`OBSERVED_FINANCING_SCHEMA_RECONCILIATION.md`](OBSERVED_FINANCING_SCHEMA_RECONCILIATION.md)

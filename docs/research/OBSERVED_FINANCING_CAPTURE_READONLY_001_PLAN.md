# Observed Financing Capture Read-Only — Execution Plan

**Date:** 2026-05-27  
**Branch:** `infra-observed-financing-capture-readonly-001`  
**Sprint ID:** `OBSERVED_FINANCING_CAPTURE_READONLY_001`  
**Type:** Infrastructure / read-only capture — `strategy_evidence: false`

---

## 1. Purpose

Capture and normalize observed OANDA **practice-account** `DAILY_FINANCING` transactions via read-only GET endpoints, producing sanitized fixtures for future OBSERVED_FINANCING_DIAGNOSTIC / MODELED readiness.

---

## 2. Non-goals

- Approve any strategy; create CAMPAIGN_019; run strategy campaigns
- Retune C008/C009/C018; enable paper/demo/live
- Place/modify/cancel/close orders or call mutation endpoints
- Use live OANDA credentials
- Commit credentials, `.env`, raw secrets, bulky dumps, SQLite DBs
- Change executor/broker behavior

---

## 3. Read-only endpoint allowlist

| endpoint | method |
|---|---|
| `GET /v3/accounts/{accountID}` | GET |
| `GET /v3/accounts/{accountID}/summary` | GET |
| `GET /v3/accounts/{accountID}/transactions` | GET |
| `GET /v3/accounts/{accountID}/transactions/sinceid` | GET |
| `GET /v3/accounts/{accountID}/transactions/idrange` | GET |
| `GET /v3/accounts/{accountID}/transactions/{id}` | GET |

Host: **`https://api-fxpractice.oanda.com` only**

---

## 4. Endpoint denylist

- `/orders`, `/trades/`, `/positions/`, `/openTrades`, `/openPositions`, `/pendingOrders`
- `/transactions/stream`
- `/configure`, `/funding`
- **`api-fxtrade.oanda.com`** (live host)
- Any POST/PUT/PATCH/DELETE

---

## 5. Credential handling

- Read only: `OANDA_ACCESS_TOKEN_PRACTICE`, `OANDA_ACCOUNT_ID_PRACTICE`
- Never read: `OANDA_*_LIVE`
- Never print token or account ID
- Account ID stored as SHA-256 hash in committed artifacts only
- If missing: `BLOCKED_CREDENTIALS_MISSING`, no API call

---

## 6. Sanitization rules

| field | committed form |
|---|---|
| accountID | SHA-256 hash at file level |
| userID | `REDACTED_USER` |
| requestID | `REDACTED_REQUEST` |
| tradeID | `trade_<sha256[:12]>` |
| transaction id | `tx_<sha256[:12]>` |
| raw responses | gitignored under `research/financing/observed/raw/` |

---

## 7. Target capture window

Default: **last 180 days** of practice transactions, filtered to `type=DAILY_FINANCING` (API param + local filter fallback).

---

## 8. Expected artifacts

```
research/financing/observed/observed_financing_capture_status.json
research/financing/observed/observed_daily_financing_sanitized.json  (if captured)
research/financing/observed/observed_financing_manifest.json
research/financing/observed/observed_financing_schema_reconciliation.json
docs/research/OBSERVED_FINANCING_CAPTURE_READONLY_RUNBOOK.md
docs/research/OBSERVED_FINANCING_CAPTURE_PREFLIGHT.md
docs/research/OBSERVED_FINANCING_CAPTURE_RESULT.md
docs/research/OBSERVED_FINANCING_SCHEMA_RECONCILIATION.md
docs/research/OBSERVED_FINANCING_READINESS_DECISION.md
scripts/capture_observed_financing_readonly.py
research/financing/observed.py
```

---

## 9. Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```

---

## 10. Blocked conditions

- Live environment or live host URL
- Missing practice credentials
- Denylisted endpoint requested
- Non-GET method
- Attempt to commit raw account ID or token
- Claim MODELED without readiness decision support

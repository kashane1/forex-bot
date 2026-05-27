# Observed Financing Capture (Read-Only) — Sprint Plan 002

**Branch:** `infra-observed-financing-capture-readonly-002`  
**Base:** `infra-observed-cost-financing-overlay-local-first-001` @ `5b83e2b`  
**Date:** 2026-05-27

## Purpose

Build a **strictly read-only** OANDA practice financing capture pipeline: inspect transaction history, sanitize to local fixtures, reconcile against synthetic overlay assumptions, and quantify differences — **without** strategy reruns, orders, or approvals.

## Non-goals

- No CAMPAIGN_020 / strategy campaigns / tuning
- No paper/demo/live enablement
- No order/trade/position mutation
- No live OANDA environment
- No raw transaction dumps or account IDs committed
- No verdict rewrites to PASS

## Read-only safety rules

1. Practice host only (`api-fxpractice.oanda.com`)
2. GET allowlist for account summary + transaction list/range only
3. Explicit denylist for orders, trades, positions, streams, funding configure
4. Default **dry-run** (no network); `--execute-readonly-capture` required for API
5. Bounded `--start-date` / `--end-date` required for execute
6. Never log Authorization, tokens, or raw account IDs
7. Raw responses only under gitignored `research/financing/observed/raw/`

## Forbidden endpoints (mutation / live)

| Class | Examples |
|-------|----------|
| Live host | `api-fxtrade.oanda.com` |
| Order mutation | `POST .../orders`, `PUT .../orders/...` |
| Trade mutation | `PUT .../trades/{id}/close` |
| Position mutation | `PUT .../positions/.../close` |
| Streams | `.../transactions/stream`, `.../pricing/stream` (not used in capture) |
| Deny fragments | `/orders`, `/trades/`, `/openTrades`, `/pendingOrders`, `/configure`, `/funding` |

## Allowed read-only candidates

- `GET /v3/accounts/{id}` (practice tag check)
- `GET /v3/accounts/{id}/summary`
- `GET /v3/accounts/{id}/transactions` (date-bounded)
- `GET /v3/accounts/{id}/transactions/sinceid`
- `GET /v3/accounts/{id}/transactions/idrange`
- `GET /v3/accounts/{id}/transactions/{numericId}`

## Credential handling

- Read `OANDA_ACCESS_TOKEN_PRACTICE` / `OANDA_ACCOUNT_ID_PRACTICE` from environment only when executing capture
- Refuse `OANDA_ENVIRONMENT=live`
- If missing on execute → `BLOCKED_READONLY_CREDENTIALS` (no workarounds)

## Sanitization rules

- `account_id_hash` = SHA-256 hex only in committed fixtures
- Transaction IDs → `tx_<hash>` / `transaction_id_hash`
- Reject token-like strings and raw account ID patterns in committed JSON
- `source: oanda_practice_observed`, `redaction_status: sanitized`

## Expected fixture schema

See `docs/research/OBSERVED_FINANCING_FIXTURE_SCHEMA.md` — `ObservedFinancingFixture` in `src/forex_bot/research/observed_financing_fixture.py`.

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/capture_oanda_observed_financing_readonly.py --start-date 2026-05-01 --end-date 2026-05-14
```

## Prior overlay sprint verified

- `OBSERVED_COST_FINANCING_OVERLAY_LOCAL_FIRST_001_SUMMARY.md`
- `FINANCING_OVERLAY_LOCAL_FIRST_RESULT.md`
- `research/financing_overlay_local_first/adjusted_metric_delta.json`

## Baseline (Phase 0)

| Check | Result |
|-------|--------|
| `approved_strategies.yaml` | `approved: []` |
| pytest | 1764 passed (post Phase 1–3 code) |
| research freeze / archive | PASS |

## No-approval statement

This sprint does not approve any strategy or enable trading.

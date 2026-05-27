# Observed Financing Capture — Read-Only Result

**Sprint:** `infra-observed-financing-capture-readonly-002`

## Capture executed?

| Mode | Result |
|------|--------|
| Dry-run | Yes — `DRY_RUN_OK` |
| Execute (practice API) | **No** — `BLOCKED_READONLY_CREDENTIALS` in sprint runner environment |

## Date range (dry-run / placeholder fixture)

`2026-05-01` → `2026-05-14` (dry-run); placeholder fixture window `2026-05-13` → `2026-05-27`

## Endpoint family

`GET /v3/accounts/{id}/transactions` (allowlisted, practice host only) — **not invoked** without credentials.

## Counts

| Metric | Value |
|--------|-------|
| Transactions captured | 0 (no execute) |
| Financing transactions | 0 |
| Unknown transaction types | 0 |

## Sanitized fixture path

`research/observed_financing_capture_readonly/observed_practice_financing.json` (empty entries, schema-valid placeholder)

## Raw local path

`research/financing/observed/raw/` (gitignored; written only on successful execute)

## Secret scan

PASS (pattern scan; no credentials in committed artifacts)

## No-order / no-mutation statement

No OANDA POST/PUT order, trade close, or position close endpoints were called.

## No-approval statement

Empty placeholder fixture is not strategy evidence.

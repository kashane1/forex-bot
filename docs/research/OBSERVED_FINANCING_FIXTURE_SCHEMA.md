# Observed Financing Fixture Schema (Practice Capture)

**Version:** 1  
**Implementation:** `src/forex_bot/research/observed_financing_fixture.py`  
**Committed path:** `research/observed_financing_capture_readonly/observed_practice_financing.json`

## Top-level fields

| Field | Required | Notes |
|-------|----------|-------|
| `fixture_version` | Yes | `1` |
| `source` | Yes | Must be `oanda_practice_observed` |
| `captured_at_utc` | Yes | ISO-8601 UTC |
| `account_id_hash` | Yes | 64-char SHA-256 hex; **never** raw account id |
| `environment` | Yes | `practice` |
| `account_currency` | Yes | e.g. `USD` |
| `capture_window` | Yes | `{from, to}` ISO bounds |
| `redaction_status` | Yes | `sanitized` |
| `entries` | Yes | Array (may be empty) |
| `transaction_counts` | Yes | `total`, `financing`, `unknown` |

## Entry fields

| Field | Notes |
|-------|-------|
| `local_id` | Monotonic local id `obs_00000` |
| `transaction_id_hash` | Redacted tx id |
| `instrument` | `EUR_USD` or null |
| `side` | Optional |
| `units` | Optional string decimal |
| `financing_home` | Signed home currency cashflow |
| `transaction_time` | ISO-8601 |
| `effective_date` | Calendar date |
| `transaction_type` | Known financing class |
| `raw_type` | OANDA `type` field |
| `redaction_status` | `sanitized` |

## Known financing transaction types

- `DAILY_FINANCING` (primary)
- `FINANCING`, `DIVIDEND_ADJUSTMENT` (included when present)
- Other types → counted as `unknown`, not silently treated as financing

## Validation rules

- Reject raw account id patterns and token-like strings
- Reject invalid `account_id_hash`
- Empty `entries` allowed with explicit `transaction_counts` (no-data capture)

## Distinction from synthetic rate fixtures

Files under `research/financing/fixtures/` remain **`synthetic: true`** diagnostic rate tables. Observed practice fixtures live under `research/observed_financing_capture_readonly/` and use `source: oanda_practice_observed`.

## No-approval statement

Observed fixtures are not strategy evidence.

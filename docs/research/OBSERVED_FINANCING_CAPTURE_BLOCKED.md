# Observed Financing Capture — Blocked

**Sprint:** `infra-observed-financing-capture-readonly-002`  
**Date:** 2026-05-27

## Classification

**`BLOCKED_READONLY_CREDENTIALS`** — in the sprint execution environment, `OANDA_ACCESS_TOKEN_PRACTICE` and `OANDA_ACCOUNT_ID_PRACTICE` were not available.

## What ran instead

- Dry-run capture: **PASS** (`DRY_RUN_OK`, no network)
- Execute capture: **not attempted** (credentials missing)
- Empty sanitized placeholder fixture committed at `research/observed_financing_capture_readonly/observed_practice_financing.json` for schema/pipeline validation only

## Prior repo state

Committed `research/financing/observed/observed_financing_capture_status.json` from sprint 001 shows credentials were present historically with **`OBSERVED_FINANCING_EMPTY`** (zero `DAILY_FINANCING` in 180-day window) — not a credential failure.

## Human action to unblock

1. Configure practice credentials locally (never commit)
2. Ensure `OANDA_ENVIRONMENT=practice` (or unset)
3. Hold at least one overnight position across rollover, or widen date range
4. Run:

```bash
python scripts/capture_oanda_observed_financing_readonly.py \
  --execute-readonly-capture \
  --start-date YYYY-MM-DD \
  --end-date YYYY-MM-DD
python scripts/scan_artifacts_for_secrets.py
```

5. Commit only if sanitized fixture validates and secret scan passes

## No-approval statement

Blocked capture does not change strategy verdicts.

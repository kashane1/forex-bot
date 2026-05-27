# Observed Financing Capture — Read-Only Runbook

**Date:** 2026-05-27  
**Script:** `scripts/capture_observed_financing_readonly.py`  
**Type:** Infrastructure only — `strategy_evidence: false`

---

## Prerequisites

- `OANDA_ACCESS_TOKEN_PRACTICE` set locally (never commit)
- `OANDA_ACCOUNT_ID_PRACTICE` set locally (never commit)
- `OANDA_ENVIRONMENT=practice` (or unset)
- Network access to `api-fxpractice.oanda.com`

---

## Commands

### Dry-run (no transaction fetch)

```bash
python scripts/capture_observed_financing_readonly.py --dry-run --no-require-practice-tag
```

Use `--no-require-practice-tag` if the practice account lacks an explicit `PRACTICE` tag but uses the practice REST host (defense-in-depth: host is still hard-coded to fxpractice).

### Capture last 180 days

```bash
python scripts/capture_observed_financing_readonly.py --no-require-practice-tag
```

### Custom window

```bash
python scripts/capture_observed_financing_readonly.py \
  --from-iso 2025-01-01T00:00:00Z \
  --to-iso 2026-05-27T00:00:00Z \
  --no-require-practice-tag
```

---

## Outputs

| file | committed? |
|---|---|
| `research/financing/observed/observed_financing_capture_status.json` | yes |
| `research/financing/observed/observed_financing_manifest.json` | yes |
| `research/financing/observed/observed_daily_financing_sanitized.json` | yes, if captured |
| `research/financing/observed/raw/*` | **no** (gitignored) |

---

## Status values

| status | meaning |
|---|---|
| `DRY_RUN_OK` | Credentials + practice host OK; no fetch |
| `OBSERVED_FINANCING_CAPTURED` | DAILY_FINANCING transactions found |
| `OBSERVED_FINANCING_EMPTY` | No DAILY_FINANCING in window |
| `BLOCKED_CREDENTIALS_MISSING` | Env vars absent |
| `BLOCKED_NOT_PRACTICE_ENVIRONMENT` | `OANDA_ENVIRONMENT=live` |
| `BLOCKED_NOT_PRACTICE_ACCOUNT` | Account tag check failed |
| `ERROR` | HTTP or parse failure |

---

## Safety

- GET only; practice host only
- Order/trade/position endpoints denylisted
- Credentials never printed
- Account ID hashed in sanitized output; trade/tx IDs redacted

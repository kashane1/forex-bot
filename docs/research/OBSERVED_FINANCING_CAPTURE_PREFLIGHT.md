# Observed Financing Capture — Preflight

**Date:** 2026-05-27  
**Branch:** `infra-observed-financing-capture-readonly-001`

---

## Credential presence (yes/no only)

| check | result |
|---|---|
| `OANDA_ACCOUNT_ID_PRACTICE` present | **yes** |
| `OANDA_ACCESS_TOKEN_PRACTICE` present | **yes** |
| Environment is practice (not live) | **yes** |
| Live token present in env | **yes** (not read by script) |

---

## Practice environment

| check | result |
|---|---|
| REST host | `https://api-fxpractice.oanda.com` |
| Live host refused | **yes** |
| Account PRACTICE tag | **no** — capture uses `--no-require-practice-tag`; host lock sufficient |

---

## Endpoint allowlist

Allowed path suffixes: `""`, `/summary`, `/transactions`, `/transactions/sinceid`, `/transactions/idrange`, `/transactions/{numeric_id}`

## Denylist

`/orders`, `/trades/`, `/positions/`, `/openTrades`, `/openPositions`, `/pendingOrders`, `/transactions/stream`, `/configure`, `/funding`, live host

**Result:** PASS — script enforces before every GET

---

## Planned capture

| parameter | value |
|---|---|
| Date range | Last **180 days** (auto: 2025-11-28 → 2026-05-27 UTC) |
| Type filter | `DAILY_FINANCING` (API param + local fallback) |
| Methods | GET only |

---

## Dry-run command

```bash
python scripts/capture_observed_financing_readonly.py --dry-run --no-require-practice-tag
```

**Dry-run result:** PASS (exit 0)

---

## Raw output gitignore

`research/financing/observed/raw/` — **gitignored** ✓

---

## Preflight verdict

**SAFE TO PROCEED** with read-only capture using practice credentials and `--no-require-practice-tag`.

# Observed Financing Capture — Result

**Date:** 2026-05-27  
**Branch:** `infra-observed-financing-capture-readonly-001`  
**Status:** `OBSERVED_FINANCING_EMPTY`

> **No strategy approved.** No orders placed. Read-only GET only.

---

## Command run

```bash
python scripts/capture_observed_financing_readonly.py --no-require-practice-tag
```

(No secrets in command.)

---

## Capture parameters

| parameter | value |
|---|---|
| Date range | 2025-11-28T02:52:53Z → 2026-05-27T02:52:53Z (180 days) |
| Endpoint | `GET /v3/accounts/{accountID}/transactions?from=&to=&type=DAILY_FINANCING` |
| Host | `api-fxpractice.oanda.com` |
| Method | GET only |

---

## Results

| metric | value |
|---|---|
| Transactions fetched | 0 |
| DAILY_FINANCING count | 0 |
| Instruments observed | *(none)* |
| Total financing by instrument | *(none)* |

---

## Status interpretation

**OBSERVED_FINANCING_EMPTY** — honest empty result, not manufactured.

Likely reasons:
1. Research freeze — no orders submitted; no overnight positions held
2. Practice account has no `DAILY_FINANCING` history in the 180-day window
3. Bot has never held multi-day positions on this account

---

## Limitations

- Account lacks explicit `PRACTICE` tag (capture used host lock + `--no-require-practice-tag`)
- Single-page range fetch; pagination not needed for zero results
- No per-trade financing records available without overnight holds

---

## Artifacts

- [`research/financing/observed/observed_financing_capture_status.json`](../../research/financing/observed/observed_financing_capture_status.json)
- [`research/financing/observed/observed_financing_manifest.json`](../../research/financing/observed/observed_financing_manifest.json)
- `observed_daily_financing_sanitized.json` — **not written** (empty capture)

---

## Explicit statements

- **No strategy approved**
- **No orders placed, modified, or closed**
- **No CAMPAIGN_019**
- C008/C009/C018 verdicts unchanged

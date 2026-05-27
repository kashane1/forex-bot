# Practice Overnight Financing Sample — Human Collection Runbook

**Date:** 2026-05-27  
**Sprint:** `PRACTICE_OVERNIGHT_FINANCING_SAMPLE_PLAN_001`  
**Type:** Human-executed procedure — `strategy_evidence: false`

> **WARNING — READ BEFORE PROCEEDING**
>
> - **Practice account only.** Never use a live OANDA account for this procedure.
> - **Human-only manual trade placement.** You must place and close trades yourself in the OANDA practice UI (or another explicitly human-approved channel).
> - **Cursor and the forex-bot must NOT place orders.** Do not enable paper-loop, demo-loop, or any config that sets `allow_order_submission`. Do not ask Cursor to submit trades.
> - **The bot remains frozen.** `configs/approved_strategies.yaml` stays `approved: []`.

---

## 1. Purpose

Collect a **small, non-empty set** of observed `DAILY_FINANCING` transactions on the OANDA **practice** account so a future read-only capture sprint can populate sanitized fixtures and unblock observed-to-modeled financing work.

---

## 2. Sample objective

Generate enough overnight exposure that OANDA posts at least one `DAILY_FINANCING` transaction, then capture it read-only with:

```bash
python scripts/capture_observed_financing_readonly.py --no-require-practice-tag
```

---

## 3. Minimum sample design

| requirement | target |
|---|---|
| Directions | At least **one long** and **one short** if feasible |
| Instruments | At least **two different pairs** if feasible (e.g. EUR_USD, USD_JPY) |
| Hold duration | Positions open across **at least one rollover** (17:00/21:00 UTC daily financing cutoff) |
| Count | **2–4** small positions total — not a trading campaign |
| Close | **Manually close** all sample positions after at least one rollover has occurred |

Suggested pairs (low spread, liquid): `EUR_USD`, `GBP_USD`, `USD_JPY`.

---

## 4. Step-by-step (human only)

### Before opening positions

1. Confirm you are logged into **OANDA practice** (fxTrade Practice), not live.
2. Confirm `OANDA_ENVIRONMENT=practice` locally if you will run capture afterward.
3. Confirm the bot has **not** been enabled for order submission.
4. Note today's date and planned rollover window (hold positions past the next daily financing time in UTC).

### Opening positions (manual UI)

5. Open **position 1**: small size long on instrument A (e.g. EUR_USD, 1,000 units or minimum allowed).
6. Open **position 2**: small size short on instrument B (e.g. USD_JPY) if feasible.
7. Optionally add one more long/short on a third instrument for side/instrument diversity.
8. Set a **server-side stop-loss** on each position (manual UI) to cap downside — tiny size, but still prudent.
9. **Do not** use the forex-bot CLI, paper-loop, demo-loop, or any script to open these.

### Holding through rollover

10. Keep positions open **at least until after the next daily financing event** (typically one calendar day; Wednesday may include triple swap — that is useful data).
11. Do not modify the repo or enable automation during the hold.

### After rollover

12. Verify in OANDA practice **Transaction History** that at least one **`DAILY_FINANCING`** entry appears.
13. Follow [`POST_SAMPLE_OBSERVED_FINANCING_CAPTURE_CHECKLIST.md`](POST_SAMPLE_OBSERVED_FINANCING_CAPTURE_CHECKLIST.md) to run read-only capture.
14. **Manually close** all sample positions in the practice UI.
15. Do not commit account statements, screenshots with account IDs, or credentials.

---

## 5. Safety constraints

| constraint | detail |
|---|---|
| Position size | Minimum practical units (e.g. 1k–5k) — not meaningful PnL risk on practice |
| Account | Practice only |
| Stop-loss | Set in OANDA UI when opening each leg |
| Live account | **Forbidden** |
| Bot order submission | **Forbidden** |
| Strategy approval | **Not required and not granted** — this is infrastructure sampling, not strategy research |

---

## 6. What to capture after sample exists

1. Run read-only capture (see post-sample checklist).
2. Verify `observed_financing_capture_status.json` shows `OBSERVED_FINANCING_CAPTURED` and `daily_financing_count > 0`.
3. Verify `observed_daily_financing_sanitized.json` exists and contains no raw account IDs or tokens.
4. Do **not** commit raw API dumps from `research/financing/observed/raw/` (gitignored).

---

## 7. What NOT to do

- Do not edit `configs/approved_strategies.yaml`
- Do not enable `paper-loop` or `demo-loop`
- Do not set `allow_order_submission: true` in any config
- Do not commit `.env`, tokens, account IDs, or PDF/CSV account statements
- Do not treat sample PnL as strategy evidence
- Do not create CAMPAIGN_019 or run backtests on sample trades as a campaign

---

## 8. Success criteria (human sample)

- At least **1** `DAILY_FINANCING` transaction visible in OANDA practice history
- At least **1** instrument represented in financing breakdown
- Positions were opened and closed **manually**
- Read-only capture (future sprint) can reproduce sanitized JSON from repo script

---

## 9. If no DAILY_FINANCING appears

- Confirm positions were actually open across the rollover cutoff (UTC)
- Confirm practice account (not demo-with-zero-financing edge case)
- Hold one more night if needed — still manual, still tiny size
- Do not manufacture or synthetic-fill observed data in the repo

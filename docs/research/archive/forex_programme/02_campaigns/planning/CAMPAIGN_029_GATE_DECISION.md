# CAMPAIGN_029 — gate decision

**Strategy:** `usdjpy_range_bar_mtf_breakout 0.1.0-c029`
**Classification:** **`REJECT_TRAIN_GATE`**
**Approved:** **No** · **Test lockbox opened:** **No** · **Paper/demo/live:** **blocked**
**Machine artifact:** [`research/campaign_029/execution/gate_decision.json`](../../research/campaign_029/execution/gate_decision.json)

---

## 1. Decision path (frozen, precommit §10)

1. **Execution engine** — implemented & tested; **parity `PASS`** (independent
   verifier reproduced all 2,387 train trades exactly). → not `BLOCKED_EXECUTION_ENGINE`,
   not `BLOCKED_PARITY`.
2. **Train gate** — train expectancy **−0.018785 < 0** ⇒ **catastrophic fail**.
3. Per frozen policy, validation is **confirmation, not rescue** ⇒ **validation
   NOT run**.
4. ⇒ **`REJECT_TRAIN_GATE`.**

The maximum reachable status was `PROMOTION_REVIEW_REQUIRED` (never approval); the
actual result is a reject at the first binding gate.

## 2. Why not the other classifications

| candidate | applies? | why |
|-----------|:--------:|-----|
| `BLOCKED_EXECUTION_ENGINE` | no | engine implemented + unit-tested |
| `BLOCKED_PARITY` | no | parity `PASS` (2,387 == 2,387, exit 100%, ΔR 0.0) |
| `INSUFFICIENT_SAMPLE` | no | 2,387 train trades ≫ floor |
| `REJECT_VALIDATION_GATE` | no | validation not reached (train gate failed first) |
| `PROMOTION_REVIEW_REQUIRED` | no | requires train + validation + parity all pass |
| **`REJECT_TRAIN_GATE`** | **yes** | net train expectancy < 0 after conservative cost |

## 3. Validation — NOT run (and why)

Running validation after a net-negative, catastrophic train result would be
fishing for a window that happens to look better; the precommit forbids that
("validation is confirmation, not rescue"). The 2024 validation window therefore
**remains unused**, and the 2025-01-01 → 2026-05-20 **test lockbox stays sealed**.

## 4. Hard-rule confirmations

- `configs/approved_strategies.yaml` remains `approved: []` (unchanged).
- No paper/demo/live; no OANDA/network; no live credentials.
- No parameter tuning; frozen rule unchanged after seeing results.
- No bulky/raw artifacts committed (full ledger is local & gitignored).

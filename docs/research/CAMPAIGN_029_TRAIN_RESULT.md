# CAMPAIGN_029 — TRAIN result (2021-05-27 → 2023-12-31)

**Strategy:** `usdjpy_range_bar_mtf_breakout 0.1.0-c029`
**Verdict:** `REJECT_TRAIN_GATE` · `NOT_APPROVED` · test lockbox **closed**
**Artifacts:** [`research/campaign_029/execution/train_summary.json`](../../research/campaign_029/execution/train_summary.json),
[`gate_decision.json`](../../research/campaign_029/execution/gate_decision.json)
**Parity:** `PASS` (see `CAMPAIGN_029_PARITY_RESULT.md`)

> Train evidence for the FROZEN rule, resolved on the M1 tape with conservative,
> M1-resolved cost (real half-spread at the entry+exit fill rows + 0.2 pip
> slippage each side) and the frozen H4/D1AGG staleness policy. No tuning. The
> 2025–2026 test window was **not** loaded.

---

## 1. Headline

| metric | value |
|--------|------:|
| trades | **2,387** |
| **net expectancy (per-R)** | **−0.018785** |
| gross expectancy (per-R) | **+0.083855** |
| net R total | −44.84 |
| gross R total | +200.16 |
| profit factor (net pips) | **0.974** |
| hit rate | 39.4% |
| max drawdown (R) | −91.72 |
| avg hold | 7.87 range bars · ~21,760 s (~6.0 h) |
| avg risk | 24.05 pips |
| avg total cost | **2.29 pips ≈ 0.095R / trade** |
| 2× cost-stress expectancy | −0.121426 |
| long / short | 1,362 / 1,025 |
| exits | stop 1,234 · time 1,152 · end_of_data 1 |

## 2. The finding: a small gross edge, fully cost-defeated

The trigger has a **positive gross edge** (+0.084R/trade; gross PF > 1; +200R
gross over 2,387 trades). But the **conservative M1-resolved cost is ~0.095R per
trade** (avg 2.29 pips against avg 24.0-pip risk), which **more than consumes the
gross edge** → **net −0.0188R/trade**, PF 0.974. Under 2× cost the net is −0.121R.

This is the same failure mode the timeframe-ladder (C026) documented for the M5
family: **not a signal with no information, but an edge too small to survive
realistic transaction cost.** The 10-pip range bar's ~24-pip average stop distance
means each trade pays ~0.4 pip-of-cost-per-pip-of… i.e. cost is ~9.5% of risk,
and the gross edge per unit risk is below that.

## 3. Frozen train gate

| gate (precommit §10) | threshold | observed | pass |
|---|---|---:|:--:|
| train sample | ≥ 30 trades | 2,387 | ✅ |
| **train expectancy** | **≥ 0** | **−0.018785** | ❌ |

The binding train gate (expectancy ≥ 0) **fails**, and it fails the *catastrophic*
condition (net-negative expectancy). Per the frozen policy **validation is a
confirmation step, not a rescue** — it was **not run**.

## 4. Lookahead / integrity

- Entries strictly next-range-bar-open; stops M1-walked; parity `PASS` (an
  independent re-implementation reproduced all 2,387 trades exactly).
- HTF context from the last completed bar at the decision; H4 stale>8h / missing →
  no trade (frozen). D1AGG stale>3d / missing → gate skipped.
- No parameter was changed; this is the first and only evidence run of the frozen
  rule on train.

## 5. Verdict

**`REJECT_TRAIN_GATE`.** The `usdjpy_range_bar_mtf_breakout` candidate does **not**
clear the binding train expectancy gate after conservative cost. Nothing approved;
paper/demo/live blocked; the test lockbox stays sealed. See
`CAMPAIGN_029_GATE_DECISION.md` and `CAMPAIGN_029_FINAL_INTERPRETATION.md`.

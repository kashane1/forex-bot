# CAMPAIGN_029 — final interpretation

**Strategy:** `usdjpy_range_bar_mtf_breakout 0.1.0-c029`
**Verdict:** `REJECT_TRAIN_GATE` · `NOT_APPROVED`
**Date:** 2026-05-29

---

## 1. Did the range-bar thesis survive train? **No.**

The thesis — that trend-aligned continuation after a pullback-and-reclaim,
measured on **10-pip USD_JPY range bars**, is a tradable trigger — **failed the
binding train gate**. Over 2,387 train trades (2021-05-27 → 2023-12-31) the rule's
**net expectancy was −0.0188R** with a profit factor of **0.974**.

## 2. Real edge or only noise? **A small *gross* edge, fully cost-defeated.**

This is the important nuance and not the same as "pure noise":

- **Gross** expectancy was **+0.0839R/trade** (gross profit factor > 1, +200R over
  the window). The trigger does carry *some* directional information.
- The **conservative, M1-resolved cost** averaged **2.29 pips ≈ 0.095R/trade**
  (real bid/ask half-spread at the entry+exit fill rows + 0.2 pip slippage each
  side, against an average 24.0-pip stop distance).
- Cost (**0.095R**) **exceeds** the gross edge (**0.084R**) → **net −0.0188R**.
  Under 2× cost stress the net is **−0.121R**.

So the candidate is **cost-defeated**, the same failure mode the timeframe-ladder
(C026) documented for the M5 family: the signal is not information-free, but the
edge is **below the transaction-cost floor**.

## 3. Did validation run? **No.** Did parity pass? **Yes.** Lockbox? **Closed.**

- **Validation: NOT run** — train failed catastrophically (net-negative), and the
  frozen policy treats validation as confirmation, not rescue.
- **Parity: PASS** — an independent verifier reproduced all 2,387 train trades
  exactly (exit reasons 100% aligned, ΔnetR = 0.0). The reject is a property of the
  *strategy*, not a bookkeeping artifact.
- **Test lockbox (2025-01-01 → 2026-05-20): never opened.**

## 4. Are USD_JPY 10-pip range bars worth more work?

**Not under this thesis/parameterisation.** At a 10-pip threshold with ~24-pip
structural stops, cost is ~9.5% of risk and swamps the observed gross edge. Three
*hypothetical* revival directions exist, but **each would be a NEW pre-registered
campaign, not a re-tune of C029** (changing thresholds now would be forking-path
fitting):

1. **Wider range bars** (e.g. 20–30 pip) to raise edge-per-trade above the cost
   floor — but C026 already showed the *time-bar* cost gradient improves with
   slower bars yet stayed net-negative; a range-bar version may well repeat that.
2. **A cheaper execution** (tighter sessions / spread-gated entries) — speculative.
3. **A different trigger** on range bars — a genuinely new thesis.

Per lab discipline, the `usdjpy_range_bar_mtf_breakout` candidate at 10 pip is
**CLOSED**. Any revival needs a fresh external thesis and a new precommit, not a
parameter sweep over the same data.

## 5. Standing confirmations

- **No strategy is approved.** `configs/approved_strategies.yaml` stays `approved: []`.
- **Paper / demo / live remain blocked**; no OANDA/network; no live credentials.
- **No parameter tuning; the frozen rule was unchanged after seeing results.**
- **Test lockbox stayed closed.** C011 stays the null benchmark; C025/C026/C027
  stay REJECT; C028 (relative-value spread) stays LIKELY_SELECTION_NOISE.

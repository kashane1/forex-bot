# Next-Step Prompt — after C1 factor validation

**Status:** RECOMMENDATION (not started; no campaign, no strategy, freeze intact)
**Date:** 2026-05-29
**Predecessor:** `research-c1-factor-validation-001` →
verdict `FACTOR_FRONT_GATE_CANDIDATE` (`docs/research/C1_FACTOR_VERDICT.md`)

This prompt is provided because the Phase-6 verdict warrants it. It describes
**exactly one** future pre-registered **front-gate screen** — *not* a campaign,
*not* a strategy, *not* a scaffold. Running it is a separate, optional decision.

---

## Why this is the only sanctioned next step

The C1 factor-validation sprint established that `C1_trend_cont_long` (fade full
H4+H1+M15 bullish alignment → 30–60-min downward reversion) is a **genuine,
robust, non-USD-artifact** factor that is **cost-defeated as a flat signal** but
has **one economically-motivated cost-aware path**: the reversion grows
monotonically with volatility (pre-cost, all-pairs), and in high-volatility
windows on EUR_USD/USD_JPY the spread-adjusted reversion is positive and survives
outlier checks. That path is a **hypothesis**, found post-hoc and optimistically
costed; only a pre-registered, out-of-sample, realistically-costed screen can
adjudicate it. The lab's history (C026/C029/C031/H16/H03 all died at realistic
cost) sets a high prior that it will fail — which is exactly why it must be
tested rather than assumed either way.

---

## Suggested prompt (copy-paste)

```
We are starting a research-only front-gate SCREEN from clean, updated origin/main.

Branch: research-c1-highvol-frontgate-screen-001

Context:
- The C1 factor-validation sprint (research-c1-factor-validation-001) returned
  FACTOR_FRONT_GATE_CANDIDATE for C1_trend_cont_long (fade full H4+H1+M15 bullish
  alignment -> 30-60min downward reversion).
- C1 is genuine, robust, persistent, and NOT a USD-regime artifact. It is
  cost-defeated as a flat signal but shows a positive spread-adjusted reversion in
  HIGH-VOLATILITY windows on EUR_USD/USD_JPY (Phase 2 pre-cost monotone vol
  gradient + Phase 5 cost cells).
- This is the candidate's ONE earned front-gate screen. It is NOT a campaign and
  NOT a strategy.

Hard rules:
- Do NOT create a campaign. Do NOT build a strategy. Do NOT create entry/exit
  logic beyond what the screen's response measurement strictly requires.
- Do NOT run train/validation/test. Do NOT approve anything. Do NOT enable
  paper/demo/live. Do NOT call OANDA APIs or use credentials.
- This is a frozen pre-commit + ONE screen pass, mirroring H16/H03.

PHASE 0 - frozen precommit
  Write the screen's make-or-break BEFORE any number: the exact high-volatility
  definition (within-pair top-tertile H4 ATR, locked), pairs (EUR_USD + USD_JPY,
  GBP_USD as a weaker third), the realistic round-trip cost model (event-bar
  spread + slippage + high-vol spread widening), the out-of-sample split (held-out
  period not used in the validation sprint), and the matched-null-post-cost bar.
  Commit.

PHASE 1 - screen pass
  Reuse src/forex_bot/research/c1_factor_validation.py + m1_response_matrix.
  On the held-out period only: measure the high-vol-conditioned C1_long fade's
  signed forward response NET of realistic cost, vs a session/direction-matched
  null charged the same cost. Report per pair. Commit.

PHASE 2 - decision (one of):
  PASS_FRONT_GATE   -> beats matched-null-post-cost OOS on BOTH EUR_USD & USD_JPY;
                       authorises a SEPARATE later scaffold sprint (not started here).
  FAIL_FRONT_GATE   -> does not; the M1/HTF time-bar confluence directional lane is
                       CLOSED on this corpus (joins the retired non-time-bar lane);
                       reopen only with new data / new external thesis, fresh screen.
  Commit.

PHASE 3 - validation
  pytest tests/ -q; ruff check; check_research_freeze; validate_research_archive;
  scan_artifacts_for_secrets; git status --short. Write a summary doc. Commit.

Success criteria: a clean PASS/FAIL on whether the high-volatility-conditioned C1
fade beats a realistic post-cost matched null out-of-sample. Do not build a
strategy; do not create a campaign; do not trade.
```

---

## Pre-committed stop criterion (carried from the verdict)

If the screen does **not** beat the matched-null-**post-cost** bar
**out-of-sample on both EUR_USD and USD_JPY**, the M1/HTF time-bar confluence
directional lane is **closed** on this corpus. Reopen only with new data
(10–15y, or genuine non-USD crosses to finally settle the residual USD share) or a
new external thesis — via a fresh screen, never a re-tune of C1.

## What this prompt is NOT

Not a campaign, not a scaffold, not an approval, not a trade. A `PASS` would only
authorise a *later, separate* scaffold sprint behind the existing front gate.

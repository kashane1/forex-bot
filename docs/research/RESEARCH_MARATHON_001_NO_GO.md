# Research Marathon 001 — NO-GO

**Outcome: NO-GO. No tested hypothesis earned PAPER-TRADE-ONLY status.**

This is one of the two acceptable marathon outcomes (the other being a
PAPER-TRADE-ONLY candidate). It is a *valid evidence result*, not a
failure of process. No strategy should move to paper, demo, or live
trading on the strength of this work.

## What was tested

| campaign | hypothesis / family | verdict | why |
|---|---|---|---|
| CAMPAIGN_005 | benchmarks & diagnostics | diagnostic | random entry −0.095 R; efficiency ratio 0.24; H4 majors are choppy |
| CAMPAIGN_006 | D1 daily trend | REJECT (no valid result) | D1 candles close at the rollover — backtester cannot validly test D1 |
| CAMPAIGN_007 | H4 pullback-continuation | REJECT | screening fail: train −0.164 R, validation −0.166 R |
| CAMPAIGN_008 | H4 range mean-reversion (research-only) | REJECT (narrow) | screening fail by one criterion: train −0.017 R; validation was **+0.172 R** |

Prior to the marathon, CAMPAIGN_002 (trend), 003 (trend+ADX) and 004
(volatility breakout) were already REJECT on real OANDA data.

## Why no strategy should move to paper / demo / live

1. **No strategy passed its pre-committed gates.** CAMPAIGN_007 failed
   screening outright. CAMPAIGN_008 failed screening by a single
   criterion (train expectancy −0.017 R vs a ≥ 0 gate). Per
   test-window discipline the 2025-2026 reported window was never
   opened for any marathon strategy — there is no out-of-sample test
   result that would justify promotion.
2. **Breakout / trend / pullback entries have no edge here.**
   CAMPAIGN_002-004 and 007 — four distinct trend/breakout/pullback
   entries — all produced negative expectancy on real 2020-2026 H4
   majors. CAMPAIGN_005 showed they are **not better than random
   entry** (−0.095 R) once real spreads are paid.
3. **Financing is still unmodeled.** Accurate historical financing
   cannot be obtained from the current stack; it is estimated via a
   conservative stress overlay only, and remains a hard live-promotion
   blocker independent of any backtest result.
4. **D1 could not be tested at all** — an infrastructure limitation
   (the backtester's intraday assumptions are invalid for D1 candles
   that close at rollover).

## The one near-miss — CAMPAIGN_008 mean-reversion

CAMPAIGN_008 is REJECT, but it is **categorically different** from the
other rejections and is the recommended human decision point:

- Validation (2023-2024, never used to design the strategy):
  **+0.172 R, profit factor 1.29, +1.04%, 6 of 6 pairs positive.**
- Cost stress: expectancy stays positive at base / 1.5× / 2.0×
  (+0.069 / +0.040 / +0.027).
- Train (2020-2022): **−0.017 R, PF 1.02** — flat within noise, not a
  loss. It is the *only* marathon strategy that beats the
  CAMPAIGN_005 random-entry benchmark on every split.
- It failed the screening gate solely because train came in at
  −0.017 R and the pre-committed gate is "train ≥ 0". That gate was
  **not** relaxed after the fact — doing so would be the exact
  post-hoc rationalization the precommit discipline exists to prevent.

This is consistent with the CAMPAIGN_005 diagnostic: the H4 majors were
choppy/range-bound across 2020-2026 (efficiency ratio 0.24), which
*broke* the trend strategies and is the *natural habitat* of a
regime-filtered mean-reversion strategy.

## Recommended next human decision point

The marathon stops here (4 campaigns run; ladder complete; no
broad-optimizer search permitted). A **human** should now decide
between:

1. **Authorize a focused CAMPAIGN_009** that (a) adds a proper
   midline-target exit to `mean_reversion` — the engine currently has
   only stop/time exits, and the flat train split is plausibly an
   artifact of exiting reversion trades on a 40-bar timer instead of
   at the mean — then (b) re-screens under a fresh pre-commit. This is
   a *strategy change* and needs a new pre-commit + explicit
   authorization; it is not a marathon action.
2. **Decline further research.** The honest base-rate reading is that
   a USD-500 retail account trading 6 majors has no demonstrated edge,
   and three entry families plus a near-miss is reasonable grounds to
   stop.

Either way, **mean reversion must not be paper-traded or promoted
without that human review** — it is `paper_only` and was capped at
REVISE by design.

## Required infrastructure follow-ups (independent of strategy choice)

- **Financing model** (hypothesis H-09): still the top blocker for any
  live consideration, ever.
- **D1 backtest support**: next-bar-open fills and a non-rollover
  spread reference, so a daily timeframe can be tested at all.
- A **midline-target exit** in the backtest engine, if mean-reversion
  research continues.

## Bottom line

Research Marathon 001 generated **valid negative evidence**. The
disciplined verdict is NO-GO: nothing is promoted, nothing is
paper-traded, no orders are submitted. The single direction worth a
human's attention is regime-filtered mean reversion (CAMPAIGN_008),
which showed a real but not-yet-confirmed signal and is explicitly
handed to human review rather than auto-advanced.

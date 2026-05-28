# CAMPAIGN_022 — Final Interpretation

**Date:** 2026-05-28 · **Strategy:** `h4_h1_pullback_resolution_entry 0.1.0-c022`
**Final verdict:** **REJECT**

## The question the sprint set out to answer

Does the H4/H1 **pullback-resolution** framework (H4 bias + H1 counter-trend pullback that holds +
M15 reclaim) produce **materially better** behavior than the prior **all-green alignment** campaigns
(C020/C021)?

**Answer: No.** It is materially *worse*.

## Point-by-point

| question | finding |
|---|---|
| Did pullback-resolution improve behavior? | **No.** Train −0.1042R, validation −0.1663R; both negative, PF < 1. |
| Did time-stop churn improve? | **No.** 60% of trades hit the −2×ATR stop before the 32-bar clock; stop bucket mean −0.86R. |
| Did trend-continuation quality improve? | **Partially present but insufficient.** Surviving trades (time-exit, 40%) average +0.96R, but only 40% survive; win rate 32.6% vs ~39% breakeven. |
| Did it reduce late-trend chasing? | **No.** The M15 reclaim after an H1 holding-pullback buys local noise and is whipsawed; the "resolution" trigger fails too often. |
| Did C022 beat C021? | **No numeric head-to-head** — C021 is scaffold-only with no executed evidence. Structurally, C022's earlier reclaim entries underperform; not fabricated. |
| Did C022 beat C020? | **No.** C020 train −0.035R / val +0.053R; C022 is worse on both (train −0.104R / val −0.166R). |
| Did C022 beat the C011 null? | **No.** Null −0.0029R; C022 validation −0.1663R — far below; `beat_null = false`. |
| Did 2× cost stress pass? | **No.** Validation 2× stress −0.2468R. |
| Did Backtrader parity pass? | **Not run** — moot; train-gate REJECT closes the lockbox (parity is a pre-lockbox gate only). |
| Was the test lockbox opened? | **No.** |

## Why it failed (mechanism)

The payoff geometry is favorable when a trade works (avg win +1.24R vs avg loss −0.79R), but the
**entry hit-rate is too low**: requiring an H1 counter-trend pullback and then an M15 EMA20 reclaim
times entries into frequent failed resolutions. 42% of trades lose a near-full stop. The slow,
genuine continuation that pays (+0.96R time-exits) occurs in only 40% of cases — not enough to
overcome the 60% stop rate. Pullback-resolution did not, in this frozen form, locate higher-quality
trend continuations than all-green alignment; it traded earlier and got whipsawed.

## Why no approval is granted

- Binding train gate failed (−0.1042R) → terminal REJECT under the no-rescue discipline.
- Every validation and robustness gate also failed (expectancy, PF, pair breadth, cost stress, null).
- Research-execution evidence never authorizes promotion regardless; max attainable status was
  RESEARCH_PASS, and even that is unreachable here.

## Standing invariants

`configs/approved_strategies.yaml` = `approved: []`. Paper/demo/live blocked. No broker/executor
change. No OANDA mutation/order APIs. No live trading. No cloud execution. No retuning occurred.
CAMPAIGN_020 remains REJECT; CAMPAIGN_021 remains scaffold-only.

## Forward note (not acted on here)

A C023 ADX-22 sibling is a separate, independently-frozen campaign; nothing in C022 was tuned toward
it. Given C022's decisive REJECT, a stricter H4 ADX alone is unlikely to flip the sign — the failure
is in entry hit-rate, not regime strength — but that is a question for C023's own precommit, not this
sprint.

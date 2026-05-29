# CAMPAIGN_026 — timeframe-ladder interpretation & decision

**Verdict: REJECT the lower-timeframe Donchian + HTF confluence family.** The
timeframe ladder answers C026's five questions cleanly. Lowering the execution
timeframe **does** fix the cost problem that defeated M5 — but the underlying signal
has **no edge** at any timeframe, so cheaper cost only makes the loss smaller, never
positive.

## The core result in one line

Net expectancy and cost both improve monotonically as the timeframe slows, in lockstep:

| TF | median spread/ATR | best candidate expectancy_R | best PF |
|---|---|---|---|
| M3 | 0.59 | −0.140 | 0.73 |
| M5 (C025) | 0.44 | −0.077 | 0.85 |
| M15 | 0.23 | −0.039 | 0.92 |
| M30 | 0.15 | **−0.0083** | 0.976 |

The line extrapolates *toward* zero but does not cross it. The best candidate anywhere
(C026_TF_010, M30 trend-runner) is still **−0.0083R**, below the C011 null (−0.0029R),
PF 0.976, only 2/7 pairs non-negative, and fails 2× cost stress (−0.112R).

## 1. Is M3 worse than M5? — Yes

M3 expectancy −0.14…−0.18R vs M5 −0.08…−0.18R; spread/ATR 0.59 vs 0.44; **0/7** pairs
non-negative on every M3 candidate. M3 is cost-hostile and the worst rung, exactly as
predicted. The faster bar amplifies the spread-to-range penalty.

## 2. Does M15 improve enough vs M5? — Cost yes, edge no

M15 halves the cost drag (spread/ATR 0.23 vs 0.44) and roughly halves the loss
(−0.04…−0.08R vs −0.08…−0.18R). But every M15 candidate is still net-negative, PF < 1,
1/7 pairs positive. The cost veto is lifted; no edge appears underneath it.

## 3. Does M30 improve enough vs M15/M5? — Best, still negative

M30 has the best cost profile (0.15) and the least-bad expectancy (−0.008…−0.031R),
PF up to 0.98, 2/7 pairs positive on the trend-runner. It is the closest the family
ever gets to breakeven — and it still does not clear it, the null, or the stress gate.

## 4. Do slower lower timeframes reduce cost drag? — Yes, decisively

This is the one unambiguous positive finding. Spread/ATR falls 0.59 → 0.44 → 0.23 →
0.15 from M3 to M30, and realised expectancy tracks it. **M5 was not uniquely
cost-defeated** — it sits on a smooth cost/timeframe curve; M15/M30 are genuinely much
cheaper to trade. The cost hypothesis behind this sprint was correct.

## 5. Does Donchian + HTF confluence have any promising timeframe? — No

No timeframe produces positive, cost-robust train expectancy. The signal's gross edge
is at best ~0 (PF approaching 1.0 only as cost shrinks), meaning the breakout +
HTF-trend + regime + pullback/compression construct has **no intrinsic directional
edge** on these majors — it was the *cost* masking how close to a coin-flip the raw
signal is. Remove the cost and you find a coin-flip, not an edge.

## Pair and exit-model standouts

- **Pair:** USD_JPY is the only consistently-positive leg (M30 +0.19R, M15 +0.124R) —
  the *same* lone-USD_JPY pattern C025 found on M5. It is the cheapest-spread major, so
  this is most parsimoniously explained by cost, not a JPY-specific breakout edge. It
  fails 2× stress and the aggregate is negative → **not** a SINGLE_PAIR_REVIEW_ONLY
  trigger, and it overlaps the already-exhausted USD_JPY microstructure thread.
- **Exit model:** breakeven-then-ATR-trail on M30 is the least-bad (amortises fixed
  cost over longer holds), but no exit model manufactures edge from a null signal.

## What this supports

- **Reject the whole lower-timeframe Donchian + HTF family.** ✔ M3/M5/M15/M30 all null
  after cost; the limiting behaviour is breakeven-from-below, not a hidden edge.
- **Continue with M15?** ✘ Net-negative, PF < 1, 1/7 pairs.
- **Continue with M30?** ✘ Least-bad but still negative, fails null + 2× stress.
- **Single-pair (USD_JPY) follow-up?** ✘ Best explained by cost; fails stress; duplicates
  the exhausted USD_JPY microstructure/price-structure thread (see MEMORY / backlog).
- **Build Backtrader parity?** ✘ Nothing passed train (see parity-readiness doc →
  `DEFER_PARITY_REJECTED`).
- **Open the test lockbox in a future sprint?** ✘ No train+validation-clean champion
  exists to justify spending the lockbox.

## Why no approval is granted

No candidate passed even the train screen (0/11). There is no champion, no validation,
no parity, no out-of-sample evidence — nothing that could support promotion.
`approved_strategies.yaml` stays `approved: []`; paper/demo/live stay blocked.

## Recommended next step

**Close the Donchian + HTF confluence family across all execution timeframes (M3–M30)
and stop tuning it.** The cost-ladder experiment was the right, decisive test and it
returned a clean null: the signal has no edge, only a cost gradient. Any future revival
needs a *different external thesis or signal* — not another parameter/timeframe sweep
of this construct. This dovetails with the standing `PAUSE_STRATEGY_RESEARCH` posture
for internal USD_JPY price-structure mining: prefer sourcing a genuinely new external
thesis over further in-sample search. The M3/M30 materialization + cost-diagnostic
infrastructure built here is reusable for any future timeframe-sensitive study.

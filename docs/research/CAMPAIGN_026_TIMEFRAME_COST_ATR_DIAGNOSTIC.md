# CAMPAIGN_026 — timeframe cost/ATR diagnostic (Phase 3)

**Decision: PROCEED to the train matrix.** M15 and M30 improve spread/ATR materially
vs M5; M3 is worse than M5 (as expected). Not all timeframes are cost-hostile, so this
is **not** `BLOCKED_COST_STRUCTURE`. This diagnostic runs **before** strategy evidence.

Command:
```
PYTHONPATH=$PWD/src python scripts/run_campaign_026_donchian_htf_timeframe_ladder.py --cost-diagnostic
```
Window 2021-07-01 → 2024-12-31 (train+validation span; **test lockbox excluded**), 7
majors, ATR(14) on each execution frame, spread = (ask_close − bid_close)/pip.

## Aggregate spread/ATR by timeframe

| TF | bars | median | mean | p75 | p90 |
|---|---|---|---|---|---|
| **M3** | 2,911,946 | **0.5924** | 0.7295 | 0.8681 | 1.2394 |
| **M5** (C025 ref) | 1,719,855 | **0.4387** | 0.5217 | 0.6273 | 0.8662 |
| **M15** | 545,834 | **0.2315** | 0.2547 | 0.3078 | 0.3914 |
| **M30** | 261,427 | **0.1548** | 0.1658 | 0.1966 | 0.2416 |

The ladder is monotone in the hypothesized direction: bar range scales with timeframe,
spread does not, so spread/ATR falls as the timeframe slows. **M5 ≈ 0.44 reproduces the
C025 finding** (reported ~0.45–0.50) — the cost diagnostic is consistent with the prior
campaign.

## Is M3 worse than M5?

**Yes.** M3 median spread/ATR 0.59 vs M5 0.44 (+35% relative). M3 is **cost-hostile**
(median ≥ 0.30): the bid/ask spread is ~0.6× the per-bar ATR. M3 is retained in the
matrix as a **diagnostic anchor** (with a higher 150-trade floor), but the cost profile
predicts it cannot clear realistic-cost filters.

## Does M15 improve meaningfully vs M5?

**Yes, materially.** M15 median 0.23 ≈ **53% of M5's 0.44** — the spread is now ~¼ of
per-bar ATR rather than ~½. Below the 0.30 cost-hostile line. This is the first
timeframe where the Donchian breakout idea has a plausible cost budget.

## Does M30 improve meaningfully vs M15/M5?

**Yes.** M30 median 0.155 ≈ **35% of M5** and ~67% of M15 — the best cost profile of
the ladder. p90 just 0.24 (M30) vs 0.87 (M5).

## Pair-level observations (median spread/ATR)

USD_JPY is consistently the **cheapest** (M3 0.43, M5 0.32, M15 0.17, M30 0.12);
NZD_USD / USD_CAD / USD_CHF are the **most expensive** at every timeframe. Ranking is
stable across timeframes — a structural spread property, not a timeframe artifact. No
single pair is cost-hostile at M15/M30.

## Session-level observations (median spread/ATR)

| TF | asia | london | newyork |
|---|---|---|---|
| M3 | 0.843 | 0.497 | 0.465 |
| M5 | 0.618 | 0.383 | 0.339 |
| M15 | 0.293 | 0.228 | 0.183 |
| M30 | 0.175 | 0.161 | 0.132 |

**Asia is the worst session** at every timeframe (thin liquidity → wider spread
relative to range), London/NY materially cheaper. Even Asia-session M30 (0.175) is
below the cost-hostile line; Asia-session M3 (0.843) is severely cost-hostile.

## Is any timeframe cost-hostile before strategy evidence?

- **M3: cost-hostile** (median 0.59 ≥ 0.30). Diagnostic-only expectation.
- **M5: cost-hostile** (0.44) — already rejected by C025.
- **M15: not cost-hostile** (0.23).
- **M30: not cost-hostile** (0.155).

## Decision

Per the Phase 3 decision rule:
- M3 spread/ATR worse than M5 → **documented**; M3 stays diagnostic-only in the matrix.
- M15/M30 spread/ATR materially better than M5 → **proceed with the train matrix**.
- Not all timeframes cost-hostile → **not** `BLOCKED_COST_STRUCTURE`.

A better cost profile is **necessary, not sufficient** — it removes the M5 cost veto
but says nothing about edge. The train matrix (Phase 7) tests whether the Donchian +
HTF signal actually has positive, cost-robust expectancy at M15/M30.

## Artifacts (`research/campaign_026/timeframe_cost_diagnostics/`)

`timeframe_spread_atr_summary.csv`, `timeframe_spread_atr_by_pair.csv`,
`timeframe_spread_atr_by_session.csv`, `timeframe_cost_drag_estimates.json`,
`timeframe_viability_flags.json`, `cost_diagnostic_run_manifest.json`.

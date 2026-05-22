# Research Marathon 001 — Plan

Branch: `research-marathon-001`. A **bounded** autonomous research
marathon. The goal is **valid evidence, not a forced positive result.**

A successful outcome is EITHER:
1. one candidate strategy that earns PAPER-TRADE-ONLY review status
   under strict pre-committed gates, OR
2. a documented NO-GO showing no tested hypothesis survived.

Both outcomes are equally acceptable. The marathon will not iterate to
make a chart look good.

## Hard constraints

- No paper trading, no demo-loop, no order submission, no live creds.
- Real OANDA practice data only; no synthetic fallback; stop if real
  data is unavailable.
- Prior campaign artifacts (CAMPAIGN_001–004) are immutable.
- No broad optimizers, no unbounded search.
- The 2025-01-01 → 2026-05-20 test window is a **reported lockbox** —
  only run it for a hypothesis that has already cleared train +
  validation + stress gates.
- Every hypothesis is pre-committed (`CAMPAIGN_XXX_PRECOMMIT.md`)
  before it runs.
- Max 5 new campaigns. Commit after each.

## Campaign ladder (may stop early)

| phase | campaign | purpose | promotion |
|---|---|---|---|
| 1 | CAMPAIGN_005_BENCHMARKS | diagnostics + baselines (no-trade, random entry, always-long/short, trendiness, autocorrelation, spread/ATR) | diagnostic only — never PAPER-TRADE-ONLY |
| 2 | CAMPAIGN_006_DAILY_TREND | D1 trend following — does lower turnover beat spread drag? | can reach PAPER-TRADE-ONLY |
| 3 | CAMPAIGN_007_H4_PULLBACK_CONTINUATION | H4 pullback-continuation entry — avoid breakout exhaustion | can reach PAPER-TRADE-ONLY |
| 4 | CAMPAIGN_008_RANGE_MEAN_REVERSION | regime-filtered mean reversion | research-only — cannot exceed REVISE without human review |
| 5 | stop / review | NO-GO doc or candidate review doc | — |

**The ladder stops early** the moment a hard stop condition is hit.

## Hard stop conditions

Stop the marathon immediately if:
1. A candidate reaches PAPER-TRADE-ONLY (do not keep optimizing it).
2. Three consecutive distinct strategy families fail validation.
3. A required infrastructure / data-quality blocker appears.
4. Real OANDA data is unavailable.
5. The 10-hour budget is reached.
6. The work would need a broad optimizer / unbounded search.
7. Evidence emerges that the backtester / reporting path is unreliable.

## Test-window discipline

For CAMPAIGN_006–008:
1. Screen on **train + validation + cost stress** first.
2. Run the reported **test** window only if train AND validation are
   both non-negative after costs, validation PF ≥ 1.05, stress_15x
   survives, ≥ 2 pairs positive/near-breakeven, trade count meaningful,
   financing stress not obviously fatal.
3. If a hypothesis fails the train/validation gate, the test window is
   **not** run.

## Standard splits & costs

- train 2020-01-01 → 2022-12-31, validation 2023-01-01 → 2024-12-31,
  reported test 2025-01-01 → 2026-05-20, full 2020-01-01 → 2026-05-20.
- cost regimes: base, stress_15x, stress_2x.
- Financing: estimated via the conservative stress model
  (`forex_bot.financing`); unmodeled in-engine; a hard live blocker.

## Best attainable outcome

PAPER-TRADE-ONLY. **No strategy will be called live-ready** on this
historical data alone.

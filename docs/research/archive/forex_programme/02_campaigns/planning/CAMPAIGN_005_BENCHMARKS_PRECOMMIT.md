# CAMPAIGN_005 — Benchmarks & Diagnostics — Pre-Commit

Written before the campaign runs. **Diagnostic only — CAMPAIGN_005
cannot produce a PAPER-TRADE-ONLY recommendation and promotes nothing.**

## Purpose

Before testing new strategies (CAMPAIGN_006-008), establish *what
"better than nothing" means* on this data. Prior campaigns rejected
three strategy families with expectancy roughly −0.07R to −0.16R. This
campaign asks: is that worse than simple baselines, or is *any* entry
roughly that bad once real costs are paid?

## Data

Real OANDA practice H4 candles, reused from `data/campaign_002.sqlite3`
(6-pair universe: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD,
USD_CHF). Provenance hashes already verified in CAMPAIGN_002/003/004.
No re-fetch, no synthetic data.

## Benchmarks (all expectancy in R, R = 2.0 × ATR-14 at entry)

1. **No-trade** — return 0.00%. The do-nothing reference.
2. **Always-long / always-short** — descriptive buy-and-hold over the
   full window: the pair's own net drift. Tells us whether a static
   directional bias would have captured anything.
3. **Random-entry** — the key control. One position at a time (mirrors
   the risk policy): walk each H4 series, enter with a fixed
   per-bar probability, random 50/50 direction, hold a fixed 30 bars,
   exit on time. Bid/ask fills with the base cost model (0.5× spread
   multiplier + 0.2 pip slippage). 20 random seeds. Report mean
   expectancy R and its spread. Entry probability is set so the random
   trade count per pair is within roughly ±50% of the prior-campaign
   H4 trade counts (matched frequency).

## Diagnostics (per pair, H4, full window)

- **Spread-to-ATR**: median spread ÷ median ATR-14 — the cost hurdle.
- **Trendiness — efficiency ratio**: |net move| ÷ Σ|bar move| over
  rolling 20-bar windows, averaged. Near 1 = trending; near 0 = choppy.
- **Return autocorrelation (lag 1)**: negative ⇒ mean-reverting,
  positive ⇒ trending.
- **Volatility clustering**: lag-1 autocorrelation of |returns| —
  expected positive (GARCH effect); reported for completeness.
- **Directional drift**: net full-window return per pair.

## Pass/fail

CAMPAIGN_005 has **no pass/fail gate** — it is diagnostic. Its output
feeds the marathon's go/no-go reasoning:

- If random-entry expectancy is roughly as negative as the rejected
  strategies, that is evidence the failures are **cost/structure
  driven**, and a hard signal that further breakout/trend variants are
  unlikely to clear costs.
- Trendiness / autocorrelation diagnostics indicate whether trend or
  mean-reversion is the better-supported direction for CAMPAIGN_006-008.

## Overfitting risk

None — no strategy is fitted or promoted. The only judgement calls are
the random-entry hold length (30 bars) and frequency (matched to prior
campaigns); both are fixed here before running and are not tuned.

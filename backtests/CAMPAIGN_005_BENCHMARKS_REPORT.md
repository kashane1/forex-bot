# CAMPAIGN 005 — Benchmarks & Diagnostics

> **Diagnostic only.** CAMPAIGN_005 promotes nothing and has no pass/fail gate. It establishes what simple baselines achieve on the real OANDA H4 data so later campaigns can be judged against them. Part of Research Marathon 001.

## Provenance

- Git commit: `8753a3aa4ceee7bab3eba2285865889368804844`
- Working tree dirty: YES
- Data: real OANDA practice H4, reused from `data/campaign_002.sqlite3`
- Pre-commit: `docs/research/CAMPAIGN_005_BENCHMARKS_PRECOMMIT.md`
- Generated: 2026-05-22T06:41:30.860545+00:00

| pair | source | candles | raw_sha256 (16) |
|---|---|---:|---|
| EUR_USD | oanda-practice | 9934 | `f56b30030f3abbd6` |
| GBP_USD | oanda-practice | 9934 | `6ea9b168cf234d1d` |
| USD_JPY | oanda-practice | 9935 | `568f4c6104e1f73a` |
| AUD_USD | oanda-practice | 9934 | `710f6aed5875367a` |
| USD_CAD | oanda-practice | 9934 | `9fe3b74d78c5cc5a` |
| USD_CHF | oanda-practice | 9934 | `46a0f6748c7dfc9c` |

## Benchmark 1 — no-trade

Return **0.00%**, expectancy **0.000 R**. The do-nothing reference.

## Benchmark 2 — always-long / always-short (descriptive)

Full-window buy-and-hold of the mid price — the pair's own drift.

| pair | always-long return % | always-short return % |
|---|---:|---:|
| EUR_USD | +3.39% | -3.39% |
| GBP_USD | +1.01% | -1.01% |
| USD_JPY | +46.31% | -46.31% |
| AUD_USD | +1.10% | -1.10% |
| USD_CAD | +6.04% | -6.04% |
| USD_CHF | -18.45% | +18.45% |

## Benchmark 3 — random entry (matched frequency, 20 seeds)

One position at a time, random 50/50 direction, fixed 30-bar hold, bid/ask fills + base costs. Expectancy in R (R = 2×ATR at entry).

| pair | random expectancy R | seed std | trades/seed |
|---|---:|---:|---:|
| EUR_USD | -0.183 | 0.202 | 85 |
| GBP_USD | -0.107 | 0.193 | 85 |
| USD_JPY | -0.122 | 0.209 | 85 |
| AUD_USD | -0.147 | 0.140 | 85 |
| USD_CAD | -0.008 | 0.147 | 85 |
| USD_CHF | -0.004 | 0.167 | 85 |
| **mean** | **-0.095** | | |

## Diagnostics — market character (H4, full window)

| pair | median spread (pips) | median ATR (pips) | spread/ATR % | efficiency ratio | return AC(1) | abs-return AC(1) | net drift % |
|---|---:|---:|---:|---:|---:|---:|---:|
| EUR_USD | 1.50 | 27.9 | 5.4% | 0.241 | -0.015 | +0.161 | +3.39% |
| GBP_USD | 1.90 | 36.4 | 5.2% | 0.237 | +0.006 | +0.223 | +1.01% |
| USD_JPY | 1.60 | 41.4 | 3.9% | 0.254 | +0.024 | +0.195 | +46.31% |
| AUD_USD | 1.40 | 25.5 | 5.5% | 0.229 | -0.014 | +0.176 | +1.10% |
| USD_CAD | 1.90 | 30.0 | 6.3% | 0.237 | -0.008 | +0.210 | +6.04% |
| USD_CHF | 1.70 | 23.6 | 7.2% | 0.245 | +0.010 | +0.166 | -18.45% |

## Interpretation

- **Random-entry expectancy averages -0.095 R.** Prior rejected strategies: CAMPAIGN_002 −0.085 R, CAMPAIGN_003 −0.071 R, CAMPAIGN_004 −0.163 R (untouched test). The strategies are **not meaningfully better than random entry** — once real bid/ask spread and slippage are paid, an arbitrary entry on these pairs loses at a similar rate. The prior failures are **cost/structure driven**, not unique defects of those entries.
- **Efficiency ratio averages 0.240** (0 = pure chop, 1 = pure trend). A low efficiency ratio means H4 price paths on these majors retrace most of their movement — hostile to breakout/trend entries that need follow-through.
- **Lag-1 return autocorrelation averages +0.000.** Near zero / slightly positive — no strong directional persistence to exploit at H4.
- Always-long/short returns show no consistent capturable drift across the universe.

**Marathon implication:** the bar for CAMPAIGN_006-008 is not merely 'positive' — it is 'positive enough to beat the random-entry cost drag of -0.095 R by a clear margin on out-of-sample data.' Low efficiency ratios argue against further breakout/trend variants; lower turnover (D1) and non-breakout entries are the remaining reasonable hypotheses.

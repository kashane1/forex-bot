# CAMPAIGN 004 — Volatility Breakout

> **Result: REJECT.** Real OANDA practice H4 data. A genuinely
> different entry family — `volatility_breakout 0.1.0-c004`: a breakout
> *out of an ATR-compressed regime*, no EMA trend filter. One controlled
> hypothesis, no optimizer, RiskEngine wired in. This campaign does
> **not** authorize paper-loop, demo-loop, or any order submission.

## Provenance

- **Git commit:** `3a7d2054db7659245286c3f1d5c3546cada629b7`
- **Working tree dirty at report time:** YES
- **Config:** [`configs/campaign_004_volatility_breakout.yaml`](../configs/campaign_004_volatility_breakout.yaml)
- **Config hash:** `11c22978adc8116ce39f13900ff1ef0fb109785c1f206970d91a16bb8412fea4`
- **Strategy version:** `volatility_breakout 0.1.0-c004`
- **Pre-commit spec:** [`docs/research/CAMPAIGN_004_PRECOMMIT.md`](../docs/research/CAMPAIGN_004_PRECOMMIT.md) (written before the run)
- **Data source:** real OANDA practice, **reused** from `data/campaign_002.sqlite3`
- **RiskEngine invoked:** YES — all 42 runs, `mode="backtest"`
- **Total runs:** 42 (24 baseline + 18 cost stress, H4 only)
- **Runner elapsed:** 329s

### Data provenance (reused CAMPAIGN_002 hashes)

CAMPAIGN_004 **reuses** the real OANDA practice H4 candles fetched for CAMPAIGN_002 (`data/campaign_002.sqlite3`). No re-fetch, no synthetic data. Hashes below were recorded at CAMPAIGN_002 fetch time and match the CAMPAIGN_002 report.

| instrument | gran | source | candles | first | last | raw_sha256 (16) | norm_sha256 (16) |
|---|---|---|---:|---|---|---|---|
| EUR_USD | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | `f56b30030f3abbd6` | `f5d1d1b193020976` |
| GBP_USD | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | `6ea9b168cf234d1d` | `2c751fec8b0e9f6d` |
| USD_JPY | H4 | oanda-practice | 9935 | 2020-01-01 | 2026-05-19 | `568f4c6104e1f73a` | `64836ea0f08e21c7` |
| AUD_USD | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | `710f6aed5875367a` | `7a19f3e957ea8ee5` |
| USD_CAD | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | `9fe3b74d78c5cc5a` | `dc04b583759ec5c6` |
| USD_CHF | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | `46a0f6748c7dfc9c` | `11b0a134792a62a3` |

## Strategy rule definition

`volatility_breakout 0.1.0-c004` — full spec and parameter rationale in
the pre-commit doc. Summary:

| element | rule |
|---|---|
| compression | ATR-14 at bar t-1 ≤ 40th percentile of ATR-14 over the trailing 60 bars |
| breakout | close[t] beyond the 20-bar prior-bar Donchian channel |
| direction | breakout direction — **no EMA 50/200 filter** |
| stop | 2.0 × ATR-14 initial |
| exit | 2.0 × ATR-14 trailing stop + 120-bar time stop |
| risk | 0.25% / trade, 1 position per instrument |
| universe | 6 pairs (NZD_USD excluded), H4 only |

This is **not** a Donchian trend rescue: the EMA regime filter that
defined CAMPAIGN_002/003 is gone; entries are pure compression→expansion.

## Assumptions

- Fills: bid/ask-aware; slippage applied against the trade.
- PnL → USD: quote-currency PnL converted at the exit price for
  USD-base pairs; USD-quote pairs already in USD.
- **Financing: NOT modeled in-engine** (accurate historical financing
  is unavailable — see `docs/financing_decision.md`). The conservative
  stress overlay from `forex_bot.financing` is applied below. Financing
  remains a hard blocker for any live promotion.

## RiskEngine — approvals and rejections

Total rejection rows (one per signal × code) across all 42 runs: **10392**, exported per-run to `*_risk_rejections.csv`.

**By code:**

| code | count |
|---|---:|
| `DRAWDOWN_LIMIT` | 5466 |
| `SPREAD_TO_ATR` | 2210 |
| `SPREAD_TOO_WIDE` | 1558 |
| `SESSION_BLOCKED` | 1158 |

**By pair:**

| pair | rejections |
|---|---:|
| EUR_USD | 2461 |
| GBP_USD | 1718 |
| USD_JPY | 544 |
| AUD_USD | 1771 |
| USD_CAD | 1537 |
| USD_CHF | 2361 |

**By split:**

| split | rejections |
|---|---:|
| train | 356 |
| validation | 216 |
| test_untouched | 266 |
| full | 9554 |

**By UTC hour (non-zero):**

| hour | rejections |
|---:|---:|
| 01:00 | 660 |
| 02:00 | 274 |
| 05:00 | 1355 |
| 06:00 | 587 |
| 09:00 | 1236 |
| 10:00 | 739 |
| 13:00 | 1282 |
| 14:00 | 555 |
| 17:00 | 1201 |
| 18:00 | 494 |
| 21:00 | 1263 |
| 22:00 | 746 |

## Metrics by split (H4, base costs)

| split | trades | rejected | return % | max-DD % | PF | expectancy R | win % |
|---|---:|---:|---:|---:|---:|---:|---:|
| train | 575 | 285 | -5.30% | -6.22% | 0.54 | -0.229 | 28.2% |
| validation | 411 | 186 | -3.69% | -4.54% | 0.56 | -0.198 | 31.7% |
| test_untouched | 233 | 214 | -1.40% | -1.90% | 0.63 | -0.163 | 33.9% |
| full | 812 | 1647 | -6.97% | -7.52% | 0.50 | -0.241 | 28.3% |

## Metrics by pair — untouched test (2025-01-01 → 2026-05-20)

| pair | trades | rejected | return % | max-DD % | PF | expectancy R | win % |
|---|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | 42 | 18 | -1.10% | -1.52% | 0.74 | -0.104 | 35.7% |
| EUR_USD | 23 | 66 | -1.86% | -1.86% | 0.33 | -0.322 | 26.1% |
| GBP_USD | 43 | 10 | -1.61% | -2.38% | 0.62 | -0.148 | 37.2% |
| USD_CAD | 36 | 54 | -1.27% | -1.72% | 0.62 | -0.100 | 38.9% |
| USD_CHF | 37 | 43 | -2.30% | -2.50% | 0.55 | -0.307 | 27.0% |
| USD_JPY | 52 | 23 | -0.28% | -1.44% | 0.94 | -0.000 | 38.5% |

## Metrics by pair — full window (2020-01-01 → 2026-05-20)

| pair | trades | rejected | return % | max-DD % | PF | expectancy R | win % |
|---|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | 111 | 340 | -7.85% | -8.04% | 0.44 | -0.292 | 25.2% |
| EUR_USD | 97 | 324 | -7.09% | -8.12% | 0.40 | -0.300 | 20.6% |
| GBP_USD | 103 | 331 | -8.13% | -8.13% | 0.34 | -0.326 | 31.1% |
| USD_CAD | 180 | 191 | -7.95% | -8.08% | 0.60 | -0.134 | 31.7% |
| USD_CHF | 92 | 368 | -8.09% | -8.09% | 0.34 | -0.394 | 22.8% |
| USD_JPY | 229 | 93 | -2.71% | -4.68% | 0.89 | -0.000 | 38.4% |

## Cost stress (full window)

| regime | trades | rejected | avg return % | avg max-DD % | avg PF | avg expectancy R |
|---|---:|---:|---:|---:|---:|---:|
| base | 812 | 1647 | -6.97% | -7.52% | 0.50 | -0.241 |
| stress_15x | 762 | 1749 | -7.19% | -7.60% | 0.47 | -0.253 |
| stress_2x | 756 | 1758 | -7.33% | -7.67% | 0.46 | -0.254 |

## Financing treatment

Financing is **estimated via a conservative stress overlay**, not
modeled. It is a hard live-promotion blocker regardless of the result.

Conservative financing stress from the tested [`forex_bot.financing`](../src/forex_bot/financing.py) module (worst-of-long/short bp/day). Financing is **not** in the engine PnL — this is an after-the-fact overlay. 'Raw expectancy R' is the per-run summary metric.

| pair | trades | total financing debit (USD) | mean debit/trade (R) | raw expectancy R | financing-stressed expectancy R |
|---|---:|---:|---:|---:|---:|
| EUR_USD | 97 | 2.69 | 0.022 | -0.300 | -0.322 |
| GBP_USD | 103 | 2.51 | 0.020 | -0.326 | -0.347 |
| USD_JPY | 229 | 12.61 | 0.044 | -0.000 | -0.045 |
| AUD_USD | 111 | 2.32 | 0.017 | -0.292 | -0.308 |
| USD_CAD | 180 | 4.62 | 0.021 | -0.134 | -0.155 |
| USD_CHF | 92 | 3.16 | 0.028 | -0.394 | -0.422 |

### Financing-stressed expectancy by split

Pair-averaged, consistent with Metrics-by-split.

| split | raw expectancy R | financing debit R | financing-stressed expectancy R |
|---|---:|---:|---:|
| train | -0.229 | 0.027 | -0.256 |
| validation | -0.198 | 0.026 | -0.224 |
| test_untouched | -0.163 | 0.029 | -0.192 |
| full | -0.241 | 0.026 | -0.267 |

## Trade diagnostics (full-window baseline)

Full-window baseline trades: **812**.

| metric | value |
|---|---:|
| win rate | 30.3% |
| mean R | -0.192 |
| median R | -0.061 |
| total PnL (USD) | -209.14 |
| long trades | 446 (expR -0.173) |
| short trades | 366 (expR -0.214) |

**Exit reasons:**

| exit reason | trades | total PnL (USD) | expectancy R | win % |
|---|---:|---:|---:|---:|
| trailing_stop | 644 | -6.29 | -0.054 | 38.0% |
| stop | 167 | -204.35 | -0.723 | 0.0% |
| eod | 1 | +1.50 | +0.008 | 100.0% |

**Top 10 losers:**

| pair | side | entry | bars | R | PnL (USD) | exit |
|---|---|---|---:|---:|---:|---|
| USD_JPY | long | 2022-09-21 | 1 | -0.01 | -1.28 | stop |
| USD_JPY | long | 2023-01-18 | 2 | -0.01 | -1.28 | stop |
| EUR_USD | long | 2020-07-02 | 2 | -1.00 | -1.27 | stop |
| USD_CHF | long | 2020-04-15 | 1 | -1.04 | -1.27 | stop |
| USD_JPY | long | 2022-12-15 | 6 | -0.01 | -1.27 | stop |
| EUR_USD | long | 2020-07-06 | 5 | -1.00 | -1.27 | stop |
| USD_JPY | long | 2020-06-25 | 6 | -0.01 | -1.27 | stop |
| USD_CAD | long | 2021-08-03 | 12 | -0.80 | -1.27 | trailing_stop |
| USD_CAD | long | 2021-09-29 | 6 | -0.79 | -1.27 | stop |
| EUR_USD | short | 2020-04-15 | 1 | -1.00 | -1.27 | stop |

**Top 10 winners:**

| pair | side | entry | bars | R | PnL (USD) | exit |
|---|---|---|---:|---:|---:|---|
| USD_JPY | long | 2022-08-29 | 49 | +0.03 | +5.31 | trailing_stop |
| EUR_USD | short | 2020-02-06 | 47 | +4.11 | +5.21 | trailing_stop |
| EUR_USD | long | 2020-05-27 | 37 | +4.05 | +5.12 | trailing_stop |
| USD_JPY | long | 2022-03-21 | 20 | +0.03 | +5.06 | trailing_stop |
| USD_CAD | long | 2024-10-04 | 44 | +3.02 | +4.86 | trailing_stop |
| AUD_USD | short | 2021-08-17 | 25 | +3.64 | +4.49 | trailing_stop |
| USD_CAD | long | 2022-06-09 | 25 | +2.69 | +4.24 | trailing_stop |
| USD_CAD | long | 2023-04-19 | 42 | +2.49 | +4.03 | trailing_stop |
| USD_JPY | long | 2021-10-08 | 40 | +0.03 | +3.90 | trailing_stop |
| USD_JPY | long | 2021-03-04 | 18 | +0.03 | +3.89 | trailing_stop |

## Comparison vs CAMPAIGN_002 and CAMPAIGN_003

All three campaigns: real OANDA H4 data, identical 6-pair universe, RiskEngine wired in. CAMPAIGN_002 H4 is recomputed over the same 6 pairs (NZD_USD excluded).

| split | campaign | trades | return % | PF | expectancy R | win % |
|---|---|---:|---:|---:|---:|---:|
| train | CAMPAIGN_002 trend H4 | 570 | -2.83% | 0.74 | -0.126 | 32.8% |
| train | CAMPAIGN_003 trend+ADX | 310 | -1.24% | 0.81 | -0.120 | 33.0% |
| train | **CAMPAIGN_004 vol-breakout** | 575 | -5.30% | 0.54 | -0.229 | 28.2% |
| validation | CAMPAIGN_002 trend H4 | 368 | -2.55% | 0.66 | -0.151 | 32.2% |
| validation | CAMPAIGN_003 trend+ADX | 203 | -1.34% | 0.69 | -0.111 | 35.2% |
| validation | **CAMPAIGN_004 vol-breakout** | 411 | -3.69% | 0.56 | -0.198 | 31.7% |
| test_untouched | CAMPAIGN_002 trend H4 | 204 | -1.02% | 0.75 | -0.085 | 35.1% |
| test_untouched | CAMPAIGN_003 trend+ADX | 101 | -0.63% | 0.77 | -0.071 | 35.2% |
| test_untouched | **CAMPAIGN_004 vol-breakout** | 233 | -1.40% | 0.63 | -0.163 | 33.9% |
| full | CAMPAIGN_002 trend H4 | 994 | -5.62% | 0.67 | -0.147 | 32.2% |
| full | CAMPAIGN_003 trend+ADX | 628 | -3.42% | 0.71 | -0.121 | 33.6% |
| full | **CAMPAIGN_004 vol-breakout** | 812 | -6.97% | 0.50 | -0.241 | 28.3% |

Three campaigns now agree on the real 2020-2026 majors: neither the
Donchian trend breakout (CAMPAIGN_002), nor that breakout conditioned
on ADX trend strength (CAMPAIGN_003), nor a volatility-compression
breakout with no trend filter (CAMPAIGN_004) has a positive
untouched-test edge. CAMPAIGN_004 is in fact the **worst** of the three
— removing the trend filter and trading expansion out of compression
did not help; it hurt.

## Artifact paths

- Equity curves: `backtests/campaign_004_volatility_breakout/runs/**/*_equity.csv`
- Trade lists: `backtests/campaign_004_volatility_breakout/runs/**/*_trades.csv`
- **Per-signal risk rejections:** `backtests/campaign_004_volatility_breakout/runs/**/*_risk_rejections.csv`
- Summaries (committed): `backtests/campaign_004_volatility_breakout/runs/**/*_summary.json`
- Run index: `backtests/campaign_004_volatility_breakout/runs/_index.json`

(Equity/trade CSVs gitignored for size; regenerate with
`python scripts/run_campaign_004.py --clean`.)

## Known limitations

1. Financing unmodeled in-engine — stress overlay only; hard live blocker.
2. `compression_lookback=60` is a pre-committed judgement call, not swept.
3. NZD_USD exclusion is partly returns-correlated (acknowledged in the
   pre-commit doc).
4. Backtest fills approximate broker behavior; no live dry-run.

## Pass/fail decision

Pre-committed CAMPAIGN_004 gates. **REJECT.**

Untouched-test expectancy **-0.163 R**. Gate findings:

- untouched-test expectancy negative (-0.163 R)
- untouched-test PF 0.63 < 1.05
- only 0/6 pairs positive on test — not broad
- stress_2x expectancy negative (-0.254 R)
- financing-stressed test expectancy negative (-0.192 R)
- financing remains unmodeled in-engine — blocker for live promotion (docs/financing_decision.md)

**REJECT.** The volatility-compression breakout entry family does not have a positive untouched-test edge on the real 2020-2026 majors — and underperforms both prior trend-following campaigns. Do not paper-trade, demo-trade, or live-trade `volatility_breakout 0.1.0-c004`. With three rejected entry families, the evidence points away from simple breakout/trend H4 systems on these pairs; the next research step should reconsider the premise (timeframe, instrument class, or strategy family) rather than iterate another breakout variant.

_Live trading is not recommended and not in scope for CAMPAIGN_004._

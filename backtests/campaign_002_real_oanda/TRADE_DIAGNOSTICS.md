# CAMPAIGN_002 — Trade-Level Diagnostics

> Diagnostic-only, full-window baseline trades from the diagnostic re-run (reproduces the committed CAMPAIGN_002 trade counts exactly). No strategy rule changed. MAE/MFE are **not available** — the v0 `TradeRecord` does not capture intra-trade excursion; recovering it is listed as a code change in the hypothesis backlog.

Total full-window baseline trades analyzed: **2254**.

## Long vs short

| side | trades | total PnL (USD) | expectancy R | win rate |
|---|---:|---:|---:|---:|
| long | 1153 | -167.34 | -0.124 | 34.3% |
| short | 1101 | -198.94 | -0.105 | 34.5% |

## Expectancy by pair (both timeframes)

| pair | trades | total PnL (USD) | expectancy R | win rate |
|---|---:|---:|---:|---:|
| EUR_USD | 282 | -71.28 | -0.206 | 32.6% |
| GBP_USD | 509 | -49.03 | -0.077 | 37.5% |
| USD_JPY | 597 | -37.33 | -0.000 | 37.4% |
| AUD_USD | 350 | -75.77 | -0.177 | 31.7% |
| USD_CAD | 243 | -69.40 | -0.174 | 30.0% |
| USD_CHF | 234 | -53.02 | -0.204 | 30.8% |
| NZD_USD | 39 | -10.45 | -0.212 | 35.9% |

## H1 vs H4

| gran | trades | total PnL (USD) | expectancy R | win rate |
|---|---:|---:|---:|---:|
| H4 | 1032 | -178.32 | -0.135 | 33.0% |
| H1 | 1222 | -187.96 | -0.097 | 35.6% |

## Entry hour (UTC)

| UTC hour | trades | expectancy R |
|---:|---:|---:|
| 00:00 | 28 | -0.171 |
| 01:00 | 148 | -0.147 |
| 02:00 | 78 | -0.187 |
| 03:00 | 21 | -0.214 |
| 04:00 | 21 | -0.162 |
| 05:00 | 167 | -0.068 |
| 06:00 | 138 | -0.240 |
| 07:00 | 59 | -0.188 |
| 08:00 | 52 | +0.089 |
| 09:00 | 225 | -0.111 |
| 10:00 | 137 | -0.181 |
| 11:00 | 63 | -0.159 |
| 12:00 | 99 | -0.150 |
| 13:00 | 327 | -0.041 |
| 14:00 | 288 | -0.131 |
| 15:00 | 148 | -0.091 |
| 16:00 | 61 | -0.163 |
| 17:00 | 72 | -0.093 |
| 18:00 | 62 | -0.012 |
| 19:00 | 34 | -0.090 |
| 20:00 | 12 | +0.301 |
| 23:00 | 14 | -0.096 |

## Entry day of week

| day | trades | expectancy R |
|---|---:|---:|
| Mon | 387 | -0.150 |
| Tue | 447 | -0.094 |
| Wed | 445 | -0.214 |
| Thu | 550 | -0.117 |
| Fri | 425 | +0.005 |

## Holding period (bars held)

- Min / median / max: 1 / 11 / 65
- Mean: 13.1 bars

| bars held | trades |
|---|---:|
| 1-5 | 542 |
| 6-20 | 1285 |
| 21-60 | 426 |
| 61-120 | 1 |
| 121-240 | 0 |

## Exit reason distribution

| exit reason | trades | total PnL (USD) | expectancy R | win rate |
|---|---:|---:|---:|---:|
| trailing_stop | 1802 | +191.17 | +0.044 | 43.1% |
| stop | 452 | -557.44 | -0.744 | 0.0% |

## R-multiple distribution

| R bucket | trades |
|---|---:|
| ≤ -1.0R (full stop or worse) | 294 |
| -1.0 to -0.3R | 611 |
| -0.3 to 0R | 573 |
| 0 to +1R | 611 |
| +1 to +2R | 113 |
| ≥ +2R | 52 |

- Mean R **-0.114**, median R **-0.008**.

## Top 20 losers

| pair | gran | side | entry | bars | R | PnL (USD) | exit |
|---|---|---|---|---:|---:|---:|---|
| USD_JPY | H4 | long | 2022-09-21 | 1 | -0.01 | -1.30 | stop |
| USD_JPY | H4 | long | 2023-08-29 | 1 | -0.01 | -1.30 | stop |
| USD_JPY | H4 | long | 2022-06-13 | 2 | -0.01 | -1.29 | stop |
| USD_JPY | H4 | long | 2024-04-03 | 8 | -0.01 | -1.29 | stop |
| USD_JPY | H4 | long | 2023-03-02 | 6 | -0.01 | -1.29 | stop |
| USD_JPY | H4 | long | 2024-10-04 | 10 | -0.01 | -1.29 | stop |
| USD_JPY | H4 | long | 2022-04-13 | 4 | -0.01 | -1.29 | stop |
| USD_JPY | H4 | long | 2023-10-31 | 6 | -0.01 | -1.29 | stop |
| USD_JPY | H4 | long | 2023-03-08 | 3 | -0.01 | -1.29 | stop |
| USD_JPY | H4 | long | 2024-06-14 | 2 | -0.01 | -1.29 | stop |
| USD_JPY | H1 | long | 2020-03-20 | 6 | -0.01 | -1.28 | stop |
| USD_JPY | H4 | long | 2024-10-28 | 2 | -0.01 | -1.28 | stop |
| USD_JPY | H4 | long | 2024-11-06 | 6 | -0.01 | -1.28 | stop |
| USD_JPY | H4 | long | 2021-07-13 | 4 | -0.01 | -1.28 | trailing_stop |
| USD_JPY | H4 | long | 2023-06-15 | 3 | -0.01 | -1.28 | trailing_stop |
| USD_CHF | H4 | long | 2021-08-19 | 1 | -1.09 | -1.28 | stop |
| USD_JPY | H4 | short | 2020-10-02 | 4 | -0.01 | -1.28 | stop |
| USD_JPY | H4 | long | 2022-01-04 | 5 | -0.01 | -1.28 | stop |
| USD_JPY | H1 | long | 2022-02-14 | 3 | -0.01 | -1.28 | stop |
| USD_JPY | H4 | short | 2021-04-23 | 1 | -0.01 | -1.28 | stop |

## Top 20 winners

| pair | gran | side | entry | bars | R | PnL (USD) | exit |
|---|---|---|---|---:|---:|---:|---|
| GBP_USD | H4 | short | 2020-03-12 | 25 | +5.89 | +7.38 | trailing_stop |
| USD_JPY | H1 | long | 2024-10-21 | 52 | +0.04 | +6.70 | trailing_stop |
| USD_JPY | H4 | long | 2022-03-16 | 39 | +0.04 | +6.53 | trailing_stop |
| USD_JPY | H4 | long | 2021-02-24 | 53 | +0.05 | +6.49 | trailing_stop |
| USD_JPY | H4 | long | 2022-08-29 | 49 | +0.03 | +5.37 | trailing_stop |
| USD_CAD | H1 | long | 2020-03-16 | 46 | +3.00 | +5.26 | trailing_stop |
| GBP_USD | H4 | short | 2022-04-22 | 25 | +4.13 | +5.18 | trailing_stop |
| EUR_USD | H4 | long | 2020-05-27 | 37 | +4.05 | +5.12 | trailing_stop |
| GBP_USD | H1 | long | 2026-01-22 | 65 | +4.09 | +4.93 | trailing_stop |
| GBP_USD | H4 | long | 2024-08-16 | 32 | +4.11 | +4.92 | trailing_stop |
| USD_JPY | H1 | short | 2022-11-30 | 37 | +0.03 | +4.91 | trailing_stop |
| GBP_USD | H1 | long | 2021-05-07 | 60 | +4.00 | +4.85 | trailing_stop |
| USD_CHF | H4 | long | 2021-02-26 | 41 | +4.09 | +4.72 | trailing_stop |
| GBP_USD | H1 | short | 2020-09-07 | 49 | +3.73 | +4.67 | trailing_stop |
| GBP_USD | H1 | short | 2022-06-10 | 28 | +3.83 | +4.67 | trailing_stop |
| AUD_USD | H4 | short | 2021-08-17 | 25 | +3.64 | +4.58 | trailing_stop |
| USD_JPY | H1 | long | 2025-06-20 | 22 | +0.03 | +4.54 | trailing_stop |
| AUD_USD | H1 | short | 2020-03-17 | 39 | +3.45 | +4.33 | trailing_stop |
| EUR_USD | H1 | short | 2021-03-04 | 58 | +3.57 | +4.30 | trailing_stop |
| USD_JPY | H1 | long | 2020-03-18 | 36 | +0.03 | +4.25 | trailing_stop |

## What drives the losses?

- 1478 losers (66%), 776 winners (34%).
- 1478 losers (100% of losers) exited via stop or trailing stop — i.e. the trade moved against the entry and never recovered. Classic **false-breakout** signature.
- 573 losers are small (-0.3R to 0R): the trailing stop caught a move that briefly went favourable then reversed — **late/whipsaw exits** giving back open profit.
- Average spread paid across all trades: **1.59 pips**. Spread is a constant drag but is not, on its own, the dominant loss source — the dominant source is direction: most breakouts fail to follow through.

- Average winner **+0.61R**, average loser **-0.50R**. 
- Break-even win rate at this R-ratio ≈ **45%**; actual win rate **34%**. The system is **-10 percentage points** from break-even — it loses because it wins too rarely for its average win size, the textbook trend-follower failure mode in chop.

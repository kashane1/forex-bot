# CAMPAIGN 007 — H4 Pullback-Continuation

> **Result: REJECT** (SCREENING ONLY (test lockbox NOT opened)). Real OANDA practice data, RiskEngine
> wired in, pre-committed gates. Part of Research Marathon 001. This
> campaign does **not** authorize paper-loop, demo-loop, or order
> submission.

## Provenance

- **Campaign:** CAMPAIGN_007
- **Branch:** `research-marathon-001`
- **Git commit:** `b71f55cb45ca0b87a1bae6e408cb3573a6466d5d`
- **Working tree dirty at report time:** YES
- **Config:** `configs/campaign_007_h4_pullback.yaml`
- **Config hash:** `4aa81b5e82e80a074fec06a2fe023b7197434e95f43c9ae4edcb8ba9fd41b7ef`
- **Strategy:** `pullback_continuation 0.1.0-c007`
- **Granularity:** H4
- **Pre-commit spec:** `docs/research/CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md`
- **Data source:** real OANDA practice (reused from `data/campaign_002.sqlite3` unless noted)
- **RiskEngine invoked:** YES — all runs, `mode="backtest"`
- **Financing:** estimated via conservative stress overlay
  (`forex_bot.financing`); UNMODELED in-engine; hard live blocker.
- **Total runs:** 36
- **Phases run:** screen

## Test-window discipline

- **Screening gate (train + validation + stress):**
  FAIL.
  - train expectancy negative (-0.164 R)
  - validation expectancy negative (-0.166 R)
  - validation PF 0.66 < 1.05
  - only 1 pair(s) positive on validation
  - stress_15x expectancy negative (-0.181 R)
- **Reported test window (2025-01-01 → 2026-05-20) opened:** NO.
  The test lockbox was NOT opened — the screening gate did not pass, so per marathon discipline the 2025-2026 window was not run.

## Metrics by split

| split | trades | rejected | return % | max-DD % | PF | expectancy R | win % | +pairs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 822 | 699 | -5.76% | -6.71% | 0.62 | -0.164 | 31.5% | 0/6 |
| validation | 568 | 301 | -3.99% | -5.11% | 0.66 | -0.166 | 30.1% | 1/6 |
| full | 1109 | 3367 | -6.93% | -7.91% | 0.61 | -0.178 | 31.5% | 0/6 |

## Metrics by pair — validation (2023-01-01 → 2024-12-31)

| pair | trades | rejected | return % | max-DD % | PF | expectancy R | win % |
|---|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | 88 | 75 | -7.62% | -8.09% | 0.34 | -0.355 | 25.0% |
| EUR_USD | 85 | 79 | -4.08% | -4.32% | 0.56 | -0.193 | 28.2% |
| GBP_USD | 125 | 24 | -7.39% | -7.86% | 0.52 | -0.242 | 28.8% |
| USD_CAD | 90 | 32 | -4.27% | -5.54% | 0.59 | -0.141 | 26.7% |
| USD_CHF | 88 | 53 | -1.29% | -3.75% | 0.86 | -0.063 | 34.1% |
| USD_JPY | 92 | 38 | +0.70% | -1.13% | 1.08 | +0.000 | 38.0% |

## Metrics by pair — full window (2020-01-01 → 2026-05-20)

| pair | trades | rejected | return % | max-DD % | PF | expectancy R | win % |
|---|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | 211 | 507 | -6.22% | -8.18% | 0.73 | -0.120 | 33.2% |
| EUR_USD | 108 | 827 | -8.20% | -8.20% | 0.43 | -0.313 | 27.8% |
| GBP_USD | 222 | 492 | -6.64% | -8.04% | 0.73 | -0.121 | 36.5% |
| USD_CAD | 145 | 616 | -6.95% | -8.22% | 0.59 | -0.154 | 28.3% |
| USD_CHF | 101 | 793 | -8.18% | -8.18% | 0.35 | -0.360 | 26.7% |
| USD_JPY | 322 | 132 | -5.41% | -6.65% | 0.84 | -0.001 | 36.3% |

## Cost stress (full window)

| regime | trades | avg return % | avg max-DD % | avg PF | avg expectancy R |
|---|---:|---:|---:|---:|---:|
| base | 1109 | -6.93% | -7.91% | 0.61 | -0.178 |
| stress_15x | 1039 | -7.38% | -8.10% | 0.59 | -0.181 |
| stress_2x | 1013 | -7.38% | -8.08% | 0.58 | -0.183 |

## Financing stress

Conservative financing stress overlay from the tested `forex_bot.financing` module. Financing is NOT in the engine PnL — a hard live-promotion blocker.

| split | raw expectancy R | financing debit R | financing-stressed expectancy R |
|---|---:|---:|---:|
| train | -0.164 | 0.027 | -0.190 |
| validation | -0.166 | 0.027 | -0.192 |
| full | -0.178 | 0.026 | -0.204 |

## RiskEngine — rejections

Total rejection rows: **21190** (per-run `*_risk_rejections.csv`).

**By code:**

| code | count |
|---|---:|
| `DRAWDOWN_LIMIT` | 12554 |
| `SPREAD_TOO_WIDE` | 3223 |
| `SESSION_BLOCKED` | 2862 |
| `SPREAD_TO_ATR` | 2551 |

**By pair:**

| pair | count |
|---|---:|
| AUD_USD | 2769 |
| EUR_USD | 6068 |
| GBP_USD | 2652 |
| USD_CAD | 3600 |
| USD_CHF | 5008 |
| USD_JPY | 1093 |

**By split:**

| split | count |
|---|---:|
| train | 973 |
| validation | 353 |
| full | 19864 |

**By UTC hour (non-zero):**

| hour | count |
|---:|---:|
| 01:00 | 1743 |
| 02:00 | 856 |
| 05:00 | 2357 |
| 06:00 | 1193 |
| 09:00 | 1979 |
| 10:00 | 1068 |
| 13:00 | 2050 |
| 14:00 | 1037 |
| 17:00 | 2448 |
| 18:00 | 1151 |
| 21:00 | 3233 |
| 22:00 | 2075 |

## Trade diagnostics (full-window baseline)

Full-window baseline trades: **1109**.

| metric | value |
|---|---:|
| win rate | 33.0% |
| mean R | -0.131 |
| median R | -0.009 |
| total PnL USD | -207.95 |

**Exit reasons:**

| exit | trades | total PnL | expectancy R | win % |
|---|---:|---:|---:|---:|
| trailing_stop | 878 | +75.78 | +0.025 | 41.7% |
| stop | 231 | -283.73 | -0.724 | 0.0% |

**Top 5 losers / winners:**

| pair | side | entry | bars | R | PnL |
|---|---|---|---:|---:|---:|
| AUD_USD | short | 2020-10-02 | 12 | -1.00 | -1.29 |
| AUD_USD | short | 2021-12-22 | 2 | -1.00 | -1.28 |
| USD_CAD | long | 2020-03-31 | 2 | -0.71 | -1.28 |
| AUD_USD | short | 2020-09-30 | 3 | -1.00 | -1.28 |
| AUD_USD | short | 2020-10-22 | 7 | -1.00 | -1.28 |
| GBP_USD | short | 2022-04-22 | 25 | +4.13 | +5.04 |
| USD_JPY | long | 2022-03-07 | 35 | +0.04 | +5.65 |
| AUD_USD | short | 2021-08-16 | 31 | +4.46 | +5.69 |
| USD_JPY | long | 2021-02-23 | 59 | +0.06 | +8.25 |
| GBP_USD | short | 2020-03-10 | 35 | +7.04 | +8.76 |

## Comparison to prior campaigns (real OANDA H4, untouched test)

| campaign | expectancy R | PF | return % |
|---|---|---|---|
| CAMPAIGN_002 trend H4 | −0.085 R | 0.75 | −1.02% |
| CAMPAIGN_003 trend+ADX H4 | −0.071 R | 0.77 | −0.63% |
| CAMPAIGN_004 vol-breakout H4 | −0.163 R | 0.63 | −1.40% |

(This campaign's screening/test figures are in the tables above. Prior
campaigns ran the test window directly; this marathon screens first.)

## Known limitations

1. Financing unmodeled in-engine — stress overlay only; hard live blocker.
2. Backtest fills approximate broker behavior; no live dry-run.
3. Single pre-committed configuration — no parameter sweep (by design).

## Pass/fail decision

Stage: **SCREENING ONLY (test lockbox NOT opened)**. Verdict: **REJECT**.

- train expectancy negative (-0.164 R)
- validation expectancy negative (-0.166 R)
- validation PF 0.66 < 1.05
- only 1 pair(s) positive on validation
- stress_15x expectancy negative (-0.181 R)

Pre-committed gates not met. Do not paper-trade, demo-trade, or live-trade this strategy.

_Live trading is not recommended and not in scope._

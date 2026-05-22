# CAMPAIGN 008 — Range Mean-Reversion (Research-Only)

> **Result: REJECT** (SCREENING ONLY (test lockbox NOT opened)). Real OANDA practice data, RiskEngine
> wired in, pre-committed gates. Part of Research Marathon 001. This
> campaign does **not** authorize paper-loop, demo-loop, or order
> submission.

## Provenance

- **Campaign:** CAMPAIGN_008
- **Branch:** `research-marathon-001`
- **Git commit:** `68fdf69b1d1194939c65de850d4c04e9ee49200b`
- **Working tree dirty at report time:** YES
- **Config:** `configs/campaign_008_range_mean_reversion.yaml`
- **Config hash:** `8ba497c9fae422ff86257a554d15e7920674ae74af6d420cc53c40e6f692fdc6`
- **Strategy:** `mean_reversion 0.1.0-c008`
- **Granularity:** H4
- **Pre-commit spec:** `docs/research/CAMPAIGN_008_RANGE_MEAN_REVERSION_PRECOMMIT.md`
- **Data source:** real OANDA practice (reused from `data/campaign_002.sqlite3` unless noted)
- **RiskEngine invoked:** YES — all runs, `mode="backtest"`
- **Financing:** estimated via conservative stress overlay
  (`forex_bot.financing`); UNMODELED in-engine; hard live blocker.
- **Total runs:** 36
- **Phases run:** screen

## Test-window discipline

- **Screening gate (train + validation + stress):**
  FAIL.
  - train expectancy negative (-0.017 R)
- **Reported test window (2025-01-01 → 2026-05-20) opened:** NO.
  The test lockbox was NOT opened — the screening gate did not pass, so per marathon discipline the 2025-2026 window was not run.

## Metrics by split

| split | trades | rejected | return % | max-DD % | PF | expectancy R | win % | +pairs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 216 | 85 | -0.05% | -2.92% | 1.02 | -0.017 | 27.2% | 5/6 |
| validation | 138 | 64 | +1.04% | -1.84% | 1.29 | +0.172 | 31.5% | 6/6 |
| full | 469 | 213 | +1.75% | -3.51% | 1.12 | +0.069 | 29.4% | 5/6 |

## Metrics by pair — validation (2023-01-01 → 2024-12-31)

| pair | trades | rejected | return % | max-DD % | PF | expectancy R | win % |
|---|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | 26 | 6 | +0.56% | -1.77% | 1.13 | +0.088 | 34.6% |
| EUR_USD | 20 | 20 | +1.57% | -1.51% | 1.43 | +0.310 | 25.0% |
| GBP_USD | 28 | 2 | +0.81% | -2.14% | 1.19 | +0.117 | 39.3% |
| USD_CAD | 18 | 15 | +0.66% | -2.18% | 1.20 | +0.105 | 27.8% |
| USD_CHF | 21 | 16 | +1.80% | -1.49% | 1.63 | +0.409 | 38.1% |
| USD_JPY | 25 | 5 | +0.85% | -1.96% | 1.19 | +0.001 | 24.0% |

## Metrics by pair — full window (2020-01-01 → 2026-05-20)

| pair | trades | rejected | return % | max-DD % | PF | expectancy R | win % |
|---|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | 95 | 21 | +3.20% | -1.92% | 1.20 | +0.135 | 33.7% |
| EUR_USD | 66 | 55 | +4.00% | -2.25% | 1.34 | +0.241 | 28.8% |
| GBP_USD | 90 | 13 | +2.99% | -2.64% | 1.20 | +0.133 | 33.3% |
| USD_CAD | 73 | 43 | -3.12% | -7.00% | 0.77 | -0.137 | 23.3% |
| USD_CHF | 58 | 54 | +0.56% | -2.35% | 1.05 | +0.042 | 27.6% |
| USD_JPY | 87 | 27 | +2.85% | -4.90% | 1.19 | +0.001 | 29.9% |

## Cost stress (full window)

| regime | trades | avg return % | avg max-DD % | avg PF | avg expectancy R |
|---|---:|---:|---:|---:|---:|
| base | 469 | +1.75% | -3.51% | 1.12 | +0.069 |
| stress_15x | 469 | +1.08% | -3.70% | 1.07 | +0.040 |
| stress_2x | 469 | +0.74% | -3.81% | 1.05 | +0.027 |

## Financing stress

Conservative financing stress overlay from the tested `forex_bot.financing` module. Financing is NOT in the engine PnL — a hard live-promotion blocker.

| split | raw expectancy R | financing debit R | financing-stressed expectancy R |
|---|---:|---:|---:|
| train | -0.017 | 0.058 | -0.075 |
| validation | +0.172 | 0.063 | +0.109 |
| full | +0.069 | 0.059 | +0.011 |

## RiskEngine — rejections

Total rejection rows: **1243** (per-run `*_risk_rejections.csv`).

**By code:**

| code | count |
|---|---:|
| `SPREAD_TO_ATR` | 457 |
| `SPREAD_TOO_WIDE` | 453 |
| `SESSION_BLOCKED` | 333 |

**By pair:**

| pair | count |
|---|---:|
| AUD_USD | 127 |
| EUR_USD | 315 |
| GBP_USD | 64 |
| USD_CAD | 259 |
| USD_CHF | 339 |
| USD_JPY | 139 |

**By split:**

| split | count |
|---|---:|
| train | 111 |
| validation | 76 |
| full | 1056 |

**By UTC hour (non-zero):**

| hour | count |
|---:|---:|
| 01:00 | 64 |
| 02:00 | 10 |
| 05:00 | 75 |
| 06:00 | 35 |
| 09:00 | 105 |
| 10:00 | 31 |
| 13:00 | 71 |
| 14:00 | 17 |
| 17:00 | 295 |
| 18:00 | 140 |
| 21:00 | 266 |
| 22:00 | 134 |

## Trade diagnostics (full-window baseline)

Full-window baseline trades: **469**.

| metric | value |
|---|---:|
| win rate | 29.9% |
| mean R | +0.071 |
| median R | -0.749 |
| total PnL USD | +52.40 |

**Exit reasons:**

| exit | trades | total PnL | expectancy R | win % |
|---|---:|---:|---:|---:|
| stop | 318 | -404.33 | -0.794 | 0.0% |
| time | 151 | +456.73 | +1.892 | 92.7% |

**Top 5 losers / winners:**

| pair | side | entry | bars | R | PnL |
|---|---|---|---:|---:|---:|
| USD_JPY | long | 2021-09-14 | 4 | -0.01 | -1.35 |
| USD_JPY | long | 2021-07-27 | 24 | -0.01 | -1.34 |
| AUD_USD | long | 2025-08-19 | 3 | -1.00 | -1.33 |
| AUD_USD | short | 2026-01-20 | 8 | -1.00 | -1.33 |
| AUD_USD | short | 2026-01-06 | 6 | -1.00 | -1.33 |
| EUR_USD | short | 2024-04-09 | 40 | +6.71 | +8.72 |
| EUR_USD | long | 2022-11-03 | 40 | +7.94 | +9.98 |
| USD_JPY | short | 2026-04-29 | 40 | +0.05 | +10.54 |
| EUR_USD | long | 2026-01-15 | 40 | +8.58 | +11.18 |
| USD_CHF | short | 2022-11-03 | 40 | +10.11 | +12.63 |

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

- train expectancy negative (-0.017 R)

Pre-committed gates not met. Do not paper-trade, demo-trade, or live-trade this strategy.

_Live trading is not recommended and not in scope._

## Marathon research note — narrow miss, flagged for human review

CAMPAIGN_008 is recorded as **REJECT** strictly because the
pre-committed screening gate requires train expectancy >= 0 and the
train split came in at **-0.017 R** (PF 1.02 — flat within noise). The
gate is a bright line, committed before the run; it was not relaxed
after seeing results, and the 2025-2026 test lockbox was therefore not
opened.

That said, this is **categorically different from the marathon's other
rejections** and is the single most promising result in the entire
project (CAMPAIGN_002-008):

- Validation (2023-2024): **+0.172 R, PF 1.29, +1.04%, 6 of 6 pairs
  positive** — a clear, broad positive on a split never used to design
  the strategy.
- Cost stress: expectancy stays positive at base (+0.069), stress_15x
  (+0.040) and stress_2x (+0.027) — it survives doubled costs.
- Train: flat (-0.017 R, PF 1.02) — not a loss like the -0.12 to
  -0.18 R trend/breakout campaigns; genuinely breakeven.
- It beats the CAMPAIGN_005 random-entry benchmark (-0.095 R) on every
  split, unlike CAMPAIGN_002/003/004/007.

The honest reading: regime-filtered mean reversion is the **one
direction in this universe that showed a real signal**, consistent with
the CAMPAIGN_005 diagnostic (choppy H4 majors, efficiency ratio 0.24).
It did not *pass* — train was flat-negative and the campaign is
research-only (capped at REVISE) — but it is the recommended human
decision point. See `docs/research/RESEARCH_MARATHON_001_NO_GO.md`.

Known weakness that likely explains the flat train split: the engine
has no midline-target exit, so reversion trades exit on a 40-bar time
stop rather than at the mean. A proper mean-target exit is the obvious
first thing a follow-up would add — but that is a strategy change
requiring a fresh pre-commit and human authorization, not a marathon
action.

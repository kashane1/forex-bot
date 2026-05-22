# CAMPAIGN 009 — Mean-Reversion + Midline Exit

> **Result: REJECT** (SCREENING ONLY (test lockbox NOT opened)). Real OANDA practice data, RiskEngine wired in, pre-committed gates. Human-authorized follow-up to CAMPAIGN_008 — **not** a marathon campaign. This campaign does **not** authorize paper-loop, demo-loop, or order submission.

## Provenance

- **Campaign:** CAMPAIGN_009 (mean-reversion + midline exit)
- **Branch:** `campaign-009-mean-reversion-human-review`
- **Git commit (run time):** `6c8d8faead8eff6821659cb58690a385de5acd02`
- **Working tree dirty at run time:** YES
- **Git commit (report time):** `6c8d8faead8eff6821659cb58690a385de5acd02`
- **Working tree dirty at report time:** YES
- **Config:** `configs/campaign_009_mean_reversion.yaml`
- **Config hash:** `47b5414c2639fe4f2b3278553d9af24044a08abfd7951e56745a668ca0e2f882`
- **Strategy:** `mean_reversion 0.2.0-c009`
- **Granularity:** H4
- **Pre-commit spec:** `docs/research/CAMPAIGN_009_PRECOMMIT.md`
- **Human-review authority:** `docs/research/CAMPAIGN_008_HUMAN_REVIEW.md`
- **Data source:** real OANDA practice H4 candles, reused from `data/campaign_002.sqlite3` (provenance hashes below).
- **RiskEngine invoked:** YES — all runs, `mode="backtest"`.
- **Financing:** estimated via conservative stress overlay (`forex_bot.financing`); UNMODELED in-engine; hard live blocker.
- **Total runs:** 36
- **Phases run:** screen
- **Rejection CSVs:** `backtests/campaign_009_mean_reversion/runs/<split>/<regime>/*_risk_rejections.csv` (one per run; committed).

## Exact diff versus CAMPAIGN_008

CAMPAIGN_009 changes **exactly one rule** versus `mean_reversion 0.1.0-c008`;
every entry/regime parameter is frozen identical.

| dimension | CAMPAIGN_008 | CAMPAIGN_009 |
|---|---|---|
| strategy version | `mean_reversion 0.1.0-c008` | `mean_reversion 0.2.0-c009` |
| `midline_exit` config | absent (defaulted false) | **`true`** |
| exit model | hard stop **or** 40-bar time stop | hard stop **or midline target or** 40-bar time stop |
| midline target | none (engine had no take-profit path) | rolling mean of close over `zscore_lookback` (=20) bars, emitted as the signal `take_profit_price` |
| ADX-14 regime gate | < 20.0 | < 20.0 (unchanged) |
| z-score thresholds | -2.0 / +2.0 | -2.0 / +2.0 (unchanged) |
| RSI confirmation | < 35 / > 65 | < 35 / > 65 (unchanged) |
| hard stop | 1.5 x ATR-14 | 1.5 x ATR-14 (unchanged) |
| time stop | 40 bars | 40 bars (unchanged) |
| risk per trade | 0.25% | 0.25% (unchanged) |
| universe / timeframe | 6 majors / H4 | 6 majors / H4 (unchanged) |

Engine: `_OpenTrade` gained an optional `take_profit_price`; the exit
check now tests stop -> target -> time, with the adverse stop keeping
same-bar precedence. With `midline_exit` false the emitted signal is
byte-identical to c008, so CAMPAIGN_008 stays exactly reproducible.

## Data provenance & request hashes

Real OANDA practice candles, reused from the identical store CAMPAIGN_002-008 used. Each data-request hash is a deterministic function of instrument / granularity / window / source / candle-count, so a matching hash proves the exact same candles were replayed.

| split | pair | data source | data-request hash |
|---|---|---|---|
| train | AUD_USD | oanda-practice | `a99b361405ea09f9` |
| train | EUR_USD | oanda-practice | `0245bbb93292ed45` |
| train | GBP_USD | oanda-practice | `db68e305c34b0164` |
| train | USD_CAD | oanda-practice | `3cf380e718827472` |
| train | USD_CHF | oanda-practice | `2ad33a9087468c86` |
| train | USD_JPY | oanda-practice | `ab966a4fc624d0eb` |
| validation | AUD_USD | oanda-practice | `d17b45bf5a187703` |
| validation | EUR_USD | oanda-practice | `49a39daf47fbdf7c` |
| validation | GBP_USD | oanda-practice | `1f50c172361a28f9` |
| validation | USD_CAD | oanda-practice | `42f3e98cc961d2d6` |
| validation | USD_CHF | oanda-practice | `eb8da165e37c1a9b` |
| validation | USD_JPY | oanda-practice | `8a57e2979f604bde` |

## Test-window discipline

- **Screening gate (train + validation, base/15x/2x):** FAIL.
- **Reported test window (2025-01-01 -> 2026-05-20) opened:** NO.
  The test lockbox was NOT opened — the screening gate did not pass, so per the pre-commit the 2025-2026 window and the full descriptive window were not run. No parameters were tuned in response.

## Pass/fail gate table

### Screening gate (pre-committed)

| gate | required | observed | result |
|---|---|---:|:--:|
| 1. train expectancy >= 0 | >= 0.000 R | -0.062 R | **FAIL** |
| 2. validation expectancy > 0 | > 0.000 R | +0.170 R | **PASS** |
| 3. validation profit factor >= 1.05 | >= 1.05 | 1.37 | **PASS** |
| 4. stress_2x validation expectancy >= 0 | >= 0.000 R | +0.119 R | **PASS** |
| 5. financing-stressed validation expectancy >= 0 | >= 0.000 R | +0.139 R | **PASS** |
| 6. >= 2 of 6 pairs positive (validation) | >= 2 | 4/6 | **PASS** |
| 7. validation trade count meaningful | >= 30 | 151 | **PASS** |
| 8. worst validation max-DD within policy | >= -8.0% | -1.90% | **PASS** |
| 9. RiskEngine invoked on every screening run | all runs | yes | **PASS** |
| 10. data provenance clean | all oanda-practice | yes | **PASS** |

## Metrics by split (base cost regime)

| split | trades | rejected | return % | max-DD % | worst-DD % | PF | expectancy R | win % | +pairs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 252 | 93 | -0.08% | -2.45% | -4.02% | 0.97 | -0.062 | 38.4% | 2/6 |
| validation | 151 | 69 | +1.14% | -1.40% | -1.90% | 1.37 | +0.170 | 47.8% | 4/6 |

## Metrics by pair — validation (2023-01-01 -> 2024-12-31)

| pair | trades | rejected | return % | max-DD % | PF | expectancy R | win % |
|---|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | 29 | 6 | +1.83% | -1.26% | 1.52 | +0.248 | 51.7% |
| EUR_USD | 22 | 21 | -0.14% | -1.19% | 0.96 | -0.023 | 40.9% |
| GBP_USD | 31 | 2 | +3.10% | -1.53% | 1.85 | +0.391 | 54.8% |
| USD_CAD | 19 | 19 | +0.10% | -1.90% | 1.04 | +0.014 | 42.1% |
| USD_CHF | 23 | 16 | +2.01% | -0.76% | 1.85 | +0.391 | 56.5% |
| USD_JPY | 27 | 5 | -0.06% | -1.74% | 0.99 | -0.000 | 40.7% |

## Metrics by pair — train (2020-01-01 -> 2022-12-31)

| pair | trades | rejected | return % | max-DD % | PF | expectancy R | win % |
|---|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | 55 | 10 | +3.77% | -1.24% | 1.55 | +0.269 | 49.1% |
| EUR_USD | 38 | 17 | -0.57% | -1.65% | 0.90 | -0.057 | 39.5% |
| GBP_USD | 43 | 8 | -1.04% | -3.12% | 0.85 | -0.092 | 34.9% |
| USD_CAD | 45 | 15 | -1.94% | -4.02% | 0.74 | -0.136 | 33.3% |
| USD_CHF | 25 | 28 | -2.10% | -2.96% | 0.54 | -0.358 | 28.0% |
| USD_JPY | 46 | 15 | +1.39% | -1.71% | 1.22 | +0.001 | 45.7% |

## Cost stress

| split | regime | trades | avg return % | avg max-DD % | avg PF | avg expectancy R |
|---|---|---:|---:|---:|---:|---:|
| train | base | 252 | -0.08% | -2.45% | 0.97 | -0.062 |
| train | stress_15x | 252 | -0.43% | -2.63% | 0.92 | -0.085 |
| train | stress_2x | 252 | -0.60% | -2.72% | 0.89 | -0.096 |
| validation | base | 151 | +1.14% | -1.40% | 1.37 | +0.170 |
| validation | stress_15x | 151 | +0.92% | -1.48% | 1.29 | +0.136 |
| validation | stress_2x | 151 | +0.80% | -1.52% | 1.25 | +0.119 |

## Financing stress

Conservative financing stress overlay from the tested `forex_bot.financing` module. Financing is NOT in the engine PnL — a hard live-promotion blocker.

| split | raw expectancy R | financing debit R | financing-stressed expectancy R |
|---|---:|---:|---:|
| train | -0.062 | 0.027 | -0.089 |
| validation | +0.170 | 0.031 | +0.139 |

## RiskEngine — rejections

Total rejection rows: **612** (per-run `*_risk_rejections.csv`).

**By code:**

| code | count |
|---|---:|
| `SPREAD_TO_ATR` | 234 |
| `SPREAD_TOO_WIDE` | 219 |
| `SESSION_BLOCKED` | 159 |

**By pair:**

| pair | count |
|---|---:|
| AUD_USD | 57 |
| EUR_USD | 147 |
| GBP_USD | 33 |
| USD_CAD | 132 |
| USD_CHF | 177 |
| USD_JPY | 66 |

**By split:**

| split | count |
|---|---:|
| train | 363 |
| validation | 249 |

**By UTC hour (non-zero):**

| hour | count |
|---:|---:|
| 01:00 | 24 |
| 02:00 | 6 |
| 05:00 | 33 |
| 06:00 | 21 |
| 09:00 | 54 |
| 10:00 | 9 |
| 13:00 | 36 |
| 14:00 | 9 |
| 17:00 | 162 |
| 18:00 | 63 |
| 21:00 | 135 |
| 22:00 | 60 |

## Trade diagnostics — Screening-window (train + validation)

Screening-window (train + validation) baseline trades: **403**.

| metric | value |
|---|---:|
| win rate | 42.9% |
| mean R | +0.054 |
| median R | -0.009 |
| total PnL USD | +31.79 |

**Exit reasons:**

| exit | trades | total PnL | expectancy R | win % |
|---|---:|---:|---:|---:|
| stop | 227 | -288.67 | -0.789 | 0.0% |
| target | 165 | +313.14 | +1.182 | 100.0% |
| time | 10 | +7.36 | +0.578 | 80.0% |
| eod | 1 | -0.05 | -0.037 | 0.0% |

**Top 5 losers / winners:**

| pair | side | entry | bars | exit | R | PnL |
|---|---|---|---:|---|---:|---:|
| GBP_USD | short | 2024-05-15 | 1 | stop | -1.00 | -1.34 |
| GBP_USD | short | 2024-05-15 | 27 | stop | -1.00 | -1.33 |
| GBP_USD | long | 2024-06-20 | 4 | stop | -1.00 | -1.33 |
| GBP_USD | short | 2024-05-15 | 2 | stop | -1.00 | -1.33 |
| GBP_USD | short | 2024-08-13 | 16 | stop | -1.00 | -1.32 |
| GBP_USD | short | 2020-10-21 | 29 | target | +2.28 | +2.87 |
| USD_JPY | short | 2023-09-05 | 21 | target | +0.02 | +2.97 |
| USD_CHF | short | 2024-04-10 | 39 | target | +2.53 | +2.97 |
| AUD_USD | short | 2024-06-12 | 12 | target | +2.36 | +3.07 |
| AUD_USD | short | 2022-08-10 | 28 | target | +2.51 | +3.18 |

## Comparison to CAMPAIGN_008 (same data, same entry rules)

| split | campaign | trades | return % | max-DD % | PF | expectancy R | win % |
|---|---|---:|---:|---:|---:|---:|---:|
| train | c009 | 252 | -0.08% | -2.45% | 0.97 | -0.062 | 38.4% |
| train | c008 | 216 | -0.05% | -2.92% | 1.02 | -0.017 | 27.2% |
| validation | c009 | 151 | +1.14% | -1.40% | 1.37 | +0.170 | 47.8% |
| validation | c008 | 138 | +1.04% | -1.84% | 1.29 | +0.172 | 31.5% |

_CAMPAIGN_008 figures are quoted verbatim from the committed `backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md`; CAMPAIGN_008 did not open its test window._

## Comparison to prior campaigns (real OANDA H4, untouched test)

| campaign | expectancy R | PF | return % |
|---|---|---|---|
| CAMPAIGN_002 trend H4 | -0.085 R | 0.75 | -1.02% |
| CAMPAIGN_003 trend+ADX H4 | -0.071 R | 0.77 | -0.63% |
| CAMPAIGN_004 vol-breakout H4 | -0.163 R | 0.63 | -1.40% |

## Research note — the midline-exit hypothesis is falsified

CAMPAIGN_009 tested exactly one predeclared hypothesis: that giving the
strategy a midline-target exit would lift CAMPAIGN_008's flat train
split (the sole reason c008 was REJECT). It did the opposite.

**On the train split — identical data, identical entry rules —
expectancy fell from −0.017 R (c008) to −0.062 R (c009).** Validation
barely moved (+0.170 R versus c008's +0.172 R). The one change made the
screening result worse, not better.

The exit-reason breakdown shows the mechanism. The midline `target`
exit fired as designed — 165 of the 403 screening-window trades exited
at the mean, every one a winner, averaging **+1.18 R**. But c008's
`time`-stop winners averaged **+1.89 R** on its full window: the
reverting trades c008 let run toward the 40-bar timer, c009 cashes out
early at the mean. The midline target banks the reversion sooner and
**caps the upside**. That forgone upside outweighs the losers the early
exit rescues — decisively so on the train era, roughly neutrally on the
validation era.

This falsifies the hypothesis behind CAMPAIGN_009: c008's flat train
split was **not** an artifact of exiting on a 40-bar timer instead of
at the mean. Two independent, separately pre-committed campaigns now
agree — regime-filtered H4 mean reversion shows a real validation-era
signal (2023–2024) that **does not generalise to the train era
(2020–2022) under either exit rule**. The train split is flat-to-negative
both ways.

**Consequence.** CAMPAIGN_009 is REJECT on its own pre-committed gate,
exactly as written — no gate relaxed, no parameter tuned, the test
window never opened. The result strengthens, rather than weakens, the
Research Marathon 001 NO-GO conclusion. No further campaign is
authorised by this outcome. Any further mean-reversion research would
require a fresh human decision and a new pre-commit; the marathon is
not resumed.

## Known limitations

1. **Financing is unmodeled in-engine** — a conservative stress overlay only, applied above. It remains a hard, unconditional blocker for any live consideration regardless of any figure in this report.
2. Backtest fills approximate broker behaviour; no live dry-run.
3. Single pre-committed configuration — no parameter sweep, by design. The midline exit has no free parameter (its window equals `zscore_lookback`).
4. Mean reversion has fat-tailed loss risk (a range breaking into a trend); the ADX gate and hard stop bound it but do not remove it.
5. The midline target can cap winning trades; the exit-reason breakdown above is the evidence to judge whether it helped or hurt versus the c008 time stop.
6. NZD_USD is excluded from the universe (cost structure; partly returns-correlated — acknowledged since CAMPAIGN_003).

## Pass/fail decision

Stage: **SCREENING ONLY (test lockbox NOT opened)**. Verdict: **REJECT**.

One or more pre-committed **screening** gates failed (see the gate table). Per the pre-commit, the 2025-2026 test window was not opened, no parameters were tuned, and the verdict is **REJECT**. Do not paper-trade, demo-trade, or live-trade this strategy.

_Live trading is not recommended and not in scope. The strategy is `paper_only = True`._

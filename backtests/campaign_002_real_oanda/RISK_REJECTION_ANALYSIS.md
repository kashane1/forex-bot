# CAMPAIGN_002 — Risk Rejection Analysis

> Diagnostic-only. By-pair / by-timeframe / by-split counts are read from the committed CAMPAIGN_002 summary JSONs. By-hour and by-session counts come from a diagnostic re-run of the 14 full-window baselines (CAMPAIGN_002 did not export per-rejection timestamps). The re-run reproduced every committed trade count exactly. **No risk setting was changed.**

## Rejections by split (committed summaries)

| split | gran | candidate signals | trades | rejected | trade/candidate |
|---|---|---:|---:|---:|---:|
| train | H4 | 1093 | 597 | 496 | 54.6% |
| validation | H4 | 743 | 373 | 370 | 50.2% |
| test_untouched | H4 | 469 | 207 | 262 | 44.1% |
| full | H4 | 2785 | 1032 | 1753 | 37.1% |
| train | H1 | 7306 | 725 | 6581 | 9.9% |
| validation | H1 | 4969 | 322 | 4647 | 6.5% |
| test_untouched | H1 | 3245 | 247 | 2998 | 7.6% |
| full | H1 | 15838 | 1222 | 14616 | 7.7% |

## Rejections by pair × timeframe (full window)

| pair | gran | trades | rejected | trade/candidate | dominant reasons |
|---|---|---:|---:|---:|---|
| EUR_USD | H4 | 132 | 274 | 32.5% | SPREAD_TOO_WIDE 179, DRAWDOWN_LIMIT 175, SESSION_BLOCKED 48 |
| GBP_USD | H4 | 198 | 55 | 78.3% | SESSION_BLOCKED 29, SPREAD_TO_ATR 22, SPREAD_TOO_WIDE 20 |
| USD_JPY | H4 | 217 | 84 | 72.1% | SESSION_BLOCKED 47, SPREAD_TOO_WIDE 35, SPREAD_TO_ATR 14 |
| AUD_USD | H4 | 144 | 271 | 34.7% | DRAWDOWN_LIMIT 226, SESSION_BLOCKED 61, SPREAD_TO_ATR 34 |
| USD_CAD | H4 | 122 | 373 | 24.6% | DRAWDOWN_LIMIT 328, SPREAD_TO_ATR 137, SPREAD_TOO_WIDE 50 |
| USD_CHF | H4 | 181 | 120 | 60.1% | SPREAD_TO_ATR 81, DRAWDOWN_LIMIT 31, SPREAD_TOO_WIDE 27 |
| NZD_USD | H4 | 38 | 576 | 6.2% | SPREAD_TO_ATR 532, SPREAD_TOO_WIDE 252, SESSION_BLOCKED 95 |
| EUR_USD | H1 | 150 | 2100 | 6.7% | SPREAD_TO_ATR 1923, DRAWDOWN_LIMIT 1328, SPREAD_TOO_WIDE 837 |
| GBP_USD | H1 | 311 | 1618 | 16.1% | SPREAD_TO_ATR 1603, SPREAD_TOO_WIDE 99, SESSION_BLOCKED 39 |
| USD_JPY | H1 | 380 | 1569 | 19.5% | SPREAD_TO_ATR 1402, DRAWDOWN_LIMIT 290, SPREAD_TOO_WIDE 133 |
| AUD_USD | H1 | 206 | 1961 | 9.5% | SPREAD_TO_ATR 1948, SESSION_BLOCKED 51, SPREAD_TOO_WIDE 47 |
| USD_CAD | H1 | 121 | 2308 | 5.0% | SPREAD_TO_ATR 2295, SPREAD_TOO_WIDE 118, SESSION_BLOCKED 52 |
| USD_CHF | H1 | 53 | 2380 | 2.2% | SPREAD_TO_ATR 2373, SPREAD_TOO_WIDE 200, SESSION_BLOCKED 46 |
| NZD_USD | H1 | 1 | 2680 | 0.0% | SPREAD_TO_ATR 2676, SPREAD_TOO_WIDE 881, SESSION_BLOCKED 72 |

## Rejections by UTC hour (diagnostic re-run, full window)

| UTC hour | rejections | session |
|---:|---:|---|
| 00:00 | 624 | Asia/late |
| 01:00 | 739 | Asia/late |
| 02:00 | 575 | Asia/late |
| 03:00 | 425 | Asia/late |
| 04:00 | 391 | Asia/late |
| 05:00 | 622 | Asia/late |
| 06:00 | 717 | London |
| 07:00 | 843 | London |
| 08:00 | 851 | London |
| 09:00 | 926 | London |
| 10:00 | 779 | London |
| 11:00 | 663 | London |
| 12:00 | 1050 | London/NY overlap |
| 13:00 | 1316 | London/NY overlap |
| 14:00 | 1248 | London/NY overlap |
| 15:00 | 820 | London/NY overlap |
| 16:00 | 611 | NY |
| 17:00 | 664 | NY |
| 18:00 | 652 | NY |
| 19:00 | 451 | NY |
| 20:00 | 319 | NY |
| 21:00 | 353 | Asia/late |
| 22:00 | 369 | Asia/late |
| 23:00 | 361 | Asia/late |

### Rejections by trading session

| session | rejections |
|---|---:|
| London | 4779 |
| Asia/late | 4459 |
| London/NY overlap | 4434 |
| NY | 2697 |

## Rejections by reason code (diagnostic re-run, full window)

| code | count | peak UTC hour | protective? |
|---|---:|---:|---|
| `SPREAD_TO_ATR` | 15081 | 13:00 | yes — avoids entries where cost dwarfs the move |
| `SPREAD_TOO_WIDE` | 2897 | 13:00 | yes — avoids paying a bad spread |
| `DRAWDOWN_LIMIT` | 2390 | 13:00 | yes — hard equity-preservation stop |
| `SESSION_BLOCKED` | 729 | 21:00 | yes — avoids rollover / Friday-close / Sunday-open |
| `MARGIN_BUFFER` | 37 | 09:00 | yes — leverage ceiling |

## Interpretation: protecting the bot, or choking opportunity?

- Full-window diagnostic re-run: **2254** trades vs **21134** rejections across 14 series.
- Spread-family rejections (`SPREAD_TO_ATR` + `SPREAD_TOO_WIDE`): **17978** (85% of all rejections).
- `DRAWDOWN_LIMIT`: **2390** (11%). This fires *after* equity has already fallen 8% — it is a symptom of the strategy losing money, not a cause of missed profit.

The spread filters are doing their job: they block entries whose edge is smaller than the cost to enter. That is **protective**, and removing them would not create profit — it would convert rejected signals into *losing* trades (the strategy is already net-negative on the signals that DO pass). `DRAWDOWN_LIMIT` rejections are a consequence of the negative expectancy, not an independent problem.

**However** — the spread filter is also the clearest *structural* finding: on H1, and on wide-spread pairs (NZD_USD, USD_CAD, USD_CHF), the hourly ATR is simply too small relative to the spread for a breakout edge to clear costs. That is a universe/timeframe selection problem, addressed in the hypothesis backlog — not a reason to loosen the filter.

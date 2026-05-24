# CAMPAIGN_012 — Portfolio-Risk Diagnostics (auto-generated)

> Diagnostic only — does not gate the verdict. CAMPAIGN_012 is
> research-only; even a clean diagnostics pass produces
> RESEARCH_PASS_UNAPPROVED at best. configs/approved_strategies.yaml
> remains approved: [].

## Per-pair exposure

| pair | trades | total units | total notional (quote ccy) | total PnL (USD) | max loss streak | max win streak | largest single loss | largest single win |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EUR_USD | 479 | 90,063 | 97,382 | -5.36 | 8 | 6 | -1.30 | +4.98 |
| GBP_USD | 555 | 82,832 | 105,856 | -40.61 | 8 | 6 | -1.28 | +2.53 |
| USD_JPY | 624 | 103,974 | 14,046,568 | +41.71 | 9 | 8 | -1.30 | +4.86 |
| AUD_USD | 551 | 111,202 | 75,148 | -67.39 | 8 | 7 | -1.28 | +4.20 |
| USD_CAD | 584 | 137,031 | 186,190 | -63.55 | 10 | 9 | -1.29 | +2.62 |
| USD_CHF | 542 | 99,701 | 91,404 | -28.69 | 10 | 9 | -1.29 | +4.21 |
| NZD_USD | 391 | 87,860 | 53,902 | -53.68 | 9 | 6 | -1.29 | +2.96 |

## Entry-session clustering

| UTC hour | trades |
|---:|---:|
| 01:00 | 603 |
| 02:00 | 377 |
| 05:00 | 480 |
| 06:00 | 229 |
| 09:00 | 520 |
| 10:00 | 265 |
| 13:00 | 604 |
| 14:00 | 338 |
| 17:00 | 221 |
| 18:00 | 89 |

| session bucket | trades |
|---|---:|
| asian | 1460 |
| london | 1014 |
| london_ny_overlap | 942 |
| ny | 310 |

## Exit reason distribution

| reason | trades |
|---|---:|
| eod | 13 |
| stop | 760 |
| time | 2953 |

## Risk-engine rejection totals (mode=backtest)

| code | count |
|---|---:|
| SESSION_BLOCKED | 758 |
| SPREAD_TOO_WIDE | 2013 |

## Concurrency

- Max concurrent open positions per instrument: 1 (structurally enforced by BacktestEngine + R2 rule).
- Max open positions (config gate): 1.
- Max correlated positions (config gate): 1.

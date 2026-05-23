# CAMPAIGN_010 — Portfolio-Risk Diagnostics (auto-generated)

> Diagnostic only — does not gate the verdict. Phase 4 verdict
> remains REJECT regardless. configs/approved_strategies.yaml
> remains approved: [].

## Per-pair exposure

| pair | trades | total units | total notional (quote ccy) | total PnL (USD) | max loss streak | max win streak | largest single loss | largest single win |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EUR_USD | 310 | 68,083 | 73,732 | -31.07 | 8 | 4 | -1.28 | +3.09 |
| GBP_USD | 565 | 98,223 | 125,162 | -30.57 | 10 | 8 | -1.28 | +4.20 |
| USD_JPY | 492 | 97,166 | 13,913,539 | -26.81 | 9 | 9 | -1.29 | +3.49 |
| AUD_USD | 511 | 125,636 | 83,478 | -48.14 | 8 | 11 | -1.29 | +2.96 |
| USD_CAD | 434 | 114,900 | 155,389 | -46.32 | 8 | 6 | -1.28 | +3.33 |
| USD_CHF | 432 | 90,675 | 81,024 | +8.45 | 9 | 8 | -1.30 | +5.35 |
| NZD_USD | 47 | 8,361 | 5,124 | -8.33 | 4 | 4 | -1.27 | +1.35 |

## Entry-session clustering

| UTC hour | trades |
|---:|---:|
| 06:00 | 1030 |
| 09:00 | 1761 |

| session bucket | trades |
|---|---:|
| london | 2791 |

## Exit reason distribution

| reason | trades |
|---|---:|
| eod | 23 |
| stop | 661 |
| time | 2107 |

## Risk-engine rejection totals (mode=backtest)

| code | count |
|---|---:|
| SPREAD_TOO_WIDE | 414 |
| SPREAD_TO_ATR | 770 |

## Concurrency

- Max concurrent open positions per instrument: 1 (structurally enforced by BacktestEngine + R2 rule).
- Max open positions (config gate): 1.
- Max correlated positions (config gate): 1.

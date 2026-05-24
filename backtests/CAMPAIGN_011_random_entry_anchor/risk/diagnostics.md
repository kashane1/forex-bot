# CAMPAIGN_011 — Portfolio-Risk Diagnostics (auto-generated)

> Diagnostic only — does not gate the verdict. Phase 4 verdict
> remains REJECT regardless. configs/approved_strategies.yaml
> remains approved: [].

## Per-pair exposure

| pair | trades | total units | total notional (quote ccy) | total PnL (USD) | max loss streak | max win streak | largest single loss | largest single win |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EUR_USD | 119 | 25,726 | 27,762 | -6.10 | 6 | 5 | -1.28 | +2.79 |
| GBP_USD | 196 | 33,639 | 42,927 | +20.95 | 5 | 5 | -1.30 | +2.97 |
| USD_JPY | 174 | 34,384 | 4,911,002 | +1.76 | 8 | 7 | -1.28 | +2.78 |
| AUD_USD | 190 | 47,014 | 31,242 | -8.65 | 6 | 7 | -1.29 | +5.32 |
| USD_CAD | 182 | 52,979 | 71,827 | -2.18 | 9 | 8 | -1.29 | +3.12 |
| USD_CHF | 177 | 39,518 | 35,240 | +4.62 | 4 | 6 | -1.29 | +3.42 |
| NZD_USD | 139 | 37,882 | 22,933 | -13.07 | 5 | 6 | -1.30 | +3.09 |

## Entry-session clustering

| UTC hour | trades |
|---:|---:|
| 01:00 | 173 |
| 02:00 | 88 |
| 05:00 | 182 |
| 06:00 | 80 |
| 09:00 | 195 |
| 10:00 | 77 |
| 13:00 | 169 |
| 14:00 | 91 |
| 17:00 | 84 |
| 18:00 | 38 |

| session bucket | trades |
|---|---:|
| asian | 443 |
| london | 352 |
| london_ny_overlap | 260 |
| ny | 122 |

## Exit reason distribution

| reason | trades |
|---|---:|
| eod | 7 |
| stop | 241 |
| time | 929 |

## Risk-engine rejection totals (mode=backtest)

| code | count |
|---|---:|
| SESSION_BLOCKED | 281 |
| SPREAD_TOO_WIDE | 363 |

## Concurrency

- Max concurrent open positions per instrument: 1 (structurally enforced by BacktestEngine + R2 rule).
- Max open positions (config gate): 1.
- Max correlated positions (config gate): 1.

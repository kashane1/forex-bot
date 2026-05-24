# CAMPAIGN_014 — Portfolio-Risk Diagnostics (auto-generated)

> Diagnostic only — does not gate the verdict. CAMPAIGN_014 is
> research-only; Phase 5 verdict was REJECT. configs/approved_strategies.yaml
> remains approved: [].

## Per-pair exposure

| pair | trades | total units | total notional (quote ccy) | total PnL (USD) | max loss streak | max win streak | largest single loss | largest single win |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EUR_USD | 100 | 21,687 | 23,672 | -25.49 | 7 | 4 | -1.28 | +3.43 |
| GBP_USD | 152 | 24,110 | 30,773 | -16.06 | 9 | 4 | -1.27 | +3.94 |
| USD_JPY | 134 | 25,458 | 3,531,590 | -19.00 | 7 | 3 | -1.27 | +3.77 |
| AUD_USD | 91 | 21,103 | 14,162 | -31.91 | 6 | 3 | -1.27 | +1.38 |
| USD_CAD | 91 | 24,190 | 32,577 | -17.99 | 7 | 6 | -1.28 | +2.00 |
| USD_CHF | 89 | 17,920 | 16,092 | -31.34 | 5 | 3 | -1.27 | +1.88 |
| NZD_USD | 63 | 16,205 | 9,814 | -12.47 | 5 | 4 | -1.29 | +1.05 |

## Entry-session clustering

| UTC hour | trades |
|---:|---:|
| 05:00 | 34 |
| 06:00 | 13 |
| 13:00 | 444 |
| 14:00 | 229 |

| session bucket | trades |
|---|---:|
| asian | 34 |
| london | 13 |
| london_ny_overlap | 673 |

## Exit reason distribution

| reason | trades |
|---|---:|
| eod | 9 |
| stop | 174 |
| time | 537 |

## Risk-engine rejection totals (mode=backtest)

| code | count |
|---|---:|
| SESSION_BLOCKED | 409 |
| SPREAD_TOO_WIDE | 196 |

## Concurrency

- BacktestEngine is single-instrument single-position-at-a-time.
- The CAMPAIGN_014 runner invokes one engine PER PAIR PER FOLD; `MAX_OPEN_POSITIONS_EXCEEDED` rejections observed: 0.
- Max open positions (config gate): 1 (within-pair only).
- Max correlated positions (config gate): 1 (within-pair only).

## CAMPAIGN_014 calendar-event-window-specific

### Entry-window concentration (R3 binding)

- Trades at bars_since_event == 1 (trigger bar): **720 / 720 = 100.0%**
- R3 binding requires trigger bar to be the FIRST post-event bar; the strategy emits zero trades at offsets ≥ 2.
- Unattributed trades (no event maps to entry bar - 1): **0**
  (zero unattributed expected since R3 fires only on confirmed event bars)

### Per-event-class PnL distribution

| event class | impacted pairs | trades | total PnL (USD) | mean PnL (USD) | median PnL (USD) | long | short | long share |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| NFP | all 7 | 571 | -151.17 | -0.2647 | -0.2665 | 284 | 287 | 49.7% |
| FOMC | all 7 | 0 | +0.00 | +0.0000 | +0.0000 | 0 | 0 | 0.0% |
| ECB | EUR_USD | 41 | +2.56 | +0.0624 | -0.1029 | 18 | 23 | 43.9% |
| BoJ | USD_JPY | 47 | -9.07 | -0.1930 | -0.2897 | 16 | 31 | 34.0% |
| BoE | GBP_USD | 61 | +3.42 | +0.0561 | -0.3448 | 35 | 26 | 57.4% |

### Per-event-class × per-pair sensitivity heatmap

Cells show (trades, total_pnl_usd). `—` = pair not impacted by event class.

| event class | EUR_USD | GBP_USD | USD_JPY | AUD_USD | USD_CAD | USD_CHF | NZD_USD |
|---|---|---|---|---|---|---|---|
| NFP | (59, -28.05) | (91, -19.48) | (87, -9.93) | (91, -31.91) | (91, -17.99) | (89, -31.34) | (63, -12.47) |
| FOMC | (0, +0.00) | (0, +0.00) | (0, +0.00) | (0, +0.00) | (0, +0.00) | (0, +0.00) | (0, +0.00) |
| ECB | (41, +2.56) | — | — | — | — | — | — |
| BoJ | — | — | (47, -9.07) | — | — | — | — |
| BoE | — | (61, +3.42) | — | — | — | — | — |

### NFP / FOMC concurrent-firing (out of 7 impacted pairs per event)

Each NFP / FOMC event impacts all 7 USD pairs. How many distinct pairs actually fired entries on each event?

| pairs fired | event count |
|---:|---:|
| 4 | 2 |
| 5 | 3 |
| 6 | 24 |
| 7 | 23 |

### Per-fold event-fixture coverage (R4 binding)

| fold | test window | fixture_coverage_end_utc | covered |
|---|---|---|:---:|
| 0 | 2021-12-21 → 2022-06-18 | 2026-05-20T23:59:59+00:00 | ✓ |
| 1 | 2022-06-19 → 2022-12-15 | 2026-05-20T23:59:59+00:00 | ✓ |
| 2 | 2022-12-16 → 2023-06-13 | 2026-05-20T23:59:59+00:00 | ✓ |
| 3 | 2023-06-14 → 2023-12-10 | 2026-05-20T23:59:59+00:00 | ✓ |
| 4 | 2023-12-11 → 2024-06-07 | 2026-05-20T23:59:59+00:00 | ✓ |
| 5 | 2024-06-08 → 2024-12-04 | 2026-05-20T23:59:59+00:00 | ✓ |
| 6 | 2024-12-05 → 2025-06-02 | 2026-05-20T23:59:59+00:00 | ✓ |
| 7 | 2025-06-03 → 2025-11-29 | 2026-05-20T23:59:59+00:00 | ✓ |

## Drawdown clustering (per-fold median pair max drawdown)

| fold | test window | median pair max drawdown % |
|---|---|---:|
| 0 | 2021-12-21 → 2022-06-18 | -0.72% |
| 1 | 2022-06-19 → 2022-12-15 | -0.85% |
| 2 | 2022-12-16 → 2023-06-13 | -1.05% |
| 3 | 2023-06-14 → 2023-12-10 | -0.66% |
| 4 | 2023-12-11 → 2024-06-07 | -0.73% |
| 5 | 2024-06-08 → 2024-12-04 | -1.06% |
| 6 | 2024-12-05 → 2025-06-02 | -0.88% |
| 7 | 2025-06-03 → 2025-11-29 | -1.07% |

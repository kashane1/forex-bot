# CAMPAIGN_013 — Portfolio-Risk Diagnostics (auto-generated)

> Diagnostic only — does not gate the verdict. CAMPAIGN_013 is
> research-only; even a clean diagnostics pass produces
> RESEARCH_PASS_UNAPPROVED at best. configs/approved_strategies.yaml
> remains approved: [].

## Per-pair exposure

| pair | trades | total units | total notional (quote ccy) | total PnL (USD) | max loss streak | max win streak | largest single loss | largest single win |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EUR_USD | 1412 | 337,260 | 368,841 | -84.66 | 7 | 7 | -1.28 | +4.39 |
| GBP_USD | 648 | 97,696 | 124,198 | -48.94 | 7 | 8 | -1.27 | +4.57 |
| USD_JPY | 310 | 54,397 | 8,290,363 | +2.27 | 12 | 7 | -1.26 | +5.89 |
| AUD_USD | 1942 | 458,364 | 305,252 | -101.32 | 9 | 8 | -1.29 | +3.71 |
| USD_CAD | 958 | 308,793 | 423,438 | -52.01 | 9 | 7 | -1.29 | +4.30 |
| USD_CHF | 807 | 183,884 | 166,467 | -73.33 | 14 | 6 | -1.30 | +8.16 |
| NZD_USD | 1863 | 481,332 | 295,179 | -208.82 | 9 | 7 | -1.30 | +3.34 |

## Entry-session clustering

| UTC hour | trades |
|---:|---:|
| 01:00 | 1150 |
| 02:00 | 796 |
| 05:00 | 832 |
| 06:00 | 427 |
| 09:00 | 1563 |
| 10:00 | 612 |
| 13:00 | 1591 |
| 14:00 | 752 |
| 17:00 | 168 |
| 18:00 | 49 |

| session bucket | trades |
|---|---:|
| asian | 2778 |
| london | 2602 |
| london_ny_overlap | 2343 |
| ny | 217 |

## Exit reason distribution

| reason | trades |
|---|---:|
| eod | 23 |
| stop | 1830 |
| time | 6087 |

## Risk-engine rejection totals (mode=backtest)

| code | count |
|---|---:|
| DRAWDOWN_LIMIT | 1507 |
| SESSION_BLOCKED | 992 |
| SPREAD_TOO_WIDE | 3024 |

## Concurrency

- BacktestEngine is single-instrument single-position-at-a-time.
- The CAMPAIGN_013 runner invokes one engine PER PAIR PER FOLD; `MAX_OPEN_POSITIONS_EXCEEDED` rejections observed: 0.
- Max open positions (config gate): 1 (within-pair only).
- Max correlated positions (config gate): 1 (within-pair only).

## Cross-pair-specific diagnostics

### Zero-trade pair-fold cells

- Count: **29 / 56** (51.8 %)
- The cross-pair rank-gap rule `|rank(quote) − rank(base)| ≥ 4` is selective: more than half of (pair × fold) cells produce zero trades because the gap is not exceeded for that pair in that fold's window.

### Per-fold long/short imbalance

| fold | long | short | total | long share |
|---|---:|---:|---:|---:|
| fold_00 | 509 | 285 | 794 | 64.1% |
| fold_01 | 0 | 321 | 321 | 0.0% |
| fold_02 | 1166 | 0 | 1166 | 100.0% |
| fold_03 | 207 | 603 | 810 | 25.6% |
| fold_04 | 322 | 933 | 1255 | 25.7% |
| fold_05 | 321 | 931 | 1252 | 25.6% |
| fold_06 | 524 | 625 | 1149 | 45.6% |
| fold_07 | 878 | 315 | 1193 | 73.6% |

### Per-fold simultaneous-signal frequency

A 'simultaneous signal' is a single H4 bar where the strategy fires entries on ≥ 2 pairs at the same timestamp.

| fold | bars with any signal | bars with sim. signal (≥ 2 pairs) | sim. share |
|---|---:|---:|---:|
| fold_00 | 591 | 176 | 29.8% |
| fold_01 | 321 | 0 | 0.0% |
| fold_02 | 712 | 313 | 44.0% |
| fold_03 | 591 | 195 | 33.0% |
| fold_04 | 752 | 327 | 43.5% |
| fold_05 | 729 | 341 | 46.8% |
| fold_06 | 757 | 299 | 39.5% |
| fold_07 | 720 | 333 | 46.2% |

### Per-fold cross-pair runner contract status

| fold | contract_satisfied | common_index_length (H4 bars) |
|---|:---:|---:|
| fold_00 | ✓ | 1,841 |
| fold_01 | ✓ | 1,848 |
| fold_02 | ✓ | 1,837 |
| fold_03 | ✓ | 1,830 |
| fold_04 | ✓ | 1,835 |
| fold_05 | ✓ | 1,836 |
| fold_06 | ✓ | 1,825 |
| fold_07 | ✓ | 1,829 |

All 8 folds satisfied the cross-pair runner integration contract; no fold was BLOCKED. The REJECT verdict comes from inherited gates alone.

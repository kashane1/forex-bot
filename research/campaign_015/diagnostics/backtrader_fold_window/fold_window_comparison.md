# Backtrader Fold-Window vs Bespoke Rehydrate — CAMPAIGN_015

> `strategy_evidence: false`. Does **not** approve any strategy.

- Generated at: `2026-05-26T03:18:39+00:00`
- Backtrader fold-window trades: **532**
- Bespoke rehydrate trades: **164**
- Delta: **+368**
- Prior full-window BT trades: **575** (classification `TIMESTAMP_MISMATCH`)
- **Classification: `SIGNAL_RULE_MISMATCH`**

## Per-fold totals

| fold | BT | bespoke | Δ |
|---:|---:|---:|---:|
| 0 | 57 | 18 | +39 |
| 1 | 65 | 26 | +39 |
| 2 | 70 | 26 | +44 |
| 3 | 69 | 28 | +41 |
| 4 | 66 | 24 | +42 |
| 5 | 61 | 14 | +47 |
| 6 | 65 | 14 | +51 |
| 7 | 79 | 14 | +65 |

## Per-pair totals

| pair | BT | bespoke | Δ |
|---|---:|---:|---:|
| AUD_USD | 101 | 24 | +77 |
| EUR_USD | 79 | 27 | +52 |
| GBP_USD | 95 | 41 | +54 |
| NZD_USD | 53 | 5 | +48 |
| USD_CAD | 81 | 23 | +58 |
| USD_CHF | 70 | 27 | +43 |
| USD_JPY | 53 | 17 | +36 |

## Side distribution

- BT: `{'short': 256, 'long': 276}`
- bespoke: `{'long': 85, 'short': 79}`

## Notes

- full-window BT had 575 trades vs fold-window 532; gap vs bespoke 164 shrank by 43 from full-window excess
- TIMESTAMP_MISMATCH resolved (window coverage aligned); residual trade-count drift likely SIGNAL_RULE_MISMATCH or FILL_TIMING_MISMATCH

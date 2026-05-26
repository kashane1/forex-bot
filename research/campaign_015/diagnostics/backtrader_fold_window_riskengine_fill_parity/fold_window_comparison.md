# Backtrader Fold-Window vs Bespoke Rehydrate — CAMPAIGN_015

> `strategy_evidence: false`. Does **not** approve any strategy.

- Generated at: `2026-05-26T04:43:49+00:00`
- Backtrader fold-window trades: **416**
- Bespoke rehydrate trades: **164**
- Delta: **+252**
- Prior full-window BT trades: **532** (classification `SIGNAL_RULE_MISMATCH`)
- **Classification: `SIGNAL_RULE_MISMATCH`**

## Per-fold totals

| fold | BT | bespoke | Δ |
|---:|---:|---:|---:|
| 0 | 44 | 18 | +26 |
| 1 | 54 | 26 | +28 |
| 2 | 57 | 26 | +31 |
| 3 | 61 | 28 | +33 |
| 4 | 54 | 24 | +30 |
| 5 | 42 | 14 | +28 |
| 6 | 52 | 14 | +38 |
| 7 | 52 | 14 | +38 |

## Per-pair totals

| pair | BT | bespoke | Δ |
|---|---:|---:|---:|
| AUD_USD | 88 | 24 | +64 |
| EUR_USD | 46 | 27 | +19 |
| GBP_USD | 83 | 41 | +42 |
| NZD_USD | 46 | 5 | +41 |
| USD_CAD | 59 | 23 | +36 |
| USD_CHF | 52 | 27 | +25 |
| USD_JPY | 42 | 17 | +25 |

## Side distribution

- BT: `{'short': 192, 'long': 224}`
- bespoke: `{'long': 85, 'short': 79}`

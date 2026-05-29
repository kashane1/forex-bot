# CAMPAIGN_029 — USD_JPY 10-pip range-bar preflight diagnostics

> Bar-stream characterisation only. **No signals, trades, or P&L.** Source: local Postgres M1. Full generated bars are local & gitignored.

- instrument: **USD_JPY** · threshold: **10 pip** · price basis: **mid**
- window: 2021-05-27T00:00:00+00:00 → 2026-05-26T23:59:00+00:00 (max_rows=None)
- M1 rows consumed: **1,844,454**
- range bars: **72,940 completed** (+1 incomplete final)
- first bar open: 2021-05-27T00:00:00+00:00
- last bar close: 2026-05-26T23:59:00+00:00
- M1 rows / bar: mean 25.2869, median 11, max 1363
- elapsed sec / bar: median 600.0, p99 17520.0, max 266040.0 (gap-spanning >1d: 261)
- multi-threshold crossing: 3167 (rate 0.043419)
- overshoot pips: mean 2.7208, p99 24.7, max 265.0
- session dist (UTC): {'tokyo': 21001, 'london': 15862, 'london_ny_overlap': 21363, 'new_york': 9937, 'pacific': 4778}
- weekday dist: {'Mon': 12597, 'Tue': 13545, 'Wed': 15128, 'Thu': 15326, 'Fri': 14904, 'Sat': 0, 'Sun': 1441}
- completion reasons: {'range_down': 36081, 'range_up': 36859, 'incomplete': 1}
- **lookahead violations: 0**


# M1 Derived H4 Drift Comparison Result

**Overall status:** WARN (non-blocking)
**Reference:** Native OANDA practice H4 rows already in `market_data.candles`
**Comparison:** M1-derived H4 (`aggregate_m1_candles`, NY 17:00 alignment) vs native H4 on overlapping timestamps

## Summary

| Pair | Overlap | Exact OHLC match | OHLC mismatch | Native-only H4 | Derived-only H4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| EUR_USD | 5,225 | 5,225 | **0** | 2,545 | 9 |
| GBP_USD | 5,177 | 5,177 | **0** | 2,593 | 9 |
| USD_JPY | 5,439 | 5,439 | **0** | 2,331 | 9 |
| AUD_USD | 4,357 | 4,357 | **0** | 3,413 | 5 |
| USD_CAD | 5,008 | 5,008 | **0** | 2,762 | 7 |
| USD_CHF | 4,034 | 4,034 | **0** | 3,736 | 5 |
| NZD_USD | 4,193 | 4,193 | **0** | 3,581 | 6 |

On every overlapping bar, bid/ask OHLC matches within tolerance. Volume differences were not material.

## Likely Causes of Native-only Bars

- **missing_minute_coverage:** M1-derived H4 omits incomplete 240-minute blocks; native H4 may exist where M1 gaps exist.
- Not timestamp convention drift on overlap (0 OHLC mismatches).

## C021 Impact

- Prior H4-native campaigns remain valid on their native series.
- Future M1/M15 campaigns should use M1-derived HTF for internal consistency.
- Drift does **not** block CAMPAIGN_021 **scaffold**; it documents series divergence for evidence design.

**Artifacts:** `h4_drift_summary.json`, `h4_drift_by_pair.csv`

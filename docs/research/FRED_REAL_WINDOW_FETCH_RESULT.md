# FRED Real-Window Fetch Result

**Diagnostic only** — `strategy_evidence: false`

## Run summary

| field | value |
|---|---|
| Date | 2026-05-26 |
| `FRED_API_KEY` present | **yes** (not printed) |
| Overall status | `OK` |
| Observation start | 2018-01-01 |
| Observation end | 2026-05-24 |
| H4 research window | 2020-01-01 22:00 UTC → 2026-05-24 21:00 UTC |

## Attempted series

| feature_id | FRED ID | required | result | rows |
|---|---|---|---|---:|
| broad_usd_index | DTWEXBGS | yes | **ok** | 2,094 |
| us_2y_yield | DGS2 | yes | **ok** | 2,098 |
| us_10y_yield | DGS10 | yes | **ok** | 2,098 |
| vix | VIXCLS | yes | **ok** | 2,138 |
| sp500 | SP500 | yes | **ok** | 2,109 |
| oil_wti | DCOILWTICO | yes | **ok** | 2,093 |
| nasdaq_composite | NASDAQCOM | optional | **ok** | 2,110 |

All required series complete. No failures.

## Output files

- `research/cross_asset_features/fred_fetch_status_real_window.json`
- `research/cross_asset_features/normalized_features.csv`
- `research/cross_asset_features/normalized_features_manifest.json`
- `research/cross_asset_features/feature_quality_report.json`

## Missing rates (normalized daily frame, 2,148 rows)

| feature | missing count | missing rate % |
|---|---:|---:|
| broad_usd_index | 54 | 2.51 |
| us_2y_yield | 50 | 2.33 |
| us_10y_yield | 50 | 2.33 |
| vix | 10 | 0.47 |
| sp500 | 39 | 1.82 |
| oil_wti | 55 | 2.56 |
| nasdaq_composite | 38 | 1.77 |

Missing rows reflect weekends/holidays and FRED publication gaps — expected for daily series.

## Disclaimer

No strategy evidence. No win-rate or expectancy claims.

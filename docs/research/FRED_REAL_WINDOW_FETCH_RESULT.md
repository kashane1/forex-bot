# FRED Real-Window Fetch Result

**Diagnostic only** — `strategy_evidence: false`

## Run summary

| field | value |
|---|---|
| Date | 2026-05-26 |
| `FRED_API_KEY` present | **no** (not printed) |
| Overall status | `BLOCKED_AUTH_OR_LOCAL_CSV_REQUIRED` |
| Observation start | 2018-01-01 |
| Observation end | 2026-05-24 |
| H4 research window | 2020-01-01 22:00 UTC → 2026-05-24 21:00 UTC |

## Attempted series

| feature_id | FRED ID | required | result |
|---|---|---|---|
| broad_usd_index | DTWEXBGS | yes | **not fetched** — auth blocked |
| us_2y_yield | DGS2 | yes | **not fetched** |
| us_10y_yield | DGS10 | yes | **not fetched** |
| vix | VIXCLS | yes | **not fetched** |
| sp500 | SP500 | yes | **not fetched** |
| oil_wti | DCOILWTICO | yes | **not fetched** |
| nasdaq_composite | NASDAQCOM | optional | **not fetched** |

## Output files

- `research/cross_asset_features/fred_fetch_status_real_window.json`
- `research/cross_asset_features/fred_fetch_blocked_report.json`

## Missing rates / rows

Not applicable — live fetch did not execute.

## Remediation

See [`EXTERNAL_DATA_INGEST_STILL_BLOCKED.md`](EXTERNAL_DATA_INGEST_STILL_BLOCKED.md).

## Disclaimer

No strategy evidence. No win-rate or expectancy claims.

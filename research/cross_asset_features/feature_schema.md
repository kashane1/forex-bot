# Cross-Asset Feature CSV Schema

**Diagnostic only** — `strategy_evidence: false`

Place operator-local files under `data/external_features/` (gitignored). Fixtures live in `tests/fixtures/cross_asset/`.

## Canonical normalized format (preferred)

Long or wide CSV with columns:

| column | required | description |
|---|---|---|
| `date` | yes | Observation calendar date (UTC) |
| `value` | yes | Feature level |
| `source` | optional | `fred_api`, `local_csv`, `derived` |
| `as_of_date` | optional | Source as-of date if different from `date` |
| `release_date` | optional | Publication/release date when known |
| `ingestion_time` | optional | UTC timestamp when row was ingested |
| `quality_flags` | optional | Comma-separated flags e.g. `stale,interpolated` |

Wide-format multi-feature files are also accepted by the normalizer when documented in the manifest.

## Legacy per-feature files

| file | columns | maps to |
|---|---|---|
| `dxy.csv` / `broad_usd_index.csv` | `date`, `close` / `value` | `broad_usd_index` |
| `us2y.csv` / `us_2y_yield.csv` | `date`, `yield` / `value` | `us_2y_yield` |
| `us10y.csv` / `us_10y_yield.csv` | `date`, `yield` / `value` | `us_10y_yield` |
| `vix.csv` | `date`, `close` / `value` | `vix` |
| `sp500.csv` | `date`, `close` / `value` | `sp500` |
| `oil.csv` / `oil_wti.csv` | `date`, `close` / `value` | `oil_wti` |
| `nasdaq.csv` / `nasdaq_composite.csv` | `date`, `close` / `value` | `nasdaq_composite` |
| `gold.csv` | `date`, `close` / `value` | `gold` |
| `cot_eur_net.csv` | `report_date`, `net_position` / `value` | `cot_eur_net` |

Frequency: daily except `cot_eur_net` (weekly).

## Alignment rule

Forward-fill onto H4 timestamps using **availability time**, not raw observation date alone:

- Daily close dated `D` → available at `D + 1 day 00:00 UTC`.
- H4 bar at `T` uses latest observation with `availability_ts <= T`.
- No backfill from future data.

## Registry

Machine-readable definitions: `research/cross_asset_features/source_registry.json`.

# Cross-Asset Feature CSV Schema

**Diagnostic only** — `strategy_evidence: false`

Place operator-local files under `data/external_features/` (gitignored). Fixtures live in `tests/fixtures/cross_asset/`.

| file | columns | frequency |
|---|---|---|
| `dxy.csv` | `date`, `close` | daily |
| `us2y.csv` | `date`, `yield` | daily |
| `us10y.csv` | `date`, `yield` | daily |
| `vix.csv` | `date`, `close` | daily |
| `sp500.csv` | `date`, `close` | daily |
| `nasdaq.csv` | `date`, `close` | daily |
| `gold.csv` | `date`, `close` | daily |
| `oil.csv` | `date`, `close` | daily |
| `cot_eur_net.csv` | `report_date`, `net_position` | weekly |

## Alignment rule

Forward-fill onto H4 timestamps: latest observation with `timestamp <= bar_time`. No backfill from future data.

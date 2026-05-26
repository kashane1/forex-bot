# External Feature Local CSV Template

**Diagnostic only** — `strategy_evidence: false`

Use this template when FRED is unavailable or a series needs manual supplementation.

## Drop location

```
data/external_features/   (gitignored — never commit)
```

## Required files (minimum for confluence core)

| file | columns | maps to |
|---|---|---|
| `broad_usd_index.csv` or `dxy.csv` | `date`, `value` or `close` | `broad_usd_index` |
| `us_2y_yield.csv` or `us2y.csv` | `date`, `value` or `yield` | `us_2y_yield` |
| `us_10y_yield.csv` or `us10y.csv` | `date`, `value` or `yield` | `us_10y_yield` |
| `vix.csv` | `date`, `value` or `close` | `vix` |
| `sp500.csv` | `date`, `value` or `close` | `sp500` |
| `oil_wti.csv` or `oil.csv` | `date`, `value` or `close` | `oil_wti` |

## Date range requirement

Cover **2018-01-01 through latest H4 bar** (currently ~2026-05-24) to eliminate early `cross_asset_missing` in confluence diagnostics.

## Example row format

```csv
date,value
2018-01-02,95.4
2018-01-03,95.6
```

## Validation rules (enforced by loader)

- Monotonic dates (duplicates deduped with `keep_last`)
- No future-dated rows relative to observation end
- Required timestamp and value columns

## Gold

No FRED series in registry. Use `gold.csv` with `date,close` only if you have a licensed source. Otherwise status remains `MANUAL_CSV_REQUIRED`.

## After dropping files

```bash
python scripts/run_external_data_full_window_pipeline.py
python scripts/align_cross_asset_features_to_h4.py
```

Check `research/cross_asset_features/local_csv_fallback_status.json` for scan results.

## Do not commit

Never commit `data/external_features/` contents, `.env`, or API keys.

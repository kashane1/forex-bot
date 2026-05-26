# Cross-Asset FRED Ingest Runbook

**Diagnostic only** — `strategy_evidence: false`

## Prerequisites

- Python env with project dependencies (`httpx`, `pandas`, `python-dotenv`).
- Free FRED API key from https://fred.stlouisfed.org/docs/api/api_key.html

## Set FRED_API_KEY locally

```bash
export FRED_API_KEY='your-key-here'   # never commit this
# or add to local .env (gitignored)
```

Never print or commit the key. The fetcher reads env / `.env` only.

## Fetch FRED series

```bash
python scripts/fetch_cross_asset_fred_features.py \
  --observation-start 2019-01-01
```

Outputs:

| path | commit? |
|---|---|
| `data/external_features/.fred_cache/*.json` | **no** (gitignored) |
| `research/cross_asset_features/normalized_features.csv` | yes if compact |
| `research/cross_asset_features/normalized_features_manifest.json` | yes |
| `research/cross_asset_features/feature_quality_report.json` | yes |
| `research/cross_asset_features/fred_fetch_blocked_report.json` | yes when blocked |

If `FRED_API_KEY` is missing, the script exits with code 2 and writes `fred_fetch_blocked_report.json` with status `BLOCKED_AUTH_OR_LOCAL_CSV_REQUIRED`.

## Local CSV fallback

Place files in `data/external_features/` (gitignored) using schema in `research/cross_asset_features/feature_schema.md`.

Legacy filenames (`dxy.csv`, `us2y.csv`, …) are accepted.

Then normalize without FRED:

```bash
python -c "
from pathlib import Path
from research.cross_asset_features.normalizer import write_normalized_outputs
write_normalized_outputs(Path('.'), Path('research/cross_asset_features'))
"
```

## Align to H4

Requires local H4 SQLite store (`data/campaign_002.sqlite3` or env override):

```bash
python scripts/align_cross_asset_features_to_h4.py
```

## Troubleshooting

| symptom | action |
|---|---|
| `BLOCKED_AUTH_OR_LOCAL_CSV_REQUIRED` | Set `FRED_API_KEY` or drop local CSVs |
| Empty normalized CSV | Check cache dir / local CSV paths |
| Low H4 coverage early in sample | FRED series must start before first H4 bar |
| `cross_asset_missing` still high | Fixture date range too short; fetch full-window FRED data |

## Safe vs unsafe to commit

**Safe:** manifests, quality reports, compact normalized CSVs, blocked reports, docs.  
**Unsafe:** `.env`, raw FRED cache, SQLite DBs, bulky downloads.

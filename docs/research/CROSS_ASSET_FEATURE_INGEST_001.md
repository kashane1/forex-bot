# Cross-Asset Feature Ingest — Sprint 001

**Branch:** `infra-multi-timeframe-confluence-and-cost-atlas-001`  
**Status:** Scaffolding only — not tradable, not approved.

## Implemented

- CSV schema: `research/cross_asset_features/feature_schema.md`
- Loader: `research/cross_asset_features/loader.py`
- Fixtures: `tests/fixtures/cross_asset/`
- Availability report: `research/cross_asset_features/feature_availability_report.json`

## Data paths

| path | purpose |
|---|---|
| `data/external_features/` | Operator-local real CSVs (gitignored) |
| `tests/fixtures/cross_asset/` | Committed tiny fixtures for tests |

## Status

If `data/external_features/` is empty, status is **FIXTURE_ONLY** or **BLOCKED_LOCAL_DATA_REQUIRED**. Real FRED/CFTC ingest is a future sprint (`infra-cross-asset-real-data-ingest-001`).

## Rules

- No paid APIs, no broker order APIs, no API keys committed.
- Features are filters for confluence — not trade triggers.

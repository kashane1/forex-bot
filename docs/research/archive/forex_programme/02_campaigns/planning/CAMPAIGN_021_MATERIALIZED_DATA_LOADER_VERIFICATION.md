# CAMPAIGN_021 Materialized Data Loader Verification

**Date:** 2026-05-28  
**Branch:** `research-campaign-021-ltf-mtf-confluence-execution-001`

## Loader path (`campaign_021_loader.py`)

| requirement | implementation |
|---|---|
| M15 from materialized Postgres | `_load_materialized_granularity(..., "M15", "M15")` |
| H1 from materialized Postgres | `_load_materialized_granularity(..., "H1", "H1")` |
| H4 from materialized H4M1 | `_load_materialized_granularity(..., STORAGE_GRANULARITY["H4"], "H4")` |
| D1AGG from native H4 only | `_load_native_h4` with `exclude_sources=(m1_materialized,)` → `aggregate_h4_to_d1` |
| No M1 streaming in normal path | `m1_row_count=0` when materialized coverage PASS |
| Missing coverage fails clearly | `SystemExit` with materialization script hint |
| Live fallback debug-only | requires `FOREX_BOT_ALLOW_LIVE_M1_AGGREGATION=1` |

## Runner guards (`run_campaign_021_ltf_mtf_confluence.py`)

- `load_ctx()` raises if live aggregation env is set
- `--preflight-only` checks materialized coverage per pair on train window
- `--data-feature-preflight` reports `m1_rows_loaded: 0` for all 7 pairs (observed 2026-05-28)

## Tests

- `tests/unit/test_m1_timeframe_materialization.py` — coverage fail, upsert preserve native H4
- `tests/unit/test_campaign_021_loader_materialized.py` — missing coverage, native H4 for D1AGG, live env required for fallback
- `tests/unit/test_campaign_021_runner_guards.py` — gate discipline, registry empty

## Observed preflight

```
materialized_source: m1_materialized
m1_rows_loaded: 0 (all pairs)
d1agg_source: native_h4_derived_d1agg
m1_derived_d1agg_used: false
```

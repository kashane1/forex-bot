# M1 Derived Timeframe Materialization 001 Plan

**Date:** 2026-05-27  
**Branch:** `infra-m1-derived-timeframe-materialization-001`  
**Base:** `main` @ `dc8e0cb` or later

## Purpose

Persist M1-derived M5/M15/H1/H4 candles in Postgres so research campaigns (starting with CAMPAIGN_021) query pre-aggregated bars instead of streaming and re-aggregating ~500k+ M1 rows per pair/split on every run.

## Non-goals

- No CAMPAIGN_021 train/validation/test evidence
- No strategy rule or parameter changes
- No M1-derived D1AGG materialization
- No approval registry changes
- No paper/demo/live enablement
- No OANDA mutation APIs

## Materialization scope

| Target | Source | Postgres `source` label | Notes |
|--------|--------|-------------------------|-------|
| M5 | M1 | `m1_materialized` | New rows only |
| M15 | M1 | `m1_materialized` | C021 execution TF |
| H1 | M1 | `m1_materialized` | C021 context |
| H4 | M1 | `m1_materialized` | C021 context; **does not overwrite** existing `oanda-practice` H4 |
| D1AGG | — | — | Remains native H4 → D1AGG at campaign time |

Aggregation: `aggregate_m1_candles(..., missing_policy="omit")` — identical to on-the-fly path.

## H4 coexistence

Postgres PK is `(instrument, granularity, time_utc)`. Native OANDA H4 and M1-derived H4 share granularity `H4`. Materialization upserts use `ON CONFLICT … UPDATE` **only when existing `source = m1_materialized`**, preserving native H4 rows for D1AGG. Campaign loaders filter by `source` / `exclude_sources`.

## Artifacts

| path | content |
|------|---------|
| `src/forex_bot/data/m1_timeframe_materialization.py` | Core pipeline |
| `scripts/materialize_m1_derived_timeframes.py` | CLI |
| `research/m1_timeframe_materialization/` | Run manifests, coverage, verification JSON |
| `docs/research/M1_DERIVED_TIMEFRAME_MATERIALIZATION_RESULT.md` | Verification outcome |

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/materialize_m1_derived_timeframes.py --verify-only --all-majors
python scripts/run_campaign_021_ltf_mtf_confluence.py --preflight-only
python scripts/run_campaign_021_ltf_mtf_confluence.py --data-feature-preflight
```

## No approval

`configs/approved_strategies.yaml` remains `approved: []`.

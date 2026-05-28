# M1 Derived Timeframe Materialization 001 Summary

**Date:** 2026-05-28  
**Branch:** `infra-m1-derived-timeframe-materialization-001`  
**Verdict:** **INFRA_PASS** — materialized LTF lane ready for CAMPAIGN_021 resume

## Commits by phase

| phase | commit | description |
|---|---|---|
| 0 | `d9b3da0` | plan |
| 1 | `35bace8` | materialization module + CLI |
| 2 | `5cfae7f` | full corpus materialize + verification PASS |
| 3 | `bbba239` + `2061357` | loader reads materialized bars; H4M1 mapping |
| 4 | `b613f4e` | registry, summary, coverage verify script |

## What changed

1. **`scripts/materialize_m1_derived_timeframes.py`** — materialize / verify / incremental
2. **`src/forex_bot/data/m1_timeframe_materialization.py`** — core pipeline
3. **`src/forex_bot/research/campaign_021_loader.py`** — query Postgres instead of M1 streaming
4. **`scripts/verify_m1_materialized_coverage.py`** — store coverage check
5. Postgres **`candles`** table populated with `m1_materialized` M5/M15/H1/H4M1

## Verification

All 7 pairs × 4 targets: stored bars **bit-match** on-the-fly `aggregate_m1_candles` path.

## Loader behavior

- Default: read materialized M15/H1/H4M1; native H4 (exclude `m1_materialized`) → D1AGG
- Fallback: `FOREX_BOT_ALLOW_LIVE_M1_AGGREGATION=1` re-aggregates M1 (debug only)
- Missing coverage: fail with message to run materialization script

## CAMPAIGN_021 preflight

- `--preflight-only`: checks materialized coverage on train window
- `--data-feature-preflight`: **~21 s** for 7 pairs (`m1_rows_loaded: 0`; was dominated by per-run M1 aggregation previously)

## Not done (non-goals)

- O(n²) M15 indicator recomputation in backtest engine (separate future work)
- No CAMPAIGN_021 train/validation/test evidence on this branch

## Recommended next step

Merge to `main`, then on `research-campaign-021-ltf-mtf-confluence-execution-001`:

```bash
git merge main
python scripts/run_campaign_021_ltf_mtf_confluence.py train-only
```

## Files to review first

1. `src/forex_bot/data/m1_timeframe_materialization.py`
2. `src/forex_bot/research/campaign_021_loader.py`
3. `research/m1_timeframe_materialization/verification_result.json`
4. `docs/research/M1_DERIVED_TIMEFRAME_MATERIALIZATION_RESULT.md`

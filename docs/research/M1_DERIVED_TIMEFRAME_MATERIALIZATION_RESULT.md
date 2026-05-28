# M1 Derived Timeframe Materialization Result

**Date:** 2026-05-28  
**Branch:** `infra-m1-derived-timeframe-materialization-001`  
**Status:** **PASS**

## Summary

| check | result |
|---|---|
| Targets materialized | M5, M15, H1, H4 (stored as `H4M1`) |
| Pairs | 7 majors |
| Source label | `m1_materialized` |
| Verification vs on-the-fly M1 aggregation | **PASS** (0 OHLC mismatches) |
| Native OANDA H4 preserved | yes (`oanda-practice` rows untouched) |

## H4 storage note

M1-derived H4 is stored as granularity **`H4M1`** to avoid PK conflicts with native `H4` rows used for D1AGG. Campaign loaders map `H4M1` → `H4` frames for strategy context.

## Row counts (verified stored = expected)

| pair | M5 | M15 | H1 | H4 (H4M1) |
|---|---:|---:|---:|---:|
| EUR_USD | 360,972 | 116,628 | 27,249 | 5,234 |
| GBP_USD | 357,741 | 115,243 | 26,758 | 5,186 |
| USD_JPY | 362,519 | 118,035 | 28,013 | 5,448 |
| AUD_USD | 348,717 | 109,904 | 24,774 | 4,362 |
| USD_CAD | 356,992 | 114,562 | 26,405 | 5,015 |
| USD_CHF | 336,541 | 105,604 | 23,400 | 4,039 |
| NZD_USD | 351,408 | 110,462 | 23,856 | 4,199 |

## Loader speed (qualitative)

`--data-feature-preflight` for 7 pairs: **~2 min** (was dominated by per-run M1 aggregation previously).

## Artifacts

- `research/m1_timeframe_materialization/run_manifest.json`
- `research/m1_timeframe_materialization/verification_result.json`
- `research/m1_timeframe_materialization/store_coverage_check.json`

## No approval

`configs/approved_strategies.yaml` remains `approved: []`.

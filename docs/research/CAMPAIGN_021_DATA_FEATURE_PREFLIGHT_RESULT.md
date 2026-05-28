# CAMPAIGN_021 Data/Feature Preflight Result

**Date:** 2026-05-28  
**Branch:** `research-campaign-021-ltf-mtf-confluence-execution-001`  
**Command:** `python scripts/run_campaign_021_ltf_mtf_confluence.py --data-feature-preflight`  
**Runtime:** ~21 s  
**Status:** **PASS**

## Summary

| check | result |
|---|---|
| Pairs | 7/7 |
| Materialized M15/H1/H4M1 | present |
| Native H4 for D1AGG | present |
| M1-derived D1AGG | not used |
| `m1_rows_loaded` | 0 all pairs |
| Lookahead violations | 0 |
| Warmup (M15 ≥ 120) | satisfied all pairs |

## Provenance

- `materialized_source`: `m1_materialized`
- `d1agg_source`: `native_h4_derived_d1agg`

## Artifact

`research/campaign_021/data_feature_preflight.json`

## No approval

Preflight does not approve strategy. `approved_strategies.yaml` remains `approved: []`.

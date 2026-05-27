# CAMPAIGN_021 — Data / Feature Preflight Result

**Date:** 2026-05-27  
**Artifact:** `research/campaign_021/data_feature_preflight.json`  
**Status:** **PASS** — execution not blocked

## Summary

| check | result |
|---|---|
| `preflight_ok` | true |
| `d1agg_source` | `native_h4_derived_d1agg` |
| `m1_derived_d1agg_used` | false |
| `blocked_pairs` | none |
| lookahead violations (sampled) | 0 across all pairs |

## Coverage note (train window 2020-01-01 → 2022-12-31)

M1 corpus begins **2021-05-27**; effective M15/H1/H4 coverage starts then. Precommitted splits unchanged; train metrics apply to available history only.

## Pair-level (train window)

| pair | M15 bars | H1 | H4 | D1AGG | M1 rows loaded |
|---|---:|---:|---:|---:|---:|
| EUR_USD | 36,187 | 8,308 | 1,483 | 779 | 585,876 |
| GBP_USD | 33,954 | 7,479 | 1,269 | 779 | 577,450 |
| USD_JPY | 36,490 | 8,367 | 1,458 | 779 | 586,321 |
| AUD_USD | 31,679 | 6,730 | 1,031 | 779 | 570,033 |
| USD_CAD | 34,340 | 7,556 | 1,240 | 779 | (see JSON) |
| USD_CHF | (see JSON) | | | | |
| NZD_USD | (see JSON) | | | | |

All pairs: `status: PASS`, `lookahead_violations: 0`.

## Feature availability

Warmup requires ~120 M15 bars; all pairs exceed this on available span. HTF alignment samples show rare `htf_blocked_samples` (1–2 per pair) — expected at series edges.

## No approval

`configs/approved_strategies.yaml` remains `approved: []`.

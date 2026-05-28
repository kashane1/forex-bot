# CAMPAIGN_021 Execution After M1 Materialization — Plan

**Date:** 2026-05-28  
**Branch:** `research-campaign-021-ltf-mtf-confluence-execution-001`  
**Base merge commit:** `1c53150` (main @ `85a8932` materialization + C021 scaffold @ `dc8e0cb`)

## Base conditions

| check | status |
|---|---|
| main includes C021 scaffold (≥ dc8e0cb) | yes |
| main includes M1 corpus validation (≥ b0f92e5) | yes |
| main includes M1 materialization infra | yes |
| materialized verification PASS | yes (`research/m1_timeframe_materialization/verification_result.json`) |
| `approved_strategies.yaml` | `approved: []` |
| paper/demo/live | blocked |

## Materialization verification

- 7 majors × M5/M15/H1/H4M1 materialized under `source=m1_materialized`
- 0 OHLC mismatches vs on-the-fly aggregation
- Native OANDA H4 preserved for D1AGG

## Data/feature preflight (2026-05-28)

- `verify_m1_materialized_coverage.py`: **PASS** (7 pairs)
- `--preflight-only`: **PASS** (materialized coverage on train window)
- `--data-feature-preflight`: **PASS** (~21 s, `m1_rows_loaded: 0` all pairs)

## Provenance (binding)

| layer | source |
|---|---|
| M15 execution | materialized M15 (`m1_materialized`) |
| H1 context | materialized H1 |
| H4 context | materialized H4M1 → H4 frame |
| D1AGG | native H4 → `aggregate_h4_to_d1` (exclude `m1_materialized`) |
| M1-derived D1AGG | **blocked** |
| Live M1 aggregation fallback | **forbidden** (`FOREX_BOT_ALLOW_LIVE_M1_AGGREGATION` must be unset) |

## Gate order (non-negotiable)

1. Data/feature preflight  
2. Train only  
3. If train fails → REJECT; no validation, parity, or test  
4. If train passes → validation  
5. If validation fails → REJECT; no parity or test  
6. If validation passes → Backtrader parity  
7. If parity fails → REJECT/BLOCKED_PARITY; no test  
8. If all pass → test lockbox once (still no approval)

## Safety rules

- No parameter tuning after seeing results
- No strategy rule changes
- No OANDA mutation APIs; no live environment
- No raw M1/DB commits
- No approval under any outcome

## Blocked conditions

- `BLOCKED_MATERIALIZED_COVERAGE` — missing materialized rows for requested window
- `BLOCKED_PROVENANCE_AMBIGUITY` — ambiguous or forbidden provenance
- Train gate fail → validation blocked

## No approval

`configs/approved_strategies.yaml` remains `approved: []`.

# CAMPAIGN_021 — Train Result

**Date:** 2026-05-28  
**Command:** `PYTHONUNBUFFERED=1 python scripts/run_campaign_021_ltf_mtf_confluence.py train-only`  
**Re-run:** post-M1 materialization (`m1_materialized` bars; `m1_rows_loaded: 0`)  
**Runtime:** ~40.4 min (2,427 s) for 7 pairs — data load no longer bottleneck

## Split

| field | value |
|---|---|
| window | 2020-01-01 → 2022-12-31 (effective M15 from 2021-05-27) |
| fill_timing | `next_bar_open` |
| cost | base (0.5× spread + 0.2 pip slippage) |
| pairs | 7 majors |

## Aggregate train metrics

| metric | value |
|---|---|
| trade_count | 1,438 |
| expectancy_r | **−0.0174** |
| profit_factor | 0.9642 |
| pairs_positive | 3 / 7 |

## Per-pair expectancy (R)

| pair | trades | expectancy_r | PF |
|---|---:|---:|---:|
| EUR_USD | 170 | −0.184 | 0.71 |
| GBP_USD | 251 | +0.117 | 1.20 |
| USD_JPY | 239 | +0.001 | 1.13 |
| AUD_USD | 203 | −0.001 | 1.00 |
| USD_CAD | 195 | −0.041 | 0.91 |
| USD_CHF | 150 | −0.173 | 0.73 |
| NZD_USD | 230 | +0.047 | 1.07 |

## Train gate

| gate | threshold | result |
|---|---|---|
| train_expectancy_gte_zero | ≥ 0 | **FAIL** (−0.0174) |
| train_trade_count_sanity | ≥ 30 | PASS |
| train_provenance_ok | true | PASS |

**train_gate_pass:** false  
**validation_allowed:** false

## Provenance

- M15/H1/H4: materialized M1-derived Postgres (`source=m1_materialized`; H4 stored as `H4M1`)
- D1AGG: `native_h4_derived_d1agg`
- No M1-derived D1AGG; no live M1 aggregation fallback

## Exit reasons

| reason | trades | share |
|---|---:|---:|
| stop | 819 | 57.0% |
| time | 618 | 43.0% |
| eod | 1 | 0.1% |

## Artifacts

- `research/campaign_021/train_metrics.json`
- `research/campaign_021/train_gate_result.json`
- `research/campaign_021/train_pair_metrics.csv`
- `research/campaign_021/train_exit_reason_summary.csv`
- `research/campaign_021/raw/train/base/*_trades.csv` (gitignored)

## No approval

`configs/approved_strategies.yaml` remains `approved: []`.

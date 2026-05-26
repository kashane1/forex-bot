# CAMPAIGN_011 — Deduped Null Baseline

**Sprint:** CAMPAIGN_011_DEDUPED_NULL_BASELINE_001  
**Canonical JSON:** [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)  
**Status:** NULL MODEL — REJECT expected; metrics are the falsifiability floor for CAMPAIGN_012–014 re-evaluation.

> Old walk-forward doc [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) is **SUPERSEDED** for numeric null-band use.

# CAMPAIGN_011 — Deduped Canonical Null Baseline (rollup)

> **Canonical** for post-dedupe null comparisons. Supersedes
> pre-fix `backtests/CAMPAIGN_011_random_entry_anchor/` metrics.
> **Not a tradable strategy.** `approved: []`. Paper/demo/live blocked.

| field | value |
|---|---|
| strategy | `random_entry_anchor` `0.1.0-c011` |
| master_seed | `20260523` |
| data_source | `oanda-practice` |
| dedupe_policy | `keep_last` |
| config_hash | `6f2c04981a3f02f08bae65b73b09f873de6a42cb067b9462885c5ffd2c6a1206` |
| total_trades | **1180** |
| aggregate expectancy R | **-0.0029** |
| aggregate return % | **-0.6771** |
| profit_factor | **0.8937394430150798** |
| pairs_positive | **3 / 7** |
| fold pass rate | **0 / 8** |
| per-fold exp R mean | **-0.0027144263546915355** |
| per-fold exp R std | **0.04789840054747161** |

## Superseded (pre-fix contaminated null)

| metric | contaminated | deduped canonical |
|---|---:|---:|
| total_trades | 1177 | 1180 |
| aggregate expectancy R | -0.0024 | -0.0029 |

## Per-fold

| fold | trades | exp R | return % |
|---:|---:|---:|---:|
| 0 | 143 | -0.1039 | -4.7942 |
| 1 | 150 | -0.0239 | -0.5901 |
| 2 | 155 | 0.0391 | 4.2692 |
| 3 | 150 | -0.0060 | -0.8457 |
| 4 | 162 | 0.0147 | -0.0845 |
| 5 | 154 | -0.0028 | 0.4892 |
| 6 | 128 | 0.0541 | 0.9370 |
| 7 | 138 | 0.0068 | -0.0579 |

## Per-pair

| pair | trades | exp R | return % |
|---|---:|---:|---:|
| EUR_USD | 121 | -0.0407 | -1.2498 |
| GBP_USD | 196 | 0.0842 | 4.1895 |
| USD_JPY | 174 | 0.0000 | 0.3525 |
| AUD_USD | 191 | -0.0354 | -1.7150 |
| USD_CAD | 182 | -0.0102 | -0.4554 |
| USD_CHF | 177 | 0.0220 | 0.8281 |
| NZD_USD | 139 | -0.0741 | -2.6270 |

## Local-only (not committed)

- `CAMPAIGN_011_random_entry_anchor_deduped/folds/**/**_trades.csv`
- `CAMPAIGN_011_random_entry_anchor_deduped/folds/**/**_summary.json (optional; fold_detail is canonical)`

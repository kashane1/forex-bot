# Edge-discovery study — pair_level_baseline

> Exploratory lab output. Not a strategy verdict; does not approve,
> promote, or change any campaign status. See
> `docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md`.

## Question

Per pair: did any prior campaign cleanly beat the artifact-backed random-entry baseline (CAMPAIGN_005, by-pair) by at least `+0.05` R? If so, was it on the **test window** (test lockbox opened — CAMPAIGN_002 / 003 / 004) or only on the **validation window** (test lockbox never opened — CAMPAIGN_007 / 008 / 009)?

## Per-pair table (expectancy R)

| pair | random R | CAMPAIGN_002_H4_test | CAMPAIGN_003_test | CAMPAIGN_004_test | CAMPAIGN_007_val | CAMPAIGN_008_val | CAMPAIGN_009_val | best gap | best campaign | n above null (test) | n above null (val-only) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EUR_USD | -0.183 | +0.257 | +0.257 | -0.322 | -0.193 | +0.310 | -0.023 | +0.493 | CAMPAIGN_008_val | 2 | 2 |
| GBP_USD | -0.107 | -0.028 | -0.028 | -0.148 | -0.242 | +0.117 | +0.391 | +0.498 | CAMPAIGN_009_val | 2 | 2 |
| USD_JPY | -0.122 | -0.002 | -0.002 | -0.000 | +0.000 | +0.001 | -0.000 | +0.123 | CAMPAIGN_008_val | 3 | 3 |
| AUD_USD | -0.147 | -0.037 | -0.037 | -0.104 | -0.355 | +0.088 | +0.248 | +0.395 | CAMPAIGN_009_val | 2 | 2 |
| USD_CAD | -0.008 | -0.159 | -0.159 | -0.100 | -0.141 | +0.105 | +0.014 | +0.113 | CAMPAIGN_008_val | 0 | 1 |
| USD_CHF | -0.004 | -0.459 | -0.459 | -0.307 | -0.063 | +0.409 | +0.391 | +0.413 | CAMPAIGN_008_val | 0 | 2 |

## Reading

- `random R` = CAMPAIGN_005 random-entry expectancy for that pair (mean of 20 seeds × matched-frequency entries). The univ-wide mean is **−0.095 R**.
- A cell is `>= random R + +0.05` only when the strategy's expectancy is *materially* better than random entry; smaller gaps are within the random null's noise band.
- A pair with `n above null (test) >= 1` shows at least one *test-window* result above the null — that is the strongest form of evidence in the archive. A pair with only `n above null (val-only) >= 1` was above null only on a validation window whose test lockbox never opened — that is the high-overfit-risk pattern flagged in the meta-analysis (Lesson 4).
- The lab does not interpret these cells as future expectations. They are descriptive history; a new edge-discovery candidate should still run its own per-pair forward-return study against its own random null.

## Reproducibility

- Numbers are verbatim from committed CAMPAIGN_002, 003, 004, 005, 007, 008, 009 reports under `backtests/`. The source row for each cell is named in the source-cells block at the top of `research/edge_discovery/studies/study_pair_baseline.py`.


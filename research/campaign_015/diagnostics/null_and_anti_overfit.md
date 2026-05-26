# CAMPAIGN_015 — Null + Anti-Overfit Post-Run Diagnostic

**Campaign:** `failed_breakout_reversal 0.1.0-c015`
**Null model:** `random_entry_anchor`
**Anti-overfit label:** **`ROBUST_ABOVE_NULL`**
**Approval status:** `NOT_APPROVED` — `approved: []`

> Even a ROBUST_ABOVE_NULL label here does NOT approve failed_breakout_reversal; approval requires a fresh pre-committed campaign on a clean candidate and a human registry edit. CAMPAIGN_011 evidence is read-only.

## Per-fold gap vs matched CAMPAIGN_011 null

| fold | window | campaign exp R | null exp R | gap R | campaign trades | null trades |
|---|---|---|---|---|---|---|
| 0 | 2021-12-21..2022-06-18 | -0.2049 | -0.1039 | **-0.1011** | 18 | 143 |
| 1 | 2022-06-19..2022-12-15 | +0.0594 | -0.0209 | **+0.0803** | 26 | 150 |
| 2 | 2022-12-16..2023-06-13 | +0.3138 | +0.0387 | **+0.2751** | 26 | 153 |
| 3 | 2023-06-14..2023-12-10 | +0.4288 | -0.0056 | **+0.4344** | 28 | 150 |
| 4 | 2023-12-11..2024-06-07 | +0.3086 | +0.0147 | **+0.2938** | 24 | 162 |
| 5 | 2024-06-08..2024-12-04 | +0.2090 | -0.0014 | **+0.2103** | 14 | 153 |
| 6 | 2024-12-05..2025-06-02 | +0.5681 | +0.0541 | **+0.5140** | 14 | 128 |
| 7 | 2025-06-03..2025-11-29 | +0.1015 | +0.0068 | **+0.0947** | 14 | 138 |

- mean per-fold gap R = **+0.2252**
- null per-fold std R = **0.0477**

## Anti-overfit gates

- ✓ `loo_min_mean_gap_ge_0p05` = True
- ✓ `per_fold_t_stat_ge_2p0` = True
- ✓ `median_per_fold_expectancy_ge_0` = True
- ✓ `trade_level_cumulative_r_gt_0` = True
- ✓ `pair_concentration_le_70pct` = True
- ✓ `fold_concentration_le_60pct` = True
- ✓ `cost_dominance_le_50pct` = True

## Anti-overfit metrics

- `loo_min_mean_gap_r` = +0.1840
- `per_fold_t_stat` = +3.1902
- `gap_mean_r` = +0.2252
- `median_per_fold_expectancy_r` = +0.2588
- `trade_level_cumulative_r` = +37.7265
- `pair_concentration` = +0.3021
- `fold_concentration` = +0.2226
- `cost_dominance` = +0.0000
- `aggregate_floor_pass` = True
- `within_null_pf_band_match` = False
- `worse_than_null` = False
- `selected_cell_artifact_geometry` = False

## Reasons

- all aggregate + anti-overfit gates pass; not driven by a single cell

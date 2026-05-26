# CAMPAIGN_015 — Null + Anti-Overfit Post-Run Diagnostic

**Campaign:** `failed_breakout_reversal 0.1.0-c015`
**Null model:** `random_entry_anchor`
**Anti-overfit label:** **`WITHIN_NULL`**
**Approval status:** `NOT_APPROVED` — `approved: []`

> Even a ROBUST_ABOVE_NULL label here does NOT approve failed_breakout_reversal; approval requires a fresh pre-committed campaign on a clean candidate and a human registry edit. CAMPAIGN_011 evidence is read-only.

## Per-fold gap vs matched CAMPAIGN_011 null

| fold | window | campaign exp R | null exp R | gap R | campaign trades | null trades |
|---|---|---|---|---|---|---|
| 0 | 2021-12-21..2022-06-18 | -0.0913 | -0.1039 | **+0.0126** | 38 | 143 |
| 1 | 2022-06-19..2022-12-15 | -0.0161 | -0.0239 | **+0.0077** | 52 | 150 |
| 2 | 2022-12-16..2023-06-13 | +0.0263 | +0.0391 | **-0.0129** | 55 | 155 |
| 3 | 2023-06-14..2023-12-10 | -0.1246 | -0.0060 | **-0.1186** | 50 | 150 |
| 4 | 2023-12-11..2024-06-07 | -0.0984 | +0.0147 | **-0.1131** | 47 | 162 |
| 5 | 2024-06-08..2024-12-04 | +0.2580 | -0.0028 | **+0.2607** | 38 | 154 |
| 6 | 2024-12-05..2025-06-02 | +0.0823 | +0.0541 | **+0.0283** | 48 | 128 |
| 7 | 2025-06-03..2025-11-29 | -0.0813 | +0.0068 | **-0.0882** | 47 | 138 |

- mean per-fold gap R = **-0.0029**
- null per-fold std R = **0.0479**

## Anti-overfit gates

- ✗ `loo_min_mean_gap_ge_0p05` = False
- ✗ `per_fold_t_stat_ge_2p0` = False
- ✗ `median_per_fold_expectancy_ge_0` = False
- ✗ `trade_level_cumulative_r_gt_0` = False
- ✓ `pair_concentration_le_70pct` = True
- ✓ `fold_concentration_le_60pct` = True
- ✓ `cost_dominance_le_50pct` = True

## Anti-overfit metrics

- `loo_min_mean_gap_r` = -0.0406
- `per_fold_t_stat` = -0.0681
- `gap_mean_r` = -0.0029
- `median_per_fold_expectancy_r` = -0.0487
- `trade_level_cumulative_r` = -3.7859
- `pair_concentration` = +0.3750
- `fold_concentration` = +0.1578
- `cost_dominance` = +0.0000
- `aggregate_floor_pass` = False
- `within_null_pf_band_match` = False
- `worse_than_null` = False
- `selected_cell_artifact_geometry` = False

## Reasons

- aggregate floor not met and neither worse-than-null nor selected-cell-artifact criteria fully tripped; defaulting to WITHIN_NULL

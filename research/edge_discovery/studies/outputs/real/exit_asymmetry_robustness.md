# Cross-Campaign Exit-Asymmetry — Phase 3 Robustness

**Sprint:** `research-exit-asymmetry-cross-campaign-001`
**Phase:** 3 (robustness + null comparison)
**Date:** 2026-05-24

> Exploratory lab output. **No strategy approved.** **No campaign**
> **verdict changed.** Paper / demo / live remain blocked.
> CAMPAIGN_010 - CAMPAIGN_014 remain REJECT-anchored.

## R-9 sweep across the 5 × 7 = 35 (campaign, pair) grid

- Total (campaign, pair) cells evaluated: **35**
- Cells with `mean_of_fold_means_overall > 0`: **7**
- Cells with `cumulative_r_overall < 0`: **29**
- **R-9 fires** (mean>0 AND cumulative<0): **1** out of 35
- Cells with negative median per-fold mean_R: **29**

R-9 fires on **the cells whose mean-of-fold-means looked positive while their**
**trade-level cumulative R was negative** — by construction these are small-n
averaging artifacts. They are surfaced for the lab's reading and are **not**
proposed as candidate strategies.

### Cells where R-9 fires

| campaign | instrument | mean_of_fold_means_overall | cumulative_r_overall | median_per_fold_R | stop_rate σ |
|---|---|---:|---:|---:|---:|
| CAMPAIGN_012_regime_switcher_atr_percentile | EUR_USD | +0.0300 | -4.391 | -0.0189 | 0.0542 |

## Per-(campaign × pair) fold dispersion of stop_rate and mean_R_overall

(Selected highlights only; full table in JSON.)

| campaign | instrument | stop_rate σ | mean_R_overall σ |
|---|---|---:|---:|
| CAMPAIGN_010_session_breakout | NZD_USD | 0.1694 | 0.2732 |
| CAMPAIGN_011_random_entry_anchor | NZD_USD | 0.1411 | 0.1999 |
| CAMPAIGN_014_calendar_event_window_anomaly | USD_CHF | 0.1354 | 0.1129 |
| CAMPAIGN_011_random_entry_anchor | USD_CAD | 0.1196 | 0.1463 |
| CAMPAIGN_014_calendar_event_window_anomaly | EUR_USD | 0.1139 | 0.2134 |
| CAMPAIGN_014_calendar_event_window_anomaly | AUD_USD | 0.1110 | 0.1411 |
| CAMPAIGN_014_calendar_event_window_anomaly | NZD_USD | 0.1067 | 0.1436 |
| CAMPAIGN_011_random_entry_anchor | USD_JPY | 0.1033 | 0.0015 |
| CAMPAIGN_011_random_entry_anchor | EUR_USD | 0.1006 | 0.1898 |
| CAMPAIGN_010_session_breakout | EUR_USD | 0.0831 | 0.0804 |

## Above-floor-cell screens

### CAMPAIGN_013_cross_pair_currency_strength_rotation × EUR_USD on `mean_r_given_time`

**Classification:** `INSUFFICIENT_DATA`

- n_folds_paired: 5
- mean_gap_r: **+0.1112** R
- median_gap_r: +0.1433 R
- se_mean_gap_r: 0.0563 R
- t_stat: **1.974**
- min_loo_mean_gap_r: **+0.0785** R
- max_loo_mean_gap_r: +0.1490 R
- median per-fold candidate metric: +0.2341
- folds positive on metric (≥ 5/8): 5
- folds with positive gap (≥ 5/8): 3
- mean_of_fold_means_overall: -0.0463
- cumulative_r_overall: -67.447
- R-9 fires: **False**
- stop_rate-gap correlation: -0.794

Screens:
  - `enough_paired_folds_for_screen`: NOT MET
  - `loo_min_above_floor`: PASS
  - `t_stat_at_or_above_2`: NOT MET
  - `median_per_fold_cand_non_negative`: PASS
  - `r9_does_not_fire`: PASS
  - `majority_folds_positive_on_metric`: PASS
  - `majority_folds_positive_gap`: NOT MET
  - `stop_rate_driven_corr_below_0_5`: NOT MET

**Failures (4):** ['enough_paired_folds_for_screen', 't_stat_at_or_above_2', 'majority_folds_positive_gap', 'stop_rate_driven_corr_below_0_5']

LOO values by dropped fold:
  - dropping fold-paired index 0: +0.1032
  - dropping fold-paired index 1: +0.1490
  - dropping fold-paired index 2: +0.0863
  - dropping fold-paired index 3: +0.1392
  - dropping fold-paired index 4: +0.0785

## Provenance

- data_kind: `real`
- pair_universe: `['EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD', 'USD_CAD', 'USD_CHF', 'NZD_USD']`
- date_coverage: 2020-01-01 00:00:00+00:00 → 2026-05-20 00:00:00+00:00
- inputs (6):
  - campaign_walk_forward_results · /Users/kashane/dev/forex-bot/.claude/worktrees/vibrant-heisenberg-1d2de2/backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json · sha256 `36792d75d32b...`
  - campaign_walk_forward_results · /Users/kashane/dev/forex-bot/.claude/worktrees/vibrant-heisenberg-1d2de2/backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json · sha256 `ac6e72942d1a...`
  - campaign_walk_forward_results · /Users/kashane/dev/forex-bot/.claude/worktrees/vibrant-heisenberg-1d2de2/backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.json · sha256 `3bea07f2399b...`
  - campaign_walk_forward_results · /Users/kashane/dev/forex-bot/.claude/worktrees/vibrant-heisenberg-1d2de2/backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/results.json · sha256 `ddef199dc95b...`
  - campaign_walk_forward_results · /Users/kashane/dev/forex-bot/.claude/worktrees/vibrant-heisenberg-1d2de2/backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/results.json · sha256 `fbf8a0762c3d...`
  - phase12_extraction_json · /Users/kashane/dev/forex-bot/.claude/worktrees/vibrant-heisenberg-1d2de2/research/edge_discovery/studies/outputs/real/exit_asymmetry_cross_campaign.json · sha256 `dd07e4d07e4b...`

---

This output **does not approve** any strategy and **does not change**
any campaign verdict. `PROMISING_BUT_INSUFFICIENT_LAB_SIGNAL` is a
descriptive record of the partial-signal pattern the single-pair-probe
sprint already required ≥ 2 above-floor cells (or LOO stability) to override.

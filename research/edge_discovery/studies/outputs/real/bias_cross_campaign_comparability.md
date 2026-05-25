# Bias-of-Fixtures Audit — Cross-Campaign Comparability (Phase 3)

> Exploratory lab output. Not a strategy verdict. Does not approve, reverse, or revive any strategy. Verdict-word ban acknowledged.

## Headline

- n_campaigns: 5
- n_invariant_axes_pass: 5
- n_invariant_axes_total: 5
- trade_window_asymmetry_present: True
- exit_asymmetry_headline_survives_test_only_restriction: True
- max_classification_severity: weakens_comparison

## Invariant axes (Phase-1 facts re-asserted as code)

- **fold_layout**: all campaigns share layout = `True`
- **pair_universe**: all campaigns share universe = `True`
- **cost_assumptions**: all share fill_model + fill_timing + granularity = `True`
- **trade_csv_schema**: single column-set across all 280 CSVs = `True`  (count = 14)
- **exit_reason_vocab**: all share vocabulary = `True`  (`['eod', 'stop', 'time']`)

## Trade-window populations (the F0-2 finding, quantified)

| campaign | n_total | in test | in validation | in train | share test | coverage |
|---|---:|---:|---:|---:|---:|---|
| CAMPAIGN_010_session_breakout | 2791 | 2791 | 0 | 0 | 1.000 | complete |
| CAMPAIGN_011_random_entry_anchor | 1177 | 1177 | 0 | 0 | 1.000 | complete |
| CAMPAIGN_012_regime_switcher_atr_percentile | 3726 | 2009 | 1717 | 0 | 0.539 | partial |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 7940 | 3237 | 3530 | 1173 | 0.408 | partial |
| CAMPAIGN_014_calendar_event_window_anomaly | 720 | 365 | 355 | 0 | 0.507 | partial |

## Headline-number survival under test-only restriction

| campaign | n_full | n_test_only | mean_R given_time (full) | mean_R given_time (test-only) | Δ | mean_R_overall (full) | mean_R_overall (test-only) | Δ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CAMPAIGN_010_session_breakout | 2791 | 2791 | 0.1926 | 0.1926 | +0.0000 | -0.0408 | -0.0408 | +0.0000 |
| CAMPAIGN_011_random_entry_anchor | 1177 | 1177 | 0.2093 | 0.2093 | +0.0000 | -0.0024 | -0.0024 | +0.0000 |
| CAMPAIGN_012_regime_switcher_atr_percentile | 3726 | 2009 | 0.1450 | 0.1436 | -0.0014 | -0.0521 | -0.0484 | +0.0037 |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 7940 | 3237 | 0.2105 | 0.2107 | +0.0002 | -0.0564 | -0.0415 | +0.0149 |
| CAMPAIGN_014_calendar_event_window_anomaly | 720 | 365 | 0.0667 | 0.0640 | -0.0027 | -0.1477 | -0.1667 | -0.0190 |

**Survival summary:**
- all_campaigns_positive_mean_r_given_time_test_only: True
- all_campaigns_negative_mean_r_overall_test_only:    True
- null_still_highest_mean_r_given_time_test_only:     False
- exit_asymmetry_headline_survives_test_only:         True

## Per-campaign coverage anomalies

| campaign | empty (fold,pair) cells out of 56 |
|---|---:|
| CAMPAIGN_010_session_breakout | 2 |
| CAMPAIGN_011_random_entry_anchor | 0 |
| CAMPAIGN_012_regime_switcher_atr_percentile | 0 |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 29 |
| CAMPAIGN_014_calendar_event_window_anomaly | 0 |

## Differences classification

| axis | observed | classification | rationale |
|---|---|---|---|
| fold_layout | identical 8-fold layout across all 5 campaigns | **harmless** | no comparability cost; comparison preserved |
| pair_universe | identical 7-major universe across all 5 campaigns | **harmless** | no comparability cost |
| fill_model_fill_timing_granularity | identical across all 5 campaigns | **harmless** | engine-level assumptions match; no comparability cost |
| trade_csv_schema | single 14-column schema across all 280 trade CSVs | **harmless** | no comparability cost |
| exit_reason_vocabulary | vocabulary ['eod', 'stop', 'time'] identical across 5 | **harmless** | no comparability cost |
| trade_window_population | test-only complete: ['CAMPAIGN_010_session_breakout', 'CAMPAIGN_011_random_entry_anchor']; partial (mixed train/validation/test): ['CAMPAIGN_012_regime_switcher_atr_percentile', 'CAMPAIGN_013_cross_pair_currency_strength_rotation', 'CAMPAIGN_014_calendar_event_window_anomaly'] | **needs_documentation** | trade-window asymmetry exists but the cross-campaign exit-asymmetry headline survives the test-only restriction; the screens themselves remain correct because they are cell-level (per fold per pair) and the test-only restriction tightens rather than loosens them |
| coverage_anomalies | empty cells: {'CAMPAIGN_010_session_breakout': 2, 'CAMPAIGN_013_cross_pair_currency_strength_rotation': 29} | **weakens_comparison** | empty cells are a strategy property (no signal), not a fixture defect, but they reduce per-pair sample size in cross-campaign aggregates and should be documented |

## Provenance and refusals

- data_kind: `real`
- exploratory_only: `True`
- inputs: 5 artifact(s)
- verdict_word_ban_acknowledged: `True`
- refusals:
  - approves_strategy: `False`
  - changes_campaign_verdict: `False`
  - proposes_parameter_tune: `False`
  - writes_to_approved_strategies_yaml: `False`

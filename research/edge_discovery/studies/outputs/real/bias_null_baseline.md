# Bias-of-Fixtures Audit — Null Baseline (Phase 2)

> Exploratory lab output. Not a strategy verdict. Does not approve, reverse, or revive any strategy. Verdict-word ban acknowledged.

## Headline

- n_campaigns: 5
- n_trades_total: 16354
- null_campaign: `CAMPAIGN_011_random_entry_anchor`
- null_trade_count: 1177
- null_coverage_complete: True
- null_outlier_vs_others_any_metric: True

## Coverage

| campaign | folds with trades | pairs with trades | empty (fold,pair) cells |
|---|---:|---:|---:|
| CAMPAIGN_010_session_breakout | 8 | 7 | 2 |
| CAMPAIGN_011_random_entry_anchor | 8 | 7 | 0 |
| CAMPAIGN_012_regime_switcher_atr_percentile | 8 | 7 | 0 |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 8 | 7 | 29 |
| CAMPAIGN_014_calendar_event_window_anomaly | 8 | 7 | 0 |

## Trade-count dispersion (null highlighted)

| campaign | n_trades | max_pair_share | max_pair | max_fold_share | max_fold | classification |
|---|---:|---:|---|---:|---:|---|
| CAMPAIGN_010_session_breakout | 2791 | 0.202 | GBP_USD | 0.147 | 2 | minor_deviation / within_expected_range |
| CAMPAIGN_011_random_entry_anchor | 1177 | 0.167 | GBP_USD | 0.138 | 4 | within_expected_range / within_expected_range |
| CAMPAIGN_012_regime_switcher_atr_percentile | 3726 | 0.167 | USD_JPY | 0.218 | 1 | within_expected_range / minor_deviation |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 7940 | 0.245 | AUD_USD | 0.158 | 4 | minor_deviation / within_expected_range |
| CAMPAIGN_014_calendar_event_window_anomaly | 720 | 0.211 | GBP_USD | 0.139 | 4 | minor_deviation / within_expected_range |

## Direction balance

| campaign | n | long_share | short_share | |Δ|–from-50/50 | classification |
|---|---:|---:|---:|---:|---|
| CAMPAIGN_010_session_breakout | 2791 | 0.506 | 0.494 | 0.006 | within_expected_range |
| CAMPAIGN_011_random_entry_anchor | 1177 | 0.518 | 0.482 | 0.018 | within_expected_range |
| CAMPAIGN_012_regime_switcher_atr_percentile | 3726 | 0.515 | 0.485 | 0.015 | within_expected_range |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 7940 | 0.495 | 0.505 | 0.005 | within_expected_range |
| CAMPAIGN_014_calendar_event_window_anomaly | 720 | 0.490 | 0.510 | 0.010 | within_expected_range |

## Session / hour-of-day clustering

| campaign | n | max_hour_utc | max_hour_share | classification |
|---|---:|---:|---:|---|
| CAMPAIGN_010_session_breakout | 2791 | 9 | 0.631 | material_deviation |
| CAMPAIGN_011_random_entry_anchor | 1177 | 9 | 0.166 | minor_deviation |
| CAMPAIGN_012_regime_switcher_atr_percentile | 3726 | 13 | 0.162 | minor_deviation |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 7940 | 13 | 0.200 | minor_deviation |
| CAMPAIGN_014_calendar_event_window_anomaly | 720 | 13 | 0.617 | material_deviation |

## Exit-reason distribution

| campaign | stop | time | eod | shares |
|---|---:|---:|---:|---|
| CAMPAIGN_010_session_breakout | 661 | 2107 | 23 | stop: 0.237 / time: 0.755 / eod: 0.008 |
| CAMPAIGN_011_random_entry_anchor | 241 | 929 | 7 | stop: 0.205 / time: 0.789 / eod: 0.006 |
| CAMPAIGN_012_regime_switcher_atr_percentile | 760 | 2953 | 13 | stop: 0.204 / time: 0.793 / eod: 0.003 |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 1830 | 6087 | 23 | stop: 0.230 / time: 0.767 / eod: 0.003 |
| CAMPAIGN_014_calendar_event_window_anomaly | 174 | 537 | 9 | stop: 0.242 / time: 0.746 / eod: 0.013 |

## Null-vs-others exit-shape comparison

Question: does the null sit *inside* the range that the four candidate
campaigns span on each shape metric? If yes, the null is a structurally
legitimate baseline. If no, the null is an outlier.

| metric | null_value | others_min | others_max | null_outside_range |
|---|---:|---:|---:|:---:|
| stop_rate | 0.2048 | 0.2040 | 0.2417 | no |
| time_rate | 0.7893 | 0.7458 | 0.7925 | no |
| mean_r_given_stop | -0.8312 | -0.9483 | -0.7917 | no |
| mean_r_given_time | 0.2093 | 0.0667 | 0.2105 | no |
| mean_r_overall | -0.0024 | -0.1477 | -0.0408 | **YES** |

## Interpretation (Phase-2 only)

The null sits **outside** the cross-campaign range on at least one shape metric: `mean_r_overall`. This does not automatically disqualify the null — by construction the random-entry baseline can legitimately have a different shape than rule-based candidates. The audit's purpose is to surface this, not to silently bury it. Phase 5 decides whether the deviation requires a documentation note or a rule update.

---

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

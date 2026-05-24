# Cross-Campaign Exit-Asymmetry — Phases 1 + 2 Output

**Sprint:** `research-exit-asymmetry-cross-campaign-001`
**Phase:** 1 + 2 (extraction + descriptive aggregation)
**Date:** 2026-05-24

> Exploratory lab output. **No strategy approved.** **No campaign**
> **verdict changed.** Paper / demo / live remain blocked.
> CAMPAIGN_010 - CAMPAIGN_014 remain REJECT-anchored.

## Headline numbers

- Trades loaded: **16,354** across 5 campaigns × 7 pairs × 8 folds per campaign.
- Observed `exit_reason` vocabulary: `['eod', 'stop', 'time']`.

## Per-campaign exit shape

| campaign | n_total | stop_rate | time_rate | mean_R_given_stop | mean_R_given_time | mean_R_overall | sum_R_overall | pct_stops≤−0.95 | pct_time∈[−0.5,+0.5] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CAMPAIGN_010_session_breakout | 2,791 | 0.237 | 0.755 | -0.7917 | 0.1926 | -0.0408 | -113.938 | 0.637 | 0.687 |
| CAMPAIGN_011_random_entry_anchor | 1,177 | 0.205 | 0.789 | -0.8312 | 0.2093 | -0.0024 | -2.872 | 0.705 | 0.665 |
| CAMPAIGN_012_regime_switcher_atr_percentile | 3,726 | 0.204 | 0.792 | -0.8178 | 0.1450 | -0.0521 | -194.205 | 0.679 | 0.686 |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 7,940 | 0.231 | 0.767 | -0.9483 | 0.2105 | -0.0564 | -448.021 | 0.856 | 0.630 |
| CAMPAIGN_014_calendar_event_window_anomaly | 720 | 0.242 | 0.746 | -0.8081 | 0.0667 | -0.1477 | -106.370 | 0.718 | 0.739 |

## Structural-pattern check (Phase 0 §6)

**Classification:** `STRUCTURAL_FAILURE_PATTERN_PARTIAL`

- Condition 1 (universal hard stop, ≥ 90% stops at or below −0.95 R): **NOT MET**
  - CAMPAIGN_010_session_breakout: 0.637
  - CAMPAIGN_011_random_entry_anchor: 0.705
  - CAMPAIGN_012_regime_switcher_atr_percentile: 0.679
  - CAMPAIGN_013_cross_pair_currency_strength_rotation: 0.856
  - CAMPAIGN_014_calendar_event_window_anomaly: 0.718
- Condition 2 (universal small-positive time shape): **NOT MET**
  - CAMPAIGN_010_session_breakout: pct_in_band=0.687, mean_r_given_time>0=True
  - CAMPAIGN_011_random_entry_anchor: pct_in_band=0.665, mean_r_given_time>0=True
  - CAMPAIGN_012_regime_switcher_atr_percentile: pct_in_band=0.686, mean_r_given_time>0=True
  - CAMPAIGN_013_cross_pair_currency_strength_rotation: pct_in_band=0.630, mean_r_given_time>0=True
  - CAMPAIGN_014_calendar_event_window_anomaly: pct_in_band=0.739, mean_r_given_time>0=True
- Condition 3 (null shares the shape, |Δ| ≤ 0.05 vs median of others): **PASS**
  - null stop_rate 0.2048 vs median 0.2337 (|Δ|=0.0289)
  - null mean_R_given_stop -0.8312 vs median -0.8129 (|Δ|=0.0183)
- Condition 4 (fold-noise driver, median per-pair stop_rate σ ≥ 0.05): **PASS** (observed 0.0609)

## Decomposition of gross losses and gross gains

| campaign | share_gross_loss_from_stops | share_gross_gain_from_time_exits |
|---|---:|---:|
| CAMPAIGN_010_session_breakout | 0.688 | 0.990 |
| CAMPAIGN_011_random_entry_anchor | 0.668 | 0.989 |
| CAMPAIGN_012_regime_switcher_atr_percentile | 0.631 | 0.999 |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 0.681 | 0.996 |
| CAMPAIGN_014_calendar_event_window_anomaly | 0.642 | 0.997 |

## Per-(campaign, side) — does long vs short share the pattern?

| campaign | side | n | stop_rate | mean_R_given_stop | mean_R_given_time | mean_R_overall |
|---|---|---:|---:|---:|---:|---:|
| CAMPAIGN_010_session_breakout | long | 1,413 | 0.226 | -0.7708 | 0.1865 | -0.0310 |
| CAMPAIGN_010_session_breakout | short | 1,378 | 0.248 | -0.8113 | 0.1989 | -0.0509 |
| CAMPAIGN_011_random_entry_anchor | long | 610 | 0.225 | -0.8054 | 0.1885 | -0.0352 |
| CAMPAIGN_011_random_entry_anchor | short | 567 | 0.183 | -0.8652 | 0.2307 | 0.0328 |
| CAMPAIGN_012_regime_switcher_atr_percentile | long | 1,918 | 0.208 | -0.8171 | 0.1501 | -0.0518 |
| CAMPAIGN_012_regime_switcher_atr_percentile | short | 1,808 | 0.200 | -0.8187 | 0.1397 | -0.0525 |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | long | 3,927 | 0.234 | -0.9655 | 0.2120 | -0.0643 |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | short | 4,013 | 0.227 | -0.9309 | 0.2090 | -0.0487 |
| CAMPAIGN_014_calendar_event_window_anomaly | long | 353 | 0.252 | -0.8647 | 0.0090 | -0.2129 |
| CAMPAIGN_014_calendar_event_window_anomaly | short | 367 | 0.232 | -0.7487 | 0.1204 | -0.0850 |

## Above-floor cells worth Phase 3 screening

Cells whose `mean_R_given_time` or `mean_R_overall` clears the +0.05 R floor against CAMPAIGN_011's matched cell. **Listed for Phase 3 robustness screens only — none of these is approved.**

| campaign | instrument | n_cand | n_null | gap mean_R_overall | gap mean_R_given_time |
|---|---|---:|---:|---:|---:|
| CAMPAIGN_013_cross_pair_currency_strength_rotation | EUR_USD | 1,412 | 119 | -0.0074 | +0.0531 |

## Provenance

- data_kind: `real`
- pair_universe: `['EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD', 'USD_CAD', 'USD_CHF', 'NZD_USD']`
- date_coverage: 2020-01-01 00:00:00+00:00 → 2026-05-20 00:00:00+00:00
- inputs (5):
  - campaign_walk_forward_results · /Users/kashane/dev/forex-bot/.claude/worktrees/vibrant-heisenberg-1d2de2/backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json · sha256 `36792d75d32b...`
  - campaign_walk_forward_results · /Users/kashane/dev/forex-bot/.claude/worktrees/vibrant-heisenberg-1d2de2/backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json · sha256 `ac6e72942d1a...`
  - campaign_walk_forward_results · /Users/kashane/dev/forex-bot/.claude/worktrees/vibrant-heisenberg-1d2de2/backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.json · sha256 `3bea07f2399b...`
  - campaign_walk_forward_results · /Users/kashane/dev/forex-bot/.claude/worktrees/vibrant-heisenberg-1d2de2/backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/results.json · sha256 `ddef199dc95b...`
  - campaign_walk_forward_results · /Users/kashane/dev/forex-bot/.claude/worktrees/vibrant-heisenberg-1d2de2/backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/results.json · sha256 `fbf8a0762c3d...`

---

This output **does not approve** any strategy and **does not change**
any campaign verdict. The classification fields above describe the
lab's structural-pattern check; they do not promote any candidate.

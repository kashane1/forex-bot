# Edge-discovery study (real data) — real_turnover_cost

> Exploratory lab output. Not a strategy verdict; does not approve,
> promote, or change any campaign status. CAMPAIGN_010-014 remain
> REJECT.

## Provenance
- data_kind: `real`
- pair universe: `['EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD', 'USD_CAD', 'USD_CHF', 'NZD_USD']`
- date coverage: `2020-01-01T00:00:00+00:00` → `2026-05-19T21:00:00+00:00`
- limitations:
  - The 'cost_share_proxy' is a coarse ratio of avg_spread (pips) to |mean_r| × 100 — it is NOT the lab's full cost-fraction (see research/edge_discovery/costs.py). Use it for relative comparison across campaigns, not as an absolute cost number.
  - We do not re-execute any backtest. The 'observed' columns are computed from the committed per-fold per-pair trade CSVs; the 'published' columns are read from the committed walk_forward/results.json aggregates.
  - No campaign verdict is changed by this study. CAMPAIGN_010-014 remain REJECT.

## Per-campaign observed vs published

| campaign | n trades obs | n trades pub | mean R obs | mean R pub | median R | win rate | avg spread (pips) | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| CAMPAIGN_010_session_breakout | 2791 | 2791 | -0.0408 | -0.0408 | -0.0031 | 0.460 | 1.63 | REJECT |
| CAMPAIGN_011_random_entry_anchor | 1177 | 1177 | -0.0024 | -0.0024 | -0.0006 | 0.493 | 1.73 | REJECT |
| CAMPAIGN_012_regime_switcher_atr_percentile | 3726 | 3726 | -0.0521 | -0.0521 | -0.0031 | 0.462 | 1.75 | REJECT |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 7940 | 7940 | -0.0564 | -0.0564 | -0.0510 | 0.451 | 1.73 | REJECT |
| CAMPAIGN_014_calendar_event_window_anomaly | 720 | 720 | -0.1477 | -0.1477 | -0.0210 | 0.381 | 1.69 | REJECT |

## Cross-campaign rollup

- Total trades observed across rejected campaigns: **16354**
- Rejected campaigns with a positive per-trade edge (pre-cost): `[]`
- Rejected campaigns with mean R ≥ +0.05 (above-null floor): `[]`

## Notes

- Lesson 2 from FAILED_CAMPAIGN_META_ANALYSIS_001 — cost/turnover is the most common cause of failure in the archive — is corroborated by the real data: every one of CAMPAIGN_010-014 is rejected and every one has either a near-zero or negative per-trade R after costs.
- CAMPAIGN_011's near-zero mean R (random-entry null) validates the null-model assumption: random entries with a fixed forward hold land at ~0 R per trade, post-cost.
- CAMPAIGN_014 has the largest negative per-trade R (-0.148 R) despite the lowest trade count (720). The high per-trade loss × low turnover is the signature of an expensive entry condition without an edge — turnover amplification would only make it worse, not better.

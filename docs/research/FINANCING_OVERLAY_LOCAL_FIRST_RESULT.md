# Financing Overlay — Local-First Result

**Sprint:** `infra-observed-cost-financing-overlay-local-first-001`  
**Date:** 2026-05-27

## Commands run

```bash
python scripts/apply_financing_overlay_to_trade_ledgers.py --inventory-only
python scripts/apply_financing_overlay_to_trade_ledgers.py
# modes: none, synthetic_fixture, manual_observed_fixture (default)
```

Artifacts: `research/financing_overlay_local_first/`

## Selected ledgers

| Label | Campaign | Trades (aggregate) |
|-------|----------|-------------------|
| c019_train_validation_base | C019 | 357 |
| c016_weekly_momentum_folds_base | C016 | 137 |
| c017_weekly_vol_breakout_folds_base | C017 | 230 |
| c008_deduped_forensic_train | C008 | 216 |

## Financing mode(s)

Primary analysis: **`synthetic_fixture`** (`default_stress_rate_source`, conservative stress).  
Baseline comparison: **`none`**.  
Secondary: **`manual_observed_fixture`** (committed `rates_two_week_*.json`, still synthetic-labeled).

## Assumptions

- H4 bar = 4 hours for hold-day buckets
- R from `stop_price` and `units` via `risk_usd`
- Ledger rows with `exit_time <= entry_time` repaired using `bars_held` (see warnings in overlay output)
- Stress rates are **upper-bound diagnostic**, not observed broker financing

## Campaign-level adjusted deltas (synthetic_fixture)

| Ledger | Gross E[R] | Adjusted E[R] | Financing drag (ΔR) |
|--------|------------|---------------|---------------------|
| c019_train_validation_base | -0.0070 | -0.0893 | -0.0823 |
| c016_weekly_momentum_folds_base | -0.0633 | -0.1153 | -0.0520 |
| c017_weekly_vol_breakout_folds_base | -0.0227 | -0.0665 | -0.0439 |
| c008_deduped_forensic_train | -0.0250 | -0.1051 | -0.0802 |

Source: `research/financing_overlay_local_first/adjusted_metric_delta.json`

## Pair-level / hold-bucket

See `overlay_summary_by_pair.csv` and `overlay_summary_by_hold_bucket.csv`.  
**3–7d** and **7d+** buckets show largest cumulative financing drag (multi-day holds).

## Sensitivity

- **Most sensitive:** C008/C019 H4 mean-reversion families (~0.08R drag under stress)
- **Weekly:** C016/C017 show ~0.04–0.05R drag; already weak gross expectancy
- **Pairs:** JPY crosses and longer-hold USD legs typically dominate drag in per-pair CSV (see artifacts)

## Campaign interpretation changes

- **No verdict changes.** C019 remains **REJECT**; financing overlay makes negative expectancy more negative but does not upgrade or downgrade formal verdict tokens.
- Multi-day/weekly campaigns should treat gross R as **optimistic** until observed financing overlay or capture sprint completes.
- Short-hold / intraday campaigns: smaller drag; financing WARN less blocking than fill-timing (`next_bar_open`).

## Observed financing rerun required?

**Yes, for promotion review of any multi-day/weekly strategy** — but via future read-only capture sprint, not this infrastructure sprint.

## No-approval statement

Synthetic financing-adjusted metrics are **not** strategy evidence and do not approve trading.

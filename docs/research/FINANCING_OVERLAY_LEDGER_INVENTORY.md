# Financing Overlay — Trade Ledger Inventory

**Sprint:** `infra-observed-cost-financing-overlay-local-first-001`  
**Generated:** 2026-05-27 (from `scripts/apply_financing_overlay_to_trade_ledgers.py --inventory-only`)

## Summary

Scanned compact `*_trades.csv` under C015–C019, C008 forensic train, weekly fold bases. All sampled ledgers include timestamps, side, units, `r_multiple`, `pnl`, `stop_price`. **Financing is not applied in campaign engine PnL** (`financing_in_engine: false`).

## Full inventory (campaign aggregates)

| Campaign folder | CSV files | Total trades | Avg hold (days) | Max hold (days) | Overlay-ready |
|-----------------|-----------|--------------|-----------------|-----------------|---------------|
| CAMPAIGN_008_mean_reversion_deduped_forensic | 6 | 216 | 3.13 | 6.7 | Yes |
| CAMPAIGN_015_failed_breakout_reversal_deduped | 52 | 375 | 1.28 | 2.0 | Yes (short holds) |
| CAMPAIGN_016_weekly_cross_sectional_momentum | 45 | 137 | 4.00 | 7.0 | Yes |
| CAMPAIGN_017_weekly_volatility_contraction_breakout | 56 | 230 | 5.87 | 7.0 | Yes |
| CAMPAIGN_018_mean_reversion_protective_stop | 12 | 378 | 2.25 | 6.7 | Yes |
| CAMPAIGN_019_mean_reversion_thesis_invalidation | 12 | 357 | 3.19 | 6.7 | Yes |

Per-file detail: `research/financing_overlay_local_first/ledger_inventory_used.json` (machine-readable).

## Selected reference ledgers

| Ledger label | Campaign | Why selected |
|--------------|----------|--------------|
| `c019_train_validation_base` | C019 | Recent REJECT reference; train+validation base, 357 trades, ~3.2d avg hold |
| `c016_weekly_momentum_folds_base` | C016 | Weekly rebalance; longest typical holds in pause-era weekly family |
| `c017_weekly_vol_breakout_folds_base` | C017 | Weekly breakout; higher avg hold (~5.9d aggregate) |
| `c008_deduped_forensic_train` | C008 | Prior `c008_c009_c018_financing_exposure.json` baseline for comparison |

## Ledgers skipped

| Item | Reason |
|------|--------|
| CAMPAIGN_011 null baseline | JSON metrics, not standard trades CSV |
| CAMPAIGN_015 (full) | Short holds (~1.3d); lower financing sensitivity; kept in inventory only |
| C018 train/full stress | Redundant with C019 for sprint scope; available for future overlay |
| Raw summary-only JSON without trades | Cannot apply position-interval financing |

## Data gaps

- Some weekly fold rows have `exit_time <= entry_time` in CSV (e.g. C016 `fold_00_USD_JPY`); overlay repairs using `bars_held` × H4 bar hours (documented warning).
- `manual_observed_fixture` uses committed **synthetic** rate JSON, not broker transaction history.
- Session/spread bucket not in trade CSV — requires join to `research/cost_atlas/` (Phase 6).

## No-approval statement

Ledger selection does not approve any strategy or change campaign verdicts.

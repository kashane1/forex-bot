# Backtrader CAMPAIGN_015 Fold-Window Preflight

**Sprint:** [Window Alignment 001](BACKTRADER_CAMPAIGN_015_WINDOW_ALIGNMENT_001_PLAN.md)
**Branch:** `infra-backtrader-campaign-015-window-alignment-001`
**Date:** 2026-05-26
**Status:** **PASS** (all folds runnable)

> Diagnostic-only. Does not approve any strategy.
> `configs/approved_strategies.yaml` remains `approved: []`.

## Command

```bash
python scripts/run_backtrader_parity.py \
  --campaign CAMPAIGN_015 \
  --run-mode fold_windows \
  --fold-plan research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/plan.json \
  --output research/campaign_015/diagnostics/backtrader_fold_window \
  --dry-run
```

## Results

| check | result |
|---|---|
| Fold plan loaded | 8 folds from rehydrate `plan.json` |
| Instruments | 7/7 (EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD) |
| CSV/provenance strict preflight | PASS (no sha drift) |
| Blocked instruments | **0** |
| Blocked folds | **0** |
| Warmup margin | 90 calendar days (matches bespoke `_fold_dates_to_dts`) |
| Candle coverage per fold | ~1,140–1,164 H4 bars per pair per fold |
| Live/broker/OANDA/LEAN path | **not touched** |
| `runnable` | **true** |

## Fold load windows (sample)

| fold | test_start | test_end | candle_load_start | pairs loaded |
|---:|---|---|---|---:|
| 0 | 2021-12-21 | 2022-06-18 | 2021-09-22 | 7/7 |
| 1 | 2022-06-19 | 2022-12-15 | 2022-03-21 | 7/7 |
| 2 | 2022-12-16 | 2023-06-13 | 2022-09-17 | 7/7 |
| 3 | 2023-06-14 | 2023-12-10 | 2023-03-16 | 7/7 |
| 4 | 2023-12-11 | 2024-06-07 | 2023-09-12 | 7/7 |
| 5 | 2024-06-08 | 2024-12-04 | 2024-03-10 | 7/7 |
| 6 | 2024-12-05 | 2025-06-02 | 2024-09-06 | 7/7 |
| 7 | 2025-06-03 | 2025-11-29 | 2025-03-05 | 7/7 |

Machine-readable dry-run manifest:
[`research/campaign_015/diagnostics/backtrader_fold_window/run_manifest.json`](../../research/campaign_015/diagnostics/backtrader_fold_window/run_manifest.json)

## Safety invariants

| invariant | state |
|---|---|
| Strategy approved | **No** |
| Paper/demo/live | **Blocked** |
| OANDA / broker called | **No** |
| Full-window BT output overwritten | **No** (separate `backtrader_fold_window/` path) |

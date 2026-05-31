# Backtrader CAMPAIGN_015 Window Alignment 001 — Plan

**Branch:** `infra-backtrader-campaign-015-window-alignment-001`
**Date:** 2026-05-26
**Sprint type:** Infrastructure (Backtrader secondary-lane window alignment)

> Does **not** approve any strategy. `configs/approved_strategies.yaml`
> remains `approved: []`. Paper / demo / live remain blocked.

## 1 · Problem statement

The Backtrader provenance-repair sprint (`infra-backtrader-campaign-015-provenance-repair-001`)
fixed CSV/provenance drift and ran BT to completion (575 trades full-window).
Bespoke rehydrate walk-forward evidence counts **164 trades** across 8 test
windows. The binding comparison classification was **`TIMESTAMP_MISMATCH`**
because BT iterated the entire ~2020–2026 CSV while bespoke ran only 8 rolling
180-day test slices with per-fold equity reset.

This sprint adds **BT-on-fold-windows** mode so the secondary lane can be
compared apples-to-apples with
`research/campaign_015/diagnostics/walk_forward_rehydrate/`.

## 2 · Phase 0 truth audit (2026-05-26)

| check | status |
|---|---|
| Branch | `infra-backtrader-campaign-015-window-alignment-001` (from provenance-repair-001) |
| `configs/approved_strategies.yaml` | `approved: []` ✓ |
| Paper/demo/live refusal | research-freeze gate PASS ✓ |
| Bespoke rehydrate artifacts | `research/campaign_015/diagnostics/walk_forward_rehydrate/` ✓ |
| BT CAMPAIGN_015 adapter | `research/backtrader_lane/strategies/campaign_015_failed_breakout_reversal.py` ✓ |
| BT CSV/provenance preflight | passes all 7 instruments (provenance-repair sprint) ✓ |
| Prior comparison classification | `TIMESTAMP_MISMATCH` (575 vs 164) ✓ |
| `pytest tests/ -q` | 1460 passed (pre-implementation baseline) |
| `check_research_freeze.py` | PASS |
| `validate_research_archive.py` | PASS |
| `scan_artifacts_for_secrets.py` | PASS |

## 3 · Fold-window source of truth

Primary:

```
research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/plan.json
```

Fallback (identical rolling parameters from `scripts/run_campaign_015.py`):

- `train_days=540`, `validation_days=180`, `test_days=180`, `step_days=180`
- `universe_start=2020-01-01`, `universe_end=2026-05-20`
- → `backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/plan.json`

8 folds; candle load window per fold matches bespoke `_fold_dates_to_dts`:
`[test_start - 90 calendar days, test_end]` inclusive.

## 4 · Implementation approach (BT-on-fold-windows)

1. **`research/backtrader_lane/fold_windows.py`** — plan loader, candle slicer, preflight.
2. **`RunOptions.run_mode = fold_windows`** — per fold × pair independent runs with equity reset.
3. **CLI** — `scripts/run_backtrader_parity.py --run-mode fold_windows --fold-plan …`
4. **Output** — `research/campaign_015/diagnostics/backtrader_fold_window/` (does not overwrite full-window BT lane).
5. **Comparison** — `scripts/compare_campaign_015_fold_windows.py` vs rehydrate.
6. **Tests** — `tests/unit/backtrader_lane/test_fold_windows.py` (synthetic data).

### Approximation flags

- `FOLD_WINDOW_BESPOKE_MIRROR`: per fold × pair equity reset; 90-day warmup margin.
- `STRICT_TEST_WINDOW=false` (default): counts trades with `entry_time` before
  `test_start` inside warmup margin (mirrors bespoke engine; 47/164 rehydrate trades).
- Full-window mode preserved unchanged (`run_mode=full`).

## 5 · Hard rules (reaffirmed)

- No strategy approval, no YAML registry change, no paper/demo/live enablement.
- No OANDA / broker / LEAN paths.
- No CAMPAIGN_015 parameter tuning or gate changes.
- No mutation of prior campaign evidence (new labeled diagnostic paths only).

## 6 · Phase deliverables

| phase | deliverable |
|---|---|
| 0 | This plan |
| 1 | fold_windows module + runner extension + tests |
| 2 | `BACKTRADER_CAMPAIGN_015_FOLD_WINDOW_PREFLIGHT.md` |
| 3 | BT fold-window run artifacts under `backtrader_fold_window/` |
| 4 | `BACKTRADER_CAMPAIGN_015_FOLD_WINDOW_COMPARISON.md` |
| 5 | `BACKTRADER_CAMPAIGN_015_WINDOW_ALIGNMENT_RESULT.md` |
| 6 | `BACKTRADER_CAMPAIGN_015_WINDOW_ALIGNMENT_001_SUMMARY.md` |

## 7 · Success criteria

1. BT fold-window mode runs all 8 folds × 7 pairs without BLOCKED.
2. Total BT fold-window trades materially closer to bespoke 164 than prior 575.
3. Comparison classification improves from `TIMESTAMP_MISMATCH`.
4. CAMPAIGN_015 remains unapproved; paper/demo/live remain blocked.

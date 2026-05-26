# Backtrader CAMPAIGN_015 Window Alignment 001 — Summary

**Branch:** `infra-backtrader-campaign-015-window-alignment-001`
**Date:** 2026-05-26
**Sprint label:** **`BT_WINDOW_ALIGNED_DIVERGENCE_NEEDS_DEBUG`**

> CAMPAIGN_015 remains **unapproved**. `configs/approved_strategies.yaml`
> remains `approved: []`. Paper / demo / live remain **blocked**.

## Commits by phase

| phase | commit | summary |
|---:|---|---|
| 0 | `ad9b2a1` | Truth audit + plan |
| 1 | `e0a5d81` | Fold-window runner mode + tests |
| 2 | `8986117` | Preflight PASS doc |
| 3–4 | `264da09` | Fold-window run + comparison artifacts |
| 5 | `c837b95` | Interpretation + next-step decision |
| 6 | *(this commit)* | Final validation + summary |

## Files changed (code + docs)

| area | paths |
|---|---|
| Core | `research/backtrader_lane/fold_windows.py`, `runner.py`, `strategies/campaign_015_failed_breakout_reversal.py` |
| CLI | `scripts/run_backtrader_parity.py`, `scripts/compare_campaign_015_fold_windows.py` |
| Tests | `tests/unit/backtrader_lane/test_fold_windows.py` |
| Docs | `docs/research/BACKTRADER_CAMPAIGN_015_WINDOW_ALIGNMENT_001_PLAN.md`, `*_FOLD_WINDOW_PREFLIGHT.md`, `*_FOLD_WINDOW_COMPARISON.md`, `*_WINDOW_ALIGNMENT_RESULT.md`, this summary |
| Artifacts | `research/campaign_015/diagnostics/backtrader_fold_window/` (summaries + comparison; trade JSONL local-only) |

## Commands run

```bash
pytest tests/ -q                                    # 1467 passed
python scripts/check_research_freeze.py             # PASS
python scripts/validate_research_archive.py         # PASS
python scripts/scan_artifacts_for_secrets.py      # PASS

python scripts/run_backtrader_parity.py \
  --campaign CAMPAIGN_015 --run-mode fold_windows \
  --fold-plan research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/plan.json \
  --output research/campaign_015/diagnostics/backtrader_fold_window \
  --dry-run

python scripts/run_backtrader_parity.py \
  --campaign CAMPAIGN_015 --run-mode fold_windows \
  --fold-plan research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/plan.json \
  --output research/campaign_015/diagnostics/backtrader_fold_window

python scripts/compare_campaign_015_fold_windows.py \
  --backtrader-dir research/campaign_015/diagnostics/backtrader_fold_window \
  --bespoke-dir research/campaign_015/diagnostics/walk_forward_rehydrate \
  --prior-bt-full-trades 575 --prior-classification TIMESTAMP_MISMATCH \
  --output research/campaign_015/diagnostics/backtrader_fold_window
```

## Fold-window source of truth

`research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/plan.json`
(8 folds, 540/180/180/180 rolling windows, universe 2020-01-01..2026-05-20)

## Preflight status

**PASS** — 8/8 folds, 7/7 pairs, 0 blocked, 90-day warmup coverage confirmed.

## Fold-window run status

**COMPLETE** — 532 total trades, ~11s wall time, no live/broker paths.

## Trade counts

| lane | trades |
|---|---:|
| Bespoke rehydrate | 164 |
| BT fold-window (this sprint) | 532 |
| BT full-window (prior) | 575 |

## Classification

| when | label |
|---|---|
| Before (full-window BT) | `TIMESTAMP_MISMATCH` |
| After (fold-window BT) | `SIGNAL_RULE_MISMATCH` (TIMESTAMP_MISMATCH **resolved**) |

## Remaining divergence

Uniform ~3.2× trade inflation across folds and sides. Most probable cause:
bespoke **RiskEngine** rejections not wired into BT adapter.

## Approval / safety

| check | state |
|---|---|
| CAMPAIGN_015 approved | **No** |
| `approved: []` | **Yes** |
| Paper/demo/live | **Blocked** |
| `.env` / credentials staged | **No** |
| SQLite staged | **No** |

## Recommended next step

**Debug remaining BT divergence** — wire RiskEngine rejection parity or
bar-level signal diff on one fold×pair before bespoke re-run or stop decision.

## Review first

1. [`docs/research/BACKTRADER_CAMPAIGN_015_WINDOW_ALIGNMENT_RESULT.md`](BACKTRADER_CAMPAIGN_015_WINDOW_ALIGNMENT_RESULT.md)
2. [`docs/research/BACKTRADER_CAMPAIGN_015_FOLD_WINDOW_COMPARISON.md`](BACKTRADER_CAMPAIGN_015_FOLD_WINDOW_COMPARISON.md)
3. [`research/campaign_015/diagnostics/backtrader_fold_window/fold_window_comparison.json`](../research/campaign_015/diagnostics/backtrader_fold_window/fold_window_comparison.json)
4. [`research/campaign_015/diagnostics/backtrader_fold_window/backtrader_summary.json`](../research/campaign_015/diagnostics/backtrader_fold_window/backtrader_summary.json)
5. [`research/backtrader_lane/fold_windows.py`](../research/backtrader_lane/fold_windows.py)

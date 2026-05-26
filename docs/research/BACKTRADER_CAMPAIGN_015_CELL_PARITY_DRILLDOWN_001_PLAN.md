# Backtrader CAMPAIGN_015 Cell Parity Drilldown 001 — Plan

**Branch:** `infra-backtrader-campaign-015-cell-parity-drilldown-001`
**Parent:** `infra-backtrader-campaign-015-riskengine-and-fill-parity-001`
**Date:** 2026-05-26

> Diagnostic-only. Does **not** approve any strategy.
> `configs/approved_strategies.yaml` remains `approved: []`.

## Context

CAMPAIGN_015 remains an unapproved research candidate:

| metric | value |
|---|---:|
| base exp_r | +0.2300 |
| 2x-cost exp_r | +0.1909 |
| trades | 164 (< 200 gate) |
| folds_pass | 0/8 |
| matched null | ROBUST_ABOVE_NULL |
| interpretation | SPARSE_BUT_PROMISING |

After window alignment, entry-bar policy alignment, and read-only RiskEngine parity:

| lane | trades |
|---|---:|
| BT prior fold-window | 532 |
| BT RiskEngine/fill parity | **416** |
| Bespoke rehydrate | **164** |

Classification remains **`SIGNAL_RULE_MISMATCH`**. All 56 fold×pair cells have BT ≥ bespoke.

## Phase 0 — truth audit

### Branch / worktree

- Current branch: `infra-backtrader-campaign-015-cell-parity-drilldown-001`
- Forked from: `infra-backtrader-campaign-015-riskengine-and-fill-parity-001`

### Safety gates verified

- [x] `configs/approved_strategies.yaml` → `approved: []`
- [x] Research freeze gate passes (paper/demo/live refusal intact)
- [x] RiskEngine/fill parity artifacts present under
      `research/campaign_015/diagnostics/backtrader_fold_window_riskengine_fill_parity/`
- [x] Bespoke rehydrate artifacts present under
      `research/campaign_015/diagnostics/walk_forward_rehydrate/`
- [x] Comparison: `SIGNAL_RULE_MISMATCH`, 416 BT vs 164 bespoke

### Cell ranking (extra BT trades, preferred pairs)

Ranked by `delta` for AUD_USD, NZD_USD, GBP_USD:

| rank | fold | pair | bespoke | BT | delta |
|---:|---:|---|---:|---:|---:|
| 1 | 6 | GBP_USD | 1 | 16 | +15 |
| 2 | 1 | AUD_USD | 2 | 13 | +11 |
| 2 | 2 | AUD_USD | 2 | 13 | +11 |
| 4 | 3 | NZD_USD | 2 | 11 | +9 |
| 5 | 2 | NZD_USD | 1 | 8 | +7 |

### Target cell selected

**fold 1 × AUD_USD**

Rationale:

- Tied for largest **AUD_USD** per-fold drift (+11 extra BT trades).
- Only **2 bespoke accepted trades** → small, traceable bespoke baseline.
- **13 BT trades** → moderate trace window (not fold 6 GBP_USD with 16 BT / 1 bespoke).
- AUD_USD is the largest **pair-level** drift contributor (+64 total).

## Phases

| phase | deliverable |
|---|---|
| 0 | This plan + validation commands |
| 1 | `scripts/diff_campaign_015_cell_trades.py` + tests |
| 2 | `scripts/trace_campaign_015_cell_bar_decisions.py` + bar trace around first BT-only trade |
| 3 | Root-cause classification doc |
| 4 | Fix design doc (no broad implementation) |
| 5 | Summary + final validation |

## Hard rules (unchanged)

- No strategy approval, tuning, or promotion.
- No paper/demo/live enablement.
- No OANDA / broker API calls.
- No frozen CAMPAIGN_015 setting changes.
- No bespoke evidence manipulation.
- No broad fixes until root cause proven on one cell.

## Validation commands (each phase)

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```

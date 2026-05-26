# CAMPAIGN_015 Cell Parity Drilldown 001 — Summary

**Branch:** `infra-backtrader-campaign-015-cell-parity-drilldown-001`
**Date:** 2026-05-26
**Verdict:** Root cause proven; no parity fix shipped

## Target cell

**fold 1 × AUD_USD** — largest AUD_USD per-fold drift (+11), only 2 bespoke trades (manageable trace).

## Commits by phase

| phase | scope |
|---:|---|
| 0 | Plan doc + Phase 0 validation |
| 1 | `scripts/diff_campaign_015_cell_trades.py` + tests |
| 2 | `scripts/trace_campaign_015_cell_bar_decisions.py` + tests + bar trace artifacts |
| 3 | Root-cause classification doc |
| 4 | Fix design doc (no implementation) |
| 5 | This summary + final validation |

## Key findings

| item | result |
|---|---|
| Bespoke trades | 2 |
| BT parity trades | 13 |
| First BT-only | `2022-05-06T17:00:00+00:00` long |
| Raw signals match? | **No** (CSV long vs SQLite none at signal bar) |
| RiskEngine match? | **N/A** at first BT-only (bespoke no signal) |
| Data/spread match? | **Mostly**; duplicate SQLite rows dominate |
| Position/re-entry match? | **Yes** at first BT-only (`flat`) |
| Root cause | **`CSV_SQLITE_DATA_MISMATCH`** (+ secondary test-window counting) |
| Proposed fix | Dedupe SQLite candles at load (`keep='last'`) — **not implemented** |

## Safety

- CAMPAIGN_015: **unapproved**
- `configs/approved_strategies.yaml`: **`approved: []`**
- Paper / demo / live: **blocked**
- No broker API calls; no frozen setting changes

## Validation (Phase 5)

```text
pytest tests/ -q          → pass
ruff check …              → pass
check_research_freeze     → pass
validate_research_archive → pass
scan_artifacts_for_secrets → pass
```

## Files to review first

1. `docs/research/BACKTRADER_CAMPAIGN_015_CELL_PARITY_ROOT_CAUSE.md`
2. `research/campaign_015/diagnostics/cell_parity_drilldown/fold_01_AUD_USD_trade_diff.md`
3. `research/campaign_015/diagnostics/cell_parity_drilldown/fold_01_AUD_USD_bar_trace.json` (see `2022-05-06T13:00:00+00:00`)
4. `scripts/diff_campaign_015_cell_trades.py`
5. `scripts/trace_campaign_015_cell_bar_decisions.py`
6. `docs/research/BACKTRADER_CAMPAIGN_015_CELL_PARITY_FIX_DESIGN.md`

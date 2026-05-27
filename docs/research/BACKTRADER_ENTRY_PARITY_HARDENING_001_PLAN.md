# Backtrader Entry Parity Hardening 001 — Plan

**Branch:** `infra-backtrader-entry-parity-hardening-001`  
**Date:** 2026-05-27  
**Evidence class:** `parity_diagnostic_only` — `strategy_evidence: false`

---

## Purpose

Formally land the Backtrader **quote→USD PnL conversion** fix discovered in entry-orchestration diagnostics, refresh C008/C009/C018 parity artifacts, and establish the independent Backtrader lane as **viable within ±1 trade tolerance** for these campaigns.

---

## Non-goals

- CAMPAIGN_019, new strategy family, campaign runs, strategy approval
- Paper/demo/live, orders, OANDA mutations, tuning C008/C009/C018
- Test lockbox, profitability claims, bespoke engine changes

---

## Root cause

Backtrader lane `_pnl()` treated JPY/CAD/CHF quote PnL as USD → inflated drawdown → `DRAWDOWN_LIMIT` blocked ~20% of entries (primarily USD_JPY).

---

## Fix being formalized

1. **`research/backtrader_exit_parity/pnl.py`** — home-currency conversion matching `BacktestEngine._pnl`
2. **Default `risk_window_mode=engine_aligned`** — calendar Monday-week realized PnL windows
3. **Regression tests** for USD-quote and USD-base pairs

---

## Campaigns covered

C008, C009, C018 — deduped H4 train/validation only.

---

## Tolerance target

**±1 trade** per campaign vs bespoke deduped forensic replay.

---

## Local-only rules

- `data/campaign_002.sqlite3` deduped candles
- `approved: []` preserved
- All campaign verdicts unchanged

---

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/run_backtrader_exit_parity.py
python scripts/run_entry_parity_diagnostics.py
```

---

## Expected artifacts

| Artifact | Purpose |
|---|---|
| `research/backtrader_exit_parity/c008|c009|c018_parity_summary.json` | Refreshed BT aggregates |
| `research/backtrader_exit_parity/exit_reason_comparison.csv` | Exit-reason side-by-side |
| `research/backtrader_exit_parity/parity_run_manifest.json` | Run metadata |
| `research/entry_parity/entry_timestamp_comparison.json` | Entry gap post-hardening |
| `docs/research/BACKTRADER_PARITY_HARDENED_STATUS.md` | Final parity decision |

---

## Phase 0 truth audit

| Check | Status |
|---|---|
| Entry orchestration sprint artifacts | Present |
| PnL fix in `strategy.py` | Present (to be formalized in `pnl.py`) |
| `approved: []` | Confirmed |
| CAMPAIGN_019 | Does not exist |
| Paper/demo/live | Blocked |

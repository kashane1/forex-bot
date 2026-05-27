# Exit Hypothesis Precommit 002 — Plan

**Branch:** `research-exit-hypothesis-precommit-002`  
**Date:** 2026-05-27  
**Evidence class:** `precommit_design_only` — `strategy_evidence: false`

---

## Purpose

Pre-register **exactly one** next exit hypothesis after CAMPAIGN_018 REJECT, supported by
hardened Backtrader parity evidence and deduped C008/C009/C018 diagnostics. Design only —
no execution.

---

## Non-goals

- Execute CAMPAIGN_019 or any backtest
- Approve any strategy; enable paper/demo/live
- Retune C008/C009/C018 parameters
- Open test lockbox
- Call OANDA APIs or use live credentials
- Optimize from validation winners

---

## Source evidence

| artifact | role |
|---|---|
| [`BACKTRADER_ENTRY_PARITY_HARDENING_001_SUMMARY.md`](BACKTRADER_ENTRY_PARITY_HARDENING_001_SUMMARY.md) | ±1 trade parity; exit CLOSE_MATCH |
| [`BACKTRADER_PARITY_HARDENED_STATUS.md`](BACKTRADER_PARITY_HARDENED_STATUS.md) | Independent lane viable C008/C009/C018 |
| [`CAMPAIGN_018_FINAL_INTERPRETATION.md`](CAMPAIGN_018_FINAL_INTERPRETATION.md) | C018 REJECT; +1R break-even falsified on train |
| [`CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_SUMMARY.md`](CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_SUMMARY.md) | Gate table, mechanism rates |
| [`STOP_DISTANCE_AND_ADVERSE_EXCURSION_DIAGNOSTICS.md`](STOP_DISTANCE_AND_ADVERSE_EXCURSION_DIAGNOSTICS.md) | 41–47% stops never +1R; 53–60% +1R then stopped |
| [`C008_C009_C018_FINANCING_EXPOSURE_DIAGNOSTIC.md`](C008_C009_C018_FINANCING_EXPOSURE_DIAGNOSTIC.md) | Financing drag on multi-day holds |
| [`EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md`](EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md) | Prior precommit (C018 scope) |

---

## Candidate hypothesis classes

1. **Entry-invalidation exit** — exit when mean-reversion thesis fails (z-score continuation), not on profit threshold.
2. **Volatility-decay / early failure-to-revert** — exit if no favorable excursion within fixed early window.
3. **Delayed trailing after larger R** — profit-triggered (C018 family; high retune risk).
4. **No further exit hypothesis** — stop exit family; pursue financing or entry-quality research.

---

## Hard rules

| rule | enforcement |
|---|---|
| No-run | CAMPAIGN_019 docs only; zero `backtests/CAMPAIGN_019*` |
| No-retune | Frozen C008 entry, 1.5× ATR stop, 40-bar time stop |
| No-approval | `approved: []` unchanged |
| strategy_evidence | false for all sprint outputs |

---

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```

---

## Expected deliverables

| phase | artifact |
|---|---|
| 0 | this plan |
| 1 | `CAMPAIGN_018_FAILURE_ANALYSIS_FOR_NEXT_EXIT_HYPOTHESIS.md` |
| 2 | `EXIT_HYPOTHESIS_PRECOMMIT_002_SELECTION_MEMO.md` |
| 3 | `CAMPAIGN_019_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md` |
| 4 | `CAMPAIGN_019_EXIT_HYPOTHESIS_GATE_DESIGN.md` |
| 5 | implementation design + execution prompt |
| 6 | archive/backlog updates |
| 7 | `EXIT_HYPOTHESIS_PRECOMMIT_002_SUMMARY.md` |

---

## Phase 0 truth audit

| check | status |
|---|---|
| Backtrader hardened artifacts | Present |
| C018 execution artifacts | Present |
| Financing diagnostics | Present |
| `approved: []` | Confirmed |
| CAMPAIGN_019 backtest outputs | None |
| Paper/demo/live | Blocked |

# Entry Orchestration Parity Diagnostics 001 — Plan

**Branch:** `infra-entry-orchestration-parity-diagnostics-001`  
**Date:** 2026-05-27  
**Evidence class:** `parity_diagnostic_only` — `strategy_evidence: false`

---

## Purpose

Explain the ~20–25% trade-count gap between bespoke `BacktestEngine` and the Backtrader exit-parity lane for C008/C009/C018. Exit-reason shares already matched; this sprint isolates **entry / RiskEngine / orchestration** causes.

---

## Non-goals

- CAMPAIGN_019, new strategy family, campaign runs, strategy approval
- Paper/demo/live, orders, OANDA mutations, tuning C008/C009/C018
- Test lockbox, profitability claims

---

## Source artifacts

| Artifact | Role |
|---|---|
| [`BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_SUMMARY.md`](BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_SUMMARY.md) | Prior exit-parity close-out |
| [`research/backtrader_exit_parity/*_parity_trades.jsonl`](../research/backtrader_exit_parity/) | Backtrader entries |
| `backtests/CAMPAIGN_*_deduped_forensic/` | Bespoke trades + risk rejections |
| [`research/campaign_018/gate_result.json`](../research/campaign_018/gate_result.json) | C018 verdict (unchanged) |

---

## Suspected divergence causes (pre-registered)

1. RiskEngine realized PnL window mismatch (legacy BT rolling 7-day vs calendar week)
2. Drawdown peak computation drift
3. **PnL home-currency conversion missing for USD_JPY / USD_CAD** (non-USD quote)
4. Session/spread filter timing
5. Warmup / dedupe / fill-timing differences
6. Same-bar re-entry / position blocking

---

## Diagnostic plan

| Phase | Deliverable |
|---|---|
| 0 | This plan + truth audit |
| 1 | Timestamp-level entry comparison JSON/CSV |
| 2 | Risk/filter attribution JSON |
| 3 | Backtrader adjustment experiment (risk windows + PnL fix) |
| 4 | Parity decision doc |
| 5 | Archive/backlog updates |
| 6 | 19-item summary |

---

## Local-only rules

- Deduped `data/campaign_002.sqlite3` only
- No broker APIs; `approved: []` preserved
- Diagnostic instrumentation only — no campaign rule changes

---

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/run_entry_parity_diagnostics.py
```

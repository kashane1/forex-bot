# Entry Orchestration Parity Diagnostics 001 — Summary

**Branch:** `infra-entry-orchestration-parity-diagnostics-001`  
**Date:** 2026-05-27  
**Evidence class:** `parity_diagnostic_only` — `strategy_evidence: false`

---

## 1. Branch name

`infra-entry-orchestration-parity-diagnostics-001`

---

## 2. Commit hashes by phase

| Phase | Commit |
|---|---|
| 0 | *(phase 0 commit)* |
| 1 | *(phase 1 commit)* |
| 2 | *(phase 2 commit)* |
| 3 | *(phase 3 commit)* |
| 4 | *(phase 4 commit)* |
| 5 | *(phase 5 commit)* |
| 6 | *(this commit)* |

---

## 3. Files changed by phase

| Phase | Key paths |
|---|---|
| 0 | `docs/research/ENTRY_ORCHESTRATION_PARITY_DIAGNOSTICS_001_PLAN.md` |
| 1 | `research/entry_parity/compare_entries.py`, `load_trades.py`, `entry_timestamp_comparison.{json,csv}` |
| 2 | `research/entry_parity/risk_attribution.py`, `risk_filter_attribution.json` |
| 3 | `research/backtrader_exit_parity/strategy.py` (PnL fix), `risk_windows.py`, `adjustment_experiment.py`, `backtrader_adjustment_experiment.json` |
| 4 | `docs/research/ENTRY_ORCHESTRATION_PARITY_DECISION.md` |
| 5 | `EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`, `FUTURE_RESEARCH_BACKLOG.md` |
| 6 | This summary |

---

## 4. Entry timestamp comparison result

**100% of Backtrader entries were a subset of bespoke** (prior broken lane). Common entries have **identical entry and exit timestamps**. Bespoke-only: 75/71/64 trades (C008/C009/C018). **Zero Backtrader-only entries.**

Primary pair gap: **USD_JPY** (59 of 75 C008 bespoke-only trades).

---

## 5. Risk/filter attribution result

**BACKTRADER_IMPLEMENTATION_GAP** — `_pnl()` omitted quote→USD conversion for USD_JPY and USD_CAD. JPY losses recorded as USD inflated drawdown → **DRAWDOWN_LIMIT** (71 rejections on USD_JPY train). Spread/session filters ruled out as primary cause.

---

## 6. Backtrader adjustment experiment result

| Profile | C008 delta | C009 delta | C018 delta |
|---|---:|---:|---:|
| legacy_bt_wrong_pnl | 75 (21%) | 71 (18%) | 64 (17%) |
| fixed_pnl_engine_aligned | **1 (0.3%)** | **1 (0.3%)** | **1 (0.3%)** |

---

## 7. Final divergence classification

**BACKTRADER_IMPLEMENTATION_GAP** (resolved in diagnostic code; hardening sprint recommended to land formally).

---

## 8. Custom engine bug suspected?

**No.** Bespoke entry orchestration is trustworthy.

---

## 9. Backtrader implementation gap suspected?

**Yes — confirmed and fixed in branch.** Missing home-currency PnL conversion.

---

## 10. Exit parity remains valid?

**Yes.** Exit shares matched before fix; matched trades had identical exits.

---

## 11. Full campaign parity limited?

**Was limited; now viable** after PnL fix (±1 trade residual).

---

## 12. Campaign verdict changed?

**No.**

---

## 13. Strategy approved?

**No.** `approved: []`.

---

## 14. CAMPAIGN_019 created?

**No.**

---

## 15. Paper/demo/live blocked?

**Yes.**

---

## 16. Archive/freeze validation

| Check | Result |
|---|---|
| pytest | **1701 passed** |
| ruff | **PASS** |
| research freeze | **PASS** |
| archive validation | **PASS** |
| secret scan | **PASS** |

---

## 17. Remaining blockers

- Land PnL fix in Backtrader lane formally (hardening sprint)
- Refresh exit-parity JSON artifacts post-fix
- Financing manual sample paused
- Broad search paused; all campaigns REJECT

---

## 18. Recommended next sprint

**`infra-backtrader-entry-parity-hardening-001`** — land PnL fix, refresh artifacts, confirm ±1 tolerance, then `research-exit-hypothesis-precommit-002`.

---

## 19. Files to review first

1. [`docs/research/ENTRY_ORCHESTRATION_PARITY_DECISION.md`](ENTRY_ORCHESTRATION_PARITY_DECISION.md)
2. [`docs/research/BACKTRADER_ENTRY_PARITY_ADJUSTMENT_EXPERIMENT.md`](BACKTRADER_ENTRY_PARITY_ADJUSTMENT_EXPERIMENT.md)
3. [`research/entry_parity/backtrader_adjustment_experiment.json`](../../research/entry_parity/backtrader_adjustment_experiment.json)
4. [`research/backtrader_exit_parity/strategy.py`](../../research/backtrader_exit_parity/strategy.py) (`_pnl` fix)
5. [`docs/research/ENTRY_TIMESTAMP_PARITY_COMPARISON.md`](ENTRY_TIMESTAMP_PARITY_COMPARISON.md)

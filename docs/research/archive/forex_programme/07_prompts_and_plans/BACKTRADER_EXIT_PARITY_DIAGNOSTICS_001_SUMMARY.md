# Backtrader Exit Parity Diagnostics 001 — Summary

**Branch:** `infra-backtrader-exit-parity-diagnostics-001`  
**Date:** 2026-05-27  
**Evidence class:** `parity_diagnostic_only` — `strategy_evidence: false`

---

## 1. Branch name

`infra-backtrader-exit-parity-diagnostics-001`

---

## 2. Commit hashes by phase

| Phase | Commit | Description |
|---|---|---|
| 0 | `68d9449` | Plan + truth audit |
| 1 | `f1fc0d5` | Scaffold + fixture tests |
| 2 | `f1fc0d5` | Parity replay outputs (same commit as Phase 1) |
| 3 | `ad56bbd` | Divergence analysis |
| 4 | `1f4748d` | Status + next sprint |
| 5 | `27cc212` | Archive/backlog updates |
| 6 | *(this commit)* | Final summary |

---

## 3. Files changed by phase

| Phase | Key paths |
|---|---|
| 0 | `docs/research/BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_PLAN.md` |
| 1 | `research/backtrader_exit_parity/{constants,data_feed,exit_logic,strategy,runner,compare}.py`, `scripts/run_backtrader_exit_parity.py`, `tests/unit/backtrader_exit_parity/test_exit_fixtures.py` |
| 2 | `research/backtrader_exit_parity/c008_parity_summary.json`, `c009_parity_summary.json`, `c018_parity_summary.json`, `exit_reason_comparison.csv`, `*_parity_trades.jsonl` |
| 3 | `docs/research/BACKTRADER_EXIT_PARITY_DIVERGENCE_ANALYSIS.md` |
| 4 | `docs/research/BACKTRADER_EXIT_PARITY_STATUS.md` |
| 5 | `docs/research/EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`, `FUTURE_RESEARCH_BACKLOG.md` |
| 6 | `docs/research/BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_SUMMARY.md` |

---

## 4. Backtrader used or blocked?

**Used.** Backtrader **1.9.78.123** via `backtrader-lane` extra. Full C008/C009/C018 replay completed (~340 s).

---

## 5. C008 parity result

| Split | Bespoke trades | BT trades | Stop share (B/BT) | Time share (B/BT) |
|---|---:|---:|---|---|
| train | 216 | 165 | 70.8% / 73.9% | 28.7% / 25.5% |
| validation | 138 | 114 | 63.8% / 63.2% | 36.2% / 36.8% |

**Exit shares: CLOSE_MATCH.** Stop/time sign split **persists**. Trade counts: **MATERIAL_DIVERGENCE**.

---

## 6. C009 parity result

| Split | Bespoke trades | BT trades | Target share (B/BT) | Stop share (B/BT) |
|---|---:|---:|---|---|
| train | 252 | 207 | 38.5% / 36.7% | 59.9% / 61.4% |
| validation | 151 | 125 | 45.0% / 45.6% | 50.3% / 48.8% |

**Exit shares: CLOSE_MATCH.** Midline target capping **persists**. Trade counts: **MATERIAL_DIVERGENCE**.

---

## 7. C018 parity result

| Split | Bespoke trades | BT trades | Protective share (B/BT) | Stop share (B/BT) |
|---|---:|---:|---|---|
| train | 236 | 197 | 37.3% / 36.6% | 48.7% / 51.3% |
| validation | 142 | 117 | 40.1% / 41.0% | 41.6% / 39.3% |

**Exit shares: CLOSE_MATCH.** Protective-stop exit mix **persists**. Trade counts: **MATERIAL_DIVERGENCE**.

---

## 8. Exit-reason distribution comparison

See [`research/backtrader_exit_parity/exit_reason_comparison.csv`](../../research/backtrader_exit_parity/exit_reason_comparison.csv). Max share delta across all splits/reasons: **3.3 pp** (C008 train time). Dominant pathology direction matches bespoke on all campaigns.

---

## 9. Divergence classification

| Campaign | Exit shares | Trade counts |
|---|---|---|
| C008 | CLOSE_MATCH | MATERIAL_DIVERGENCE |
| C009 | CLOSE_MATCH | MATERIAL_DIVERGENCE |
| C018 | CLOSE_MATCH | MATERIAL_DIVERGENCE |

Primary cause: **entry / RiskEngine orchestration in Backtrader loop** (not exit precedence).

---

## 10. Custom engine bug suspected?

**No** for exit behavior. Independent `exit_logic` reproduces stop/time/target/protective distributions. Trade-count gap does not implicate bespoke exit precedence.

---

## 11. Campaign verdict changed?

**No.** C008/C009/C018 remain REJECT.

---

## 12. Strategy approved?

**No.** `configs/approved_strategies.yaml` → `approved: []`.

---

## 13. CAMPAIGN_019 created?

**No.**

---

## 14. Paper/demo/live blocked?

**Yes.** Research freeze gate PASS; no orders placed; manual financing sample **paused**.

---

## 15. Archive/freeze validation results

| Check | Result |
|---|---|
| `pytest tests/ -q` | **1696 passed** |
| `ruff check src tests scripts research` | **PASS** |
| `python scripts/check_research_freeze.py` | **PASS** |
| `python scripts/validate_research_archive.py` | **PASS** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASS** |

---

## 16. Remaining blockers

- Trade-count parity not achieved (~20–25% fewer BT entries) — entry pipeline follow-up if full trade-list parity required
- Manual overnight financing sample **paused** — observed financing remains empty
- Broad strategy search **paused** — no new candidate discovery
- All campaigns **REJECT** — no approval path

---

## 17. Recommended next sprint

**`research-exit-hypothesis-precommit-002`** — exit pathology corroborated at distribution level; financing blocked without manual sample; no exit bug signal for `infra-engine-exit-bug-investigation-001`.

---

## 18. Files to review first

1. [`docs/research/BACKTRADER_EXIT_PARITY_STATUS.md`](BACKTRADER_EXIT_PARITY_STATUS.md)
2. [`docs/research/BACKTRADER_EXIT_PARITY_DIVERGENCE_ANALYSIS.md`](BACKTRADER_EXIT_PARITY_DIVERGENCE_ANALYSIS.md)
3. [`research/backtrader_exit_parity/exit_reason_comparison.csv`](../../research/backtrader_exit_parity/exit_reason_comparison.csv)
4. [`research/backtrader_exit_parity/exit_logic.py`](../../research/backtrader_exit_parity/exit_logic.py)
5. [`docs/research/BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_PLAN.md`](BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_PLAN.md)

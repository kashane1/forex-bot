# CAMPAIGN_018 Protective Stop — Execution Sprint Plan

**Date:** 2026-05-27  
**Branch:** `research-campaign-018-protective-stop-execution-001`  
**Sprint ID:** `CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001`  
**Prior sprint:** `research-exit-hypothesis-precommit-001`

> **Precommitted research execution** — not approval. Follow precommit docs exactly.

---

## Purpose

Implement and run **CAMPAIGN_018** (`mean_reversion_protective_stop 0.1.0-c018`) testing hypothesis **`delayed_reversion_protective_stop_after_1R`** on deduped H4 inputs. Evaluate precommitted gates; open test lockbox only if screening passes.

---

## Source precommit docs

| document | role |
|---|---|
| [`EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md`](EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md) | Sprint context |
| [`EXIT_HYPOTHESIS_SELECTION_MEMO.md`](EXIT_HYPOTHESIS_SELECTION_MEMO.md) | Hypothesis rationale |
| [`CAMPAIGN_018_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md`](CAMPAIGN_018_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md) | Frozen scope |
| [`CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md`](CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md) | Gates |
| [`CAMPAIGN_018_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md`](CAMPAIGN_018_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md) | Implementation plan |
| [`NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT.md`](NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT.md) | Phase checklist |

---

## Exact frozen scope

**Entries:** identical to C008 (ADX<20, z±2.0 + RSI, 6 pairs, 0.25% risk, session/spread filters).

**Exit:** initial stop 1.5× ATR-14; no target; 40-bar time stop; on first MFE ≥ +1.0R move stop to entry (break-even); no ratchet.

**Splits:** train 2020–2022, validation 2023–2024, test 2025–2026 (conditional).

**Data:** deduped `oanda-practice` H4 from `data/campaign_002.sqlite3`.

---

## Non-goals

No retuning, no approval, no paper/demo/live, no executor/broker changes, no OANDA API calls, no gate changes after results.

---

## Safety rules

- `configs/approved_strategies.yaml` stays `approved: []`
- `strategy_evidence: true` on campaign artifacts; `not_approved: true`
- Bulky trade CSVs gitignored
- BLOCKED_PRECOMMIT_AMBIGUITY if implementation cannot match precommit

---

## Gate plan

Screening G1–G9 (+ G10–G12 validation gates). Test T1–T4 only if screening passes. Verdict ceiling REVISE / RESEARCH_PASS — not approved.

---

## Test lockbox rule

Open **only if** all precommitted train/validation unlock gates pass. Otherwise document `CAMPAIGN_018_TEST_LOCKBOX_NOT_OPENED.md`.

---

## Expected artifacts

| path | content |
|---|---|
| `research/campaign_018/*.json` | compact metrics, gates, comparisons (committed) |
| `backtests/CAMPAIGN_018_mean_reversion_protective_stop/` | trade CSVs (gitignored) |
| `docs/research/CAMPAIGN_018_*` | human reports |

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

## Blocked conditions

- Precommit ambiguity unresolved
- Dedupe preflight failure
- Missing SQLite data store
- Protective mechanism inert (<5% arm rate) due to implementation bug

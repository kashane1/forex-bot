# Exit Hypothesis Precommit Sprint — Plan

**Date:** 2026-05-27  
**Branch:** `research-exit-hypothesis-precommit-001`  
**Sprint ID:** `EXIT_HYPOTHESIS_PRECOMMIT_001`  
**Prior sprint:** `infra-deduped-c008-c009-rerun-forensic-only-001`

> **Precommit / design only** — `strategy_evidence: false`. **No backtest. No approval.**

---

## Purpose

Pre-register **exactly one** future exit-research campaign (proposed **CAMPAIGN_018**) based on deduped C008/C009 forensic findings. The campaign will test whether a protective stop transition after objective +1R favorable excursion can reduce hard-stop giveback **without** imposing a fixed profit target that caps the delayed-reversion tail (as C009 midline target did).

This sprint produces written precommit artifacts only. It does **not** execute CAMPAIGN_018.

---

## Non-goals

| non-goal | reason |
|---|---|
| Run CAMPAIGN_018 or any backtest | execution is a separate future sprint |
| Open test lockbox 2025–2026 | requires passing train + validation gates first |
| Approve any strategy | all campaigns remain REJECT until separate promotion review |
| Retune C008/C009 | historical artifacts frozen |
| Create backtest output folders | precommit docs only |
| Enable paper/demo/live | order-capable loops remain blocked |
| Modify executor/broker | no code changes in this sprint |
| Call OANDA order APIs | research-only |
| Optimize parameters from validation winners | forbidden by exit research gate |
| Revive C009 midline target | falsified rescue hypothesis |

---

## Source evidence

### Deduped forensic replay (confirmed)

| document | role |
|---|---|
| [`DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_SUMMARY.md`](DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_SUMMARY.md) | Sprint close-out |
| [`C008_C009_EVIDENCE_INTEGRITY_DECISION.md`](C008_C009_EVIDENCE_INTEGRITY_DECISION.md) | Integrity ruling |
| [`C008_C009_OLD_VS_DEDUPED_COMPARISON.md`](C008_C009_OLD_VS_DEDUPED_COMPARISON.md) | Metric comparison |
| [`C008_C009_DEDUPED_FORENSIC_REPLAY_RESULTS.md`](C008_C009_DEDUPED_FORENSIC_REPLAY_RESULTS.md) | Replay execution |
| [`C008_C009_DEDUPED_EXIT_ANATOMY.md`](C008_C009_DEDUPED_EXIT_ANATOMY.md) | Exit reason breakdown |
| [`C008_C009_DEDUPED_MAE_MFE_DIAGNOSTICS.md`](C008_C009_DEDUPED_MAE_MFE_DIAGNOSTICS.md) | MAE/MFE refresh |
| [`research/deduped_c008_c009_rerun/frozen_config_reconstruction.json`](../../research/deduped_c008_c009_rerun/frozen_config_reconstruction.json) | Frozen C008/C009 rules |

### Prior exit diagnostics

| document | role |
|---|---|
| [`FUTURE_EXIT_RESEARCH_HYPOTHESES.md`](FUTURE_EXIT_RESEARCH_HYPOTHESES.md) | Allowed hypothesis catalog (A1–A7) |
| [`FUTURE_EXIT_RESEARCH_GATE.md`](FUTURE_EXIT_RESEARCH_GATE.md) | Exit research gate requirements |
| [`CROSS_CAMPAIGN_EXIT_PATHOLOGY_MATRIX.md`](CROSS_CAMPAIGN_EXIT_PATHOLOGY_MATRIX.md) | Framework-wide exit context |

---

## Selected hypothesis candidates (for Phase 1 selection)

| ID | hypothesis class | notes |
|---|---|---|
| **A7 (preferred)** | Break-even / protective stop after +1R favorable excursion | Directly addresses 60% of C008 stops that reached ≥1R before stopping; preserves no-target time tail |
| A1 | Volatility-scaled stop redesign | Changes initial stop geometry — closer to stop retune |
| A2 | Regime-dependent time stop | Adds FRED bucket complexity; harder to isolate single exit change |
| A3 | Counter-signal exit | New mechanism; less directly tied to favorable-then-stopped population |
| A4 | ATR trail after favorable excursion | Similar to A7 but trail offset adds parameters |
| A5 | Partial exit + runner bundle | Two-leg bundle; C009 partial leg already falsified midline |
| A6 | No-target invalidation-only | Equivalent to C008 baseline — no new information |
| **Rejected** | C009 midline target | Already falsified; caps winner tail at ~1.18R |

Phase 1 will select **exactly one** hypothesis with written justification.

---

## No-run rule

- No `backtests/CAMPAIGN_018*` output directories created in this sprint.
- No strategy config files for CAMPAIGN_018 committed (design doc only).
- No SQLite queries for trade generation.
- No changes to `configs/approved_strategies.yaml`.

---

## No-retune rule

- Entry rules derived from C008 frozen config — not re-optimized.
- Exit change is **one pre-declared mechanism** (protective stop after +1R), not a sweep of thresholds.
- The +1R threshold is an **objective R-multiple** (standard risk unit), not chosen to maximize prior fold metrics.

---

## No-approval rule

- All sprint outputs: `strategy_evidence: false`, `precommit_only: true`.
- C008/C009 verdicts remain **REJECT / research-only**.
- Passing future CAMPAIGN_018 gates would permit **further research or separate promotion review** — not automatic approval.

---

## Expected deliverables

| phase | deliverable |
|---|---|
| 0 | This plan |
| 1 | [`EXIT_HYPOTHESIS_SELECTION_MEMO.md`](EXIT_HYPOTHESIS_SELECTION_MEMO.md) |
| 2 | [`CAMPAIGN_018_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md`](CAMPAIGN_018_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md) |
| 3 | [`CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md`](CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md) |
| 4 | [`CAMPAIGN_018_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md`](CAMPAIGN_018_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md) |
| 5 | [`NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT.md`](NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT.md) |
| 6 | Archive updates (EVIDENCE_INDEX, FUTURE_RESEARCH_BACKLOG, EVIDENCE_MANIFEST) |
| 7 | [`EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md`](EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md) |

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

## Truth audit (Phase 0)

| check | status |
|---|---|
| Branch | `research-exit-hypothesis-precommit-001` from `infra-deduped-c008-c009-rerun-forensic-only-001` |
| Deduped forensic artifacts | present |
| Exit diagnostic artifacts | present |
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_018 backtest outputs | none (expected) |
| Paper/demo loops | refuse without approved registry |
| Validation suite | run at phase close |

# CAMPAIGN_011 Deduped Null-Baseline Promotion — Plan

**Sprint:** CAMPAIGN_011_DEDUPED_NULL_BASELINE_001  
**Branch:** `research-campaign-011-deduped-null-baseline-001`  
**Base:** `research-campaign-contamination-audit-001`  
**Date:** 2026-05-26

## Goal

Promote the deduped CAMPAIGN_011 random-entry anchor as the **canonical null reference** for post-dedupe evidence comparisons. This is an evidence-integrity sprint only — not strategy approval, not tuning, not paper/demo/live enablement.

## Hard rules (binding)

| rule | status at plan time |
|---|---|
| No strategy approval | `configs/approved_strategies.yaml` → `approved: []` |
| No OANDA / broker API calls | enforced |
| No CAMPAIGN_011 tuning or seed changes | frozen config unchanged |
| No bulky per-trade CSV/JSONL in git | rollups only |
| Annotate superseded contaminated null docs | required |
| CAMPAIGN_012–014 comparisons pending re-eval | after promotion |

## Phase 0 — truth audit

### Branch / worktree

| check | result |
|---|---|
| Sprint branch | `research-campaign-011-deduped-null-baseline-001` (from contamination-audit base) |
| Unrelated dirty files | `research/backtrader_lane/fold_windows.py`, `research/lean_parity/.../main.py` — **out of sprint scope** |

### Evidence integrity prerequisites

| check | result |
|---|---|
| `CandleRepo.list` dedupes at load (`dedupe_candles`, `keep_last`) | **PASS** — `src/forex_bot/data/repositories.py` |
| Contamination audit docs | **PASS** — `CAMPAIGN_CONTAMINATION_AUDIT_001_*` |
| CAMPAIGN_011 classification | **NULL_BASELINE_REQUIRES_RERUN** |
| Local deduped run | **PRESENT** — `backtests/CAMPAIGN_011_random_entry_anchor_deduped/` |
| `approved: []` | **PASS** |
| Paper/demo/live blocked | **PASS** — research freeze `loops_refuse` |

### Validation commands (baseline)

| command | result |
|---|---|
| `pytest tests/ -q` (excl. backtrader + trace_015 import) | **1346 passed** |
| `ruff check src tests scripts research` | **11 pre-existing UP042** (not sprint-introduced) |
| `check_research_freeze.py` | **ALL PASS** |
| `validate_research_archive.py` | **ALL PASS** |
| `scan_artifacts_for_secrets.py` | **PASSED** |

## Phase plan

| phase | deliverable | commit scope |
|---:|---|---|
| 0 | This plan | doc only |
| 1 | `CAMPAIGN_011_DEDUPED_RUN_VERIFICATION.md` | doc only; local deduped dir inspected, not trade CSVs |
| 2 | `scripts/promote_campaign_011_deduped_null_baseline.py`, `research/null_baselines/*`, tests | compact canonical rollup |
| 3 | Supersession doc; code/doc pointer updates to canonical JSON | no silent metric rewrite |
| 4 | `EVIDENCE_INDEX`, `EVIDENCE_MANIFEST`, `STRATEGY_STATUS`, `POST_DEDUP_RERUN_BACKLOG` | manifest metrics → deduped |
| 5 | `CAMPAIGN_015_VS_DEDUPED_NULL_CHECK.md` | anti-overfit vs deduped null |
| 6 | `CAMPAIGN_011_DEDUPED_NULL_BASELINE_001_SUMMARY.md` | final validation |

## Canonical artifact target

```
research/null_baselines/campaign_011_deduped_null_baseline.json
research/null_baselines/campaign_011_deduped_null_baseline.md
docs/research/CAMPAIGN_011_DEDUPED_NULL_BASELINE.md
```

## Superseded sources (retain, annotate)

- `backtests/CAMPAIGN_011_random_entry_anchor/` — LIKELY_CONTAMINATED headline metrics
- `docs/research/CAMPAIGN_011_WALK_FORWARD_RESULT.md` — pre-fix numbers
- `docs/research/CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md` §1 — superseded for numeric floor; binding protocol retained

## Out of scope

- CAMPAIGN_012–014 reruns
- Financing overlay re-run for deduped CAMPAIGN_011
- Strategy approval or registry edits

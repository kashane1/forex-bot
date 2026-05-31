# Broad Strategy Pause and Roadmap — Sprint 001 Plan

**Date:** 2026-05-26  
**Branch:** `research-broad-strategy-pause-and-roadmap-001`  
**Base branch:** `research-post-dedup-failure-meta-analysis-001`  
**Sprint type:** Research closeout and roadmap — **not** strategy implementation, tuning, or paper/demo/live enablement.

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_018 will **not** be created.

---

## 0. Goal

Formally pause broad seven-pair pattern strategy campaigns after post-dedup failure meta-analysis, document strict re-entry gates for future strategy research, compare non-strategy workstream options, and select exactly one next non-strategy sprint (default: observed cost and spread-regime diagnostics).

This sprint produces **documentation, registry updates, and a next-sprint prompt only**. It does not approve strategies, tune rejected campaigns, or enable trading loops.

---

## 1. Phase 0 — truth audit (this document)

### 1.1 Branch / worktree

| dimension | value |
|---|---|
| branch | `research-broad-strategy-pause-and-roadmap-001` |
| created from | `research-post-dedup-failure-meta-analysis-001` |
| sprint scope | pause memo + archive updates + non-strategy roadmap |

### 1.2 Evidence integrity checks

| check | status | path / note |
|---|---|---|
| CAMPAIGN_011 deduped null baseline | **PASS** | `research/null_baselines/campaign_011_deduped_null_baseline.json` — exp_r = −0.002915, trades = 1,180 |
| CAMPAIGN_015 deduped REJECT | **PASS** | `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/gate_result.json` — REJECT, DEDUPED_INPUT, exp_r = −0.0101 |
| CAMPAIGN_016 deduped REJECT | **PASS** | `backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/walk_forward/gate_result.json` — REJECT, DEDUPED_INPUT, exp_r = −0.0633 |
| CAMPAIGN_017 deduped REJECT | **PASS** | `backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/walk_forward/gate_result.json` — REJECT, DEDUPED_INPUT, exp_r = −0.0227 |
| Post-dedup meta-analysis docs | **PASS** | `docs/research/POST_DEDUP_FAILURE_META_ANALYSIS_001_SUMMARY.md`, `POST_DEDUP_CAMPAIGN_METRIC_MATRIX.md`, `POST_DEDUP_ARCHETYPE_ANALYSIS.md`, `POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md` |
| Meta-analysis machine artifacts | **PASS** | `research/post_dedup_meta/campaign_metric_matrix.json`, `research/post_dedup_meta/archetype_analysis.json` |
| `configs/approved_strategies.yaml` | **PASS** | `approved: []` |
| paper / demo / live refusal | **PASS** | `scripts/check_research_freeze.py` — loops refuse |

### 1.3 Post-dedup meta-analysis headline (inputs to pause)

| campaign | role | base exp_r | gap vs null | trades | anti-overfit |
|---|---|---:|---:|---:|---|
| CAMPAIGN_011 | deduped null | −0.0029 | 0 | 1,180 | n/a |
| CAMPAIGN_015 | REJECT | −0.0101 | −0.0072 | 375 | WITHIN_NULL |
| CAMPAIGN_016 | REJECT | −0.0633 | −0.0604 | 137 | WITHIN_NULL |
| CAMPAIGN_017 | REJECT | −0.0227 | −0.0198 | 230 | WITHIN_NULL |

Classification from prior sprint: **NO_RELIABLE_ARCHETYPE**. Selected lane: **pause broad strategy search**.

### 1.4 Baseline validation (Phase 0)

| check | result |
|---|---|
| `pytest tests/ -q` | **1565 passed** |
| `ruff check src tests scripts research` | **All checks passed** (after fixing post-dedup script lint from prior sprint) |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** |

### 1.5 Hard rules (all phases)

- Do not approve any strategy or edit `configs/approved_strategies.yaml` beyond confirming `approved: []`.
- Do not enable paper / demo / live.
- Do not create CAMPAIGN_018 or any new backtest campaign.
- Do not tune CAMPAIGN_015, CAMPAIGN_016, or CAMPAIGN_017.
- Do not call OANDA or broker APIs.
- Do not commit `.env`, credentials, SQLite DBs, or bulky trade dumps.
- Do not present exploratory hints as tradable edge.

---

## 2. Phase plan

| phase | deliverable | commit |
|---:|---|---|
| 0 | This plan + truth audit | yes |
| 1 | `BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md` | yes |
| 2 | Update `STRATEGY_STATUS.md`, `EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`, `POST_DEDUP_RERUN_BACKLOG.md`, `FUTURE_RESEARCH_BACKLOG.md` | yes |
| 3 | `NON_STRATEGY_WORKSTREAM_OPTIONS_AFTER_PAUSE.md` | yes |
| 4 | `NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md` | yes |
| 5 | `NEXT_SPRINT_PROMPT_AFTER_BROAD_STRATEGY_PAUSE.md` | yes |
| 6 | `BROAD_STRATEGY_PAUSE_AND_ROADMAP_001_SUMMARY.md` + final validation | yes |

---

## 3. Expected outcomes

- Broad seven-pair pattern strategy search is **formally paused** with documented re-entry gates.
- Next sprint: **`infra-observed-cost-and-spread-regime-diagnostics-001`** (local bid/ask H4 diagnostics; no strategy; no broker APIs).
- CAMPAIGN_018: **not created**.
- Strategies: **none approved**.
- Trading loops: **remain blocked**.

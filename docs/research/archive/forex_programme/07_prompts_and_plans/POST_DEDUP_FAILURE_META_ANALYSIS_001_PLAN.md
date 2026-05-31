# Post-Dedup Failure Meta-Analysis — Sprint 001 Plan

**Date:** 2026-05-26  
**Branch:** `research-post-dedup-failure-meta-analysis-001`  
**Base branch:** `research-weekly-volatility-contraction-breakout-001`  
**Sprint type:** Research meta-analysis and lab-selection — **not** strategy implementation, tuning, or paper/demo/live enablement.

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_018 will **not** be created in this sprint.

---

## 0. Goal

Analyze dedup-safe evidence from CAMPAIGN_015, CAMPAIGN_016, and CAMPAIGN_017 (with CAMPAIGN_011 deduped null baseline) to decide whether the next research move should be:

1. pair-specific research lab  
2. regime-specific research lab  
3. new broad CAMPAIGN_018 candidate discovery  
4. data expansion first  
5. financing / cost-modeling infrastructure  
6. pause broad pattern research  

This sprint produces **descriptive synthesis and a lane recommendation only**. It does not approve, tune, or re-run campaigns.

---

## 1. Phase 0 — truth audit (completed)

### 1.1 Branch / worktree

| dimension | value |
|---|---|
| branch | `research-post-dedup-failure-meta-analysis-001` |
| created from | `research-weekly-volatility-contraction-breakout-001` |
| sprint scope | meta-analysis + lab selection only |

### 1.2 Evidence integrity checks

| check | status | path / note |
|---|---|---|
| `CandleRepo.list` dedupe | **PASS** | `src/forex_bot/data/repositories.py` — `list()` calls `dedupe_candles()` and stores `last_list_dedupe_stats` |
| CAMPAIGN_011 deduped null baseline | **PASS** | `research/null_baselines/campaign_011_deduped_null_baseline.json` — aggregate exp_r = −0.002915, trades = 1,180 |
| CAMPAIGN_015 deduped canonical | **PASS** | `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/gate_result.json` — REJECT, DEDUPED_INPUT |
| CAMPAIGN_016 deduped canonical | **PASS** | `backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/walk_forward/gate_result.json` — REJECT, DEDUPED_INPUT |
| CAMPAIGN_017 deduped canonical | **PASS** | `backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/walk_forward/gate_result.json` — REJECT, DEDUPED_INPUT |
| `configs/approved_strategies.yaml` | **PASS** | `approved: []` |
| paper / demo / live refusal | **PASS** | `scripts/check_research_freeze.py` — loops refuse |

### 1.3 Baseline validation results

| check | result |
|---|---|
| `pytest tests/ -q` | **1560 passed** |
| `ruff check src tests scripts research` | **All checks passed** |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** (pattern scan; value scan skipped — no live credentials in env) |

### 1.4 Dedup-safe campaign snapshot (headline)

| campaign | strategy | verdict | base exp_r | 2x exp_r | trades | fold pass | anti-overfit | Backtrader |
|---|---|---|---:|---:|---:|---:|---|---|
| CAMPAIGN_011 (null) | random_entry_anchor | REJECT (null) | −0.0029 | n/a | 1,180 | 0/8 | n/a | n/a |
| CAMPAIGN_015 | failed_breakout_reversal | REJECT | −0.0101 | −0.0283 | 375 | 2/8 | WITHIN_NULL | TOLERABLE_DRIFT |
| CAMPAIGN_016 | weekly_cross_sectional_momentum | REJECT | −0.0633 | −0.0719 | 137 | 3/8 | WITHIN_NULL | BLOCKED (non-decision-blocking) |
| CAMPAIGN_017 | weekly_volatility_contraction_breakout | REJECT | −0.0227 | −0.0283 | 230 | 3/8 | WITHIN_NULL | BLOCKED (non-decision-blocking) |

**No strategy is approved.** All three candidate campaigns are WITHIN_NULL on the deduped CAMPAIGN_011 baseline.

---

## 2. Sprint phases

| phase | deliverable | commit |
|---|---|---|
| 0 | This plan + truth audit | yes |
| 1 | `scripts/collect_post_dedup_campaign_metrics.py` + metric matrix JSON/MD | yes |
| 2 | `scripts/analyze_post_dedup_archetypes.py` + archetype analysis JSON/MD | yes |
| 3 | `docs/research/POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md` — exactly one lane | yes |
| 4 | `docs/research/NEXT_SPRINT_PROMPT_AFTER_POST_DEDUP_META.md` | yes |
| 5 | Final validation + `POST_DEDUP_FAILURE_META_ANALYSIS_001_SUMMARY.md` | yes |

---

## 3. Hard rules (non-negotiable)

- Do **not** approve any strategy or edit `configs/approved_strategies.yaml`.
- Do **not** enable paper / demo / live.
- Do **not** call OANDA or broker APIs.
- Do **not** tune CAMPAIGN_015, 016, or 017.
- Do **not** create CAMPAIGN_018.
- Do **not** present exploratory findings as tradable edge.
- Do **not** use pre-dedup / contaminated metrics as positive evidence.
- Do **not** commit `.env`, credentials, SQLite DBs, or bulky trade dumps.
- If local trade CSVs are missing, emit `PARTIAL` / `BLOCKED` for that section and continue with JSON summaries.

---

## 4. Inputs (canonical paths)

| artifact | path |
|---|---|
| Null baseline | `research/null_baselines/campaign_011_deduped_null_baseline.json` |
| C015 gate | `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/gate_result.json` |
| C015 fold detail | `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/fold_detail.json` |
| C016 gate | `backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/walk_forward/gate_result.json` |
| C016 fold detail | `backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/walk_forward/fold_detail.json` |
| C017 gate | `backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/walk_forward/gate_result.json` |
| C017 fold detail | `backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/walk_forward/fold_detail.json` |
| Per-fold/per-pair summaries | `backtests/CAMPAIGN_0{15,16,17}_*/folds/base/fold_**/*_summary.json` (when present) |
| Trade CSVs | same tree `*_trades.csv` (optional; not required for commit) |

---

## 5. Outputs

| output | path |
|---|---|
| Metric matrix (machine) | `research/post_dedup_meta/campaign_metric_matrix.json` |
| Metric matrix (human) | `research/post_dedup_meta/campaign_metric_matrix.md` |
| Metric matrix (docs) | `docs/research/POST_DEDUP_CAMPAIGN_METRIC_MATRIX.md` |
| Archetype analysis (machine) | `research/post_dedup_meta/archetype_analysis.json` |
| Archetype analysis (human) | `research/post_dedup_meta/archetype_analysis.md` |
| Archetype analysis (docs) | `docs/research/POST_DEDUP_ARCHETYPE_ANALYSIS.md` |
| Lane decision | `docs/research/POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md` |
| Next sprint prompt | `docs/research/NEXT_SPRINT_PROMPT_AFTER_POST_DEDUP_META.md` |
| Sprint summary | `docs/research/POST_DEDUP_FAILURE_META_ANALYSIS_001_SUMMARY.md` |

---

## 6. Decision framework (Phase 3 preview)

The lane decision will weigh:

- Phase 1/2 evidence (pair / fold / side / exit / cost sensitivity)
- Overfitting risk — exploratory cells must not drive campaign creation
- Trade count sufficiency — C016 at 137 trades is sparse for cell-level claims
- Falsifiability — chosen lane must have pre-declared pass/fail criteria
- Financing dependency — MODELED financing remains refused
- Backtrader verifiability — C016/C017 BT parity deferred
- Contamination avoidance — deduped paths only
- No retuning of rejected campaigns

Expected lean: if no reliable archetype survives null-band scrutiny, prefer **pause broad strategy search** or **data expansion** over another broad CAMPAIGN_018.

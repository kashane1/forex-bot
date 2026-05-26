# New Candidate Strategy Discovery (Deduped) — Sprint Plan

**Sprint:** NEW_CANDIDATE_DISCOVERY_DEDUPED_001  
**Branch:** `research-new-candidate-strategy-discovery-deduped-001`  
**Base branch:** `research-post-dedup-null-reference-refresh-001`  
**Date:** 2026-05-26

## Purpose

Choose the next **structurally distinct** strategy candidate to implement on
deduped canonical data. This is a **docs-only candidate-discovery sprint** —
not strategy approval, tuning, paper/demo/live enablement, or implementation.

## Phase 0 truth audit (this document)

### Branch / worktree

| check | status |
|---|---|
| Target branch | `research-new-candidate-strategy-discovery-deduped-001` |
| Created from | `research-post-dedup-null-reference-refresh-001` |
| HEAD | `8e43749` (post-dedup null reference refresh close-out) |

### Dedupe fix (verified)

| check | status |
|---|---|
| `src/forex_bot/data/candle_dedupe.py` | **EXISTS** — `dedupe_candles()`, policy `keep_last` |
| `CandleRepo.list` calls dedupe | **VERIFIED** — `repositories.py` L214–216 |
| Dedupe fix commit referenced in null baseline | `30b4654` (provenance in canonical JSON) |

### CAMPAIGN_011 deduped null baseline (verified)

| artifact | path | status |
|---|---|---|
| Machine rollup | `research/null_baselines/campaign_011_deduped_null_baseline.json` | **EXISTS, canonical** |
| Deduped backtest input | `backtests/CAMPAIGN_011_random_entry_anchor_deduped/` | **EXISTS (local)** |

**Headline metrics:**

| metric | value |
|---|---:|
| aggregate trades | 1,180 |
| aggregate expectancy R | −0.0029154071495408797 |
| per-fold expectancy mean / std | −0.0027 / 0.0479 |
| aggregate return % | −0.68 |
| profit factor | 0.89 |
| verdict | REJECT (null model) |

### CAMPAIGN_015 deduped rerun (verified REJECT)

| artifact | path | status |
|---|---|---|
| Deduped walk-forward | `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/results.json` | **EXISTS (local)** |
| Null / anti-overfit doc | `docs/research/CAMPAIGN_015_DEDUPED_NULL_AND_ANTI_OVERFIT.md` | **EXISTS** |
| Backtrader comparison | `docs/research/BACKTRADER_CAMPAIGN_015_DEDUPED_COMPARISON.md` | **EXISTS** |

**Headline metrics (deduped):**

| metric | base | 2× cost |
|---|---:|---:|
| aggregate expectancy R | −0.0101 | −0.0283 |
| total trades | 375 | — |
| fold pass | 2 / 8 | — |
| anti-overfit | WITHIN_NULL | — |
| Backtrader comparison | TOLERABLE_DRIFT | — |
| verdict | **REJECT** | **REJECT** |

### Post-dedup null refresh for CAMPAIGN_012–014 (verified)

| campaign | doc | gap vs deduped null | verdict |
|---|---|---:|---|
| CAMPAIGN_012 | `docs/research/CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md` | −0.0492 R | REJECT (unchanged) |
| CAMPAIGN_013 | `docs/research/CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md` | −0.0535 R | REJECT (unchanged) |
| CAMPAIGN_014 | `docs/research/CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md` | −0.1448 R | REJECT (unchanged) |

Campaign walk-forward metrics remain **LIKELY_CONTAMINATED** (pre-fix SQLite);
null-relative conclusions are far below null and not decision-critical.

### Safety invariants (verified)

| check | status |
|---|---|
| `configs/approved_strategies.yaml` → `approved: []` | **VERIFIED** |
| No strategy approved | **VERIFIED** |
| Paper / demo / live blocked (`STRATEGY_STATUS.md`) | **VERIFIED** |
| CAMPAIGN_002–010 archived/rejected | **VERIFIED** |
| CAMPAIGN_015 revival blocked | **VERIFIED** |

### Validation commands (Phase 0)

| command | result |
|---|---|
| `pytest tests/ -q` | **1509 passed** |
| `ruff check src tests scripts research` | **PASS** |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** |

## Phases

### Phase 1 — Post-dedup evidence map

Create `docs/research/POST_DEDUP_EVIDENCE_MAP.md`:

- Dedup-safe vs contaminated/archival evidence
- Retired strategy families
- Open families (if any)
- New null baseline and future-candidate constraints

### Phase 2 — Candidate universe and ranking

Create `docs/research/DEDUPED_CANDIDATE_UNIVERSE.md`:

- 4–6 structurally distinct candidates
- Thesis, blockers, risks, ranking table

### Phase 3 — Select one next candidate

Create `docs/research/NEXT_CANDIDATE_SELECTION_DEDUPED_001.md`:

- Exactly one candidate for next implementation sprint
- Default: `weekly_cross_sectional_momentum_low_turnover` unless evidence review disagrees

### Phase 4 — CAMPAIGN_016 precommit draft

Create `docs/research/CAMPAIGN_016_PRECOMMIT_DRAFT.md`:

- Draft only — not implementation
- Gates, blocked conditions, null comparison plan, Backtrader plan

### Phase 5 — Final validation and summary

Create `docs/research/NEW_CANDIDATE_DISCOVERY_DEDUPED_001_SUMMARY.md`.

Re-run all validation commands; verify no secrets, DBs, or bulky artifacts staged.

## Hard rules (binding)

- Do **not** approve any strategy.
- Do **not** add to `configs/approved_strategies.yaml`.
- Do **not** enable paper / demo / live.
- Do **not** run broker / OANDA calls.
- Do **not** tune old strategies or revive CAMPAIGN_015.
- Do **not** use contaminated historical metrics as positive evidence.
- Do **not** implement strategy code (small docs/test helpers only if absolutely necessary).
- Do **not** commit `.env`, credentials, SQLite DBs, or bulky artifacts.
- Label contaminated/archival evidence explicitly when referenced.

## Deliverables

| phase | artifact |
|---|---|
| 0 | This plan |
| 1 | `POST_DEDUP_EVIDENCE_MAP.md` |
| 2 | `DEDUPED_CANDIDATE_UNIVERSE.md` |
| 3 | `NEXT_CANDIDATE_SELECTION_DEDUPED_001.md` |
| 4 | `CAMPAIGN_016_PRECOMMIT_DRAFT.md` |
| 5 | `NEW_CANDIDATE_DISCOVERY_DEDUPED_001_SUMMARY.md` |

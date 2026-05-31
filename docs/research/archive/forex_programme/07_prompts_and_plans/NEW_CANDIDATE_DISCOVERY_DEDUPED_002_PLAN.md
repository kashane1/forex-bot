# New Candidate Strategy Discovery (Deduped) — Sprint Plan 002

**Sprint:** NEW_CANDIDATE_DISCOVERY_DEDUPED_002  
**Branch:** `research-new-candidate-strategy-discovery-deduped-002`  
**Base branch:** `research-weekly-cross-sectional-momentum-001`  
**Date:** 2026-05-26

## Purpose

Choose the next **structurally distinct** strategy candidate (CAMPAIGN_017)
after CAMPAIGN_016 **REJECT** on deduped canonical data. This is a **docs-only
candidate-discovery sprint** — not strategy approval, tuning, paper/demo/live
enablement, or implementation.

## Phase 0 truth audit (this document)

### Branch / worktree

| check | status |
|---|---|
| Target branch | `research-new-candidate-strategy-discovery-deduped-002` |
| Created from | `research-weekly-cross-sectional-momentum-001` |
| HEAD (Phase 0 open) | `96a531e` — CAMPAIGN_016 sprint summary and archive test |

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

**Headline metrics (deduped):**

| metric | base | 2× cost |
|---|---:|---:|
| aggregate expectancy R | −0.0101 | −0.0283 |
| total trades | 375 | — |
| fold pass | 2 / 8 | — |
| anti-overfit | WITHIN_NULL | — |
| Backtrader comparison | TOLERABLE_DRIFT | — |
| verdict | **REJECT** | **REJECT** |

### CAMPAIGN_016 deduped run (verified REJECT)

| artifact | path | status |
|---|---|---|
| Walk-forward result | `docs/research/CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_RESULT.md` | **EXISTS** |
| Sprint summary | `docs/research/CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_001_SUMMARY.md` | **EXISTS** |
| Null / anti-overfit | `docs/research/CAMPAIGN_016_NULL_AND_ANTI_OVERFIT.md` | **EXISTS** |
| Gate artifacts | `backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/walk_forward/gate_result.json` | **EXISTS (local)** |

**Headline metrics (deduped):**

| metric | base | 2× cost |
|---|---:|---:|
| aggregate expectancy R | **−0.0633** | **−0.0719** |
| total trades | **137** | 137 |
| fold pass | **3 / 8** | 3 / 8 |
| pairs positive | **4 / 7** | — |
| anti-overfit | **WITHIN_NULL** | — |
| gap vs deduped null | **−0.0604 R** | — |
| Backtrader | **BLOCKED** (non-decision-blocking; boundary parity only) | — |
| verdict | **REJECT** | **REJECT** |

Deduped input: 138,522 duplicate H4 rows dropped (`keep_last`).

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
| Paper / demo / live blocked (`check_research_freeze.py` loops_refuse) | **VERIFIED** |
| CAMPAIGN_002–010 archived/rejected | **VERIFIED** |
| CAMPAIGN_015 revival blocked | **VERIFIED** |
| CAMPAIGN_016 retune blocked | **VERIFIED** (this sprint selects fresh candidate) |

### Validation commands (Phase 0)

| command | result |
|---|---|
| `pytest tests/ -q` | **1532 passed** |
| `ruff check src tests scripts research` | **1 pre-existing I001** in `tests/unit/backtrader_lane/test_campaign_016_weekly_cross_sectional_momentum.py` (import sort; not introduced by this sprint) |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** |

## Phases

### Phase 1 — Post-dedup evidence map (002)

Create `docs/research/POST_DEDUP_EVIDENCE_MAP_002.md`:

- CAMPAIGN_011 deduped null baseline
- CAMPAIGN_015 deduped REJECT
- CAMPAIGN_016 deduped REJECT
- Retired families (including weekly cross-sectional momentum)
- Remaining open hypothesis space
- Why cross-sectional momentum is now lower priority
- Constraints for CAMPAIGN_017

### Phase 2 — Candidate universe refresh

Create `docs/research/DEDUPED_CANDIDATE_UNIVERSE_002.md`:

- 4–6 structurally distinct candidates (post-C016)
- Thesis, blockers, risks, ranking table

### Phase 3 — Select CAMPAIGN_017

Create `docs/research/NEXT_CANDIDATE_SELECTION_DEDUPED_002.md`:

- Select exactly one candidate for CAMPAIGN_017

### Phase 4 — CAMPAIGN_017 precommit draft

Create `docs/research/CAMPAIGN_017_PRECOMMIT_DRAFT.md`:

- Frozen hypothesis and parameters (draft only, not implementation)

### Phase 5 — Final validation and summary

Create `docs/research/NEW_CANDIDATE_DISCOVERY_DEDUPED_002_SUMMARY.md`

## Hard rules (binding for entire sprint)

- Do **not** approve any strategy.
- Do **not** add to `configs/approved_strategies.yaml`.
- Do **not** enable paper / demo / live.
- Do **not** call OANDA or broker APIs.
- Do **not** tune CAMPAIGN_016.
- Do **not** revive CAMPAIGN_015.
- Do **not** use contaminated historical metrics as positive evidence.
- Do **not** implement strategy code.
- Do **not** commit `.env`, credentials, SQLite DBs, or bulky artifacts.

## Expected outcome

CAMPAIGN_017 candidate selected and precommit drafted. No strategy code.
No approval. Paper / demo / live remain blocked.

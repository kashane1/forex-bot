# Post-Dedup Null Reference Refresh — Sprint Plan

**Sprint:** POST_DEDUP_NULL_REFERENCE_REFRESH_001  
**Branch:** `research-post-dedup-null-reference-refresh-001`  
**Base branch:** `research-campaign-011-deduped-null-baseline-001`  
**Date:** 2026-05-25

## Purpose

Refresh CAMPAIGN_012–014 null-comparison references so they point to the
canonical deduped CAMPAIGN_011 null baseline, and determine whether their
existing conclusions materially change. This is a **docs/evidence-reference
cleanup sprint** — not strategy approval, tuning, or paper/demo/live enablement.

## Canonical null baseline (verified)

| artifact | path |
|---|---|
| Machine rollup | [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json) |
| Rollup markdown | [`research/null_baselines/campaign_011_deduped_null_baseline.md`](../../research/null_baselines/campaign_011_deduped_null_baseline.md) |
| Supersession record | [`CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md`](CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md) |

**Deduped headline metrics:**

| metric | value |
|---|---:|
| aggregate trades | 1,180 |
| aggregate expectancy R | −0.0029154071495408797 |
| per-fold expectancy mean / std | −0.0027 / 0.0479 |
| aggregate return % | −0.68 |
| profit factor | 0.89 |
| verdict | REJECT (null model) |

## Superseded contaminated null (retain for history only)

| metric | contaminated (superseded) |
|---|---:|
| trades | 1,177 |
| expectancy R | −0.0024 |
| return % | −0.53 |
| profit factor | 0.91 |

## Phase 0 truth audit (this document)

### Branch / worktree

- Created `research-post-dedup-null-reference-refresh-001` from
  `research-campaign-011-deduped-null-baseline-001`.

### Verified artifacts

| check | status |
|---|---|
| `research/null_baselines/campaign_011_deduped_null_baseline.json` | **EXISTS** |
| `docs/research/CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md` | **EXISTS** |
| `research/contamination_audit/campaign_integrity_classification.json` | **EXISTS** |
| `configs/approved_strategies.yaml` → `approved: []` | **VERIFIED** |
| Paper / demo / live refusal (`STRATEGY_STATUS.md`) | **VERIFIED** |

### Validation commands (Phase 0)

| command | result |
|---|---|
| `pytest tests/ -q` | **1505 passed** |
| `ruff check src tests scripts research` | **PASS** (7 pre-existing fixable issues auto-fixed) |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** |

## Phases

### Phase 1 — Inventory null references

Create `scripts/find_campaign_null_references.py` to scan:

- `docs/research/`
- `research/campaign_*/`
- `backtests/`
- `EVIDENCE_INDEX.md`
- `EVIDENCE_MANIFEST.json`

Output:

- `research/contamination_audit/post_dedup_null_reference_inventory.json`
- `research/contamination_audit/post_dedup_null_reference_inventory.md`
- `docs/research/POST_DEDUP_NULL_REFERENCE_INVENTORY.md`

### Phase 2 — Refresh CAMPAIGN_012–014 null comparison notes

For each campaign, create:

- `docs/research/CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md`
- `docs/research/CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md`
- `docs/research/CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md`

Rules:

- Campaign metrics from pre-fix SQLite are **LIKELY_CONTAMINATED** — do not
  treat as validated post-dedup evidence.
- Recompute gap vs deduped null from existing compact rollups where possible.
- Annotate old null centre (−0.0024 R / 1,177 trades) as
  **SUPERSEDED_NULL_REFERENCE**.
- If conclusion unchanged, state explicitly.

### Phase 3 — Update evidence index / manifest / status

Update:

- `docs/research/EVIDENCE_INDEX.md`
- `docs/research/EVIDENCE_MANIFEST.json`
- `docs/research/STRATEGY_STATUS.md`
- `docs/research/POST_DEDUP_RERUN_BACKLOG.md`

### Phase 4 — Final summary and validation

Create `docs/research/POST_DEDUP_NULL_REFERENCE_REFRESH_001_SUMMARY.md`.

## Hard rules (binding)

- Do **not** approve any strategy.
- Do **not** add anything to `configs/approved_strategies.yaml`.
- Do **not** enable paper / demo / live.
- Do **not** call OANDA or broker APIs.
- Do **not** tune any strategy.
- Do **not** rerun full campaigns unless explicitly necessary and cheap.
- Do **not** silently rewrite old contaminated results.
- Do **not** commit `.env`, credentials, SQLite DBs, or bulky trade dumps.

## Expected outcome

- CAMPAIGN_012–014 conclusions likely remain **REJECT**; numeric old-null
  references are superseded.
- Full deduped reruns for CAMPAIGN_012–014 remain on the backlog for
  validated post-dedup rejection certification.

## References

- [`CAMPAIGN_011_DEDUPED_NULL_BASELINE_001_SUMMARY.md`](CAMPAIGN_011_DEDUPED_NULL_BASELINE_001_SUMMARY.md)
- [`CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md`](CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md)
- [`POST_DEDUP_RERUN_BACKLOG.md`](POST_DEDUP_RERUN_BACKLOG.md)

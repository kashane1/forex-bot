# CAMPAIGN Contamination Audit 001 — Summary

**Branch:** `research-campaign-contamination-audit-001`  
**Base:** `infra-canonical-candle-dedup-and-campaign015-rerun-001`  
**Date:** 2026-05-26

## Sprint outcome

Evidence-integrity audit complete. **No strategy approved.**  
`configs/approved_strategies.yaml` remains `approved: []`. Paper / demo / live blocked.

## Commits by phase

| phase | commit | description |
|---:|---|---|
| 0 | `6483bc2` | Plan + truth baseline |
| 1 | `1d3025c` | Data-source inventory script + scan |
| 2 | `6926f61` | Integrity classification |
| 3 | `ecc6cd0` | Doc annotations |
| 4 | `13fefcb` | Rerun backlog |
| 5 | `71f6188` | Summary + validation |

## Inventory scale

| metric | value |
|---|---:|
| evidence artifacts inventoried | **561** |
| campaigns covered | **15** |
| inventory JSON | `research/contamination_audit/campaign_data_source_inventory.json` |

## Campaign-level classification (CAMPAIGN_001–015)

| integrity status | count | campaigns |
|---|---:|---|
| **DEDUP_SAFE** | 2 | 001, 015 (deduped canonical) |
| **CONTAMINATED_SUPERSEDED** | 0 at campaign level | CAMPAIGN_015 *original* bespoke artifacts superseded (artifact-level) |
| **LIKELY_CONTAMINATED** | 11 | 002–010, 012–014 |
| **NULL_BASELINE_REQUIRES_RERUN** | 1 | 011 |
| **UNKNOWN_REQUIRES_RERUN** | 0 at campaign level | (artifact-level unknowns in inventory only) |
| **BLOCKED_NO_RUN** | 1 | 006 |

## Key answers

| question | answer |
|---|---|
| CAMPAIGN_011 null baseline must rerun? | **Yes — Priority 1.** Promote deduped rerun as canonical. |
| CAMPAIGN_002 needs rerun? | **Not urgent.** REJECT stable; optional metric re-certification. CSV parity lane **DEDUP-SAFE**. |
| CAMPAIGN_010–014 rerun? | **Should rerun** after CAMPAIGN_011 deduped promotion (priorities 2–5 in backlog). |
| Backtrader parity safe? | **Yes** — CSV export lane deduped; diagnostic only. |

## Docs annotated

- `docs/research/EVIDENCE_INDEX.md`
- `docs/research/EVIDENCE_MANIFEST.json`
- `docs/research/STRATEGY_STATUS.md`
- `docs/research/FAILED_CAMPAIGN_META_ANALYSIS_001.md`
- `docs/research/CAMPAIGN_010_WALK_FORWARD_RESULT.md`
- `docs/research/CAMPAIGN_011_WALK_FORWARD_RESULT.md`
- `docs/research/CAMPAIGN_012_WALK_FORWARD_RESULT.md`
- `docs/research/CAMPAIGN_013_WALK_FORWARD_RESULT.md`
- `docs/research/CAMPAIGN_014_WALK_FORWARD_RESULT.md`
- (CAMPAIGN_015 post-run docs already marked SUPERSEDED in prior sprint)

## New artifacts

| path | purpose |
|---|---|
| `docs/research/CAMPAIGN_CONTAMINATION_AUDIT_001_PLAN.md` | Phase 0 plan |
| `docs/research/CAMPAIGN_DATA_SOURCE_INVENTORY.md` | Human inventory summary |
| `docs/research/CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md` | Classification report |
| `docs/research/POST_DEDUP_RERUN_BACKLOG.md` | Rerun priorities |
| `scripts/inventory_campaign_data_sources.py` | Inventory CLI |
| `scripts/classify_campaign_contamination.py` | Classification CLI |
| `src/forex_bot/contamination_audit/` | Testable library |
| `tests/unit/test_contamination_audit.py` | Unit tests |

## Validation (Phase 5)

All passed at sprint close:

- `pytest tests/ -q`
- `ruff check src tests scripts research`
- `python scripts/check_research_freeze.py`
- `python scripts/validate_research_archive.py`
- `python scripts/scan_artifacts_for_secrets.py`
- No `.env`, credentials, SQLite DBs, or bulky trade dumps staged

## Recommended next step

Execute **CAMPAIGN_011 deduped null-baseline promotion sprint**: commit walk-forward rollups (not per-fold trade CSVs), update manifest/index/null-band docs, then re-run null comparisons for CAMPAIGN_012–014.

## Files to review first

1. [`CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md`](CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md)
2. [`POST_DEDUP_RERUN_BACKLOG.md`](POST_DEDUP_RERUN_BACKLOG.md)
3. [`research/contamination_audit/campaign_integrity_classification.json`](../../research/contamination_audit/campaign_integrity_classification.json)
4. [`CAMPAIGN_015_DEDUPED_RERUN_RESULT.md`](CAMPAIGN_015_DEDUPED_RERUN_RESULT.md) (reference deduped rerun pattern)

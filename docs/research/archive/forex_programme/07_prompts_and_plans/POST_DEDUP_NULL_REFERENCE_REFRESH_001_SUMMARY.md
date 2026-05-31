# Post-Dedup Null Reference Refresh — Sprint Summary

**Sprint:** POST_DEDUP_NULL_REFERENCE_REFRESH_001  
**Branch:** `research-post-dedup-null-reference-refresh-001`  
**Date:** 2026-05-25

## Objective

Refresh CAMPAIGN_012–014 null-comparison references to the canonical deduped
CAMPAIGN_011 null baseline and determine whether conclusions materially change.

## Canonical null baseline

| metric | deduped canonical |
|---|---:|
| path | `research/null_baselines/campaign_011_deduped_null_baseline.json` |
| aggregate trades | 1,180 |
| aggregate expectancy R | −0.0029154071495408797 |
| per-fold expectancy mean / std | −0.0027 / 0.0479 |
| aggregate return % | −0.68 |
| profit factor | 0.89 |
| verdict | REJECT (null model) |

## Scanner inventory (Phase 1)

| metric | count |
|---|---:|
| files scanned | 8,043 |
| files with matches | 487 |
| files with old null metrics (−0.0024 / 1,177 / etc.) | 173 |
| files referencing canonical null JSON | 21 |
| CAMPAIGN_012 mention files | 178 |
| CAMPAIGN_013 mention files | 135 |
| CAMPAIGN_014 mention files | 126 |

Inventory artifacts:

- `research/contamination_audit/post_dedup_null_reference_inventory.json`
- `research/contamination_audit/post_dedup_null_reference_inventory.md`
- `docs/research/POST_DEDUP_NULL_REFERENCE_INVENTORY.md`

## CAMPAIGN refresh results

### CAMPAIGN_012

| field | value |
|---|---|
| campaign expectancy R (pre-fix rollup) | −0.0521 |
| gap vs deduped null | −0.0492 R |
| prior verdict | REJECT |
| post-refresh verdict | **REJECT (unchanged)** |
| doc | [`CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md) |

### CAMPAIGN_013

| field | value |
|---|---|
| campaign expectancy R (pre-fix rollup) | −0.0564 |
| gap vs deduped null | −0.0535 R |
| prior verdict | REJECT |
| post-refresh verdict | **REJECT (unchanged)** |
| doc | [`CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md) |

### CAMPAIGN_014

| field | value |
|---|---|
| campaign expectancy R (pre-fix rollup) | −0.14774 |
| gap vs deduped null | −0.1448 R |
| prior verdict | REJECT (direction-of-trade falsification) |
| post-refresh verdict | **REJECT (unchanged)** |
| doc | [`CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md) |

## Conclusion change?

**No.** All three campaigns remain far outside the indistinguishability band
on the worse side. Shifting the null centre from −0.0024 R to −0.0029 R is
immaterial relative to campaign deficits of −0.05 R to −0.15 R.

## Full rerun required?

**Yes, for validated post-dedup rejection certification** — but not for
directional verdict. CAMPAIGN_012–014 walk-forward metrics remain
**LIKELY_CONTAMINATED** (pre-fix SQLite). This sprint updated null-reference
docs only; it did not rerun campaigns.

## Safety invariants (verified)

| check | status |
|---|---|
| `configs/approved_strategies.yaml` → `approved: []` | **PASS** |
| No strategy approved | **PASS** |
| Paper / demo / live blocked | **PASS** |
| No OANDA / broker API calls | **PASS** |
| No bulky trade dumps committed | **PASS** |
| `pytest tests/ -q` | **1509 passed** |
| `ruff check src tests scripts research` | **PASS** |
| `check_research_freeze.py` | **PASS** |
| `validate_research_archive.py` | **PASS** |
| `scan_artifacts_for_secrets.py` | **PASS** |

## CAMPAIGN_011 deduped null canonical everywhere?

**Partially.** Canonical JSON and supersession docs are authoritative. **173
files** still contain superseded null metric literals (−0.0024 / 1,177) for
historical reference; new comparisons must use deduped canonical centre. Primary
evidence index rows for CAMPAIGN_012–014 now point to post-dedup refresh docs.

## Recommended next step

Run optional **deduped walk-forward reruns** for CAMPAIGN_012–014 (Priority 2
in [`POST_DEDUP_RERUN_BACKLOG.md`](POST_DEDUP_RERUN_BACKLOG.md)) if validated
post-dedup rejection certification is needed before archive close-out.

## Files to review first

1. [`CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md)
2. [`CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md)
3. [`CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md)
4. [`POST_DEDUP_NULL_REFERENCE_INVENTORY.md`](POST_DEDUP_NULL_REFERENCE_INVENTORY.md)
5. [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)

## Commits by phase

| phase | scope |
|---|---|
| 0 | Plan + ruff fixes from prior sprint |
| 1 | Scanner, inventory, tests |
| 2 | CAMPAIGN_012–014 post-dedup null reference docs |
| 3 | EVIDENCE_INDEX, EVIDENCE_MANIFEST, STRATEGY_STATUS, rerun backlog |
| 4 | This summary + final validation |

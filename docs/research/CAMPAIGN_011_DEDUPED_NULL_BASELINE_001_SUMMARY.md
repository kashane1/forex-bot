# CAMPAIGN_011 Deduped Null-Baseline Promotion — Summary

**Branch:** `research-campaign-011-deduped-null-baseline-001`  
**Base:** `research-campaign-contamination-audit-001`  
**Date:** 2026-05-26

## Outcome

Deduped CAMPAIGN_011 random-entry anchor promoted to **canonical null baseline**. No strategy approved. Paper/demo/live remain blocked.

## CAMPAIGN_011 run

| item | value |
|---|---|
| Method | **Inspected** local `backtests/CAMPAIGN_011_random_entry_anchor_deduped/` (no rerun) |
| Deduped aggregate trades | **1,180** |
| Deduped aggregate expectancy R | **−0.0029** |
| Per-fold expectancy R mean / std | **−0.0027** / **0.0479** |
| Verdict | **REJECT** (unchanged) |

## Contaminated vs deduped

| metric | contaminated (superseded) | deduped canonical |
|---|---:|---:|
| trades | 1,177 | 1,180 |
| expectancy R | −0.0024 | −0.0029 |
| return % | −0.53 | −0.68 |
| profit_factor | 0.91 | 0.89 |

## Canonical path

`research/null_baselines/campaign_011_deduped_null_baseline.json`

## Committed (compact)

- `research/null_baselines/campaign_011_deduped_null_baseline.{json,md}`
- `scripts/promote_campaign_011_deduped_null_baseline.py`
- `tests/unit/test_campaign_011_deduped_null_baseline.py`
- Sprint docs under `docs/research/CAMPAIGN_011_DEDUPED_*`, `CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md`
- Manifest/index/status/backlog updates
- `.gitignore` for deduped `*_trades.csv`

## Local-only (not committed)

- `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/**/**_trades.csv`
- `backtests/CAMPAIGN_011_random_entry_anchor_deduped/walk_forward/fold_detail.json` (source only)

## Superseded docs (annotated, not deleted)

- `docs/research/CAMPAIGN_011_WALK_FORWARD_RESULT.md`
- `docs/research/CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md` §1 numbers
- `backtests/CAMPAIGN_011_random_entry_anchor/` artifact folder

## CAMPAIGN_015 check

| item | value |
|---|---|
| Ran vs deduped null? | **yes** |
| anti_overfit_label | **WITHIN_NULL** |
| CAMPAIGN_015 verdict | **REJECT** (unchanged) |

## Gates

| gate | status |
|---|---|
| `approved: []` | **yes** |
| Strategy approved | **no** |
| Paper/demo/live | **blocked** |

## Validation (close)

| check | result |
|---|---|
| pytest (excl. backtrader/trace_015) | 1346+ pass |
| research freeze | PASS |
| validate_research_archive | PASS |
| scan_artifacts_for_secrets | PASS |
| ruff | 11 pre-existing UP042 |

## Recommended next step

Re-evaluate CAMPAIGN_012–014 walk-forward null-comparison sections against `research/null_baselines/campaign_011_deduped_null_baseline.json` (verdicts likely stable; numeric gaps will shift).

## Review first

1. [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)
2. [`CAMPAIGN_011_DEDUPED_NULL_BASELINE.md`](CAMPAIGN_011_DEDUPED_NULL_BASELINE.md)
3. [`CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md`](CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md)
4. [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json) CAMPAIGN_011 entry

# CAMPAIGN Contamination Audit 001 — Plan

**Branch:** `research-campaign-contamination-audit-001`  
**Base:** `infra-canonical-candle-dedup-and-campaign015-rerun-001`  
**Date:** 2026-05-26  
**Sprint type:** evidence-integrity audit (NOT strategy / NOT tuning / NOT enablement)

> **No strategy is approved.** `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.

## Problem statement

A duplicate-candle defect was found in the local OANDA H4 SQLite store
(`data/campaign_002.sqlite3`): two rows per bar at the same UTC instant
with different ISO timezone strings. Backtrader CSV exports deduped at
export time; bespoke loads via `CandleRepo.list` did not dedupe until
commit `30b4654` (Phase 1 of the dedup sprint).

CAMPAIGN_015 bespoke evidence was **materially contaminated**:
contaminated base exp_r +0.2300 → deduped −0.0101; anti-overfit label
`ROBUST_ABOVE_NULL` → `WITHIN_NULL`. Prior CAMPAIGN_015 bespoke artifacts
are superseded by the deduped rerun.

This sprint audits **all** historical campaign artifacts and docs to
determine which results may be contaminated, which are dedup-safe, and
which require rerun or superseded annotation.

## Phase 0 — truth audit (this document)

### Branch / worktree verification

| check | result |
|---|---|
| branch | `research-campaign-contamination-audit-001` from `infra-canonical-candle-dedup-and-campaign015-rerun-001` |
| dedupe module | `src/forex_bot/data/candle_dedupe.py` — `keep_last` policy |
| `CandleRepo.list` dedupes | yes — calls `dedupe_candles` at load boundary |
| CAMPAIGN_015 deduped rerun | `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/` + `docs/research/CAMPAIGN_015_DEDUPED_RERUN_RESULT.md` |
| `approved_strategies.yaml` | `approved: []` |
| paper/demo/live | refused by freeze gate |

### Dedupe-fix commit metadata

| field | value |
|---|---|
| design doc | `9d0650f` |
| contamination memo | `cac03f3` |
| canonical dedupe implementation | `30b4654` |
| CAMPAIGN_015 deduped bespoke rerun | `d6c23a3` |
| deduped null/anti-overfit diagnostics | `7b7f734` |
| deduped Backtrader comparison | `dc7bc06` |
| evidence supersession docs | `388e285` |

### Validation baseline (Phase 0)

Run before and after sprint:

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```

## Phase 1 — inventory historical campaign artifacts

**Script:** `scripts/inventory_campaign_data_sources.py`

Scan:

- `docs/research/`
- `backtests/`
- `research/campaign_*/`
- `research/walk_forward/`
- `research/backtrader_lane/`
- `configs/campaign_*.yaml`
- `docs/research/EVIDENCE_INDEX.md`
- `docs/research/EVIDENCE_MANIFEST.json`

Outputs:

- `research/contamination_audit/campaign_data_source_inventory.json`
- `research/contamination_audit/campaign_data_source_inventory.md`
- `docs/research/CAMPAIGN_DATA_SOURCE_INVENTORY.md`

## Phase 2 — classify campaign evidence integrity

**Script:** `scripts/classify_campaign_contamination.py`

Inputs: Phase 1 inventory + dedupe-fix metadata + CAMPAIGN_015 rerun facts.

Classify CAMPAIGN_001–015 per campaign and artifact.

Outputs:

- `research/contamination_audit/campaign_integrity_classification.json`
- `research/contamination_audit/campaign_integrity_classification.md`
- `docs/research/CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md`

## Phase 3 — annotate docs (no history erasure)

Targets (as classified):

- `docs/research/STRATEGY_STATUS.md`
- `docs/research/EVIDENCE_INDEX.md`
- `docs/research/EVIDENCE_MANIFEST.json`
- `docs/research/FAILED_CAMPAIGN_META_ANALYSIS_001.md`
- CAMPAIGN_010–015 docs where affected
- CAMPAIGN_011 null-baseline docs where affected

Annotation tokens:

- `SUPERSEDED BY DEDUP AUDIT` — proven contaminated
- `EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE` — likely but unproven
- `DEDUP-SAFE` — post-fix or CSV-only / synthetic / diagnostic-only

## Phase 4 — rerun backlog

**Doc:** `docs/research/POST_DEDUP_RERUN_BACKLOG.md`

Rank reruns: must / should / archive-only / no rerun needed.

## Phase 5 — final validation and summary

**Doc:** `docs/research/CAMPAIGN_CONTAMINATION_AUDIT_001_SUMMARY.md`

Verify freeze, no secrets staged, no approval changes.

## Hard rules (non-negotiable)

1. Do not approve any strategy.
2. Do not add to `configs/approved_strategies.yaml`.
3. Do not enable paper / demo / live.
4. Do not call OANDA or broker APIs.
5. Do not tune strategies.
6. Do not rerun campaigns in this sprint unless explicitly scoped.
7. Do not silently rewrite history — annotate superseded / stale / unknown.
8. Do not commit `.env`, credentials, SQLite DBs, or bulky trade dumps.

## Contamination status vocabulary

| status | meaning |
|---|---|
| `DEDUP_SAFE` | Post-fix CandleRepo load, deduped rerun artifact, CSV export lane, or synthetic data |
| `CONTAMINATED_SUPERSEDED` | Proven contaminated; superseding deduped evidence exists |
| `LIKELY_CONTAMINATED` | Pre-fix bespoke SQLite path; no deduped rerun yet |
| `CSV_EXPORT_SAFE` | Backtrader / Lean CSV export path (deduped at export) |
| `BACKTRADER_ONLY_DIAGNOSTIC` | Parity lane; not strategy evidence |
| `BLOCKED_NO_RUN` | Campaign blocked / no valid bespoke run |
| `NULL_BASELINE_REQUIRES_RERUN` | Null-model anchor; contaminated baseline invalidates comparisons |
| `UNKNOWN_REQUIRES_RERUN` | Cannot classify from committed artifacts |

## Expected high-priority findings (hypotheses to verify)

1. **CAMPAIGN_011 null baseline** — pre-fix bespoke metrics (−0.0024 R, 1177 trades) likely contaminated; deduped rerun folder exists locally but may need formal promotion.
2. **CAMPAIGN_010–014 walk-forward** — all used `campaign_002.sqlite3` via CandleRepo pre-fix → likely contaminated; REJECT verdicts may still hold but null comparisons and magnitude claims need rerun or unknown annotation.
3. **CAMPAIGN_002–009 marathon era** — same SQLite path → likely contaminated; all REJECT; low rerun priority unless metrics used for active decisions.
4. **CAMPAIGN_015** — original bespoke superseded; deduped rerun is canonical.
5. **Backtrader parity** — CSV lane dedup-safe; diagnostic only.

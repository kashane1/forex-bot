# Stop and Exit Diagnostics — Sprint 001 Plan

**Date:** 2026-05-26  
**Branch:** `research-stop-and-exit-diagnostics-001`  
**Base branch:** `research-c008-mean-reversion-post-mortem-001`

> **Diagnostic only** — `strategy_evidence: false`. No strategy approved. No CAMPAIGN_018. Broad strategy search **paused**.

---

## Purpose

Investigate stop/exit pathology across existing rejected campaigns, with special focus on C008/C009 mean reversion, to determine whether exit mechanics are a structural failure mode and what future pre-registered exit research would require.

## Non-goals

- Approve any strategy or exit variant.
- Create CAMPAIGN_018 or any new strategy campaign.
- Retune C008/C009 (stops, time-stop length, targets, entries).
- Open test lockbox or enable paper/demo/live.
- Claim any exit is profitable.

## Source artifacts

### C008 post-mortem (verified)

- `docs/research/C008_MEAN_REVERSION_POST_MORTEM_001_SUMMARY.md`
- `docs/research/C008_C009_EVIDENCE_RECONSTRUCTION.md`
- `docs/research/C008_TRADE_ANATOMY_DIAGNOSTICS.md`
- `docs/research/C008_HUMAN_REVIEW_POST_MORTEM.md`
- `docs/research/FUTURE_MEAN_REVERSION_RESEARCH_GATE.md`
- `research/c008_post_mortem/c008_trade_anatomy.json`

### External data (verified)

- `research/cross_asset_features/normalized_features.csv`
- `research/cross_asset_features/h4_aligned_feature_availability.json`
- `research/confluence_diagnostics/confluence_diagnostic_summary_full_window_cross_asset.json`

### Campaign trade lists (local, gitignored)

C008, C009, C010–C017, C011 deduped, C015 deduped; C002–C007 if present.

## Evidence-integrity caveats

| status | campaigns | use |
|---|---|---|
| LIKELY_CONTAMINATED | C002–C004, C007–C014, C008, C009, C016, C017 | descriptive only, labeled |
| DEDUP_SAFE | C015 deduped | preferred for cross-campaign compare |
| SUPERSEDED / NULL | C011 (use deduped folder) | null baseline lane |
| BLOCKED | C006 | no trades |

Never mix contaminated and dedup-safe without labels.

## Diagnostic questions

1. Is C008 stop/time split unique or visible elsewhere?
2. Are hard stops too tight, badly placed, or revealing bad entries?
3. Are time exits delayed reversion or validation luck?
4. Did C009 fail because midline target capped winners?
5. What exit hypotheses are legitimate for future research?

## No-retune / no-approval rules

Frozen entries and exits for C008/C009. No parameter optimization from validation winners. All outputs `strategy_evidence: false`.

## Phase plan

| phase | deliverable |
|---:|---|
| 0 | This plan |
| 1 | `exit_artifact_inventory.json`, `EXIT_ARTIFACT_INVENTORY.md` |
| 2 | cross-campaign exit matrix JSON/CSV + doc |
| 3 | C008/C009 exit forensics JSON + doc |
| 4 | stop distance / MAE-MFE JSON + doc |
| 5 | `FUTURE_EXIT_RESEARCH_HYPOTHESES.md` |
| 6 | `FUTURE_EXIT_RESEARCH_GATE.md` |
| 7 | archive updates |
| 8 | summary + validation |

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/run_exit_diagnostics.py
git status --short
```

## Disclaimer

Diagnostic research only. Not strategy evidence.

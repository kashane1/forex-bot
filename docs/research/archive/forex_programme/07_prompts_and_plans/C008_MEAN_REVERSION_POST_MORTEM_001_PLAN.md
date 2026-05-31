# C008 Mean-Reversion Post-Mortem — Sprint 001 Plan

**Date:** 2026-05-26  
**Branch:** `research-c008-mean-reversion-post-mortem-001`  
**Base branch:** `infra-external-data-ingest-blocker-resolution-001`

> **Diagnostic post-mortem only** — `strategy_evidence: false`. No strategy approved. No CAMPAIGN_018. Broad strategy search remains **paused**.

---

## Purpose

Understand why `mean_reversion 0.1.0-c008` (CAMPAIGN_008) was the strongest positive clue in the research archive, why it failed its pre-committed train gate, and what evidence would be required before any future mean-reversion strategy research is allowed.

Use the newly ingested full-window FRED cross-asset features and MTF confluence framework **descriptively** — not to approve, retune, or claim edge.

## Non-goals

- Approve C008, C009, or any strategy.
- Create CAMPAIGN_018 or any new backtest campaign.
- Retune C008/C009 parameters, thresholds, or exits.
- Use validation/test winners to choose new parameters.
- Enable paper/demo/live or modify executor/broker behavior.
- Claim C008 is profitable or approved.
- Compute confluence-bucket profitability as a strategy claim.

## Safety rules

| rule | enforcement |
|---|---|
| `approved_strategies.yaml` | verify `approved: []` only |
| CAMPAIGN_018 | must not exist |
| paper/demo/live | freeze `loops_refuse` must pass |
| OANDA order APIs | no calls |
| Retuning | forbidden — read-only analysis of existing artifacts |
| Outputs | all `strategy_evidence: false` |

## Source artifacts

### Prior infra (verified)

- `docs/research/INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md`
- `research/cross_asset_features/normalized_features.csv`
- `research/cross_asset_features/h4_aligned_feature_availability.json`
- `research/confluence_diagnostics/confluence_diagnostic_summary_full_window_cross_asset.json`

### C008

- `docs/research/CAMPAIGN_008_RANGE_MEAN_REVERSION_PRECOMMIT.md`
- `docs/research/CAMPAIGN_008_HUMAN_REVIEW.md`
- `backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md`
- `configs/campaign_008_range_mean_reversion.yaml`
- `backtests/campaign_008_range_mean_reversion/runs/baseline/{train,validation}/*_summary.json`
- `backtests/campaign_008_range_mean_reversion/runs/baseline/{train,validation}/*_trades.csv` (local, gitignored)

### C009

- `docs/research/CAMPAIGN_009_PRECOMMIT.md`
- `backtests/CAMPAIGN_009_MEAN_REVERSION_REPORT.md`
- `configs/campaign_009_mean_reversion.yaml`
- `backtests/campaign_009_mean_reversion/runs/{train,validation}/base/*_summary.json`
- `backtests/campaign_009_mean_reversion/runs/{train,validation}/base/*_trades.csv` (local, gitignored)

## Diagnostic questions

1. What exact pre-committed gate did C008 fail? What did C009 fail?
2. How do train vs validation differ in trade anatomy (pair, session, exit, R distribution)?
3. Were validation winners concentrated in specific pairs/sessions/exits?
4. Did train losers vs validation winners differ in cost/spread or outlier concentration?
5. What cross-asset regime mix describes C008 train vs validation contexts?
6. Does MTF confluence grading explain the train/validation split descriptively?
7. Why is C008 a clue but not an approval?
8. What would a future mean-reversion campaign need pre-registered?

## No-retune rule

All analysis uses **frozen** C008/C009 rules and **existing** trade outputs. No parameter changes, no threshold optimization, no feature shopping for edge.

## No-approval rule

This sprint produces descriptive diagnostics and future gate requirements only. Verdicts remain **REJECT / research-only**.

## Phase plan

| phase | deliverable |
|---:|---|
| 0 | This plan + truth audit |
| 1 | `C008_C009_EVIDENCE_RECONSTRUCTION.md` |
| 2 | `c008_trade_anatomy.json` + `C008_TRADE_ANATOMY_DIAGNOSTICS.md` |
| 3 | `c008_cross_asset_regime_overlay.json` + `C008_CROSS_ASSET_REGIME_OVERLAY.md` |
| 4 | `c008_confluence_overlay.json` + `C008_CONFLUENCE_OVERLAY_DIAGNOSTIC.md` |
| 5 | `C008_HUMAN_REVIEW_POST_MORTEM.md` |
| 6 | `FUTURE_MEAN_REVERSION_RESEARCH_GATE.md` |
| 7 | Archive/backlog updates |
| 8 | Summary + final validation |

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/run_c008_post_mortem_diagnostics.py
git status --short
```

## Disclaimer

Diagnostic research only. Not strategy evidence. No win-rate or expectancy approval claims.

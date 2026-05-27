# next_bar_open Policy and HTF Align Migration — Plan

**Branch:** `infra-next-bar-open-policy-and-htf-align-migration-001`  
**Base:** `infra-observed-financing-capture-readonly-002` @ `cbead73`  
**Date:** 2026-05-27

## Purpose

1. Make **fill_timing** policy mechanical for future approval-bound / promotion-review evidence (`next_bar_open` default).
2. Begin **HTF alignment** migration using `htf_align.align_last_completed()` via shared `d1agg_htf` helpers.

## Non-goals

No CAMPAIGN_020, no strategy approval, no paper/demo/live, no C019 rerun, no verdict rewrites.

## Safety rules

See sprint hard rules in user prompt; `approved: []` unchanged; broker mutation untouched.

## next_bar_open policy intent

C019 validation: `signal_bar_close` +0.0962R vs `next_bar_open` +0.0175R (~−0.079R). Approval-bound evidence must use `next_bar_open` unless justified; `signal_bar_close` is optimistic upper-bound.

## HTF migration intent

Migrate **regime_switcher D1AGG** path to `forex_bot.features.d1agg_htf` (shared with `htf_align` provenance on signals). Weekly strategies remain on completed-week helpers (documented exception).

## Inspected modules

- `src/forex_bot/research/execution_realism.py` (new)
- `src/forex_bot/features/d1agg_htf.py` (new)
- `src/forex_bot/features/htf_align.py`
- `src/forex_bot/strategies/regime_switcher_atr_percentile.py`
- `src/forex_bot/research_archive.py`
- `configs/campaign_019_mean_reversion_thesis_invalidation.yaml`
- `docs/research/EVIDENCE_MANIFEST.json`

## Compatibility

Legacy campaigns without `research_metadata` load via `legacy` mode. Historical `signal_bar_close` marked `optimistic_upper_bound` where metadata added (C019).

## Selected HTF target

**CAMPAIGN_012 regime_switcher D1AGG** — equivalence tests pass; behavior preserved; `htf_feature_times` added to signals.

## Validation

`pytest`, `ruff`, `check_research_freeze`, `validate_research_archive`, `scan_artifacts_for_secrets`.

## No-approval statement

Infrastructure/policy only.

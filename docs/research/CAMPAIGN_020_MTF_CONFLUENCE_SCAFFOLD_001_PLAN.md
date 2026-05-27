# CAMPAIGN_020 — MTF Confluence Pullback Scaffold Sprint Plan

**Date:** 2026-05-27  
**Branch:** `research-mtf-confluence-candidate-020-scaffold-001`  
**Base:** `main` @ `fe34c4d` (clean, synced with `origin/main`)

## Purpose

Create a genuinely new research candidate — `multi_timeframe_confluence_pullback 0.1.0-c020` — that trades only when D1AGG structure, H4 trend context, and a local pullback re-acceptance align. This sprint delivers design freeze, implementation scaffold, invariant tests, preflight runner, and execution prompt only.

## Non-goals

- No full train / validation / test historical evidence
- No test lockbox open
- No strategy approval
- No paper / demo / live enablement
- No broker order submission or OANDA mutation APIs
- No live credentials
- No parameter sweeps or tuning after results
- No modification of legacy campaign verdicts (C008–C019 unchanged)

## Safety rules

| rule | enforcement |
|---|---|
| `configs/approved_strategies.yaml` stays `approved: []` | freeze gate + unit tests |
| `trading_enabled: false`, `allow_order_submission: false` | campaign YAML + config validation |
| Strategy emits `Signal` only | no broker/executor imports |
| Approval-bound fill timing | `research_metadata.fill_timing: next_bar_open` |
| HTF alignment | `htf_align.align_last_completed` + `d1agg_htf` for D1AGG |
| Incomplete D1AGG excluded | `complete=True` filter in align path |
| Strict RSI warmup | `warmup_policy="nan"` when RSI used |

## Structural distinctness requirement

CAMPAIGN_020 must not be an exit-only C008 variant, a C012 regime-switcher retune, C013/C014/C015–C017 family retunes, or a C007 Donchian-free pullback clone without MTF gates. Phase 1 memo documents the defense; if indefensible, stop with `CAMPAIGN_020_BLOCKED_NOT_STRUCTURALLY_DISTINCT.md`.

## Selected thesis

**Family:** `multi_timeframe_confluence_pullback`  
**Version:** `0.1.0-c020`  
**Working name:** MTF Confluence Pullback  

Trade H4 continuation pullbacks only when D1AGG trend (EMA structure) and H4 trend (close vs EMA50) agree, after a recent pullback toward EMA20 / RSI zone and a same-bar re-acceptance above/below EMA20. Cost/session filters remain in the existing risk layer; financing is declared for holds > 1 day.

## Expected phases

| phase | deliverable |
|---|---|
| 0 | This plan + branch audit (this doc) |
| 1 | Structural distinctness memo |
| 2 | Precommit design + frozen parameters |
| 3 | Strategy module + campaign YAML |
| 4 | Unit / invariant tests |
| 5 | Preflight runner (no full evidence) |
| 6 | Backtrader parity design |
| 7 | Future execution sprint prompt |
| 8 | Evidence index / manifest / backlog / strategy status |
| 9 | Final validation + summary |

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

## Policy docs verified (present on base)

- `docs/research/FILL_TIMING_APPROVAL_BOUND_POLICY.md`
- `docs/research/NEXT_BAR_OPEN_POLICY_AND_HTF_ALIGN_MIGRATION_001_SUMMARY.md`
- `docs/research/HTF_ALIGNMENT_POLICY_FOR_FUTURE_STRATEGIES.md`
- `docs/research/CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_NEXT_BAR_OPEN_POLICY_AND_HTF_MIGRATION.md`
- `docs/research/OBSERVED_COST_FINANCING_OVERLAY_LOCAL_FIRST_001_SUMMARY.md`

## Shared modules verified

- `src/forex_bot/features/htf_align.py`
- `src/forex_bot/features/d1agg_htf.py`
- `src/forex_bot/research/execution_realism.py`

## Explicit no-approval statement

**No strategy is approved by this sprint.** Maximum status after future execution is `RESEARCH_PASS` / `PROMOTION_REVIEW_REQUIRED`, never paper/demo/live without a separate human approval action.

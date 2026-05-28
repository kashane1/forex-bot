# CAMPAIGN_023 — ADX22 Sibling Plan (sensitivity campaign of C022)

**Date:** 2026-05-27
**Branch:** `claude/loving-hawking-7ab830`
**Status:** PLAN — scaffold sprint only; no execution, no evidence

## Purpose

CAMPAIGN_023 is a tightly controlled **sibling / sensitivity** campaign of
CAMPAIGN_022 (`h4_h1_pullback_resolution_entry 0.1.0-c022`). It is identical to C022 in
every respect **except one** — the H4 directional-bias strength gate:

| campaign | H4 ADX(14) gate |
|---|---|
| CAMPAIGN_022 | `h4_adx_min >= 20.0` |
| CAMPAIGN_023 | `h4_adx_min >= 22.0` |

Nothing else changes: pairs, execution timeframe (M15), context timeframes (H4/H1),
no-D1/no-D1AGG scope, M15 trigger, H1 pullback-holds logic, stop, time stop,
spread/session filters, execution realism, financing mode, gates, no-lookahead rules,
approved-strategies registry, and broker/executor behavior are all held constant.

## Identity

| field | value |
|---|---|
| `campaign_id` | CAMPAIGN_023 |
| `strategy_name` | `h4_h1_pullback_resolution_entry` |
| `version` | `0.1.0-c023` |
| `working_name` | H4/H1 Pullback Resolution Entry — ADX22 |
| `promotion_eligible` | false |

## Why this is pre-registration, not post-hoc tuning

C022 is **SCAFFOLD_ONLY / PRECOMMITTED_NOT_EXECUTED**. No C022 train/validation/test
evidence has been generated or viewed (confirmed: C022 has no entry in
`docs/research/EVIDENCE_MANIFEST.json`; `scripts/check_research_freeze.py` and
`scripts/validate_research_archive.py` both PASS with no C022 verdict). Choosing the
ADX22 variant **before any results exist** is a legitimate pre-registered sensitivity arm,
not parameter tuning after seeing outcomes.

> If C022 evidence had already been executed or viewed before this sprint started, the
> correct action would be to **stop and document `BLOCKED_CONTAMINATED_BY_PRIOR_RESULTS`**.
> That condition does **not** hold here.

## Phase 0 audit findings (C022 baseline)

1. **C022 scaffold exists** — strategy, config model, YAML, precommit doc, tests all
   present in the working tree.
2. **C022 uses H4 ADX threshold 20.0** — confirmed in
   `configs/campaign_022_h4_h1_pullback_resolution.yaml` (`h4_adx_min: 20.0`) and the
   config-model default `H4H1PullbackResolutionEntryStrategyConfig.h4_adx_min = 20.0`.
3. **`configs/approved_strategies.yaml` remains `approved: []`.**
4. **No paper/demo/live enablement** — C022 YAML has `mode: paper`,
   `trading_enabled: false`, `allow_order_submission: false`, `allow_live_trading: false`.
5. **C022 targeted tests PASS** — `tests/unit/test_h4_h1_pullback_resolution_entry.py`
   → 22 passed.

### Deviation noted honestly (does not weaken the freeze)

The C022 scaffold is **present but uncommitted** on this branch (untracked strategy/YAML/
docs/tests; modified `config.py` and `strategies/__init__.py`). The branch working tree is
therefore the source of truth. C023 reuses the same shared strategy class and config model
in place. C023 commits add only C023-specific artifacts and the minimal shared
parameterization required for reuse; pre-existing uncommitted C022 files and unrelated
CAMPAIGN_021 working changes are left untouched and are **not** staged by this sprint.

## Implementation approach (minimal duplication)

- **Reuse** `H4H1PullbackResolutionEntryStrategy` — no logic fork.
- The strategy already parameterizes `h4_adx_min`, `version`, and all other knobs through
  config; the only shared-code change needed is to **parameterize `campaign_id`** (default
  `CAMPAIGN_022`) so the same class can emit `CAMPAIGN_023` signals.
- C023 differs only by a new frozen YAML with `h4_adx_min: 22.0`, C023 identity/version,
  and C023 artifact paths.

## Scaffold deliverables (this sprint — no execution, no evidence)

1. This plan (`docs/research/CAMPAIGN_023_ADX22_SIBLING_PLAN.md`).
2. `docs/research/CAMPAIGN_023_H4_H1_PULLBACK_RESOLUTION_ADX22_PRECOMMIT.md`.
3. `configs/campaign_023_h4_h1_pullback_resolution_adx22.yaml` (frozen, `h4_adx_min: 22.0`).
4. Minimal `campaign_id` parameterization in the shared strategy (behavior-preserving for
   C022).
5. `tests/unit/test_h4_h1_pullback_resolution_adx22.py` — proves C023 == C022 except the
   ADX gate (block at 21.9, pass at 22.0).
6. `scripts/run_campaign_023_h4_h1_pullback_resolution_adx22.py` — preflight-only.
7. Docs/status/archive updates marking C023 `PRECOMMITTED_NOT_EXECUTED / SCAFFOLD_ONLY`.
8. `docs/research/CAMPAIGN_023_ADX22_SIBLING_SCAFFOLD_SUMMARY.md`.

## No approval

`configs/approved_strategies.yaml` remains `approved: []`. Paper/demo/live blocked. No
train/validation/test evidence is produced by this sprint.

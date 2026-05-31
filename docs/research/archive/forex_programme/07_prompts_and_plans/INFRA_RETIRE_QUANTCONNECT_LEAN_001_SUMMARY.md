# Infrastructure QuantConnect/LEAN Retirement Sprint 001 — Summary & Handoff

**Date:** 2026-05-22 · **Branch:** `infra-retire-quantconnect-lean-001`
**Base commit:** `0d89e8a` (HEAD of `infra-lean-parity-execute-001`)

This sprint formally closes the QuantConnect/LEAN CLI execution path
for this project. The decision and reasoning are recorded in
`QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`; the replacement direction
is planned in `FREE_LOCAL_PARITY_VERIFIER_PLAN.md`. Prior LEAN
documentation has been superseded with retirement banners but
preserved as historical infrastructure evidence. **No strategy is
approved, CAMPAIGN_002 remains REJECT, paper / demo / live remain
blocked, no QuantConnect credentials were requested or written, and no
LEAN run exists.**

## What changed (by phase)

### Phase 0 — baseline safety check
No file changes. Baseline state confirmed:
- working tree clean, branch created
- `configs/approved_strategies.yaml`: `approved: []`
- pytest: 388 passed
- ruff: clean
- archive validator: ALL CHECKS PASSED
- freeze checker: ALL CHECKS PASSED
- secret scan: PASSED
- no `.env`, SQLite store, candle CSV, or large LEAN output staged
- no QuantConnect credential present anywhere in the repo

Commit: none (no changes).

### Phase 1 — supersede LEAN recommendation
Added a "SUPERSEDED — QuantConnect/LEAN CLI execution is RETIRED for
this project" banner to every prior LEAN doc that recommended creating
a QuantConnect account or running `lean login` / `lean init`. The
verbatim next-step commands in `LEAN_PARITY_EXECUTE_BLOCKED.md` are
retired and preserved only as historical evidence of the prior plan.
Files updated:
- `docs/research/INFRA_LEAN_PARITY_EXECUTE_001_SUMMARY.md`
- `docs/research/LEAN_PARITY_EXECUTE_BLOCKED.md`
- `docs/research/LEAN_LOCAL_WORKSPACE_STATUS.md`
- `docs/research/CAMPAIGN_002_H4_PARITY_STATUS.md`
- `docs/research/LEAN_PARITY_CAMPAIGN_002_BLOCKED.md`
- `docs/research/EVIDENCE_INDEX.md` (retirement-section header; full
  link entries added in Phases 2/3/4)

Commit: `6208447`.

### Phase 2 — retirement decision record
Created `docs/research/QUANTCONNECT_LEAN_RETIREMENT_DECISION.md` — the
formal decision record (decision date 2026-05-22): why LEAN was
considered, what was successfully prepared, what blocked execution,
the user decision (free-tier QC lacks the required API access, paid
upgrade declined), the exact project consequence (bespoke engine
remains uncorroborated by an independent engine), the list of actions
that must not be attempted again without explicit user approval
(QC account creation, `lean login`, `lean init`, `lean backtest`,
brokerage connection), what remains valid from the prior work, and
the replacement direction.

Updated `docs/research/EVIDENCE_INDEX.md` to link the new decision
record. Updated `docs/research/EVIDENCE_MANIFEST.json` to record the
retirement under a new `retired_paths` field (the retired artifact
list, decision date, branch, reason, decision-record path,
replacement-plan path, plus explicit `lean_result_exists: false`,
`lean_comparison_exists: false`, `strategy_approved: false`,
`campaign_002_verdict: "REJECT"` confirmations) and refresh the
top-level description.

Commit: `0a8f92d`.

### Phase 3 — free/local verifier plan
Created `docs/research/FREE_LOCAL_PARITY_VERIFIER_PLAN.md` — the
replacement for the retired LEAN parity path. The plan covers
purpose, non-goals, safety constraints, four candidate approaches
(minimal independent event-loop verifier *recommended*; vectorized
pandas verifier; third-party-library feasibility for `backtesting.py`
/ `vectorbt` / `backtrader` — all require new deps; fixture-level
rule verifier as a supporting layer), the recommended approach (4a +
4d using only repo-existing dependencies pandas / numpy / pydantic /
pyyaml), why this is useful independent evidence even without LEAN,
inputs (existing OANDA H4 SQLite, seven-pair export CSVs,
CAMPAIGN_002 frozen rules, no-RiskEngine bespoke reference), outputs
(independent trade list, per-pair summary in the same shape as the
LEAN `parity_summary.json`, comparison report, implementation notes),
the divergence taxonomy extending the LEAN-era taxonomy, guardrails,
and a proposed phased implementation sprint (eight phases on a
separate branch).

Updated `docs/research/EVIDENCE_INDEX.md` to link the new plan.

Commit: `2692275`.

### Phase 4 — final validation & summary
This document plus the final validation pass. Re-ran the full
validation suite and verified paper / demo loops refuse.

## Commit hashes by phase

| phase | commit |
|---|---|
| Phase 0 | (no changes) |
| Phase 1 | `6208447` |
| Phase 2 | `0a8f92d` |
| Phase 3 | `2692275` |
| Phase 4 | (this commit) |

## Files changed by phase

| phase | files |
|---|---|
| Phase 0 | — |
| Phase 1 | `docs/research/INFRA_LEAN_PARITY_EXECUTE_001_SUMMARY.md`, `docs/research/LEAN_PARITY_EXECUTE_BLOCKED.md`, `docs/research/LEAN_LOCAL_WORKSPACE_STATUS.md`, `docs/research/CAMPAIGN_002_H4_PARITY_STATUS.md`, `docs/research/LEAN_PARITY_CAMPAIGN_002_BLOCKED.md`, `docs/research/EVIDENCE_INDEX.md` |
| Phase 2 | `docs/research/QUANTCONNECT_LEAN_RETIREMENT_DECISION.md` (new), `docs/research/EVIDENCE_INDEX.md`, `docs/research/EVIDENCE_MANIFEST.json` |
| Phase 3 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_PLAN.md` (new), `docs/research/EVIDENCE_INDEX.md` |
| Phase 4 | `docs/research/INFRA_RETIRE_QUANTCONNECT_LEAN_001_SUMMARY.md` (new), `docs/research/EVIDENCE_INDEX.md` |

No code, test, script, config, or strategy file was touched. No
artifact data was staged.

## What was superseded

Every prior doc that recommended creating a (free) QuantConnect
account, running `lean login`, or running `lean init` now carries a
"SUPERSEDED — QuantConnect/LEAN CLI execution is RETIRED for this
project" banner pointing at the decision record and the replacement
plan. The verbatim next-step commands in `LEAN_PARITY_EXECUTE_BLOCKED.md`
are retired and preserved as historical evidence of the prior plan.

## Confirmations

- **QuantConnect/LEAN is RETIRED** unless explicitly reopened by the
  user.
- **No QuantConnect account credential** was requested, prompted-for,
  read, written, or committed at any point in this sprint.
- **No LEAN run exists.** No `parity_summary.json`. No
  `LEAN_PARITY_CAMPAIGN_002_RESULT.md`. No
  `LEAN_PARITY_CAMPAIGN_002_COMPARISON.md`. No LEAN-side trade list.
- **No strategy is approved.** `configs/approved_strategies.yaml`
  remains `approved: []`.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.** `paper-loop` and `demo-loop`
  both refuse with the registry-empty message; no `live-loop` command
  exists at all.
- **No broker credential was used.** No order was submitted. No
  brokerage was contacted.

## Validation results (final pass)

- `pytest` — **388 passed**.
- `ruff check src tests scripts` — clean.
- `scripts/validate_research_archive.py` — ALL CHECKS PASSED (67
  evidence-index links resolve; 4 diagnostic artifacts present;
  no credential-shaped strings in 1907+ committed artifact files).
- `scripts/check_research_freeze.py` — ALL CHECKS PASSED (paper-loop
  refuses `['trend_following']`; demo-loop refuses `['trend_following']`).
- `scripts/scan_artifacts_for_secrets.py` — PASSED.
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml` —
  refused (registry empty; clear approval-process message).
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml` —
  refused (registry empty; clear approval-process message).
- No `live-loop` command exists in the CLI.

## Safety state at handoff

The research freeze is **intact**. The approved-strategy registry is
empty; every order-capable loop refuses; the bespoke engine is
unchanged; no credential of any kind (forex-bot `.env`, OANDA, or
QuantConnect) was read, prompted-for, written, or committed in this
sprint. The local `/tmp/lean-venv` LEAN CLI install and the absence of
`~/.lean/credentials` are left as-is and are not expected to be used
again under this project.

## Replacement verifier recommendation

A **minimal independent event-loop verifier** in
`research/parity_verifier/`, using only the repo's existing
dependencies (pandas, numpy, pydantic, pyyaml), supported by a
**fixture-level rule verifier** that pins EMA / ATR / Donchian and a
small set of trade-rule fixtures. The verifier consumes the existing
seven-pair H4 candle CSVs and the no-RiskEngine bespoke reference
(1,647 trades), and reuses the divergence taxonomy and tolerance
ranges from `LEAN_PARITY_COMPARISON_METHOD.md`. The verifier is
fully local, free, deterministic, and does not require cloud, API, or
broker credentials. See `FREE_LOCAL_PARITY_VERIFIER_PLAN.md` §5 and
§11 for the recommended approach and the proposed phased
implementation sprint.

## Recommended next branch

`infra-free-local-parity-verifier-001` — the implementation sprint
for the free / local independent verifier. Eight phases (baseline,
scaffold, fixture-level rule verifier, single-pair event loop,
seven-pair generalization, comparison-harness wiring, divergence
resolution, final validation & summary), all on a separate branch,
with the freeze checker / archive validator / secret scanner passing
on every commit. At no phase does the sprint touch
`configs/approved_strategies.yaml`, the bespoke engine, the
CAMPAIGN_002 rules, or any broker credential.

## Remaining blockers

1. **Independent-engine corroboration is still pending.** The
   bespoke engine remains internally reproducible but uncorroborated
   by an independent engine. The path to closing this gap is the
   free / local verifier plan; the QuantConnect / LEAN path is
   retired.
2. **Financing is estimated / stress-only.** Unchanged standing live
   blocker; not in scope for this retirement sprint.

## Files to review first

1. `docs/research/QUANTCONNECT_LEAN_RETIREMENT_DECISION.md` — the
   formal retirement decision record.
2. `docs/research/FREE_LOCAL_PARITY_VERIFIER_PLAN.md` — the
   replacement direction and proposed implementation sprint.
3. This summary (`docs/research/INFRA_RETIRE_QUANTCONNECT_LEAN_001_SUMMARY.md`).
4. `docs/research/EVIDENCE_INDEX.md` — updated index showing the
   retirement section.
5. `docs/research/EVIDENCE_MANIFEST.json` — the new `retired_paths`
   entry that records the retirement machine-readably.

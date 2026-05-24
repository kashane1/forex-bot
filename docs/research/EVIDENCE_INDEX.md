# Evidence Index

**Date:** 2026-05-22 · **Branch:** `research-freeze-no-go`

A single index of every campaign report, pre-commit, post-mortem, and
research-freeze document. All paths are repo-relative. This index is the
map; the linked documents are the authoritative evidence.

> **Bottom line:** nine campaigns, five strategy families, **no approved
> trading strategy.** See `docs/research/FINAL_RESEARCH_DECISION_MEMO.md`.

## Campaign reports

| campaign | report | verdict | key metrics |
|---|---|---|---|
| 001 | [`backtests/CAMPAIGN_001_REPORT.md`](../../backtests/CAMPAIGN_001_REPORT.md) | not evidence | **Synthetic** candles (no OANDA creds at the time) — harness validation only; superseded by 002 |
| 002 | [`backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`](../../backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md) | **REJECT** | trend_following baseline, real OANDA H4/H1: −0.085 R, PF 0.75, −1.02 % |
| 003 | [`backtests/CAMPAIGN_003_CONTROLLED_ADX_REPORT.md`](../../backtests/CAMPAIGN_003_CONTROLLED_ADX_REPORT.md) | **REJECT** | trend_following + ADX-14 > 25 gate, real OANDA H4: −0.071 R, PF 0.77, −0.63 % |
| 004 | [`backtests/CAMPAIGN_004_VOLATILITY_BREAKOUT_REPORT.md`](../../backtests/CAMPAIGN_004_VOLATILITY_BREAKOUT_REPORT.md) | **REJECT** | volatility_breakout (ATR compression), real OANDA H4: −0.163 R, PF 0.63, −1.40 % |
| 005 | [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md) | diagnostic | benchmarks: random entry −0.095 R; efficiency ratio 0.24 (choppy H4 majors) |
| 006 | [`backtests/CAMPAIGN_006_DAILY_TREND_REPORT.md`](../../backtests/CAMPAIGN_006_DAILY_TREND_REPORT.md) | **REJECT** — no valid result | D1 trend untestable: rollover / session / spread contamination (infrastructure blocker) |
| 007 | [`backtests/CAMPAIGN_007_H4_PULLBACK_REPORT.md`](../../backtests/CAMPAIGN_007_H4_PULLBACK_REPORT.md) | **REJECT** | H4 pullback-continuation: screening fail, train −0.164 R, validation −0.166 R |
| 008 | [`backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md`](../../backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md) | **REJECT** (narrow) | range mean-reversion: train −0.017 R (failing gate); validation +0.172 R, PF 1.29, 6/6 pairs positive |
| 009 | [`backtests/CAMPAIGN_009_MEAN_REVERSION_REPORT.md`](../../backtests/CAMPAIGN_009_MEAN_REVERSION_REPORT.md) | **REJECT** | mean-reversion + midline-target exit: train −0.062 R (failing gate); validation +0.170 R, PF 1.37 |

## Research Marathon 001

A disciplined four-campaign ladder (005–008) under one supervisor spec.

| document | what it is |
|---|---|
| [`docs/research/RESEARCH_MARATHON_001_PLAN.md`](RESEARCH_MARATHON_001_PLAN.md) | marathon plan / supervisor spec |
| [`docs/research/RESEARCH_MARATHON_001_LEDGER.md`](RESEARCH_MARATHON_001_LEDGER.md) | campaign-by-campaign running ledger |
| [`docs/research/RESEARCH_MARATHON_001_NO_GO.md`](RESEARCH_MARATHON_001_NO_GO.md) | **close-out: NO-GO** — no hypothesis earned PAPER-TRADE-ONLY |
| [`docs/research/RESUME_RESEARCH_MARATHON_001.md`](RESUME_RESEARCH_MARATHON_001.md) | marathon resume / handover notes |

## Pre-commit specs (the discipline trail)

Each campaign's pass/fail gates, fixed and committed *before* the run.

| campaign | pre-commit |
|---|---|
| 004 | [`docs/research/CAMPAIGN_004_PRECOMMIT.md`](CAMPAIGN_004_PRECOMMIT.md) |
| 005 | [`docs/research/CAMPAIGN_005_BENCHMARKS_PRECOMMIT.md`](CAMPAIGN_005_BENCHMARKS_PRECOMMIT.md) |
| 006 | [`docs/research/CAMPAIGN_006_DAILY_TREND_PRECOMMIT.md`](CAMPAIGN_006_DAILY_TREND_PRECOMMIT.md) |
| 007 | [`docs/research/CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md`](CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md) |
| 008 | [`docs/research/CAMPAIGN_008_RANGE_MEAN_REVERSION_PRECOMMIT.md`](CAMPAIGN_008_RANGE_MEAN_REVERSION_PRECOMMIT.md) |
| 009 | [`docs/research/CAMPAIGN_009_PRECOMMIT.md`](CAMPAIGN_009_PRECOMMIT.md) |

## Post-mortems, proposals & diagnostics

| document | what it is |
|---|---|
| [`docs/research/CAMPAIGN_002_POSTMORTEM.md`](CAMPAIGN_002_POSTMORTEM.md) | post-mortem of the trend baseline rejection |
| [`docs/research/CAMPAIGN_003_POSTMORTEM.md`](CAMPAIGN_003_POSTMORTEM.md) | post-mortem of the ADX-trend rejection |
| [`docs/research/CAMPAIGN_003_PROPOSAL.md`](CAMPAIGN_003_PROPOSAL.md) | proposal that led to the ADX campaign |
| [`docs/research/HYPOTHESIS_BACKLOG.md`](HYPOTHESIS_BACKLOG.md) | campaign-era hypothesis backlog |
| [`docs/research/CAMPAIGN_008_HUMAN_REVIEW.md`](CAMPAIGN_008_HUMAN_REVIEW.md) | human review authorizing the CAMPAIGN_009 follow-up |
| [`docs/strategy_research.md`](../strategy_research.md) | strategy-research overview / methodology |
| [`docs/financing_decision.md`](../financing_decision.md) | financing investigation & decision |

Diagnostics scripts live under `scripts/` (e.g. `diagnostics_campaign_002.py`),
and per-run risk-rejection CSVs are committed under each campaign's
`backtests/campaign_00X*/runs/` tree.

## Diagnostic & parity artifacts (NOT strategy evidence)

Infrastructure outputs from the `infra-execution-fidelity-001`,
`infra-data-parity-001`, `oanda-practice-readonly-001`,
`infra-lean-parity-001`, `infra-lean-parity-run-001`,
`infra-lean-parity-execute-001`, and `infra-retire-quantconnect-lean-001`
sprints. **These are not campaign evidence.**
They are mechanical plumbing checks and independent-verification
inputs — none measures, implies, or can establish a strategy edge, and
none can approve anything. The machine-readable manifest lists them
under `diagnostic_artifacts` with `strategy_evidence: false`, enforced
by `scripts/validate_research_archive.py`.

| artifact | what it is |
|---|---|
| [`backtests/diagnostics/d1agg_next_open_smoke.md`](../../backtests/diagnostics/d1agg_next_open_smoke.md) | D1AGG + next-bar-open fill-path smoke (single-pair) |
| [`backtests/diagnostics/d1agg_next_open_six_pair_smoke.md`](../../backtests/diagnostics/d1agg_next_open_six_pair_smoke.md) | D1AGG + next-bar-open smoke across the six majors |
| [`research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md`](../../research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md) | Lean-parity export bundle for the CAMPAIGN_002 H4 baseline (seven pairs) |
| [`backtests/diagnostics/custom_campaign_002_h4_parity.md`](../../backtests/diagnostics/custom_campaign_002_h4_parity.md) | custom-engine reproduction of the rejected CAMPAIGN_002 H4 baseline |

Supporting infrastructure docs:
[fill-timing model](FILL_TIMING_MODEL.md) ·
[Lean parity execution](LEAN_PARITY_EXECUTION_GUIDE.md) (LEAN path retired — historical) ·
[Lean parity local status](LEAN_PARITY_LOCAL_STATUS.md) (LEAN path retired — historical) ·
[OANDA H4 rehydration](OANDA_H4_DATA_REHYDRATION.md) ·
[data rehydration runbook](DATA_REHYDRATION_RUNBOOK.md) ·
[data/parity sprint plan](INFRA_DATA_PARITY_001_PLAN.md).

### OANDA practice read-only integration (`oanda-practice-readonly-001`)

Read-only OANDA practice integration and data-foundation reports. All
diagnostic / infrastructure outputs — none is strategy evidence, none
approves anything, and the research freeze is unaffected.

| document | what it is |
|---|---|
| [`OANDA_PRACTICE_READONLY_001_PLAN.md`](OANDA_PRACTICE_READONLY_001_PLAN.md) | the read-only sprint plan |
| [`OANDA_PRACTICE_CREDENTIAL_CHECK.md`](OANDA_PRACTICE_CREDENTIAL_CHECK.md) | practice credential & environment gate (redacted) |
| [`OANDA_READONLY_HEALTHCHECK_RESULT.md`](OANDA_READONLY_HEALTHCHECK_RESULT.md) | read-only OANDA API healthcheck result |
| [`OANDA_INSTRUMENT_METADATA_AUDIT.md`](OANDA_INSTRUMENT_METADATA_AUDIT.md) | instrument metadata audit |
| [`OANDA_H4_REHYDRATION_RESULT.md`](OANDA_H4_REHYDRATION_RESULT.md) | real OANDA H4 store rehydration result |
| [`OANDA_H4_DATA_QUALITY_AUDIT.md`](OANDA_H4_DATA_QUALITY_AUDIT.md) | H4 data quality audit |
| [`OANDA_PRACTICE_READONLY_001_SUMMARY.md`](OANDA_PRACTICE_READONLY_001_SUMMARY.md) | sprint summary & handoff |

### Lean parity completeness (`infra-lean-parity-001`)

Independent-engine parity readiness for the CAMPAIGN_002 H4 baseline.
All diagnostic / infrastructure outputs — none is strategy evidence,
none approves anything; CAMPAIGN_002 stays REJECT.

| document | what it is |
|---|---|
| [`INFRA_LEAN_PARITY_001_PLAN.md`](INFRA_LEAN_PARITY_001_PLAN.md) | the Lean-parity sprint plan |
| [`OANDA_H4_NZDUSD_REHYDRATION_RESULT.md`](OANDA_H4_NZDUSD_REHYDRATION_RESULT.md) | NZD_USD H4 rehydration result |
| [`OANDA_H4_DATA_QUALITY_AUDIT_7PAIR.md`](OANDA_H4_DATA_QUALITY_AUDIT_7PAIR.md) | seven-pair H4 data quality audit |
| [`LEAN_PARITY_CAMPAIGN_002_BLOCKED.md`](LEAN_PARITY_CAMPAIGN_002_BLOCKED.md) | Lean dry-run blocker (`lean init` needs a QuantConnect account) |
| [`CAMPAIGN_002_H4_PARITY_STATUS.md`](CAMPAIGN_002_H4_PARITY_STATUS.md) | independent-engine parity status |
| [`INFRA_LEAN_PARITY_001_SUMMARY.md`](INFRA_LEAN_PARITY_001_SUMMARY.md) | sprint summary & handoff |

### Lean parity run (`infra-lean-parity-run-001`)

The faithful Lean parity algorithm and comparison harness for the
CAMPAIGN_002 H4 baseline. All verification infrastructure — none is
strategy evidence; CAMPAIGN_002 stays REJECT.

| document | what it is |
|---|---|
| [`INFRA_LEAN_PARITY_RUN_001_PLAN.md`](INFRA_LEAN_PARITY_RUN_001_PLAN.md) | the Lean-parity-run sprint plan |
| [`CAMPAIGN_002_LEAN_MAPPING_SPEC.md`](CAMPAIGN_002_LEAN_MAPPING_SPEC.md) | bespoke→Lean behavior mapping spec |
| [`LEAN_ALGORITHM_IMPLEMENTATION_NOTES.md`](LEAN_ALGORITHM_IMPLEMENTATION_NOTES.md) | Lean algorithm — faithful vs approximated |
| [`LEAN_PARITY_COMPARISON_METHOD.md`](LEAN_PARITY_COMPARISON_METHOD.md) | comparison metrics, tolerances, pass/fail |
| [`INFRA_LEAN_PARITY_RUN_001_SUMMARY.md`](INFRA_LEAN_PARITY_RUN_001_SUMMARY.md) | sprint summary & handoff |

### Lean parity execute attempt (`infra-lean-parity-execute-001`)

A second attempt at running the local Lean parity backtest, gated on
locally-present QuantConnect/Lean CLI credentials. Auth was absent;
execution did not proceed and no Lean result was fabricated.

| document | what it is |
|---|---|
| [`INFRA_LEAN_PARITY_EXECUTE_001_PLAN.md`](INFRA_LEAN_PARITY_EXECUTE_001_PLAN.md) | the execute-sprint plan + auth-handling rules |
| [`LEAN_LOCAL_WORKSPACE_STATUS.md`](LEAN_LOCAL_WORKSPACE_STATUS.md) | local Lean tooling / auth / workspace state |
| [`LEAN_PARITY_EXECUTE_BLOCKED.md`](LEAN_PARITY_EXECUTE_BLOCKED.md) | precise execution blocker + exact next human steps |
| [`INFRA_LEAN_PARITY_EXECUTE_001_SUMMARY.md`](INFRA_LEAN_PARITY_EXECUTE_001_SUMMARY.md) | sprint summary & handoff |

### QuantConnect/LEAN retirement (`infra-retire-quantconnect-lean-001`)

QuantConnect/LEAN CLI execution is **retired** for this project
(decision date 2026-05-22). The free-tier QuantConnect account does
not provide the API access required for the intended local LEAN CLI
workflow, and a paid QuantConnect upgrade is declined. The LEAN
algorithm / mapping spec / harness artifacts are preserved as
**historical infrastructure evidence only**; no LEAN result exists; no
LEAN comparison exists; no strategy is approved; CAMPAIGN_002 remains
**REJECT**; paper / demo / live remain blocked. The replacement
direction is a free / local independent verifier.

| document | what it is |
|---|---|
| [`QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`](QUANTCONNECT_LEAN_RETIREMENT_DECISION.md) | decision record retiring the QuantConnect/LEAN path |
| [`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md) | plan for the free / local independent verifier |
| [`INFRA_RETIRE_QUANTCONNECT_LEAN_001_SUMMARY.md`](INFRA_RETIRE_QUANTCONNECT_LEAN_001_SUMMARY.md) | retirement-sprint summary & handoff |

### Free / local parity verifier implementation (`infra-free-local-parity-verifier-001`)

Implementation of the free / local independent parity verifier
designed in `FREE_LOCAL_PARITY_VERIFIER_PLAN.md`. All
diagnostic / infrastructure outputs — none is strategy evidence; none
approves anything; CAMPAIGN_002 remains REJECT.

| document | what it is |
|---|---|
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md) | the implementation-sprint plan |
| [`FREE_LOCAL_PARITY_VERIFIER_INDICATOR_FIXTURES.md`](FREE_LOCAL_PARITY_VERIFIER_INDICATOR_FIXTURES.md) | indicator fixture-test status (EMA / ATR / Donchian — 16 cases pass) |
| [`FREE_LOCAL_PARITY_VERIFIER_RULE_FIXTURES.md`](FREE_LOCAL_PARITY_VERIFIER_RULE_FIXTURES.md) | rule fixture-test status (entry / stop / trailing / fill / sizing / PnL — 31 cases pass) |
| [`FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md) | event-loop status (8 integration tests pass; full-data run BLOCKED — CSVs absent) |
| [`FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md`](FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md) | comparison-harness status (11 fixture tests pass; full-data comparison BLOCKED) |
| [`FREE_LOCAL_PARITY_VERIFIER_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_STATUS.md) | headline verifier status (85 verifier-side fixture tests pass; full-data run BLOCKED locally) |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md) | sprint summary & handoff |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_002_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_002_PLAN.md) | sprint-002 plan — full-data unblock & first-run |
| [`FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md) | sprint-002 data unblock status (BLOCKED — no SQLite, no creds) |
| [`FREE_LOCAL_PARITY_VERIFIER_FULL_DATA_RUN.md`](FREE_LOCAL_PARITY_VERIFIER_FULL_DATA_RUN.md) | sprint-002 first full-data run (BLOCKED — 7/7 pairs missing CSVs, exit code 2) |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_002_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_002_SUMMARY.md) | sprint-002 summary & handoff |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_003_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_003_PLAN.md) | sprint-003 plan — guarded OANDA-practice historical rehydrate + export + run |
| [`FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md) | sprint-003 rehydrate status (BLOCKED — no creds, only `--verify` ran) |
| [`FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md) | sprint-003 export status (BLOCKED — no SQLite source) |
| [`FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md`](FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md) | sprint-003 full-data run (BLOCKED — exit code 2, valid empty summary) |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_003_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_003_SUMMARY.md) | sprint-003 summary & handoff |
| [`FREE_LOCAL_PARITY_VERIFIER_003_UNBLOCKED_RESULT.md`](FREE_LOCAL_PARITY_VERIFIER_003_UNBLOCKED_RESULT.md) | sprint-003 mid-sprint unblock — verifier ran end-to-end (post-Phase-5: 1,655 vs 1,647 trades, overall WARN; 2 verifier-side bugs fixed) |
| [`FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md`](FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md) | sprint-003 Phase 5 verifier-side debug notes (Bug #1 initial-stop base; Bug #2 same-bar re-entry) |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_004_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_004_PLAN.md) | sprint-004 plan — precision / rounding closure |
| [`FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md`](FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md) | sprint-004 rounding audit (bespoke metadata, round_price, mismatch table) |
| [`FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md`](FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md) | sprint-004 verifier-side rounding fixes (round_price wired into initial stop; observed comparison impact negligible) |
| [`FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md`](FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md) | sprint-004 remaining-drift classification (localized to float-vs-Decimal precision; USD_CAD is the cleanest evidence) |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md) | sprint-004 summary & handoff |
| [`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md) | **single closeout reference** — verifier accepted as WARN-band corroboration; no further sprints planned unless deferral conditions are met |
| [`FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md`](FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md) | explicit deferral of the Decimal end-to-end rewrite; conditions for reopening |
| [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md) | post-verifier next-research-direction plan; recommended next branch + success criteria for any future candidate |
| [`RESEARCH_CLOSE_FREE_LOCAL_VERIFIER_AND_NEXT_DIRECTION_001_SUMMARY.md`](RESEARCH_CLOSE_FREE_LOCAL_VERIFIER_AND_NEXT_DIRECTION_001_SUMMARY.md) | closeout-sprint summary & handoff |

### Walk-forward research harness (`research-walk-forward-harness-001`)

Reusable fold-generation library that future strategy campaigns
must use. Infrastructure, not a strategy. Diagnostic only — every
emitted artifact carries `strategy_evidence: false`. Sprint
adds no campaign and does not change any verdict.

| document | what it is |
|---|---|
| [`WALK_FORWARD_HARNESS_001_PLAN.md`](WALK_FORWARD_HARNESS_001_PLAN.md) | sprint plan |
| [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md) | protocol future campaigns must follow (splits, no-leakage, parameter freeze, metrics, rejection criteria, required artifacts) |
| [`CAMPAIGN_002_WALK_FORWARD_RETROSPECTIVE.md`](CAMPAIGN_002_WALK_FORWARD_RETROSPECTIVE.md) | metadata-only retrospective showing how the harness would frame CAMPAIGN_002; no re-run, no verdict change |
| [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md) | headline status — implemented pieces, tests (42 cases pass), limitations, usage |
| [`RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md`](RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md) | sprint summary & handoff |

### Research-grade financing calculator (`research-financing-model-001`)

Reusable per-day rollover-event calculator that future strategy
campaigns can attach to their trade lists for a richer, calendar-
and side-aware financing diagnostic than the existing per-trade
overlay. Infrastructure, not a strategy. Diagnostic only — every
emitted artifact carries `strategy_evidence: false` and is at
most `financing_treatment: estimated`. Sprint adds no campaign,
does not change any verdict, and does not lift the live-promotion
financing blocker.

| document | what it is |
|---|---|
| [`FINANCING_MODEL_001_PLAN.md`](FINANCING_MODEL_001_PLAN.md) | sprint plan |
| [`FINANCING_MODEL_CURRENT_ASSUMPTIONS.md`](FINANCING_MODEL_CURRENT_ASSUMPTIONS.md) | audit of how the repo currently handles (and mostly does not handle) financing in engine PnL, overlays, observed-event capture, instrument metadata, and risk |
| [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md) | protocol the new `research/financing/` calculator follows (inputs, outputs, rollover convention, triple swap, weekend skip, missing-rate fallback, currency conversion, stress mode, required/optional/deferred classification, approval-gate non-interaction) |
| [`CAMPAIGN_002_FINANCING_RETROSPECTIVE.md`](CAMPAIGN_002_FINANCING_RETROSPECTIVE.md) | diagnostic-only retrospective showing how the calculator attaches to CAMPAIGN_002-shaped positions; no real CAMPAIGN_002 artifact loaded; verdict unchanged |
| [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md) | headline status — implemented pieces, tests (71 cases pass), limitations, usage |
| [`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md) | sprint summary & handoff |

### Financing rate-source fixtures & pilot spec (`research-financing-rate-source-fixtures-001`)

The fixture format, loader/adapter, and pilot specification a
future observed-financing capture sprint will land into.
Synthetic fixtures only; **no broker data fetched**.
Infrastructure, not a strategy. Diagnostic only — every
emitted artifact carries `strategy_evidence: false`. Sprint
adds no campaign, does not change any verdict, and does not
lift the live-promotion financing blocker.

| document | what it is |
|---|---|
| [`FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md`](FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md) | sprint plan |
| [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md) | on-disk fixture schema (observed-events + financing-rates shapes; mirrors the canonical `ObservedFinancingEvent` field-for-field) |
| [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md) | future-facing specification for the read-only `DAILY_FINANCING` capture pilot (authorization, endpoint allow-list, redaction, reconciliation, `MODELED` acceptance criteria, why `MODELED` remains blocked) |
| [`FINANCING_RATE_SOURCE_FIXTURES_STATUS.md`](FINANCING_RATE_SOURCE_FIXTURES_STATUS.md) | headline status — schema, fixtures (9 files ~9 KB), loader/adapter, tests (43 cases pass), no broker data fetched, MODELED unavailable, live blocker remains |
| [`RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md) | sprint summary & handoff |

### Financing reconciliation tooling (`research-financing-reconciliation-tooling-001`)

Local-only CLI that reconciles an observed-financing
fixture against the calculator's prediction for the same
window. Diagnostic only — every output carries
`strategy_evidence: false` and at most
`financing_treatment: estimated`. No broker call, no
credential read. Sprint adds no campaign, does not change
any verdict, and does not lift the live-promotion blocker.

| document | what it is |
|---|---|
| [`FINANCING_RECONCILIATION_TOOLING_001_PLAN.md`](FINANCING_RECONCILIATION_TOOLING_001_PLAN.md) | sprint plan |
| [`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md) | CLI protocol — inputs, JSON + markdown output shapes, classification rules, exit codes, defense-in-depth MODELED guard |
| [`FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md`](FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md) | records of five synthetic runs (commands, inputs, exit codes, per-run summaries); confirms no broker / OANDA data fetched |
| [`FINANCING_RECONCILIATION_TOOLING_STATUS.md`](FINANCING_RECONCILIATION_TOOLING_STATUS.md) | headline status — script (`scripts/reconcile_financing_fixtures.py`), tests (22 cases pass), no broker data fetched, MODELED unavailable, live blocker remains |
| [`RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md`](RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md) | sprint summary & handoff |

### Observed-financing capture pilot (`research-financing-observed-capture-pilot-001`)

Read-only OANDA practice DAILY_FINANCING capture pilot.
Authorized for **practice transaction history only** —
no orders, trades, positions, pricing, mutation, or live
access. The pilot run did **not** execute (practice
credentials absent in the worktree); the script, tests,
allowlist + denylist, and dry-run path are all in place
for a future credentialed sprint. **No OANDA data
fetched. No MODELED financing. Live blocker remains.**

| document | what it is |
|---|---|
| [`FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md) | sprint plan + endpoint allow/denylist + credential / redaction rules |
| [`FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md`](FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md) | code-level audit of the existing parser / schema / repo / read-only endpoint; confirms minimal pilot wiring |
| [`FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md) | record of the attempted dry-run (no credentials → exit 2; valid pilot result) |
| [`FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md`](FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md) | reconciliation blocker (no captured events to reconcile); records the would-be command and the rate-fixture coverage gap |
| [`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md) | headline status — script (`scripts/capture_oanda_observed_financing_pilot.py`), tests (27 cases pass), no broker data fetched, no MODELED, live blocker remains |
| [`RESEARCH_FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md`](RESEARCH_FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md) | sprint summary & handoff |

### Financing bp/day fixture expansion (`research-financing-bp-day-fixture-expansion-001`)

Synthetic-data sprint. Expands the rate-fixture coverage so
all seven CAMPAIGN_002 H4 universe pairs (EUR_USD,
GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD)
have committed synthetic rate fixtures + a non-EUR
observed companion. Infrastructure only — no broker call,
no code change in `research/financing/` Python, no
production-path change. Every fixture continues to feed
`TableRateSource(treatment=ESTIMATED)`; **MODELED is
refused at all four pipeline layers**. The live blocker
remains.

| document | what it is |
|---|---|
| [`FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md) | sprint plan |
| [`FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md) | per-pair sign / precision / missing-rate / triple-swap / weekend conventions; contributor checklist for adding more pair fixtures |
| [`FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md) | 7 synthetic reconciliation runs (commands, exit codes, summaries); confirms no broker data fetched |
| [`FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md) | headline status — 7-pair coverage, fixture files added, tests (16 cases pass), synthetic run status, MODELED unavailable, live blocker remains |
| [`RESEARCH_FINANCING_BP_DAY_FIXTURE_EXPANSION_001_SUMMARY.md`](RESEARCH_FINANCING_BP_DAY_FIXTURE_EXPANSION_001_SUMMARY.md) | sprint summary & handoff |

### New candidate strategy discovery (`research-new-candidate-strategy-discovery-001`)

Docs-only design sprint. Produces the protocol, framework
inventory, candidate shortlist, and preferred-candidate
evaluation design for a future strategy candidate
meaningfully distinct from CAMPAIGN_002 and the other four
already-rejected families (trend_following, volatility_breakout,
pullback_continuation, mean_reversion). **No code is added**;
no strategy is implemented; no campaign is run; no approval is
granted; paper / demo / live remain blocked. The preferred
candidate (Asian-range / London-open session breakout) is
designed for a *separate, future, human-authorized* sprint
named `research-asian-london-session-breakout-001`. The
702-test baseline is preserved.

| document | what it is |
|---|---|
| [`NEXT_BRANCH_DECISION_AUDIT.md`](NEXT_BRANCH_DECISION_AUDIT.md) | Phase 0 repo-truth audit & branch decision (records the completed financing + walk-forward state, the 702-test baseline, the safety gates, and the PATH B selection) |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md) | sprint plan — scope, non-goals, phase deliverables, safety rails, success criteria |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md) | binding protocol — "meaningfully distinct from CAMPAIGN_002"; allowed / disallowed family categories; frozen-parameter / walk-forward / financing / risk-diagnostic requirements; six-item evidence ladder; §12 overfitting-pattern disqualifiers |
| [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md) | read-only inventory of every surface a new candidate plugs into (Strategy Protocol, existing 4 families, indicator primitives, bespoke BacktestEngine, RiskEngine gates, StrategyConfig, walk-forward harness API, financing calculator API, reporting, data sources) |
| [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md) | five candidates (C1 session breakout — PREFERRED; C2 carry overlay — blocked on MODELED; C3 daily-ATR regime switcher; C4 volatility-expansion straddle; C5 random-entry anchor) with 6-dimension distinctness scoring and §12 overfitting audit |
| [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md) | finalised evidence-pipeline design for C1 (frozen params, universe, timeframe, walk-forward fold design ~9 folds, per-fold + aggregate + financing + risk-diagnostic gates, no-lookahead checks, rejection criteria, required artifacts, future implementation branch name) |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md) | Phase B5 decision note — five helper-code options considered, all rejected with documented rationale; zero code added |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md) | sprint summary & handoff |

### CAMPAIGN_010 candidate scaffold (`research-asian-london-session-breakout-001`)

Candidate-scaffold sprint for **C1 — Asian-range / London-open
session breakout** (strategy `session_breakout 0.1.0-c010`,
campaign label `CAMPAIGN_010`). Adds the strategy module, the
`StrategyConfig.session_breakout` schema slot, the candidate
config YAML, 33 unit + structural-audit tests, and the
candidate's pre-commit / status / smoke / readiness docs.
**CANDIDATE SCAFFOLD ONLY — not approved for paper / demo / live.**
`configs/approved_strategies.yaml` remains `approved: []`;
CAMPAIGN_002 remains REJECT; the candidate is structurally
ready for a future evidence sprint to generate walk-forward
results + financing overlay + risk diagnostics. The 735-test
baseline (702 prior + 33 new) is preserved.

| document | what it is |
|---|---|
| [`ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md) | Phase 0 sprint plan + repo truth audit (verified preconditions, 702 baseline, all safety gates) |
| [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md) | machine-facing implementation spec: candidate identity, R1–R11 rule table, session window definitions with half-open intervals + midnight wrap, frozen parameter table (12 strategy params + 2 RiskConfig params), no-lookahead rules, H4/intraday limitation risks (DST, holidays), data + risk + financing + walk-forward interface assumptions, expected test cases (≥ 24 floor), explicit non-evidence warning |
| [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md) | candidate-pre-commit citing hypothesis verbatim, implementation + config files, frozen parameters, required local-only evaluation commands, required walk-forward / financing / risk artifacts, verbatim pass/fail gates from design §8–§15, explicit no-approval statement |
| [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md) | candidate-scaffold-only status (no verdict; no campaign report; no approval; safety state confirmed) |
| [`CAMPAIGN_010_SMOKE_RESULT.md`](CAMPAIGN_010_SMOKE_RESULT.md) | Phase 5 NON-EVIDENCE smokes: config-load PASS; signal-generation unit suite PASS (33 cases); walk-forward dry-run PASS (8-fold validated plan, ≥ 6 floor satisfied); local historical backtest BLOCKED (no SQLite store) |
| [`CAMPAIGN_010_WALK_FORWARD_READINESS.md`](CAMPAIGN_010_WALK_FORWARD_READINESS.md) | walk-forward integration readiness: harness plug-in READY; fold-by-fold sketch; missing adapters (only the per-fold backtest driver); data soft-blocker (data/ empty); strict gates restated |
| [`CAMPAIGN_010_FINANCING_RISK_READINESS.md`](CAMPAIGN_010_FINANCING_RISK_READINESS.md) | financing + portfolio-risk readiness: ESTIMATED-only via default_stress_rate_source(); per-pair TableRateSource diagnostic sample; MODELED refused at four layers; expected 0–1 rollover events per trade; risk-engine diagnostic checklist with note on conservative max_open_positions=1 |
| [`ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md) | sprint summary & handoff |

### CAMPAIGN_010 walk-forward evidence (`research-asian-london-session-breakout-walk-forward-001`)

Walk-forward evidence sprint that ran the full
`PREFERRED_CANDIDATE_EVALUATION_DESIGN` pipeline against the
`session_breakout 0.1.0-c010` candidate on the 7-pair × 6-year
real OANDA practice H4 universe. Verdict: **REJECT** —
`fold_pass_rate = 0/8`, `aggregate_expectancy_r = -0.0408`,
`profit_factor = 0.04`, `pairs_positive = 1/7` (USD_CHF only,
which flips to net negative under conservative-stress financing).
CAMPAIGN_010 reclassifies from `candidate-scaffold (no verdict)`
to `rejected`. `configs/approved_strategies.yaml` remains
`approved: []`; CAMPAIGN_002 remains REJECT and untouched.
Paper / demo / live remain blocked. No broker call, no credential
read, no engine edit.

| document | what it is |
|---|---|
| [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md) | Phase 0 repo truth audit + 8-phase sprint plan; baseline 735 pytests pass; data status (existing 7-pair × 6-year H4 store reused via gitignored symlink) |
| [`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md) | Phase 1 data provenance — per-pair counts, first/last bar timestamps, recorded raw/normalized SHA-256 prefixes; reconfirms `source=oanda-practice`; no rehydration this sprint |
| [`CAMPAIGN_010_WALK_FORWARD_PLAN.md`](CAMPAIGN_010_WALK_FORWARD_PLAN.md) | Phase 2 authoritative walk-forward plan — 8 folds rolling/frozen, 540/180/180/180 days, universe 2020-01-01 → 2026-05-20, `validate_plan()` PASS, `strategy_evidence=false` Pydantic-pinned |
| [`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md) | Phase 3 per-fold execution — 56 backtests (8 folds × 7 pairs) in 7.9 s, 2,791 trades, frozen-parameter assertion in runner, no implementation bug fixes required |
| [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) | Phase 4 formal verdict — REJECT against verbatim gates from `CAMPAIGN_010_PRECOMMIT_CHECKLIST.md` §10 (5 gates fail, 4 pass) |
| [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md) | Phase 5 financing overlay — ESTIMATED + `default_stress_rate_source()` (MODELED refused at four layers); 2,483 rollover events; cashflow_home_stress_total = -$55.69; USD_CHF flips +→- under stress |
| [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md) | Phase 6 risk diagnostics — concurrency structurally bounded; per-pair exposure under risk cap; 75.5 % time-stop exit; RiskEngine rejected 29.8 % of raw signals as cost-unsafe |
| [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md) | Phase 7 verifier capability assessment — verifier capability-locked to CAMPAIGN_002 trend_following; did NOT run for CAMPAIGN_010; would only matter for a hypothetical PASS (not for this REJECT) |
| [`CAMPAIGN_010_EVIDENCE_SUMMARY.md`](CAMPAIGN_010_EVIDENCE_SUMMARY.md) | Phase 8 one-page evidence summary — headline numbers, six-evidence-ladder status, committed artifact tree, safety state |
| [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md) (updated) | now reclassified `candidate-scaffold → rejected`; verdict, gates, evidence artifacts, safety state |
| [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md) | sprint summary & handoff |

### New candidate strategy discovery — Sprint 002 (`research-new-candidate-strategy-discovery-002`)

Second candidate-discovery sprint, opened after CAMPAIGN_010
(`session_breakout 0.1.0-c010`) was REJECTED. Re-scores the
prior shortlist (C2-C5) against the now-5 rejected baseline,
codifies rejected-family anti-overfit guardrails, and selects
**C5 — H4 random-entry diagnostic anchor (future CAMPAIGN_011)**
as the next preferred candidate. **Selection is not approval.**
The selected candidate is a null model by design and cannot be
paper-promoted; its purpose is to validate the full evidence
pipeline and establish a per-fold + aggregate falsifiability
floor that every subsequent C2 / C3 / C4 / new-family candidate
must beat by a meaningful margin. No strategy code, no backtest,
no broker call, no approval. The 735-test baseline is preserved.

| document | what it is |
|---|---|
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md) | Phase 0 audit + 8-phase sprint plan; verifies safety state at the close of CAMPAIGN_010's REJECT; baseline 735 pytests pass |
| [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md) | Phase 1 — formal closeout for `session_breakout 0.1.0-c010`; codifies which session-breakout parameters are off-limits to retune; binding cooldown rule against re-attempts |
| [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) | Phase 1 — cross-cutting anti-overfit guardrails for every future candidate; concrete illegitimate-vs-legitimate examples for each of the 7 disqualifier patterns; universe/stop/exit/data/financing/selection/verifier/approval guardrails |
| [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md) | Phase 2 — full scoring of C2 / C3 / C4 / C5 against the now-5 rejected families plus implementation complexity, engine compatibility, data availability, walk-forward compatibility, financing dependency, portfolio-risk implications, verifier feasibility, overfit risk, diagnostic value, paper-candidate suitability; blockers per candidate; recommendation = C5 |
| [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md) | Phase 3 — C5 selected as CAMPAIGN_011 (`random_entry_anchor 0.1.0-c011`); distinctness vs CAMPAIGN_002 + CAMPAIGN_010; why not parameter tuning; compatibility checks; success/rejection criteria; cooldown/re-attempt rule; C2 / C3 / C4 deferred (not abandoned) |
| [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md) | Phase 4 binding design — hypothesis, R1-R8 signal rules, frozen parameters (master_seed=20260523, entry_probability=0.05, atr_lookback=14, atr_multiple=2.0, max_bars=6), no-lookahead rules, config schema, walk-forward (inherits CAMPAIGN_010's 8-fold rolling/frozen 540/180/180/180), financing (ESTIMATED + conservative stress; MODELED refused), risk diagnostics (uniform-distribution expectations), verifier (extension recommended but not required for REJECT), rejection criteria + UNEXPECTED-PASS investigation playbook |
| [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md) | Phase 5a — future scaffold-branch prompt (`research-random-entry-diagnostic-anchor-001`); 8 phases; strategy module + config + ≥ 20 unit tests + research config + CAMPAIGN_011 docs + smoke; baseline 735 → ≥ 755 pytests; no backtest run |
| [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md) | Phase 5b — future evidence-branch prompt (`research-random-entry-diagnostic-anchor-walk-forward-001`); 9 phases mirroring CAMPAIGN_010 exactly; full walk-forward + financing + risk + verifier; expected verdict REJECT; UNEXPECTED-PASS playbook |
| [`NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md) | Phase 6 — five helper-code options considered, all rejected with documented rationale; zero code added; matches prior discovery sprint's identical no-helper decision |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md) | Phase 7 — sprint summary & handoff; final validation; recommended next branch is the scaffold sprint |

### CAMPAIGN_011 candidate scaffold (`research-random-entry-diagnostic-anchor-001`)

Scaffold sprint for **CAMPAIGN_011** / `random_entry_anchor
0.1.0-c011` — the C5 diagnostic-anchor null model. Adds the
strategy module, the `StrategyConfig.random_entry_anchor`
schema slot, the candidate config YAML, 36 unit + structural-audit
tests, and the CAMPAIGN_011 pre-commit / status / smoke /
readiness docs. **CANDIDATE SCAFFOLD ONLY; NULL MODEL BY DESIGN
— cannot be approved under any circumstance.** `configs/approved_strategies.yaml`
remains `approved: []`; CAMPAIGN_002 / CAMPAIGN_010 remain
REJECT; the candidate is structurally ready for the future
evidence sprint to generate `WalkForwardResults`. The 771-test
baseline (735 prior + 36 new) is preserved.

| document | what it is |
|---|---|
| [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md) | Phase 0 sprint plan + repo truth audit (verified preconditions, 735 baseline, all safety gates) |
| [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md) | Phase 1 binding spec — R1-R8 rule table; frozen parameters (master_seed=20260523, entry_probability=0.05, atr_lookback=14, atr_multiple=2.0, max_bars=6, trailing=None); no-lookahead invariants (seed input never contains close[t]/ATR); distribution/determinism expectations; null-model restrictions |
| [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md) | candidate pre-commit; null-model hypothesis verbatim; implementation + config files; frozen parameters; binding no-seed-optimization rule; required local-only evaluation commands; required walk-forward / financing / risk artifacts; verbatim gate vector inherited from CAMPAIGN_010 §10; unexpected-PASS investigation playbook |
| [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md) | candidate-scaffold-only status; null model / diagnostic anchor; no backtest verdict yet; no evidence campaign run; no strategy approval possible (by design) |
| [`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md) | Phase 5 NON-EVIDENCE smokes: config-load PASS; unit-test suite PASS (36 cases); walk-forward dry-run plan PASS (8 folds; matches CAMPAIGN_010); full repo regression 771 passes. Explicit "this is not evidence" framing |
| [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md) | scaffold readiness GREEN across all 11 dimensions; future evidence branch identity (`research-random-entry-diagnostic-anchor-walk-forward-001`); comparison vs CAMPAIGN_005 (strictly stronger anchor); pre-flight checklist |
| [`CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md) | walk-forward integration readiness; harness plug-in READY; fold table identical to CAMPAIGN_010 (8 folds); inherited gate vector; per-fold backtest invocation deferred to future evidence sprint |
| [`CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md) | financing + portfolio-risk readiness; ESTIMATED + conservative-stress; MODELED refused at 4 layers; expected uniform per-pair distribution and uniform session-of-day distribution (KEY contrast with CAMPAIGN_010); expected ~$30-60 cashflow_home_stress |
| [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md) | verifier capability-locked to CAMPAIGN_002; extension NOT required for the REJECT verdict (null model cannot be paper-promoted); recommended follow-up `infra-free-local-parity-verifier-random-entry-001` because deterministic seed allows EXACT (not WARN-band) corroboration |
| [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md) | sprint summary & handoff; recommended next branch is the evidence sprint |

### CAMPAIGN_011 walk-forward evidence (`research-random-entry-diagnostic-anchor-walk-forward-001`)

Walk-forward evidence sprint that ran the full
`PREFERRED_CANDIDATE_EVALUATION_DESIGN` pipeline against the
`random_entry_anchor 0.1.0-c011` null-model candidate on the
7-pair × 6-year real OANDA practice H4 universe. Verdict:
**REJECT (null model anchor)** — `fold_pass_rate = 0/8`,
`aggregate_expectancy_r = -0.0024` (≈ 0; null-model
signature), `profit_factor = 0.91` (≈ 1), `aggregate_return =
-0.53%` over 4 years, `pairs_positive = 3/7` (≈ uniform-noise
expectation of 3.5). USD_JPY expectancy literally **+0.0000**
to 4 dp (textbook random-walk signature). The REJECT is the
**expected and desired outcome** — it validates the evidence
pipeline by demonstrating the gates correctly REJECT a
known-zero-edge strategy with metrics consistent with random
expectations. CAMPAIGN_011 reclassifies from `scaffold-only`
to `rejected (null model anchor)`.
`configs/approved_strategies.yaml` remains `approved: []`;
CAMPAIGN_002 / CAMPAIGN_010 remain REJECT and untouched.
Paper / demo / live remain blocked. **CAMPAIGN_011 cannot be
approved by design** (null model). No broker call, no
credential read, no parameter tuning, no seed optimization.

| document | what it is |
|---|---|
| [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md) | Phase 0 repo truth audit + 10-phase sprint plan; baseline 771 pytests pass; data status (existing 7-pair × 6-year H4 store reused via gitignored symlink) |
| [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md) | Phase 1 data provenance — per-pair counts, first/last bar timestamps, recorded raw/normalized SHA-256 prefixes; ALL HASHES MATCH CAMPAIGN_010 verbatim (same physical store; identical data; the entry-signal comparison is on byte-for-byte identical candles) |
| [`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FORWARD_PLAN.md) | Phase 2 authoritative walk-forward plan — 8 folds rolling/frozen, 540/180/180/180 days, universe 2020-01-01 → 2026-05-20, IDENTICAL to CAMPAIGN_010's plan |
| [`CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_011_WALK_FORWARD_EXECUTION.md) | Phase 4 per-fold execution — 56 backtests (8 folds × 7 pairs) in 5.6s, 1,177 trades, frozen-parameter + master-seed (20260523) assertion held, no implementation bug fixes required |
| [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) | Phase 5 formal verdict — REJECT (null model anchor); 4 PnL-direction gates fail, 6 structural / dominance / financing gates pass; metrics statistically consistent with random/no-edge expectations |
| [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md) | Phase 6 financing overlay — ESTIMATED + `default_stress_rate_source()` (MODELED refused at four layers); 1,080 rollover events; cashflow_home_stress_total = -$24.38; USD_JPY flips +→- under stress; per-trade cost (-$0.023/event) consistent with CAMPAIGN_010 (-$0.022/event) |
| [`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md) | Phase 7 risk diagnostics — per-pair ratio max/min = 1.65 (random-uniform vs CAMPAIGN_010's 12.0); session diffuse across all 4 UTC buckets (no concentration > 50%; KEY contrast vs CAMPAIGN_010's 100% London); 79% time-stop exit (matches CAMPAIGN_010); 8/8 pipeline sanity checks pass |
| [`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md) | Phase 8 verifier capability assessment — verifier capability-locked to CAMPAIGN_002; did NOT run for CAMPAIGN_011; not required for null-model REJECT; recommended follow-up `infra-free-local-parity-verifier-random-entry-001` (uniquely valuable because deterministic-seed → EXACT, not WARN-band, corroboration is possible) |
| [`CAMPAIGN_011_EVIDENCE_SUMMARY.md`](CAMPAIGN_011_EVIDENCE_SUMMARY.md) | Phase 9 one-page evidence summary — headline numbers, null-model interpretation, falsifiability floor for future candidates, six-evidence-ladder status, comparison to CAMPAIGN_010 |
| [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md) (updated) | now reclassified `scaffold-only → rejected (null model anchor)`; verdict, gates, evidence artifacts, safety state |
| [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md) | sprint summary & handoff |

### New candidate strategy discovery — Sprint 003 (`research-new-candidate-strategy-discovery-003`)

Third candidate-discovery sprint, opened after CAMPAIGN_011
(`random_entry_anchor 0.1.0-c011`) was REJECTED as the
expected/desired null-model anchor. Codifies CAMPAIGN_011 as a
**quantitative falsifiability floor** (aggregate expectancy
−0.0024 R, profit factor 0.91, fold pass rate 0/8, pairs
positive 3/7, return −0.53 % over 4 years; USD_JPY expectancy
literally +0.0000) and defines an "indistinguishable from null"
band + "meaningful improvement over null" margins that every
future real-edge candidate must beat. Re-scores the remaining
shortlist (C2 / C3 / C4 / new-family) against the now-6 rejected
baseline (5 prior + CAMPAIGN_011 null anchor), confirms C3 has
NONE HARD blockers because the H4→D1AGG aggregator already
exists (`src/forex_bot/backtesting/d1_aggregation.py`), and
selects **C3 — Daily-ATR-percentile regime switcher (future
CAMPAIGN_012)** as the next preferred real candidate.
**Selection is not approval.** The selected candidate is
designed but not yet implemented; the discovery output is two
binding future-branch specs (scaffold + evidence). No strategy
code, no backtest, no broker call, no approval. The 771-test
baseline is preserved.

| document | what it is |
|---|---|
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md) | Phase 0 audit + 9-phase sprint plan; verifies safety state at the close of CAMPAIGN_011's REJECT; confirms D1AGG infrastructure already exists; baseline 771 pytests pass |
| [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) | Phase 1 — codifies CAMPAIGN_011's verbatim metrics as a quantitative falsifiability floor; defines "indistinguishable from null" band (±0.005 R / ±0.10 PF / ±2 pp / ±1 pair) and "meaningful improvement over null" margins (≥+0.0524 R / ≥+0.19 PF / ≥+5.5 pp / ≥+1 pair / 100% fold pass); 7 anti-overfit rules; binds future scaffold pre-commit + evidence verdict docs to include null-baseline reference / comparison sections |
| [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md) | Phase 2 — full scoring of C2 / C3 / C4 against the now-6 rejected baseline (incl. CAMPAIGN_011 null anchor); C2 blocked (MODELED financing); C3 NONE HARD (D1AGG infra already exists); C4 blocked (engine paired-entry); recommendation = C3 |
| [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md) | Phase 3 — C3 feasibility deep dive; frozen parameters pre-committed BEFORE any code (`daily_atr_lookback=14`, `regime_lookback_days=60`, `regime_percentile_threshold=0.70`, `min_close_move_atr_fraction=0.25`, `trend_lookback_h4_bars=4`); 6 leakage risks with concrete mitigations; safe implementation pattern in pseudocode using `aggregate_h4_to_d1`; distinctness vs every rejected family ≥5/6; feasibility GREEN |
| [`NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md) | Phase 4 — C3 selected as `regime_switcher_atr_percentile 0.1.0-c012` (CAMPAIGN_012); future branches `research-regime-switcher-atr-percentile-001` (scaffold) + `research-regime-switcher-atr-percentile-walk-forward-001` (evidence); distinctness tables vs CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 all 5/6; compatibility checks all GREEN; C2 / C4 deferred (not abandoned) |
| [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md) | Phase 5 binding design — R1-R8 signal rules (warm-up 500 bars; regime via `aggregate_h4_to_d1` + Wilder ATR-14 + trailing-60 P70; H4 ATR fail-closed; close[t] vs close[t-4] trend + ATR-fraction filter; ATR-stop placement; spread delegated; emit deterministic Signal); 11 no-lookahead invariants; `RegimeSwitcherAtrPercentileStrategyConfig` Pydantic schema; ≥25 unit tests planned; walk-forward inherits CAMPAIGN_010 §10 + adds null-baseline comparison gate; `RESEARCH_PASS_UNAPPROVED` classification rule |
| [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md) | Phase 6a — future scaffold-branch prompt (`research-regime-switcher-atr-percentile-001`); 8 phases; strategy module + config + ≥ 25 unit tests + research config + CAMPAIGN_012 docs + smoke; baseline 771 → ≥ 796 pytests; no backtest run |
| [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md) | Phase 6b — future evidence-branch prompt (`research-regime-switcher-atr-percentile-walk-forward-001`); 9 phases mirroring CAMPAIGN_011 exactly; full walk-forward + financing + risk + verifier; verdict options REJECT / REJECT (indistinguishable from null) / RESEARCH_PASS_UNAPPROVED / BLOCKED; UNEXPECTED-PASS 5-step protocol |
| [`NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md) | Phase 7 — six helper-code options considered, all rejected with documented rationale; zero code added; matches both prior discovery sprints' identical no-helper decision |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md) | Phase 8 — sprint summary & handoff; final validation; recommended next branch is the scaffold sprint `research-regime-switcher-atr-percentile-001` |

### CAMPAIGN_012 candidate scaffold (`research-regime-switcher-atr-percentile-001`)

Scaffold sprint for **CAMPAIGN_012** /
`regime_switcher_atr_percentile 0.1.0-c012` — the C3 daily-ATR-percentile
regime switcher selected by the
`research-new-candidate-strategy-discovery-003` sprint. Adds the strategy
module (R1-R8 per binding spec), the
`StrategyConfig.regime_switcher_atr_percentile` schema slot, 47 unit +
structural-audit tests, the candidate config YAML, and the CAMPAIGN_012
pre-commit / status / readiness / smoke docs. **CANDIDATE SCAFFOLD
ONLY — NOT APPROVED.** `configs/approved_strategies.yaml` remains
`approved: []`; CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 all remain
REJECT; the candidate is structurally ready for the future evidence
sprint to generate `WalkForwardResults`. The 818-test baseline
(771 prior + 47 new) is preserved. The future evidence sprint must
beat the CAMPAIGN_011 null-baseline floor (≥ +0.0524 R aggregate
expectancy, ≥ +0.19 PF, ≥ +5.5 pp pairs-positive, ≥ +1 pair, 100 %
fold pass rate) to count as evidence of an edge; "indistinguishable
from null" (within ± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair) is
REJECTED.

| document | what it is |
|---|---|
| [`REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md) | Phase 0 sprint plan + repo truth audit (verified 771 baseline + base commit `384314a` + D1AGG infra present + clean slate for CAMPAIGN_012) |
| [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md) | Phase 1 binding spec — R1-R8 rule table; 12 frozen parameters (`atr_lookback=14`, `atr_stop_multiple=2.0`, `max_bars_in_trade=6`, `trailing_stop_atr_multiple=None`, `daily_atr_lookback=14`, `regime_lookback_days=60`, `regime_percentile_threshold=0.70`, `min_close_move_atr_fraction=0.25`, `trend_lookback_h4_bars=4`); 15 no-lookahead invariants; 11 fail-closed conditions; 40 expected tests |
| [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md) | candidate pre-commit; hypothesis verbatim; implementation files + frozen parameters + no-lookahead checklist; D1AGG completed-day rule; rolling percentile rule; binding null-baseline comparison gate vs CAMPAIGN_011; required walk-forward / financing / risk artifacts; verbatim gate vector inherited from CAMPAIGN_010 §10 + CAMPAIGN_011 §11; unexpected-PASS 5-step escalation protocol |
| [`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md) | candidate-scaffold-only status; no backtest verdict yet; no evidence campaign run; no strategy approval (cannot be approved by any research sprint); CAMPAIGN_002 / 010 / 011 all REJECT relationship; why this is a real candidate (deterministic, directional, distinct) but not approved |
| [`REGIME_SWITCHER_ATR_PERCENTILE_READINESS.md`](REGIME_SWITCHER_ATR_PERCENTILE_READINESS.md) | scaffold readiness GREEN across all 21 dimensions; future evidence branch identity `research-regime-switcher-atr-percentile-walk-forward-001`; data expectations; known limitations (verifier lock; MODELED financing); D1AGG usage; null-baseline comparison; why this is a real candidate but not approved |
| [`CAMPAIGN_012_SMOKE_RESULT.md`](CAMPAIGN_012_SMOKE_RESULT.md) | Phase 5 NON-EVIDENCE smokes: config-load PASS; unit-test suite PASS (47 cases); walk-forward dry-run plan PASS (8 folds; matches CAMPAIGN_010 / 011 verbatim); full repo regression 818 passes. Explicit "this is not evidence" framing; dry-run output written to /tmp and NOT committed |
| [`CAMPAIGN_012_WALK_FORWARD_READINESS.md`](CAMPAIGN_012_WALK_FORWARD_READINESS.md) | future-evidence walk-forward plan (inherited verbatim from CAMPAIGN_010 / 011: rolling, frozen, 540/180/180/180 days, 2020-01-01 → 2026-05-20, expected 8 folds); per-fold + aggregate gate vector; binding null-baseline comparison gate; expected artifact paths |
| [`CAMPAIGN_012_FINANCING_RISK_READINESS.md`](CAMPAIGN_012_FINANCING_RISK_READINESS.md) | future-evidence financing overlay (ESTIMATED + conservative stress; MODELED refused at 4 layers; not lifted) + portfolio-risk diagnostics (regime-period clustering as the signature; expected session-of-day diffuse across 4 UTC buckets like CAMPAIGN_011); per-instrument concurrency = 1 |
| [`CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md) | future-evidence verifier coverage; current capability lock to CAMPAIGN_002 / `trend_following`; not required for REJECT; required only on RESEARCH_PASS_UNAPPROVED via the suggested follow-up sprint `infra-free-local-parity-verifier-regime-switcher-001` |
| [`REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md) | sprint summary & handoff; final validation; recommended next branch is the evidence sprint `research-regime-switcher-atr-percentile-walk-forward-001` |

### CAMPAIGN_012 walk-forward evidence (`research-regime-switcher-atr-percentile-walk-forward-001`)

Walk-forward evidence sprint that ran the full
`PREFERRED_CANDIDATE_EVALUATION_DESIGN` pipeline against the
`regime_switcher_atr_percentile 0.1.0-c012` C3 daily-ATR-percentile
regime-switcher candidate on the 7-pair × 6-year real OANDA practice
H4 universe. Verdict: **REJECT** — 5 of 8 inherited aggregate gates
fail (`fold_pass_rate = 0/8`; `aggregate_expectancy_r = −0.0521 R`;
`profit_factor = 0.034`; `pairs_positive = 1/7`); aggregate return
`−43.52 %` over 4 years. **Markedly worse than CAMPAIGN_011 null
baseline** on every binding axis (expectancy −0.0497 R lower, PF
−0.876 lower, return −42.99 pp lower, pairs −2 lower) — well outside
the symmetric ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair
indistinguishability band; classification is **REJECT** (not
`REJECT_INDISTINGUISHABLE_FROM_NULL`, because the divergence is in
the WORSE direction). The regime gate amplified trade count (3,726 vs
1,177) without improving signal quality, accumulating cost drag.
USD_JPY's +0.0004 R is the same near-exact-zero random-walk floor
CAMPAIGN_011 surfaced. CAMPAIGN_012 reclassifies from `scaffold-only`
to `rejected`. `configs/approved_strategies.yaml` remains
`approved: []`; CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 remain
REJECT and untouched. Paper / demo / live remain blocked.
**CAMPAIGN_012 cannot be approved.** No broker call, no credential
read, no parameter tuning.

| document | what it is |
|---|---|
| [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md) | Phase 0 repo truth audit + 10-phase evidence-sprint plan; baseline 818 pytests pass; data status (existing 7-pair × 6-year H4 store reused via gitignored symlink) |
| [`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md) | Phase 1 data provenance — per-pair counts, first/last bar timestamps, recorded raw/normalized SHA-256 prefixes; ALL HASHES MATCH CAMPAIGN_010 / CAMPAIGN_011 verbatim (same physical store; identical data; the entry-signal comparison is on byte-for-byte identical candles) |
| [`CAMPAIGN_012_WALK_FORWARD_PLAN.md`](CAMPAIGN_012_WALK_FORWARD_PLAN.md) | Phase 2 authoritative walk-forward plan — 8 folds rolling/frozen, 540/180/180/180 days, universe 2020-01-01 → 2026-05-20, IDENTICAL to CAMPAIGN_010 / 011 plans |
| [`CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_012_WALK_FORWARD_EXECUTION.md) | Phase 4 per-fold execution — 56 backtests (8 folds × 7 pairs) in ~2,022 s, 3,726 trades, frozen-parameter assertion in runner, no implementation bug fixes required |
| [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md) | Phase 5 formal verdict — REJECT; 5 of 8 inherited aggregate gates fail; CAMPAIGN_011 null-baseline comparison classifies REJECT (not REJECT_INDISTINGUISHABLE_FROM_NULL because metrics diverge from null in WORSE direction) |
| [`CAMPAIGN_012_FINANCING_OVERLAY.md`](CAMPAIGN_012_FINANCING_OVERLAY.md) | Phase 6 financing overlay — ESTIMATED + `default_stress_rate_source()` (MODELED refused at four layers); 3,404 rollover events; cashflow_home_stress_total = −$65.07; no pair flip; `conservative_stress_run_does_not_flip_verdict` PASSES (verdict already REJECT pre-financing) |
| [`CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md) | Phase 7 risk diagnostics — per-pair ratio max/min = 1.60 (uniform; close to CAMPAIGN_011's 1.65 vs CAMPAIGN_010's 12.0); session distribution diffuse across all 4 UTC buckets (no concentration > 50 %; like CAMPAIGN_011); 79.3 % time-stop exit; 8 / 8 pipeline sanity checks PASS; RiskEngine rejected 42.7 % of raw signals (SPREAD_TOO_WIDE 2013, SESSION_BLOCKED 758) |
| [`CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md) | Phase 8 verifier capability assessment — verifier capability-locked to CAMPAIGN_002 / `trend_following`; did NOT run for CAMPAIGN_012; not required for REJECT; recommended follow-up `infra-free-local-parity-verifier-regime-switcher-001` **deferred indefinitely** (no paper-promotion candidate to corroborate) |
| [`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md) | Phase 9 one-page evidence summary — headline numbers, null-baseline interpretation, regime-switcher interpretation (hypothesis falsified), comparison to prior REJECT campaigns (CAMPAIGN_012 has the worst aggregate return of any campaign to date) |
| [`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md) (updated) | now reclassified `scaffold-only → rejected`; verdict, gates, evidence artifacts, safety state |
| [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md) | sprint summary & handoff |

### New candidate strategy discovery — Sprint 004 (`research-new-candidate-strategy-discovery-004`)

Fourth candidate-discovery sprint, opened after CAMPAIGN_012
(`regime_switcher_atr_percentile 0.1.0-c012`) was REJECTED.
Codifies CAMPAIGN_012's rejection closeout (off-limits parameter
surface + indefinite cooldown for the regime-switcher family);
adds 5 new disqualifying overfitting patterns (H–L) to the base
rejected-family guardrails (forbidding same-regime-different-
threshold retunes, trend-filter lookback sweeps, rank-inversion
"different cutoff" variants, rejected-family stacks, and per-fold-
artifact-driven family selection); re-scores the now-7 rejected
baseline (5 prior + CAMPAIGN_011 null + CAMPAIGN_012 real) against
4 deferred candidates (C2 / C4) + 4 infrastructure paths
(financing-MODELED-capture, paired-entry-engine-support, verifier-
extension, ruff-cleanup); proposes 4 genuinely-new candidate
families (C6 / C7 / C8 / C9); selects **C6 — Cross-Pair Currency
Strength Rotation** for future **CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`** as the next
preferred real candidate. **Selection is not approval.** The
selected candidate is designed but not yet implemented; the
discovery output is two binding future-branch specs (scaffold +
evidence). No strategy code, no backtest, no broker call, no
approval. The 818-test baseline is preserved.

| document | what it is |
|---|---|
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md) | Phase 0 audit + 10-phase sprint plan; verifies safety state at the close of CAMPAIGN_012's REJECT; baseline 818 pytests pass |
| [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md) | Phase 1 — formal closeout for `regime_switcher_atr_percentile 0.1.0-c012`; codifies which regime-switcher parameters are off-limits to retune (12 frozen parameters + 5 illegitimate extension patterns); binding cooldown rule against the regime-switcher family until a future human explicitly authorizes a "materially different" thesis |
| [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) | Phase 2 — additive addendum to the base guardrails doc; adds Patterns H (same regime gate, different threshold), I (same trend filter, different lookback), J (same percentile, different cutoff), K (rejected-family stack), L (per-fold-artifact-driven family selection); "genuinely new" criteria (7 axes) any candidate must satisfy after the now-7 rejected baseline |
| [`NEXT_DIRECTION_REASSESSMENT_004.md`](NEXT_DIRECTION_REASSESSMENT_004.md) | Phase 3 — 15-axis scoring of 7 paths (C2 / C4 / C6+ + infra-A/B/C/D); recommends discovery-driven C6+ family selection (zero blockers; evaluable honestly today); fallback to infra-A if Phase 4 fails |
| [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md) | Phase 4 — shortlist of 4 genuinely-new families (C6 cross-pair currency strength rotation; C7 calendar-event window anomaly; C8 multi-window vol-compression breakout; C9 time-of-day cost-adjusted MR on spreads); 13 disqualified variants documented |
| [`NEXT_PREFERRED_DIRECTION_004.md`](NEXT_PREFERRED_DIRECTION_004.md) | Phase 5 — C6 selected as `cross_pair_currency_strength_rotation 0.1.0-c013` (CAMPAIGN_013); future branches `research-cross-pair-currency-strength-rotation-001` (scaffold) + `research-cross-pair-currency-strength-rotation-walk-forward-001` (evidence); distinctness vs every rejected family 6/6; Patterns H–L explicitly cleared; C7/C8/C9 and all 4 infra paths deferred (not abandoned) |
| [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md) | Phase 6 binding design — currency-strength feature definition (8 currencies; USD-base / USD-quote sign convention; USD strength = `−mean(non-USD)`); R1-R8 signal rules; 9 frozen parameters (`currency_strength_lookback_bars=24`, `rank_gap_threshold=4`, etc.); 12 no-lookahead invariants; `CrossPairCurrencyStrengthRotationStrategyConfig` schema; ≥ 30 unit tests planned; walk-forward inherits CAMPAIGN_010 §10 + adds null-baseline comparison gate; critical multi-pair-runner integration contract for the evidence sprint; cross-pair concurrent-rejection rate as CAMPAIGN_013-specific risk diagnostic |
| [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md) | Phase 7a — future scaffold-branch prompt (`research-cross-pair-currency-strength-rotation-001`); 8 phases; strategy module + config + ≥ 30 unit tests + research config + CAMPAIGN_013 docs + smoke; baseline 818 → ≥ 848 pytests; no backtest run |
| [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md) | Phase 7b — future evidence-branch prompt (`research-cross-pair-currency-strength-rotation-walk-forward-001`); 10 phases mirroring CAMPAIGN_012 evidence sprint; full walk-forward + financing + risk + verifier; verdict options REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / RESEARCH_PASS_UNAPPROVED / BLOCKED; binding cross-pair-runner integration contract |
| [`NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md) | Phase 8 — seven helper-code options considered, all rejected with documented rationale; zero code added; matches all three prior discovery sprints' identical no-helper decision |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md) | Phase 9 — sprint summary & handoff; final validation; recommended next branch is the scaffold sprint `research-cross-pair-currency-strength-rotation-001` |

### CAMPAIGN_013 candidate scaffold (`research-cross-pair-currency-strength-rotation-001`)

Scaffold sprint for **CAMPAIGN_013** /
`cross_pair_currency_strength_rotation 0.1.0-c013` — the C6
cross-pair currency-strength rotation candidate selected by the
`research-new-candidate-strategy-discovery-004` sprint. Adds the
strategy module (R1-R8 per binding spec), the
`StrategyConfig.cross_pair_currency_strength_rotation` schema slot,
57 unit + structural-audit tests, the candidate config YAML, and
the CAMPAIGN_013 pre-commit / status / readiness / smoke docs.
**CANDIDATE SCAFFOLD ONLY — NOT APPROVED.**
`configs/approved_strategies.yaml` remains `approved: []`;
CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 / CAMPAIGN_012 all remain
REJECT; the candidate is structurally ready for the future evidence
sprint to generate `WalkForwardResults`. The 875-test baseline
(818 prior + 57 new) is preserved. The future evidence sprint must
beat the CAMPAIGN_011 null-baseline floor (≥ +0.0524 R aggregate
expectancy, ≥ +0.19 PF, ≥ +5.5 pp pairs-positive, ≥ +1 pair, 100 %
fold pass rate) to count as evidence of an edge; "indistinguishable
from null" (within ± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair) is
REJECTED. **Critical CAMPAIGN_013-specific evidence-runner
requirement:** must implement the cross-pair runner integration
contract (align all 7 pairs' completed H4 closes to a common index;
inject as `cross_pair_closes` into each pair's `strategy_config`).

| document | what it is |
|---|---|
| [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md) | Phase 0 sprint plan + repo truth audit (verified 818 baseline + base commit `ff34e96` + clean slate for CAMPAIGN_013) |
| [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md) | Phase 1 binding spec — R1-R8 rule table; 9 frozen parameters (`currency_strength_lookback_bars=24`, `rank_gap_threshold=4`, `atr_lookback=14`, `atr_stop_multiple=2.0`, `max_bars_in_trade=6`, `trailing_stop_atr_multiple=None`); 7-pair universe + 8-currency sign convention (USD-base = +log_return; USD-quote = −log_return; USD = −mean(non-USD)); 14 no-lookahead invariants; 10 fail-closed conditions; 51 expected tests |
| [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md) | candidate pre-commit; hypothesis verbatim; implementation files + frozen parameters + no-lookahead checklist; cross-pair-closes contract; currency-strength sign convention; rank-gap rule (inclusive at threshold); binding null-baseline comparison gate vs CAMPAIGN_011; required walk-forward / financing / risk artifacts; verbatim gate vector inherited from CAMPAIGN_010 / 011 / 012; unexpected-PASS 5-step escalation protocol |
| [`CAMPAIGN_013_STATUS.md`](CAMPAIGN_013_STATUS.md) | candidate-scaffold-only status; no backtest verdict yet; no evidence campaign run; no strategy approval (cannot be approved by any research sprint); CAMPAIGN_002 / 010 / 011 / 012 all REJECT relationship; why this is a real candidate (deterministic, directional, cross-pair structure never tested before) but not approved |
| [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md) | scaffold readiness GREEN across 18 dimensions; future evidence branch identity `research-cross-pair-currency-strength-rotation-walk-forward-001`; data expectations; known limitations (verifier lock; MODELED financing; MAX_OPEN_POSITIONS_EXCEEDED rejection from cross-pair concurrent signals — KNOWN behavior, NOT a bug); binding cross-pair runner integration requirement; null-baseline comparison; why this is a real candidate but not approved |
| [`CAMPAIGN_013_SMOKE_RESULT.md`](CAMPAIGN_013_SMOKE_RESULT.md) | Phase 5 NON-EVIDENCE smokes: config-load PASS; unit-test suite PASS (57 cases); walk-forward dry-run plan PASS (8 folds; matches CAMPAIGN_010 / 011 / 012 verbatim); full repo regression 875 passes. Explicit "this is not evidence" framing; dry-run output written to `/tmp` and NOT committed |
| [`CAMPAIGN_013_WALK_FORWARD_READINESS.md`](CAMPAIGN_013_WALK_FORWARD_READINESS.md) | future-evidence walk-forward plan (inherited verbatim from CAMPAIGN_010 / 011 / 012: rolling, frozen, 540/180/180/180 days, 2020-01-01 → 2026-05-20, expected 8 folds); per-fold + aggregate gate vector; binding null-baseline comparison gate; **binding cross-pair runner integration contract**; expected artifact paths |
| [`CAMPAIGN_013_FINANCING_RISK_READINESS.md`](CAMPAIGN_013_FINANCING_RISK_READINESS.md) | future-evidence financing overlay (ESTIMATED + conservative stress; MODELED refused at 4 layers; not lifted) + portfolio-risk diagnostics (standard battery PLUS CAMPAIGN_013-specific: rank-gap distribution, simultaneous-signal frequency, MAX_OPEN_POSITIONS_EXCEEDED rejection rate, currency-rank flip rate, pair-direction conflict rate); per-instrument concurrency = 1 |
| [`CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md) | future-evidence verifier coverage; current capability lock to CAMPAIGN_002 / `trend_following`; not required for REJECT; required only on RESEARCH_PASS_UNAPPROVED via the suggested follow-up sprint `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001` |
| [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md) | sprint summary & handoff; final validation; recommended next branch is the evidence sprint `research-cross-pair-currency-strength-rotation-walk-forward-001` |

## Research-freeze documents (this branch)

| document | what it is |
|---|---|
| [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md) | the freeze decision — **NO APPROVED TRADING STRATEGY** |
| [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md) | per-strategy status registry (all paper/demo/live = NO) |
| [`docs/research/FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) | unauthorized menu of possible future directions |
| [`docs/research/EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) | this index |
| [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml) | machine-enforced approved-strategy registry (empty) |

## Machine-readable manifest & validation

- [`docs/research/EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json) — a
  machine-readable index of all nine campaigns: report path, strategy
  family, data source, verdict, key metrics, commit hash, artifact
  folder, whether the test window was opened, whether the RiskEngine was
  used, the financing treatment, and `strategy_approved` (false for
  every campaign). Manifest version 2 adds a `diagnostic_artifacts`
  array — the diagnostic / parity outputs above, each carrying
  `strategy_evidence: false`.
- [`scripts/validate_research_archive.py`](../../scripts/validate_research_archive.py)
  audits the archive's integrity. Run it any time — before trusting a
  report, after editing docs, or in CI:

  ```bash
  .venv/bin/python scripts/validate_research_archive.py
  ```

  It checks that the approved-strategy registry is empty, that every
  report and artifact folder named in the manifest exists, that no
  campaign is marked approved, that every verdict is a non-approval
  verdict, that each report corroborates its manifest verdict, that
  every declared diagnostic artifact exists and is not marked strategy
  evidence, that every link in this index resolves, and that no
  committed artifact contains a credential-shaped string. The check
  logic lives in
  `forex_bot.research_archive` and is unit-tested by
  `tests/unit/test_validate_research_archive.py`.

## How to read the evidence

- **Verdicts are bright lines.** Every campaign fixed its gates in a
  pre-commit *before* running. A REJECT means a pre-committed gate
  failed; gates were never relaxed afterward.
- **Test-window discipline.** The 2025–2026 window was a sealed
  lockbox, opened only if a screening gate passed. For 007/008/009 it
  was never opened.
- **R is per-trade expectancy** in units of initial risk. Negative R
  means the strategy lost money per trade after real costs.
- **CAMPAIGN_001 is not evidence** about edge — it ran on synthetic
  candles before OANDA credentials were configured, and exists only as
  harness validation.

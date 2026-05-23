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

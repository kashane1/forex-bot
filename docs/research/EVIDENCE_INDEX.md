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
`infra-data-parity-001`, and `oanda-practice-readonly-001` sprints.
**These are not campaign evidence.**
They are mechanical plumbing checks and independent-verification
inputs — none measures, implies, or can establish a strategy edge, and
none can approve anything. The machine-readable manifest lists them
under `diagnostic_artifacts` with `strategy_evidence: false`, enforced
by `scripts/validate_research_archive.py`.

| artifact | what it is |
|---|---|
| [`backtests/diagnostics/d1agg_next_open_smoke.md`](../../backtests/diagnostics/d1agg_next_open_smoke.md) | D1AGG + next-bar-open fill-path smoke (single-pair) |
| [`backtests/diagnostics/d1agg_next_open_six_pair_smoke.md`](../../backtests/diagnostics/d1agg_next_open_six_pair_smoke.md) | D1AGG + next-bar-open smoke across the six majors |
| [`research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md`](../../research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md) | Lean-parity export bundle for the CAMPAIGN_002 H4 baseline |

Supporting infrastructure docs:
[fill-timing model](FILL_TIMING_MODEL.md) ·
[Lean parity execution](LEAN_PARITY_EXECUTION_GUIDE.md) ·
[Lean parity local status](LEAN_PARITY_LOCAL_STATUS.md) ·
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

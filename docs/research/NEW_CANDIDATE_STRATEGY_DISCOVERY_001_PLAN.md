# New Candidate Strategy Discovery — Sprint 001 Plan

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-001`
`strategy_evidence: false`

Plan for a **docs-only design sprint** that produces the proposal,
shortlist, and evaluation design for a future strategy candidate
distinct from CAMPAIGN_002 and the other four already-rejected
strategy families. **This sprint does not write a strategy, does
not run a campaign, does not approve anything, and does not enable
paper / demo / live.**

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. The discovery sprint emits design
> docs only. Every artifact carries `strategy_evidence: false`.

## 1. Scope

This sprint is **PATH B** from
[`NEXT_BRANCH_DECISION_AUDIT.md`](NEXT_BRANCH_DECISION_AUDIT.md)
§7. It picks up §5.1 ("New strategy family (highest-leverage)")
of
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md),
which the project recommended only after the walk-forward harness
(§5.2) and the financing model (§5.4) were both in place. Both
prerequisites are now committed and tested (702 tests pass).

The sprint produces:

- A **protocol** the discovery itself must follow
  ([`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md))
  — non-goals, what "meaningfully distinct" means, the disallowed
  reuse / overfitting patterns, and the evidence required of any
  future candidate.
- A **strategy-framework inventory**
  ([`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md))
  — what already exists in `src/forex_bot/strategies/`, what a new
  candidate would need from the existing infrastructure
  (walk-forward harness, financing calculator, RiskEngine, reporting,
  data store), and what gaps would block a future scaffold sprint.
- A **shortlist of 3–5 candidate strategy families**
  ([`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md))
  — each with hypothesis, distinctness vs. CAMPAIGN_002, required
  features, overfitting risks, frozen parameters, walk-forward plan,
  financing sensitivity, and rejection criteria. The shortlist picks
  exactly one preferred candidate for the next sprint.
- A **preferred-candidate evaluation design**
  ([`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md))
  — frozen parameter set, allowed universe, timeframe, walk-forward
  fold plan, per-fold / aggregate / financing / risk gates, no-
  lookahead checks, rejection criteria, required artifacts, **future
  implementation branch name** — but **does not run anything**.
- Optionally, a small **docs-only schema helper** for candidate
  proposal docs (Phase B5). Strategy code is out of scope.
- A **sprint summary**
  ([`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md))
  and corresponding updates to the evidence index / manifest.

## 2. Non-goals

These are explicitly **out of scope** for this sprint:

- **No strategy implementation.** No new module under
  `src/forex_bot/strategies/`; no edits to the existing four
  rejected families.
- **No backtest run.** No campaign launched, no `BacktestEngine`
  invocation against any new candidate, no test-window opening.
- **No CAMPAIGN_002 tuning, revival, or parameter search.**
- **No approval.** `configs/approved_strategies.yaml` is not
  touched (verified verbatim in Phase B6).
- **No paper-loop, demo-loop, or live-loop changes.** The
  refusal-path tests stay green and are re-run in Phase B6.
- **No broker / OANDA call.** No `.env` read. No credentials
  printed. No new endpoint surface enabled.
- **No QuantConnect / LEAN.** Retirement stands.
- **No engine-PnL edit.** The bespoke `BacktestEngine` and
  `src/forex_bot/financing.py` are frozen for this sprint.
- **No new strategy code in production paths**, even as a
  "non-evidence scaffold". If a Phase B5 helper is added at all, it
  is a docs-only schema validator for proposal documents.
- **No new external dependency.**
- **No paid data source procurement.** All design must be
  feasible against the data sources the repo already has.

## 3. Why this direction and not the alternatives

The prompt's PATH B decision rule fires precisely because:

- Walk-forward harness is complete
  ([`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)).
- All five financing sprints are complete
  ([`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md),
  [`FINANCING_RATE_SOURCE_FIXTURES_STATUS.md`](FINANCING_RATE_SOURCE_FIXTURES_STATUS.md),
  [`FINANCING_RECONCILIATION_TOOLING_STATUS.md`](FINANCING_RECONCILIATION_TOOLING_STATUS.md),
  [`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md),
  [`FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md)).
- The remaining financing gap (MODELED + engine-PnL integration +
  real captured data) requires either a separately-authorized
  credentialed practice run or human MODELED approval — outside
  this worktree's authorization envelope.

Continuing infrastructure sprints (e.g. another financing pass,
more parity work, deployment plumbing) would have nothing new to
ship today. Designing a candidate distinct from the four rejected
families is the highest-leverage research direction that respects
the freeze.

## 4. Phases & deliverables

Each phase commits its own artifact before the next begins. A
blocked phase documents the blocker and the sprint continues with
the next independent safe phase.

### Phase B1 — protocol & exclusions (this commit also includes the plan you are reading)

| deliverable | type |
|---|---|
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md) | docs (this file) |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md) | docs |

### Phase B2 — inventory existing strategy / research framework

| deliverable | type |
|---|---|
| [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md) | docs |

Inspects (read-only): `src/forex_bot/strategies/`, the bespoke
`BacktestEngine`, the RiskEngine surfaces, the candle / instrument
data store, the walk-forward harness public API, the financing
calculator public API, and the campaign / pre-commit / report doc
templates. Records what a new candidate would need from each.

### Phase B3 — propose candidate families

| deliverable | type |
|---|---|
| [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md) | docs |

3–5 candidate families. Each entry covers: hypothesis, why
distinct from CAMPAIGN_002 (and from the other three already-tested
families), required indicators / features, data requirements,
known failure modes, overfitting risks, frozen parameters,
walk-forward plan, financing sensitivity, risk-engine implications,
rejection criteria. Picks exactly one preferred candidate for
Phase B4.

### Phase B4 — evaluation design for the preferred candidate

| deliverable | type |
|---|---|
| [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md) | docs |

Designs but **does not run** the evidence pipeline: candidate
name, hypothesis, frozen parameter set, allowed universe,
timeframe, data requirements, walk-forward fold design, minimum
fold count, per-fold gates, aggregate gates, financing overlay
gates, risk-engine diagnostics gates, no-lookahead checks,
minimum trade count, dominance checks, rejection criteria,
required artifacts, future implementation branch name.

### Phase B5 — optional safe helper scaffolding (docs-only preferred)

Allowed:
- a docs-only proposal-document template;
- a tiny YAML / JSON schema validator for the candidate-family
  proposal shape, with tests;
- helper docs.

Disallowed:
- strategy approval;
- trading code wired into the engine;
- paper / demo / live changes;
- CAMPAIGN_002 tuning;
- parameter search;
- broker calls;
- new external dependencies.

If nothing safe and useful is identified, Phase B5 commits a short
explanatory note and skips code.

### Phase B6 — final validation & summary

| deliverable | type |
|---|---|
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md) | docs |
| Updates to [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) (and `EVIDENCE_MANIFEST.json` if appropriate) | docs |

Re-runs all the standing safety / freeze / archive / secret
checks, the paper-loop and demo-loop refusal checks, the full
pytest suite, and ruff over the touched trees. Reports the final
test count and the safety-state diff (which must be: zero
changes from Phase 0).

## 5. Safety rails (binding for every phase of this sprint)

| rail | enforcement |
|---|---|
| `configs/approved_strategies.yaml` stays `approved: []` | Phase B6 re-reads it; freeze checker re-asserts. |
| CAMPAIGN_002 verdict unchanged | no edit to `backtests/CAMPAIGN_002_*` or `docs/research/CAMPAIGN_002_*`. |
| paper-loop / demo-loop refuse | Phase B6 re-runs the refusal commands. |
| no `live-loop` exists | CLI `--help` re-inspected in Phase B6. |
| no broker / OANDA call | no script in this sprint imports `forex_bot.broker.oanda` for execution; nothing in this sprint hits the network. |
| no credential read | no `.env` opened; no `os.environ.get('OANDA_*')`. |
| no QuantConnect / LEAN | retirement decision stands; no LEAN command issued. |
| no engine-PnL edit | `src/forex_bot/backtesting/` untouched. |
| no `src/forex_bot/financing.py` edit | grep verifies. |
| no new external dependency | `pyproject.toml` untouched. |
| no strategy code in `src/forex_bot/strategies/` | grep verifies. |
| ruff clean over `src tests scripts research` | Phase B6. |
| pytest `702 passes` (or +N for any new Phase B5 helper tests) | Phase B6. |
| no `*.sqlite3`, candle CSV, raw OANDA dump, or bulky output committed | Phase B6 `git status --short`. |

## 6. Commit cadence

One commit per phase, each titled with the canonical
`Phase X (research-new-candidate-strategy-discovery-001): <slug>`
prefix matching the prior sprints' style. Phase 0 is already
committed (audit doc); the next commits are Phase B1 (this plan
+ protocol), Phase B2 (inventory), Phase B3 (shortlist), Phase
B4 (eval design), Phase B5 (optional helper or note), Phase B6
(summary + final validation + manifest updates).

## 7. Success criteria for this sprint

The sprint is "done" when **all** of these are true:

1. The four design docs (protocol, inventory, shortlist,
   evaluation design) are committed and self-consistent.
2. The preferred candidate is clearly identified, distinct from
   CAMPAIGN_002 and the other three already-tested families on
   theoretical grounds, and matched to the existing
   walk-forward + financing infrastructure.
3. The future implementation branch name for the preferred
   candidate is documented.
4. Every standing safety check (archive, freeze, secret, refusal,
   `--help`) re-runs PASS in Phase B6.
5. The full pytest suite is **702 passes** (or higher only via
   new Phase B5 helper tests; never lower).
6. `git status --short` after Phase B6 is clean.
7. The summary doc carries `strategy_evidence: false` and
   re-states the safety state verbatim.

## 8. Out-of-scope (recorded so the next sprint does not need to
re-decide)

- Implementing the preferred candidate's strategy module.
- Generating the candidate's walk-forward plan and committing
  `plan.json` / `plan.md`.
- Running a backtest for the candidate.
- Building a candidate-specific pre-commit doc.
- Approving the candidate for paper / demo / live.

Each of these belongs to a *separate* future sprint, named in
the Phase B4 eval design doc.

## 9. Cross-links

- Phase 0 audit:
  [`NEXT_BRANCH_DECISION_AUDIT.md`](NEXT_BRANCH_DECISION_AUDIT.md)
- Next-direction memo:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- Walk-forward protocol:
  [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- Walk-forward status:
  [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- Financing model status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Financing protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Bp/day fixture status:
  [`FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md)
- Research freeze:
  [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- Strategy status registry:
  [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- Future research backlog:
  [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md)
- Strategy approval process:
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)

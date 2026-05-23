# Random-Entry Diagnostic Anchor — Sprint 001 Plan

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-001`
`strategy_evidence: false`

Phase 0 truth audit + sprint plan for the scaffold sprint that
will implement **CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011`**
— the **C5 diagnostic-anchor null model** selected in
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md).
**This document does not implement the strategy, does not approve
it, and does not run any evidence campaign.**

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.
> **CAMPAIGN_011 is a null model by design and cannot be approved.**

## 1. Repo state (Phase 0 audit)

| dimension | value |
|---|---|
| current branch | `claude/affectionate-fermi-d950fc` (worktree for `research-random-entry-diagnostic-anchor-001`) |
| base commit | `d926341` — Phase 7 of `research-new-candidate-strategy-discovery-002` (CAMPAIGN_011 selected as next candidate, design committed) |
| worktree path | `/Users/kashane/dev/forex-bot/.claude/worktrees/affectionate-fermi-d950fc/` |
| `git status` at Phase 0 start | clean |
| `configs/approved_strategies.yaml` | **`approved: []`** (verified) |
| CAMPAIGN_002 status | **REJECT** (unchanged; untouched) |
| CAMPAIGN_010 status | **REJECT** (unchanged; untouched) |
| paper-loop / demo-loop | refuse — verified |
| live-loop | does not exist — verified |
| QuantConnect / LEAN | retired; not used |

### 1.1 Baseline validation results

| check | result |
|---|---|
| `python -m pytest -q` | **735 passed** in 2.92s |
| `ruff check src tests scripts research` | **11 pre-existing UP042 findings** in untouched files (`research/parity_verifier/models.py`, `research/walk_forward/models.py`, `research/financing/models.py`, `research/lean_parity/algorithms/...`). Matches the documented baseline from prior sprints. |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED (10 campaigns, 14 diagnostic artifacts, **164 evidence-index links**, 2,147 artifact files clean) |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED (registry empty, loops refuse, archive valid) |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refused (registry empty) |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refused (registry empty) |
| `python -m forex_bot.cli --help` | no `live-loop` command present |

### 1.2 Files inspected (read-only)

Discovery / design (the binding documents):

- [`docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md)
- [`docs/research/NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)
- [`docs/research/NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
- [`docs/research/NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md)
  (the prompt spec this sprint follows)
- [`docs/research/NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
- [`docs/research/CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
- [`docs/research/REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`docs/research/CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`docs/research/STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`docs/research/WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`docs/research/FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)

Implementation patterns (the structural template):

- [`src/forex_bot/strategies/session_breakout.py`](../../src/forex_bot/strategies/session_breakout.py)
  (model strategy module — mirror structure, swap rules)
- [`src/forex_bot/strategies/__init__.py`](../../src/forex_bot/strategies/__init__.py)
  (re-export pattern)
- [`src/forex_bot/config.py`](../../src/forex_bot/config.py)
  (`SessionBreakoutStrategyConfig` + `StrategyConfig.session_breakout` + `_check_enabled` slot pattern)
- [`tests/unit/test_session_breakout.py`](../../tests/unit/test_session_breakout.py)
  (33-case test pattern — mirror; this scaffold targets ≥ 20 cases)
- [`configs/campaign_010_session_breakout.yaml`](../../configs/campaign_010_session_breakout.yaml)
  (research config template)
- [`scripts/run_campaign_010.py`](../../scripts/run_campaign_010.py)
  (campaign runner template — *not* used in this scaffold sprint;
  documented for the future evidence sprint)

## 2. Repo-truth summary

The prior discovery sprint
(`research-new-candidate-strategy-discovery-002`,
commits `863d5ea` → `d926341`) produced 9 markdown docs (≈ 2,830
lines) selecting C5 as the next candidate and binding its design.
No Python code, no test changes, no config changes. The 735-test
baseline is preserved.

The candidate identity (from
[`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)):

| field | value |
|---|---|
| candidate id | C5 |
| candidate role | **diagnostic anchor / null model** (NOT a paper candidate) |
| strategy id | `random_entry_anchor` |
| strategy version | `0.1.0-c011` |
| campaign label | `CAMPAIGN_011` |
| this scaffold branch | `research-random-entry-diagnostic-anchor-001` |
| future evidence branch | `research-random-entry-diagnostic-anchor-walk-forward-001` |
| timeframe / universe | H4 / 7 pairs (matches CAMPAIGN_010) |
| approval path | **none — null model by design** |

## 3. Current safety state (unchanged)

| dimension | status |
|---|---|
| approved registry | `approved: []` |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| `random_entry_anchor` in any code path | none yet (scaffold sprint will add) |
| paper-loop / demo-loop refuse | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| broker / OANDA call (this sprint, baseline phase) | none |
| `.env` read | none |
| credentials printed | none |
| engine-PnL change | none (will not change in this scaffold sprint either) |
| `src/forex_bot/financing.py` change | none |
| `MODELED` financing reachable | no (four refusal layers) |
| pytest baseline | **735 passes** |

## 4. Null-model purpose

CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` is a
**diagnostic anchor**, not a paper-trade candidate. Its purpose
is to:

1. **Validate the full evidence pipeline as designed.** The
   strategy goes through every stage of the walk-forward +
   financing + risk + verifier pipeline that any "real"
   candidate would, using the **same engine, same gates, same
   universe, same data, and same financing source** as
   CAMPAIGN_010.
2. **Establish a per-fold + aggregate falsifiability bar**
   that every subsequent C2 / C3 / C4 / new-family candidate
   must beat by a meaningful margin to count as evidence of an
   edge.
3. **Demonstrate the gates correctly REJECT a known-zero-edge
   strategy** — if random-entry under bid/ask costs + ATR stop
   does not REJECT, that is a bug report against the pipeline,
   not an edge.
4. **Provide a deterministic, reproducible reference** —
   because random is parameter-free (only the master seed is
   "tunable", and it is fixed before any backtest), the
   reference is exactly reproducible across runs and across
   independent verifier implementations.

The strategy **cannot become a paper / demo / live candidate**
under any circumstance. The scaffold sprint is explicitly
forbidden from adding it to `configs/approved_strategies.yaml`.

## 5. Sprint phases (8 commits)

| phase | scope | deliverable(s) |
|---|---|---|
| 0 (this doc) | Repo truth + scaffold plan | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md) |
| 1 | Implementation spec (R1–R8 rule table, frozen parameters, no-lookahead, distribution / determinism, null-model restrictions) | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md) |
| 2 | Strategy module + config sub-model + slot + re-export | code changes to `src/forex_bot/strategies/random_entry_anchor.py`, `src/forex_bot/strategies/__init__.py`, `src/forex_bot/config.py` |
| 3 | Unit tests (≥ 20 cases per the spec) | `tests/unit/test_random_entry_anchor.py` |
| 4 | Research config + CAMPAIGN_011 pre-commit + status + scaffold-readiness | `configs/campaign_011_random_entry_anchor.yaml`, [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md), [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md), [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md) |
| 5 | Non-evidence smoke (config-load, unit tests, optional walk-forward dry-run plan to `/tmp` only) | [`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md) |
| 6 | Future evidence-readiness docs (walk-forward, financing/risk, verifier) | [`CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md), [`CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md), [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md) |
| 7 | Sprint summary + EVIDENCE_INDEX update + final validation | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md), [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) update, optionally [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) annotation |

Commits at the end of each phase.

## 6. Implementation files expected (Phase 2)

| file | role |
|---|---|
| `src/forex_bot/strategies/random_entry_anchor.py` | NEW — implements the `Strategy` protocol with R1–R8 from the Phase 1 spec; deterministic-seed coin-flip entry; no broker imports |
| `src/forex_bot/strategies/__init__.py` | EDIT — add `RandomEntryAnchorStrategy` import + `__all__` entry |
| `src/forex_bot/config.py` | EDIT — add `RandomEntryAnchorStrategyConfig` sub-model + `StrategyConfig.random_entry_anchor` slot + enabled-list check |

**No edits** to `src/forex_bot/backtesting/`, `src/forex_bot/risk/`,
`src/forex_bot/broker/`, `src/forex_bot/financing.py`,
`src/forex_bot/loops.py`, or `src/forex_bot/cli.py`.

## 7. Tests expected (Phase 3)

`tests/unit/test_random_entry_anchor.py` — **≥ 20 cases**
(targeting ~25 for safety) covering:

- Config defaults and validation (≥ 5 cases)
- Determinism: same seed → same decisions; different seed →
  different decisions; pair / timestamp dependence (≥ 4 cases)
- Distribution / frequency: long-short balance; entry-probability
  rate (≥ 2 cases)
- No-lookahead structural audit: seed input does not contain
  close[t]; strategy uses prior-bar ATR; AST or grep-level check
  (≥ 3 cases)
- Strategy core: R1 warm-up; R2 block re-entry; R5 fail-closed on
  NaN ATR; R7 stop placement long/short (≥ 4 cases)
- No-import audit: no `random.random`, no `numpy.random`, no
  Python built-in `hash()`, no `forex_bot.broker` import (≥ 2 cases)
- No-rejected-family audit: no `CAMPAIGN_002` / `trend_following`
  / `Donchian` / `EMA` references; no `CAMPAIGN_010` /
  `session_breakout` / `Asian` / `London` references (≥ 2 cases)
- Approval / safety regression: `approved_strategies.yaml` still
  empty; `random_entry_anchor` NOT in `configs/paper.yaml` or
  `configs/practice.yaml` enabled lists (≥ 2 cases)
- Null-model invariant: strategy exposes no approval-shaped field
  / method (≥ 1 case)

## 8. Docs expected (Phases 1, 4, 5, 6, 7)

| doc | phase | purpose |
|---|---|---|
| `RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md` | 0 (this doc) | sprint plan + audit |
| `RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md` | 1 | binding R1–R8 spec |
| `CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` | 4 | pre-commit checklist with frozen parameters + gates |
| `CAMPAIGN_011_STATUS.md` | 4 | candidate-scaffold-only status |
| `RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md` | 4 | scaffold readiness summary |
| `CAMPAIGN_011_SMOKE_RESULT.md` | 5 | non-evidence smoke result |
| `CAMPAIGN_011_WALK_FORWARD_READINESS.md` | 6 | future evidence walk-forward readiness |
| `CAMPAIGN_011_FINANCING_RISK_READINESS.md` | 6 | future evidence financing + risk readiness |
| `CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md` | 6 | future verifier readiness |
| `RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md` | 7 | sprint summary |

## 9. Validation commands

After every phase commit:

- `python -m pytest -q` (target: ≥ 735 → ≥ 755 after Phase 3)
- `ruff check src tests scripts research` — must not introduce
  any new finding beyond the 11 pre-existing UP042
- `python scripts/validate_research_archive.py`
- `python scripts/check_research_freeze.py`
- `python scripts/scan_artifacts_for_secrets.py`

At Phase 0 and Phase 7:
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml`
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml`
- `python -m forex_bot.cli --help`
- `git status --short`

## 10. Non-goals (binding)

- **No historical backtest run.** The evidence sprint
  (`research-random-entry-diagnostic-anchor-walk-forward-001`)
  is the only path to a verdict; the scaffold sprint produces
  no `WalkForwardResults` and no per-fold metrics.
- **No walk-forward evidence campaign.** Same — evidence sprint.
- **No financing overlay computation.** Same — evidence sprint.
- **No risk-diagnostic generation.** Same — evidence sprint.
- **No data fetch.** No OANDA call. No `.env` read.
- **No approval action.** `configs/approved_strategies.yaml`
  remains `approved: []`.
- **No paper/demo/live enablement.**
- **No engine / financing / risk-policy code edits.**
- **No edits to any CAMPAIGN_002 / CAMPAIGN_010 artifact** (or
  any earlier campaign verdict).
- **No seed optimization.** `master_seed = 20260523` is fixed
  in the Phase 1 spec and Phase 4 pre-commit *before* any unit
  test runs.
- **No parameter tuning.** `entry_probability_per_bar = 0.05`
  and every other frozen parameter is fixed before any code.
- **No new external dependency.**

## 11. Explicit no-approval statement

**CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` cannot be
approved by design.** It is a null model. The protocol's §4
whitelist lists it as a "Baseline / null model" category
"allowed only as a diagnostic comparison anchor for the
preferred candidate; cannot itself be the 'preferred
candidate' for paper promotion."

The scaffold sprint does not approve. The future evidence
sprint cannot approve. Even an unexpected PASS in the future
evidence sprint **does not approve** — it triggers the
unexpected-PASS investigation playbook (treat as a bug report
against the pipeline; investigate for information leakage; do
not promote).

## 12. Explicit "this sprint must not run an evidence campaign" statement

This scaffold sprint **must not**:

- Invoke `scripts/run_campaign_010.py` against the CAMPAIGN_011
  config.
- Invoke any new `scripts/run_campaign_011.py`-style runner
  (this scaffold sprint does not write such a runner; that is
  the evidence sprint's job).
- Produce any `walk_forward/results.json` or
  `walk_forward/results.md` artifact under
  `backtests/CAMPAIGN_011_random_entry_anchor/`.
- Produce any `financing/financing_run.{json,md}` artifact.
- Produce any `risk/diagnostics.{json,md}` artifact.
- Produce any per-fold per-pair trade CSV.
- Record any verdict for CAMPAIGN_011 (no REJECT, no PASS, no
  INCONCLUSIVE).

The scaffold sprint produces only: strategy module + config +
unit tests + research config + pre-commit + readiness docs +
non-evidence smoke + sprint summary. The verdict comes from the
future evidence sprint, which is specified in
[`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md).

## 13. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md)
- [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md)
  (the prompt spec this sprint follows)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md)
  (the model scaffold sprint to mirror)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)

# New Candidate Strategy Discovery — Sprint 002 Plan

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-002`
`strategy_evidence: false`

Phase 0 truth audit + sprint plan for the second
candidate-discovery sprint, opened after CAMPAIGN_010
(`session_breakout 0.1.0-c010`) was **REJECTED** by the evidence
sprint. **This document does not approve any strategy.** It
records the repo state and the design-only pipeline this sprint
will run.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked. This is a
> **design / selection** sprint — no new strategy code, no new
> backtest, no broker call, no parameter tuning.

## 1. Repo state (Phase 0 audit)

| dimension | value |
|---|---|
| current branch | `claude/affectionate-fermi-d950fc` (the worktree for `research-new-candidate-strategy-discovery-002`) |
| base commit | `21482cb` — Phase 8 of `research-asian-london-session-breakout-walk-forward-001` (CAMPAIGN_010 REJECT, status registries updated) |
| worktree path | `/Users/kashane/dev/forex-bot/.claude/worktrees/affectionate-fermi-d950fc/` |
| `git status` at Phase 0 start | clean |
| `configs/approved_strategies.yaml` | **`approved: []`** (verified) |
| CAMPAIGN_002 status | **REJECT** (unchanged; untouched) |
| CAMPAIGN_010 status | **REJECT** (set by the prior evidence sprint; see [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)) |
| `session_breakout 0.1.0-c010` in registry | **no** (rejected) |
| paper-loop / demo-loop | refuse — verified |
| live-loop | does not exist — verified |
| QuantConnect / LEAN | retired; not used |

### 1.1 Baseline validation results

| check | result |
|---|---|
| `python -m pytest -q` | **735 passed** in 2.92s (unchanged from prior sprint) |
| `ruff check src tests scripts research` | **11 pre-existing UP042 findings** in untouched files (matches the documented baseline; recommended cleanup sprint: `infra-ruff-up042-stress-enum-001`) |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED (10 campaigns including CAMPAIGN_010, 14 diagnostic artifacts, 154 evidence-index links, 2,137 artifact files clean) |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED (registry empty, loops refuse, archive valid) |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED (no credential value or shape) |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refused (registry empty) |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refused (registry empty) |
| `python -m forex_bot.cli --help` | no `live-loop` command present |

### 1.2 Files inspected (read-only)

- [`docs/research/ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md)
- [`docs/research/CAMPAIGN_010_EVIDENCE_SUMMARY.md`](CAMPAIGN_010_EVIDENCE_SUMMARY.md)
- [`docs/research/CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`docs/research/CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`docs/research/CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
- [`docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- [`docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md)
- [`docs/research/STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
- [`docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`docs/research/WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`docs/research/FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`docs/research/STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md) (the existing random-entry benchmark)
- [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
- [`configs/campaign_010_session_breakout.yaml`](../../configs/campaign_010_session_breakout.yaml)
- [`src/forex_bot/strategies/session_breakout.py`](../../src/forex_bot/strategies/session_breakout.py)
- [`research/walk_forward/`](../../research/walk_forward/)
- [`research/financing/`](../../research/financing/)

## 2. Repo-truth summary

### 2.1 Latest rejected campaigns

| campaign | strategy / version | verdict | evidence pointer |
|---|---|---|---|
| CAMPAIGN_001 | `trend_following 0.1.0` (synthetic) | SYNTHETIC_NOT_EVIDENCE | superseded by CAMPAIGN_002 |
| CAMPAIGN_002 | `trend_following 0.1.0` (real OANDA H4) | REJECT | [`CAMPAIGN_002_FINANCING_RETROSPECTIVE.md`](CAMPAIGN_002_FINANCING_RETROSPECTIVE.md) |
| CAMPAIGN_003 | `trend_following + ADX-14 > 25` | REJECT | [`CAMPAIGN_003_POSTMORTEM.md`](CAMPAIGN_003_POSTMORTEM.md) |
| CAMPAIGN_004 | `volatility_breakout 0.1.0-c004` | REJECT | [`CAMPAIGN_004_PRECOMMIT.md`](CAMPAIGN_004_PRECOMMIT.md) (+ campaign artifacts) |
| CAMPAIGN_005 | benchmarks / random / always-long | DIAGNOSTIC | [`CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md) — random expectancy mean **−0.095 R** across 6 majors |
| CAMPAIGN_006 | D1 daily trend | BLOCKED (infrastructure) | [`CAMPAIGN_006_DAILY_TREND_PRECOMMIT.md`](CAMPAIGN_006_DAILY_TREND_PRECOMMIT.md) |
| CAMPAIGN_007 | `pullback_continuation` | REJECT | [`CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md`](CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md) |
| CAMPAIGN_008 | `mean_reversion 0.1.0-c008` | REJECT (research-only) | [`CAMPAIGN_008_HUMAN_REVIEW.md`](CAMPAIGN_008_HUMAN_REVIEW.md) |
| CAMPAIGN_009 | `mean_reversion 0.2.0-c009` | REJECT | [`CAMPAIGN_009_PRECOMMIT.md`](CAMPAIGN_009_PRECOMMIT.md) |
| **CAMPAIGN_010** | **`session_breakout 0.1.0-c010`** | **REJECT** (this is the prior sprint's verdict) | [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) |

### 2.2 Current approved-strategy status

Empty. Every candidate ever evaluated has been either REJECTED,
SYNTHETIC_NOT_EVIDENCE, DIAGNOSTIC, or BLOCKED.
`configs/approved_strategies.yaml` reads `approved: []` and no
strategy is in any active loop.

### 2.3 Safety state (unchanged across both prior sprints + this Phase 0)

| dimension | status |
|---|---|
| approved registry | `approved: []` |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched this sprint) |
| `session_breakout` in any active loop | no |
| paper-loop / demo-loop refuse | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| broker / OANDA call (this sprint, baseline phase) | none |
| `.env` read | none |
| credentials printed | none |
| engine-PnL change | none |
| `src/forex_bot/financing.py` change | none |
| `MODELED` financing reachable | no (four refusal layers) |
| pytest baseline | **735 passes** |

## 3. Sprint scope (design + selection only)

| dimension | scope |
|---|---|
| sprint type | candidate **selection** + **design**, not implementation |
| Python code added | **none** (Phase 6 may add a tiny docs/schema helper only if clearly useful) |
| backtests run | **none** |
| broker calls | **none** |
| data fetched | **none** |
| approval actions | **none** (and structurally cannot — the next candidate, even if selected, is not added to `configs/approved_strategies.yaml` by this sprint) |
| target deliverables | seven new docs (the eight phase-output files below; Phase 7 also updates `EVIDENCE_INDEX.md`) |

## 4. Candidate-selection goals

1. **Avoid CAMPAIGN_010 re-attempt.** No re-look at session_breakout
   with any rule / parameter variation. CAMPAIGN_010 is REJECTED;
   re-tuning is a curve-fitting anti-pattern per
   [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
   §12.
2. **Score the remaining shortlist (C2–C5) under the protocol's
   distinctness rubric extended to include CAMPAIGN_010 as a 5th
   rejected family.** Note any candidate that no longer clears
   the ≥ 3-of-6 distinctness threshold against the now-larger
   rejected set.
3. **Surface every blocker honestly** — engine constraints
   (single-instrument single-position), MODELED-financing
   refusal, D1-aggregation status, missing verifier coverage,
   etc.
4. **Pick exactly one next preferred candidate** for a future
   scaffold sprint, with a candidate id, strategy id, version,
   and proposed `CAMPAIGN_011` label.
5. **Document a falsifiable rejection criterion in the
   implementation design** so the future scaffold + evidence
   sprints inherit a non-negotiable gate vector.
6. **Be willing to pick a diagnostic / null candidate** if
   that is the highest-value next step. The protocol explicitly
   authorizes this option (the C5 anchor) — selecting it is not
   a punt; it is sometimes the right call after consecutive
   directional REJECTs.

## 5. Non-goals (binding)

- **No strategy code** (even a no-signal scaffold).
- **No approval.** No edit to `configs/approved_strategies.yaml`
  except to verify it remains `approved: []`.
- **No backtest, paper, demo, live** action.
- **No broker / OANDA call.**
- **No data fetch.** No `.env` read; no credential printed.
- **No QuantConnect / LEAN.**
- **No engine PnL change.** No `src/forex_bot/financing.py`
  edit.
- **No CAMPAIGN_002 or CAMPAIGN_010 revival / tuning.**
- **No new external dependency.**
- **No use of CAMPAIGN_010's metric outputs to motivate parameter
  selection for any new candidate.** (Even the legitimate use of
  CAMPAIGN_010 as "rejected historical evidence" stops at
  "this family does not work"; it cannot become "try this knob.")

## 6. Sprint phases

| phase | scope | deliverable(s) |
|---|---|---|
| 0 (this doc) | Repo truth + sprint plan | [`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md) |
| 1 | Rejected-family closeout + anti-overfit guardrails | [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md) + [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) |
| 2 | Reassess remaining candidate families (C2–C5) against the now-5-rejected baseline | [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md) |
| 3 | Select exactly one next preferred candidate with id / version / campaign label | [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md) |
| 4 | Implementation + evaluation design for the selected candidate | [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md) |
| 5 | Future-branch prompt specs (scaffold + evidence) | [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md) + [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md) |
| 6 | Optional docs/schema helper decision | [`NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md) |
| 7 | Sprint summary + EVIDENCE_INDEX update + final validation | [`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md), [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) update (optionally [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)) |

Commits at the end of each phase.

## 7. Expected outputs

All outputs are markdown docs in `docs/research/`. No artifact
folders, no JSON manifests beyond optional `EVIDENCE_INDEX.md` /
`EVIDENCE_MANIFEST.json` edits in Phase 7, no Python files
(Phase 6 may add a tiny schema helper if clearly worthwhile;
the default decision is "none").

## 8. Validation plan

Run after every phase commit:

- `python -m pytest -q` (≥ 735 — unchanged unless Phase 6 adds tests)
- `ruff check src tests scripts research` — must not introduce
  any new finding beyond the 11 pre-existing UP042
- `python scripts/validate_research_archive.py`
- `python scripts/check_research_freeze.py`
- `python scripts/scan_artifacts_for_secrets.py`

Run at Phase 0 and Phase 7:
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml` (refuses)
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml` (refuses)
- `python -m forex_bot.cli --help` (no `live-loop`)
- `git status --short` (clean at every commit boundary)

## 9. Explicit no-approval statements

1. **This sprint cannot approve any strategy.** It is design-only.
2. **Selecting a "next preferred candidate" is not an approval.**
   The selection only fixes which family the future scaffold
   sprint targets; the candidate must then accumulate the full
   six-evidence ladder before any approval can be considered.
3. **The future scaffold sprint cannot approve either.** It can
   implement the candidate, add unit tests, and pass a
   non-evidence smoke; it cannot run paper / demo / live.
4. **The future evidence sprint cannot approve either.** Even a
   clean PASS produces *research evidence*; approval requires a
   separate, reviewed human action per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 10. Explicit "CAMPAIGN_010 must not be tuned or revived" statement

- The candidate id `session_breakout 0.1.0-c010` is **REJECTED**
  and will not be revisited under any name / version variant in
  this sprint or in any future scaffold sprint authorised by
  this sprint.
- The CAMPAIGN_010 walk-forward metrics, fold structure,
  per-pair sensitivities, financing impact, and risk-engine
  rejection profile **may not be used as tuning feedback** for
  any other candidate's parameter choice. Their only legitimate
  use is as "evidence that this family does not work on this
  universe under frozen-parameter walk-forward".
- Any future "session-breakout-like" proposal must be a
  meaningfully distinct family (≥ 3 of 6 distinctness dimensions
  per the protocol) — not a parameter tweak with a different
  name. The Phase 1 anti-overfit guardrails will codify this.

## 11. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
- [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
- [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md)

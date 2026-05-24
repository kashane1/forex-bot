# Discovery-005 Helper Decision

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-005`
`strategy_evidence: false`

Phase 9 decision: **NO helper code added this sprint.** This doc
records the options considered and the rationale.

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 all
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`.

## 1. Decision

**No helper code, no schema check, no validator extension, no test
helper is added in this sprint.** The discovery-005 sprint output is
**11 markdown docs** (Phase 0 plan + Phase 1 closeout + Phase 2
anti-pattern + Phase 3 guardrails addendum + Phase 4 reassessment +
Phase 5 shortlist + Phase 6 selection + Phase 7 implementation
design + Phase 8a scaffold spec + Phase 8b evidence spec + Phase 10
summary), zero code.

## 2. Options considered

The discovery-005 sprint prompt explicitly allowed:

- docs-only checklist
- candidate-vs-null comparison checklist
- rejected-family similarity checklist
- turnover-amplification checklist
- infrastructure-readiness checklist
- schema/checker extension only if a relevant checker already exists
  and the change is small

### Option A — A "candidate-vs-null comparison" checklist

| pros | cons |
|---|---|
| would be reusable across future evidence sprints | already codified in [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §3 + §8 + §9; CAMPAIGN_012's and CAMPAIGN_013's `WALK_FORWARD_RESULT.md` §3 demonstrate the comparison concretely; [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) §17 binds CAMPAIGN_014's version. A separate checklist would duplicate; the single source of truth is `CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`. |

**Decision: reject.** Already covered.

### Option B — A "rejected-family similarity" checklist

| pros | cons |
|---|---|
| would help future candidate proposers self-audit against the do-not-revive list | already codified in [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) (Patterns A–G) + [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) (Patterns H–L) + this sprint's [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (Patterns R–W; plus M–Q from the Phase 2 anti-pattern doc). Each addendum has explicit pass/fail examples. A separate checklist would split the source of truth across multiple docs. |

**Decision: reject.** Already covered.

### Option C — A "turnover-amplification" checklist

| pros | cons |
|---|---|
| would help future candidate proposers self-audit against Patterns M–Q | already codified in [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) §4 (turnover-budget requirement, 4 sub-items) + §5 (Patterns M–Q with pass/fail examples). The Phase 7 [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) §8 + §9 + §11 + §18 demonstrate the application for C7. A separate checklist would duplicate. |

**Decision: reject.** Already covered.

### Option D — An "infrastructure-readiness" checklist

| pros | cons |
|---|---|
| could speed up future Phase 4 reassessments | each Phase 4 reassessment naturally scores against all infrastructure paths (this sprint's [`NEXT_DIRECTION_REASSESSMENT_005.md`](NEXT_DIRECTION_REASSESSMENT_005.md) §3 is the template — 18 axes including the 3 new ones for discovery-005). A separate checklist file would diverge from the actual scoring shape over time. |

**Decision: reject.** Each Phase 4 reassessment doc *is* the
checklist for that sprint's context.

### Option E — Extend `scripts/validate_research_archive.py` to validate the new "turnover budget" doc convention

| pros | cons |
|---|---|
| would catch drift if a future verdict doc forgot the turnover-budget section | the convention is binding via the Phase 2 anti-pattern doc + each candidate's `*_PRECOMMIT_CHECKLIST.md` (per the Phase 7 design §18). CAMPAIGN_014's evidence-sprint Phase 5 verdict doc will include the turnover-budget evaluation per the binding spec. Adding a validator schema-check would risk false positives across the 13 historical campaigns that pre-date the convention (CAMPAIGN_002 / 003 / 004 / 007 / 008 / 009 / 010 / 011 / 012 / 013). The convention is enforced by binding spec at evidence-sprint time, not by validator at every commit. |

**Decision: reject.** Same conclusion as the equivalent options in
discovery-002, discovery-003, discovery-004. The recommended sprint
name `infra-research-archive-validator-turnover-budget-section-check-001`
remains out of scope for discovery sprints.

### Option F — Extend `scripts/validate_research_archive.py` to validate the new "cost section" doc convention (Pattern Q)

| pros | cons |
|---|---|
| same as Option E | same as Option E — the convention is binding via the Phase 2 anti-pattern doc + the Phase 7 design's binding cost section requirement; validator would risk false positives across pre-Pattern-Q campaigns. |

**Decision: reject.** Out of scope for discovery sprints.

### Option G — A "CAMPAIGN_014 frozen-parameter pre-commit assertion" helper

| pros | cons |
|---|---|
| could let the strategy module assert its own frozen parameters | the runner already asserts frozen parameters before any backtest fires (the CAMPAIGN_010 / 011 / 012 / 013 runners' `_assert_frozen()` pattern); the future Phase 3 runner of the evidence sprint will implement the same. A separate helper would duplicate. |

**Decision: reject.** Runner-level assertion is the right layer.

### Option H — A "discovery-output-template" docs helper

| pros | cons |
|---|---|
| would speed up the next discovery sprint | the 5 discovery sprints (001 / 002 / 003 / 004 / this 005) have produced increasingly-consistent file structures; the file structure itself is the template. Adding a separate template doc adds maintenance surface that drifts from the actual deliverables. |

**Decision: reject.** Same conclusion as discovery-001, discovery-002,
discovery-003, discovery-004.

### Option I — Pre-allocate the CAMPAIGN_014 manifest entry as a placeholder

| pros | cons |
|---|---|
| pre-allocates the slot | the validator's `check_manifest_schema` requires `report_path` and `artifact_folder` to exist; CAMPAIGN_014 has neither yet (no scaffold sprint has run). Adding a placeholder would break the validator. |

**Decision: reject.** CAMPAIGN_014 entry must wait for the future
evidence sprint. This is the same convention CAMPAIGN_010 / 011 /
012 / 013 scaffolds followed exactly.

### Option J — A new `scripts/compile_event_calendar.py` skeleton in this sprint

| pros | cons |
|---|---|
| would pre-stage the Phase 1b deliverable of the scaffold sprint | discovery sprint charter is **design / discovery only**. The Phase 1b event-fixture compilation is explicitly a *scaffold-sprint* deliverable per the Phase 8a branch spec §2. Pre-staging it here would (a) blur the discovery / scaffold boundary, (b) commit a working compilation script that is part of the *scaffold sprint's commit history* per project convention, (c) potentially break the test suite if the script imports anything the scaffold sprint hasn't built yet. |

**Decision: reject.** Belongs in the scaffold sprint Phase 1b.

## 3. Why no-code is right for this sprint

| reason | detail |
|---|---|
| **Charter** | the discovery-005 prompt opens with "This is a design/discovery sprint only. Do not implement a new strategy in this sprint. Do not run a backtest, walk-forward evidence campaign, financing overlay, risk diagnostics, or verifier run in this sprint." None of options A–J clears a "tiny docs/schema helper that clearly improves safety" bar. |
| **Single source of truth** | every piece of would-be helper content already has a home: null-baseline comparison (`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`); rejected-family similarity (base guardrails + 004 addendum + this sprint's 005 addendum); turnover-amplification (Phase 2 anti-pattern doc); infrastructure readiness (each Phase 4 reassessment doc); frozen-parameter assertion (runner-level pattern); validator schema-check (deferred to a separate infra sprint); manifest pre-allocation (forbidden by validator); compilation script (scaffold sprint Phase 1b). |
| **Precedent** | discovery-001, discovery-002, discovery-003, discovery-004 all made identical no-helper decisions for identical reasons; the discipline has held across 4 scaffold sprints + 3 evidence sprints + this 5th discovery sprint. |
| **Test-suite preservation** | 875-pytest baseline is preserved with zero risk by adding no code. |
| **Ruff posture preservation** | 3 pre-existing findings in `research/lean_parity/algorithms/` unchanged; adding code might introduce new findings. |
| **No scope creep** | the standing rule "don't add features, refactor, or introduce abstractions beyond what the task requires" applies. |

## 4. The 11-doc output is the discipline trail

The discovery-005 sprint's value is the **11 markdown deliverables**:

1. `NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md` (Phase 0)
2. `CAMPAIGN_013_REJECTION_CLOSEOUT.md` (Phase 1)
3. `TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md` (Phase 2)
4. `REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md` (Phase 3)
5. `NEXT_DIRECTION_REASSESSMENT_005.md` (Phase 4)
6. `CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md` (Phase 5)
7. `NEXT_PREFERRED_DIRECTION_005.md` (Phase 6)
8. `NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md` (Phase 7)
9. `NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md` (Phase 8a)
10. `NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md` (Phase 8b)
11. `NEW_CANDIDATE_DISCOVERY_005_HELPER_DECISION.md` (Phase 9 — this doc)

Plus the Phase 10 summary doc + small EVIDENCE_INDEX /
STRATEGY_STATUS edits.

A helper file would not add discipline; the 11-doc trail already
*is* the discipline (each doc cites the prior + is bound by the
guardrails + closes out a specific decision).

## 5. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 875 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |
| code added this sprint | **none** |
| tests added this sprint | **none** |
| validator / schema-checker change | **none** |

## 6. Cross-links

- [`NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md) (sibling — identical no-helper decision)
- [`NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md) (sibling — identical no-helper decision)
- [`NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md) (sibling — identical no-helper decision)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md) (discovery-001 sibling)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md) (Phase 0 of this sprint)
- [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

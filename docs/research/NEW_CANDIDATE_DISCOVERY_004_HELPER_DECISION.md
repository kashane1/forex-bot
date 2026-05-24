# Discovery-004 Helper Decision

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-004`
`strategy_evidence: false`

Phase 8 decision: **NO helper code added this sprint.** This doc
records the options considered and the rationale.

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 all remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.

## 1. Decision

**No helper code, no schema check, no validator extension, no test
helper is added in this sprint.** The discovery-004 sprint output is
**10 markdown docs** (Phase 0 plan + Phase 1 closeout + Phase 2
guardrails addendum + Phase 3 reassessment + Phase 4 shortlist +
Phase 5 selection + Phase 6 implementation design + Phase 7 scaffold-
branch spec + Phase 7 evidence-branch spec + Phase 9 summary), zero
code.

## 2. Options considered

The discovery-004 sprint prompt explicitly allowed:

- docs-only checklist
- candidate-vs-null comparison checklist
- rejected-family similarity checklist
- infrastructure-readiness checklist
- schema/checker extension only if a relevant checker already exists
  and the change is small

### Option A — A "candidate-vs-null comparison" checklist

| pros | cons |
|---|---|
| would be reusable across future evidence sprints | already codified in [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §3 + §8 + §9; CAMPAIGN_012's `WALK_FORWARD_RESULT.md` §3 demonstrates the comparison concretely; [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md) §12 binds CAMPAIGN_013's version. A separate checklist would duplicate; the single source of truth is `CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`. |

**Decision: reject.** Already covered.

### Option B — A "rejected-family similarity" checklist

| pros | cons |
|---|---|
| would help future candidate proposers self-audit against the do-not-revive list | already codified in [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) (Patterns A–G) + this sprint's [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) (Patterns H–L). The addendum has explicit pass/fail examples. A separate checklist would split the source of truth across three docs. |

**Decision: reject.** Already covered.

### Option C — An "infrastructure-readiness" checklist

| pros | cons |
|---|---|
| could speed up future Phase 3 reassessments | each Phase 3 reassessment naturally scores against all infrastructure paths (this sprint's [`NEXT_DIRECTION_REASSESSMENT_004.md`](NEXT_DIRECTION_REASSESSMENT_004.md) §3 is the template). A separate checklist file would diverge from the actual scoring shape over time. |

**Decision: reject.** Each Phase 3 reassessment doc *is* the checklist for that sprint's context.

### Option D — Extend `scripts/validate_research_archive.py` to validate the new "null-baseline comparison" doc convention

| pros | cons |
|---|---|
| would catch drift if a future verdict doc forgot the section | the convention is binding via the CAMPAIGN_011 interpretation doc + each candidate's `*_PRECOMMIT_CHECKLIST.md` §8; CAMPAIGN_012's `WALK_FORWARD_RESULT.md` already includes the section. Adding a validator schema-check risks false positives across the 11 historical campaigns that pre-date the convention. The convention is enforced by binding spec, not by validator. |

**Decision: reject.** Same conclusion as the equivalent options in discovery-002 and discovery-003 (recommended sprint name `infra-research-archive-validator-null-baseline-section-check-001`; out of scope for this discovery).

### Option E — A "CAMPAIGN_013 frozen-parameter pre-commit assertion" helper

| pros | cons |
|---|---|
| could let the strategy module assert its own frozen parameters | the runner already asserts frozen parameters before any backtest fires (the CAMPAIGN_010 / 011 / 012 runners' `_assert_frozen()` pattern); the future Phase 3 runner of the evidence sprint will implement the same. A separate helper would duplicate. |

**Decision: reject.** Runner-level assertion is the right layer.

### Option F — A "discovery-output-template" docs helper

| pros | cons |
|---|---|
| would speed up the next discovery sprint | the 4 discovery sprints (001 / 002 / 003 / this 004) have produced increasingly-consistent file structures; the file structure itself is the template. Adding a separate template doc adds maintenance surface that drifts from the actual deliverables. |

**Decision: reject.** Same conclusion as discovery-001, discovery-002, discovery-003.

### Option G — Pre-allocate the CAMPAIGN_013 manifest entry as a placeholder

| pros | cons |
|---|---|
| pre-allocates the slot | the validator's `check_manifest_schema` requires `report_path` and `artifact_folder` to exist; CAMPAIGN_013 has neither yet (no scaffold sprint has run). Adding a placeholder would break the validator. |

**Decision: reject.** CAMPAIGN_013 entry must wait for the future evidence sprint. This is the same convention CAMPAIGN_010 / 011 / 012 scaffolds followed exactly.

## 3. Why no-code is right for this sprint

| reason | detail |
|---|---|
| **Charter** | the discovery-004 prompt opens with "This is design/discovery sprint only. Do not implement a new strategy in this sprint. Do not run a backtest or evidence campaign in this sprint." None of options A–G clears a "tiny docs/schema helper that clearly improves safety" bar. |
| **Single source of truth** | every piece of would-be helper content already has a home: null-baseline comparison (CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md); rejected-family similarity (base guardrails + this sprint's addendum); infrastructure readiness (each Phase 3 reassessment doc); frozen-parameter assertion (runner-level pattern); validator schema-check (deferred to a separate infra sprint); manifest pre-allocation (forbidden by validator). |
| **Precedent** | discovery-001, discovery-002, discovery-003 all made identical no-helper decisions for identical reasons; the discipline has held across 3 scaffold sprints + 2 evidence sprints. |
| **Test-suite preservation** | 818-pytest baseline is preserved with zero risk by adding no code. |
| **Ruff posture preservation** | 3 pre-existing findings in `research/lean_parity/algorithms/` unchanged; adding code might introduce new findings. |
| **No scope creep** | the standing rule "don't add features, refactor, or introduce abstractions beyond what the task requires" applies. |

## 4. The 10-doc output is the discipline trail

The discovery-004 sprint's value is the **10 markdown deliverables**:

1. `NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md` (Phase 0)
2. `CAMPAIGN_012_REJECTION_CLOSEOUT.md` (Phase 1)
3. `REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md` (Phase 2)
4. `NEXT_DIRECTION_REASSESSMENT_004.md` (Phase 3)
5. `CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md` (Phase 4)
6. `NEXT_PREFERRED_DIRECTION_004.md` (Phase 5)
7. `NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md` (Phase 6)
8. `NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md` (Phase 7a)
9. `NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md` (Phase 7b)
10. `NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md` (Phase 8 — this doc)

Plus the Phase 9 summary doc + small EVIDENCE_INDEX / STRATEGY_STATUS
edits.

A helper file would not add discipline; the 10-doc trail already
*is* the discipline (each doc cites the prior + is bound by the
guardrails + closes out a specific decision).

## 5. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 818 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |
| code added this sprint | **none** |
| tests added this sprint | **none** |
| validator / schema-checker change | **none** |

## 6. Cross-links

- [`NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md) (sibling — identical no-helper decision)
- [`NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md) (sibling — identical no-helper decision)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md) (discovery-001 sibling)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md) (Phase 0 of this sprint)
- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

# New Candidate Discovery Sprint 003 — Helper Decision Note

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-003`
`strategy_evidence: false`

Phase 7 decision note on whether this discovery sprint should
add any docs/schema helper code. **The decision is NO — no
helper code added in this sprint.** This document records the
options considered and the rationale for the no-code decision.

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. This sprint is design-only by charter; the
> 771-pytest baseline is preserved without effort.

## 1. Helper options considered

The prompt explicitly allowed:

> - docs-only checklist
> - candidate-vs-null comparison checklist
> - leakage-risk checklist
> - regime-feature checklist
> - schema/checker extension only if a relevant checker already
>   exists and the change is small

### Option A — A "candidate-vs-null comparison" markdown checklist

| pros | cons |
|---|---|
| Concrete, actionable for the future scaffold + evidence sprints | The comparison logic is already codified in [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §3 + §8 + §9 — a separate checklist file would split the source of truth |
| Reusable across future candidates (CAMPAIGN_013+, etc.) | The protocol's §13 documentation discipline is the same enforcement, but in markdown form |

**Decision: reject.** The Phase 1 null-baseline doc + Phase 5
implementation design §10.3 + Phase 6 evidence-branch spec §4
already contain the comparison table and "indistinguishable
from null?" classification rule. A separate file would
duplicate them.

### Option B — A "leakage-risk" markdown checklist

| pros | cons |
|---|---|
| Concrete; new candidates often introduce new leakage risks | The C3-specific leakage analysis is already in [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md) §5 (6 specific risks + mitigations); generic leakage rules are in [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md) §6 + [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md); a separate checklist would split the source of truth |

**Decision: reject.** Each candidate's leakage analysis belongs
in its own design doc (per the established pattern), not a
generic checklist.

### Option C — A "regime-feature" markdown checklist

A C3-specific guide to safe regime-feature computation.

| pros | cons |
|---|---|
| Concrete; the regime-feature pattern may be reused by future candidates | The C3-specific pattern is documented in [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md) §6 + [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md) §3 (R3) + §5; a separate checklist would duplicate |

**Decision: reject.** If a future candidate (CAMPAIGN_013+)
wants regime features, that candidate's design doc should
inherit / cite the C3 pattern explicitly, not via a generic
intermediate checklist.

### Option D — A "candidate-selection" markdown checklist

| pros | cons |
|---|---|
| Easier for the next discovery sprint to clone | The 9 Phase 0–8 deliverable docs from *this* sprint already serve as the template — the next discovery sprint can clone the file structure directly |
| Pure docs | Adds maintenance surface (a template that must be kept in sync with the actual deliverables drifts over time) |

**Decision: reject.** The
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md)
+
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md)
+ [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md)
triple acts as the structural template — a future discovery
sprint can mirror their phase outputs without an intermediate
template doc.

### Option E — Extend `scripts/validate_research_archive.py` to validate the new "null-baseline comparison" doc convention

A schema check that any future `CAMPAIGN_NN_WALK_FORWARD_RESULT.md`
contains a "Null-baseline comparison" section + the six metrics
verbatim.

| pros | cons |
|---|---|
| Tightens the existing rail; catches drift early | The validator currently checks `report_verdict_tokens` (the verdict keyword appears in the report); adding a section-header check is a new feature surface that risks false positives across all 11 prior campaigns (which do not have this section) |
| Could be unit-tested | The CAMPAIGN_012 evidence sprint can be the first to demonstrate the section; codifying the requirement in the *evidence-branch spec* (Phase 6b §4 Phase 4) is enforcement enough |

**Decision: reject.** The CAMPAIGN_012 evidence sprint's
verdict doc will include the section because the binding spec
([`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md)
Phase 4 + §8) requires it. A validator schema-check is a
deferred future improvement (recommended sprint name:
`infra-research-archive-validator-null-baseline-section-check-001`),
not in scope for this discovery sprint.

### Option F — Pre-allocate the CAMPAIGN_012 manifest entry as a placeholder

| pros | cons |
|---|---|
| Pre-allocates the slot | The validator's `check_manifest_schema` requires `report_path` and `artifact_folder` to exist; CAMPAIGN_012 has neither (no scaffold sprint has run yet). Adding a placeholder would break the validator. |

**Decision: reject.** CAMPAIGN_012 entry must wait for the
future evidence sprint. This is the convention CAMPAIGN_010 /
CAMPAIGN_011 scaffolds followed exactly.

## 2. The decision — no helper code added

This discovery sprint **adds zero Python files, zero schema
helpers, zero new tests, and zero template docs beyond the 9
phase-output documents prescribed by the sprint plan**:

1. `NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md` (Phase 0)
2. `CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md` (Phase 1)
3. `CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md` (Phase 2)
4. `C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md` (Phase 3)
5. `NEXT_PREFERRED_REAL_CANDIDATE_003.md` (Phase 4)
6. `NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md` (Phase 5)
7. `NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md` (Phase 6a)
8. `NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md` (Phase 6b)
9. `NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md` (Phase 7 — this doc)
10. `NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md` (Phase 8 — pending)
11. `EVIDENCE_INDEX.md` (Phase 8 update — pending)

Plus a possible small annotation to `STRATEGY_STATUS.md` in
Phase 8 noting the next candidate is selected (but not yet
implemented).

## 3. Why the no-code decision is the right call

| reason | detail |
|---|---|
| **Charter** | The prompt opens with "This is research/design-only unless a tiny docs/schema helper is clearly justified." None of the six options above clear that "clearly justified" bar. |
| **Test-suite preservation** | The 771-pytest baseline is preserved with zero risk by adding no code. |
| **Ruff posture preservation** | The 11 pre-existing UP042 findings remain unchanged. Adding code might introduce new findings. |
| **Single source of truth** | Each piece of would-be helper content already has a home: the null-baseline interpretation (Phase 1); the C3 leakage analysis (Phase 3 §5); the regime-feature pattern (Phase 3 §6 + Phase 5 §3.R3); the validator rail (deferred to a separate sprint); the manifest placeholder (deferred to the evidence sprint). |
| **Precedent** | The prior two discovery sprints made the same decision for the same reasons; the discipline held across two scaffold sprints + two evidence sprints without a helper. |
| **No scope creep** | The standing rule "Don't add features, refactor, or introduce abstractions beyond what the task requires" applies. |

## 4. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 remain REJECT**
  (untouched).
- No code added this sprint.
- No new tests added this sprint.
- No edits to `src/`, `tests/`, `scripts/`, or `research/` this
  sprint.
- pytest baseline: **771 passes** (unchanged).
- ruff: 11 pre-existing UP042 in untouched files (unchanged).
- Archive validator / freeze checker / secret scanner: all PASS.
- paper-loop / demo-loop refuse; no `live-loop`.

## 5. Cross-links

- [`NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md)
  (the prior discovery sprint's identical decision)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md)
  (the first discovery sprint's identical decision)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
- [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
- [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md)
- [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)

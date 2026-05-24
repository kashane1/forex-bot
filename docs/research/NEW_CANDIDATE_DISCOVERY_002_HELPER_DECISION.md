# New Candidate Discovery Sprint 002 — Helper Decision Note

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-002`
`strategy_evidence: false`

Phase 6 decision note on whether this discovery sprint should
add any docs/schema helper code. **The decision is NO — no
helper code added in this sprint.** This document records the
options considered and the rationale for the no-code decision.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. This sprint is design-only by charter; the
> protocol's §14 validation rail requires the test suite to be
> ≥ 702 passes (today: 735); a no-helper-added sprint preserves
> that without effort.

## 1. Helper options considered

The prompt explicitly allowed:

> - docs-only templates
> - a candidate-selection checklist
> - a validation checklist for future candidate design docs
> - tests only if a tiny schema/checker already exists and should
>   be extended

### Option A — Pydantic-style schema for a "candidate design doc"

| pros | cons |
|---|---|
| Forces future discovery sprints to emit consistent shapes | Adds Python to a docs-only sprint; the protocol already prescribes the structure verbatim |
| Could be lint-checked in CI | The protocol's §13 documentation discipline is the same enforcement, but in markdown form |
| Could be auto-rendered into a markdown template | Engineering burden vs. payoff is poor — markdown templates do the same with less infrastructure |

**Decision: reject.** The prior discovery sprint
([`NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md))
made the same call for the same reason and the discipline held.
Two consecutive discovery sprints have now produced cleanly
structured docs without a schema enforcer.

### Option B — A `candidate-selection checklist` markdown template

| pros | cons |
|---|---|
| Easier to copy / fill for the next discovery sprint | The 7 Phase 0–7 deliverable docs from *this* sprint already serve as the template — the next discovery sprint can clone the file structure directly |
| Pure docs (no code) | Adds maintenance surface (a template that must be kept in sync with the actual deliverables drifts over time) |

**Decision: reject.** The
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md)
+
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md)
pair already act as the structural template — a future
discovery sprint can mirror their phase outputs without an
intermediate template doc.

### Option C — A "validation checklist for future candidate design docs"

A checklist (markdown) the future scaffold sprint can tick off
before declaring its design ready.

| pros | cons |
|---|---|
| Concrete, actionable | The Phase 4 design doc
[`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
§19 already contains a pre-flight checklist for the future
scaffold sprint |
| Pure docs | Duplicates the Phase 4 checklist; risks divergence |

**Decision: reject.** The Phase 4 design's §19 pre-flight
checklist is the right place for this content; adding a parallel
file would split the source of truth.

### Option D — Extend tests of a tiny existing schema/checker

The only existing schema/checker that could reasonably be
extended is
[`scripts/validate_research_archive.py`](../../scripts/validate_research_archive.py)
(via `forex_bot.research_archive`). A possible extension:

> Validate that every CAMPAIGN_NN entry's `report_path` resolves
> to a file under either `backtests/` (for full evidence
> sprints) or `docs/research/` (for evidence-doc-only campaigns
> like CAMPAIGN_010 / CAMPAIGN_011).

| pros | cons |
|---|---|
| Tightens the existing rail | The rail already exists (`check_reports_exist`); the new check would be tightening pattern-matching, not a structural addition |
| Could be unit-tested | The CAMPAIGN_010 evidence sprint already proved the existing rail accepts a `docs/research/CAMPAIGN_010_*.md` report path correctly |

**Decision: reject.** The existing validator already enforces
`report_path` resolution and verdict-token corroboration. Adding
a directory-pattern check would be a code change for marginal
benefit, and this sprint is design-only.

### Option E — A research-archive entry for CAMPAIGN_011 as a placeholder

| pros | cons |
|---|---|
| Pre-allocates the manifest slot | The validator's
`check_manifest_schema` requires `report_path` and
`artifact_folder` to exist; CAMPAIGN_011 has neither (no
scaffold sprint has run yet). Adding a placeholder would
break the validator. |

**Decision: reject.** CAMPAIGN_011 entries must wait for the
future evidence sprint. This is the convention CAMPAIGN_010's
sprints followed exactly.

## 2. The decision — no helper code added

This discovery sprint **adds zero Python files, zero schema
helpers, zero new tests, and zero template docs beyond the 7
phase-output documents prescribed by the sprint plan**:

1. `NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md` (Phase 0)
2. `CAMPAIGN_010_REJECTION_CLOSEOUT.md` (Phase 1)
3. `REJECTED_FAMILY_OVERFIT_GUARDRAILS.md` (Phase 1)
4. `CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md` (Phase 2)
5. `NEXT_PREFERRED_CANDIDATE_002.md` (Phase 3)
6. `NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md` (Phase 4)
7. `NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md` (Phase 5)
8. `NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md` (Phase 5)
9. `NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md` (Phase 6 — this doc)
10. `NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md` (Phase 7 — pending)
11. `EVIDENCE_INDEX.md` (Phase 7 update — pending)

Plus a possible (small) edit to `STRATEGY_STATUS.md` in Phase 7
to record that the next candidate is selected (but not yet
implemented).

## 3. Why the no-code decision is the right call

| reason | detail |
|---|---|
| **Charter** | The user's prompt opens with "This is research/design-only **unless** a tiny docs/schema helper is clearly justified." The clear-justification bar is not met by any option above. |
| **Test-suite preservation** | The 735-pytest baseline is preserved with zero risk by adding no code. Any test addition would need to be validated against the existing assertions (and any test-count guard updates). |
| **Ruff posture preservation** | The 11 pre-existing UP042 findings remain unchanged. Adding code might introduce new findings (e.g. via new Pydantic models that themselves trip UP042). |
| **Single source of truth** | Each piece of would-be helper content already has a home: the protocol (§13 doc discipline), the Phase 4 design doc (§19 pre-flight checklist), the Phase 5 branch specs (§§4 / 6 / 7 / 8 phase plans), and the existing archive validator (`forex_bot.research_archive`). |
| **Precedent** | The prior discovery sprint made the same decision for the same reasons; the discipline held across an entire scaffold sprint and a complete evidence sprint without a helper. |
| **No scope creep** | The standing rule "Don't add features, refactor, or introduce abstractions beyond what the task requires" applies here. |

## 4. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- No code added this sprint.
- No new tests added this sprint.
- No edits to `src/`, `tests/`, `scripts/`, or `research/` this
  sprint.
- pytest baseline: **735 passes** (unchanged).
- ruff: 11 pre-existing UP042 in untouched files (unchanged).
- Archive validator / freeze checker / secret scanner: all PASS.
- paper-loop / demo-loop refuse; no `live-loop`.

## 5. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md)
  (the prior discovery sprint's identical decision)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
  §§13 / 14
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
  §19 (the pre-flight checklist already lives here)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)

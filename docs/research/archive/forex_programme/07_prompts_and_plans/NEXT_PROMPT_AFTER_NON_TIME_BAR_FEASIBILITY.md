# Next prompt after the non-time-bar feasibility study

**Sprint:** `research-range-volatility-bar-feasibility-001` · Phase 7
**Status:** drafted only — **do NOT execute in this sprint.**

The Phase-6 decision was **Option 3: keep the infrastructure, pause non-time-bar
strategy research** (no edge demonstrated; cost-feasibility is necessary-not-
sufficient; reopening requires a new external thesis through the front gate). Per the
protocol, because the lane **pauses**, the next sprint is a **research-closeout /
infrastructure** sprint — **NOT a new campaign, NOT CAMPAIGN_030, no evidence run.**

Two candidate next prompts are drafted below. **Recommended: Prompt A** (closeout +
archive integration + merge-readiness). Prompt B (external-thesis sourcing) is the
follow-on once A lands, and is the only path that can ever reopen the lane.

---

## Prompt A (recommended) — non-time-bar lane closeout & archive integration

```
We are starting a research closeout sprint from clean, updated origin/main.

Branch:
research-non-time-bar-lane-closeout-001

Context:
- CAMPAIGN_029 (usdjpy_range_bar_mtf_breakout) was REJECT_TRAIN_GATE (cost-defeated).
- research-range-volatility-bar-feasibility-001 then ran a diagnostic feasibility
  study (7 majors x 13 thresholds, C029 train window) and decided:
  Option 3 — KEEP non-time-bar infrastructure, PAUSE strategy search, with a strict
  external-thesis re-entry door. See:
    docs/research/NON_TIME_BAR_LANE_DECISION_AFTER_C029.md
    docs/research/SEVEN_PAIR_NON_TIME_BAR_FEASIBILITY_RESULT.md
    docs/research/USDJPY_NON_TIME_BAR_FEASIBILITY_RESULT.md

Goal:
Integrate this decision into the research archive and confirm merge-readiness.
This is a DOCS/ARCHIVE-ONLY closeout. Hard rules: no new campaign, no CAMPAIGN_030,
no strategy approved, no paper/demo/live, no OANDA calls, no tuning of C029, no
evidence/train/validation/test runs, no test lockbox. Commit only docs/archive/
index updates. Do not weaken the freeze.

Phases:
0. Baseline: clean origin/main; create branch; verify approved_strategies empty and
   loops still refuse; run pytest -q, ruff, check_research_freeze.py,
   validate_research_archive.py, scan_artifacts_for_secrets.py.
1. Update the research backlog / STATUS docs to record: non-time-bar lane = PAUSED
   (infra kept), C029 family closed, feasibility study complete, re-entry criteria.
2. Add the feasibility study + lane decision to EVIDENCE_INDEX / EVIDENCE_MANIFEST
   (whatever index files the archive validator checks), with correct verdict tokens
   ("diagnostic", "not approved", "no strategy evidence").
3. Cross-link the feasibility docs from the C029 final-interpretation / numbering /
   re-entry-gate docs so future readers find the lane status.
4. Re-run all five validators; fix any link/verdict-token failures.
5. Write docs/research/NON_TIME_BAR_LANE_CLOSEOUT_001_SUMMARY.md and confirm
   merge-readiness (no bulky artifacts, freeze intact, all gates green).

Deliver: branch name, commit hashes per phase, files changed, confirmation that
nothing was approved and the freeze holds, and the validator outputs.
```

## Prompt B (follow-on, the only lane-reopening path) — external non-time-bar thesis brief

```
We are starting an external-thesis sourcing sprint from clean, updated origin/main.

Branch:
research-non-time-bar-external-thesis-brief-001

Context:
The non-time-bar lane is PAUSED (see NON_TIME_BAR_LANE_DECISION_AFTER_C029.md). It can
only reopen with a NEW EXTERNAL THESIS that satisfies the re-entry criteria
(cost/threshold <= 0.10; cost/risk <= 0.05 i.e. range >= 25-30 pip or volatility
>= 50 pip; 200 <= bars/yr <= 20000; front-gate before any campaign number;
distinctness from C029 and the retired breakout/pullback families).

Goal:
Produce a DOCS-ONLY brief that either (a) presents one or more falsifiable external
theses for why a SPECIFIC wide-threshold non-time bar carries a gross edge
(microstructure/liquidity/order-flow/auction or an instrument-class change), each
mapped to the §4 re-entry criteria and the front-gate plan, OR (b) concludes no
credible external thesis exists yet and recommends continued pause.

Hard rules: docs only; no new campaign; no CAMPAIGN_030; no strategy approved; no
paper/demo/live; no OANDA calls; no C029 tuning; no evidence/train/validation/test;
no test lockbox. Do not weaken the freeze. Do NOT scaffold a campaign in this sprint —
a thesis that passes is handed to a SEPARATE future front-gate sprint.

Deliver: the brief, an explicit go/no-go on whether any thesis clears the §4 bar, and
(if go) the exact front-gate screen that must run BEFORE a campaign number is assigned.
```

---

## Why no campaign prompt

A campaign/scaffold prompt is deliberately **not** drafted: the lane is paused and
the re-entry door requires an external thesis that does not yet exist. Drafting a
scaffold prompt now would invite a C029 retune — the exact forking-path move the lane
decision forbids. The campaign door opens only **after** Prompt B yields a thesis that
clears the §4 criteria **and** passes the edge-discovery front gate.

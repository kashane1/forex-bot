# New Candidate Strategy Discovery — Sprint 003 Summary

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-003`
`strategy_evidence: false`

End-of-sprint summary and handoff for the third candidate
discovery sprint, opened after CAMPAIGN_011 (the C5 null-model
anchor) closed with the expected REJECT and established the
falsifiability floor. **No strategy was implemented, no campaign
was run, no broker call was made, no code was added, and no
approval was granted.** The 771-test baseline is preserved.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. CAMPAIGN_011 remains REJECT (null-model
> anchor). `configs/approved_strategies.yaml` remains
> `approved: []`. **The selected next real candidate (C3 — Daily
> ATR-percentile regime switcher, future CAMPAIGN_012) is NOT
> approved and cannot be approved by this sprint, the future
> scaffold sprint, or the future evidence sprint — only the full
> six-evidence ladder + a deliberate human approval action can
> approve it.**

## 1. What this sprint did

Nine markdown documents committed in eight numbered phases.
Each phase committed its own artifact(s) before the next began.

| phase | commit | deliverable(s) | LOC |
|---|---|---|---:|
| 0 | `d1aa55f` | [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md) | 297 |
| 1 | `7f44faf` | [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) | 242 |
| 2 | `308fd56` | [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md) | 304 |
| 3 | `fdb8309` | [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md) | 411 |
| 4 | `d294332` | [`NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md) | 360 |
| 5 | `315154c` | [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md) | 670 |
| 6 | `22de6d7` | [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md) + [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md) | 728 |
| 7 | `7585018` | [`NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md) | 168 |
| 8 | (this commit) | [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md) + [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) update + [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) annotation | — |

**Total: 9 new markdown docs (≈ 3,180 lines of documentation),
0 Python files, 0 test changes, 0 fixture changes, 0 config
changes, 0 new external dependencies.**

## 2. Latest repo state

| dimension | value |
|---|---|
| current branch | `claude/affectionate-fermi-d950fc` (worktree for `research-new-candidate-strategy-discovery-003`) |
| sprint tip commit | (this Phase 8 commit) |
| `git status` at sprint end | clean |
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
| candidate selection | **C3 — Daily-ATR-percentile regime switcher** chosen for future CAMPAIGN_012 |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (four refusal layers) |
| pytest baseline | **771 passes** (unchanged) |

## 3. CAMPAIGN_011 null-baseline interpretation (Phase 1 highlights)

Per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md):

| metric | CAMPAIGN_011 null floor | future real candidate must beat |
|---|---|---|
| aggregate expectancy R | −0.0024 R | by ≥ +0.0524 R → reach ≥ 0.05 R |
| aggregate profit factor | 0.91 | by ≥ +0.19 → reach ≥ 1.10 |
| aggregate return % (4 years) | −0.53 % | meaningfully positive (≥ +5 %) |
| `pairs_positive` | 3 / 7 | ≥ 4 / 7 |
| `fold_pass_rate` | 0 / 8 | 100 % (strict-pass) |

**Beating CAMPAIGN_011 is necessary but not sufficient.** Even
a candidate beating every CAMPAIGN_011 number must still pass
every per-fold + aggregate + financing + risk gate, plus earn
a deliberate human approval action.

**"Statistically indistinguishable from null"** is defined
quantitatively as metrics clustering within
**±0.005 R / ±0.10 PF / ±2 pp / ±1 pair** of CAMPAIGN_011's;
candidates whose metrics fall in this band must be classified
`REJECT (indistinguishable from null)` even if a single gate
happens to pass by luck.

The binding rules also forbid: tuning the random seed; using
CAMPAIGN_011 as a trading candidate; lowering future gates;
treating merely beating random as approval; result-driven
family selection; per-pair/per-fold filters motivated by
CAMPAIGN_011 output; re-running CAMPAIGN_011 with different
entry probability.

## 4. Candidate families reassessed (Phase 2 highlights)

Per
[`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md):

| candidate | distinctness min (vs all 6 rejected families) | blockers | overfit risk | recommendation |
|---|:---:|---|---|---|
| C2 (carry overlay) | 6 / 6 | **MODELED financing refused** (4-layer block) — long-term blocker | low | deferred |
| **C3 (regime switcher)** | **5 / 6** | **NONE HARD** — D1AGG aggregation infra already exists | medium (mitigated by Phase 3 pre-commit) | **SELECTED** |
| C4 (vol-expansion straddle) | 5 / 6 | **engine paired-entry support missing** — long-term blocker | medium | deferred (engine sprint required) |

C3 is the only candidate this sprint can responsibly select.
No new family proposed (the protocol whitelist + null-baseline
anti-overfit rules cover every plausible mechanism; proposing
a new family now would be pattern G "result-driven family
selection" if motivated by CAMPAIGN_011 output).

## 5. C3 feasibility deep dive (Phase 3 highlights)

Per
[`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md):

- **D1AGG aggregation infra** already exists
  (`src/forex_bot/backtesting/d1_aggregation.py` with
  `aggregate_h4_to_d1` + `D1AggregationResult` + `rollover_safe`);
  the C3 strategy can compute regime features in-process from
  H4 windowed data without invoking the CAMPAIGN_006 native-D1
  blocker.
- **Frozen parameters** pre-committed in Phase 3 §2 *before any
  code, before any backtest, before any view of CAMPAIGN_011
  output*:
  - `daily_atr_lookback = 14`
  - `regime_lookback_days = 60` (~3 trading months)
  - `regime_percentile_threshold = 0.70` ("top 30 %")
  - `min_close_move_atr_fraction = 0.25`
  - `trend_lookback_h4_bars = 4`
  - `atr_lookback_h4 = 14`, `atr_stop_multiple = 2.0`,
    `max_bars_in_trade = 6`, `trailing_stop = None`,
    `min_atr_pips = {}` (all matching CAMPAIGN_010 / 011)
- **Leakage analysis** covers 6 specific risks with concrete
  mitigations: current-incomplete-day's high/low (aggregator
  drops `incomplete` days); full-sample percentile (rolling
  60-day window strictly preceding the reference day);
  test-window leakage into train/validation (harness enforces
  fold boundaries); global percentile cache (per-bar
  computation); bar-`t` close in regime feature (feature uses
  only prior-completed-day D1AGG ATR); weekend/holiday handling
  (aggregator classifies separately).
- **Distinctness** vs every rejected family ≥ 5 / 6 (TF, VB,
  PB, MR, CAMPAIGN_010 session_breakout, CAMPAIGN_011 random
  anchor).
- **Feasibility status: GREEN** — no infrastructure prerequisite
  sprint required.

## 6. Selected next preferred real candidate

| field | value |
|---|---|
| candidate id (prior shortlist) | **C3** |
| candidate role | **real candidate** (potential paper-promotion candidate if it survives every gate + human approval) |
| proposed strategy id | `regime_switcher_atr_percentile` |
| proposed strategy version | `0.1.0-c012` |
| proposed campaign label | `CAMPAIGN_012` |
| proposed future scaffold branch | `research-regime-switcher-atr-percentile-001` |
| proposed future evidence branch | `research-regime-switcher-atr-percentile-walk-forward-001` |
| approval path | requires the full six-evidence ladder + a deliberate human approval action per [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md) |

### 6.1 Why C3 (high-level)

- It is the only remaining candidate that has zero hard
  infrastructure blockers.
- Distinctness from every rejected family ≥ 5 / 6.
- D1AGG aggregator already exists (no infra prerequisite).
- Plausibility of beating CAMPAIGN_011 null floor: medium
  (regime-conditional trend persistence has a weak prior in
  the literature; H4-specific evidence is thin; a
  frozen-parameter test is informative either way).
- Can produce a verdict in two sprints (scaffold + evidence).
- All frozen parameters pre-committed in Phase 3 §2 before any
  code, mitigating the medium-overfit-risk surface.

### 6.2 Why other candidates were deferred

- **C2 — carry overlay:** blocked on MODELED financing
  (separate credentialed-pilot sprint needed first).
- **C4 — vol-expansion straddle:** blocked on engine
  paired-entry support (separate engine sprint needed first).

## 7. Implementation design summary (Phase 5 highlights)

Per
[`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md):

- **Hypothesis** (frozen, verbatim): "Trend persistence on H4
  OANDA majors is regime-conditional. Only trade trend signals
  when the most recent completed D1AGG ATR-14 is in the top
  30 % of trailing 60 completed days. CAMPAIGN_011's metrics
  provide the null-baseline floor that a passing CAMPAIGN_012
  must beat by a meaningful margin."
- **R1–R8 signal rules**: warm-up (500 H4 bars); block re-entry
  while position open; compute regime via aggregator + Wilder
  ATR-14 + trailing-60 P70 percentile (HIGH_VOL gate);
  fail-closed on NaN H4 ATR; trend sub-signal `close[t] vs
  close[t-4]` with ATR-fraction filter; spread filter delegated
  to RiskEngine; ATR-stop placement; emit deterministic Signal.
- **Frozen parameters** (verbatim from Phase 3 §2).
- **No-lookahead binding** (11 invariants enforced by
  structural unit tests).
- **Walk-forward** inherited verbatim from CAMPAIGN_010 / 011:
  rolling/frozen, 540/180/180/180 days, 7-pair universe,
  2020-01-01 → 2026-05-20, 8 expected folds.
- **Gate vector** inherited verbatim from
  `CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §11.
- **NEW: Null-baseline comparison gate** per Phase 1 doc —
  CAMPAIGN_012's verdict doc must include the "Null-baseline
  comparison" section with binary "meaningful improvement over
  null?" verdict per metric + "indistinguishable from null?"
  classification.
- **Financing**: ESTIMATED + conservative stress; MODELED
  refused (blocks live promotion via existing rule; paper
  acceptable under human override).
- **Risk diagnostics**: regime-period clustering reporting added
  on top of CAMPAIGN_010/011 pattern.
- **Independent verifier**: not required for REJECT; REQUIRED
  for any paper-promotion verdict.
- **Rejection criteria**: any per-fold or aggregate gate fails;
  financing flips verdict; null-baseline indistinguishable;
  any structural-audit unit test fails; BLOCKED on pipeline.
- **PASS classification**: `RESEARCH_PASS_UNAPPROVED` pending
  items 5 + 6 of the six-evidence ladder. Even PASS does not
  approve.

## 8. Future branch specifications (Phase 6 highlights)

Two complete future-branch prompt specs committed:

- [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md):
  scaffold sprint (`research-regime-switcher-atr-percentile-001`),
  8 phases, strategy module (~250 LOC) + config + ≥ 25 unit
  tests + research config + CAMPAIGN_012 pre-commit (with
  binding null-baseline reference) + readiness docs + smoke.
  Baseline 771 → ≥ 796 pytests. No backtest run.
- [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md):
  evidence sprint (`research-regime-switcher-atr-percentile-walk-forward-001`),
  9 phases mirroring CAMPAIGN_011 exactly. Walk-forward +
  financing overlay + risk diagnostics + verifier readiness.
  Expected verdict: REJECT (most likely) or
  `RESEARCH_PASS_UNAPPROVED` (unlikely) or
  `REJECT (indistinguishable from null)`. UNEXPECTED-PASS
  playbook documented and binding.

Both specs explicitly **forbid approving** the strategy under
any circumstance — only deliberate human approval per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md),
after items 5 + 6 are satisfied, can do that.

## 9. Helper-decision (Phase 7)

Per
[`NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md):
six helper-code options considered (candidate-vs-null
comparison checklist; leakage-risk checklist; regime-feature
checklist; candidate-selection markdown template; extension of
the research-archive validator with null-baseline section
check; pre-allocating CAMPAIGN_012 manifest entry); all six
rejected. **No code added.** Each piece of would-be helper
content already has a home in the existing 8 phase-output docs.

## 10. Final validation (Phase 8)

| command | result |
|---|---|
| `python -m pytest -q` | **771 passed** (unchanged) |
| `ruff check src tests scripts research` | **3 pre-existing findings** in untouched `research/lean_parity/algorithms/` files (`2× RUF100` unused-noqa + `1× I001` unsorted-imports). Identical to the base-commit (66254f4) ruff state; no new findings introduced by this sprint. (Earlier sprint-summary docs cited "11 pre-existing UP042" — that historical baseline was reduced by intermediate sprints; the current count is 3.) |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED (11 campaigns; 14 diagnostic artifacts; expanded evidence-index links from the new sub-section; clean credential scan) |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refused |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refused |
| `python -m forex_bot.cli --help` | no `live-loop` command present |
| `git status --short` | clean (this Phase 8 commit pending) |

## 11. Was anything I/O-bearing done?

| dimension | status |
|---|---|
| code added | **none** |
| data fetched | **none** |
| broker / OANDA call | **none** |
| `.env` read | **none** |
| credentials read or printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| `MODELED` financing reached | **no** (four refusal layers intact) |
| QuantConnect / LEAN action | **none** (retired) |
| engine / financing / risk-policy code edit | **none** |
| `D1AGG` aggregator edit | **none** |
| campaign verdict change | **none** (CAMPAIGN_002 / 010 / 011 all unchanged) |
| CAMPAIGN_010 / 011 parameter "tweak" or "rescue" | **none** |
| new external dependency | **none** |

## 12. Safety state (unchanged from Phase 0)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 | REJECT |
| CAMPAIGN_010 | REJECT |
| CAMPAIGN_011 | REJECT (null-model anchor) |
| approved strategies | none |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| `MODELED` financing reachable | no (4 refusal layers) |
| live-promotion financing blocker | stands |
| pytest baseline (771) | preserved |

## 13. Remaining blockers

| blocker | affects | next step |
|---|---|---|
| **MODELED financing refused** | C2 (carry overlay) cannot be a paper candidate | `research-financing-modeled-capture-credentialed-001` — separately-authorized credentialed-pilot sprint to collect real `DAILY_FINANCING` events; required before MODELED slot can be lifted |
| **Engine paired-entry support absent** | C4 (vol-expansion straddle) cannot run on bespoke engine | `infra-engine-paired-entry-support-001` — separately-authorized engine sprint |
| **Independent verifier capability-locked to CAMPAIGN_002** | item 5 of six-evidence ladder cannot be satisfied for any post-CAMPAIGN_002 family today | `infra-free-local-parity-verifier-<FAMILY>-NNN` per family that survives walk-forward + financing; specifically `infra-free-local-parity-verifier-regime-switcher-001` is required if CAMPAIGN_012 unexpectedly passes |
| **3 pre-existing ruff findings** (2× RUF100 unused-noqa + 1× I001 unsorted-imports in `research/lean_parity/algorithms/`) | code-quality only; no runtime impact; would shrink the LEAN parity-attempt archive | `infra-ruff-lean-parity-archive-cleanup-001` — small cleanup sprint, low priority |

**None of these block CAMPAIGN_012** (the next selected real
candidate). The D1AGG aggregator + walk-forward harness +
financing calculator + risk diagnostics + RiskEngine are all
already in place.

## 14. Recommended next branch

**`research-regime-switcher-atr-percentile-001`** — the scaffold
sprint for the selected next real candidate (CAMPAIGN_012), per
[`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md).

Subsequent ordering (recommended):

1. `research-regime-switcher-atr-percentile-001` — scaffold (next)
2. `research-regime-switcher-atr-percentile-walk-forward-001` — evidence
3. (Conditional on PASS) `infra-free-local-parity-verifier-regime-switcher-001` — verifier extension
4. (Conditional on PASS + verifier) human approval action per `STRATEGY_APPROVAL_PROCESS.md`
5. (Eventual) `research-financing-modeled-capture-credentialed-001` — unblock MODELED for C2
6. (Eventual) `infra-engine-paired-entry-support-001` — unblock C4

## 15. Exact files to review first

For the next reviewer / future-sprint operator:

1. [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md)
   — this doc (sprint summary).
2. [`NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md)
   — Phase 4 candidate selection (C3 + CAMPAIGN_012).
3. [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
   — Phase 5 binding design (R1–R8, frozen parameters, walk-forward, financing, risk, verifier, rejection criteria, null-baseline comparison gate).
4. [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
   — Phase 3 feasibility deep dive (D1AGG integration, 6 leakage-risk mitigations, distinctness scoring, frozen parameter pre-commit).
5. [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
   — Phase 1 binding null-baseline rules (the falsifiability floor every future candidate must beat by a meaningful margin).
6. [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md)
   — Phase 6a future scaffold-branch prompt.
7. [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md)
   — Phase 6b future evidence-branch prompt.
8. [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md)
   — Phase 2 full C2/C3/C4 scoring against the 6-rejected baseline + CAMPAIGN_011 null floor.
9. [`NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md)
   — Phase 7 why no helper code was added.
10. [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md)
    — Phase 0 audit + 9-phase plan.

For the standing safety state:

- [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md) (now includes the "next real candidate selected" annotation)
- [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`docs/research/STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

## 16. EVIDENCE_MANIFEST.json

The manifest tracks **campaigns with concrete artifacts**.
This sprint adds no campaign artifact folder (no scaffold
sprint has run yet for CAMPAIGN_012), so `EVIDENCE_MANIFEST.json`
requires no edit in this sprint. Same deferral pattern as the
prior two discovery sprints + the CAMPAIGN_010 / 011 scaffold
sprints. The future CAMPAIGN_012 evidence sprint will add the
manifest entry once `WalkForwardResults` is committed.

The [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) is updated in
this commit to add a sub-section pointing at the 9 new
discovery-003 docs.

A small annotation is added to
[`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) recording that
the next real candidate (C3 / `regime_switcher_atr_percentile`
/ CAMPAIGN_012) has been **selected** for a future scaffold
sprint but has no scaffold and no verdict yet.

## 17. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
- [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_011_EVIDENCE_SUMMARY.md`](CAMPAIGN_011_EVIDENCE_SUMMARY.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`D1_AGGREGATION_DESIGN.md`](D1_AGGREGATION_DESIGN.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)

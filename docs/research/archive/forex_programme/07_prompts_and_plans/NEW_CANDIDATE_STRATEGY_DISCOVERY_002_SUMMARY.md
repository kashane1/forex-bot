# New Candidate Strategy Discovery — Sprint 002 Summary

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-002`
`strategy_evidence: false`

End-of-sprint summary and handoff for the second candidate
discovery sprint, opened after CAMPAIGN_010
(`session_breakout 0.1.0-c010`) was REJECTED. **No strategy was
implemented, no campaign was run, no broker call was made, no
code was added, and no approval was granted.** The 735-test
baseline is preserved.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **The selected next candidate (C5 — random
> entry diagnostic anchor, future CAMPAIGN_011) is a null model
> by design; it cannot be approved and is selected precisely
> because its purpose is to *validate the evidence pipeline*
> rather than to find an edge.**

## 1. What this sprint did

Nine markdown documents committed in eight numbered phases.
Each phase committed its own artifact(s) before the next began.

| phase | commit | deliverable(s) | LOC |
|---|---|---|---:|
| 0 | `863d5ea` | [`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md) | 261 |
| 1 | `1aac41d` | [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md) + [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) | 357 |
| 2 | `3de4a91` | [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md) | 396 |
| 3 | `39beec5` | [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md) | 339 |
| 4 | `4466e72` | [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md) | 514 |
| 5 | `94d4e76` | [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md) + [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md) | 798 |
| 6 | `f13346f` | [`NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md) | 169 |
| 7 | (this commit) | [`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md) + [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) update + [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) update | — |

**Total: 9 markdown docs (≈ 2,830 lines of documentation),
0 Python files, 0 test changes, 0 fixture changes, 0 config
changes, 0 new external dependencies.**

## 2. Latest repo state

| dimension | value |
|---|---|
| current branch | `claude/affectionate-fermi-d950fc` (worktree for `research-new-candidate-strategy-discovery-002`) |
| sprint tip commit | (this Phase 7 commit) |
| `git status` at sprint end | clean |
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| candidate selection | **C5 — random entry diagnostic anchor** chosen for future CAMPAIGN_011 |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (four refusal layers) |
| pytest baseline | **735 passes** (unchanged) |

## 3. Rejected-family closeout (Phase 1 highlights)

Per
[`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
and
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md):

- CAMPAIGN_010 reject metrics cited verbatim: `fold_pass_rate
  0/8`; `aggregate_expectancy_R −0.0408`; `profit_factor 0.04`;
  `pairs_positive 1/7`; financing strictly worsens.
- Every session-breakout parameter (sessions, ATR thresholds,
  stops, holding time, pair selection, direction filters,
  spread filters) is **off-limits to retune**.
- A binding **cooldown rule** disqualifies any future
  session-breakout-shaped proposal that re-uses any of
  CAMPAIGN_010's frozen parameters as motivation, that has the
  same primary entry signal shape, that claims distinctness
  only via parameter changes, that is motivated by
  CAMPAIGN_010's per-pair / per-fold output, or that is
  motivated by fold-6's marginal positive result.
- Cross-cutting **overfit guardrails** added for every future
  candidate: concrete illegitimate-vs-legitimate examples for
  each of the 7 §12 disqualifier patterns (test-window leakage,
  filter-set tuning, parameter range overlap, implicit per-pair
  tuning, pick-best-fold, rejection-criterion drift,
  result-driven family selection).

## 4. Candidate families reassessed (Phase 2 highlights)

Per
[`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md):

| candidate | distinctness min (vs all 5 rejected families) | blockers | overfit risk | recommendation |
|---|:---:|---|---|---|
| C2 (carry overlay) | 6/6 | **MODELED financing refused** (4-layer block); requires separate credentialed-pilot sprint | low | **deferred** |
| C3 (regime switcher) | 5/6 | D1 ATR aggregation; parameter-overlap soft warning | **medium-high** | **deferred (second priority after CAMPAIGN_011)** |
| C4 (vol-expansion straddle) | 5/6 | **engine paired-entry support** missing | medium | **deferred (engine sprint required)** |
| C5 (random-entry diagnostic anchor) | n/a (null model — exempt) | **none** | **none** | **SELECTED** |

C2 / C3 / C4 are deferred (not abandoned). Recommended ordering
after CAMPAIGN_011: C5 → C3 → C2 → C4.

No new family is proposed in this sprint; the protocol's §4
whitelist + §5 disallowed-list cover every plausible mechanism,
and proposing a "new" family after CAMPAIGN_010's rejection
risks pattern G (result-driven family selection).

## 5. Selected next preferred candidate

| field | value |
|---|---|
| candidate id (prior shortlist) | **C5** |
| candidate role | **diagnostic anchor / null model** (NOT a paper candidate) |
| proposed strategy id | `random_entry_anchor` |
| proposed strategy version | `0.1.0-c011` |
| proposed campaign label | `CAMPAIGN_011` |
| proposed future scaffold branch | `research-random-entry-diagnostic-anchor-001` |
| proposed future evidence branch | `research-random-entry-diagnostic-anchor-walk-forward-001` |
| approval path | **none — null model by design** |

### 5.1 Why C5 (high-level)

C5 is the highest-value, lowest-risk next step because:

- It is **structurally unable to be approved** (null model).
- It is **structurally unable to be parameter-tuned** (random by
  definition; the only "knob" is the master seed, frozen in the
  pre-commit).
- It is **structurally falsifiable** by construction (REJECT is
  the expected outcome).
- It has **zero infrastructure blockers** (engine, harness,
  financing, data, credentials all green).
- It **validates the evidence pipeline as designed** (CAMPAIGN_005's
  random benchmark was pre-walk-forward, pre-financing-overlay,
  pre-explicit-risk-diagnostics; CAMPAIGN_011 strictly improves
  on it).
- It **establishes the falsifiability bar** that every future
  C2 / C3 / C4 / new-family candidate must beat by a meaningful
  margin to count as evidence of an edge.

### 5.2 Why other candidates were deferred

- **C2 — carry overlay:** blocked on MODELED financing
  (separate credentialed-pilot sprint needed first; the
  4-layer MODELED refusal in `src/forex_bot/financing.py` plus
  `research/financing/` cannot be lifted by this sprint).
- **C3 — regime switcher:** strongest "real" candidate (zero
  infrastructure work to start; D1 ATR can be aggregated inside
  the strategy from H4 windowed data) but carries the
  parameter-overlap soft warning (atr_lookback=14,
  atr_multiple=2.0 shared with TF / VB / CAMPAIGN_010) and is
  "adjacent to CAMPAIGN_002 in spirit". Best to follow the
  CAMPAIGN_011 anchor so the comparison baseline is in place
  before testing a "real" candidate.
- **C4 — vol-expansion straddle:** requires engine paired-entry
  support; out of scope until a separate engine sprint.

## 6. Implementation design summary (Phase 4 highlights)

Per
[`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md):

- **Hypothesis** (frozen, verbatim): "A deterministic-seed
  coin-flip H4 entry on the 7-pair OANDA universe, under
  CAMPAIGN_010's exit + RiskEngine + financing logic, has no
  edge by construction. Its per-fold and aggregate expectancy
  sets the falsifiability bar."
- **R1–R8 signal rules**: warm-up; block re-entry;
  deterministic-seed coin flip via
  `sha256((master_seed, pair, t))`; entry-probability gate
  (~5 % per bar for CAMPAIGN_010-comparable trade counts); ATR
  fail-closed; spread filter delegated to RiskEngine; ATR-stop
  placement; emit deterministic `Signal`.
- **Frozen parameters**: master_seed=20260523,
  entry_probability_per_bar=0.05, atr_lookback=14,
  atr_stop_multiple=2.0, max_bars_in_trade=6, no trailing,
  no per-pair min_atr_pips.
- **No-lookahead** binding: seed input contains only
  `(master_seed, pair, bar_timestamp_iso)` — never close[t],
  never ATR, never any bar-t data.
- **Walk-forward** inherited verbatim from CAMPAIGN_010:
  rolling/frozen, 540/180/180/180 days, 7-pair universe,
  2020-01-01 → 2026-05-20, 8 expected folds.
- **Gate vector** inherited verbatim from
  `CAMPAIGN_010_PRECOMMIT_CHECKLIST.md` §10.
- **Financing**: ESTIMATED + conservative-stress; MODELED
  refused at four layers; expected magnitude ~−$45–55.
- **Risk diagnostics**: max concurrent = 1 (engine-enforced);
  per-pair distribution should be ~uniform; session clustering
  should be ~uniform across UTC hours (contrast vs CAMPAIGN_010's
  100 % London concentration).
- **Independent verifier**: extension not required (paper-promotion
  gate; null model cannot be paper-promoted); recommended
  follow-up: `infra-free-local-parity-verifier-random-entry-001`.
- **Rejection classification**: REJECT (expected), INCONCLUSIVE,
  BLOCKED, or UNEXPECTED PASS (the latter triggers an
  investigation playbook, never promotion).

## 7. Future branch specifications (Phase 5 highlights)

Two complete future-branch prompt specs committed:

- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md):
  scaffold sprint (`research-random-entry-diagnostic-anchor-001`),
  8 phases, strategy module + config + ≥ 20 unit tests +
  research config + CAMPAIGN_011 pre-commit + readiness docs +
  smoke. Baseline 735 → ≥ 755 pytests. No backtest run.
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md):
  evidence sprint (`research-random-entry-diagnostic-anchor-walk-forward-001`),
  9 phases mirroring CAMPAIGN_010 exactly. Walk-forward +
  financing overlay + risk diagnostics + verifier readiness.
  Expected verdict: REJECT. Unexpected-PASS playbook documented.

Both specs explicitly **forbid approving** the strategy under
any circumstance — null model by design.

## 8. Helper-decision (Phase 6)

Per
[`NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md):
five helper-code options considered (Pydantic schema for design
docs; markdown candidate-selection template; validation checklist
for future design docs; extension of `forex_bot.research_archive`
validator; pre-allocating CAMPAIGN_011 manifest entry); all
five rejected. **No code added.** Each piece of would-be helper
content already has a home (the protocol §13, the Phase 4
design §19, the Phase 5 branch specs, the existing archive
validator). Decision matches the prior discovery sprint's
identical no-helper call.

## 9. Final validation (Phase 7)

| command | result |
|---|---|
| `python -m pytest -q` | **735 passed in 2.92s** (unchanged) |
| `ruff check src tests scripts research` | **11 pre-existing UP042 findings** in untouched files (`research/parity_verifier/models.py`, `research/walk_forward/models.py`, `research/financing/models.py`, `research/lean_parity/algorithms/...`). Identical to the Phase 0 baseline and to the prior sprint's documented baseline. Not refactored — would change `str(EnumValue)` runtime semantics outside this sprint's scope. Recommended cleanup sprint: `infra-ruff-up042-stress-enum-001`. |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED (10 campaigns, 14 diagnostic artifacts, 154 evidence-index links, 2,1xx artifact files clean) |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED (registry empty, loops refuse, archive valid) |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED (pattern scan over 2,1xx files; no credential value or shape) |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refused |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refused |
| `python -m forex_bot.cli --help` | no `live-loop` command present |
| `git status --short` | clean (this Phase 7 commit pending) |

## 10. Was anything I/O-bearing done?

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
| campaign verdict change | **none** (CAMPAIGN_002 REJECT, CAMPAIGN_010 REJECT both unchanged) |
| CAMPAIGN_010 parameter "tweak" or "rescue" | **none** |
| new external dependency | **none** |

## 11. Safety state (unchanged from Phase 0)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 | REJECT |
| CAMPAIGN_010 | REJECT |
| approved strategies | none |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| `MODELED` financing reachable | no (4 refusal layers) |
| live-promotion financing blocker | stands |
| pytest baseline (735) | preserved |

## 12. Remaining blockers

| blocker | affects | next step |
|---|---|---|
| **MODELED financing refused** | C2 (carry overlay) cannot be a paper candidate | `research-financing-modeled-capture-credentialed-001` — separately-authorized credentialed-pilot sprint to collect real `DAILY_FINANCING` events; required before MODELED slot can be lifted |
| **Engine paired-entry support absent** | C4 (vol-expansion straddle) cannot run on the bespoke engine | `infra-engine-paired-entry-support-001` — separately-authorized engine sprint |
| **D1 aggregation status** | C3 (regime switcher) needs daily ATR; can be done in-strategy from H4 windowed data | will be addressed by the future C3 candidate sprint's Phase 4 design; no separate infra sprint required |
| **Independent verifier capability-locked to CAMPAIGN_002** | item 5 of the six-evidence ladder cannot be satisfied for any post-CAMPAIGN_002 family today | `infra-free-local-parity-verifier-<FAMILY>-NNN` sprint per family that survives walk-forward + financing |
| **11 pre-existing UP042 ruff findings** | code-quality only; no runtime impact | `infra-ruff-up042-stress-enum-001` — small cleanup sprint, low priority |

None of these block CAMPAIGN_011 (the next selected candidate)
because the diagnostic-anchor framing has no MODELED, no D1, no
paired-entry, and no verifier dependency.

## 13. Recommended next branch

**`research-random-entry-diagnostic-anchor-001`** — the scaffold
sprint for the selected next candidate (CAMPAIGN_011), per
[`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md).

Subsequent ordering (recommended):

1. `research-random-entry-diagnostic-anchor-001` — scaffold (this is next)
2. `research-random-entry-diagnostic-anchor-walk-forward-001` — evidence
3. (Optional) `infra-free-local-parity-verifier-random-entry-001` — verifier coverage
4. `research-new-candidate-strategy-discovery-003` — pick the next *real* candidate (likely C3 — regime switcher)
5. (Eventual) `research-financing-modeled-capture-credentialed-001` — unblock MODELED for C2
6. (Eventual) `infra-engine-paired-entry-support-001` — unblock C4

## 14. Exact files to review first

For the next reviewer / future-sprint operator:

1. [`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md)
   — Phase 0 audit + sprint plan.
2. [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)
   — Phase 3 candidate selection (C5 + CAMPAIGN_011).
3. [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
   — Phase 4 binding design (R1–R8, frozen parameters, walk-forward, financing, risk, verifier).
4. [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md)
   — Phase 5a future-branch prompt for the scaffold sprint.
5. [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
   — Phase 5b future-branch prompt for the evidence sprint.
6. [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
   — what CAMPAIGN_010's REJECT means for future work + cooldown rule.
7. [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
   — anti-overfit rules every future candidate must satisfy.
8. [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md)
   — full scoring of C2 / C3 / C4 / C5 + recommendation rationale.
9. [`NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md)
   — why no helper code was added.
10. (this doc) — sprint summary.

For the standing safety state:

- [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`docs/research/STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

## 15. EVIDENCE_MANIFEST.json

The manifest tracks **campaigns** with concrete artifacts. This
sprint adds no campaign (no scaffold sprint has run yet for
CAMPAIGN_011, no evidence sprint has run, so there are no
artifacts to manifest). `EVIDENCE_MANIFEST.json` requires no
edit in this sprint. The same posture was taken by the prior
discovery sprint and by the CAMPAIGN_010 scaffold sprint —
both deferred their manifest entries to the evidence sprint.

The [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) is updated in this
commit to add a sub-section pointing at the nine discovery-002
docs.

## 16. STRATEGY_STATUS.md note

A small annotation is added to
[`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) recording that the
next candidate (CAMPAIGN_011) has been **selected for a future
scaffold sprint** but has **no scaffold and no verdict yet**.
The row is informational; no verdict appears until the future
evidence sprint runs.

## 17. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
- [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_010_EVIDENCE_SUMMARY.md`](CAMPAIGN_010_EVIDENCE_SUMMARY.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)

# `research-new-candidate-strategy-discovery-004` — Sprint Summary

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-004`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

End-of-sprint summary for the discovery-004 sprint. Re-opened
candidate selection after CAMPAIGN_012's REJECT; selected **C6 —
Cross-Pair Currency Strength Rotation** as the next real candidate
(`cross_pair_currency_strength_rotation 0.1.0-c013`, CAMPAIGN_013).
**Design / discovery sprint only — no strategy implementation, no
backtest, no broker call.**

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked. CAMPAIGN_011 is the null
> baseline only, not a trading candidate.

## 1. What changed

| dimension | value |
|---|---|
| commits this sprint | 10 (Phase 0 through Phase 9) |
| files added | 10 NEW docs |
| files edited | 2 (EVIDENCE_INDEX + STRATEGY_STATUS) |
| Python LOC added | **0** |
| test LOC added | **0** |
| markdown LOC added | ~2,800 |
| pytest count | **818 → 818** (preserved) |
| ruff findings | **3 pre-existing** in `research/lean_parity/algorithms/` (unchanged baseline) |

## 2. Commits by phase

| phase | commit | scope |
|---|---|---|
| Phase 0 | `9919563` | repo truth audit & discovery plan |
| Phase 1 | `769a96e` | CAMPAIGN_012 rejection closeout |
| Phase 2 | `e19adba` | guardrails addendum (Patterns H–L) |
| Phase 3 | `a911b9c` | reassess candidates + infrastructure |
| Phase 4 | `027b972` | candidate family shortlist (C6 / C7 / C8 / C9) |
| Phase 5 | `303ff6e` | select next path — C6 (CPCSR) |
| Phase 6 | `ba8ff05` | C6 implementation + evaluation design |
| Phase 7 | `dc79370` | future scaffold + evidence branch specs |
| Phase 8 | `b3619d4` | helper decision — NO helper |
| Phase 9 | (this commit) | summary + EVIDENCE_INDEX + STRATEGY_STATUS update + final validation |

## 3. Latest repo state

| dimension | value |
|---|---|
| pytest count | 818 passed (3.x s) |
| ruff status | 3 pre-existing in `research/lean_parity/algorithms/` (unchanged) |
| `validate_research_archive.py` | ALL PASS (12 campaigns) |
| `check_research_freeze.py` | ALL PASS (loops refuse) |
| `scan_artifacts_for_secrets.py` | PASSED |
| `paper-loop` / `demo-loop` | refuse |
| `live-loop` | does not exist |
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 / 010 / 011 / 012 | all REJECT (untouched) |

## 4. CAMPAIGN_012 rejection closeout (Phase 1)

Codified CAMPAIGN_012's REJECT verdict + off-limits parameter
surface (12 frozen parameters + 5 illegitimate extension patterns)
and a binding cooldown rule. The regime-switcher family is on
indefinite cooldown until a future human explicitly authorizes a
"materially different" regime-switching thesis.

## 5. Updated anti-overfit guardrails (Phase 2)

Discovery-004 addendum adds 5 new disqualifying overfitting patterns
(H–L) specifically motivated by CAMPAIGN_012:

- **H** — "same regime gate, different threshold" (forbidden)
- **I** — "same trend filter, different lookback" (forbidden)
- **J** — "same daily-ATR-percentile, different cutoff" (forbidden;
  including inversion)
- **K** — "rescue rejected regime switcher with session/pair/day
  filters" (forbidden — rejected-family stack)
- **L** — "pick new family because it fixes a CAMPAIGN_012 per-fold
  artifact" (forbidden — fitting to noise within a REJECT aggregate)

Plus "genuinely new" criteria (7 axes) any candidate must satisfy
after the now-7 rejected baseline (5 prior + CAMPAIGN_011 null +
CAMPAIGN_012 real).

## 6. Candidate and infrastructure paths reassessed (Phase 3)

7 paths scored on 15 axes:

| path | type | status |
|---|---|---|
| C2 carry overlay | candidate | DEFERRED (gated by infra-A) |
| C4 vol-expansion paired straddle | candidate | DEFERRED (gated by infra-B; multi-sprint engine rewrite) |
| C6+ new families | candidate | VIABLE (Phase 4 shortlist) |
| infra-A `research-financing-modeled-capture-credentialed-001` | infrastructure | HOLD (requires human authorization) |
| infra-B `infra-engine-paired-entry-support-001` | infrastructure | HOLD (multi-sprint; only C4 justifies today) |
| infra-C verifier extension per-family | infrastructure | DEFER (post-PASS; no candidate has passed) |
| infra-D ruff cleanup | infrastructure | LOW PRIORITY (cosmetic) |

Recommended path: C6+ discovery-driven family selection (zero
blockers; evaluable honestly today).

## 7. New candidate families proposed (Phase 4)

Shortlist of 4 genuinely-new families:

| candidate | name | distinctness | blockers |
|---|---|:---:|---|
| **C6** | Cross-Pair Currency Strength Rotation (CPCSR) | 6 / 6 | **NONE** |
| C7 | Calendar-Event Window Anomaly (CEWA) | 6 / 6 | NEW data dep (calendar fixture) |
| C8 | Multi-Window Volatility-Compression Breakout | 6 / 6 | CAMPAIGN_004 proximity risk |
| C9 | Time-of-Day Cost-Adjusted Mean Reversion on Spreads | 5 / 6 | CAMPAIGN_008/009 proximity risk |

13 disqualified family variants documented (regime-switcher retunes,
C2/C4 without infra unblocks, trend-following + new knob,
vol-breakout 0.2.0, MR 0.3.0, session-breakout 0.2.0,
pullback-continuation 0.2.0, weighted-pair-vote ensembles).

## 8. Selected next path (Phase 5)

# **SELECTED: C6 — Cross-Pair Currency Strength Rotation (CPCSR)**

| field | value |
|---|---|
| candidate id | C6 |
| strategy id | `cross_pair_currency_strength_rotation` |
| version | `0.1.0-c013` |
| campaign label | **CAMPAIGN_013** |
| scaffold branch | `research-cross-pair-currency-strength-rotation-001` |
| evidence branch | `research-cross-pair-currency-strength-rotation-walk-forward-001` |

**Why C6 over C7 / C8 / C9 / infra-A / infra-B / infra-C / infra-D:**

- Zero new data dependencies (vs C7's calendar fixture).
- Structurally furthest from rejected families (vs C8's CAMPAIGN_004
  proximity, C9's CAMPAIGN_008/009 proximity).
- Distinctness 6/6 vs every rejected family.
- Fits bespoke engine + existing local store + ESTIMATED financing
  with no infra change (vs infra-A's human-authorization requirement,
  infra-B's multi-sprint engine rewrite).
- Post-PASS infrastructure (infra-C) is not yet warranted; cosmetic
  cleanup (infra-D) does not unblock anything.

## 9. Why selected path is distinct from rejected families

| rejected family | shared mechanism with C6? | distinctness argument |
|---|---|---|
| CAMPAIGN_002 (`trend_following`) | NO | no EMA / Donchian / single-pair direction trigger; signal is *cross-pair rank delta*, not within-pair momentum |
| CAMPAIGN_010 (`session_breakout`) | NO | no session windows |
| CAMPAIGN_011 (`random_entry_anchor`, null) | NO | fully deterministic from price; no PRNG |
| CAMPAIGN_012 (`regime_switcher_atr_percentile`) | NO | no single-pair vol-percentile gate; signal is structural cross-pair relative strength |
| CAMPAIGN_004 (`volatility_breakout`) | NO | no ATR-compression / breakout logic |
| CAMPAIGN_007 (`pullback_continuation`) | NO | no pullback definition |
| CAMPAIGN_008 / 009 (`mean_reversion`) | NO | trades *in direction of relative strength*, not counter to range overshoot |

**Distinctness vs each rejected family: 6 / 6.**

## 10. Why this is not parameter tuning

- No existing strategy in the bespoke engine implements cross-pair
  ranking (all 7 implemented strategies operate on a single instrument
  at a time).
- C6 requires a new orchestration layer that reads all 7 pairs' H4
  closes simultaneously — a new mechanism, not a knob.
- C6's frozen parameters (`currency_strength_lookback_bars = 24`,
  `rank_gap_threshold = 4`, etc.) are pre-committed pre-implementation;
  no sweep around prior campaigns' values.
- No CAMPAIGN_012 parameter is reused.

## 11. Implementation design summary (Phase 6 highlights)

- **R1–R8 rule table** (binding) — warm-up, re-entry block, sibling-
  pair close read from `ctx.config`, 8-currency strength computation
  with USD-base / USD-quote sign convention, rank computation +
  rank-gap gate, H4 ATR fail-closed, ATR stop placement, deterministic
  Signal emission.
- **12 no-lookahead invariants** binding for Phase 3 of the scaffold
  sprint to enforce.
- **9 frozen parameters** pre-committed.
- **`CrossPairCurrencyStrengthRotationStrategyConfig` schema** with
  `extra="forbid"` + `@model_validator` rejecting invalid bounds.
- **≥ 30 unit tests** planned (config validation, happy path, sign
  convention, R1–R8 fixtures, no-lookahead audit, forbidden imports,
  rejected-family contamination, approval regression).
- **Walk-forward** inherits CAMPAIGN_010 / 011 / 012 plan verbatim
  (8 folds rolling/frozen) + null-baseline comparison gate.
- **Financing** ESTIMATED + conservative stress; MODELED refused
  (live-promotion blocker stands).
- **Risk diagnostics** must include CAMPAIGN_013-specific rank-gap
  clustering + simultaneous-signal frequency + cross-pair concurrent
  rejection rate.
- **Verifier extension** required only if `RESEARCH_PASS_UNAPPROVED`.

## 12. Future branch specs (Phase 7)

Two binding prompt templates for the next Claude Code instances:

- **`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`** — scaffold sprint
  `research-cross-pair-currency-strength-rotation-001` (8 phases;
  no evidence run; test target 818 → ≥ 848).
- **`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`** — evidence sprint
  `research-cross-pair-currency-strength-rotation-walk-forward-001`
  (10 phases; runs walk-forward + financing + risk + verifier-
  assessment; binding **cross-pair-runner integration contract**).

## 13. Safety state at sprint close

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
| CAMPAIGN_012 | REJECT (untouched) |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| live-promotion financing blocker | stands |
| broker / OANDA call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| historical campaign verdict change | **none** |
| parameter "tweak" or "rescue" | **none** (no rejected family revived) |
| pytest baseline | 818 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |
| code added this sprint | **none** |
| tests added this sprint | **none** |

## 14. Validations run

```
python -m pytest -q                                       # 818 passed
ruff check src tests scripts research                     # 3 pre-existing
python scripts/validate_research_archive.py               # ALL PASS
python scripts/check_research_freeze.py                   # ALL PASS
python scripts/scan_artifacts_for_secrets.py              # PASSED
python -m forex_bot.cli paper-loop -c configs/paper.yaml  # refused
python -m forex_bot.cli demo-loop -c configs/practice.yaml # refused
python -m forex_bot.cli --help                            # no live-loop
git status --short                                        # clean
```

## 15. Remaining blockers

| blocker | affects | next step |
|---|---|---|
| MODELED financing refused at 4 layers | C2 + future carry candidates | `research-financing-modeled-capture-credentialed-001` (requires human authorization; out of scope for Claude Code) |
| engine lacks paired-entry support | C4 + future paired/spread candidates | `infra-engine-paired-entry-support-001` (multi-sprint; HOLD until additional multi-family justification) |
| verifier capability-locked to CAMPAIGN_002 | item 5 of six-evidence ladder for any non-`trend_following` paper-promotion candidate | `infra-free-local-parity-verifier-<FAMILY>-NNN` per family; not needed until a candidate reaches `RESEARCH_PASS_UNAPPROVED` |
| 3 pre-existing ruff findings | cosmetic | `infra-ruff-lean-parity-archive-cleanup-001` (low priority) |

**None of these block CAMPAIGN_013's scaffold sprint or evidence sprint.**

## 16. Recommended next branch

### **`research-cross-pair-currency-strength-rotation-001`** (scaffold sprint)

The 8-phase scaffold-branch prompt is the full text of
[`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md).
Adds strategy module + config schema + ≥ 30 unit tests + research
config + CAMPAIGN_013 docs + non-evidence smoke. Test-count target
818 → ≥ 848. No backtest run; no broker call; no approval.

After the scaffold completes, the recommended sprint after is
**`research-cross-pair-currency-strength-rotation-walk-forward-001`**
(the 10-phase evidence sprint, full prompt in
[`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md)).

## 17. Exact files to review first

In review order:

1. **[`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md)** — this one-page sprint summary.
2. **[`NEXT_PREFERRED_DIRECTION_004.md`](NEXT_PREFERRED_DIRECTION_004.md)** — Phase 5 selection (C6 / CAMPAIGN_013); selection rationale vs every other path.
3. **[`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md)** — binding R1–R8 + 9 frozen parameters + 12 no-lookahead invariants + 30+ expected tests.
4. **[`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md)** — the prompt for the next sprint.
5. **[`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md)** — the prompt for the sprint after that, including the binding cross-pair-runner integration contract.
6. **[`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md)** — the off-limits parameter surface for the rejected regime-switcher family.
7. **[`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)** — binding Patterns H–L + "genuinely new" criteria.
8. **[`NEXT_DIRECTION_REASSESSMENT_004.md`](NEXT_DIRECTION_REASSESSMENT_004.md)** — Phase 3 candidate/infra scoring.
9. **[`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md)** — Phase 4 C6 / C7 / C8 / C9 proposals.
10. **[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)** (reference) — binding null baseline.
11. **[`NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md)** — no-helper rationale.
12. (Reference) **[`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md)** — Phase 0 plan.

## 18. Cross-links

- [`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md) (the predecessor evidence sprint's outcome)
- [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md) (predecessor sprint summary)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md) (predecessor discovery sprint)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)

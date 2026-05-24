# New Candidate Strategy Discovery — Sprint 003 Plan

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-003`
`strategy_evidence: false`

Phase 0 truth audit + sprint plan for the third candidate-discovery
sprint, opened after CAMPAIGN_011 / `random_entry_anchor
0.1.0-c011` (the C5 null-model anchor) closed with the expected
REJECT and established the **falsifiability floor** every future
real candidate must beat by a meaningful margin. **This document
does not approve any strategy and does not implement any strategy.**

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. CAMPAIGN_011 remains REJECT (null-model anchor;
> cannot be approved by design). `configs/approved_strategies.yaml`
> remains `approved: []`. Paper / demo / live remain blocked. This
> is a **design / selection** sprint — no new strategy code, no
> new backtest, no broker call, no parameter tuning.

## 1. Repo state (Phase 0 audit)

| dimension | value |
|---|---|
| current branch | `claude/affectionate-fermi-d950fc` (worktree for `research-new-candidate-strategy-discovery-003`) |
| base commit | `66254f4` — Phase 9 of `research-random-entry-diagnostic-anchor-walk-forward-001` (CAMPAIGN_011 REJECT, status registries updated) |
| worktree path | `/Users/kashane/dev/forex-bot/.claude/worktrees/affectionate-fermi-d950fc/` |
| `git status` at Phase 0 start | clean |
| `configs/approved_strategies.yaml` | **`approved: []`** (verified) |
| CAMPAIGN_002 status | **REJECT** (unchanged; untouched) |
| CAMPAIGN_010 status | **REJECT** (unchanged; untouched) |
| CAMPAIGN_011 status | **REJECT (null-model anchor)** (unchanged; cannot be approved by design) |
| paper-loop / demo-loop | refuse — verified |
| live-loop | does not exist — verified |
| QuantConnect / LEAN | retired; not used |

### 1.1 Baseline validation results

| check | result |
|---|---|
| `python -m pytest -q` | **771 passed** in 3.10s (unchanged from prior sprint) |
| `ruff check src tests scripts research` | **11 pre-existing UP042 findings** in untouched files (`research/parity_verifier/models.py`, `research/walk_forward/models.py`, `research/financing/models.py`, `research/lean_parity/algorithms/...`). Matches the documented baseline from prior sprints. |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED (11 campaigns including CAMPAIGN_011, 14 diagnostic artifacts, 185 evidence-index links, 2,290 artifact files clean) |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED (registry empty, loops refuse, archive valid) |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED (no credential value or shape) |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refused (registry empty) |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refused (registry empty) |
| `python -m forex_bot.cli --help` | no `live-loop` command present |

### 1.2 Files inspected (read-only)

Latest sprint outputs (the CAMPAIGN_011 evidence sprint):

- [`docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md)
- [`docs/research/CAMPAIGN_011_EVIDENCE_SUMMARY.md`](CAMPAIGN_011_EVIDENCE_SUMMARY.md)
- [`docs/research/CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
- [`docs/research/CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`docs/research/CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`docs/research/CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md)
- [`docs/research/CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md)

Prior-sprint candidate-discovery docs (the binding context):

- [`docs/research/CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md)
- [`docs/research/NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)
- [`docs/research/NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
- [`docs/research/CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
- [`docs/research/REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- [`docs/research/CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
- [`docs/research/STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`docs/research/STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`docs/research/WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`docs/research/FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`docs/research/D1_AGGREGATION_DESIGN.md`](D1_AGGREGATION_DESIGN.md) (the existing H4→D1AGG aggregation design — relevant for C3)

Implementation surface (read-only; no edits in this sprint):

- [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
- [`src/forex_bot/strategies/`](../../src/forex_bot/strategies/) (mean_reversion, pullback_continuation, random_entry_anchor, session_breakout, trend_following, volatility_breakout, base, indicators)
- [`src/forex_bot/config.py`](../../src/forex_bot/config.py) (`StrategyConfig` slots)
- [`src/forex_bot/backtesting/d1_aggregation.py`](../../src/forex_bot/backtesting/d1_aggregation.py) (existing H4→D1AGG aggregator with `rollover_safe` clearance — relevant for C3)
- [`configs/campaign_010_session_breakout.yaml`](../../configs/campaign_010_session_breakout.yaml)
- [`configs/campaign_011_random_entry_anchor.yaml`](../../configs/campaign_011_random_entry_anchor.yaml)
- [`scripts/run_campaign_010.py`](../../scripts/run_campaign_010.py), [`scripts/run_campaign_011.py`](../../scripts/run_campaign_011.py)
- [`research/walk_forward/`](../../research/walk_forward/), [`research/financing/`](../../research/financing/)

## 2. Repo-truth summary

### 2.1 Latest campaign statuses (verified at Phase 0)

| campaign | strategy / version | verdict | primary evidence |
|---|---|---|---|
| CAMPAIGN_001 | `trend_following 0.1.0` (synthetic) | SYNTHETIC_NOT_EVIDENCE | superseded by CAMPAIGN_002 |
| CAMPAIGN_002 | `trend_following 0.1.0` (real OANDA H4) | **REJECT** | [`CAMPAIGN_002_FINANCING_RETROSPECTIVE.md`](CAMPAIGN_002_FINANCING_RETROSPECTIVE.md) |
| CAMPAIGN_003 | `trend_following + ADX-14 > 25` | **REJECT** | [`CAMPAIGN_003_POSTMORTEM.md`](CAMPAIGN_003_POSTMORTEM.md) |
| CAMPAIGN_004 | `volatility_breakout 0.1.0-c004` | **REJECT** | [`CAMPAIGN_004_PRECOMMIT.md`](CAMPAIGN_004_PRECOMMIT.md) |
| CAMPAIGN_005 | benchmarks / random / always-long | DIAGNOSTIC | [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md) |
| CAMPAIGN_006 | D1 daily trend | BLOCKED | [`CAMPAIGN_006_DAILY_TREND_PRECOMMIT.md`](CAMPAIGN_006_DAILY_TREND_PRECOMMIT.md) |
| CAMPAIGN_007 | `pullback_continuation` | **REJECT** | [`CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md`](CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md) |
| CAMPAIGN_008 | `mean_reversion 0.1.0-c008` | **REJECT** | [`CAMPAIGN_008_HUMAN_REVIEW.md`](CAMPAIGN_008_HUMAN_REVIEW.md) |
| CAMPAIGN_009 | `mean_reversion 0.2.0-c009` | **REJECT** | [`CAMPAIGN_009_PRECOMMIT.md`](CAMPAIGN_009_PRECOMMIT.md) |
| CAMPAIGN_010 | `session_breakout 0.1.0-c010` | **REJECT** | [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) |
| CAMPAIGN_011 | `random_entry_anchor 0.1.0-c011` | **REJECT (null-model anchor)** | [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) |

### 2.2 CAMPAIGN_011 null-baseline (what the next real candidate must beat)

| metric | CAMPAIGN_011 (random anchor) |
|---|---|
| folds executed | 8 |
| total trades | 1,177 |
| `fold_pass_rate` | 0 / 8 |
| `aggregate_expectancy_r` | **−0.0024 R** (≈ 0; null-model signature) |
| `aggregate_profit_factor` | **0.91** (≈ 1) |
| `aggregate_return_pct` | **−0.53 %** over 4 years |
| `pairs_positive` | **3 / 7** (close to uniform-noise expectation of ~3.5) |
| financing impact | strictly worsens; USD_JPY flips +→− under stress |
| verifier ran? | no (capability-locked to CAMPAIGN_002; not required for null-model REJECT) |
| approval path | **none (null model by design)** |

Phase 1 of this sprint will formalize the null-baseline
interpretation and the "meaningful improvement over null"
definition.

### 2.3 Current approved-strategy status

Empty. Every candidate ever evaluated has been either REJECTED,
SYNTHETIC_NOT_EVIDENCE, DIAGNOSTIC, BLOCKED, or REJECTED (null
model). `configs/approved_strategies.yaml` reads `approved: []`
and no strategy is in any active loop.

### 2.4 Safety state (unchanged across all prior sprints + this Phase 0)

| dimension | status |
|---|---|
| approved registry | `approved: []` |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched this sprint) |
| paper-loop / demo-loop refuse | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| broker / OANDA call this sprint | none |
| `.env` read | none |
| credentials printed | none |
| engine-PnL change | none |
| `src/forex_bot/financing.py` change | none |
| `MODELED` financing reachable | no (four refusal layers) |
| pytest baseline | **771 passes** |

## 3. Sprint scope (design + selection only)

| dimension | scope |
|---|---|
| sprint type | candidate **selection** + **design**, not implementation |
| Python code added | **none** (Phase 7 may add a tiny docs-only helper only if clearly useful) |
| backtests run | **none** |
| broker calls | **none** |
| data fetched | **none** |
| approval actions | **none** (and structurally cannot — the next candidate, even if selected, is not added to `configs/approved_strategies.yaml` by this sprint) |
| target deliverables | 9 new docs (Phase 0–8 outputs); Phase 8 also updates `EVIDENCE_INDEX.md` and `STRATEGY_STATUS.md` |

## 4. Candidate-selection goals

1. **Use CAMPAIGN_011 as the null-baseline reference** for every
   reassessment. Any real candidate proposal must explain how it
   plausibly beats CAMPAIGN_011's metrics (aggregate expectancy
   −0.0024 R, profit factor 0.91, 3/7 pairs positive, 0/8 fold
   pass rate) by a meaningful margin, not just by noise.
2. **Reassess C2 / C3 / C4** from the prior shortlist using
   CAMPAIGN_011 as a new comparison floor + current infrastructure
   constraints (MODELED financing still refused; paired-entry
   engine support still absent; D1AGG aggregation infra **is**
   present per `src/forex_bot/backtesting/d1_aggregation.py`).
3. **Surface every blocker honestly** — engine constraints,
   MODELED-financing refusal, D1AGG status, missing verifier
   coverage, etc.
4. **Pick exactly one next real candidate** for a future scaffold
   sprint, with a candidate id, strategy id, version, and
   proposed `CAMPAIGN_012` label. Or pick an infrastructure
   prerequisite branch if all real candidates are blocked.
5. **Document a falsifiable rejection criterion** in the
   implementation design so the future scaffold + evidence
   sprints inherit a non-negotiable gate vector — including the
   null-baseline comparison gate.
6. **Be willing to pick an infrastructure prerequisite** (e.g.
   `infra-engine-paired-entry-support-001` or
   `research-financing-modeled-capture-credentialed-001`) if no
   real candidate is feasibly ready. Honest blockers > forced
   selection.

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
- **No CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 revival or
  tuning.**
- **No use of CAMPAIGN_011 as a trading candidate.** CAMPAIGN_011
  is a null-model anchor only; it cannot become an approved
  strategy under any circumstance.
- **No new external dependency.**
- **No use of CAMPAIGN_010 / CAMPAIGN_011 metric outputs to
  motivate parameter selection for any new candidate.** (Even
  the legitimate use of these as "rejected historical evidence"
  / "null-model baseline" stops at "this family does not work" /
  "candidates must beat this floor"; it cannot become "try this
  knob.")

## 6. Sprint phases

| phase | scope | deliverable(s) |
|---|---|---|
| 0 (this doc) | Repo truth + sprint plan | [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md) |
| 1 | Null-baseline interpretation: codify CAMPAIGN_011 as the comparison floor; define "meaningful improvement over null" | [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) |
| 2 | Reassess C2 / C3 / C4 against the now-6 rejected baseline + the CAMPAIGN_011 null anchor | [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md) |
| 3 | C3 feasibility deep dive: D1AGG-based regime feature, no-lookahead invariants, implementation pattern | [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md) |
| 4 | Select exactly one next real candidate (or infrastructure prerequisite) with id / version / `CAMPAIGN_012` label | [`NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md) |
| 5 | Implementation + evaluation design for the selected candidate | [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md) |
| 6 | Future-branch prompt specs (scaffold + evidence) | [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md) + [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md) |
| 7 | Optional docs/schema helper decision | [`NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md) |
| 8 | Sprint summary + EVIDENCE_INDEX + STRATEGY_STATUS updates + final validation | [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md) + updates |

Commits at the end of each phase.

## 7. Validation plan

After every phase commit:

- `python -m pytest -q` (≥ 771 — unchanged unless Phase 7 adds tests)
- `ruff check src tests scripts research` — must not introduce
  any new finding beyond the 11 pre-existing UP042
- `python scripts/validate_research_archive.py`
- `python scripts/check_research_freeze.py`
- `python scripts/scan_artifacts_for_secrets.py`

Loops + CLI surface checks repeated at Phase 8.

## 8. Explicit no-approval statements

1. **This sprint cannot approve any strategy.** It is design-only.
2. **Selecting a "next real candidate" is not an approval.** The
   selection only fixes which family the future scaffold sprint
   targets; the candidate must then accumulate the full
   six-evidence ladder before any approval can be considered.
3. **The future scaffold sprint cannot approve either.** It can
   implement the candidate, add unit tests, and pass a non-evidence
   smoke; it cannot run paper / demo / live.
4. **The future evidence sprint cannot approve either.** Even a
   clean PASS produces *research evidence*; approval requires a
   separate, reviewed human action per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 9. Explicit "CAMPAIGN_010 / CAMPAIGN_011 must not be tuned or revived" statement

- **CAMPAIGN_010** (`session_breakout 0.1.0-c010`) is REJECTED.
  Re-attempting the session-breakout family by tweaking
  parameters / windows / pair selection is the canonical
  curve-fitting anti-pattern per
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
  §12 and [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md).
- **CAMPAIGN_011** (`random_entry_anchor 0.1.0-c011`) is REJECTED
  and is a **null model by design** — it cannot become a trading
  candidate under any circumstance. The seed is frozen at
  `master_seed = 20260523`; "seed sweeps" are forbidden.
- Both candidates' verdict metrics may be cited as
  **rejected-historical-evidence** (CAMPAIGN_010) or **null-model
  baseline** (CAMPAIGN_011) — but neither may motivate parameter
  selection for a new candidate.

## 10. Cross-links

- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md)
- [`CAMPAIGN_011_EVIDENCE_SUMMARY.md`](CAMPAIGN_011_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
- [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md)
- [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`D1_AGGREGATION_DESIGN.md`](D1_AGGREGATION_DESIGN.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)

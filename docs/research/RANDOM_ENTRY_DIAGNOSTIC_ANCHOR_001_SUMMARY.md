# Random-Entry Diagnostic Anchor — Sprint 001 Summary

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-001`
`strategy_evidence: false`

End-of-sprint summary and handoff for the **CAMPAIGN_011
scaffold sprint** (`random_entry_anchor 0.1.0-c011` — the C5
diagnostic-anchor null model). **No strategy was approved, no
backtest was run, no broker call was made.** The strategy
module + config + 36 unit tests + research config + pre-commit +
status + smoke + 3 readiness docs are committed and ready for
the future evidence sprint.

> **CAMPAIGN_011 is a null model by design — cannot be approved
> under any circumstance.** CAMPAIGN_002 remains REJECT.
> CAMPAIGN_010 remains REJECT. `configs/approved_strategies.yaml`
> remains `approved: []`. Paper / demo / live remain blocked.

## 1. What this sprint did

Eight phases committed in eight commits. Each phase committed
its own artifact(s) before the next began.

| phase | commit | deliverable(s) | LOC |
|---|---|---|---:|
| 0 | `bd6b3eb` | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md) | 322 |
| 1 | `2698ca9` | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md) | 473 |
| 2 | `aef0a9c` | strategy module + config sub-model + slot + re-export | 248 (code) |
| 3 | `04d7f2d` | [`tests/unit/test_random_entry_anchor.py`](../../tests/unit/test_random_entry_anchor.py) — 36 unit + structural-audit cases | 692 |
| 4 | `3ddfb10` | research config + pre-commit + status + readiness | 846 |
| 5 | `ec18636` | [`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md) | 237 |
| 6 | `bf6db73` | walk-forward + financing/risk + verifier readiness | 589 |
| 7 | (this commit) | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md) + [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) update + [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) annotation | — |

**Totals: 11 new markdown docs + 3 new code files + 2 edited
code files + 2 edited docs ≈ 3,400 lines of docs + ~940 lines
of code (strategy + config + tests).**

## 2. What did not change

- `configs/approved_strategies.yaml` remains `approved: []`.
- CAMPAIGN_002 verdict, status, manifest entry — untouched.
- CAMPAIGN_010 verdict, status, manifest entry — untouched.
- `src/forex_bot/backtesting/engine.py` — untouched.
- `src/forex_bot/risk/policy.py` — untouched.
- `src/forex_bot/financing.py` — untouched.
- `src/forex_bot/broker/`, `src/forex_bot/execution/`,
  `src/forex_bot/loops.py`, `src/forex_bot/cli.py` —
  all untouched.
- `research/walk_forward/`, `research/financing/`,
  `research/parity_verifier/`, `research/lean_parity/` —
  all untouched.
- `configs/paper.yaml`, `configs/practice.yaml`,
  `configs/live.example.yaml` — all untouched.
- Existing campaign reports + diagnostic artifacts —
  untouched.

## 3. Implementation status

| component | status |
|---|---|
| Strategy module | committed: [`src/forex_bot/strategies/random_entry_anchor.py`](../../src/forex_bot/strategies/random_entry_anchor.py) (~190 LOC) |
| Strategy re-export | committed: [`src/forex_bot/strategies/__init__.py`](../../src/forex_bot/strategies/__init__.py) |
| StrategyConfig sub-model + slot | committed: [`src/forex_bot/config.py`](../../src/forex_bot/config.py) (`RandomEntryAnchorStrategyConfig` + `StrategyConfig.random_entry_anchor` + `_check_enabled` slot) |
| Implementation spec | committed: [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md) |

## 4. Config status

| component | status |
|---|---|
| Research config | committed: [`configs/campaign_011_random_entry_anchor.yaml`](../../configs/campaign_011_random_entry_anchor.yaml) — 7-pair H4 universe, frozen parameters match spec verbatim, all `trading_enabled` / `allow_order_submission` / `allow_live_trading` = `false` |
| Approved-strategy registry | unchanged: [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml) reads `approved: []` |
| Paper config | unchanged: [`configs/paper.yaml`](../../configs/paper.yaml) does NOT enable random_entry_anchor (verified by Phase 3 unit test) |
| Demo config | unchanged: [`configs/practice.yaml`](../../configs/practice.yaml) does NOT enable random_entry_anchor (verified by Phase 3 unit test) |

## 5. Test status

| metric | value |
|---|---|
| New test file | [`tests/unit/test_random_entry_anchor.py`](../../tests/unit/test_random_entry_anchor.py) — 36 cases |
| Test groups | config (9) + determinism-seed (5) + determinism-content (2) + distribution (2) + strategy core (7) + structural audit (3) + rejected-family contamination (2) + approval regression (5) + config-mutation (1) |
| Phase 3 new-tests result | **36 passed** in 0.09s |
| Full repo regression result (sprint tip) | **771 passed** (735 prior + 36 new) |
| Ruff status | **11 pre-existing UP042** in untouched files (matches baseline); no new findings from the added code |

## 6. Smoke status

| smoke | result | is evidence? |
|---|---|---|
| Config-load | **PASS** (all 9 frozen parameters at expected values) | **no** |
| Unit-test suite | **PASS** (36/36) | **no** |
| Walk-forward dry-run plan (to `/tmp`) | **PASS** (8 folds emitted; rolling/frozen; matches CAMPAIGN_010 structure exactly) | **no** |
| Fixture deterministic signal-generation | covered by `test_signal_emitted_with_expected_fields` + `test_signal_id_is_deterministic` (Phase 3) | **no** |

The smokes confirm scaffold load + deterministic behavior; they
**do not** produce a walk-forward verdict or evidence-grade
result. See
[`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md)
§4 for the full "no, this is not evidence" framing.

## 7. Walk-forward readiness

Per [`CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md):

| dimension | status |
|---|---|
| Harness plug-in (plan generation + `validate_plan`) | **READY** |
| Strategy protocol conformance | **READY** |
| `parameter_mode = frozen` compatibility | **READY** |
| Deterministic-seed reproducibility | **READY** |
| Inherited gate-vector from CAMPAIGN_010 | **READY** |
| Per-fold backtest invocation | **NOT EXECUTED** — future evidence sprint's task (new `scripts/run_campaign_011.py` cloning `scripts/run_campaign_010.py`) |

Expected outcome under random entry: **REJECT** with
fold_pass_rate = 0/8 and aggregate expectancy R near
CAMPAIGN_005's −0.095 R random baseline. The REJECT is the
**success outcome of the evidence sprint** — falsifiability
anchor established.

## 8. Financing/risk readiness

Per [`CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md):

| dimension | status |
|---|---|
| `research.financing.calculate_run` callable | **READY** |
| `default_stress_rate_source()` (ESTIMATED + conservative stress) | **READY** |
| `MODELED` refused at four layers | **PRESERVED** |
| `PositionInterval` adapter pattern | **READY** (same as CAMPAIGN_010's) |
| `RiskEngine(mode='backtest')` integration | **READY** |
| Financing-overlay invocation | **NOT EXECUTED** — future evidence sprint's task |
| Risk-diagnostics invocation | **NOT EXECUTED** — future evidence sprint's task |

Expected: cashflow_home_stress_total ~−$30 to −$60 USD;
~1500–2400 rollover events; vacuously PASSES the
`conservative_stress_run_does_not_flip_verdict` gate.

## 9. Independent-verifier readiness

Per [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md):

| dimension | status |
|---|---|
| Verifier capability today | **CAMPAIGN_002 trend_following only** |
| Required for CAMPAIGN_011 evidence-sprint REJECT? | **no** — item 5 of six-evidence ladder is a paper-promotion gate; null model cannot be paper-promoted |
| Recommended as follow-up? | **yes** — uniquely valuable because deterministic seed → exact-equivalence corroboration |
| Recommended follow-up branch | `infra-free-local-parity-verifier-random-entry-001` |
| Blocking this scaffold sprint? | **no** |
| Blocking the future evidence sprint? | **no** |

## 10. Null-model restrictions (binding)

| restriction | enforcement |
|---|---|
| Cannot be approved | `configs/approved_strategies.yaml` remains `approved: []`; Phase 3 unit test asserts random_entry_anchor is NOT in any approved list |
| Cannot enable paper-loop / demo-loop | paper/demo configs do NOT enable random_entry_anchor (Phase 3 unit tests verify); `app.trading_enabled=false`, `allow_order_submission=false`, `allow_live_trading=false` in the research config |
| No seed optimization | `master_seed = 20260523` fixed in pre-commit before any code |
| No parameter tuning | every frozen parameter fixed before any code; runner-side assertion will reject any drift in the future evidence sprint |
| No "improvement" loops | strategy is deliberately as simple as possible |
| Unexpected PASS → investigation, never promotion | playbook documented in CAMPAIGN_011_PRECOMMIT_CHECKLIST §12 |

## 11. Safety state (unchanged across all 8 phases)

| dimension | status |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | scaffold-only (no verdict; structurally cannot be approved) |
| approved strategies | none |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| broker / OANDA call this sprint | none |
| `.env` read this sprint | none |
| credentials printed this sprint | none |
| account / order / trade / position / transaction endpoint queried | none |
| engine-PnL change this sprint | none |
| `src/forex_bot/financing.py` change this sprint | none |
| new external dependency this sprint | none |
| `MODELED` financing reachable | no (4 refusal layers) |
| live-promotion financing blocker | stands (structurally moot for null model) |
| pytest baseline | **771 passes** (735 prior + 36 new) |
| `git status --short` | clean (at every commit boundary; verified at sprint tip after this Phase 7 commit) |

## 12. Validations run (Phase 7 final)

| command | result |
|---|---|
| `python -m pytest -q` | **771 passed** |
| `ruff check src tests scripts research` | 11 pre-existing UP042 in untouched files (unchanged from baseline) |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refused |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refused |
| `python -m forex_bot.cli --help` | no `live-loop` command present |
| `git status --short` | clean |

## 13. Remaining blockers

| blocker | affects | next step |
|---|---|---|
| **No `scripts/run_campaign_011.py`** | the future evidence sprint cannot iterate per-fold backtests without it | clone `scripts/run_campaign_010.py`; swap `EXPECTED_STRATEGY`, `EXPECTED_VERSION`, `FROZEN_PARAMETERS`, and the strategy import — this is the future evidence sprint's Phase 3 task |
| **No `scripts/build_campaign_011_financing_overlay.py`** | future evidence sprint Phase 5 | clone `scripts/build_campaign_010_financing_overlay.py` |
| **No `scripts/build_campaign_011_risk_diagnostics.py`** | future evidence sprint Phase 6 | clone `scripts/build_campaign_010_risk_diagnostics.py` |
| **Independent verifier capability-locked to CAMPAIGN_002** | item 5 of six-evidence ladder is not satisfied | not blocking for null model (cannot be paper-promoted); optional follow-up: `infra-free-local-parity-verifier-random-entry-001` |
| **11 pre-existing UP042 ruff findings** | code-quality only | `infra-ruff-up042-stress-enum-001` cleanup sprint |

None of these block the future evidence sprint — they are tasks
*within* it.

## 14. Recommended next branch

**`research-random-entry-diagnostic-anchor-walk-forward-001`** —
the future evidence sprint per
[`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md).
9 phases mirroring CAMPAIGN_010's evidence sprint exactly. Full
walk-forward + financing overlay + risk diagnostics + verifier
status. Expected verdict: **REJECT**. Unexpected PASS triggers
the investigation playbook (never promotion).

Subsequent ordering (recommended):

1. `research-random-entry-diagnostic-anchor-walk-forward-001` —
   evidence (next)
2. (Optional) `infra-free-local-parity-verifier-random-entry-001` —
   verifier coverage
3. `research-new-candidate-strategy-discovery-003` — pick the
   next *real* candidate (likely C3 — regime switcher)
4. (Eventual) `research-financing-modeled-capture-credentialed-001` —
   unblock MODELED for C2
5. (Eventual) `infra-engine-paired-entry-support-001` — unblock
   C4

## 15. Exact files to review first

1. [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md)
   — this doc (sprint summary).
2. [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
   — frozen parameters + gates the future evidence sprint inherits verbatim.
3. [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md)
   — binding R1–R8 spec with no-lookahead invariants.
4. [`src/forex_bot/strategies/random_entry_anchor.py`](../../src/forex_bot/strategies/random_entry_anchor.py)
   — strategy module (~190 LOC).
5. [`tests/unit/test_random_entry_anchor.py`](../../tests/unit/test_random_entry_anchor.py)
   — 36 unit + structural-audit tests.
6. [`configs/campaign_011_random_entry_anchor.yaml`](../../configs/campaign_011_random_entry_anchor.yaml)
   — research candidate config.
7. [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
   — candidate-scaffold-only status.
8. [`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md)
   — non-evidence smoke result.
9. [`CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md)
10. [`CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md)
11. [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md)
12. [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
    — the binding prompt spec for the future evidence sprint.

For the standing safety state:

- [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`docs/research/STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

## 16. EVIDENCE_MANIFEST.json

The manifest tracks **campaigns with concrete artifacts**. This
scaffold sprint adds no campaign artifact folder (no per-fold
backtest output exists), so `EVIDENCE_MANIFEST.json` requires
no edit in this sprint. The same posture was taken by the prior
CAMPAIGN_010 scaffold sprint — it deferred its manifest entry
to the evidence sprint. The future CAMPAIGN_011 evidence sprint
will add the manifest entry once `WalkForwardResults` is
committed.

The [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) is updated in this
commit to add a sub-section pointing at the 11 new
discovery-and-scaffold docs.

A small annotation is added to
[`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) recording that
CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` has been
**scaffolded** but has **no scaffold verdict and no evidence
yet** — the row will populate after the future evidence sprint.

## 17. Cross-links

- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md)
- [`CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md)
- [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md)
  (the prompt spec this sprint followed)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
  (the next sprint after this scaffold sprint)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  (the gate vector CAMPAIGN_011 inherits)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)

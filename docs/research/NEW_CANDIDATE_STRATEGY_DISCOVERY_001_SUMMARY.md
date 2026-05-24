# New Candidate Strategy Discovery — Sprint 001 Summary

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-001`
`strategy_evidence: false`

End-of-sprint summary and handoff for the docs-only discovery
sprint that produced the protocol, framework inventory,
candidate shortlist, preferred-candidate evaluation design, and
helper-scaffolding decision note. **No strategy was
implemented, no campaign was run, no broker call was made, no
code was added, and no approval was granted.** The 702-test
baseline is preserved.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. The preferred candidate (C1 —
> Asian-range / London-open session breakout) is designed for a
> *separate, future, human-authorized* sprint named
> `research-asian-london-session-breakout-001`.

## 1. What this sprint did

Six markdown documents committed in six numbered phases (Phase
0–B6). Each phase committed its own artifact before the next
began.

| phase | commit | deliverable | LOC |
|---|---|---|---:|
| 0 | `03fe783` | [`NEXT_BRANCH_DECISION_AUDIT.md`](NEXT_BRANCH_DECISION_AUDIT.md) | 264 |
| B1 | `5683734` | [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md) + [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md) | 661 |
| B2 | `fe18314` | [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md) | 464 |
| B3 | `da6ae24` | [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md) | 534 |
| B4 | `908793c` | [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md) | 536 |
| B5 | `8828e7e` | [`NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md) | 84 |
| B6 | (this commit) | [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md) + [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) update | — |

**Total: 7 markdown docs (≈ 2,500 lines of documentation), 0
Python files, 0 test changes, 0 fixture changes, 0 config
changes, 0 new external dependencies.**

## 2. Preferred candidate (recap)

**C1 — Asian-range / London-open session breakout**
(`session_breakout 0.1.0-c010`, campaign label CAMPAIGN_010).

Distinctness score: 5–6 of 6 against every prior rejected
family (`trend_following`, `volatility_breakout`,
`pullback_continuation`, `mean_reversion`). Detailed scoring,
parameters, fold plan, and gates are in Phase B3 / Phase B4.

The future implementation branch name is **fixed**:
**`research-asian-london-session-breakout-001`**.

C2 (carry-aware long-only overlay) is the runner-up, parked
until either (a) a credentialed practice / live capture sprint
produces ≥ 60 reconciled `DAILY_FINANCING` events and MODELED
financing becomes available, or (b) human approval re-scopes
MODELED for a stress-only carry experiment.

## 3. Final validation (Phase B6)

All commands run from the project venv against this worktree.

| command | result |
|---|---|
| `python -m pytest -q` | **702 passed in 2.96s** (matches Phase 0; baseline preserved) |
| `python scripts/validate_research_archive.py` | **PASS** (9 campaigns, 14 diagnostic artifacts, 127 evidence-index links, 1995 artifact files — 7 more than Phase 0 due to the 7 new docs) |
| `python scripts/check_research_freeze.py` | **PASS** (loops refuse `['trend_following']`; registry empty) |
| `python scripts/scan_artifacts_for_secrets.py` | **PASS** (value scan skipped — no `.env`; pattern scan over 2053 files clean) |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | **refused** (expected; `trend_following` not approved) |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | **refused** (expected; `trend_following` not approved) |
| `python -m forex_bot.cli --help` | no `live-loop` (commands: `doctor`, `sync-instruments`, `fetch-candles`, `backtest`, `audit-data`, `paper-loop`, `demo-loop`, `reconcile`, `report`) |
| `git status --short` | clean (Phase B6 commit pending) |

### 3.1 Ruff result (honest disclosure)

`ruff check src tests scripts research/parity_verifier research/walk_forward research/financing`
reports **8 pre-existing UP042 errors** in three files:

- [`research/walk_forward/models.py`](../../research/walk_forward/models.py)
  (`class ParameterMode(str, Enum)` etc.)
- [`research/financing/models.py`](../../research/financing/models.py)
  (`class FinancingTreatment(str, Enum)`,
  `class MissingRatePolicy(str, Enum)`)
- [`research/parity_verifier/models.py`](../../research/parity_verifier/models.py)
  (3 enums)

(Broader scope `ruff check src tests scripts research` adds 3
more errors in `research/lean_parity/algorithms/...` — also
pre-existing.)

**These errors are not introduced by this sprint.** This sprint
added zero Python code. The errors are the result of a
post-prior-sprint ruff upgrade (UP042 — `str + Enum` should be
`enum.StrEnum`) finding a class of issues that the prior
sprints' ruff version did not flag. The financing /
walk-forward / parity-verifier modules in question were
previously reported "ruff clean" in their respective status
docs.

**Decision:** the discovery sprint does **not** refactor these
files. Reasons:

- The fix changes `str(EnumValue)` runtime semantics (`StrEnum`
  emits `"value"` while `str + Enum` emits `"ClassName.NAME"`).
  Several test assertions key on the exact string form; a blind
  refactor risks breaking them.
- Refactoring unrelated code violates the standing safety rules
  ("Don't add features, refactor, or introduce abstractions
  beyond what the task requires").
- The discovery sprint is docs-only by charter.

**Action:** a separate cleanup sprint (suggested name
`infra-ruff-up042-stress-enum-001`) should: (a) audit every
`str(EnumValue)` call-site, (b) decide between explicit `.value`
access vs `StrEnum` migration, and (c) update affected tests
deterministically. None of that is in scope for the discovery
sprint.

The financing / walk-forward / parity-verifier behaviour is
unchanged. The test suite continues to pass.

## 4. Was any broker / OANDA data fetched?

**No.**

- Made zero OANDA calls.
- Issued zero transaction-stream queries.
- Submitted zero orders.
- Read zero credentials from `.env`.
- Did not enable any new endpoint surface.

The sprint touched only documentation files under
`docs/research/`.

## 5. Was any credential read or printed?

**No.** No `.env` opened. No `os.environ.get('OANDA_*')`
anywhere in the diff. No credential value printed.

## 6. Did engine PnL change?

**No.**
[`src/forex_bot/backtesting/engine.py`](../../src/forex_bot/backtesting/engine.py)
is untouched. So is
[`src/forex_bot/financing.py`](../../src/forex_bot/financing.py).
So is every file under
[`src/forex_bot/backtesting/`](../../src/forex_bot/backtesting/),
[`src/forex_bot/risk/`](../../src/forex_bot/risk/),
[`src/forex_bot/strategies/`](../../src/forex_bot/strategies/),
[`src/forex_bot/data/`](../../src/forex_bot/data/),
[`src/forex_bot/broker/`](../../src/forex_bot/broker/),
[`src/forex_bot/config.py`](../../src/forex_bot/config.py),
[`src/forex_bot/loops.py`](../../src/forex_bot/loops.py),
[`src/forex_bot/approval.py`](../../src/forex_bot/approval.py),
[`src/forex_bot/research_archive.py`](../../src/forex_bot/research_archive.py),
[`src/forex_bot/lean/`](../../src/forex_bot/lean/), and
[`src/forex_bot/cli.py`](../../src/forex_bot/cli.py).

## 7. Financing status

**ESTIMATED / STRESS-only** (unchanged from prior sprints).

- `TableRateSource` defaults to `ESTIMATED`; refuses `MODELED`
  at construction.
- `ConservativeStressRateSource` is the default for any
  research path; `default_stress_rate_source()` returns it.
- `calculate_run` refuses any source that self-reports
  `MODELED`.
- The reconciliation CLI's `_build_report` raises if asked to
  emit `MODELED`.
- The capture script never declares a `financing_treatment`.

**`MODELED` financing remains unavailable / refused.** No
source under `research/financing/` produces it. The future
candidate's first walk-forward run will operate against the
conservative-stress overlay (or a future per-pair multi-year
`TableRateSource(ESTIMATED)` if a separate fixture-expansion
sprint commits one).

## 8. Is the live blocker lifted?

**No.**
[`financing_treatment_blocks_approval`](../../src/forex_bot/financing.py)
in `src/forex_bot/financing.py` is unchanged. `live`
unconditionally requires `MODELED`; no source produces it. The
live-promotion financing blocker stands. Paper / demo are also
blocked by the empty approved-strategy registry.

## 9. Did CAMPAIGN_002's verdict change?

**No.** CAMPAIGN_002 remains **REJECT**. No edit to
`backtests/CAMPAIGN_002_*` or `docs/research/CAMPAIGN_002_*`
was made in this sprint.

## 10. Did any strategy get approved?

**No.**
[`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
remains `approved: []`. The discovery sprint added no name; the
freeze checker reconfirms this in Phase B6.

## 11. Were paper / demo / live changed?

**No.**

- `paper-loop` refuses (Phase B6 re-runs the refusal).
- `demo-loop` refuses (Phase B6 re-runs the refusal).
- No `live-loop` command exists or was added.

## 12. Was QuantConnect / LEAN used?

**No.** Retirement (decision 2026-05-22) stands; no `lean`
command was issued; no LEAN code path was touched.

## 13. Local files created but not committed

**None.** Every artifact of this sprint is committed under
`docs/research/`. The Phase B6 commit completes the cycle.

## 14. Research freeze / archive status

| dimension | status |
|---|---|
| approved-strategy registry | **`approved: []`** (verified by `check_research_freeze.py`) |
| CAMPAIGN_002 verdict | **REJECT** (unchanged) |
| paper / demo / live | **blocked** |
| evidence-index links | **127 / 127** resolve (validator PASS) |
| diagnostic artifacts | **14 / 14** present; none claim `strategy_evidence: true` |
| committed artifact secret scan | clean over 2053 files |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |

## 15. Remaining blockers (for any future scaffold sprint, not this one)

The future
`research-asian-london-session-breakout-001` sprint is **not
blocked** to start. Its known constraints (per Phase B4 §19
pre-flight checklist):

- Must add `StrategyConfig.session_breakout` slot in
  [`config.py`](../../src/forex_bot/config.py).
- Must add `src/forex_bot/strategies/session_breakout.py`
  implementing the `Strategy` protocol.
- Must add `tests/unit/test_session_breakout.py` with the
  no-lookahead / signal-shape / in-position-blocking / NaN
  guards documented in Phase B4 §12.
- Must commit a
  `docs/research/CAMPAIGN_010_SESSION_BREAKOUT_PRECOMMIT.md`
  citing Phase B4 §3 and §8–§15 verbatim.
- Must use `parameter_mode = "frozen"` (only authorized mode).
- Must report financing overlay (`ESTIMATED` via
  `default_stress_rate_source()` for v1 unless a per-pair
  multi-year fixture is committed first).
- Must produce risk-engine diagnostic checklist.
- Must satisfy the six-evidence ladder per
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §8 before any paper promotion request.

Soft blockers that affect *any* future candidate (not specific
to C1):

- **MODELED financing remains refused at four layers.** A
  candidate cannot be live-promoted until a separate
  credentialed-pilot sprint produces real reconciled
  `DAILY_FINANCING` events and human approval flips the MODELED
  slot in
  [`src/forex_bot/financing.py`](../../src/forex_bot/financing.py).
- **The free / local parity verifier currently corroborates
  trend-following.** Extending coverage to a new family is a
  separate future sprint.
- **Pre-existing UP042 ruff hints** in
  `research/{walk_forward,financing,parity_verifier}/models.py`
  should be addressed by a separate cleanup sprint; they do
  not affect runtime behaviour or test results.

## 16. Recommended next branch

**`research-asian-london-session-breakout-001`** — the future
scaffold sprint for the preferred candidate, per Phase B4 §18.
This is the only branch the discovery sprint authorises as the
direct successor.

Alternative branches (if the human reviewer wants to address a
soft blocker first):

- `infra-ruff-up042-stress-enum-001` — clean up the 8
  pre-existing UP042 errors before adding new code.
- `research-financing-multi-year-fixture-expansion-001` —
  extend the per-pair `TableRateSource` fixtures from 2 weeks
  to the full 2020–2026 universe so the candidate's per-pair
  overlay can use real synthetic rates rather than the flat
  conservative-stress source.
- `research-financing-modeled-capture-credentialed-001` —
  separately-authorized credentialed practice or live capture
  sprint to collect real `DAILY_FINANCING` events; required
  before MODELED can become available; required before any
  candidate can be live-promoted.

None of those is initiated by this discovery sprint.

## 17. Exact files to review first

For the next reviewer / future-sprint operator:

1. [`NEXT_BRANCH_DECISION_AUDIT.md`](NEXT_BRANCH_DECISION_AUDIT.md)
   — the Phase 0 audit that records the safety state and the
   PATH B decision.
2. [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
   — the binding protocol every future candidate must follow.
3. [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
   — the design the future scaffold sprint will implement
   verbatim.
4. [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
   — the rationale for selecting C1 over C2 / C3 / C4 / C5.
5. [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
   — the read-only inventory of what already exists.
6. [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md)
   — sprint plan for context.
7. [`NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md)
   — why no helper code was added.
8. (this doc) — the sprint summary.

For the standing safety state:

- [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)

## 18. EVIDENCE_MANIFEST.json

The manifest tracks **campaigns**. This sprint adds no
campaign, so
[`docs/research/EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json)
requires no entry. Same posture as the walk-forward harness
sprint and all five financing sprints. The archive validator
continues to PASS.

The
[`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) is updated in this
commit to add a sub-section pointing at the seven discovery
docs.

## 19. Safety state (unchanged from Phase 0)

| dimension | status |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 | **REJECT** |
| approved strategies | none |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| broker / OANDA call this sprint | none |
| `.env` read this sprint | none |
| credentials printed this sprint | none |
| engine-PnL change this sprint | none |
| `src/forex_bot/financing.py` change this sprint | none |
| new external dependency this sprint | none |
| `MODELED` financing reachable | no (four refusal layers) |
| live-promotion financing blocker | stands |
| pytest baseline (702) | preserved |

## 20. Cross-links

- Sprint plan:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md)
- Protocol:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- Inventory:
  [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
- Shortlist:
  [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
- Preferred candidate eval design:
  [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- Helper-scaffolding decision note:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md)
- Phase 0 audit:
  [`NEXT_BRANCH_DECISION_AUDIT.md`](NEXT_BRANCH_DECISION_AUDIT.md)
- Walk-forward protocol:
  [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- Walk-forward status:
  [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- Financing protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Financing status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Bp/day fixture status:
  [`FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md)
- Observed-capture pilot status:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)
- Six-evidence ladder:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- Strategy approval process:
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Strategy status registry:
  [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- Research freeze decision:
  [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- Future research backlog:
  [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)

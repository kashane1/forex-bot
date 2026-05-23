# Helper Scaffolding — Decision Note (Phase B5)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-001`
`strategy_evidence: false`

Phase B5 of the discovery sprint per
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md)
§4 allows optional safe helper scaffolding. **This phase
deliberately ships no code.** This note records the reasoning so
the next reader does not relitigate the same decision.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. This phase neither tests nor
> approves any strategy; it documents the explicit choice not to
> add code.

## 1. Options considered

| option | what it would add | shipped? | reason |
|---|---|:--:|---|
| Campaign pre-commit doc template | `docs/research/_TEMPLATE_CAMPAIGN_PRECOMMIT.md` mirroring [`CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md`](CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md)'s shape with discipline reminders | no | The existing six committed pre-commit docs (CAMPAIGN_004 → CAMPAIGN_009) already serve as authoritative templates by example. A separate template doc would create a *seventh* source-of-truth that could drift from the patterns the campaigns themselves enforce. The protocol §13 already lists every required section (hypothesis, frozen params, splits/costs/financing, test-window discipline, pre-committed gates). |
| Candidate-proposal-doc JSON / YAML schema + validator + tests | `research/discovery/proposal_schema.py` + `tests/research/test_proposal_schema.py` | no | The shortlist [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md) is a one-off; a schema for "one document about five candidates" is over-engineering. If a future sprint runs *multiple* discovery cycles in parallel, a schema may earn its keep then. Not now. |
| Walk-forward dry-run script for the C1 universe | a thin wrapper around [`scripts/run_walk_forward_dry_run.py`](../../scripts/run_walk_forward_dry_run.py) with C1's parameters baked in | no | The dry-run script already accepts all the parameters via CLI flags ([`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md) §1). The future scaffold sprint will commit its own `CAMPAIGN_010` invocation in its first or second commit. Pre-running it here would either (a) duplicate work the scaffold sprint will redo or (b) commit a `plan.json` for a candidate that does not yet have a strategy module, which would be misleading. |
| Test-helper module for the protocol's §12 overfitting-pattern audit | `research/discovery/overfitting_audit.py` + tests | no | The audit is a human-readable checklist (the shortlist applies it line-by-line in §10). Automating it would (a) require a parsed representation of a proposal doc the project does not have and (b) tempt future readers to trust the green-check without re-thinking each pattern. The audit is *correctly* a manual exercise. |
| `STRATEGY_APPROVAL_PROCESS.md` cross-reference link audit script | `scripts/audit_strategy_approval_links.py` | no | The existing `scripts/validate_research_archive.py` already checks all 127 repo-relative evidence-index links resolve. A second audit covering only `STRATEGY_APPROVAL_PROCESS.md` would duplicate that surface. |

## 2. What the sprint *did* deliver

Each of these has its own commit:

- **Phase 0** — [`NEXT_BRANCH_DECISION_AUDIT.md`](NEXT_BRANCH_DECISION_AUDIT.md)
- **Phase B1** — [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md) and [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- **Phase B2** — [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
- **Phase B3** — [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
- **Phase B4** — [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- **Phase B5** — this note
- **Phase B6** — [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md) (next commit)

Total Phase B output: six markdown docs, zero code, zero test
changes, zero new external dependency. **702-test baseline
preserved.**

## 3. What the next sprint *will* need to add

The future
`research-asian-london-session-breakout-001` sprint
will add code per
[`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
§16:

- `SessionBreakoutStrategyConfig` + `StrategyConfig.session_breakout`
  slot in [`config.py`](../../src/forex_bot/config.py).
- `src/forex_bot/strategies/session_breakout.py`.
- `tests/unit/test_session_breakout.py`.
- Walk-forward + financing + report artifacts under
  `backtests/CAMPAIGN_010_session_breakout/`.

None of that is in scope for the discovery sprint.

## 4. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.**
- No code edited this phase.
- No campaign run.
- No broker / OANDA call.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.

## 5. Cross-links

- Sprint plan:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md)
- Protocol:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- Phase B4 design:
  [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- Walk-forward dry-run script:
  [`scripts/run_walk_forward_dry_run.py`](../../scripts/run_walk_forward_dry_run.py)

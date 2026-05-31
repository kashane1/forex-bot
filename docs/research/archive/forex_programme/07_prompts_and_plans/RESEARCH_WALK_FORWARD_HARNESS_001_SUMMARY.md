# Research Walk-Forward Harness 001 — Summary

**Date:** 2026-05-22 · **Branch:** `research-walk-forward-harness-001`
**Base commit:** `8730566` (HEAD of `research-close-free-local-verifier-and-next-direction-001`)

Infrastructure sprint. Built a reusable walk-forward fold-
generation library that future strategy campaigns must use before
any candidate can be considered for paper / demo. **No strategy
ran. No campaign was modified. No strategy is approved.
CAMPAIGN_002 remains REJECT. Paper / demo / live remain blocked.**

## 1. Branch name

`research-walk-forward-harness-001`.

## 2. Commit hashes by phase

| phase | commit |
|---|---|
| Phase 0 — baseline & sprint plan | `1c7ae7f` |
| Phase 1 — protocol doc | `1a871c9` |
| Phase 2 — harness skeleton + dry-run script | `f5359e8` |
| Phase 3 — tests + fixtures | `5b4858b` |
| Phase 4 — CAMPAIGN_002 metadata-only retrospective | `e892f50` |
| Phase 5 — status & evidence updates | `e4cc884` |
| Phase 6 — final validation & summary | (this commit) |

## 3. Files changed by phase

| phase | files |
|---|---|
| Phase 0 | `docs/research/WALK_FORWARD_HARNESS_001_PLAN.md` (new) |
| Phase 1 | `docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md` (new) |
| Phase 2 | `research/walk_forward/{__init__,models,splits,validate,reporting}.py` (new), `research/walk_forward/README.md` (new), `scripts/run_walk_forward_dry_run.py` (new), `docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md` (dogfooding-driven rule fix: §6 rule #3) |
| Phase 3 | `tests/research/test_walk_forward_models.py` (new, 19 tests), `tests/research/test_walk_forward_splits.py` (new, 10 tests), `tests/research/test_walk_forward_validate.py` (new, 13 tests) |
| Phase 4 | `docs/research/CAMPAIGN_002_WALK_FORWARD_RETROSPECTIVE.md` (new) |
| Phase 5 | `docs/research/WALK_FORWARD_HARNESS_STATUS.md` (new), `docs/research/EVIDENCE_INDEX.md`, `docs/research/EVIDENCE_MANIFEST.json` |
| Phase 6 | `docs/research/RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md` (new) |

`src/forex_bot/` — **not modified**. Bespoke engine, strategy
modules, campaign configs, campaign reports,
`configs/approved_strategies.yaml`, `research/parity_verifier/` —
all unchanged.

## 4. Validation commands run

- `python -m pytest -q` → **523 passed** (481 pre-sprint + 42 new).
- `ruff check src tests scripts research/parity_verifier research/walk_forward` → **clean**.
- `python scripts/validate_research_archive.py` → **ALL CHECKS PASSED**
  (14 diagnostic artifacts; 99 evidence-index links resolve; no
  credential-shaped strings in 1,942 committed artifact files).
- `python scripts/check_research_freeze.py` → **ALL CHECKS PASSED**
  (paper-loop + demo-loop both refuse `['trend_following']` —
  frozen).
- `python scripts/scan_artifacts_for_secrets.py` → **PASSED**.
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml` →
  **refused**.
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml` →
  **refused**.
- `python -m forex_bot.cli --help` → no `live-loop` command.

## 5. No strategy is approved

**Confirmed.** `configs/approved_strategies.yaml` remains
`approved: []`. The harness writes nothing to that file and never
will.

## 6. CAMPAIGN_002 remains REJECT

**Confirmed.** The Phase 4 retrospective is metadata-only — it
captures the harness's plan output for CAMPAIGN_002's universe
and annotates each fold's test window with the already-known
REJECT verdict from the existing committed CAMPAIGN_002 evidence.
No backtest re-run. No verdict change.

## 7. Paper / demo / live remain blocked

**Confirmed.** Both `paper-loop` and `demo-loop` refused at final
validation; no `live-loop` command exists.

## 8. Walk-forward protocol summary

The protocol
([`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md))
defines:

- **Three-window structure per fold:** train → validation → test,
  contiguous and non-overlapping. For frozen-parameter
  strategies (the only kind authorized today), train and
  validation are documentation-only.
- **Two split styles:** rolling (fixed-length train slides
  forward by `step_days`) and expanding (train grows by
  `step_days`).
- **Minimum 3 folds** (recommended 6–10 for a 6-year H4
  universe).
- **Four plan-level rules enforced by `validate_plan`:**
  (1) min fold count ≥ 3; (2) forward-only fold ordering with
  `fold_index == list position`; (3) no consecutive test-window
  overlap (applies to both rolling and expanding); (4) all fold
  boundaries inside the universe.
- **Parameter-freeze modes:** `frozen` (required today),
  `per_fold_from_train`, `per_fold_from_validation` (schema
  support for future adaptive candidates; not authorized today).
- **Per-fold metrics** to record: trades, expectancy R, return %,
  PF, drawdown, win rate, bars, gate verdict.
- **Aggregate metrics:** fold pass rate, total trades, aggregate
  expectancy / return / single-fold dominance share.
- **Default rejection criteria:** any fold has non-finite
  metrics; fold pass rate < 100 %; aggregate expectancy < 0;
  single fold dominates > 80 % of aggregate return; any
  pre-commit gate fails any fold.

The protocol also enumerates the six artifacts a campaign must
produce to claim a walk-forward result and notes that walk-forward
PASS is one of six required evidence items before paper / demo
per
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8.

## 9. Harness implementation status

| component | status |
|---|---|
| `research/walk_forward/__init__.py` | done — public re-exports |
| `models.py` | done — 6 Pydantic models with cross-validation; `strategy_evidence: false` rails on plan + results |
| `splits.py` | done — `rolling_window_plan` + `expanding_window_plan`; deterministic; reject zero/negative inputs |
| `validate.py` | done — `validate_plan` enforces 4 plan-level rules with helpful error messages |
| `reporting.py` | done — `render_plan_md` + `render_results_md` |
| `research/walk_forward/README.md` | done — usage + safety |
| `scripts/run_walk_forward_dry_run.py` | done — CLI: generates + validates + writes `plan.json` + `plan.md`; exits 2 on invalid plan; warns on non-`frozen` parameter mode |
| Independence rail | done — grep-enforced test rejects any `forex_bot` import in `research/walk_forward/` |

The harness was dogfooded mid-sprint: the dry-run script caught a
too-strict rule I had originally written in the protocol (rule
#3 forbade fold-N test ↔ fold-(N+1) train overlap, which is
standard in walk-forward; the actual constraint is no consecutive
test-window overlap). Both the protocol and the validator were
fixed before any tests were written, which is exactly what the
dogfood was for.

## 10. Test status

**42 walk-forward tests pass.** Full repo suite: **523 passes**
(481 prior + 42 new).

| file | cases | covers |
|---|---|---|
| `test_walk_forward_models.py` | 19 | Pydantic invariants, enum values, plan/results cross-check, **grep-enforced no-forex_bot import rail** |
| `test_walk_forward_splits.py` | 10 | rolling + expanding generation, determinism, invalid-arg rejection, zero-folds-when-too-short, first-fold-at-universe-start |
| `test_walk_forward_validate.py` | 13 | all 4 plan-level rules; generator output passes validate; JSON round-trip preserves equality; markdown render produces required sections |

## 11. Remaining limitations

- **Harness does not run a backtest.** Per-fold execution is the
  campaign code's responsibility.
- **In-fold leakage is not detectable** by the harness. The
  fold-boundary rules are enforced; in-fold no-lookahead relies
  on the bespoke engine and pre-commit review.
- **Only `frozen` parameter mode is authorized today.** The
  schema supports the two adaptive modes; the dry-run CLI warns
  when one is requested.
- **Date-only fixtures.** The harness reasons in
  `datetime.date`; intraday H4 alignment is the campaign code's
  responsibility (already handled by the bespoke engine).
- **No `step_days < test_days` pre-check.** The validator catches
  this via the no-consecutive-test-overlap rule, but the error
  message could be more helpful at the script layer. Future
  polish.
- **No fold-set diffing.** Re-running with different parameters
  produces a new plan from scratch; no support for "diff two
  plans" yet. Low priority.

## 12. Recommended next branch

Two safe directions, prioritized:

- **A — `research-financing-model-001`** (§5.4 of
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)).
  Required prerequisite before any candidate strategy can be
  promoted to paper. Low overfitting risk (cost model, not
  signal). Substantial scope (~3 sprints). **Highest research
  value next** because the walk-forward harness is now in place
  but financing is the single hardest unconditional blocker for
  any live promotion.
- **B — `research-portfolio-risk-diagnostics-001`** (§5.6).
  Diagnostic-only audit of the RiskEngine's portfolio-level
  rules. ~1 sprint. Zero overfitting risk. Lower urgency than
  financing but useful if A is paused.

Once both A and B are done, the next sensible direction is §5.1
(new strategy family), which would then benefit from the new
walk-forward harness, the financing model, and the portfolio-
risk audit all at once.

## 13. Exact files to review first

1. [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
   — the rules future campaigns must follow.
2. [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
   — headline status, implemented pieces, tests, usage recipe.
3. [`research/walk_forward/README.md`](../../research/walk_forward/README.md)
   — module-level overview.
4. [`CAMPAIGN_002_WALK_FORWARD_RETROSPECTIVE.md`](CAMPAIGN_002_WALK_FORWARD_RETROSPECTIVE.md)
   — concrete plan + report shape on a real (already-rejected)
   campaign.
5. [`WALK_FORWARD_HARNESS_001_PLAN.md`](WALK_FORWARD_HARNESS_001_PLAN.md)
   — the sprint plan.
6. This summary
   ([`RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md`](RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md)).

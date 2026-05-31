# Walk-Forward Research Harness — Status

**Date:** 2026-05-22 · **Branch:** `research-walk-forward-harness-001`
`strategy_evidence: false`

Headline status of the walk-forward research harness after Sprint
001. **The harness is implemented, tested, and ready for use by
future strategy campaigns.** It does not run any strategy by
itself — campaign code consumes the plan and writes the per-fold
results.

> No strategy approved. CAMPAIGN_002 remains REJECT. Paper / demo /
> live remain blocked. The harness is diagnostic infrastructure and
> writes `strategy_evidence: false` on every output it emits.

## 1. Implemented pieces

| component | file | role |
|---|---|---|
| Public API | `research/walk_forward/__init__.py` | re-exports of models, splits, validate, reporting |
| Pydantic models | `research/walk_forward/models.py` | `Fold` (with within-fold ordering invariants), `WalkForwardPlan` (with `strategy_evidence: false` rail), `FoldMetrics`, `AggregateMetrics` (with pass-rate consistency check), `WalkForwardResults` (with plan / metrics / aggregate cross-check) |
| Split generators | `research/walk_forward/splits.py` | `rolling_window_plan` (fixed-length sliding train) and `expanding_window_plan` (growing train); both deterministic, both reject zero/negative window lengths |
| Plan-level validation | `research/walk_forward/validate.py` | `validate_plan(plan)` enforces: (1) min fold count ≥ 3; (2) forward-only fold ordering with `fold_index == list position`; (3) no consecutive test-window overlap (applies to both rolling and expanding); (4) all fold boundaries inside the universe |
| Markdown rendering | `research/walk_forward/reporting.py` | `render_plan_md(plan)` and `render_results_md(results)` — pure formatting, no I/O |
| Dry-run CLI | `scripts/run_walk_forward_dry_run.py` | generates + validates a plan from CLI args; writes `plan.json` + `plan.md` to `--output`; **does not execute any strategy**; emits `WARNING` if `parameter_mode != frozen` (not authorized today) |
| Package README | `research/walk_forward/README.md` | usage + safety notes |

## 2. Tests

| file | cases | role |
|---|---|---|
| `tests/research/test_walk_forward_models.py` | 19 | pin Pydantic invariants (Fold ordering, plan/results `strategy_evidence: false` rails, aggregate pass-rate consistency, plan↔metrics↔aggregate cross-check), enum values, **grep-enforced import-isolation rail** (no file under `research/walk_forward/` may import from `forex_bot`) |
| `tests/research/test_walk_forward_splits.py` | 10 | rolling + expanding generation: window lengths, train-step / train-growth behavior, determinism (same inputs → same dump), invalid-arg rejection, zero-folds-when-universe-too-short, first-fold-starts-at-universe-start |
| `tests/research/test_walk_forward_validate.py` | 13 | all 4 plan-level rules: min fold count; forward-only ordering + `fold_index == list position`; no consecutive test-window overlap (rolling AND expanding); all-boundaries-in-universe; generator-output passes validate; JSON round-trip preserves equality; markdown render produces required sections |

**42 walk-forward tests pass.** Full repo suite: **523 passes**
(481 prior + 42 new).

## 3. Known limitations

- **Harness does not run a backtest.** It emits plans and
  validates them. Per-fold backtests are the campaign code's
  responsibility (campaign reads `WalkForwardPlan`, runs the
  bespoke `BacktestEngine` against each fold's test window, writes
  `WalkForwardResults`).
- **In-fold leakage is not detected.** The harness validates
  fold-boundary leakage rules (no train/val/test overlap, no
  consecutive test-window overlap). A strategy that peeks at
  future bars *within* its own fold will produce nonsense numbers;
  catching that requires pre-commit review and the bespoke
  engine's no-lookahead rails (which it has).
- **Only `frozen` parameter mode is authorized today.** The
  schema supports `per_fold_from_train` and
  `per_fold_from_validation` for future adaptive campaigns, but
  using them today would violate the research freeze. The dry-run
  CLI emits a warning when a non-frozen mode is requested.
- **Date-only fixtures.** The harness reasons in `datetime.date`
  units; intraday H4 bar alignment is the campaign code's
  responsibility (the bespoke engine already does this).
- **No leakage check for `--step-days` smaller than `--test-days`.**
  The validator catches this case via the no-consecutive-test-
  overlap rule, but the dry-run script could surface a more
  helpful error before invoking `validate_plan`. Future
  improvement.
- **No fold-set diffing.** Re-running with different parameters
  produces a new plan from scratch; no support yet for "diff
  two plans". Low priority.

## 4. How future campaigns should use the harness

1. **Pre-commit phase.** The campaign's
   `<CAMPAIGN>_PRECOMMIT.md` records the universe, the frozen
   strategy parameters, the chosen split style + window lengths
   + step, and the pass/fail gates per fold (e.g. "expectancy_r >
   0.05 on each fold's test window").
2. **Generate the plan.** Either invoke
   `scripts/run_walk_forward_dry_run.py` (writes `plan.json` +
   `plan.md`) or call `rolling_window_plan(...)` /
   `expanding_window_plan(...)` programmatically from the
   campaign's code. Commit the plan JSON + plan markdown.
3. **Validate the plan.** Either rely on the dry-run script
   (calls `validate_plan` automatically) or call `validate_plan(plan)`
   explicitly in the campaign code. If validation fails, the
   plan is wrong — fix it before running anything.
4. **Run the strategy per fold.** Iterate over `plan.folds`,
   run the bespoke `BacktestEngine` against each fold's test
   window, emit a `FoldMetrics` per fold. (The harness ships no
   runner; the campaign owns this code.)
5. **Compute the aggregate.** Build an `AggregateMetrics` from
   the per-fold metrics. The model enforces `fold_pass_rate ==
   folds_passing_gates / fold_count`.
6. **Assemble a `WalkForwardResults`.** The model cross-checks
   plan ↔ metrics ↔ aggregate consistency; `overall_verdict`
   must be `PASS` or `REJECT`.
7. **Render the report.** `render_results_md(results)` produces
   a markdown summary the campaign commits as
   `<CAMPAIGN>_WALK_FORWARD_REPORT.md`.
8. **Apply the campaign's rejection criteria.** From
   [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
   §9: fold pass rate < 100 % under strict-pass, aggregate
   expectancy < 0, single-fold dominance > 80 %, etc.

A `WalkForwardResults` with `overall_verdict == "PASS"` is one of
the **six** evidence items required before paper / demo per
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8.

## 5. Safety state

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT.** The Phase 4 retrospective is
  metadata-only.
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` refuse via the empty approved-strategy registry. No
  `live-loop` command exists in the CLI.
- **No broker credentials used.** No OANDA API call. No `.env`
  read.
- **No QuantConnect / LEAN action.** Retirement stands.
- **No orders submitted.**
- **No bespoke-engine edits.** No CAMPAIGN_002 rule edits.
- **No verifier-code edits.** The Sprint 003/004 verifier closure
  stands; this sprint adds an independent harness package.

## 6. Cross-links

- Sprint plan: [`WALK_FORWARD_HARNESS_001_PLAN.md`](WALK_FORWARD_HARNESS_001_PLAN.md)
- Protocol: [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- CAMPAIGN_002 retrospective: [`CAMPAIGN_002_WALK_FORWARD_RETROSPECTIVE.md`](CAMPAIGN_002_WALK_FORWARD_RETROSPECTIVE.md)
- Sprint summary: [`RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md`](RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md) (Phase 6)
- Harness README: [`research/walk_forward/README.md`](../../research/walk_forward/README.md)
- Dry-run script: [`scripts/run_walk_forward_dry_run.py`](../../scripts/run_walk_forward_dry_run.py)
- Next research direction: [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)

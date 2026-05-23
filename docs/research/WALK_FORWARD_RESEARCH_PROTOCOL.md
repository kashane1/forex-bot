# Walk-Forward Research Protocol

**Date:** 2026-05-22 · **Branch:** `research-walk-forward-harness-001`
`strategy_evidence: false`

The walk-forward protocol future strategy campaigns must follow
before any candidate can be considered for paper / demo / live.
This document defines the rules; the harness in
[`research/walk_forward/`](../../research/walk_forward/) enforces
the structural parts (fold-window validity, no overlap, minimum
fold count). The non-structural parts (no-leakage inside a fold,
no-tuning during the test, etc.) are enforced by the campaign's
pre-commit and human review.

> This document does not approve any strategy. CAMPAIGN_002 remains
> REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.

## 1. Purpose

A single-window backtest is necessary but not sufficient evidence
of an edge. A walk-forward result requires the candidate to pass
its pre-committed gates on **multiple** train / validation / test
windows that walk forward in time, without parameter tuning between
folds. The protocol turns "this strategy was positive in one
sealed window" into "this strategy was positive across multiple
sealed windows under a fixed parameter rule".

This is the standard discipline for time-series strategy research;
its purpose here is to raise the bar of what counts as "evidence
of an edge" for any future candidate.

## 2. Non-goals

- **Not approval.** Surviving walk-forward is one of several
  prerequisites for paper-trade approval (see
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §7-§8); a clean walk-forward result on its own does **not**
  approve a strategy.
- **Not optimization.** The harness does not search the parameter
  space. Parameters are frozen by the pre-commit; the harness
  measures.
- **Not a leakage scanner for in-fold code.** A strategy that
  peeks at future bars inside a fold will pass the harness's
  fold-boundary checks but produce nonsense numbers. Pre-commit
  review and the bespoke engine's no-lookahead rails are the
  primary defences.
- **Not a single-window replacement.** Single-window backtests
  remain useful for prototyping; walk-forward is the gate for
  promotion to candidate status.

## 3. Train / validation / test split conventions

Every walk-forward fold defines three contiguous, non-overlapping
date ranges in this order:

```
|----- train -----|--- validation ---|---- test ----|
   t_train_start   v_train_end       v_test_start   t_test_end
                   ↑                  ↑              ↑
                   v_validation_start v_test_start   t_test_end
                   (= v_train_end + 1 bar)
                                      (= v_validation_end + 1 bar)
```

- **Train window**: bars the strategy may use to fit / select
  parameters in a per-fold style. **Forbidden** for any
  pre-committed strategy with frozen parameters — those have no
  fitting step.
- **Validation window**: bars the strategy may use to confirm a
  parameter selection from train. **Forbidden** for frozen-param
  strategies. Used only by adaptive strategies (per-fold
  optimization, regime-classifier training, etc.).
- **Test window**: bars the strategy's pre-committed gates are
  evaluated on. The campaign verdict is `PASS` only if **every
  fold's test window passes its gates** under the strategy's
  pre-committed parameter rule.

For frozen-parameter strategies (the only kind currently
authorized by the research freeze), `train` and `validation` are
documentation-only — they record the bars **excluded** from the
test evaluation per fold; the strategy itself does nothing with
them. The harness still enforces the three-window structure
because it generalizes cleanly to a future adaptive candidate.

## 4. Rolling-window conventions

Two split styles supported:

### 4.1 Rolling-window (default)

Each fold uses a **fixed-length** train window that slides forward
in time. Validation and test windows also have fixed lengths. Fold
*n*'s train window starts after fold *n−1*'s train window by a
fixed step.

```
fold 1:  [train1]      [val1]   [test1]
fold 2:        [train2]      [val2]   [test2]
fold 3:              [train3]      [val3]   [test3]
```

Use when the most recent N bars are the most relevant (regime
shift, structural break expected).

### 4.2 Expanding-window

The train window **grows** each fold; only validation and test
windows slide forward.

```
fold 1: [---- train1 ----]      [val1]   [test1]
fold 2: [-------- train2 --------]    [val2]   [test2]
fold 3: [------------ train3 ------------][val3][test3]
```

Use when more history is always better (no expected regime
breaks).

## 5. Minimum number of folds

Any walk-forward result must contain **at least 3 folds**. Fewer
than 3 is not walk-forward; it's "train + holdout × N" which has
weaker generalization evidence.

The harness rejects a fold plan with `< 3` folds.

Recommended fold count: **6–10** for a 6-year H4 dataset.

## 6. No-leakage rules

The harness enforces:

1. **No train ↔ validation overlap.** `train_end < validation_start`.
2. **No validation ↔ test overlap.** `validation_end < test_start`.
3. **No consecutive test-window overlap.** `fold N+1`'s
   `test_start > fold N`'s `test_end`. Adjacent folds' *train* and
   *validation* windows may overlap (that's standard walk-forward
   — the train slides by `step_days` each fold while spanning many
   `step_days` of history); but their *test* windows must be
   disjoint so aggregate metrics don't double-count trades on
   overlapped bars. Applies to both rolling and expanding modes.
4. **No future-leakage in fold ordering.** Fold *N*'s test_start
   must be strictly after fold *N−1*'s test_start; folds proceed
   forward in time.
5. **All fold boundaries in scope.** Every fold's
   `[train_start, test_end]` lies within the campaign's
   `[universe_start, universe_end]` window.

The harness rejects a plan that violates any of these.

In-fold leakage (the strategy peeks at future bars within its own
fold) is **not** enforceable by the harness — it requires
no-lookahead rails inside the bespoke engine (which they have)
plus pre-commit review.

## 7. Parameter-freeze rules

The harness records, per fold, a **parameter manifest** that pins
exactly which strategy parameters were used. Three valid modes:

- **`frozen`**: the same parameters across all folds, copied from
  the campaign's pre-commit. **Required** under the current
  research freeze. The manifest entry just records the pre-commit
  config hash.
- **`per_fold_from_train`** *(future use, not authorized today)*:
  the strategy fits its own parameters from each fold's train
  window. Manifest records the per-fold parameter set.
- **`per_fold_from_validation`** *(future use, not authorized)*:
  parameters fitted on train, confirmed/discarded on validation.
  Manifest records per-fold parameter sets.

Today only `frozen` is valid. The harness still supports the other
two modes in the schema so a future authorized adaptive campaign
doesn't need a schema change.

## 8. Acceptable metrics (per fold + aggregate)

For each fold's **test window**, record:

- `total_trades`
- `expectancy_r` (mean R-multiple)
- `return_pct` (total test-window return)
- `profit_factor`
- `max_drawdown_pct` (test-window peak-to-trough)
- `win_rate`
- `bars_in_window`
- `signal_rejection_count_by_code` (if RiskEngine is used)

Aggregate across folds:

- per-fold pass/fail under the pre-commit gates
- **fold pass rate** = (# folds passing all gates) / (# folds)
- min / median / max of each per-fold metric
- aggregate return (compounded across test windows) and aggregate
  expectancy_r (trade-weighted)

## 9. Rejection criteria (defaults; campaign pre-commit may add)

A walk-forward result is **REJECT** if any of:

- **Fewer than 3 folds.** Structurally invalid.
- **Any fold has non-finite metrics** (NaN return, divide-by-zero
  in profit factor, etc.) without an explicitly documented cause.
- **Fold pass rate < 100 %** under the strict-pass interpretation
  (every fold must pass). The pre-commit may relax this to "at
  least N of M folds pass", but the default is strict 100 %.
- **Aggregate expectancy_r < 0.** Even if fold pass rate is high,
  a net-losing expectancy across folds is REJECT.
- **Variance across folds masks a single lucky fold.** Defined
  quantitatively as: one fold contributing > 80 % of the
  aggregate return. Indicates path dependence, not edge.
- **Any pre-commit gate fails on any fold's test window.** The
  campaign pre-commit defines its own gates (e.g. expectancy_r >
  0.05 on the test window); those gates are evaluated per fold,
  not aggregated.

A walk-forward result is **PASS** only if **none** of the above
applies AND every pre-commit gate passes on every fold's test
window.

## 10. Required artifacts (per campaign that uses the harness)

For a campaign using this harness to claim a walk-forward result,
it must produce:

| artifact | content |
|---|---|
| `<CAMPAIGN>_PRECOMMIT.md` | hypothesis, frozen parameters (or adaptive parameter rule), universe, window, fold plan reference, pass/fail gates per fold |
| `<CAMPAIGN>_WALK_FORWARD_PLAN.json` | machine-readable fold plan emitted by the harness (universe_start/end, fold list, split style, parameter mode, gate definitions) |
| `<CAMPAIGN>_WALK_FORWARD_PLAN.md` | human-readable rendering of the plan |
| `<CAMPAIGN>_WALK_FORWARD_RESULTS.json` | machine-readable per-fold metrics + aggregate (produced by running the strategy against each fold's test window — that runner is the campaign's responsibility, not the harness's) |
| `<CAMPAIGN>_WALK_FORWARD_REPORT.md` | human-readable per-fold + aggregate report, gate verdict per fold, overall PASS / REJECT |

The harness produces the plan JSON + markdown directly. The
results JSON + report come from the campaign code that consumes
the plan.

## 11. Required evidence before paper / demo

Walk-forward PASS is **necessary but not sufficient**. The full
evidence package per
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8 is also required:

1. Pre-commit doc.
2. Backtest report (single-window).
3. **Walk-forward result (this protocol).**
4. Financing reconciliation (per
   [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) §1).
5. Independent corroboration (exact custom-engine reproduction
   or free / local verifier WARN-band agreement).
6. Human approval record (a reviewed `ApprovalEntry` in
   `configs/approved_strategies.yaml`).

A walk-forward PASS without items 4–6 still keeps the candidate
in research, not paper.

## 12. Explicit statement on approval

Surviving this protocol does **not** approve a strategy. It is
**one** of the gates a future candidate must pass. Approval is a
deliberate human action with a documented `ApprovalEntry` per the
`forex_bot.approval` schema. The harness writes plans and validates
their structure; it does not write to
`configs/approved_strategies.yaml` and never will.

## 13. Cross-links

- Harness: [`research/walk_forward/README.md`](../../research/walk_forward/README.md) (created Phase 2)
- Status: [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md) (created Phase 5)
- Next research direction: [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- Research freeze: [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- Strategy approval process: [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

"""Plan-level validation for walk-forward fold plans.

Per-fold structural validation is enforced by the ``Fold`` model
(contiguous train/validation/test, no within-fold overlap). This
module enforces plan-level rules:

1. Minimum fold count (>= 3) — per
   ``docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md`` §5.
2. Forward-only fold ordering — later folds' test windows start
   strictly after earlier folds'.
3. No consecutive test-window overlap — applies to both rolling
   and expanding modes; aggregate metrics must not double-count
   trades on overlapped test bars.
4. All fold boundaries lie within the campaign's universe window.
"""

from __future__ import annotations

from research.walk_forward.models import WalkForwardPlan

MIN_FOLD_COUNT = 3


class PlanValidationError(ValueError):
    """Raised when a walk-forward plan violates the protocol."""


def validate_plan(plan: WalkForwardPlan) -> None:
    """Raise ``PlanValidationError`` if the plan violates the protocol.

    Does not return a value — successful validation is silent.
    """

    if len(plan.folds) < MIN_FOLD_COUNT:
        raise PlanValidationError(
            f"plan has {len(plan.folds)} folds; protocol requires at least "
            f"{MIN_FOLD_COUNT} (see WALK_FORWARD_RESEARCH_PROTOCOL.md §5)"
        )

    # Forward-only fold ordering (test_start strictly increasing).
    for prev, curr in zip(plan.folds, plan.folds[1:], strict=False):
        if curr.test_start <= prev.test_start:
            raise PlanValidationError(
                f"fold {curr.fold_index} test_start ({curr.test_start}) is "
                f"not strictly after fold {prev.fold_index} test_start "
                f"({prev.test_start}) — folds must proceed forward in time"
            )

    # Fold-index ordering matches list order (sanity).
    for i, fold in enumerate(plan.folds):
        if fold.fold_index != i:
            raise PlanValidationError(
                f"fold at list position {i} has fold_index={fold.fold_index}; "
                f"fold_index must equal list position"
            )

    # Consecutive folds' TEST windows must not overlap.
    #
    # Standard walk-forward: adjacent folds' train windows are expected to
    # overlap (the train window slides by `step_days` each fold while
    # spanning many step-days of history). What must NOT overlap is the
    # test windows themselves — otherwise aggregate metrics would
    # double-count trades on the overlapped bars.
    #
    # This rule applies to both rolling and expanding modes: expanding
    # mode's train always starts at universe_start, so it legitimately
    # covers prior test bars; but its test windows still must not overlap.
    for prev, curr in zip(plan.folds, plan.folds[1:], strict=False):
        if curr.test_start <= prev.test_end:
            raise PlanValidationError(
                f"test-window overlap: fold {curr.fold_index} test_start "
                f"({curr.test_start}) is on or before fold "
                f"{prev.fold_index} test_end ({prev.test_end}). "
                f"Consecutive folds' test windows must be disjoint to "
                f"avoid double-counting trades in aggregate metrics."
            )

    # All boundaries inside the universe.
    for fold in plan.folds:
        if fold.train_start < plan.universe_start:
            raise PlanValidationError(
                f"fold {fold.fold_index} train_start ({fold.train_start}) is "
                f"before universe_start ({plan.universe_start})"
            )
        if fold.test_end > plan.universe_end:
            raise PlanValidationError(
                f"fold {fold.fold_index} test_end ({fold.test_end}) is after "
                f"universe_end ({plan.universe_end})"
            )

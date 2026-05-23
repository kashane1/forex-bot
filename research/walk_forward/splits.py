"""Rolling-window and expanding-window split generation.

The strategy-execution side of the harness consumes a list of
``Fold`` objects produced by these functions. Generation is
deterministic: same inputs always produce the same folds.

All date arithmetic uses ``datetime.date`` and ``timedelta(days=1)``
for boundary nudges. Dates are inclusive at both ends of each
window.
"""

from __future__ import annotations

from datetime import date, timedelta

from research.walk_forward.models import (
    Fold,
    ParameterMode,
    SplitStyle,
    WalkForwardPlan,
)


def _day(dt: date, *, offset_days: int = 0) -> date:
    return dt + timedelta(days=offset_days)


def rolling_window_plan(
    *,
    campaign_name: str,
    universe_start: date,
    universe_end: date,
    train_window_days: int,
    validation_window_days: int,
    test_window_days: int,
    step_days: int,
    parameter_mode: ParameterMode = ParameterMode.FROZEN,
    notes: list[str] | None = None,
) -> WalkForwardPlan:
    """Generate a fixed-length rolling-window walk-forward plan.

    Fold *n*'s train window starts ``step_days`` after fold *n−1*'s
    train window. Validation and test windows have fixed lengths
    and follow contiguously. The function produces every fold whose
    test window fits within ``universe_end``.
    """

    _require_positive(train_window_days=train_window_days)
    _require_positive(validation_window_days=validation_window_days)
    _require_positive(test_window_days=test_window_days)
    _require_positive(step_days=step_days)
    if universe_start > universe_end:
        raise ValueError("universe_start must be <= universe_end")

    folds: list[Fold] = []
    fold_index = 0
    train_start = universe_start
    while True:
        train_end = _day(train_start, offset_days=train_window_days - 1)
        validation_start = _day(train_end, offset_days=1)
        validation_end = _day(
            validation_start, offset_days=validation_window_days - 1
        )
        test_start = _day(validation_end, offset_days=1)
        test_end = _day(test_start, offset_days=test_window_days - 1)
        if test_end > universe_end:
            break
        folds.append(
            Fold(
                fold_index=fold_index,
                train_start=train_start,
                train_end=train_end,
                validation_start=validation_start,
                validation_end=validation_end,
                test_start=test_start,
                test_end=test_end,
            )
        )
        fold_index += 1
        train_start = _day(train_start, offset_days=step_days)

    return WalkForwardPlan(
        campaign_name=campaign_name,
        universe_start=universe_start,
        universe_end=universe_end,
        split_style=SplitStyle.ROLLING,
        parameter_mode=parameter_mode,
        folds=folds,
        notes=list(notes) if notes else [],
        strategy_evidence=False,
    )


def expanding_window_plan(
    *,
    campaign_name: str,
    universe_start: date,
    universe_end: date,
    initial_train_window_days: int,
    validation_window_days: int,
    test_window_days: int,
    step_days: int,
    parameter_mode: ParameterMode = ParameterMode.FROZEN,
    notes: list[str] | None = None,
) -> WalkForwardPlan:
    """Generate an expanding-window walk-forward plan.

    The train window grows by ``step_days`` each fold (starting at
    ``initial_train_window_days``). Validation and test windows
    have fixed lengths and follow contiguously. The function
    produces every fold whose test window fits within
    ``universe_end``.
    """

    _require_positive(initial_train_window_days=initial_train_window_days)
    _require_positive(validation_window_days=validation_window_days)
    _require_positive(test_window_days=test_window_days)
    _require_positive(step_days=step_days)
    if universe_start > universe_end:
        raise ValueError("universe_start must be <= universe_end")

    folds: list[Fold] = []
    fold_index = 0
    train_window_days = initial_train_window_days
    while True:
        train_end = _day(universe_start, offset_days=train_window_days - 1)
        validation_start = _day(train_end, offset_days=1)
        validation_end = _day(
            validation_start, offset_days=validation_window_days - 1
        )
        test_start = _day(validation_end, offset_days=1)
        test_end = _day(test_start, offset_days=test_window_days - 1)
        if test_end > universe_end:
            break
        folds.append(
            Fold(
                fold_index=fold_index,
                train_start=universe_start,
                train_end=train_end,
                validation_start=validation_start,
                validation_end=validation_end,
                test_start=test_start,
                test_end=test_end,
            )
        )
        fold_index += 1
        train_window_days += step_days

    return WalkForwardPlan(
        campaign_name=campaign_name,
        universe_start=universe_start,
        universe_end=universe_end,
        split_style=SplitStyle.EXPANDING,
        parameter_mode=parameter_mode,
        folds=folds,
        notes=list(notes) if notes else [],
        strategy_evidence=False,
    )


def _require_positive(**kwargs: int) -> None:
    for name, value in kwargs.items():
        if value <= 0:
            raise ValueError(f"{name} must be > 0 (got {value})")

"""Tests for plan-level validation.

Exercises the 4 plan-level rules in
``research/walk_forward/validate.py``:
1. minimum fold count >= 3
2. forward-only fold ordering
3. no consecutive test-window overlap (rolling + expanding)
4. all-boundaries-in-universe

Plus a positive case (a well-formed plan validates silently) and a
JSON/markdown summary-generation smoke (Phase 3 task §6).
"""

from __future__ import annotations

import json
from datetime import date

import pytest
from research.walk_forward.models import (
    Fold,
    ParameterMode,
    SplitStyle,
    WalkForwardPlan,
)
from research.walk_forward.reporting import render_plan_md
from research.walk_forward.splits import (
    expanding_window_plan,
    rolling_window_plan,
)
from research.walk_forward.validate import (
    MIN_FOLD_COUNT,
    PlanValidationError,
    validate_plan,
)


def _annual_fold(idx: int, year: int) -> Fold:
    return Fold(
        fold_index=idx,
        train_start=date(year, 1, 1),
        train_end=date(year, 6, 30),
        validation_start=date(year, 7, 1),
        validation_end=date(year, 9, 30),
        test_start=date(year, 10, 1),
        test_end=date(year, 12, 31),
    )


def _plan(folds: list[Fold], *, style: SplitStyle = SplitStyle.ROLLING) -> WalkForwardPlan:
    return WalkForwardPlan(
        campaign_name="X",
        universe_start=date(2020, 1, 1),
        universe_end=date(2030, 12, 31),
        split_style=style,
        parameter_mode=ParameterMode.FROZEN,
        folds=folds,
    )


# ---------- Rule 1: minimum fold count ----------


def test_validate_rejects_fewer_than_three_folds() -> None:
    plan = _plan([_annual_fold(0, 2020), _annual_fold(1, 2021)])
    with pytest.raises(PlanValidationError, match="at least"):
        validate_plan(plan)


def test_validate_rejects_zero_folds() -> None:
    plan = _plan([])
    with pytest.raises(PlanValidationError):
        validate_plan(plan)


def test_validate_accepts_exactly_min_fold_count() -> None:
    plan = _plan([_annual_fold(i, 2020 + i) for i in range(MIN_FOLD_COUNT)])
    validate_plan(plan)


# ---------- Rule 2: forward-only fold ordering ----------


def test_validate_rejects_non_forward_test_ordering() -> None:
    """A later list-position fold whose test_start is on or before
    the prior fold's test_start should be rejected."""

    # We need to bypass the per-fold list-position == fold_index sanity
    # check by giving the folds matching indices. But the test windows
    # are inverted in time.
    f0 = _annual_fold(0, 2022)
    f1 = _annual_fold(1, 2021)
    f2 = _annual_fold(2, 2023)
    plan = _plan([f0, f1, f2])
    with pytest.raises(PlanValidationError, match="forward in time"):
        validate_plan(plan)


def test_validate_rejects_fold_index_not_matching_position() -> None:
    f0 = _annual_fold(0, 2020)
    f1 = _annual_fold(2, 2021)  # wrong index
    f2 = _annual_fold(1, 2022)  # wrong index
    plan = _plan([f0, f1, f2])
    with pytest.raises(PlanValidationError, match="fold_index"):
        validate_plan(plan)


# ---------- Rule 3: no consecutive test-window overlap ----------


def test_validate_rejects_overlapping_consecutive_test_windows() -> None:
    """Two folds whose test windows overlap should be rejected, even
    though each fold individually has a valid train/val/test
    structure. The folds must each PASS the Fold model's
    within-fold ordering — the failure must surface at plan-level
    validation, not at Fold construction."""

    f0 = Fold(
        fold_index=0,
        train_start=date(2020, 1, 1),
        train_end=date(2020, 6, 30),
        validation_start=date(2020, 7, 1),
        validation_end=date(2020, 9, 30),
        test_start=date(2020, 10, 1),
        test_end=date(2021, 6, 30),  # extends well into next year
    )
    f1 = Fold(
        fold_index=1,
        train_start=date(2021, 1, 1),
        train_end=date(2021, 3, 31),
        validation_start=date(2021, 4, 1),
        validation_end=date(2021, 5, 31),
        # test_start forward of f0.test_start (Rule 2 OK) but on or before
        # f0.test_end (2021-06-30) — Rule 3 must fail.
        test_start=date(2021, 6, 1),
        test_end=date(2021, 12, 31),
    )
    f2 = Fold(
        fold_index=2,
        train_start=date(2022, 1, 1),
        train_end=date(2022, 6, 30),
        validation_start=date(2022, 7, 1),
        validation_end=date(2022, 9, 30),
        test_start=date(2022, 10, 1),
        test_end=date(2022, 12, 31),
    )
    plan = _plan([f0, f1, f2])
    with pytest.raises(PlanValidationError, match="test-window overlap"):
        validate_plan(plan)


def test_validate_accepts_disjoint_consecutive_test_windows() -> None:
    plan = _plan([_annual_fold(i, 2020 + i) for i in range(3)])
    validate_plan(plan)


def test_validate_test_window_overlap_rule_applies_in_expanding_mode() -> None:
    """The no-overlap rule applies to both rolling and expanding
    modes; expanding's overlapping trains are fine but its tests
    still must be disjoint."""

    # Build a plan that looks expanding but with overlapping tests.
    f0 = Fold(
        fold_index=0,
        train_start=date(2020, 1, 1),
        train_end=date(2020, 6, 30),
        validation_start=date(2020, 7, 1),
        validation_end=date(2020, 9, 30),
        test_start=date(2020, 10, 1),
        test_end=date(2021, 6, 30),
    )
    f1 = Fold(
        fold_index=1,
        train_start=date(2020, 1, 1),  # expanding: same start
        train_end=date(2021, 3, 31),
        validation_start=date(2021, 4, 1),
        validation_end=date(2021, 5, 31),
        test_start=date(2021, 6, 1),  # overlaps f0 test (which ends 2021-06-30)
        test_end=date(2022, 5, 31),
    )
    f2 = Fold(
        fold_index=2,
        train_start=date(2020, 1, 1),
        train_end=date(2022, 6, 30),
        validation_start=date(2022, 7, 1),
        validation_end=date(2022, 9, 30),
        test_start=date(2022, 10, 1),
        test_end=date(2023, 9, 30),
    )
    plan = _plan([f0, f1, f2], style=SplitStyle.EXPANDING)
    with pytest.raises(PlanValidationError, match="test-window overlap"):
        validate_plan(plan)


# ---------- Rule 4: all-boundaries-in-universe ----------


def test_validate_rejects_fold_before_universe_start() -> None:
    f0 = Fold(
        fold_index=0,
        train_start=date(2019, 1, 1),  # before universe start (2020-01-01)
        train_end=date(2019, 6, 30),
        validation_start=date(2019, 7, 1),
        validation_end=date(2019, 9, 30),
        test_start=date(2019, 10, 1),
        test_end=date(2019, 12, 31),
    )
    f1 = _annual_fold(1, 2020)
    f2 = _annual_fold(2, 2021)
    plan = _plan([f0, f1, f2])
    with pytest.raises(PlanValidationError, match="universe_start"):
        validate_plan(plan)


def test_validate_rejects_fold_after_universe_end() -> None:
    f0 = _annual_fold(0, 2020)
    f1 = _annual_fold(1, 2021)
    f2 = Fold(
        fold_index=2,
        train_start=date(2031, 1, 1),
        train_end=date(2031, 6, 30),
        validation_start=date(2031, 7, 1),
        validation_end=date(2031, 9, 30),
        test_start=date(2031, 10, 1),
        test_end=date(2031, 12, 31),  # after universe end (2030-12-31)
    )
    plan = _plan([f0, f1, f2])
    with pytest.raises(PlanValidationError, match="universe_end"):
        validate_plan(plan)


# ---------- Generator + validator integration ----------


def test_rolling_generated_plan_passes_validation() -> None:
    plan = rolling_window_plan(
        campaign_name="T",
        universe_start=date(2020, 1, 1),
        universe_end=date(2024, 12, 31),
        train_window_days=365,
        validation_window_days=30,
        test_window_days=180,
        step_days=180,
    )
    validate_plan(plan)


def test_expanding_generated_plan_passes_validation() -> None:
    plan = expanding_window_plan(
        campaign_name="T",
        universe_start=date(2020, 1, 1),
        universe_end=date(2024, 12, 31),
        initial_train_window_days=365,
        validation_window_days=30,
        test_window_days=180,
        step_days=180,
    )
    validate_plan(plan)


# ---------- Phase 3 task §6: JSON / markdown summary generation ----------


def test_plan_serializes_to_json_round_trip() -> None:
    plan = rolling_window_plan(
        campaign_name="T",
        universe_start=date(2020, 1, 1),
        universe_end=date(2024, 12, 31),
        train_window_days=365,
        validation_window_days=30,
        test_window_days=180,
        step_days=180,
    )
    dumped = json.dumps(plan.model_dump(mode="json"), default=str)
    loaded = json.loads(dumped)
    reloaded = WalkForwardPlan(**loaded)
    assert reloaded.model_dump() == plan.model_dump()


def test_plan_markdown_renders_with_required_sections() -> None:
    plan = rolling_window_plan(
        campaign_name="T",
        universe_start=date(2020, 1, 1),
        universe_end=date(2024, 12, 31),
        train_window_days=365,
        validation_window_days=30,
        test_window_days=180,
        step_days=180,
    )
    md = render_plan_md(plan)
    assert "Walk-Forward Plan" in md
    assert "strategy_evidence: false" in md
    assert "rolling" in md
    assert "frozen" in md
    assert "Folds" in md
    assert "| 0 |" in md  # first fold row

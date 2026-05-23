"""Tests for rolling-window and expanding-window split generation.

Date-only fixtures; small synthetic universes. Verifies:
- determinism (same inputs → same folds)
- fold count derived correctly from universe / window / step
- expanding mode grows the train window each fold
- argument validation (positive lengths required)
"""

from __future__ import annotations

from datetime import date

import pytest
from research.walk_forward.models import ParameterMode, SplitStyle
from research.walk_forward.splits import (
    expanding_window_plan,
    rolling_window_plan,
)

# ---------- rolling_window_plan ----------


def test_rolling_window_plan_basic_three_folds() -> None:
    plan = rolling_window_plan(
        campaign_name="T",
        universe_start=date(2020, 1, 1),
        universe_end=date(2024, 12, 31),
        train_window_days=365,
        validation_window_days=30,
        test_window_days=180,
        step_days=180,
    )
    assert plan.campaign_name == "T"
    assert plan.split_style is SplitStyle.ROLLING
    assert plan.parameter_mode is ParameterMode.FROZEN
    assert plan.strategy_evidence is False
    assert len(plan.folds) >= 3
    # Each fold has the requested fixed window lengths.
    for fold in plan.folds:
        assert (fold.train_end - fold.train_start).days == 364  # 365 incl
        assert (fold.validation_end - fold.validation_start).days == 29
        assert (fold.test_end - fold.test_start).days == 179
    # Train start steps by step_days between folds.
    for prev, curr in zip(plan.folds, plan.folds[1:], strict=False):
        assert (curr.train_start - prev.train_start).days == 180


def test_rolling_window_plan_is_deterministic() -> None:
    args = dict(
        campaign_name="T",
        universe_start=date(2020, 1, 1),
        universe_end=date(2024, 12, 31),
        train_window_days=365,
        validation_window_days=30,
        test_window_days=180,
        step_days=180,
    )
    a = rolling_window_plan(**args)
    b = rolling_window_plan(**args)
    assert a.model_dump() == b.model_dump()


def test_rolling_window_plan_rejects_zero_windows() -> None:
    for bad in [
        dict(train_window_days=0),
        dict(validation_window_days=0),
        dict(test_window_days=0),
        dict(step_days=0),
        dict(train_window_days=-1),
    ]:
        kwargs = dict(
            campaign_name="T",
            universe_start=date(2020, 1, 1),
            universe_end=date(2024, 12, 31),
            train_window_days=365,
            validation_window_days=30,
            test_window_days=180,
            step_days=180,
        )
        kwargs.update(bad)
        with pytest.raises(ValueError):
            rolling_window_plan(**kwargs)


def test_rolling_window_plan_rejects_inverted_universe() -> None:
    with pytest.raises(ValueError):
        rolling_window_plan(
            campaign_name="T",
            universe_start=date(2024, 12, 31),
            universe_end=date(2020, 1, 1),
            train_window_days=365,
            validation_window_days=30,
            test_window_days=180,
            step_days=180,
        )


def test_rolling_window_plan_zero_folds_when_universe_too_short() -> None:
    plan = rolling_window_plan(
        campaign_name="T",
        universe_start=date(2020, 1, 1),
        universe_end=date(2020, 6, 30),  # too short for 365+30+180
        train_window_days=365,
        validation_window_days=30,
        test_window_days=180,
        step_days=180,
    )
    assert plan.folds == []


def test_rolling_window_plan_first_fold_starts_at_universe_start() -> None:
    plan = rolling_window_plan(
        campaign_name="T",
        universe_start=date(2020, 1, 1),
        universe_end=date(2024, 12, 31),
        train_window_days=365,
        validation_window_days=30,
        test_window_days=180,
        step_days=180,
    )
    assert plan.folds[0].train_start == date(2020, 1, 1)


# ---------- expanding_window_plan ----------


def test_expanding_window_plan_train_grows_each_fold() -> None:
    plan = expanding_window_plan(
        campaign_name="T",
        universe_start=date(2020, 1, 1),
        universe_end=date(2024, 12, 31),
        initial_train_window_days=365,
        validation_window_days=30,
        test_window_days=180,
        step_days=180,
    )
    assert plan.split_style is SplitStyle.EXPANDING
    assert len(plan.folds) >= 3
    # Train always starts at universe_start.
    for fold in plan.folds:
        assert fold.train_start == date(2020, 1, 1)
    # Train end advances by step_days between folds.
    for prev, curr in zip(plan.folds, plan.folds[1:], strict=False):
        assert (curr.train_end - prev.train_end).days == 180


def test_expanding_window_plan_is_deterministic() -> None:
    args = dict(
        campaign_name="T",
        universe_start=date(2020, 1, 1),
        universe_end=date(2024, 12, 31),
        initial_train_window_days=365,
        validation_window_days=30,
        test_window_days=180,
        step_days=180,
    )
    a = expanding_window_plan(**args)
    b = expanding_window_plan(**args)
    assert a.model_dump() == b.model_dump()


def test_expanding_window_plan_rejects_zero_windows() -> None:
    with pytest.raises(ValueError):
        expanding_window_plan(
            campaign_name="T",
            universe_start=date(2020, 1, 1),
            universe_end=date(2024, 12, 31),
            initial_train_window_days=0,
            validation_window_days=30,
            test_window_days=180,
            step_days=180,
        )


def test_expanding_window_plan_zero_folds_when_universe_too_short() -> None:
    plan = expanding_window_plan(
        campaign_name="T",
        universe_start=date(2020, 1, 1),
        universe_end=date(2020, 12, 31),
        initial_train_window_days=730,  # already longer than universe
        validation_window_days=30,
        test_window_days=180,
        step_days=180,
    )
    assert plan.folds == []

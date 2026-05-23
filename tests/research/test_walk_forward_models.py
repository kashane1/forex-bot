"""Walk-forward model + import-isolation tests.

Pins the data shapes the harness emits and consumes, including the
`strategy_evidence: false` rails on `WalkForwardPlan` and
`WalkForwardResults`. Also grep-enforces that no file under
`research/walk_forward/` imports from `forex_bot` (independence
rail, mirroring the verifier convention).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError
from research.walk_forward.models import (
    AggregateMetrics,
    Fold,
    FoldMetrics,
    ParameterMode,
    SplitStyle,
    WalkForwardPlan,
    WalkForwardResults,
)


def _fold(idx: int, start_year: int) -> Fold:
    return Fold(
        fold_index=idx,
        train_start=date(start_year, 1, 1),
        train_end=date(start_year, 6, 30),
        validation_start=date(start_year, 7, 1),
        validation_end=date(start_year, 9, 30),
        test_start=date(start_year, 10, 1),
        test_end=date(start_year, 12, 31),
    )


def _plan(folds: list[Fold]) -> WalkForwardPlan:
    return WalkForwardPlan(
        campaign_name="X",
        universe_start=date(2020, 1, 1),
        universe_end=date(2030, 12, 31),
        split_style=SplitStyle.ROLLING,
        parameter_mode=ParameterMode.FROZEN,
        folds=folds,
    )


# ---------- Fold ----------


def test_fold_rejects_train_after_validation() -> None:
    with pytest.raises(ValidationError):
        Fold(
            fold_index=0,
            train_start=date(2020, 1, 1),
            train_end=date(2020, 12, 31),
            validation_start=date(2020, 6, 1),  # overlaps train
            validation_end=date(2020, 8, 31),
            test_start=date(2020, 9, 1),
            test_end=date(2020, 12, 31),
        )


def test_fold_rejects_validation_after_test() -> None:
    with pytest.raises(ValidationError):
        Fold(
            fold_index=0,
            train_start=date(2020, 1, 1),
            train_end=date(2020, 3, 31),
            validation_start=date(2020, 4, 1),
            validation_end=date(2020, 9, 30),
            test_start=date(2020, 6, 1),  # overlaps validation
            test_end=date(2020, 12, 31),
        )


def test_fold_rejects_inverted_train_window() -> None:
    with pytest.raises(ValidationError):
        Fold(
            fold_index=0,
            train_start=date(2020, 6, 30),
            train_end=date(2020, 1, 1),  # before start
            validation_start=date(2020, 7, 1),
            validation_end=date(2020, 9, 30),
            test_start=date(2020, 10, 1),
            test_end=date(2020, 12, 31),
        )


def test_fold_accepts_valid_three_window_layout() -> None:
    fold = _fold(0, 2020)
    assert fold.fold_index == 0
    assert fold.train_end < fold.validation_start
    assert fold.validation_end < fold.test_start


# ---------- WalkForwardPlan ----------


def test_plan_rejects_strategy_evidence_true() -> None:
    with pytest.raises(ValidationError):
        WalkForwardPlan(
            campaign_name="X",
            universe_start=date(2020, 1, 1),
            universe_end=date(2030, 12, 31),
            split_style=SplitStyle.ROLLING,
            parameter_mode=ParameterMode.FROZEN,
            folds=[_fold(0, 2020)],
            strategy_evidence=True,
        )


def test_plan_rejects_inverted_universe() -> None:
    with pytest.raises(ValidationError):
        WalkForwardPlan(
            campaign_name="X",
            universe_start=date(2030, 1, 1),
            universe_end=date(2020, 1, 1),
            split_style=SplitStyle.ROLLING,
            parameter_mode=ParameterMode.FROZEN,
            folds=[],
        )


def test_plan_accepts_zero_folds_at_construction() -> None:
    """The Plan model itself does not require >=3 folds; that's a
    plan-level rule enforced by ``validate_plan``."""

    plan = _plan(folds=[])
    assert len(plan.folds) == 0


def test_split_style_and_parameter_mode_enum_values() -> None:
    assert SplitStyle.ROLLING.value == "rolling"
    assert SplitStyle.EXPANDING.value == "expanding"
    assert ParameterMode.FROZEN.value == "frozen"
    assert ParameterMode.PER_FOLD_FROM_TRAIN.value == "per_fold_from_train"
    assert ParameterMode.PER_FOLD_FROM_VALIDATION.value == "per_fold_from_validation"


# ---------- FoldMetrics + AggregateMetrics ----------


def test_fold_metrics_pass_gates_required() -> None:
    fm = FoldMetrics(
        fold_index=0,
        total_trades=10,
        bars_in_test_window=100,
        pass_pre_commit_gates=True,
    )
    assert fm.pass_pre_commit_gates is True


def test_aggregate_metrics_pass_rate_consistency() -> None:
    """If folds_passing_gates / fold_count != fold_pass_rate,
    construction must fail."""

    with pytest.raises(ValidationError):
        AggregateMetrics(
            fold_count=4,
            folds_passing_gates=2,
            fold_pass_rate=0.9,  # actual 0.5
            total_trades_across_folds=100,
        )


def test_aggregate_metrics_rejects_passing_gt_count() -> None:
    with pytest.raises(ValidationError):
        AggregateMetrics(
            fold_count=3,
            folds_passing_gates=5,
            fold_pass_rate=5 / 3,
            total_trades_across_folds=100,
        )


def test_aggregate_metrics_zero_folds_zero_pass_rate() -> None:
    AggregateMetrics(
        fold_count=0,
        folds_passing_gates=0,
        fold_pass_rate=0.0,
        total_trades_across_folds=0,
    )


# ---------- WalkForwardResults ----------


def test_results_rejects_strategy_evidence_true() -> None:
    plan = _plan([_fold(0, 2020), _fold(1, 2021), _fold(2, 2022)])
    with pytest.raises(ValidationError):
        WalkForwardResults(
            plan=plan,
            fold_metrics=[
                FoldMetrics(fold_index=i, total_trades=0,
                            bars_in_test_window=100,
                            pass_pre_commit_gates=False)
                for i in range(3)
            ],
            aggregate=AggregateMetrics(
                fold_count=3, folds_passing_gates=0,
                fold_pass_rate=0.0, total_trades_across_folds=0,
            ),
            overall_verdict="REJECT",
            strategy_evidence=True,
        )


def test_results_rejects_invalid_overall_verdict() -> None:
    plan = _plan([_fold(0, 2020), _fold(1, 2021), _fold(2, 2022)])
    with pytest.raises(ValidationError):
        WalkForwardResults(
            plan=plan,
            fold_metrics=[
                FoldMetrics(fold_index=i, total_trades=0,
                            bars_in_test_window=100,
                            pass_pre_commit_gates=False)
                for i in range(3)
            ],
            aggregate=AggregateMetrics(
                fold_count=3, folds_passing_gates=0,
                fold_pass_rate=0.0, total_trades_across_folds=0,
            ),
            overall_verdict="MAYBE",
        )


def test_results_rejects_fold_metric_count_mismatch() -> None:
    plan = _plan([_fold(0, 2020), _fold(1, 2021), _fold(2, 2022)])
    with pytest.raises(ValidationError):
        WalkForwardResults(
            plan=plan,
            fold_metrics=[
                FoldMetrics(fold_index=0, total_trades=0,
                            bars_in_test_window=100,
                            pass_pre_commit_gates=False),
            ],  # only 1 metric for 3 folds
            aggregate=AggregateMetrics(
                fold_count=3, folds_passing_gates=0,
                fold_pass_rate=0.0, total_trades_across_folds=0,
            ),
            overall_verdict="REJECT",
        )


def test_results_rejects_fold_index_set_mismatch() -> None:
    plan = _plan([_fold(0, 2020), _fold(1, 2021), _fold(2, 2022)])
    with pytest.raises(ValidationError):
        WalkForwardResults(
            plan=plan,
            fold_metrics=[
                FoldMetrics(fold_index=0, total_trades=0,
                            bars_in_test_window=100,
                            pass_pre_commit_gates=False),
                FoldMetrics(fold_index=1, total_trades=0,
                            bars_in_test_window=100,
                            pass_pre_commit_gates=False),
                FoldMetrics(fold_index=99, total_trades=0,  # not in plan
                            bars_in_test_window=100,
                            pass_pre_commit_gates=False),
            ],
            aggregate=AggregateMetrics(
                fold_count=3, folds_passing_gates=0,
                fold_pass_rate=0.0, total_trades_across_folds=0,
            ),
            overall_verdict="REJECT",
        )


def test_results_accepts_consistent_plan_metrics_aggregate() -> None:
    plan = _plan([_fold(0, 2020), _fold(1, 2021), _fold(2, 2022)])
    results = WalkForwardResults(
        plan=plan,
        fold_metrics=[
            FoldMetrics(fold_index=i, total_trades=10,
                        bars_in_test_window=100,
                        pass_pre_commit_gates=True)
            for i in range(3)
        ],
        aggregate=AggregateMetrics(
            fold_count=3, folds_passing_gates=3,
            fold_pass_rate=1.0, total_trades_across_folds=30,
        ),
        overall_verdict="PASS",
    )
    assert results.overall_verdict == "PASS"


# ---------- Import-isolation rail ----------


def test_walk_forward_package_does_not_import_forex_bot() -> None:
    """Independence rail: no file under research/walk_forward/ may
    import the bespoke engine. A grep is sufficient because Python's
    import resolution only fires on the exact name."""

    pkg = Path(__file__).resolve().parents[2] / "research" / "walk_forward"
    offenders: list[str] = []
    for path in pkg.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if "forex_bot" in stripped and (
                stripped.startswith("import ") or stripped.startswith("from ")
            ):
                offenders.append(f"{path}:{line_no}: {stripped}")
    assert offenders == [], (
        "walk_forward must not import forex_bot:\n" + "\n".join(offenders)
    )

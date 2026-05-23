"""Walk-forward fold-plan + results models.

Pydantic models pin the shapes the harness consumes and emits.
``extra="forbid"`` catches schema drift. Strategy-evidence rails
(``strategy_evidence: false``) are baked into ``WalkForwardPlan``
and ``WalkForwardResults`` — constructing either with the flag
flipped raises ``ValidationError``.

See ``docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md`` for the
field-by-field protocol.
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SplitStyle(str, Enum):
    """How successive folds are generated."""

    ROLLING = "rolling"
    EXPANDING = "expanding"


class ParameterMode(str, Enum):
    """How strategy parameters are chosen per fold.

    Under the current research freeze only ``FROZEN`` is valid.
    The other two modes are reserved for future authorized
    adaptive campaigns; the schema supports them so a future
    addition does not require a schema migration.
    """

    FROZEN = "frozen"
    PER_FOLD_FROM_TRAIN = "per_fold_from_train"
    PER_FOLD_FROM_VALIDATION = "per_fold_from_validation"


class Fold(BaseModel):
    """One walk-forward fold: three contiguous, non-overlapping
    date ranges in train → validation → test order.

    For frozen-parameter strategies, ``train`` and ``validation``
    are documentation-only — they record the bars **excluded**
    from the test evaluation per fold. The harness still
    enforces the three-window structure so the protocol
    generalizes cleanly to a future adaptive candidate.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    fold_index: int = Field(ge=0)
    train_start: date
    train_end: date
    validation_start: date
    validation_end: date
    test_start: date
    test_end: date

    @model_validator(mode="after")
    def _check_windows(self) -> Fold:
        if not (self.train_start <= self.train_end):
            raise ValueError(
                f"fold {self.fold_index}: train_start "
                f"({self.train_start}) > train_end ({self.train_end})"
            )
        if not (self.validation_start <= self.validation_end):
            raise ValueError(
                f"fold {self.fold_index}: validation_start "
                f"({self.validation_start}) > validation_end "
                f"({self.validation_end})"
            )
        if not (self.test_start <= self.test_end):
            raise ValueError(
                f"fold {self.fold_index}: test_start ({self.test_start}) > "
                f"test_end ({self.test_end})"
            )
        # contiguous, non-overlapping
        if not (self.train_end < self.validation_start):
            raise ValueError(
                f"fold {self.fold_index}: train_end ({self.train_end}) must "
                f"be strictly before validation_start ({self.validation_start})"
            )
        if not (self.validation_end < self.test_start):
            raise ValueError(
                f"fold {self.fold_index}: validation_end "
                f"({self.validation_end}) must be strictly before test_start "
                f"({self.test_start})"
            )
        return self


class FoldMetrics(BaseModel):
    """Per-fold test-window metrics, produced by the campaign code
    that consumes a plan. The harness validates the schema only —
    it does not run any backtest."""

    model_config = ConfigDict(extra="forbid")

    fold_index: int = Field(ge=0)
    total_trades: int = Field(ge=0)
    bars_in_test_window: int = Field(ge=0)
    expectancy_r: float | None = None
    return_pct: float | None = None
    profit_factor: float | None = None
    max_drawdown_pct: float | None = None
    win_rate: float | None = None
    long_trades: int | None = None
    short_trades: int | None = None
    pass_pre_commit_gates: bool


class AggregateMetrics(BaseModel):
    """Cross-fold aggregate metrics."""

    model_config = ConfigDict(extra="forbid")

    fold_count: int = Field(ge=0)
    folds_passing_gates: int = Field(ge=0)
    fold_pass_rate: float
    total_trades_across_folds: int = Field(ge=0)
    aggregate_expectancy_r: float | None = None
    aggregate_return_pct: float | None = None
    single_fold_max_return_share: float | None = None

    @model_validator(mode="after")
    def _check_pass_rate(self) -> AggregateMetrics:
        if self.fold_count > 0:
            expected_rate = self.folds_passing_gates / self.fold_count
            if abs(self.fold_pass_rate - expected_rate) > 1e-9:
                raise ValueError(
                    f"fold_pass_rate ({self.fold_pass_rate}) does not equal "
                    f"folds_passing_gates / fold_count ({expected_rate})"
                )
        elif self.fold_pass_rate != 0.0:
            raise ValueError("fold_pass_rate must be 0.0 when fold_count == 0")
        if self.folds_passing_gates > self.fold_count:
            raise ValueError(
                f"folds_passing_gates ({self.folds_passing_gates}) > "
                f"fold_count ({self.fold_count})"
            )
        return self


class WalkForwardPlan(BaseModel):
    """A walk-forward fold plan emitted by the harness."""

    model_config = ConfigDict(extra="forbid")

    campaign_name: str
    universe_start: date
    universe_end: date
    split_style: SplitStyle
    parameter_mode: ParameterMode
    folds: list[Fold]
    notes: list[str] = Field(default_factory=list)
    strategy_evidence: bool = False

    @model_validator(mode="after")
    def _check(self) -> WalkForwardPlan:
        if self.strategy_evidence:
            raise ValueError(
                "strategy_evidence must be False — the walk-forward harness "
                "is diagnostic infrastructure and cannot approve a strategy"
            )
        if not (self.universe_start <= self.universe_end):
            raise ValueError(
                f"universe_start ({self.universe_start}) > universe_end "
                f"({self.universe_end})"
            )
        return self


class WalkForwardResults(BaseModel):
    """Per-fold metrics + aggregates for a completed walk-forward
    run. Produced by the campaign code that consumes the plan; the
    harness validates the schema only."""

    model_config = ConfigDict(extra="forbid")

    plan: WalkForwardPlan
    fold_metrics: list[FoldMetrics]
    aggregate: AggregateMetrics
    overall_verdict: str  # "PASS" or "REJECT" — campaign-defined
    strategy_evidence: bool = False

    @model_validator(mode="after")
    def _check(self) -> WalkForwardResults:
        if self.strategy_evidence:
            raise ValueError(
                "strategy_evidence must be False — the walk-forward harness "
                "is diagnostic infrastructure and cannot approve a strategy"
            )
        if self.overall_verdict not in {"PASS", "REJECT"}:
            raise ValueError(
                f"overall_verdict must be 'PASS' or 'REJECT', got "
                f"{self.overall_verdict!r}"
            )
        if len(self.fold_metrics) != len(self.plan.folds):
            raise ValueError(
                f"fold_metrics length ({len(self.fold_metrics)}) does not "
                f"match plan.folds length ({len(self.plan.folds)})"
            )
        plan_fold_indices = {fold.fold_index for fold in self.plan.folds}
        metric_fold_indices = {fm.fold_index for fm in self.fold_metrics}
        if plan_fold_indices != metric_fold_indices:
            raise ValueError(
                f"fold_metrics fold_index set ({sorted(metric_fold_indices)}) "
                f"does not match plan folds ({sorted(plan_fold_indices)})"
            )
        if self.aggregate.fold_count != len(self.plan.folds):
            raise ValueError(
                f"aggregate.fold_count ({self.aggregate.fold_count}) does "
                f"not match plan.folds length ({len(self.plan.folds)})"
            )
        return self

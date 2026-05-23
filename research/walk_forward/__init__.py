"""Walk-forward research harness.

A reusable, independent fold-generation library for walk-forward
strategy research. The harness produces fold specs (train,
validation, test date windows), validates them (no overlap, no
leakage, minimum count), and renders summaries.

Strategy execution stays in ``src/forex_bot/backtesting/``. The
harness sits on top and is consumed by the campaign code that
runs the strategy against each fold's test window.

Safety constraints (mirrored from the free / local verifier):

- imports nothing from ``forex_bot`` — independence is enforced by
  a grep test in ``tests/research/test_walk_forward_models.py``;
- makes no network calls, no broker calls, no QuantConnect / LEAN
  calls;
- reads no files at import time;
- writes no strategy approval, no campaign verdict, no broker
  order;
- harness outputs carry ``strategy_evidence: false``.

See ``docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md`` for the
protocol the harness enforces.
"""

from research.walk_forward.models import (
    AggregateMetrics,
    Fold,
    FoldMetrics,
    ParameterMode,
    SplitStyle,
    WalkForwardPlan,
    WalkForwardResults,
)
from research.walk_forward.reporting import (
    render_plan_md,
    render_results_md,
)
from research.walk_forward.splits import (
    expanding_window_plan,
    rolling_window_plan,
)
from research.walk_forward.validate import (
    PlanValidationError,
    validate_plan,
)

__all__ = [
    "AggregateMetrics",
    "Fold",
    "FoldMetrics",
    "ParameterMode",
    "PlanValidationError",
    "SplitStyle",
    "WalkForwardPlan",
    "WalkForwardResults",
    "expanding_window_plan",
    "render_plan_md",
    "render_results_md",
    "rolling_window_plan",
    "validate_plan",
]

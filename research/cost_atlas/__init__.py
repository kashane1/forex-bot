"""Observed spread / cost atlas for H4 bid/ask research universe.

Diagnostic infrastructure only — ``strategy_evidence: false``.
"""

from research.cost_atlas.atlas import (
    AtlasBuildResult,
    build_cost_atlas,
    classify_cost_state,
    flag_cost_hostile_cells,
)
from research.cost_atlas.loader import SEVEN_PAIR_UNIVERSE, load_deduped_h4_frame
from research.cost_atlas.metrics import compute_bar_metrics
from research.cost_atlas.session import session_bucket, weekday_name

__all__ = [
    "SEVEN_PAIR_UNIVERSE",
    "AtlasBuildResult",
    "build_cost_atlas",
    "classify_cost_state",
    "compute_bar_metrics",
    "flag_cost_hostile_cells",
    "load_deduped_h4_frame",
    "session_bucket",
    "weekday_name",
]

"""Multi-timeframe confluence prototype — research only, strategy_evidence: false."""

from research.confluence.divergence import DivergenceState, detect_divergence
from research.confluence.grader import ConfluenceScore, grade_confluence
from research.confluence.models import (
    AlignmentState,
    ConfluenceGrade,
    CostState,
    CrossAssetState,
    TimeframeState,
)
from research.confluence.states import (
    aggregate_d1_from_h4,
    compute_h4_setup,
    compute_timeframe_state,
    resample_h4_to_d1,
)

__all__ = [
    "AlignmentState",
    "ConfluenceGrade",
    "ConfluenceScore",
    "CostState",
    "CrossAssetState",
    "DivergenceState",
    "TimeframeState",
    "aggregate_d1_from_h4",
    "compute_h4_setup",
    "compute_timeframe_state",
    "detect_divergence",
    "grade_confluence",
    "resample_h4_to_d1",
]

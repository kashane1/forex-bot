"""Anti-overfit diagnostic classifiers.

Pure functions only. These classifiers cannot approve a strategy —
they emit one of a small set of labels describing how a campaign's
aggregate evidence compares to a matched null. See
docs/research/CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md §11
for the binding label set.
"""

from research.anti_overfit.campaign_015 import (
    CAMPAIGN_015_CLASSIFIER_LABELS,
    DiagnosticInputs,
    classify_campaign_015,
)

__all__ = [
    "CAMPAIGN_015_CLASSIFIER_LABELS",
    "DiagnosticInputs",
    "classify_campaign_015",
]

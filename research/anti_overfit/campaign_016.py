"""CAMPAIGN_016 anti-overfit diagnostic classifier.

Mirrors ``research.anti_overfit.campaign_015`` with CAMPAIGN_016 gates.
"""

from __future__ import annotations

from research.anti_overfit.campaign_015 import (
    AGG_EXPECTANCY_R_MIN_BASE,
    AGG_PROFIT_FACTOR_MIN_BASE,
    CAMPAIGN_015_CLASSIFIER_LABELS,
    DiagnosticInputs,
    classify_campaign_015,
)

CAMPAIGN_016_CLASSIFIER_LABELS = CAMPAIGN_015_CLASSIFIER_LABELS


def classify_campaign_016(inputs: DiagnosticInputs) -> dict[str, object]:
    """Classify CAMPAIGN_016 vs deduped CAMPAIGN_011 null."""
    return classify_campaign_015(inputs)


__all__ = [
    "AGG_EXPECTANCY_R_MIN_BASE",
    "AGG_PROFIT_FACTOR_MIN_BASE",
    "CAMPAIGN_016_CLASSIFIER_LABELS",
    "DiagnosticInputs",
    "classify_campaign_016",
]

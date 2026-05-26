"""CAMPAIGN_017 anti-overfit diagnostic classifier."""

from __future__ import annotations

from research.anti_overfit.campaign_015 import (
    AGG_EXPECTANCY_R_MIN_BASE,
    AGG_PROFIT_FACTOR_MIN_BASE,
    CAMPAIGN_015_CLASSIFIER_LABELS,
    DiagnosticInputs,
    classify_campaign_015,
)

CAMPAIGN_017_CLASSIFIER_LABELS = CAMPAIGN_015_CLASSIFIER_LABELS


def classify_campaign_017(inputs: DiagnosticInputs) -> dict[str, object]:
    """Classify CAMPAIGN_017 vs deduped CAMPAIGN_011 null."""
    return classify_campaign_015(inputs)


__all__ = [
    "AGG_EXPECTANCY_R_MIN_BASE",
    "AGG_PROFIT_FACTOR_MIN_BASE",
    "CAMPAIGN_017_CLASSIFIER_LABELS",
    "DiagnosticInputs",
    "classify_campaign_017",
]

"""Execution-realism metadata policy for research campaigns.

Gates promotion-readiness and validates approval-bound campaign metadata.
Does not approve strategies or enable trading loops.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class FillTiming(StrEnum):
    NEXT_BAR_OPEN = "next_bar_open"
    SIGNAL_BAR_CLOSE = "signal_bar_close"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class ExecutionRealism(StrEnum):
    CONSERVATIVE = "conservative"
    OPTIMISTIC_UPPER_BOUND = "optimistic_upper_bound"
    DIAGNOSTIC = "diagnostic"
    UNKNOWN = "unknown"


class EvidenceUse(StrEnum):
    APPROVAL_BOUND = "approval_bound"
    PROMOTION_REVIEW = "promotion_review"
    RESEARCH_ONLY = "research_only"
    LEGACY = "legacy"
    DIAGNOSTIC = "diagnostic"


class ExecutionRealismMetadata(BaseModel):
    """Optional research metadata block (YAML or manifest)."""

    model_config = ConfigDict(extra="forbid")

    fill_timing: FillTiming | None = None
    execution_realism: ExecutionRealism | None = None
    evidence_use: EvidenceUse | None = None
    promotion_eligible: bool | None = None
    fill_timing_justification: str | None = None

    @model_validator(mode="after")
    def _policy_rules(self) -> ExecutionRealismMetadata:
        if self.evidence_use in {
            EvidenceUse.APPROVAL_BOUND,
            EvidenceUse.PROMOTION_REVIEW,
        }:
            if self.fill_timing is None:
                raise ValueError("fill_timing required for approval_bound / promotion_review")
            if self.fill_timing != FillTiming.NEXT_BAR_OPEN and not (
                self.fill_timing_justification or ""
            ).strip():
                raise ValueError(
                    "fill_timing != next_bar_open requires fill_timing_justification"
                )
        if self.fill_timing == FillTiming.SIGNAL_BAR_CLOSE:
            if self.promotion_eligible is True:
                raise ValueError("signal_bar_close cannot be promotion_eligible")
            if self.evidence_use in {
                EvidenceUse.APPROVAL_BOUND,
                EvidenceUse.PROMOTION_REVIEW,
            }:
                raise ValueError(
                    "signal_bar_close is not allowed for approval_bound / promotion_review"
                )
        return self


def parse_research_metadata(raw: dict[str, Any] | None) -> ExecutionRealismMetadata | None:
    if not raw:
        return None
    return ExecutionRealismMetadata.model_validate(raw)


def legacy_mode_metadata() -> ExecutionRealismMetadata:
    """Compatibility shim for historical campaigns without metadata."""
    return ExecutionRealismMetadata(
        fill_timing=FillTiming.UNKNOWN,
        execution_realism=ExecutionRealism.UNKNOWN,
        evidence_use=EvidenceUse.LEGACY,
        promotion_eligible=False,
    )


def validate_campaign_yaml_metadata(campaign_yaml: dict[str, Any]) -> list[str]:
    """Validate ``research_metadata`` if present; return errors (empty = ok)."""
    block = campaign_yaml.get("research_metadata")
    if block is None:
        return []
    try:
        parse_research_metadata(block)
    except ValidationError as exc:
        return [str(exc)]
    return []


def promotion_readiness_errors(meta: ExecutionRealismMetadata | None) -> list[str]:
    """Return blockers for promotion-readiness (not approval)."""
    if meta is None:
        return ["missing research_metadata / execution realism fields"]
    if meta.promotion_eligible is False:
        return ["promotion_eligible is false"]
    if meta.fill_timing in {None, FillTiming.UNKNOWN}:
        return ["fill_timing missing or unknown"]
    if meta.fill_timing == FillTiming.SIGNAL_BAR_CLOSE:
        if not (meta.fill_timing_justification or "").strip():
            return ["signal_bar_close without justification blocks promotion"]
        return ["signal_bar_close is upper-bound/diagnostic only"]
    if meta.fill_timing != FillTiming.NEXT_BAR_OPEN:
        return [f"fill_timing {meta.fill_timing} not promotion-default"]
    if meta.execution_realism == ExecutionRealism.OPTIMISTIC_UPPER_BOUND:
        return ["execution_realism optimistic_upper_bound blocks promotion"]
    return []


def is_promotion_ready(meta: ExecutionRealismMetadata | None) -> bool:
    return not promotion_readiness_errors(meta)


def classify_historical_campaign(campaign_id: str, *, trades_fill_timing: str | None) -> ExecutionRealismMetadata:
    """Best-effort classification for historical campaigns."""
    ft = FillTiming.UNKNOWN
    er = ExecutionRealism.UNKNOWN
    if trades_fill_timing == "signal_bar_close":
        ft = FillTiming.SIGNAL_BAR_CLOSE
        er = ExecutionRealism.OPTIMISTIC_UPPER_BOUND
    elif trades_fill_timing == "next_bar_open":
        ft = FillTiming.NEXT_BAR_OPEN
        er = ExecutionRealism.CONSERVATIVE
    return ExecutionRealismMetadata(
        fill_timing=ft,
        execution_realism=er,
        evidence_use=EvidenceUse.LEGACY,
        promotion_eligible=False,
        fill_timing_justification=f"historical campaign {campaign_id}",
    )

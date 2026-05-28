"""Tests for execution-realism / fill_timing policy."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from forex_bot.approval import execution_realism_promotion_blockers, load_approval_registry
from forex_bot.research.execution_realism import (
    EvidenceUse,
    legacy_mode_metadata,
    parse_research_metadata,
    promotion_readiness_errors,
    validate_campaign_yaml_metadata,
)


def test_approval_bound_next_bar_open_passes() -> None:
    meta = parse_research_metadata(
        {
            "fill_timing": "next_bar_open",
            "execution_realism": "conservative",
            "evidence_use": "approval_bound",
            "promotion_eligible": True,
        }
    )
    assert meta is not None
    assert promotion_readiness_errors(meta) == []


def test_approval_bound_signal_bar_close_fails() -> None:
    with pytest.raises(ValidationError):
        parse_research_metadata(
            {
                "fill_timing": "signal_bar_close",
                "evidence_use": "approval_bound",
            }
        )


def test_signal_bar_close_diagnostic_passes_not_promotion_ready() -> None:
    meta = parse_research_metadata(
        {
            "fill_timing": "signal_bar_close",
            "execution_realism": "optimistic_upper_bound",
            "evidence_use": "diagnostic",
            "promotion_eligible": False,
            "fill_timing_justification": "C019 comparison upper bound",
        }
    )
    assert meta is not None
    assert promotion_readiness_errors(meta)


def test_legacy_missing_fields_compat() -> None:
    meta = legacy_mode_metadata()
    assert meta.evidence_use == EvidenceUse.LEGACY
    assert validate_campaign_yaml_metadata({}) == []


def test_unknown_fill_timing_blocks_promotion() -> None:
    meta = parse_research_metadata(
        {
            "fill_timing": "unknown",
            "execution_realism": "conservative",
            "evidence_use": "promotion_review",
            "promotion_eligible": True,
            "fill_timing_justification": "pending fill timing declaration",
        }
    )
    assert meta is not None
    assert promotion_readiness_errors(meta)


def test_approved_registry_empty() -> None:
    assert load_approval_registry() == []


def test_approval_module_promotion_blockers() -> None:
    meta = parse_research_metadata(
        {
            "fill_timing": "signal_bar_close",
            "execution_realism": "optimistic_upper_bound",
            "evidence_use": "diagnostic",
            "promotion_eligible": False,
            "fill_timing_justification": "upper bound",
        }
    )
    assert execution_realism_promotion_blockers(meta)

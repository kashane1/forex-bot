"""Tests for H4 research window resolution."""

from __future__ import annotations

from pathlib import Path

import pytest
from research.cross_asset_features.research_window import (
    research_window_report,
    resolve_h4_research_window,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_resolve_h4_research_window() -> None:
    try:
        window = resolve_h4_research_window(REPO_ROOT, warmup_start="2018-01-01")
    except FileNotFoundError:
        pytest.skip("H4 SQLite store not present")
    assert window.observation_start == "2018-01-01"
    assert window.h4_first < window.h4_last
    assert window.observation_end >= "2020-01-01"


def test_research_window_report_shape() -> None:
    try:
        report = research_window_report(REPO_ROOT)
    except FileNotFoundError:
        pytest.skip("H4 SQLite store not present")
    assert report["strategy_evidence"] is False
    assert "observation_end" in report

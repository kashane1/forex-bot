"""Tests for enhanced manifest and full-window normalization."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from research.cross_asset_features.normalizer import (
    normalize_from_sources,
    validate_manifest,
    write_normalized_outputs,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def no_fred_key() -> None:
    with patch(
        "research.cross_asset_features.normalizer.get_fred_api_key",
        return_value=None,
    ):
        yield


def test_validate_manifest() -> None:
    manifest = {
        "strategy_evidence": False,
        "status": "FIXTURE_ONLY",
        "observation_start": "2018-01-01",
        "columns": ["vix"],
        "row_count": 1,
    }
    assert validate_manifest(manifest) == []


def test_blocked_full_window_no_fixture_fallback(
    tmp_path: Path, no_fred_key: None
) -> None:
    wide, manifest, status = normalize_from_sources(
        REPO_ROOT,
        data_dir=tmp_path / "empty",
        cache_dir=tmp_path / "empty" / ".fred_cache",
        allow_fixture_fallback=False,
        observation_start="2018-01-01",
        observation_end="2026-05-24",
    )
    assert status == "BLOCKED_FULL_WINDOW"
    assert manifest["fred_api_key_present"] is False
    assert validate_manifest(manifest) == []


def test_derived_features_with_fixtures(tmp_path: Path, no_fred_key: None) -> None:
    wide, manifest, status = normalize_from_sources(
        REPO_ROOT,
        data_dir=tmp_path / "empty",
        cache_dir=tmp_path / "empty" / ".fred_cache",
        allow_fixture_fallback=True,
    )
    assert status == "FIXTURE_ONLY"
    assert "us_10y_minus_2y" in wide.columns
    assert manifest["features"]["us_10y_minus_2y"]["source_type"] == "derived"


def test_write_normalized_outputs_manifest(tmp_path: Path) -> None:
    paths = write_normalized_outputs(REPO_ROOT, tmp_path, allow_fixture_fallback=True)
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    assert manifest["strategy_evidence"] is False
    assert "ingestion_timestamp_utc" in manifest

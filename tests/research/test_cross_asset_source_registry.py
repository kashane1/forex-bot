"""Tests for cross-asset source registry validation."""

from __future__ import annotations

from pathlib import Path

from research.cross_asset_features.schema import (
    CANONICAL_FEATURE_IDS,
    LEGACY_FEATURE_ALIASES,
    load_source_registry,
    resolve_feature_id,
    validate_source_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_source_registry_validates() -> None:
    errors = validate_source_registry()
    assert errors == []


def test_required_features_present() -> None:
    registry = load_source_registry()
    required_ids = {f["feature_id"] for f in registry["features"] if f.get("required")}
    for fid in (
        "broad_usd_index",
        "us_2y_yield",
        "us_10y_yield",
        "us_10y_minus_2y",
        "vix",
        "sp500",
        "oil_wti",
    ):
        assert fid in required_ids


def test_derived_features_declare_dependencies() -> None:
    registry = load_source_registry()
    for entry in registry["features"]:
        if entry.get("source_type") == "derived":
            assert entry.get("depends_on"), f"{entry['feature_id']} missing depends_on"


def test_no_duplicate_feature_ids() -> None:
    registry = load_source_registry()
    ids = [f["feature_id"] for f in registry["features"]]
    assert len(ids) == len(set(ids))


def test_max_staleness_for_daily_weekly() -> None:
    registry = load_source_registry()
    for entry in registry["features"]:
        if entry.get("frequency") in ("daily", "weekly"):
            assert entry.get("max_staleness_days") is not None


def test_strategy_evidence_false() -> None:
    registry = load_source_registry()
    assert registry["strategy_evidence"] is False


def test_legacy_aliases_resolve() -> None:
    assert resolve_feature_id("dxy") == "broad_usd_index"
    assert resolve_feature_id("us10y") == "us_10y_yield"
    assert "broad_usd_index" in CANONICAL_FEATURE_IDS
    assert LEGACY_FEATURE_ALIASES["oil"] == "oil_wti"

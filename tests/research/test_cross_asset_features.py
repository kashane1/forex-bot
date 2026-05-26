"""Tests for cross-asset feature loader."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from research.cross_asset_features.loader import (
    align_features_to_h4,
    build_availability_report,
    load_feature_csv,
    load_features_from_directory,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "cross_asset"


def test_load_feature_csv_dxy() -> None:
    fs = load_feature_csv(FIXTURE_DIR / "dxy.csv", "dxy")
    assert len(fs.frame) == 5
    assert fs.name == "dxy"


def test_align_features_no_lookahead() -> None:
    h4 = pd.date_range("2022-01-03", periods=6, freq="4h", tz="UTC")
    features = load_features_from_directory(FIXTURE_DIR, feature_names=("dxy", "vix"))
    aligned = align_features_to_h4(h4, features)
    assert aligned.loc[h4[0], "dxy"] == 96.5
    # before second daily observation, still first value
    assert aligned.loc[h4[1], "dxy"] == 96.5
    assert aligned.loc[h4[-1], "dxy"] == 96.5


def test_availability_report_fixture_only() -> None:
    report = build_availability_report(REPO_ROOT, fixture_dir=FIXTURE_DIR, data_dir=REPO_ROOT / "data" / "nope")
    assert report["strategy_evidence"] is False
    assert report["status"] in ("FIXTURE_ONLY", "BLOCKED_LOCAL_DATA_REQUIRED", "REAL_DATA_AVAILABLE")

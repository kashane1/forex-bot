"""Tests for cross-asset feature loader."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from research.cross_asset_features.alignment import (
    align_features_to_h4_with_availability,
    align_wide_frame_to_h4,
    availability_index_for_series,
)
from research.cross_asset_features.loader import (
    align_features_to_h4,
    build_availability_report,
    load_feature_csv,
    load_features_from_directory,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "cross_asset"


def test_load_feature_csv_dxy_legacy() -> None:
    fs = load_feature_csv(FIXTURE_DIR / "dxy.csv", "dxy")
    assert len(fs.frame) == 5
    assert fs.name == "broad_usd_index"


def test_align_features_no_lookahead() -> None:
    h4 = pd.date_range("2022-01-03", periods=6, freq="4h", tz="UTC")
    features = load_features_from_directory(FIXTURE_DIR, feature_names=("dxy", "vix"))
    aligned = align_features_to_h4(h4, features)
    assert aligned.loc[h4[0], "dxy"] == 96.5
    assert aligned.loc[h4[1], "dxy"] == 96.5
    assert aligned.loc[h4[-1], "dxy"] == 96.5


def test_availability_alignment_no_same_day_leak() -> None:
    h4 = pd.date_range("2022-01-03 04:00", periods=8, freq="4h", tz="UTC")
    features = load_features_from_directory(FIXTURE_DIR, feature_names=("dxy",))
    fs = features["broad_usd_index"]
    avail = availability_index_for_series(fs)
    assert avail.index.min() == pd.Timestamp("2022-01-04", tz="UTC")
    aligned = align_features_to_h4_with_availability(h4, features)
    assert pd.isna(aligned.loc[h4[0], "broad_usd_index"])
    assert aligned.loc[h4[-1], "broad_usd_index"] == 96.5


def test_availability_report_fixture_only() -> None:
    report = build_availability_report(REPO_ROOT, fixture_dir=FIXTURE_DIR, data_dir=REPO_ROOT / "data" / "nope")
    assert report["strategy_evidence"] is False
    assert report["status"] in ("FIXTURE_ONLY", "BLOCKED_LOCAL_DATA_REQUIRED", "REAL_DATA_AVAILABLE")


def test_reject_future_dated_rows(tmp_path: Path) -> None:
    bad = tmp_path / "vix.csv"
    bad.write_text("date,close\n2025-01-01,20\n2026-01-01,25\n", encoding="utf-8")
    with pytest.raises(ValueError, match="future-dated"):
        load_feature_csv(bad, "vix", end_date=pd.Timestamp("2025-06-01", tz="UTC"))


def test_reject_duplicate_dates_keep_last(tmp_path: Path) -> None:
    dup = tmp_path / "vix.csv"
    dup.write_text("date,close\n2022-01-03,20\n2022-01-03,21\n", encoding="utf-8")
    fs = load_feature_csv(dup, "vix")
    assert len(fs.frame) == 1
    assert float(fs.frame.iloc[0, 0]) == 21.0


def test_wide_alignment_friday_close() -> None:
    wide = pd.DataFrame(
        {"broad_usd_index": [96.0, 97.0]},
        index=pd.to_datetime(["2022-01-07", "2022-01-10"], utc=True),
    )
    h4 = pd.date_range("2022-01-07 20:00", periods=3, freq="4h", tz="UTC")
    aligned = align_wide_frame_to_h4(h4, wide)
    assert pd.isna(aligned.iloc[0]["broad_usd_index"])
    assert aligned.iloc[-1]["broad_usd_index"] == 96.0

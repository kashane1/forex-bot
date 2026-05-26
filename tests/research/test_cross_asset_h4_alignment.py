"""Tests for H4 alignment with availability timestamps."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from research.cross_asset_features.alignment import (
    align_wide_frame_to_h4,
    build_h4_alignment_report,
    flag_stale_aligned_values,
    write_h4_alignment_outputs,
)
from research.cross_asset_features.normalizer import normalize_from_sources

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_no_future_leakage_on_weekend() -> None:
    wide = pd.DataFrame({"vix": [18.0]}, index=pd.to_datetime(["2022-01-07"], utc=True))
    h4 = pd.date_range("2022-01-07 20:00", periods=2, freq="4h", tz="UTC")
    aligned = align_wide_frame_to_h4(h4, wide)
    assert pd.isna(aligned.iloc[0]["vix"])
    assert aligned.iloc[-1]["vix"] == 18.0


def test_stale_flags_beyond_max_staleness() -> None:
    wide = pd.DataFrame(
        {"vix": [18.0, 19.0]},
        index=pd.to_datetime(["2022-01-03", "2022-01-20"], utc=True),
    )
    h4 = pd.date_range("2022-01-10", periods=1, freq="4h", tz="UTC")
    aligned = align_wide_frame_to_h4(h4, wide)
    stale = flag_stale_aligned_values(aligned, wide)
    assert bool(stale.iloc[0]["vix_stale"]) is True


def test_h4_alignment_report_structure() -> None:
    h4 = pd.date_range("2022-01-04", periods=4, freq="4h", tz="UTC")
    wide, _, _ = normalize_from_sources(REPO_ROOT, data_dir=REPO_ROOT / "data" / "nope")
    aligned = align_wide_frame_to_h4(h4, wide)
    stale = flag_stale_aligned_values(aligned, wide)
    report = build_h4_alignment_report(h4, aligned, stale)
    assert report["strategy_evidence"] is False
    assert "feature_coverage" in report


def test_write_h4_alignment_outputs(tmp_path: Path) -> None:
    h4 = pd.date_range("2022-01-04", periods=8, freq="4h", tz="UTC")
    wide, _, _ = normalize_from_sources(REPO_ROOT, data_dir=REPO_ROOT / "data" / "nope")
    paths = write_h4_alignment_outputs(REPO_ROOT, h4, wide, tmp_path, sample_rows=4)
    assert paths["report"].is_file()
    assert paths["sample"].is_file()

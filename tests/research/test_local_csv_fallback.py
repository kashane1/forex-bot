"""Tests for local CSV fallback scanning."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from research.cross_asset_features.local_csv_fallback import (
    scan_local_csv_directory,
    validate_local_csv,
    write_local_csv_fallback_status,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "cross_asset"


def test_scan_missing_directory(tmp_path: Path) -> None:
    report = scan_local_csv_directory(tmp_path / "nonexistent")
    assert report["directory_exists"] is False
    assert report["files_present_count"] == 0


def test_validate_fixture_csv(tmp_path: Path) -> None:
    src = FIXTURE_DIR / "vix.csv"
    dest = tmp_path / "vix.csv"
    dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    validate_local_csv(dest, "vix")


def test_reject_future_date(tmp_path: Path) -> None:
    bad = tmp_path / "vix.csv"
    bad.write_text("date,close\n2026-01-01,20\n", encoding="utf-8")
    with pytest.raises(ValueError, match="future-dated"):
        validate_local_csv(bad, "vix", end_date=pd.Timestamp("2025-01-01", tz="UTC"))


def test_reject_missing_column(tmp_path: Path) -> None:
    bad = tmp_path / "vix.csv"
    bad.write_text("date,not_value\n2022-01-03,20\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing"):
        validate_local_csv(bad, "vix")


def test_duplicate_keep_last(tmp_path: Path) -> None:
    dup = tmp_path / "vix.csv"
    dup.write_text("date,close\n2022-01-03,20\n2022-01-03,21\n", encoding="utf-8")
    validate_local_csv(dup, "vix")


def test_write_local_csv_fallback_status(tmp_path: Path) -> None:
    out = write_local_csv_fallback_status(REPO_ROOT, tmp_path / "status.json")
    assert out.is_file()
    assert out.read_text(encoding="utf-8").startswith("{")

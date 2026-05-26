"""Local CSV fallback scanning and validation — no invented data."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from research.cross_asset_features.loader import load_feature_csv, load_features_from_directory
from research.cross_asset_features.schema import (
    CANONICAL_FEATURE_IDS,
    FEATURE_FILES,
    LEGACY_FEATURE_FILES,
    load_source_registry,
)


def list_expected_local_csv_paths(data_dir: Path) -> dict[str, list[str]]:
    expected: dict[str, list[str]] = {}
    for fid in CANONICAL_FEATURE_IDS:
        if fid == "us_10y_minus_2y" or fid.endswith("_1d_change") or fid.endswith("_1d_return"):
            continue
        names = []
        if fid in FEATURE_FILES:
            names.append(FEATURE_FILES[fid])
        legacy = LEGACY_FEATURE_FILES.get(fid)
        if legacy:
            names.append(legacy)
        if names:
            expected[fid] = names
    return expected


def scan_local_csv_directory(data_dir: Path) -> dict[str, Any]:
    registry = load_source_registry()
    expected = list_expected_local_csv_paths(data_dir)
    files_found: dict[str, str | None] = {}
    for fid, candidates in expected.items():
        found = next((data_dir / name for name in candidates if (data_dir / name).is_file()), None)
        files_found[fid] = str(found) if found else None
    loaded: dict[str, Any] = {}
    errors: dict[str, str] = {}
    if data_dir.is_dir():
        for name, path_str in files_found.items():
            if path_str is None:
                continue
            try:
                fs = load_feature_csv(Path(path_str), name, source="local_csv")
                loaded[name] = {
                    "rows": len(fs.frame),
                    "first": str(fs.frame.index.min()),
                    "last": str(fs.frame.index.max()),
                }
            except (ValueError, FileNotFoundError) as exc:
                errors[name] = str(exc)
    present_count = sum(1 for p in files_found.values() if p is not None)
    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "data_dir": str(data_dir),
        "directory_exists": data_dir.is_dir(),
        "files_expected": expected,
        "files_found": files_found,
        "loaded_summary": loaded,
        "validation_errors": errors,
        "files_present_count": present_count,
        "required_features_present": present_count >= 6,
        "gold_status": "MANUAL_CSV_REQUIRED",
        "registry_version": registry.get("version"),
    }


def validate_local_csv(path: Path, feature_id: str, *, end_date: pd.Timestamp | None = None) -> None:
    load_feature_csv(path, feature_id, end_date=end_date, source="local_csv")


def write_local_csv_fallback_status(repo_root: Path, output_path: Path | None = None) -> Path:
    data_dir = repo_root / "data" / "external_features"
    report = scan_local_csv_directory(data_dir)
    out = output_path or repo_root / "research" / "cross_asset_features" / "local_csv_fallback_status.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return out


def load_local_csv_features(
    data_dir: Path,
    *,
    end_date: pd.Timestamp | None = None,
) -> dict[str, Any]:
    if not data_dir.is_dir():
        return {}
    return load_features_from_directory(data_dir, end_date=end_date, source="local_csv")

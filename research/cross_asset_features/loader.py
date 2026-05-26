"""Load and align cross-asset feature CSVs — read-only, no broker APIs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from research.cross_asset_features.schema import FEATURE_FILES, FEATURE_SCHEMA, FeatureSeries


def load_feature_csv(path: Path, feature_name: str) -> FeatureSeries:
    if feature_name not in FEATURE_SCHEMA:
        raise ValueError(f"unknown feature: {feature_name}")
    meta = FEATURE_SCHEMA[feature_name]
    if not path.is_file():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    ts_col = meta["timestamp_col"]
    val_col = meta["value_col"]
    if ts_col not in df.columns or val_col not in df.columns:
        raise ValueError(f"{path}: missing {ts_col} or {val_col}")
    df[ts_col] = pd.to_datetime(df[ts_col], utc=True)
    df = df.sort_values(ts_col).drop_duplicates(subset=[ts_col], keep="last")
    out = df.set_index(ts_col)[[val_col]].rename(columns={val_col: feature_name})
    return FeatureSeries(
        name=feature_name,
        frame=out,
        source_path=str(path),
        freq=meta["freq"],
    )


def load_features_from_directory(
    directory: Path,
    *,
    feature_names: tuple[str, ...] | None = None,
) -> dict[str, FeatureSeries]:
    names = feature_names or tuple(FEATURE_SCHEMA.keys())
    loaded: dict[str, FeatureSeries] = {}
    for name in names:
        path = directory / FEATURE_FILES[name]
        if path.is_file():
            loaded[name] = load_feature_csv(path, name)
    return loaded


def align_features_to_h4(
    h4_index: pd.DatetimeIndex,
    features: dict[str, FeatureSeries],
) -> pd.DataFrame:
    """Forward-fill daily/weekly features onto H4 bars — no lookahead.

    Rule: for each H4 timestamp T, use the latest feature observation
    with timestamp <= T. Never backfill from the future.
    """
    if h4_index.tz is None:
        h4_index = h4_index.tz_localize("UTC")
    else:
        h4_index = h4_index.tz_convert("UTC")
    aligned = pd.DataFrame(index=h4_index.sort_values())
    for name, series in features.items():
        s = series.frame[series.name].sort_index()
        if s.index.tz is None:
            s.index = s.index.tz_localize("UTC")
        else:
            s.index = s.index.tz_convert("UTC")
        merged = s.reindex(h4_index, method="ffill")
        aligned[name] = merged
    return aligned


def build_availability_report(
    repo_root: Path,
    *,
    data_dir: Path | None = None,
    fixture_dir: Path | None = None,
) -> dict[str, object]:
    data_dir = data_dir or repo_root / "data" / "external_features"
    fixture_dir = fixture_dir or repo_root / "tests" / "fixtures" / "cross_asset"
    report: dict[str, object] = {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "data_dir": str(data_dir),
        "fixture_dir": str(fixture_dir),
        "features": {},
        "status": "BLOCKED_LOCAL_DATA_REQUIRED",
    }
    features_meta: dict[str, object] = {}
    any_real = False
    any_fixture = False
    for name in FEATURE_SCHEMA:
        real_path = data_dir / FEATURE_FILES[name]
        fix_path = fixture_dir / FEATURE_FILES[name]
        entry: dict[str, object] = {
            "real_path": str(real_path),
            "real_available": real_path.is_file(),
            "fixture_path": str(fix_path),
            "fixture_available": fix_path.is_file(),
        }
        if real_path.is_file():
            any_real = True
            fs = load_feature_csv(real_path, name)
            entry["rows"] = len(fs.frame)
            entry["first"] = str(fs.frame.index.min())
            entry["last"] = str(fs.frame.index.max())
        elif fix_path.is_file():
            any_fixture = True
            fs = load_feature_csv(fix_path, name)
            entry["fixture_rows"] = len(fs.frame)
        features_meta[name] = entry
    report["features"] = features_meta
    if any_real:
        report["status"] = "REAL_DATA_PARTIAL" if len(features_meta) > sum(
            1 for v in features_meta.values() if v["real_available"]  # type: ignore[index]
        ) else "REAL_DATA_AVAILABLE"
    elif any_fixture:
        report["status"] = "FIXTURE_ONLY"
    return report


def write_availability_report(repo_root: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report = build_availability_report(repo_root)
    out = output_dir / "feature_availability_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return out

"""Load and align cross-asset feature CSVs — read-only, no broker APIs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from research.cross_asset_features.schema import (
    FEATURE_FILES,
    FEATURE_SCHEMA,
    LEGACY_CSV_COLUMNS,
    LEGACY_FEATURE_ALIASES,
    LEGACY_FEATURE_FILES,
    FeatureSeries,
    resolve_feature_id,
)


def _resolve_csv_columns(feature_name: str, df: pd.DataFrame) -> tuple[str, str]:
    canonical = resolve_feature_id(feature_name)
    meta = FEATURE_SCHEMA.get(canonical)
    if meta is None:
        raise ValueError(f"unknown feature: {feature_name}")
    ts_col = meta["timestamp_col"]
    val_col = meta["value_col"]
    if ts_col in df.columns and val_col in df.columns:
        return ts_col, val_col
    legacy = LEGACY_CSV_COLUMNS.get(canonical)
    if legacy and legacy["timestamp_col"] in df.columns and legacy["value_col"] in df.columns:
        return legacy["timestamp_col"], legacy["value_col"]
    raise ValueError(f"{feature_name}: missing timestamp/value columns")


def load_feature_csv(
    path: Path,
    feature_name: str,
    *,
    end_date: pd.Timestamp | None = None,
    source: str = "local_csv",
) -> FeatureSeries:
    canonical = resolve_feature_id(feature_name)
    if canonical not in FEATURE_SCHEMA:
        raise ValueError(f"unknown feature: {feature_name}")
    meta = FEATURE_SCHEMA[canonical]
    if not path.is_file():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    ts_col, val_col = _resolve_csv_columns(feature_name, df)
    df[ts_col] = pd.to_datetime(df[ts_col], utc=True)
    if end_date is not None:
        end = end_date if end_date.tzinfo else end_date.tz_localize("UTC")
        future = df[ts_col] > end
        if future.any():
            raise ValueError(f"{path}: contains {int(future.sum())} future-dated row(s) vs end_date")
    if not df[ts_col].is_monotonic_increasing:
        df = df.sort_values(ts_col)
        if not df[ts_col].is_monotonic_increasing:
            raise ValueError(f"{path}: non-monotonic dates after sort")
    df = df.sort_values(ts_col).drop_duplicates(subset=[ts_col], keep="last")
    out = df.set_index(ts_col)[[val_col]].rename(columns={val_col: canonical})
    return FeatureSeries(
        name=canonical,
        frame=out,
        source_path=str(path),
        freq=meta["freq"],
        source=source,
    )


def _candidate_paths(directory: Path, canonical: str) -> list[Path]:
    paths: list[Path] = []
    if canonical in FEATURE_FILES:
        paths.append(directory / FEATURE_FILES[canonical])
    legacy = LEGACY_FEATURE_FILES.get(canonical)
    if legacy:
        paths.append(directory / legacy)
    return paths


def load_features_from_directory(
    directory: Path,
    *,
    feature_names: tuple[str, ...] | None = None,
    end_date: pd.Timestamp | None = None,
    source: str = "local_csv",
) -> dict[str, FeatureSeries]:
    names = feature_names or tuple(FEATURE_SCHEMA.keys())
    loaded: dict[str, FeatureSeries] = {}
    for name in names:
        canonical = resolve_feature_id(name)
        if canonical in loaded:
            continue
        for path in _candidate_paths(directory, canonical):
            if path.is_file():
                loaded[canonical] = load_feature_csv(
                    path,
                    canonical,
                    end_date=end_date,
                    source=source,
                )
                break
    return loaded


def align_features_to_h4(
    h4_index: pd.DatetimeIndex,
    features: dict[str, FeatureSeries],
) -> pd.DataFrame:
    """Forward-fill daily/weekly features onto H4 bars — legacy simple alignment.

    Uses observation timestamp directly (<= T). Prefer
    ``alignment.align_features_to_h4_with_availability`` for production paths.
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
        # legacy alias columns for downstream diagnostics
        for legacy, canon in LEGACY_FEATURE_ALIASES.items():
            if canon == series.name:
                aligned[legacy] = merged
    return aligned


def build_availability_report(
    repo_root: Path,
    *,
    data_dir: Path | None = None,
    fixture_dir: Path | None = None,
    normalized_manifest: Path | None = None,
) -> dict[str, object]:
    data_dir = data_dir or repo_root / "data" / "external_features"
    fixture_dir = fixture_dir or repo_root / "tests" / "fixtures" / "cross_asset"
    manifest_path = normalized_manifest or (
        repo_root / "research" / "cross_asset_features" / "normalized_features_manifest.json"
    )
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
    any_normalized = manifest_path.is_file()
    registry_names = [
        "broad_usd_index",
        "us_2y_yield",
        "us_10y_yield",
        "vix",
        "sp500",
        "oil_wti",
        "nasdaq_composite",
        "gold",
        "cot_eur_net",
    ]
    for name in registry_names:
        real_path = _candidate_paths(data_dir, name)
        fix_paths = _candidate_paths(fixture_dir, name)
        real_file = next((p for p in real_path if p.is_file()), None)
        fix_file = next((p for p in fix_paths if p.is_file()), None)
        entry: dict[str, object] = {
            "real_available": real_file is not None,
            "fixture_available": fix_file is not None,
        }
        if real_file:
            any_real = True
            fs = load_feature_csv(real_file, name)
            entry["real_path"] = str(real_file)
            entry["rows"] = len(fs.frame)
            entry["first"] = str(fs.frame.index.min())
            entry["last"] = str(fs.frame.index.max())
        elif fix_file:
            any_fixture = True
            entry["fixture_path"] = str(fix_file)
            fs = load_feature_csv(fix_file, name)
            entry["fixture_rows"] = len(fs.frame)
        features_meta[name] = entry
    report["features"] = features_meta
    report["normalized_manifest_present"] = any_normalized
    if any_normalized:
        report["status"] = "REAL_DATA_NORMALIZED"
    elif any_real:
        real_count = sum(1 for v in features_meta.values() if v["real_available"])  # type: ignore[index]
        report["status"] = "REAL_DATA_PARTIAL" if real_count < len(registry_names) else "REAL_DATA_AVAILABLE"
    elif any_fixture:
        report["status"] = "FIXTURE_ONLY"
    return report


def write_availability_report(repo_root: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report = build_availability_report(repo_root)
    out = output_dir / "feature_availability_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return out

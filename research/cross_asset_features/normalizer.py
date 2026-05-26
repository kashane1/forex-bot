"""Normalize cross-asset features and compute derived series."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from research.cross_asset_features.fred import fetch_all_fred_features, get_fred_api_key
from research.cross_asset_features.loader import load_features_from_directory
from research.cross_asset_features.schema import load_source_registry, resolve_feature_id


def observation_to_availability_ts(obs_date: pd.Timestamp, freq: str = "daily") -> pd.Timestamp:
    obs = obs_date if obs_date.tzinfo else obs_date.tz_localize("UTC")
    if freq == "weekly":
        # conservative: report available following Friday close lag handled upstream
        return obs + pd.Timedelta(days=3)
    return obs.normalize() + pd.Timedelta(days=1)


def compute_derived_features(wide: pd.DataFrame) -> pd.DataFrame:
    out = wide.copy()
    if "us_10y_yield" in out.columns and "us_2y_yield" in out.columns:
        out["us_10y_minus_2y"] = out["us_10y_yield"] - out["us_2y_yield"]
    if "broad_usd_index" in out.columns:
        out["broad_usd_index_1d_change"] = out["broad_usd_index"].pct_change(fill_method=None) * 100.0
    if "vix" in out.columns:
        out["vix_1d_change"] = out["vix"].diff()
    if "sp500" in out.columns:
        out["sp500_1d_return"] = out["sp500"].pct_change(fill_method=None) * 100.0
    if "oil_wti" in out.columns:
        out["oil_wti_1d_return"] = out["oil_wti"].pct_change(fill_method=None) * 100.0
    return out


def series_dict_to_wide(features: dict[str, Any]) -> pd.DataFrame:
    frames: list[pd.Series] = []
    for name, fs in features.items():
        canonical = resolve_feature_id(name)
        s = fs.frame[fs.name if hasattr(fs, "name") else canonical].copy()
        s.name = canonical
        frames.append(s)
    if not frames:
        return pd.DataFrame()
    wide = pd.concat(frames, axis=1).sort_index()
    return wide


def build_feature_quality_report(wide: pd.DataFrame, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = registry or load_source_registry()
    staleness_map = {
        e["feature_id"]: int(e["max_staleness_days"])
        for e in registry["features"]
        if e.get("max_staleness_days") is not None
    }
    per_feature: dict[str, Any] = {}
    stale_flags: dict[str, int] = {}
    for col in wide.columns:
        series = wide[col]
        valid = series.dropna()
        max_stale = staleness_map.get(col, 5)
        stale_count = 0
        if len(valid) >= 2:
            gaps = valid.index.to_series().diff().dt.days.fillna(0)
            stale_count = int((gaps > max_stale).sum())
        stale_flags[col] = stale_count
        per_feature[col] = {
            "rows_total": len(series),
            "rows_non_null": int(valid.shape[0]),
            "first": str(valid.index.min()) if len(valid) else None,
            "last": str(valid.index.max()) if len(valid) else None,
            "max_staleness_days": max_stale,
            "stale_gap_count": stale_count,
        }
    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "feature_count": len(per_feature),
        "features": per_feature,
        "stale_gap_counts": stale_flags,
    }


def build_enhanced_manifest(
    wide: pd.DataFrame,
    *,
    status: str,
    fred_status: str,
    api_key_present: bool,
    observation_start: str,
    observation_end: str | None,
    h4_window: dict[str, object] | None = None,
    allow_fixture_fallback: bool,
) -> dict[str, Any]:
    registry = load_source_registry()
    feature_details: dict[str, Any] = {}
    for entry in registry["features"]:
        fid = entry["feature_id"]
        if fid not in wide.columns:
            continue
        series = wide[fid]
        non_null = int(series.notna().sum())
        total = len(series)
        feature_details[fid] = {
            "source_type": entry.get("source_type"),
            "source_series_id": entry.get("source_series_id"),
            "rows_total": total,
            "missing_count": total - non_null,
            "missing_rate_pct": round(100.0 * (total - non_null) / total, 4) if total else None,
            "depends_on": entry.get("depends_on"),
        }
    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "status": status,
        "fred_status": fred_status,
        "fred_api_key_present": api_key_present,
        "allow_fixture_fallback": allow_fixture_fallback,
        "observation_start": observation_start,
        "observation_end": observation_end,
        "h4_window": h4_window,
        "columns": list(wide.columns),
        "row_count": len(wide),
        "first_date": str(wide.index.min()) if len(wide) else None,
        "last_date": str(wide.index.max()) if len(wide) else None,
        "features": feature_details,
        "ingestion_timestamp_utc": datetime.now(tz=UTC).isoformat(),
    }


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("strategy_evidence") is not False:
        errors.append("strategy_evidence must be false")
    for key in ("status", "observation_start", "columns", "row_count"):
        if key not in manifest:
            errors.append(f"missing manifest key: {key}")
    return errors


def normalize_from_sources(
    repo_root: Path,
    *,
    data_dir: Path | None = None,
    cache_dir: Path | None = None,
    observation_start: str = "2019-01-01",
    observation_end: str | None = None,
    allow_fixture_fallback: bool = True,
    h4_window: dict[str, object] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any], str]:
    data_dir = data_dir or repo_root / "data" / "external_features"
    cache_dir = cache_dir or data_dir / ".fred_cache"
    status = "LOCAL_OR_FIXTURE"
    wide = pd.DataFrame()

    api_key = get_fred_api_key()
    fred_status = "SKIPPED_NO_KEY"
    if api_key:
        _, fred_status = fetch_all_fred_features(
            cache_dir=cache_dir,
            observation_start=observation_start,
            observation_end=observation_end,
            api_key=api_key,
        )
        if fred_status == "OK":
            status = "FRED"
            fred_frames: list[pd.Series] = []
            for cache_file in sorted(cache_dir.glob("*.json")):
                payload = json.loads(cache_file.read_text(encoding="utf-8"))
                fid = payload.get("feature_id")
                rows = payload.get("data", [])
                if not fid or not rows:
                    continue
                df = pd.DataFrame(rows)
                df["date"] = pd.to_datetime(df["date"], utc=True)
                s = df.set_index("date")["value"].rename(fid)
                fred_frames.append(s)
            if fred_frames:
                wide = pd.concat(fred_frames, axis=1).sort_index()

    local = load_features_from_directory(data_dir)
    if local:
        local_wide = series_dict_to_wide(local)
        wide = local_wide if wide.empty else wide.combine_first(local_wide)
        status = "MIXED" if status == "FRED" else "LOCAL_CSV"

    if wide.empty and allow_fixture_fallback:
        fixture_dir = repo_root / "tests" / "fixtures" / "cross_asset"
        fixtures = load_features_from_directory(fixture_dir, source="fixture")
        wide = series_dict_to_wide(fixtures)
        status = "FIXTURE_ONLY"
    elif wide.empty:
        status = "BLOCKED_FULL_WINDOW"

    wide = compute_derived_features(wide)
    manifest = build_enhanced_manifest(
        wide,
        status=status,
        fred_status=fred_status,
        api_key_present=api_key is not None,
        observation_start=observation_start,
        observation_end=observation_end,
        h4_window=h4_window,
        allow_fixture_fallback=allow_fixture_fallback,
    )
    return wide, manifest, status


def normalize_from_sources_legacy(
    repo_root: Path,
    **kwargs: Any,
) -> tuple[pd.DataFrame, dict[str, Any], str]:
    return normalize_from_sources(repo_root, allow_fixture_fallback=True, **kwargs)


def write_normalized_outputs(
    repo_root: Path,
    output_dir: Path,
    *,
    observation_start: str = "2019-01-01",
    observation_end: str | None = None,
    allow_fixture_fallback: bool = True,
    h4_window: dict[str, object] | None = None,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    wide, manifest, _ = normalize_from_sources(
        repo_root,
        observation_start=observation_start,
        observation_end=observation_end,
        allow_fixture_fallback=allow_fixture_fallback,
        h4_window=h4_window,
    )
    csv_path = output_dir / "normalized_features.csv"
    if len(wide) > 0:
        wide.to_csv(csv_path, index_label="date")
    elif csv_path.is_file():
        manifest["normalized_csv_note"] = "existing file retained; full-window ingest blocked"
    else:
        wide.to_csv(csv_path, index_label="date")
    manifest_path = output_dir / "normalized_features_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    quality = build_feature_quality_report(wide) if len(wide) else {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "feature_count": 0,
        "features": {},
        "stale_gap_counts": {},
        "note": "full-window ingest blocked; no quality metrics computed",
    }
    quality_path = output_dir / "feature_quality_report.json"
    quality_path.write_text(json.dumps(quality, indent=2) + "\n", encoding="utf-8")
    return {
        "csv": csv_path,
        "manifest": manifest_path,
        "quality": quality_path,
    }

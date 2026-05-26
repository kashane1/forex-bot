"""H4 alignment with explicit availability timestamps — no lookahead."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from research.cross_asset_features.loader import load_feature_csv
from research.cross_asset_features.normalizer import observation_to_availability_ts
from research.cross_asset_features.schema import (
    FEATURE_SCHEMA,
    LEGACY_FEATURE_ALIASES,
    FeatureSeries,
    load_source_registry,
    resolve_feature_id,
)


def availability_index_for_series(series: FeatureSeries) -> pd.Series:
    freq = series.freq
    idx = series.frame.index
    if idx.tz is None:
        idx = idx.tz_localize("UTC")
    else:
        idx = idx.tz_convert("UTC")
    avail = pd.DatetimeIndex([observation_to_availability_ts(ts, freq=freq) for ts in idx])
    values = series.frame[series.name].values
    return pd.Series(values, index=avail, name=series.name).sort_index()


def align_features_to_h4_with_availability(
    h4_index: pd.DatetimeIndex,
    features: dict[str, FeatureSeries],
) -> pd.DataFrame:
    """Align using availability timestamps — no same-day close leakage."""
    if h4_index.tz is None:
        h4_index = h4_index.tz_localize("UTC")
    else:
        h4_index = h4_index.tz_convert("UTC")
    h4_index = h4_index.sort_values()
    aligned = pd.DataFrame(index=h4_index)
    for _name, series in features.items():
        avail = availability_index_for_series(series)
        merged = avail.reindex(h4_index, method="ffill")
        aligned[series.name] = merged
        for legacy, canon in LEGACY_FEATURE_ALIASES.items():
            if canon == series.name:
                aligned[legacy] = merged
    return aligned


def align_wide_frame_to_h4(
    h4_index: pd.DatetimeIndex,
    wide: pd.DataFrame,
    *,
    freq: str = "daily",
) -> pd.DataFrame:
    if h4_index.tz is None:
        h4_index = h4_index.tz_localize("UTC")
    else:
        h4_index = h4_index.tz_convert("UTC")
    h4_index = h4_index.sort_values()
    aligned = pd.DataFrame(index=h4_index)
    for col in wide.columns:
        canonical = resolve_feature_id(col)
        col_freq = FEATURE_SCHEMA.get(canonical, {}).get("freq", freq)
        s = wide[col].dropna()
        if s.empty:
            aligned[canonical] = pd.NA
            continue
        idx = s.index
        if idx.tz is None:
            idx = idx.tz_localize("UTC")
        avail = pd.DatetimeIndex([observation_to_availability_ts(ts, freq=col_freq) for ts in idx])
        avail_series = pd.Series(s.values, index=avail, name=canonical).sort_index()
        merged = avail_series.reindex(h4_index, method="ffill")
        aligned[canonical] = merged
        for legacy, canon in LEGACY_FEATURE_ALIASES.items():
            if canon == canonical:
                aligned[legacy] = merged
    return aligned


def flag_stale_aligned_values(
    aligned: pd.DataFrame,
    wide: pd.DataFrame,
    registry: dict[str, Any] | None = None,
) -> pd.DataFrame:
    registry = registry or load_source_registry()
    staleness = {
        e["feature_id"]: int(e["max_staleness_days"])
        for e in registry["features"]
        if e.get("max_staleness_days") is not None
    }
    flags = pd.DataFrame(index=aligned.index)
    for col in aligned.columns:
        canonical = resolve_feature_id(col)
        if canonical not in wide.columns:
            continue
        max_days = staleness.get(canonical, 5)
        source = wide[canonical].dropna()
        if source.empty:
            flags[f"{canonical}_stale"] = True
            continue
        last_obs = source.index.to_series()
        stale_col: list[bool] = []
        for ts in aligned.index:
            prior = last_obs[last_obs <= ts]
            if prior.empty:
                stale_col.append(True)
                continue
            gap = (ts.normalize() - prior.iloc[-1].normalize()).days
            stale_col.append(gap > max_days)
        flags[f"{canonical}_stale"] = stale_col
    return flags


def build_h4_alignment_report(
    h4_index: pd.DatetimeIndex,
    aligned: pd.DataFrame,
    stale_flags: pd.DataFrame,
) -> dict[str, Any]:
    coverage: dict[str, Any] = {}
    coverage_by_year: dict[str, dict[str, float]] = {}
    years = sorted({ts.year for ts in h4_index})
    for col in aligned.columns:
        if col.endswith("_stale") or col in LEGACY_FEATURE_ALIASES:
            continue
        series = aligned[col]
        non_null = series.notna()
        coverage[col] = {
            "bars_total": len(series),
            "bars_with_value": int(non_null.sum()),
            "coverage_pct": round(100.0 * float(non_null.mean()), 2) if len(series) else 0.0,
            "missing_rate_pct": round(100.0 * float((~non_null).mean()), 2) if len(series) else 0.0,
            "stale_rate_pct": round(
                100.0 * float(stale_flags.get(f"{col}_stale", pd.Series(False, index=series.index)).mean()),
                2,
            )
            if len(series)
            else 0.0,
        }
        for year in years:
            mask = h4_index.year == year
            if not mask.any():
                continue
            year_series = series.loc[mask]
            coverage_by_year.setdefault(str(year), {})[col] = round(
                100.0 * float(year_series.notna().mean()),
                2,
            )
    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "h4_bars": len(h4_index),
        "first_bar": str(h4_index.min()) if len(h4_index) else None,
        "last_bar": str(h4_index.max()) if len(h4_index) else None,
        "feature_coverage": coverage,
        "coverage_by_year": coverage_by_year,
    }


def load_normalized_wide(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df["date"] = pd.to_datetime(df["date"], utc=True)
    return df.set_index("date").sort_index()


def write_h4_alignment_outputs(
    repo_root: Path,
    h4_index: pd.DatetimeIndex,
    wide: pd.DataFrame,
    output_dir: Path,
    *,
    sample_rows: int = 50,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    aligned = align_wide_frame_to_h4(h4_index, wide)
    stale = flag_stale_aligned_values(aligned, wide)
    report = build_h4_alignment_report(h4_index, aligned, stale)
    report_path = output_dir / "h4_aligned_feature_availability.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    sample = aligned.head(sample_rows)
    sample_path = output_dir / "h4_aligned_feature_sample.csv"
    sample.to_csv(sample_path, index_label="bar_time")
    return {"report": report_path, "sample": sample_path}


def load_feature_series_from_path(path: Path, feature_name: str) -> FeatureSeries:
    return load_feature_csv(path, feature_name)

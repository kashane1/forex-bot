"""Cross-asset feature CSV schema and source registry validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import pandas as pd

FeatureName = Literal[
    "broad_usd_index",
    "us_2y_yield",
    "us_10y_yield",
    "us_10y_minus_2y",
    "vix",
    "sp500",
    "oil_wti",
    "nasdaq_composite",
    "gold",
    "broad_usd_index_1d_change",
    "vix_1d_change",
    "sp500_1d_return",
    "oil_wti_1d_return",
    "cot_eur_net",
    # legacy aliases resolved at load time
    "dxy",
    "us2y",
    "us10y",
    "oil",
    "nasdaq",
]

LEGACY_FEATURE_ALIASES: dict[str, str] = {
    "dxy": "broad_usd_index",
    "us2y": "us_2y_yield",
    "us10y": "us_10y_yield",
    "oil": "oil_wti",
    "nasdaq": "nasdaq_composite",
}

CANONICAL_FEATURE_IDS: tuple[str, ...] = (
    "broad_usd_index",
    "us_2y_yield",
    "us_10y_yield",
    "us_10y_minus_2y",
    "vix",
    "sp500",
    "oil_wti",
    "nasdaq_composite",
    "gold",
    "broad_usd_index_1d_change",
    "vix_1d_change",
    "sp500_1d_return",
    "oil_wti_1d_return",
    "cot_eur_net",
)

FEATURE_SCHEMA: dict[str, dict[str, str]] = {
    "broad_usd_index": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "us_2y_yield": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "us_10y_yield": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "us_10y_minus_2y": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "vix": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "sp500": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "oil_wti": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "nasdaq_composite": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "gold": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "broad_usd_index_1d_change": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "vix_1d_change": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "sp500_1d_return": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "oil_wti_1d_return": {"timestamp_col": "date", "value_col": "value", "freq": "daily"},
    "cot_eur_net": {"timestamp_col": "report_date", "value_col": "value", "freq": "weekly"},
}

# Legacy wide-format CSV column names accepted by local loader
LEGACY_CSV_COLUMNS: dict[str, dict[str, str]] = {
    "broad_usd_index": {"timestamp_col": "date", "value_col": "close"},
    "us_2y_yield": {"timestamp_col": "date", "value_col": "yield"},
    "us_10y_yield": {"timestamp_col": "date", "value_col": "yield"},
    "vix": {"timestamp_col": "date", "value_col": "close"},
    "sp500": {"timestamp_col": "date", "value_col": "close"},
    "oil_wti": {"timestamp_col": "date", "value_col": "close"},
    "nasdaq_composite": {"timestamp_col": "date", "value_col": "close"},
    "gold": {"timestamp_col": "date", "value_col": "close"},
    "cot_eur_net": {"timestamp_col": "report_date", "value_col": "net_position"},
}

FEATURE_FILES: dict[str, str] = {
    name: f"{name}.csv" for name in CANONICAL_FEATURE_IDS if name != "us_10y_minus_2y"
}

LEGACY_FEATURE_FILES: dict[str, str] = {
    "broad_usd_index": "dxy.csv",
    "us_2y_yield": "us2y.csv",
    "us_10y_yield": "us10y.csv",
    "oil_wti": "oil.csv",
    "nasdaq_composite": "nasdaq.csv",
}


def resolve_feature_id(name: str) -> str:
    return LEGACY_FEATURE_ALIASES.get(name, name)


@dataclass(frozen=True)
class FeatureSeries:
    name: str
    frame: pd.DataFrame
    source_path: str
    freq: str
    source: str = "unknown"
    as_of_date: pd.Timestamp | None = None
    ingestion_time: pd.Timestamp | None = None


@dataclass(frozen=True)
class NormalizedFeatureRow:
    """Long-format normalized feature observation."""

    date: pd.Timestamp
    feature_id: str
    value: float | None
    source: str
    as_of_date: pd.Timestamp | None = None
    release_date: pd.Timestamp | None = None
    ingestion_time: pd.Timestamp | None = None
    quality_flags: tuple[str, ...] = ()


def load_source_registry(path: Path | None = None) -> dict[str, Any]:
    path = path or Path(__file__).resolve().parent / "source_registry.json"
    return json.loads(path.read_text(encoding="utf-8"))


def validate_source_registry(registry: dict[str, Any] | None = None) -> list[str]:
    """Return validation errors; empty list means valid."""
    registry = registry or load_source_registry()
    errors: list[str] = []
    if registry.get("strategy_evidence") is not False:
        errors.append("source_registry.strategy_evidence must be false")
    features = registry.get("features", [])
    if not isinstance(features, list):
        return ["features must be a list"]
    ids: list[str] = []
    for entry in features:
        if not isinstance(entry, dict):
            errors.append("each feature entry must be an object")
            continue
        fid = entry.get("feature_id")
        if not fid:
            errors.append("feature missing feature_id")
            continue
        if fid in ids:
            errors.append(f"duplicate feature_id: {fid}")
        ids.append(str(fid))
        freq = entry.get("frequency")
        if freq in ("daily", "weekly") and entry.get("max_staleness_days") is None:
            errors.append(f"{fid}: max_staleness_days required for {freq} features")
        if entry.get("source_type") == "derived":
            deps = entry.get("depends_on")
            if not deps:
                errors.append(f"{fid}: derived feature must declare depends_on")
    required = [f["feature_id"] for f in features if f.get("required") is True]
    for req in (
        "broad_usd_index",
        "us_2y_yield",
        "us_10y_yield",
        "us_10y_minus_2y",
        "vix",
        "sp500",
        "oil_wti",
    ):
        if req not in required:
            errors.append(f"required feature missing from registry: {req}")
    return errors

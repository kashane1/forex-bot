"""Cross-asset feature CSV schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FeatureName = Literal[
    "dxy",
    "us2y",
    "us10y",
    "vix",
    "sp500",
    "nasdaq",
    "gold",
    "oil",
    "cot_eur_net",
]

FEATURE_SCHEMA: dict[str, dict[str, str]] = {
    "dxy": {"timestamp_col": "date", "value_col": "close", "freq": "daily"},
    "us2y": {"timestamp_col": "date", "value_col": "yield", "freq": "daily"},
    "us10y": {"timestamp_col": "date", "value_col": "yield", "freq": "daily"},
    "vix": {"timestamp_col": "date", "value_col": "close", "freq": "daily"},
    "sp500": {"timestamp_col": "date", "value_col": "close", "freq": "daily"},
    "nasdaq": {"timestamp_col": "date", "value_col": "close", "freq": "daily"},
    "gold": {"timestamp_col": "date", "value_col": "close", "freq": "daily"},
    "oil": {"timestamp_col": "date", "value_col": "close", "freq": "daily"},
    "cot_eur_net": {"timestamp_col": "report_date", "value_col": "net_position", "freq": "weekly"},
}

FEATURE_FILES: dict[str, str] = {name: f"{name}.csv" for name in FEATURE_SCHEMA}


@dataclass(frozen=True)
class FeatureSeries:
    name: str
    frame: pd.DataFrame  # noqa: F821 — pandas imported in loader
    source_path: str
    freq: str

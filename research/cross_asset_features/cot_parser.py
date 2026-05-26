"""Fixture-backed COT CSV parser — design stub, no live CFTC API."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from research.cross_asset_features.loader import load_feature_csv


def parse_cot_net_csv(path: Path, *, feature_id: str = "cot_eur_net") -> pd.DataFrame:
    """Parse weekly COT net positioning CSV into normalized long format."""
    series = load_feature_csv(path, feature_id, source="optional_cot")
    df = series.frame.reset_index()
    df = df.rename(columns={series.name: "value", df.columns[0]: "report_date"})
    df["feature_id"] = feature_id
    df["source"] = "optional_cot"
    df["release_date"] = pd.to_datetime(df["report_date"], utc=True) + pd.Timedelta(days=3)
    return df


COT_STATUS = "DESIGN_ONLY"

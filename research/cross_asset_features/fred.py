"""FRED API fetcher for cross-asset features — read-only, no secrets logged."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pandas as pd

from research.cross_asset_features.schema import load_source_registry

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"


@dataclass(frozen=True)
class FredFetchResult:
    status: str
    series_id: str
    feature_id: str
    rows: int
    cache_path: Path | None
    message: str = ""


def get_fred_api_key() -> str | None:
    key = os.environ.get("FRED_API_KEY")
    if key:
        return key
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        return None
    return os.environ.get("FRED_API_KEY") or None


def fred_series_for_feature(feature_id: str) -> str | None:
    registry = load_source_registry()
    for entry in registry["features"]:
        if entry["feature_id"] == feature_id and entry.get("source_type") == "fred_api":
            return entry.get("source_series_id")
    return None


def fetch_fred_observations(
    series_id: str,
    *,
    api_key: str,
    observation_start: str,
    observation_end: str | None = None,
    client: httpx.Client | None = None,
) -> pd.DataFrame:
    params: dict[str, str] = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": observation_start,
    }
    if observation_end:
        params["observation_end"] = observation_end
    owns_client = client is None
    client = client or httpx.Client(timeout=30.0)
    try:
        resp = client.get(FRED_OBSERVATIONS_URL, params=params)
        resp.raise_for_status()
        payload = resp.json()
    finally:
        if owns_client:
            client.close()
    obs = payload.get("observations", [])
    rows: list[dict[str, Any]] = []
    for item in obs:
        val_raw = item.get("value")
        if val_raw in (None, ".", ""):
            continue
        rows.append({"date": item["date"], "value": float(val_raw)})
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], utc=True)
    return df.sort_values("date").drop_duplicates(subset=["date"], keep="last")


def write_blocked_report(output_dir: Path, *, reason: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "status": "BLOCKED_AUTH_OR_LOCAL_CSV_REQUIRED",
        "reason": reason,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "remediation": (
            "Set FRED_API_KEY in environment or .env, or place local CSVs in "
            "data/external_features/ per research/cross_asset_features/feature_schema.md"
        ),
    }
    out = output_dir / "fred_fetch_blocked_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return out


def fetch_all_fred_features(
    *,
    cache_dir: Path,
    observation_start: str,
    observation_end: str | None = None,
    api_key: str | None = None,
    client: httpx.Client | None = None,
) -> tuple[list[FredFetchResult], str]:
    api_key = api_key or get_fred_api_key()
    if not api_key:
        return [], "BLOCKED_AUTH_OR_LOCAL_CSV_REQUIRED"
    cache_dir.mkdir(parents=True, exist_ok=True)
    registry = load_source_registry()
    results: list[FredFetchResult] = []
    owns_client = client is None
    client = client or httpx.Client(timeout=30.0)
    try:
        for entry in registry["features"]:
            if entry.get("source_type") != "fred_api":
                continue
            feature_id = entry["feature_id"]
            series_id = entry.get("source_series_id")
            if not series_id:
                continue
            try:
                df = fetch_fred_observations(
                    series_id,
                    api_key=api_key,
                    observation_start=observation_start,
                    observation_end=observation_end,
                    client=client,
                )
                cache_path = cache_dir / f"{series_id}.json"
                cache_path.write_text(
                    json.dumps(
                        {
                            "series_id": series_id,
                            "feature_id": feature_id,
                            "observation_start": observation_start,
                            "observation_end": observation_end,
                            "rows": len(df),
                            "data": df.assign(date=df["date"].astype(str)).to_dict(orient="records"),
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                results.append(
                    FredFetchResult(
                        status="ok",
                        series_id=series_id,
                        feature_id=feature_id,
                        rows=len(df),
                        cache_path=cache_path,
                    )
                )
            except httpx.HTTPError as exc:
                results.append(
                    FredFetchResult(
                        status="error",
                        series_id=series_id,
                        feature_id=feature_id,
                        rows=0,
                        cache_path=None,
                        message=str(exc),
                    )
                )
    finally:
        if owns_client:
            client.close()
    if any(r.status == "error" for r in results):
        return results, "PARTIAL_OR_ERROR"
    return results, "OK"

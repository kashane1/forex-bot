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

REQUIRED_FRED_FEATURES: tuple[str, ...] = (
    "broad_usd_index",
    "us_2y_yield",
    "us_10y_yield",
    "vix",
    "sp500",
    "oil_wti",
)


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


def build_fred_fetch_status_report(
    results: list[FredFetchResult],
    *,
    observation_start: str,
    observation_end: str | None,
    overall_status: str,
    h4_first: str | None = None,
    h4_last: str | None = None,
    api_key_present: bool = False,
) -> dict[str, object]:
    series_rows: list[dict[str, object]] = []
    for r in results:
        series_rows.append(
            {
                "feature_id": r.feature_id,
                "series_id": r.series_id,
                "status": r.status,
                "rows": r.rows,
                "message": r.message,
                "required": r.feature_id in REQUIRED_FRED_FEATURES,
            }
        )
    required_ok = all(
        row["status"] == "ok" and int(row["rows"]) > 0  # type: ignore[arg-type]
        for row in series_rows
        if row.get("required")
    )
    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "overall_status": overall_status,
        "fred_api_key_present": api_key_present,
        "observation_start": observation_start,
        "observation_end": observation_end,
        "h4_research_first_bar": h4_first,
        "h4_research_last_bar": h4_last,
        "series": series_rows,
        "required_series_complete": required_ok if results else False,
        "explicit_disclaimer": (
            "Diagnostic data-readiness only. Not strategy evidence. "
            "No win-rate or expectancy claims."
        ),
    }


def write_fred_fetch_status_report(path: Path, report: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return path


def run_fred_fetch_for_window(
    *,
    cache_dir: Path,
    observation_start: str,
    observation_end: str | None,
    output_dir: Path,
    h4_first: str | None = None,
    h4_last: str | None = None,
) -> tuple[list[FredFetchResult], dict[str, object]]:
    api_key = get_fred_api_key()
    if not api_key:
        report = build_fred_fetch_status_report(
            [],
            observation_start=observation_start,
            observation_end=observation_end,
            overall_status="BLOCKED_AUTH_OR_LOCAL_CSV_REQUIRED",
            h4_first=h4_first,
            h4_last=h4_last,
            api_key_present=False,
        )
        write_blocked_report(output_dir, reason="FRED_API_KEY not set in environment or .env")
        write_fred_fetch_status_report(output_dir / "fred_fetch_status_real_window.json", report)
        return [], report

    results, status = fetch_all_fred_features(
        cache_dir=cache_dir,
        observation_start=observation_start,
        observation_end=observation_end,
        api_key=api_key,
    )
    report = build_fred_fetch_status_report(
        results,
        observation_start=observation_start,
        observation_end=observation_end,
        overall_status=status,
        h4_first=h4_first,
        h4_last=h4_last,
        api_key_present=True,
    )
    write_fred_fetch_status_report(output_dir / "fred_fetch_status_real_window.json", report)
    return results, report

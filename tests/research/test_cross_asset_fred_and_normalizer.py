"""Tests for FRED fetcher and normalization."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pandas as pd
import pytest
import respx
from research.cross_asset_features.fred import (
    fetch_all_fred_features,
    fetch_fred_observations,
    get_fred_api_key,
    write_blocked_report,
)
from research.cross_asset_features.normalizer import (
    compute_derived_features,
    normalize_from_sources,
    write_normalized_outputs,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "cross_asset"


@respx.mock
def test_fetch_fred_observations_success() -> None:
    payload = {
        "observations": [
            {"date": "2022-01-03", "value": "96.5"},
            {"date": "2022-01-04", "value": "."},
            {"date": "2022-01-05", "value": "97.1"},
        ]
    }
    respx.get("https://api.stlouisfed.org/fred/series/observations").respond(json=payload)
    df = fetch_fred_observations("DTWEXBGS", api_key="test-key", observation_start="2022-01-01")
    assert len(df) == 2
    assert float(df.iloc[0]["value"]) == 96.5


@respx.mock
def test_fetch_all_without_key_writes_blocked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    out = write_blocked_report(tmp_path, reason="missing key")
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["status"] == "BLOCKED_AUTH_OR_LOCAL_CSV_REQUIRED"


@respx.mock
def test_fetch_all_fred_features_mocked(tmp_path: Path) -> None:
    payload = {"observations": [{"date": "2022-01-03", "value": "20.0"}]}
    respx.get("https://api.stlouisfed.org/fred/series/observations").respond(json=payload)
    results, status = fetch_all_fred_features(
        cache_dir=tmp_path,
        observation_start="2022-01-01",
        api_key="test-key",
    )
    assert status == "OK"
    assert results
    assert (tmp_path / "DTWEXBGS.json").is_file()


@respx.mock
def test_fetch_fred_api_error(tmp_path: Path) -> None:
    respx.get("https://api.stlouisfed.org/fred/series/observations").respond(status_code=500)
    with pytest.raises(httpx.HTTPStatusError):
        fetch_fred_observations("VIXCLS", api_key="test-key", observation_start="2022-01-01")


def test_derived_feature_math() -> None:
    wide = pd.DataFrame(
        {
            "us_10y_yield": [3.0, 3.1],
            "us_2y_yield": [2.0, 2.2],
            "broad_usd_index": [100.0, 101.0],
            "vix": [20.0, 22.0],
            "sp500": [4000.0, 4040.0],
            "oil_wti": [70.0, 71.4],
        },
        index=pd.to_datetime(["2022-01-03", "2022-01-04"], utc=True),
    )
    out = compute_derived_features(wide)
    assert float(out.loc[out.index[0], "us_10y_minus_2y"]) == pytest.approx(1.0)
    assert float(out.loc[out.index[1], "broad_usd_index_1d_change"]) == pytest.approx(1.0)


def test_normalize_from_fixtures_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "research.cross_asset_features.normalizer.get_fred_api_key",
        lambda: None,
    )
    wide, manifest, status = normalize_from_sources(
        REPO_ROOT,
        data_dir=tmp_path / "empty",
        cache_dir=tmp_path / "empty" / ".fred_cache",
    )
    assert status == "FIXTURE_ONLY"
    assert "broad_usd_index" in wide.columns
    assert manifest["strategy_evidence"] is False


def test_write_normalized_outputs(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    paths = write_normalized_outputs(REPO_ROOT, out_dir, observation_start="2022-01-01")
    assert paths["csv"].is_file()
    assert paths["manifest"].is_file()
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    assert manifest["fred_api_key_present"] is (get_fred_api_key() is not None)

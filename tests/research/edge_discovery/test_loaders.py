"""Loader tests for the edge-discovery lab.

Pins the CSV shape contracts, the SHA-256 provenance, the instrument
inference rule, and the friendly error messages on bad inputs.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from research.edge_discovery.loaders import (
    REQUIRED_CANDLE_COLUMNS,
    REQUIRED_EVENT_COLUMNS,
    load_candles_csv,
    load_event_fixture,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
H4_FIXTURE = REPO_ROOT / "research" / "edge_discovery" / "sample_fixtures" / "synthetic_EUR_USD_H4.csv"
EVENTS_FIXTURE = REPO_ROOT / "research" / "edge_discovery" / "sample_fixtures" / "synthetic_events.csv"
D1AGG_FIXTURE = REPO_ROOT / "research" / "d1_aggregation" / "sample_EUR_USD_H4_to_D1.csv"


def test_h4_synthetic_fixture_loads_with_inferred_instrument() -> None:
    sample = load_candles_csv(H4_FIXTURE)
    assert sample.instrument == "EUR_USD"
    assert sample.granularity == "H4"
    assert sample.row_count == 480
    assert sample.source_path.endswith("synthetic_EUR_USD_H4.csv")
    assert len(sample.source_sha256) == 64
    assert "close" in sample.frame.columns
    assert sample.frame.index.is_monotonic_increasing
    assert str(sample.frame.index.tz) == "UTC"


def test_d1agg_sample_is_loadable_via_same_path() -> None:
    """The committed d1_aggregation sample is one supported input
    shape — make sure the lab loader handles it without help."""
    sample = load_candles_csv(D1AGG_FIXTURE)
    assert sample.granularity == "D1AGG"
    assert sample.instrument == "EUR_USD"
    assert sample.row_count > 0
    assert set(["bid_c", "ask_c"]).issubset(sample.frame.columns)


def test_load_candles_csv_rejects_missing_columns(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    bad.write_text("time,bid_o\n2024-01-01T00:00:00+00:00,1.1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        load_candles_csv(bad)


def test_load_candles_csv_explicit_instrument_overrides_filename() -> None:
    sample = load_candles_csv(H4_FIXTURE, instrument="OVERRIDE")
    assert sample.instrument == "OVERRIDE"


def test_event_fixture_loads_with_sorted_unique_classes() -> None:
    fixture = load_event_fixture(EVENTS_FIXTURE)
    assert fixture.event_count == 6
    assert fixture.classes == ("CPI", "FOMC", "NFP")
    assert fixture.frame.index.is_monotonic_increasing
    assert "event_class" in fixture.frame.columns


def test_event_fixture_rejects_missing_columns(tmp_path: Path) -> None:
    bad = tmp_path / "bad_events.csv"
    bad.write_text("time\n2024-01-01T00:00:00+00:00\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        load_event_fixture(bad)


def test_event_fixture_dedupes_on_time_class_pair(tmp_path: Path) -> None:
    p = tmp_path / "dupe.csv"
    p.write_text(
        "time,event_class\n"
        "2024-01-01T00:00:00+00:00,NFP\n"
        "2024-01-01T00:00:00+00:00,NFP\n"
        "2024-01-01T00:00:00+00:00,FOMC\n",
        encoding="utf-8",
    )
    fixture = load_event_fixture(p)
    assert fixture.event_count == 2
    assert fixture.classes == ("FOMC", "NFP")


def test_load_candles_csv_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_candles_csv(REPO_ROOT / "does_not_exist.csv")


def test_required_column_sets_are_documented() -> None:
    """Guard against silent expansion of the input contract."""
    assert frozenset(
        {"time", "bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c"}
    ) == REQUIRED_CANDLE_COLUMNS
    assert frozenset({"time", "event_class"}) == REQUIRED_EVENT_COLUMNS


def test_sha256_is_deterministic() -> None:
    a = load_candles_csv(H4_FIXTURE)
    b = load_candles_csv(H4_FIXTURE)
    assert a.source_sha256 == b.source_sha256


def test_mid_columns_are_midpoint_of_bid_ask() -> None:
    sample = load_candles_csv(H4_FIXTURE)
    first = sample.frame.iloc[0]
    expected = (float(first["bid_c"]) + float(first["ask_c"])) / 2.0
    assert abs(float(first["close"]) - expected) < 1e-12
    assert isinstance(sample.frame.index, pd.DatetimeIndex)

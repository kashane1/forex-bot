"""Tests for non-USD cross ingestion support (script allowlist + coverage)."""

from __future__ import annotations

import importlib.util
from datetime import UTC, datetime
from pathlib import Path

import pytest

from forex_bot.data.cross_ingestion import (
    M1_SOURCE,
    CrossCoverage,
    cross_coverage,
    cross_coverage_report,
    cross_ingestion_targets,
)

_ROOT = Path(__file__).resolve().parents[2]


def _load_ingest_module():
    spec = importlib.util.spec_from_file_location(
        "ingest_oanda_m1_candles", _ROOT / "scripts" / "ingest_oanda_m1_candles.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ingest = _load_ingest_module()


# --- script allowlist + resolution (safety preserved) ---------------------

def test_crosses_are_allowlisted_alongside_majors():
    for name in ("EUR_GBP", "EUR_JPY", "GBP_JPY", "AUD_JPY"):
        assert name in ingest.ALLOWED_INSTRUMENTS
    # majors still allowlisted
    for name in ingest.MAJOR_FOREX_PAIRS:
        assert name in ingest.ALLOWED_INSTRUMENTS


def test_validate_instrument_accepts_cross_rejects_unknown():
    assert ingest.validate_instrument("GBP_JPY") == "GBP_JPY"
    with pytest.raises(ValueError):
        ingest.validate_instrument("XAU_USD")  # not allowlisted
    with pytest.raises(ValueError):
        ingest.validate_instrument("EURJPY")  # malformed


def test_endpoint_safety_unchanged_for_crosses():
    # Candle endpoint for a cross is allowed; mutation/account paths refused.
    ingest.validate_endpoint_url("https://api-fxpractice.oanda.com/v3/instruments/EUR_JPY/candles")
    with pytest.raises(RuntimeError):
        ingest.validate_endpoint_url("https://api-fxtrade.oanda.com/v3/instruments/EUR_JPY/candles")
    with pytest.raises(RuntimeError):
        ingest.validate_endpoint_url("https://api-fxpractice.oanda.com/v3/accounts/x/orders")


def test_resolve_crosses_flag_returns_primary_wave1():
    class Args:
        majors = False
        crosses = True
        all_crosses = False
        instruments = None
        instrument = None

    assert ingest.resolve_instruments(Args()) == ["EUR_GBP", "EUR_JPY", "GBP_JPY", "AUD_JPY"]


def test_resolve_all_crosses_flag_returns_full_registry():
    class Args:
        majors = False
        crosses = False
        all_crosses = True
        instruments = None
        instrument = None

    resolved = ingest.resolve_instruments(Args())
    assert "EUR_CHF" in resolved and "NZD_JPY" in resolved
    assert len(resolved) == 8


def test_resolve_majors_flag_unchanged():
    class Args:
        majors = True
        crosses = False
        all_crosses = False
        instruments = None
        instrument = None

    assert ingest.resolve_instruments(Args()) == list(ingest.MAJOR_FOREX_PAIRS)


# --- coverage probe -------------------------------------------------------

class _FakeStore:
    def __init__(self, counts, last_times=None):
        self._counts = counts
        self._last = last_times or {}

    def count_candles(self, *, instrument, granularity, source=None):
        return self._counts.get((instrument, granularity), 0)

    def max_candle_time(self, *, instrument, granularity, source=None):
        return self._last.get((instrument, granularity))


def test_cross_ingestion_targets_scopes():
    assert cross_ingestion_targets(scope="primary") == ["EUR_GBP", "EUR_JPY", "GBP_JPY", "AUD_JPY"]
    assert len(cross_ingestion_targets(scope="all")) == 8
    with pytest.raises(ValueError):
        cross_ingestion_targets(scope="bogus")


def test_cross_coverage_not_ingested_when_empty():
    store = _FakeStore(counts={})
    cov = cross_coverage(store, "EUR_GBP")
    assert isinstance(cov, CrossCoverage)
    assert cov.state == "NOT_INGESTED"
    assert cov.row_count == 0
    assert cov.last_timestamp is None
    assert cov.tier == "primary"


def test_cross_coverage_ingested_reports_count_and_last_ts():
    last = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)
    store = _FakeStore(
        counts={("EUR_JPY", "M1"): 1_000_000},
        last_times={("EUR_JPY", "M1"): last},
    )
    cov = cross_coverage(store, "EUR_JPY")
    assert cov.state == "INGESTED"
    assert cov.row_count == 1_000_000
    assert cov.last_timestamp == last.isoformat()


def test_cross_coverage_surfaces_structural_break_note():
    store = _FakeStore(counts={})
    cov = cross_coverage(store, "EUR_CHF")
    assert any("structural_break:2015-01-15" in n for n in cov.notes)


def test_cross_coverage_rejects_non_cross():
    store = _FakeStore(counts={})
    with pytest.raises(ValueError):
        cross_coverage(store, "EUR_USD")


def test_cross_coverage_report_is_diagnostic_and_compact():
    store = _FakeStore(counts={("EUR_GBP", "M1"): 500})
    report = cross_coverage_report(store, scope="primary")
    assert report["strategy_evidence"] is False
    assert report["diagnostic_only"] is True
    assert report["source"] == M1_SOURCE
    assert report["ingested_count"] == 1
    assert set(report["not_ingested"]) == {"EUR_JPY", "GBP_JPY", "AUD_JPY"}
    assert len(report["crosses"]) == 4

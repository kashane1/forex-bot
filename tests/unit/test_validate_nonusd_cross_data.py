"""Phase 5 — non-USD cross validation/diagnostics script."""

from __future__ import annotations

import importlib.util
from datetime import UTC, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _load():
    spec = importlib.util.spec_from_file_location(
        "validate_nonusd_cross_data", _ROOT / "scripts" / "validate_nonusd_cross_data.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


vx = _load()


class _EmptyStore:
    def count_candles(self, **_kwargs):
        return 0

    def max_candle_time(self, **_kwargs):
        return None


def test_metadata_check_passes_for_all_registered_crosses():
    meta = vx.metadata_check()
    assert meta["status"] == "PASS"
    assert len(meta["crosses"]) == 8
    # JPY crosses carry -2/3 conventions
    eur_jpy = next(c for c in meta["crosses"] if c["instrument"] == "EUR_JPY")
    assert eur_jpy["pip_location"] == -2 and eur_jpy["display_precision"] == 3
    assert eur_jpy["ok"] is True


def test_build_report_all_not_ingested_with_empty_store():
    report = vx.build_report(_EmptyStore(), scope="all")
    assert report["strategy_evidence"] is False
    assert report["diagnostic_only"] is True
    assert report["metadata_check"] == "PASS"
    assert report["target_count"] == 8
    assert report["ingested_count"] == 0
    assert len(report["not_ingested"]) == 8
    # each cross still carries a cost profile even with no data
    for c in report["crosses"]:
        assert c["state"] == "NOT_INGESTED"
        assert c["cost_profile"]["diagnostic_only"] is True
        assert "quality" not in c  # diagnostics skipped when not ingested


def test_build_report_primary_scope():
    report = vx.build_report(_EmptyStore(), scope="primary")
    assert report["target_count"] == 4
    names = {c["instrument"] for c in report["crosses"]}
    assert names == {"EUR_GBP", "EUR_JPY", "GBP_JPY", "AUD_JPY"}


def test_session_spread_summary_buckets_by_session():
    def row(hour, bid, ask):
        return {"time_utc": datetime(2024, 1, 1, hour, tzinfo=UTC), "bid_c": bid, "ask_c": ask}

    rows = [
        row(2, 160.00, 160.02),   # asian, 2 pips (JPY pip 0.01)
        row(8, 160.00, 160.03),   # london, 3 pips
        row(9, 160.00, 160.05),   # london, 5 pips
        row(14, 160.00, 160.04),  # london_ny_overlap, 4 pips
    ]
    summary = vx.session_spread_summary(rows, pip_size=0.01)
    assert summary["asian"]["n"] == 1
    assert summary["asian"]["median_pips"] == 2.0
    assert summary["london"]["n"] == 2
    assert "london_ny_overlap" in summary


def test_session_spread_summary_ignores_incomplete_rows():
    rows = [{"time_utc": datetime(2024, 1, 1, 8, tzinfo=UTC), "bid_c": None, "ask_c": 1.0}]
    assert vx.session_spread_summary(rows, pip_size=0.0001) == {}


class _IngestedStore(_EmptyStore):
    """Reports rows present but is not asked for full diagnostics."""

    def count_candles(self, **_kwargs):
        return 1234

    def max_candle_time(self, **_kwargs):
        return datetime(2024, 6, 1, tzinfo=UTC)


def test_build_report_ingested_without_diagnostics_reports_counts():
    report = vx.build_report(_IngestedStore(), scope="primary", run_diagnostics=False)
    assert report["ingested_count"] == 4
    for c in report["crosses"]:
        assert c["state"] == "INGESTED"
        assert c["row_count"] == 1234
        assert "quality" not in c  # diagnostics explicitly disabled

"""Unit tests for the pure helpers in scripts/generate_non_time_bar_diagnostics.py.

Loads the script module by path (it has no __init__) and exercises the pure
aggregation helpers — no DB, no broker, no network.
"""

from __future__ import annotations

import importlib.util
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import ModuleType

from forex_bot.data.non_time_bars import RangeBarConfig, build_range_bars
from forex_bot.domain.candles import Candle

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "generate_non_time_bar_diagnostics.py"
T0 = datetime(2024, 1, 1, tzinfo=UTC)


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ntb_diag", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


diag = _load()


def test_session_bucket_partition():
    assert diag.session_bucket(0) == "tokyo"
    assert diag.session_bucket(6) == "tokyo"
    assert diag.session_bucket(7) == "london"
    assert diag.session_bucket(11) == "london"
    assert diag.session_bucket(12) == "london_ny_overlap"
    assert diag.session_bucket(15) == "london_ny_overlap"
    assert diag.session_bucket(16) == "new_york"
    assert diag.session_bucket(20) == "new_york"
    assert diag.session_bucket(21) == "rollover_late"
    assert diag.session_bucket(23) == "rollover_late"


def test_number_stats_empty_and_populated():
    empty = diag._number_stats([])
    assert all(v is None for v in empty.values())
    stats = diag._number_stats([1.0, 2.0, 3.0, 4.0])
    assert stats["min"] == 1.0
    assert stats["max"] == 4.0
    assert stats["median"] == 2.5
    assert stats["mean"] == 2.5


def _mk(i: int, o: str, h: str, low: str, c: str) -> Candle:
    return Candle(
        instrument="EUR_USD",
        granularity="M1",
        time=T0 + timedelta(minutes=i),
        complete=True,
        volume=1,
        mid_o=Decimal(o),
        mid_h=Decimal(h),
        mid_l=Decimal(low),
        mid_c=Decimal(c),
    )


def test_summarize_bars_core_fields():
    # Two clean 10-pip up bars over 4 M1 rows.
    rows = [
        _mk(0, "1.0000", "1.0011", "1.0000", "1.0010"),
        _mk(1, "1.0010", "1.0021", "1.0010", "1.0020"),
    ]
    bars = build_range_bars(rows, RangeBarConfig(instrument="EUR_USD", threshold_pips=10))
    summary = diag.summarize_bars(
        bars, instrument="EUR_USD", bar_type="range", threshold_label="10pip", m1_rows=2
    )
    assert summary["bar_count"] == 2
    assert summary["incomplete_final_bars"] == 0
    assert summary["m1_source_rows"] == 2
    assert summary["compression_vs_m1"] == 1.0  # 2 rows / 2 bars
    assert summary["completion_reason_counts"] == {"range_up": 2}
    assert summary["source_m1_rows_per_bar"]["median"] == 1.0
    assert "tokyo" in summary["session_distribution"]


def test_summarize_bars_flags_multi_threshold_warning():
    # 30 single-candle 38-pip bars -> all cross >1 threshold -> warning fires.
    bars = build_range_bars(
        [_mk(i, "1.0000", "1.0038", "1.0000", "1.0038") for i in range(30)],
        RangeBarConfig(instrument="EUR_USD", threshold_pips=10),
    )
    summary = diag.summarize_bars(
        bars, instrument="EUR_USD", bar_type="range", threshold_label="10pip", m1_rows=30
    )
    assert summary["multi_threshold_bars"] == 30
    assert any("crossed >1 threshold" in w for w in summary["data_quality_warnings"])


def test_summarize_bars_empty():
    summary = diag.summarize_bars(
        [], instrument="EUR_USD", bar_type="range", threshold_label="10pip", m1_rows=0
    )
    assert summary["bar_count"] == 0
    assert summary["compression_vs_m1"] is None
    assert any("no completed bars" in w for w in summary["data_quality_warnings"])


def test_quality_warnings_gap_spanning():
    warnings = diag._quality_warnings(bar_count=100, gap_spanning=3, multi_threshold=0)
    assert any("span >24h" in w for w in warnings)


def test_counting_stream_counts_rows():
    counter = diag._CountingStream(iter([1, 2, 3, 4]))
    consumed = list(counter)
    assert consumed == [1, 2, 3, 4]
    assert counter.count == 4

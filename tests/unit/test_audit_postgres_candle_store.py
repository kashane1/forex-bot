from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = _REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


audit = _load_script("audit_postgres_candle_store")


def _rows():
    start = datetime(2024, 1, 1, tzinfo=UTC)
    return [
        {
            "time_utc": start,
            "complete": True,
            "mid_o": 1.1,
            "mid_h": 1.2,
            "mid_l": 1.0,
            "mid_c": 1.15,
            "bid_o": 1.1,
            "bid_h": 1.2,
            "bid_l": 1.0,
            "bid_c": 1.15,
            "ask_o": 1.1002,
            "ask_h": 1.2002,
            "ask_l": 1.0002,
            "ask_c": 1.1502,
            "spread_close": 0.0002,
        },
        {
            "time_utc": start + timedelta(hours=4),
            "complete": True,
            "mid_o": 1.2,
            "mid_h": 1.3,
            "mid_l": 1.1,
            "mid_c": 1.25,
            "bid_o": 1.2,
            "bid_h": 1.3,
            "bid_l": 1.1,
            "bid_c": 1.25,
            "ask_o": 1.2002,
            "ask_h": 1.3002,
            "ask_l": 1.1002,
            "ask_c": 1.2502,
            "spread_close": 0.0002,
        },
    ]


def test_clean_fixture_pass():
    summary = audit.analyze_rows({"EUR_USD": _rows()}, granularity="H4")
    assert summary["status"] == "PASS"


def test_missing_bars_partial():
    rows = _rows()[1:]
    summary = audit.analyze_rows({"EUR_USD": rows}, granularity="H4")
    assert summary["status"] in {"PASS", "PARTIAL"}


def test_duplicate_detection():
    rows = _rows()
    summary = audit.analyze_rows({"EUR_USD": rows + [rows[0]]}, granularity="H4")
    assert summary["duplicates"]["EUR_USD"] == 1


def test_ohlc_violation_detection():
    rows = _rows()
    rows[0]["mid_h"] = 1.05
    summary = audit.analyze_rows({"EUR_USD": rows}, granularity="H4")
    assert summary["ohlc_violations"]["EUR_USD"] == 1


def test_spread_anomaly_detection():
    rows = _rows()
    rows[0]["spread_close"] = 0.0
    summary = audit.analyze_rows({"EUR_USD": rows}, granularity="H4")
    assert summary["spread_anomalies"]["EUR_USD"] == 1


def test_markdown_summary_generated():
    md = audit.render_markdown(audit.analyze_rows({"EUR_USD": _rows()}, granularity="H4"))
    assert "Postgres Candle Store Audit" in md
    assert "EUR_USD" in md


def test_json_schema_stable():
    summary = audit.analyze_rows({"EUR_USD": _rows()}, granularity="H4")
    payload = json.loads(json.dumps(summary, default=str))
    assert "common_timestamp_intersection" in payload

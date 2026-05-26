from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = _REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


export = _load_script("export_postgres_research_candles")


def _rows():
    start = datetime(2024, 1, 1, tzinfo=UTC)
    out = []
    for idx in range(2):
        out.append(
            {
                "time_utc": start + timedelta(hours=4 * idx),
                "complete": True,
                "volume": 10 + idx,
                "bid_o": 1.1 + idx,
                "bid_h": 1.2 + idx,
                "bid_l": 1.0 + idx,
                "bid_c": 1.15 + idx,
                "ask_o": 1.1002 + idx,
                "ask_h": 1.2002 + idx,
                "ask_l": 1.0002 + idx,
                "ask_c": 1.1502 + idx,
                "mid_o": 1.1001 + idx,
                "mid_h": 1.2001 + idx,
                "mid_l": 1.0001 + idx,
                "mid_c": 1.1501 + idx,
                "source": "oanda-practice",
            }
        )
    return out


def test_export_from_fixture_rows():
    csv_rows = export.rows_to_csv_rows(_rows())
    assert csv_rows[0][0].endswith("+00:00")
    assert len(csv_rows[0]) == len(export.CSV_HEADER)


def test_manifest_hashes_match():
    rows_by = {"EUR_USD": _rows()}
    manifest = export.build_manifest(rows_by, granularity="H4", database_name="forex_bot", schema_name="market_data")
    expected = export.hash_csv_rows(export.rows_to_csv_rows(_rows()))
    assert manifest["files"]["EUR_USD"]["sha256"] == expected


def test_missing_pair_fails_clearly():
    with pytest.raises(ValueError, match="Missing pair"):
        export.build_manifest({"EUR_USD": []}, granularity="H4", database_name="forex_bot", schema_name="market_data")


def test_no_secrets_in_manifest():
    manifest = export.build_manifest({"EUR_USD": _rows()}, granularity="H4", database_name="forex_bot", schema_name="market_data")
    text = json.dumps(manifest)
    assert "password" not in text.lower()
    assert "token" not in text.lower()


def test_backtrader_expected_columns_present():
    assert export.CSV_HEADER == [
        "time", "bid_open", "bid_high", "bid_low", "bid_close",
        "ask_open", "ask_high", "ask_low", "ask_close", "volume",
    ]


def test_optional_sqlite_compatibility_schema_matches_runner_expectation(tmp_path):
    out = tmp_path / "campaign_002.sqlite3"
    export.write_compat_sqlite(out, {"EUR_USD": _rows()}, granularity="H4")
    conn = sqlite3.connect(out)
    try:
        cols = [row[1] for row in conn.execute("PRAGMA table_info(candles)").fetchall()]
        assert "instrument" in cols
        assert "granularity" in cols
        assert "bid_o" in cols
    finally:
        conn.close()

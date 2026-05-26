from __future__ import annotations

import importlib.util
import json
import sys
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


ingest = _load_script("ingest_oanda_candles_postgres")


def test_db_env_absent_blocked_no_network(monkeypatch, capsys):
    hit = {"called": False}
    monkeypatch.setattr(
        ingest,
        "fetch_oanda_candles",
        lambda *args, **kwargs: hit.__setitem__("called", True),
    )
    rc = ingest.main([], environ={})
    out = json.loads(capsys.readouterr().out)
    assert rc == 2
    assert out["status"] == "BLOCKED"
    assert hit["called"] is False


def test_oanda_env_absent_blocked_no_network():
    with pytest.raises(Exception, match="BLOCKED"):
        ingest.require_practice_oanda_env({})


def test_live_env_refused():
    with pytest.raises(RuntimeError, match="live OANDA environment"):
        ingest.require_practice_oanda_env({"OANDA_ENVIRONMENT": "live"})


def test_mocked_oanda_response_parsed_correctly():
    payload = {
        "candles": [
            {
                "time": "2024-01-01T00:00:00Z",
                "complete": True,
                "volume": 7,
                "bid": {"o": "1.1", "h": "1.2", "l": "1.0", "c": "1.15"},
                "ask": {"o": "1.1002", "h": "1.2002", "l": "1.0002", "c": "1.1502"},
                "mid": {"o": "1.1001", "h": "1.2001", "l": "1.0001", "c": "1.1501"},
            },
            {"time": "2024-01-01T04:00:00Z", "complete": False, "volume": 8},
        ]
    }
    rows = ingest.parse_oanda_candles(payload, instrument="EUR_USD", granularity="H4")
    assert len(rows) == 1
    assert rows[0].volume == 7


def test_credentials_redacted_in_logs():
    text = ingest._scrub_value("Bearer abcdef0123456789abcdef0123456789-abcdef0123456789abcdef0123456789")
    assert "abcdef" not in text


def test_bad_instrument_rejected():
    with pytest.raises(ValueError, match="Invalid OANDA instrument"):
        ingest.validate_instruments(["EURUSD"])


def test_script_has_no_order_endpoint_paths():
    text = (_REPO / "scripts" / "ingest_oanda_candles_postgres.py").read_text(encoding="utf-8")
    assert "/orders" not in text
    assert "submit_order" not in text
    assert "forex_bot.execution" not in text

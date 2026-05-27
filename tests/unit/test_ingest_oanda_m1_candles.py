from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]


def _load_script():
    path = _REPO / "scripts" / "ingest_oanda_m1_candles.py"
    spec = importlib.util.spec_from_file_location("ingest_oanda_m1_candles", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ingest = _load_script()


def test_candle_endpoint_allowed() -> None:
    ingest.validate_endpoint_url(
        "https://api-fxpractice.oanda.com/v3/instruments/EUR_USD/candles"
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://api-fxpractice.oanda.com/v3/accounts/abc/orders",
        "https://api-fxpractice.oanda.com/v3/accounts/abc/openTrades",
        "https://api-fxpractice.oanda.com/v3/accounts/abc/openPositions",
    ],
)
def test_mutation_and_account_endpoints_refused(url: str) -> None:
    with pytest.raises(RuntimeError):
        ingest.validate_endpoint_url(url)


def test_live_host_refused() -> None:
    with pytest.raises(RuntimeError, match="live"):
        ingest.validate_endpoint_url(
            "https://api-fxtrade.oanda.com/v3/instruments/EUR_USD/candles"
        )


def test_missing_date_range_refused(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        ingest.main(["--instrument", "EUR_USD"], environ={})
    assert exc.value.code == 2
    assert "required" in capsys.readouterr().err


def test_too_large_date_range_requires_chunk_limit(capsys) -> None:
    rc = ingest.main(
        [
            "--instrument",
            "EUR_USD",
            "--start",
            "2024-01-01",
            "--end",
            "2024-02-01",
        ],
        environ={},
    )
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert "BLOCKED_DATE_RANGE" in out["message"]


def test_dry_run_makes_no_network_call(monkeypatch, capsys) -> None:
    hit = {"called": False}
    monkeypatch.setattr(
        ingest,
        "fetch_chunk",
        lambda *args, **kwargs: hit.__setitem__("called", True),
    )
    rc = ingest.main(
        [
            "--instrument",
            "EUR_USD",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-02",
        ],
        environ={},
    )
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["network_called"] is False
    assert hit["called"] is False


def test_payload_parses_m1_records() -> None:
    payload = {
        "candles": [
            {
                "time": "2024-01-01T00:00:00Z",
                "complete": True,
                "volume": 1,
                "bid": {"o": "1.1", "h": "1.2", "l": "1.0", "c": "1.15"},
                "ask": {"o": "1.1002", "h": "1.2002", "l": "1.0002", "c": "1.1502"},
                "mid": {"o": "1.1001", "h": "1.2001", "l": "1.0001", "c": "1.1501"},
            }
        ]
    }
    rows = ingest.parse_oanda_m1_payload(payload, instrument="EUR_USD", fetch_batch_id="batch")
    assert rows[0].granularity == "M1"
    assert rows[0].time_utc == datetime(2024, 1, 1, tzinfo=UTC)
    assert rows[0].fetch_batch_id == "batch"


def test_script_has_no_order_trade_position_paths() -> None:
    text = (_REPO / "scripts" / "ingest_oanda_m1_candles.py").read_text(encoding="utf-8")
    assert "submit_order" not in text
    assert "forex_bot.execution" not in text

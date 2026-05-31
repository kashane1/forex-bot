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


ingest = _load_script("ingest_crypto_candles_postgres")


def test_db_env_absent_blocked_no_network(monkeypatch, capsys):
    hit = {"called": False}
    monkeypatch.setattr(
        ingest,
        "fetch_coinbase_candles",
        lambda *args, **kwargs: hit.__setitem__("called", True),
    )
    rc = ingest.main(
        ["--instrument", "BTC_USD", "--start", "2024-01-01T00:00:00Z", "--end", "2024-01-02T00:00:00Z"],
        environ={},
    )
    out = json.loads(capsys.readouterr().out)
    assert rc == 2
    assert out["status"] == "BLOCKED"
    assert hit["called"] is False


def test_script_has_no_trading_endpoint_paths():
    text = (_REPO / "scripts" / "ingest_crypto_candles_postgres.py").read_text(encoding="utf-8")
    assert "/orders" not in text
    assert "submit_order" not in text
    assert "forex_bot.execution" not in text

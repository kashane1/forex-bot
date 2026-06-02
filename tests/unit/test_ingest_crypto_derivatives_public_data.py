from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

_SPEC = importlib.util.spec_from_file_location(
    "ingest_crypto_derivatives_public_data",
    ROOT / "scripts" / "ingest_crypto_derivatives_public_data.py",
)
mod = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(mod)


def _args(**overrides):
    ns = mod.build_parser().parse_args([])
    for key, value in overrides.items():
        setattr(ns, key, value)
    return ns


def test_default_is_dry_run():
    ns = mod.build_parser().parse_args([])
    assert ns.execute_public_fetch is False
    result = mod.run(ns, environ={})
    assert result["status"] == "DRY_RUN"
    assert result["would_fetch"]["canonical_id"] == "BTC_PERP_USD"
    assert result["would_fetch"]["request_url"].startswith("https://fapi.binance.com")


def test_dry_run_does_no_network_and_no_files(tmp_path, monkeypatch):
    # If any fetch/file write happened, httpx import or RAW_DIR write would occur.
    ns = _args(instrument="ETH_PERP_USD", source="bybit", data_class="open_interest")
    result = mod.run(ns, environ={})
    assert result["status"] == "DRY_RUN"
    assert result["would_fetch"]["venue_symbol"] == "ETHUSDT"


def test_refuses_unknown_instrument():
    ns = _args(instrument="SOL_PERP_USD")
    with pytest.raises(ValueError, match="unsupported crypto perp"):
        mod.run(ns, environ={})


def test_refuses_non_perp_instrument():
    ns = _args(instrument="BTC_USD")
    with pytest.raises(ValueError):
        mod.run(ns, environ={})


def test_refuses_when_exchange_credentials_present():
    ns = _args()
    with pytest.raises(mod.UnsafeSourceError, match="public-only"):
        mod.run(ns, environ={"BINANCE_API_KEY": "abc"})


def test_refuses_unknown_source():
    ns = _args(source="ftx")
    with pytest.raises(ValueError):
        mod.run(ns, environ={})

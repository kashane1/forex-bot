from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from research.crypto.derivatives_models import compute_basis, funding_cashflow  # noqa: E402
from research.crypto.derivatives_sources import (  # noqa: E402
    PUBLIC_BASE_URLS,
    UnsafeSourceError,
    assert_no_credentials_required,
    build_request_url,
    count_payload_rows,
    is_public_url,
    parse_binance_funding,
    parse_binance_mark_klines,
    parse_binance_perp_klines,
    parse_bybit_open_interest,
    parse_okx_funding,
    parse_okx_open_interest,
)

FIX = ROOT / "research" / "crypto" / "fixtures" / "derivatives"


def _load(name: str):
    return json.loads((FIX / name).read_text())


# --- public endpoint allowlist ---------------------------------------------


def test_public_urls_pass_allowlist():
    for venue in PUBLIC_BASE_URLS:
        if venue in {"binance-usdm", "bybit", "kraken-futures"}:
            assert is_public_url(build_request_url(venue, "funding"))


def test_private_or_off_allowlist_url_refused():
    assert not is_public_url("https://api.binance.com/sapi/v1/account")
    assert not is_public_url("https://fapi.binance.com/fapi/v1/order")
    assert not is_public_url("http://fapi.binance.com/fapi/v1/fundingRate")  # not https
    assert not is_public_url("https://evil.example.com/fapi/v1/fundingRate")
    assert not is_public_url("https://fapi.binance.com/fapi/v1/klines?apiKey=abc")


def test_build_request_url_rejects_unknown_venue():
    with pytest.raises(UnsafeSourceError):
        build_request_url("ftx", "funding")


# --- credential refusal -----------------------------------------------------


def test_no_credentials_required_passes_clean_env():
    assert_no_credentials_required({"PATH": "/usr/bin", "RESEARCH_DATABASE_URL": "postgres://x"})


def test_exchange_credential_env_refused():
    with pytest.raises(UnsafeSourceError, match="public-only"):
        assert_no_credentials_required({"BINANCE_API_KEY": "abc123"})
    with pytest.raises(UnsafeSourceError):
        assert_no_credentials_required({"BYBIT_API_SECRET": "xyz"})


# --- parsers / BTC-ETH-only guard ------------------------------------------


def test_parse_binance_funding_fixture():
    recs = parse_binance_funding(_load("binance_funding_btc.json"))
    assert len(recs) == 3
    assert all(r.canonical_id == "BTC_PERP_USD" for r in recs)
    assert all(r.funding_interval_hours == 8 for r in recs)
    # monotonic after parse
    assert [r.funding_time_utc for r in recs] == sorted(r.funding_time_utc for r in recs)
    assert recs[0].funding_rate == pytest.approx(0.0001)


def test_parse_binance_perp_klines_fixture():
    recs = parse_binance_perp_klines(
        _load("binance_perp_klines_btc.json"), canonical_id="BTC_PERP_USD", granularity="H1"
    )
    assert len(recs) == 3
    assert recs[0].quote_ccy == "USDT"
    assert recs[0].high >= recs[0].low


def test_parse_binance_mark_klines_fixture():
    recs = parse_binance_mark_klines(
        _load("binance_mark_klines_btc.json"), canonical_id="BTC_PERP_USD", granularity="H1"
    )
    assert len(recs) == 3
    assert recs[0].mark_close is not None
    assert recs[0].index_close is None


def test_parse_bybit_open_interest_fixture():
    recs = parse_bybit_open_interest(
        _load("bybit_open_interest_btc.json"), canonical_id="BTC_PERP_USD", interval="1h"
    )
    assert len(recs) == 3
    assert recs[0].open_interest_base is not None
    assert recs[0].open_interest_usd is not None


def test_parse_okx_funding_fixture():
    recs = parse_okx_funding(_load("okx_funding_btc.json"))
    assert len(recs) == 3
    assert all(r.canonical_id == "BTC_PERP_USD" for r in recs)
    assert all(r.funding_interval_hours == 8 for r in recs)
    assert all(r.venue == "okx" for r in recs)


def test_parse_okx_open_interest_fixture():
    recs = parse_okx_open_interest(_load("okx_open_interest_btc.json"))
    assert len(recs) == 1
    assert recs[0].canonical_id == "BTC_PERP_USD"
    assert recs[0].open_interest_base is not None
    assert recs[0].open_interest_usd is not None


def test_okx_funding_refuses_altcoin():
    bad = {"code": "0", "data": [{"instId": "SOL-USDT-SWAP", "fundingRate": "0.0001", "fundingTime": "1717200000000"}]}
    with pytest.raises(ValueError, match="unauthorized / unknown"):
        parse_okx_funding(bad)


def test_count_payload_rows_shapes():
    assert count_payload_rows([1, 2, 3]) == 3
    assert count_payload_rows({"data": [1, 2]}) == 2
    assert count_payload_rows({"result": {"list": [1]}}) == 1
    assert count_payload_rows({"nothing": 1}) == 0


def test_funding_parser_refuses_altcoin_symbol():
    bad = [{"symbol": "SOLUSDT", "fundingTime": 1717200000000, "fundingRate": "0.0001", "markPrice": "1"}]
    with pytest.raises(ValueError, match="unauthorized / unknown"):
        parse_binance_funding(bad)


def test_duplicate_timestamps_deduped():
    dup = _load("binance_funding_btc.json")
    dup.append(dup[0])  # duplicate first row
    recs = parse_binance_funding(dup)
    assert len(recs) == 3  # dedup by funding_time_utc


# --- funding direction convention ------------------------------------------


def test_funding_cashflow_sign_convention():
    # funding_rate > 0: longs pay shorts
    assert funding_cashflow(0.0001, 10_000, "long") == pytest.approx(-1.0)
    assert funding_cashflow(0.0001, 10_000, "short") == pytest.approx(1.0)
    # funding_rate < 0: shorts pay longs
    assert funding_cashflow(-0.0001, 10_000, "long") == pytest.approx(1.0)
    assert funding_cashflow(-0.0001, 10_000, "short") == pytest.approx(-1.0)


def test_funding_cashflow_bad_side():
    with pytest.raises(ValueError, match="unknown side"):
        funding_cashflow(0.0001, 1.0, "flat")  # type: ignore[arg-type]


def test_compute_basis():
    abs_, bps = compute_basis(68100.0, 68000.0)
    assert abs_ == pytest.approx(100.0)
    assert bps == pytest.approx(1e4 * 100.0 / 68000.0)
    with pytest.raises(ValueError, match="must be positive"):
        compute_basis(1.0, 0.0)

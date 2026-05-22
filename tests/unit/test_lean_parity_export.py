"""Tests for the Lean-parity preparation scripts
(Phase 3, infra-execution-fidelity-001).

Cover the pure functions of:
  * scripts/build_lean_parity_config.py — authoritative parameter
    extraction from the committed CAMPAIGN_002 config;
  * scripts/export_lean_parity_data.py — Lean custom-data CSV rows,
    the export data hash, and the real-OANDA-source guard.

No cloud, no paid service, no network — and nothing here approves a
strategy (CAMPAIGN_002 is already REJECT).
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from forex_bot.config import load_settings
from forex_bot.domain.candles import Candle

_REPO = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = _REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


build_cfg = _load_script("build_lean_parity_config")
export = _load_script("export_lean_parity_data")


def _h4(k: int) -> Candle:
    o = Decimal("1.1000") + Decimal("0.0010") * k
    return Candle(
        instrument="EUR_USD",
        granularity="H4",
        time=datetime(2020, 1, 1, 22, tzinfo=UTC) + timedelta(hours=4 * k),
        complete=True,
        volume=1000 + k,
        bid_o=o, bid_h=o + Decimal("0.0020"), bid_l=o - Decimal("0.0020"),
        bid_c=o + Decimal("0.0005"),
        ask_o=o + Decimal("0.0002"), ask_h=o + Decimal("0.0022"),
        ask_l=o - Decimal("0.0018"), ask_c=o + Decimal("0.0007"),
    )


# --------------------------------------------------------------------------
# build_lean_parity_config — authoritative parameter extraction
# --------------------------------------------------------------------------


def test_extract_parity_config_uses_the_committed_campaign_config():
    """The extractor must report the CAMPAIGN_002 config's real values —
    atr_stop_multiple 2.0 and max_bars_in_trade 240 — not the frozen
    baseline's 2.5 / 80 that an out-of-date table might carry."""
    settings = load_settings(_REPO / "configs" / "campaign_002_real_oanda.yaml")
    cfg = build_cfg.extract_parity_config(settings, source_path="configs/x.yaml")

    strat = cfg["strategy"]
    assert strat["name"] == "trend_following"
    assert strat["ema_fast"] == 50 and strat["ema_slow"] == 200
    assert strat["donchian_lookback"] == 20
    assert strat["atr_stop_multiple"] == 2.0
    assert strat["trailing_stop_atr_multiple"] == 2.0
    assert strat["max_bars_in_trade"] == 240
    assert "0.1.0" in strat["version"]

    assert cfg["market"]["granularity"] == "H4"
    assert len(cfg["market"]["instruments"]) == 7
    assert cfg["market"]["daily_alignment"] == 17


def test_extract_parity_config_is_not_an_approval():
    settings = load_settings(_REPO / "configs" / "campaign_002_real_oanda.yaml")
    cfg = build_cfg.extract_parity_config(settings, source_path="configs/x.yaml")
    assert cfg["_meta"]["is_an_approval"] is False
    assert cfg["_meta"]["verdict_on_record"] == "REJECT"
    assert cfg["_meta"]["source_config_hash"] == settings.config_hash


def test_extract_parity_config_records_cost_model_and_splits():
    settings = load_settings(_REPO / "configs" / "campaign_002_real_oanda.yaml")
    cfg = build_cfg.extract_parity_config(settings, source_path="configs/x.yaml")
    # CAMPAIGN_002 predates the fill-timing model -> signal_bar_close.
    assert cfg["cost_model"]["fill_timing"] == "signal_bar_close"
    assert cfg["cost_model"]["fixed_slippage_pips"] == 0.2
    assert set(cfg["splits"]) == {"train", "validation", "test_untouched", "full"}
    assert cfg["splits"]["full"] == ["2020-01-01", "2026-05-20"]


def test_committed_lean_parity_config_is_present_and_current():
    """The generated config is committed; it must match a fresh extraction
    from the campaign config (re-run the script if this fails)."""
    import json

    committed = json.loads(
        (_REPO / "research" / "lean_parity" / "lean_parity_config.json").read_text(
            encoding="utf-8"
        )
    )
    settings = load_settings(_REPO / "configs" / "campaign_002_real_oanda.yaml")
    assert committed["_meta"]["source_config_hash"] == settings.config_hash
    assert committed["strategy"]["atr_stop_multiple"] == 2.0
    assert committed["strategy"]["max_bars_in_trade"] == 240


# --------------------------------------------------------------------------
# export_lean_parity_data — CSV rows, hash, real-source guard
# --------------------------------------------------------------------------


def test_lean_csv_header_carries_bid_and_ask_ohlc():
    header = export.LEAN_CSV_HEADER
    assert header[0] == "time"
    for side in ("bid", "ask"):
        for field in ("open", "high", "low", "close"):
            assert f"{side}_{field}" in header
    assert "volume" in header


def test_candle_to_lean_row_is_exact_decimal_strings():
    row = export.candle_to_lean_row(_h4(0))
    assert len(row) == len(export.LEAN_CSV_HEADER)
    assert row[0] == "2020-01-01T22:00:00+00:00"
    # bid_open exact, no float round-trip.
    assert row[1] == "1.1000"


def test_data_sha256_is_deterministic_and_sensitive():
    a = [_h4(k) for k in range(5)]
    b = [_h4(k) for k in range(5)]
    assert export.data_sha256(a) == export.data_sha256(b)
    assert len(export.data_sha256(a)) == 64
    # A different candle set yields a different hash.
    assert export.data_sha256(a) != export.data_sha256([_h4(k) for k in range(6)])


def test_sources_guard_accepts_only_real_oanda():
    assert export.sources_are_real_oanda(["oanda-practice"])
    assert export.sources_are_real_oanda(["oanda-practice", "oanda-live"])
    assert not export.sources_are_real_oanda(["synthetic-v1"])
    assert not export.sources_are_real_oanda(["oanda-practice", "synthetic-v1"])
    assert not export.sources_are_real_oanda([])


def test_build_provenance_carries_hashes_and_window():
    candles = [_h4(k) for k in range(10)]
    prov = export.build_provenance(
        instrument="EUR_USD",
        candles=candles,
        source="oanda-practice",
        from_arg="2020-01-01",
        to_arg="2020-01-05",
        csv_name="EUR_USD_H4_lean.csv",
    )
    assert prov["candle_count"] == 10
    assert prov["source"] == "oanda-practice"
    assert len(prov["data_sha256"]) == 64
    assert prov["campaign_002_data_request_hash"]
    assert prov["first_ts"] == candles[0].time.isoformat()
    assert prov["last_ts"] == candles[-1].time.isoformat()

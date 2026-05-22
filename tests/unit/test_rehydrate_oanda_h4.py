"""Tests for the OANDA H4 store rehydration script
(Phase 1, infra-data-parity-001).

Cover the pure / read-only behaviour: the content-hash helper, the
store manifest, the refusal of missing or ambiguous credentials, and
that no credential-shaped string reaches a manifest. No OANDA call is
made — the fetch path is exercised only up to its credential guard.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from forex_bot.data.repositories import CandleRepo, DataSourceRecord, DataSourceRepo
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


rehydrate = _load_script("rehydrate_oanda_h4_store")


def _h4(instrument: str, k: int) -> Candle:
    o = Decimal("1.1000") + Decimal("0.0010") * k
    return Candle(
        instrument=instrument,
        granularity="H4",
        time=datetime(2024, 1, 1, tzinfo=UTC) + timedelta(hours=4 * k),
        complete=True,
        volume=1000 + k,
        bid_o=o, bid_h=o + Decimal("0.0020"), bid_l=o - Decimal("0.0020"),
        bid_c=o + Decimal("0.0005"),
        ask_o=o + Decimal("0.0002"), ask_h=o + Decimal("0.0022"),
        ask_l=o - Decimal("0.0018"), ask_c=o + Decimal("0.0007"),
    )


def _seed(db, instrument: str, n: int, *, source: str) -> None:
    candles = [_h4(instrument, k) for k in range(n)]
    CandleRepo(db).upsert_many(candles, source=source, price_components="BA", request_hash="x")
    DataSourceRepo(db).insert(
        DataSourceRecord(
            instrument=instrument, granularity="H4", source=source,
            candles_written=n, first_ts=candles[0].time.isoformat(),
            last_ts=candles[-1].time.isoformat(),
            raw_sha256="0" * 64, normalized_sha256="1" * 64,
        )
    )


# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------


def test_universe_and_window_are_the_six_majors_2020_2026():
    assert rehydrate.H4_PAIRS == [
        "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF"
    ]
    assert rehydrate.WINDOW_FROM == "2020-01-01"
    assert rehydrate.WINDOW_TO == "2026-05-20"


# --------------------------------------------------------------------------
# Content hash
# --------------------------------------------------------------------------


def test_normalized_candle_hash_deterministic_and_sensitive():
    a = [_h4("EUR_USD", k) for k in range(8)]
    b = [_h4("EUR_USD", k) for k in range(8)]
    assert rehydrate.normalized_candle_hash(a) == rehydrate.normalized_candle_hash(b)
    assert len(rehydrate.normalized_candle_hash(a)) == 64
    assert rehydrate.normalized_candle_hash(a) != rehydrate.normalized_candle_hash(
        [_h4("EUR_USD", k) for k in range(9)]
    )


def test_normalized_candle_hash_is_order_independent():
    a = [_h4("EUR_USD", k) for k in range(6)]
    assert rehydrate.normalized_candle_hash(a) == rehydrate.normalized_candle_hash(
        list(reversed(a))
    )


# --------------------------------------------------------------------------
# Store manifest
# --------------------------------------------------------------------------


def test_store_manifest_summarizes_a_real_store(temp_db):
    _seed(temp_db, "EUR_USD", 10, source="oanda-practice")
    manifest = rehydrate.store_manifest(temp_db, ["EUR_USD"])
    info = manifest["pairs"]["EUR_USD"]
    assert info["candle_count"] == 10
    assert info["source"] == "oanda-practice"
    assert len(info["content_hash"]) == 64
    assert manifest["total_candles"] == 10
    assert manifest["all_real_oanda"] is True


def test_store_manifest_flags_a_synthetic_store(temp_db):
    _seed(temp_db, "EUR_USD", 5, source="synthetic-v1")
    manifest = rehydrate.store_manifest(temp_db, ["EUR_USD"])
    assert manifest["all_real_oanda"] is False
    assert "synthetic-v1" in manifest["distinct_sources"]


def test_store_manifest_handles_empty_pairs(temp_db):
    manifest = rehydrate.store_manifest(temp_db, ["EUR_USD", "USD_JPY"])
    assert manifest["total_candles"] == 0
    assert manifest["all_real_oanda"] is False


def test_manifest_carries_no_credential_shaped_strings(temp_db):
    """A manifest is provenance-safe to surface — counts and hashes only,
    never an account id or token."""
    for pair in rehydrate.H4_PAIRS:
        _seed(temp_db, pair, 4, source="oanda-practice")
    text = json.dumps(rehydrate.store_manifest(temp_db, rehydrate.H4_PAIRS))
    assert "account" not in text.lower()
    assert "token" not in text.lower()


# --------------------------------------------------------------------------
# Credential / environment refusal (no OANDA call)
# --------------------------------------------------------------------------


def _clear_oanda_env(monkeypatch) -> None:
    for var in (
        "OANDA_ACCOUNT_ID_PRACTICE", "OANDA_ACCESS_TOKEN_PRACTICE",
        "OANDA_ACCOUNT_ID_LIVE", "OANDA_ACCESS_TOKEN_LIVE", "OANDA_ENVIRONMENT",
    ):
        monkeypatch.delenv(var, raising=False)


def test_fetch_refuses_when_credentials_are_missing(monkeypatch):
    _clear_oanda_env(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["rehydrate_oanda_h4_store"])
    # Fetch mode, no credentials -> blocked with exit 2, no OANDA call.
    assert rehydrate.main() == 2


def test_fetch_refuses_an_ambiguous_or_live_environment(monkeypatch):
    _clear_oanda_env(monkeypatch)
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "001-001-7654321-001")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "fake-practice-token")
    # OANDA_ENVIRONMENT=live contradicts the practice config -> refused.
    monkeypatch.setenv("OANDA_ENVIRONMENT", "live")
    monkeypatch.setattr(sys, "argv", ["rehydrate_oanda_h4_store"])
    assert rehydrate.main() == 2


def test_verify_mode_reports_a_missing_store(monkeypatch, tmp_path):
    _clear_oanda_env(monkeypatch)
    monkeypatch.setattr(
        sys, "argv",
        ["rehydrate_oanda_h4_store", "--verify", "--db", str(tmp_path / "absent.sqlite3")],
    )
    # Verify mode needs no credentials; a missing store is a clean exit 1.
    assert rehydrate.main() == 1


# --------------------------------------------------------------------------
# Result document (read-only, no OANDA call)
# --------------------------------------------------------------------------


def test_build_result_rows_summarizes_the_store(temp_db):
    _seed(temp_db, "EUR_USD", 8, source="oanda-practice")
    rows = rehydrate.build_result_rows(temp_db, ["EUR_USD"])
    assert len(rows) == 1
    row = rows[0]
    assert row["instrument"] == "EUR_USD"
    assert row["candle_count"] == 8
    assert row["complete_count"] == 8
    assert row["bid_available"] == 8
    assert row["ask_available"] == 8
    assert row["source"] == "oanda-practice"
    assert len(row["content_hash"]) == 64


def test_render_result_doc_carries_no_credentials(temp_db):
    for pair in rehydrate.H4_PAIRS:
        _seed(temp_db, pair, 5, source="oanda-practice")
    doc = rehydrate.render_result_doc(
        temp_db,
        rehydrate.H4_PAIRS,
        db_display="data/oanda_h4_research.sqlite3",
        generated_at=datetime(2026, 5, 22, tzinfo=UTC),
    )
    assert "gitignored" in doc
    assert "No credential value" in doc
    assert "Total: 30 completed H4 candles" in doc
    # provenance / counts only — no env-var name or bearer-token text.
    assert "OANDA_ACCOUNT" not in doc
    assert "Bearer" not in doc


def test_report_mode_blocks_on_a_missing_store(monkeypatch, tmp_path):
    _clear_oanda_env(monkeypatch)
    monkeypatch.setattr(
        sys, "argv",
        [
            "rehydrate_oanda_h4_store", "--report", str(tmp_path / "out.md"),
            "--db", str(tmp_path / "absent.sqlite3"),
        ],
    )
    # Report mode needs no credentials; a missing store is a clean exit 1.
    assert rehydrate.main() == 1
    assert not (tmp_path / "out.md").exists()

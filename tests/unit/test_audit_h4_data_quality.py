"""Tests for the H4 data-quality audit script
(Phase 5, oanda-practice-readonly-001).

Cover the pure audit logic against a seeded in-memory store. No OANDA
call is made.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from forex_bot.data.repositories import CandleRepo
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


dq = _load_script("audit_h4_data_quality")


def _h4(instrument: str, k: int, *, complete: bool = True) -> Candle:
    o = Decimal("1.1000") + Decimal("0.0010") * k
    return Candle(
        instrument=instrument,
        granularity="H4",
        time=datetime(2024, 1, 1, tzinfo=UTC) + timedelta(hours=4 * k),
        complete=complete,
        volume=1000 + k,
        bid_o=o,
        bid_h=o + Decimal("0.0020"),
        bid_l=o - Decimal("0.0020"),
        bid_c=o + Decimal("0.0005"),
        ask_o=o + Decimal("0.0002"),
        ask_h=o + Decimal("0.0022"),
        ask_l=o - Decimal("0.0018"),
        ask_c=o + Decimal("0.0007"),
    )


def _seed(db, instrument: str, candles: list[Candle]) -> None:
    CandleRepo(db).upsert_many(
        candles, source="oanda-practice", price_components="BA", request_hash="x"
    )


def test_pip_size_for_jpy_and_non_jpy():
    assert dq.pip_size_for("USD_JPY") == Decimal("0.01")
    assert dq.pip_size_for("EUR_USD") == Decimal("0.0001")
    assert dq.pip_size_for("GBP_USD") == Decimal("0.0001")


def test_audit_pair_clean_store_is_acceptable(temp_db):
    _seed(temp_db, "EUR_USD", [_h4("EUR_USD", k) for k in range(20)])
    pa = dq.audit_pair(CandleRepo(temp_db), "EUR_USD", min_candles=5)
    assert pa.acceptable is True
    assert pa.blockers == []
    assert pa.report.candle_count == 20
    assert pa.report.incomplete_count == 0


def test_audit_pair_flags_incomplete_candles(temp_db):
    candles = [_h4("EUR_USD", k) for k in range(10)]
    candles.append(_h4("EUR_USD", 10, complete=False))
    _seed(temp_db, "EUR_USD", candles)
    pa = dq.audit_pair(CandleRepo(temp_db), "EUR_USD", min_candles=5)
    assert pa.acceptable is False
    assert any("incomplete" in b for b in pa.blockers)


def test_audit_pair_flags_too_few_candles(temp_db):
    _seed(temp_db, "EUR_USD", [_h4("EUR_USD", k) for k in range(3)])
    pa = dq.audit_pair(CandleRepo(temp_db), "EUR_USD")  # default min_candles
    assert pa.acceptable is False
    assert any("candles" in b for b in pa.blockers)


def test_render_doc_has_required_sections_and_no_strategy_claim(temp_db):
    _seed(temp_db, "EUR_USD", [_h4("EUR_USD", k) for k in range(20)])
    audits = [dq.audit_pair(CandleRepo(temp_db), "EUR_USD", min_candles=5)]
    doc = dq.render_doc(
        audits,
        generated_at=datetime(2026, 5, 22, tzinfo=UTC),
        db_display="data/oanda_h4_research.sqlite3",
    )
    assert "Gap & anomaly classification" in doc
    assert "Expected weekend gaps" in doc
    assert "Expected holiday closures" in doc
    assert "outage-like" in doc
    assert "strategy_evidence: false" in doc
    assert "EUR_USD" in doc

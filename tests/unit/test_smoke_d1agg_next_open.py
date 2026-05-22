"""Tests for the D1AGG + next_bar_open diagnostic smoke check
(Phase 2, infra-execution-fidelity-001).

These cover the mechanical assertions the smoke script makes:
  * D1AGG timestamps clear the rollover blackout;
  * next-bar-open fills are available and the engine uses them;
  * a missing bar N+1 is detected explicitly;
  * synthetic data is refused — only real OANDA-provenance data is used.

The diagnostic probe is not a strategy and these tests assert no
strategy outcome — only plumbing.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo
from forex_bot.domain.candles import Candle

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "smoke_d1agg_next_open.py"


def _load_smoke():
    spec = importlib.util.spec_from_file_location("smoke_d1agg_next_open", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Register before exec: @dataclass with string annotations resolves the
    # module via sys.modules during class creation.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


smoke = _load_smoke()


def _d1agg(n: int, *, base: str = "1.1000") -> list[Candle]:
    """n synthetic-for-test D1AGG candles, ascending, each timestamped
    18:00 UTC = 13:00 New York — the research-day close, clear of the
    16:45–17:15 rollover blackout."""
    candles: list[Candle] = []
    base_dec = Decimal(base)
    for k in range(n):
        o = base_dec + Decimal("0.0010") * k
        close = o + Decimal("0.0005")
        candles.append(
            Candle(
                instrument="EUR_USD",
                granularity="D1AGG",
                time=datetime(2024, 1, 1, 18, 0, tzinfo=UTC) + timedelta(days=k),
                complete=True,
                volume=1000,
                bid_o=o, bid_h=o + Decimal("0.0030"),
                bid_l=o - Decimal("0.0030"), bid_c=close,
                ask_o=o + Decimal("0.0002"), ask_h=o + Decimal("0.0032"),
                ask_l=o - Decimal("0.0028"), ask_c=close + Decimal("0.0002"),
            )
        )
    return candles


# --------------------------------------------------------------------------
# Rollover blackout
# --------------------------------------------------------------------------


def test_check_blackout_passes_for_clean_d1agg():
    result = smoke.check_blackout(_d1agg(10))
    assert result.ok
    assert "clear" in result.detail


def test_check_blackout_fails_inside_rollover_window():
    """A D1AGG bar timestamped 22:00 UTC = 17:00 New York lands inside the
    rollover blackout — the smoke must catch it."""
    clean = _d1agg(3)
    contaminated = clean[1].model_copy(
        update={"time": datetime(2024, 1, 3, 22, 0, tzinfo=UTC)}
    )
    result = smoke.check_blackout([clean[0], contaminated, clean[2]])
    assert not result.ok


# --------------------------------------------------------------------------
# next-bar-open availability and engine fill
# --------------------------------------------------------------------------


def test_next_bar_open_data_is_available_on_clean_d1agg():
    result = smoke.check_next_bar_open_data_available(_d1agg(12))
    assert result.ok


def test_engine_fills_at_next_bar_open_on_d1agg():
    result = smoke.check_engine_fills_at_next_open(smoke.make_instrument("EUR_USD"), _d1agg(15))
    assert result.ok
    assert "N+1 open" in result.detail


def test_missing_next_bar_is_detected():
    result = smoke.check_missing_bar_detected(smoke.make_instrument("EUR_USD"), _d1agg(12))
    assert result.ok
    assert "NEXT_BAR_OPEN_UNAVAILABLE" in result.detail


# --------------------------------------------------------------------------
# No synthetic data
# --------------------------------------------------------------------------


def test_db_mode_refuses_synthetic_h4(tmp_path):
    """The smoke's DB path accepts only oanda-* sourced candles. A
    synthetic store (source 'synthetic-v1') must be refused."""
    db = Database(tmp_path / "synthetic.sqlite3")
    repo = CandleRepo(db)
    flat = Decimal("1.1000")
    h4 = [
        Candle(
            instrument="EUR_USD", granularity="H4",
            time=datetime(2024, 1, 1, 0, tzinfo=UTC) + timedelta(hours=4 * k),
            complete=True, volume=1,
            bid_o=flat, bid_h=flat, bid_l=flat, bid_c=flat,
            ask_o=flat, ask_h=flat, ask_l=flat, ask_c=flat,
        )
        for k in range(6)
    ]
    repo.upsert_many(h4, source="synthetic-v1", price_components="BA", request_hash="x")
    sources = smoke.distinct_h4_sources(db, "EUR_USD")
    assert sources == ["synthetic-v1"]
    # The smoke's guard predicate must reject this.
    assert not all(s.startswith("oanda") for s in sources)


def test_db_mode_accepts_real_oanda_source(tmp_path):
    db = Database(tmp_path / "oanda.sqlite3")
    repo = CandleRepo(db)
    flat = Decimal("1.1000")
    h4 = [
        Candle(
            instrument="EUR_USD", granularity="H4",
            time=datetime(2024, 1, 1, 0, tzinfo=UTC) + timedelta(hours=4 * k),
            complete=True, volume=1,
            bid_o=flat, bid_h=flat, bid_l=flat, bid_c=flat,
            ask_o=flat, ask_h=flat, ask_l=flat, ask_c=flat,
        )
        for k in range(6)
    ]
    repo.upsert_many(h4, source="oanda-practice", price_components="BA", request_hash="x")
    sources = smoke.distinct_h4_sources(db, "EUR_USD")
    assert sources == ["oanda-practice"]
    assert all(s.startswith("oanda") for s in sources)


def test_committed_sample_provenance_is_real_oanda():
    result = smoke.check_sample_provenance(smoke.SAMPLE_CSV)
    assert result.ok
    assert "not synthetic" in result.detail


def test_sample_provenance_fails_without_meta(tmp_path):
    fake = tmp_path / "no_meta.csv"
    fake.write_text("time,granularity\n", encoding="utf-8")
    assert not smoke.check_sample_provenance(fake).ok


def test_load_d1agg_sample_reads_committed_sample():
    candles = smoke.load_d1agg_sample(smoke.SAMPLE_CSV)
    assert len(candles) == 22
    assert all(c.granularity == "D1AGG" for c in candles)


# --------------------------------------------------------------------------
# Orchestration + report
# --------------------------------------------------------------------------


def test_smoke_instrument_passes_all_checks_on_clean_d1agg():
    result = smoke.smoke_instrument(
        smoke.make_instrument("EUR_USD"),
        _d1agg(20),
        data_source="fixture",
        provenance=smoke.Check("data_is_real_oanda", True, "fixture"),
    )
    assert result.ok
    assert {c.name for c in result.checks} == {
        "data_is_real_oanda",
        "d1agg_timestamps_clear_blackout",
        "next_bar_open_data_available",
        "engine_fills_at_next_bar_open",
        "missing_next_bar_detected",
    }


def test_report_states_diagnostic_only_disclaimers():
    result = smoke.smoke_instrument(
        smoke.make_instrument("EUR_USD"),
        _d1agg(15),
        data_source="fixture",
        provenance=smoke.Check("data_is_real_oanda", True, "fixture"),
    )
    text = smoke.render_report("test mode", [result], []).lower()
    assert "diagnostic-only" in text
    assert "no strategy evidence" in text
    assert "no trading recommendation" in text
    assert "no approval" in text

"""Tests for research/cost_atlas."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
from research.cost_atlas.atlas import (
    build_cost_atlas,
    classify_cost_state,
    flag_cost_hostile_cells,
)
from research.cost_atlas.metrics import compute_bar_metrics, spread_pips, spread_to_atr
from research.cost_atlas.session import session_bucket

from forex_bot.data.candle_dedupe import dedupe_candles
from forex_bot.domain.candles import Candle

REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_candle(instrument: str, t: datetime, bid_c: float, ask_c: float) -> Candle:
    return Candle(
        instrument=instrument,
        granularity="H4",
        time=t,
        complete=True,
        volume=100,
        bid_o=Decimal(str(bid_c - 0.0002)),
        bid_h=Decimal(str(bid_c + 0.0005)),
        bid_l=Decimal(str(bid_c - 0.0005)),
        bid_c=Decimal(str(bid_c)),
        ask_o=Decimal(str(ask_c + 0.0002)),
        ask_h=Decimal(str(ask_c + 0.0005)),
        ask_l=Decimal(str(ask_c - 0.0005)),
        ask_c=Decimal(str(ask_c)),
    )


def _build_fixture_db(path: Path, instrument: str = "EUR_USD", n: int = 80) -> None:
    start = datetime(2022, 1, 3, 0, 0, tzinfo=UTC)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE candles (
                id INTEGER PRIMARY KEY,
                instrument TEXT, granularity TEXT, time TEXT, complete INTEGER,
                volume INTEGER,
                bid_o REAL, bid_h REAL, bid_l REAL, bid_c REAL,
                ask_o REAL, ask_h REAL, ask_l REAL, ask_c REAL,
                mid_o REAL, mid_h REAL, mid_l REAL, mid_c REAL
            )
            """
        )
        for i in range(n):
            t = start + timedelta(hours=4 * i)
            bid = 1.1000 + i * 0.0001
            ask = bid + 0.00015 + (0.00005 if i % 10 == 0 else 0)
            conn.execute(
                """
                INSERT INTO candles (
                    instrument, granularity, time, complete, volume,
                    bid_o, bid_h, bid_l, bid_c, ask_o, ask_h, ask_l, ask_c,
                    mid_o, mid_h, mid_l, mid_c
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    instrument,
                    "H4",
                    t.isoformat(),
                    1,
                    100,
                    bid,
                    bid + 0.0005,
                    bid - 0.0005,
                    bid,
                    ask,
                    ask + 0.0005,
                    ask - 0.0005,
                    ask,
                    (bid + ask) / 2,
                    (bid + ask) / 2 + 0.0005,
                    (bid + ask) / 2 - 0.0005,
                    (bid + ask) / 2,
                ),
            )
        dup_t = start.isoformat()
        conn.execute(
            """
            INSERT INTO candles (
                instrument, granularity, time, complete, volume,
                bid_o, bid_h, bid_l, bid_c, ask_o, ask_h, ask_l, ask_c,
                mid_o, mid_h, mid_l, mid_c
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                instrument,
                "H4",
                dup_t,
                1,
                100,
                1.099,
                1.0995,
                1.0985,
                1.099,
                1.100,
                1.1005,
                1.0995,
                1.100,
                1.0995,
                1.100,
                1.099,
                1.0995,
            ),
        )


class TestSessionAndSpread:
    def test_session_bucket_asian(self) -> None:
        assert session_bucket(23) == "asian"
        assert session_bucket(3) == "asian"

    def test_session_bucket_london_overlap(self) -> None:
        assert session_bucket(8) == "london"
        assert session_bucket(14) == "london_ny_overlap"
        assert session_bucket(18) == "ny"

    def test_spread_pips_eur_usd(self) -> None:
        assert spread_pips("EUR_USD", 1.1000, 1.10015) == pytest.approx(1.5, abs=0.01)

    def test_spread_to_atr(self) -> None:
        assert spread_to_atr(0.00015, 0.0015) == pytest.approx(0.1)

    def test_classify_cost_state(self) -> None:
        assert classify_cost_state(5.0) == "acceptable"
        assert classify_cost_state(10.0) == "marginal"
        assert classify_cost_state(15.0) == "hostile"


class TestBarMetrics:
    def test_compute_bar_metrics_columns(self) -> None:
        idx = pd.date_range("2022-01-03", periods=30, freq="4h", tz="UTC")
        frame = pd.DataFrame(
            {
                "bid_c": 1.10,
                "ask_c": 1.1002,
                "bid_h": 1.1005,
                "bid_l": 1.0995,
                "ask_h": 1.1007,
                "ask_l": 1.0997,
                "close": 1.1001,
            },
            index=idx,
        )
        out = compute_bar_metrics("EUR_USD", frame)
        assert "spread_pips" in out.columns
        assert "spread_to_atr_pct" in out.columns
        assert "session" in out.columns
        assert out["session"].notna().all()


class TestDedupe:
    def test_dedupe_keep_last(self) -> None:
        t = datetime(2022, 1, 1, tzinfo=UTC)
        c1 = _make_candle("EUR_USD", t, 1.10, 1.1002)
        c2 = _make_candle("EUR_USD", t, 1.11, 1.1102)
        deduped, stats = dedupe_candles([c1, c2])
        assert stats.duplicates_dropped == 1
        assert deduped[0].bid_c == Decimal("1.11")


class TestHostileWindows:
    def test_flag_cost_hostile_top_decile(self) -> None:
        df = pd.DataFrame(
            {
                "instrument": ["EUR_USD"] * 5,
                "session": ["asian", "london", "ny", "london_ny_overlap", "asian"],
                "spread_to_atr_pct_median": [5.0, 6.0, 7.0, 8.0, 20.0],
                "spread_to_atr_pct_p90": [6.0, 7.0, 8.0, 9.0, 25.0],
                "spread_to_atr_pct_p95": [7.0, 8.0, 9.0, 10.0, 30.0],
            }
        )
        hostile = flag_cost_hostile_cells(df)
        assert any(h["spread_to_atr_pct_median"] == 20.0 for h in hostile)


@pytest.fixture
def fixture_db(tmp_path: Path) -> Path:
    db = tmp_path / "test.sqlite3"
    _build_fixture_db(db)
    return db


def test_build_cost_atlas_on_fixture_db(fixture_db: Path) -> None:
    result = build_cost_atlas(
        REPO_ROOT,
        instruments=("EUR_USD",),
        db_path=fixture_db,
        fold_plan_path=REPO_ROOT
        / "backtests"
        / "CAMPAIGN_011_random_entry_anchor"
        / "walk_forward"
        / "plan.json",
    )
    assert result.summary["strategy_evidence"] is False
    assert result.summary["bar_count"] >= 79
    assert result.provenance[0]["dedupe_policy"] == "keep_last"


@pytest.mark.skipif(
    not (REPO_ROOT / "data" / "campaign_002.sqlite3").is_file(),
    reason="local H4 store absent",
)
def test_build_cost_atlas_real_data_smoke() -> None:
    result = build_cost_atlas(REPO_ROOT, instruments=("EUR_USD",))
    assert result.summary["bar_count"] > 1000
    assert "cost_state_counts" in result.summary

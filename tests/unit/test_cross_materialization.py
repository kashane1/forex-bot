"""Phase 3 — non-USD cross materialization support.

Materialization (M1 → M5/M15/H1/H4M1) is price-agnostic; these tests prove
the instrument gate now accepts registered crosses, still rejects unknown
instruments, and that JPY-quote cross prices (0.01-pip scale) aggregate
exactly with provenance retained.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from forex_bot.data.m1_timeframe_materialization import (
    candle_to_record,
    materialize_pair,
)
from forex_bot.data.timeframe_aggregation import aggregate_m1_candles
from forex_bot.domain.candles import Candle


class _EmptyStore:
    """Store stub whose M1 query yields no rows (gate-acceptance probe)."""

    def query_candles(self, **_kwargs):
        return []


def _m1(instrument: str, ts: datetime, o, h, low, c) -> Candle:
    o, h, low, c = (Decimal(str(x)) for x in (o, h, low, c))
    return Candle(
        instrument=instrument, granularity="M1", time=ts, complete=True, volume=3,
        bid_o=o, bid_h=h, bid_l=low, bid_c=c,
        ask_o=o, ask_h=h, ask_l=low, ask_c=c,
        mid_o=o, mid_h=h, mid_l=low, mid_c=c,
    )


def test_materialize_pair_rejects_unknown_instrument():
    with pytest.raises(ValueError, match="supported universe"):
        materialize_pair(
            _EmptyStore(), "XAU_USD",
            from_utc=datetime(2024, 1, 1, tzinfo=UTC),
            to_utc=datetime(2024, 1, 2, tzinfo=UTC),
        )


def test_materialize_pair_accepts_registered_cross():
    # No M1 rows → empty result, but the gate must NOT reject the cross.
    result = materialize_pair(
        _EmptyStore(), "GBP_JPY",
        from_utc=datetime(2024, 1, 1, tzinfo=UTC),
        to_utc=datetime(2024, 1, 1, 0, 30, tzinfo=UTC),
    )
    assert result.instrument == "GBP_JPY"
    assert all(stats.rows_upserted == 0 for stats in result.targets.values())


def test_jpy_cross_m5_aggregation_is_exact():
    # Five consecutive M1 GBP_JPY bars at ~190 (0.01-pip scale).
    base = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
    bars = [
        _m1("GBP_JPY", base.replace(minute=0), "190.000", "190.050", "189.980", "190.010"),
        _m1("GBP_JPY", base.replace(minute=1), "190.010", "190.090", "190.000", "190.080"),
        _m1("GBP_JPY", base.replace(minute=2), "190.080", "190.120", "190.060", "190.070"),
        _m1("GBP_JPY", base.replace(minute=3), "190.070", "190.075", "189.900", "189.950"),
        _m1("GBP_JPY", base.replace(minute=4), "189.950", "190.000", "189.940", "189.990"),
    ]
    result = aggregate_m1_candles(bars, target="M5", missing_policy="omit")
    assert len(result.candles) == 1
    bar = result.candles[0]
    assert bar.complete is True
    assert bar.bid_o == Decimal("190.000")          # first open
    assert bar.bid_h == Decimal("190.120")          # max high
    assert bar.bid_l == Decimal("189.900")          # min low
    assert bar.bid_c == Decimal("189.990")          # last close
    assert bar.volume == 15                          # summed
    assert bar.time == base                          # bucket aligned to first M1


def test_cross_candle_to_record_retains_provenance_and_h4m1_storage_name():
    base = datetime(2024, 1, 1, tzinfo=UTC)
    bar = _m1("EUR_JPY", base, "160.000", "160.020", "159.990", "160.010")
    bar = bar.model_copy(update={"granularity": "H4"})
    # H4 derived from M1 is stored under the "H4M1" storage granularity.
    record = candle_to_record(bar, fetch_batch_id="batch-xyz", storage_granularity="H4M1")
    assert record.instrument == "EUR_JPY"
    assert record.granularity == "H4M1"
    assert record.fetch_batch_id == "batch-xyz"
    # JPY-scale prices survive the Decimal→float conversion unchanged.
    assert record.bid_c == 160.010

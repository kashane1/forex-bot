"""Tests for H4 -> D1AGG aggregation (Phase 1, infra-foundation-001).

Proves the synthetic daily bar is built only from complete H4 candles,
that weekend gaps are not flagged while weekday gaps are, that incomplete
days are classified rather than silently emitted, that the generated
timestamp clears the rollover blackout, and that provenance is recorded.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1, rollover_safe
from forex_bot.domain.candles import Candle, CandleFrame


def _h4(t, o, h, low, c, *, spread="0.0002", complete=True, volume=100):
    """One H4 candle. o/h/low/c accept strings or Decimals (exact)."""
    bo, bh, bl, bc = Decimal(str(o)), Decimal(str(h)), Decimal(str(low)), Decimal(str(c))
    sp = Decimal(spread)
    return Candle(
        instrument="EUR_USD", granularity="H4", time=t, complete=complete,
        volume=volume,
        bid_o=bo, bid_h=bh, bid_l=bl, bid_c=bc,
        ask_o=bo + sp, ask_h=bh + sp, ask_l=bl + sp, ask_c=bc + sp,
    )


def _h4_times(d: date) -> list[datetime]:
    """The 6 H4 open times (UTC) for the OANDA trading day ending `d`,
    in winter (EST): NY 17/21/01/05/09/13 -> UTC 22/02/06/10/14/18."""
    prev = d - timedelta(days=1)
    return [
        datetime(prev.year, prev.month, prev.day, 22, tzinfo=UTC),
        datetime(d.year, d.month, d.day, 2, tzinfo=UTC),
        datetime(d.year, d.month, d.day, 6, tzinfo=UTC),
        datetime(d.year, d.month, d.day, 10, tzinfo=UTC),
        datetime(d.year, d.month, d.day, 14, tzinfo=UTC),
        datetime(d.year, d.month, d.day, 18, tzinfo=UTC),
    ]


def _full_day(d: date, base: str = "1.1000") -> list[Candle]:
    """Six well-formed H4 candles for trading day `d`, monotone in price
    so the aggregate's max/min are predictable."""
    base_dec = Decimal(base)
    step = Decimal("0.0010")
    out = []
    for k, t in enumerate(_h4_times(d)):
        o = base_dec + k * step
        out.append(_h4(t, o, o + Decimal("0.0030"), o - Decimal("0.0030"), o + step))
    return out


def test_aggregates_full_day_from_h4_only():
    result = aggregate_h4_to_d1(_full_day(date(2024, 1, 9)), instrument="EUR_USD")
    assert len(result.candles) == 1
    c = result.candles[0]
    assert c.granularity == "D1AGG"
    # OHLC from the FIRST FIVE H4 candles only (the 6th is excluded).
    assert c.bid_o == Decimal("1.1000")   # candle 0 open
    assert c.bid_c == Decimal("1.1050")   # candle 4 close
    assert c.bid_h == Decimal("1.1070")   # max high over candles 0..4
    assert c.bid_l == Decimal("1.0970")   # min low over candles 0..4
    assert c.volume == 500                # 5 research candles x 100
    assert result.aggregated_count == 1
    assert result.day_reports[0].status == "aggregated"


def test_d1_timestamp_clears_the_rollover_blackout():
    result = aggregate_h4_to_d1(_full_day(date(2024, 1, 9)), instrument="EUR_USD")
    c = result.candles[0]
    assert rollover_safe(c.time)
    ny = c.time.astimezone(ZoneInfo("America/New_York"))
    assert ny.hour == 13  # research-day close — clear of the 17:00 rollover


def test_d1agg_candles_build_a_candle_frame():
    result = aggregate_h4_to_d1(_full_day(date(2024, 1, 9)), instrument="EUR_USD")
    frame = CandleFrame.from_candles("EUR_USD", "D1AGG", result.candles)
    assert len(frame) == 1
    assert frame.granularity == "D1AGG"


def test_incomplete_h4_candle_excludes_the_whole_day():
    day = _full_day(date(2024, 1, 9))
    day[2] = _h4(
        day[2].time, day[2].bid_o, day[2].bid_h, day[2].bid_l, day[2].bid_c,
        complete=False,
    )
    result = aggregate_h4_to_d1(day, instrument="EUR_USD")
    assert result.candles == []
    assert result.incomplete_count == 1
    assert result.day_reports[0].status == "incomplete"
    assert result.day_reports[0].h4_complete_count == 5


def test_partial_day_classified_incomplete_not_hidden():
    day = _full_day(date(2024, 1, 9))[:4]  # only 4 of 6 H4 candles
    result = aggregate_h4_to_d1(day, instrument="EUR_USD")
    assert result.candles == []
    assert result.day_reports[0].status == "incomplete"
    assert result.day_reports[0].h4_complete_count == 4


def test_weekend_produces_no_bar_and_is_not_a_holiday_gap():
    candles = _full_day(date(2024, 1, 12)) + _full_day(date(2024, 1, 15))
    result = aggregate_h4_to_d1(candles, instrument="EUR_USD")  # Fri + Mon
    assert result.aggregated_count == 2
    assert {r.trading_day for r in result.day_reports} == {
        date(2024, 1, 12), date(2024, 1, 15),
    }
    # Sat 13 / Sun 14 are weekends — never expected, never flagged.
    assert result.missing_weekdays == []


def test_missing_weekday_is_flagged_as_a_gap():
    candles = (
        _full_day(date(2024, 1, 8))   # Mon
        + _full_day(date(2024, 1, 9))   # Tue
        + _full_day(date(2024, 1, 11))  # Thu — Wed 10th deliberately skipped
    )
    result = aggregate_h4_to_d1(candles, instrument="EUR_USD")
    assert result.aggregated_count == 3
    assert result.missing_weekdays == [date(2024, 1, 10)]  # the Wednesday gap


def test_six_candles_with_wrong_slots_are_ambiguous():
    # Six candles spaced 1h apart — slot hours cannot match {17,21,1,5,9,13}.
    start = datetime(2024, 1, 9, 2, tzinfo=UTC)
    candles = [
        _h4(start + timedelta(hours=k), "1.1000", "1.2000", "1.0000", "1.1000")
        for k in range(6)
    ]
    result = aggregate_h4_to_d1(candles, instrument="EUR_USD")
    assert result.candles == []
    assert result.ambiguous_count == 1


def test_provenance_is_recorded_and_deterministic():
    result = aggregate_h4_to_d1(_full_day(date(2024, 1, 9)), instrument="EUR_USD")
    assert result.source_h4_count == 6
    assert len(result.source_hash) == 64  # sha256 hex digest
    assert result.alignment_hour == 17
    assert result.alignment_tz == "America/New_York"
    again = aggregate_h4_to_d1(_full_day(date(2024, 1, 9)), instrument="EUR_USD")
    assert again.source_hash == result.source_hash


def test_rejects_non_h4_input():
    native_d1 = Candle(
        instrument="EUR_USD", granularity="D",
        time=datetime(2024, 1, 9, tzinfo=UTC), complete=True, volume=1,
        bid_o=Decimal("1.1"), bid_h=Decimal("1.1"),
        bid_l=Decimal("1.1"), bid_c=Decimal("1.1"),
        ask_o=Decimal("1.1"), ask_h=Decimal("1.1"),
        ask_l=Decimal("1.1"), ask_c=Decimal("1.1"),
    )
    with pytest.raises(ValueError, match="only H4"):
        aggregate_h4_to_d1([native_d1])

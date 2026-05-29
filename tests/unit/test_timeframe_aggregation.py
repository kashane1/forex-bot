from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from forex_bot.data.timeframe_aggregation import aggregate_m1_candles
from forex_bot.domain.candles import Candle


def _m1(start: datetime, count: int, *, complete: bool = True) -> list[Candle]:
    candles: list[Candle] = []
    for i in range(count):
        base = Decimal("1.1000") + Decimal(i) / Decimal("10000")
        candles.append(
            Candle(
                instrument="EUR_USD",
                granularity="M1",
                time=start + timedelta(minutes=i),
                complete=complete,
                volume=i + 1,
                bid_o=base,
                bid_h=base + Decimal("0.0003"),
                bid_l=base - Decimal("0.0002"),
                bid_c=base + Decimal("0.0001"),
                ask_o=base + Decimal("0.0002"),
                ask_h=base + Decimal("0.0005"),
                ask_l=base,
                ask_c=base + Decimal("0.0003"),
                mid_o=base + Decimal("0.0001"),
                mid_h=base + Decimal("0.0004"),
                mid_l=base - Decimal("0.0001"),
                mid_c=base + Decimal("0.0002"),
            )
        )
    return candles


def test_m1_to_m5_ohlcv_and_timestamp() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    result = aggregate_m1_candles(_m1(start, 5), target="M5")
    candle = result.candles[0]
    assert candle.time == start
    assert candle.complete is True
    assert candle.volume == 15
    assert candle.bid_o == Decimal("1.1000")
    assert candle.bid_h == Decimal("1.1007")
    assert candle.bid_l == Decimal("1.0998")
    assert candle.bid_c == Decimal("1.1005")
    assert candle.ask_c - candle.bid_c == Decimal("0.0002")


def test_m1_to_m15_h1_h4_counts() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    assert len(aggregate_m1_candles(_m1(start, 15), target="M15").candles) == 1
    assert len(aggregate_m1_candles(_m1(start, 60), target="H1").candles) == 1
    h4_start = datetime(2024, 1, 1, 22, tzinfo=UTC)
    assert len(aggregate_m1_candles(_m1(h4_start, 240), target="H4").candles) == 1


def test_missing_minute_omits_block_by_default() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    candles = _m1(start, 5)
    del candles[2]
    result = aggregate_m1_candles(candles, target="M5")
    assert result.candles == []
    assert result.omitted_incomplete_blocks == 1
    assert result.coverage[0].missing_minutes == 1


def test_incomplete_source_marks_incomplete_when_configured() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    candles = _m1(start, 5)
    candles[3] = candles[3].model_copy(update={"complete": False})
    result = aggregate_m1_candles(candles, target="M5", missing_policy="mark_incomplete")
    assert len(result.candles) == 1
    assert result.candles[0].complete is False
    assert result.coverage[0].complete_source_minutes == 4


def test_d1agg_from_m1_uses_existing_research_day_timestamp() -> None:
    start = datetime(2024, 1, 1, 22, tzinfo=UTC)
    candles = _m1(start, 6 * 240)
    result = aggregate_m1_candles(candles, target="D1AGG")
    assert len(result.candles) == 1
    assert result.candles[0].granularity == "D1AGG"
    assert result.candles[0].time == datetime(2024, 1, 2, 18, tzinfo=UTC)


def test_no_synthetic_weekend_fill() -> None:
    friday = datetime(2024, 1, 5, 21, 55, tzinfo=UTC)
    monday = datetime(2024, 1, 8, 0, 0, tzinfo=UTC)
    result = aggregate_m1_candles(_m1(friday, 5) + _m1(monday, 5), target="M5")
    assert [candle.time for candle in result.candles] == [friday, monday]


# --------------------------------------------------------------------------- #
# CAMPAIGN_026 diagnostic timeframes: M3 and M30 (M1-derived, identical rules)
# --------------------------------------------------------------------------- #
def test_m1_to_m3_ohlcv_and_timestamp() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    result = aggregate_m1_candles(_m1(start, 3), target="M3")
    assert len(result.candles) == 1
    candle = result.candles[0]
    assert candle.granularity == "M3"
    assert candle.time == start  # bucket-start timestamp
    assert candle.complete is True
    assert candle.volume == 1 + 2 + 3  # source volumes summed
    assert candle.bid_o == Decimal("1.1000")  # first source open
    assert candle.bid_h == Decimal("1.1005")  # max source high
    assert candle.bid_l == Decimal("1.0998")  # min source low
    assert candle.bid_c == Decimal("1.1003")  # last source close
    assert candle.ask_c - candle.bid_c == Decimal("0.0002")  # bid/ask preserved


def test_m1_to_m30_ohlcv_and_timestamp() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    result = aggregate_m1_candles(_m1(start, 30), target="M30")
    assert len(result.candles) == 1
    candle = result.candles[0]
    assert candle.granularity == "M30"
    assert candle.time == start
    assert candle.volume == sum(range(1, 31))  # 465
    assert candle.bid_o == Decimal("1.1000")


def test_m3_m30_bucket_alignment() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    # 6 contiguous M1 -> two complete M3 buckets at :00 and :03
    m3 = aggregate_m1_candles(_m1(start, 6), target="M3")
    assert [c.time.strftime("%H:%M") for c in m3.candles] == ["00:00", "00:03"]
    # 60 contiguous M1 -> two complete M30 buckets at :00 and :30
    m30 = aggregate_m1_candles(_m1(start, 60), target="M30")
    assert [c.time.strftime("%H:%M") for c in m30.candles] == ["00:00", "00:30"]


def test_m3_missing_minute_omits_block_by_default() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    candles = _m1(start, 3)
    del candles[1]  # drop 00:01 -> bucket 00:00 incomplete
    result = aggregate_m1_candles(candles, target="M3")
    assert result.candles == []
    assert result.omitted_incomplete_blocks == 1
    assert result.coverage[0].missing_minutes == 1


def test_m30_incomplete_marks_incomplete_when_configured() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    candles = _m1(start, 30)
    candles[5] = candles[5].model_copy(update={"complete": False})
    result = aggregate_m1_candles(candles, target="M30", missing_policy="mark_incomplete")
    assert len(result.candles) == 1
    assert result.candles[0].complete is False
    assert result.coverage[0].complete_source_minutes == 29

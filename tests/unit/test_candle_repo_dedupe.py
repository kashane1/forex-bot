"""Tests for canonical candle deduplication at the repository load boundary."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from forex_bot.data.candle_dedupe import (
    DEDUPE_POLICY,
    candle_utc_time,
    dedupe_candles,
)
from forex_bot.data.repositories import CandleRepo
from forex_bot.domain.candles import Candle, CandleFrame


def _candle(
    instrument: str,
    *,
    time: datetime,
    close_offset: Decimal = Decimal("0.0000"),
    complete: bool = True,
) -> Candle:
    o = Decimal("1.1000") + close_offset
    return Candle(
        instrument=instrument,
        granularity="H4",
        time=time,
        complete=complete,
        volume=1000,
        bid_o=o,
        bid_h=o + Decimal("0.0020"),
        bid_l=o - Decimal("0.0020"),
        bid_c=o + Decimal("0.0005"),
        ask_o=o + Decimal("0.0002"),
        ask_h=o + Decimal("0.0022"),
        ask_l=o - Decimal("0.0018"),
        ask_c=o + Decimal("0.0007"),
    )


def test_dedupe_reduces_duplicate_utc_timestamps_to_one_candle():
    t1 = datetime(2026, 5, 19, 21, 0, tzinfo=UTC)
    t2 = datetime.fromisoformat("2026-05-19T14:00:00-07:00")
    first = _candle("AUD_USD", time=t1, close_offset=Decimal("0.0000"))
    second = _candle("AUD_USD", time=t2, close_offset=Decimal("0.0010"))
    deduped, stats = dedupe_candles([first, second])
    assert len(deduped) == 1
    assert stats.duplicates_detected == 1
    assert stats.duplicates_dropped == 1
    assert stats.dedupe_policy == DEDUPE_POLICY
    assert deduped[0].bid_c == second.bid_c


def test_keep_last_is_deterministic():
    base = datetime(2022, 5, 6, 13, 0, tzinfo=UTC)
    alt = datetime(2022, 5, 6, 13, 0, tzinfo=UTC)
    rows = [
        _candle("AUD_USD", time=base, close_offset=Decimal("0.0001")),
        _candle("AUD_USD", time=alt, close_offset=Decimal("0.0009")),
    ]
    deduped_a, _ = dedupe_candles(rows)
    deduped_b, _ = dedupe_candles(rows)
    assert deduped_a[0].bid_c == deduped_b[0].bid_c == rows[-1].bid_c


def test_dedupe_output_is_monotonic_by_timestamp():
    rows = [
        _candle("EUR_USD", time=datetime(2024, 1, 1, 9, 0, tzinfo=UTC)),
        _candle("EUR_USD", time=datetime(2024, 1, 1, 13, 0, tzinfo=UTC)),
        _candle("EUR_USD", time=datetime(2024, 1, 1, 17, 0, tzinfo=UTC)),
    ]
    deduped, _ = dedupe_candles(rows)
    times = [candle_utc_time(c) for c in deduped]
    assert times == sorted(times)


def test_no_duplicates_reach_candle_frame_after_repo_list(temp_db):
    repo = CandleRepo(temp_db)
    t_utc = datetime(2026, 5, 19, 21, 0, tzinfo=UTC)
    t_offset = datetime.fromisoformat("2026-05-19T14:00:00-07:00")
    repo.upsert_many(
        [
            _candle("AUD_USD", time=t_utc),
            _candle("AUD_USD", time=t_offset, close_offset=Decimal("0.0100")),
        ],
        source="oanda-practice",
        price_components="BA",
        request_hash="x",
    )
    rows = repo.list("AUD_USD", "H4", completed_only=True)
    frame = CandleFrame.from_candles("AUD_USD", "H4", rows)
    assert len(rows) == 1
    assert frame.df.index.is_unique
    assert repo.last_list_dedupe_stats is not None
    assert repo.last_list_dedupe_stats.duplicates_dropped == 1


def test_completed_only_filter_still_applies(temp_db):
    repo = CandleRepo(temp_db)
    repo.upsert_many(
        [
            _candle("EUR_USD", time=datetime(2024, 1, 1, 9, 0, tzinfo=UTC), complete=True),
            _candle("EUR_USD", time=datetime(2024, 1, 1, 13, 0, tzinfo=UTC), complete=False),
        ],
        source="oanda-practice",
        price_components="BA",
        request_hash="x",
    )
    rows = repo.list("EUR_USD", "H4", completed_only=True)
    assert len(rows) == 1
    assert rows[0].complete is True


def test_no_change_for_already_unique_data(temp_db):
    repo = CandleRepo(temp_db)
    candles = [
        _candle("EUR_USD", time=datetime(2024, 1, 1, 9, 0, tzinfo=UTC) + timedelta(hours=4 * k))
        for k in range(5)
    ]
    repo.upsert_many(
        candles,
        source="oanda-practice",
        price_components="BA",
        request_hash="x",
    )
    rows = repo.list("EUR_USD", "H4", completed_only=True)
    assert len(rows) == 5
    stats = repo.last_list_dedupe_stats
    assert stats is not None
    assert stats.duplicates_dropped == 0


def test_query_ordering_stable_with_rowid_tiebreak(temp_db):
    repo = CandleRepo(temp_db)
    t_a = datetime(2022, 5, 6, 13, 0, tzinfo=UTC)
    t_b = datetime(2022, 5, 6, 17, 0, tzinfo=UTC)
    repo.upsert_many(
        [
            _candle("GBP_USD", time=t_a, close_offset=Decimal("0.0001")),
            _candle("GBP_USD", time=t_b, close_offset=Decimal("0.0002")),
        ],
        source="oanda-practice",
        price_components="BA",
        request_hash="a",
    )
    first = repo.list("GBP_USD", "H4", completed_only=True)
    second = repo.list("GBP_USD", "H4", completed_only=True)
    assert [c.bid_c for c in first] == [c.bid_c for c in second]


def test_list_with_dedupe_stats_returns_matching_counts(temp_db):
    repo = CandleRepo(temp_db)
    t_utc = datetime(2026, 5, 19, 21, 0, tzinfo=UTC)
    t_offset = datetime.fromisoformat("2026-05-19T14:00:00-07:00")
    repo.upsert_many(
        [
            _candle("USD_JPY", time=t_utc),
            _candle("USD_JPY", time=t_offset),
        ],
        source="oanda-practice",
        price_components="BA",
        request_hash="x",
    )
    rows, stats = repo.list_with_dedupe_stats("USD_JPY", "H4", completed_only=True)
    assert len(rows) == 1
    assert stats.raw_count == 2
    assert stats.deduped_count == 1

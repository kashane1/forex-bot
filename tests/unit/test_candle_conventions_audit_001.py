"""Phase 1 audit: candle frame conventions, complete flag, dedupe policy."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from forex_bot.data.candle_dedupe import DEDUPE_POLICY, dedupe_candles
from forex_bot.domain.candles import Candle, CandleFrame


def _candle(ts: datetime, *, complete: bool, bid_c: str = "1.1000") -> Candle:
    bc = Decimal(bid_c)
    sp = Decimal("0.0002")
    return Candle(
        instrument="EUR_USD",
        granularity="H4",
        time=ts,
        complete=complete,
        bid_o=bc,
        bid_h=bc + Decimal("0.0003"),
        bid_l=bc - Decimal("0.0003"),
        bid_c=bc,
        ask_o=bc + sp,
        ask_h=bc + sp + Decimal("0.0003"),
        ask_l=bc + sp - Decimal("0.0003"),
        ask_c=bc + sp,
    )


def test_candle_frame_index_matches_input_times_sorted():
    t0 = datetime(2024, 1, 2, 6, tzinfo=UTC)
    t1 = datetime(2024, 1, 2, 10, tzinfo=UTC)
    frame = CandleFrame.from_candles("EUR_USD", "H4", [_candle(t1, complete=True), _candle(t0, complete=True)])
    assert list(frame.df.index) == [t0, t1]


def test_completed_only_drops_incomplete_bars():
    t0 = datetime(2024, 1, 2, 6, tzinfo=UTC)
    t1 = datetime(2024, 1, 2, 10, tzinfo=UTC)
    frame = CandleFrame.from_candles(
        "EUR_USD",
        "H4",
        [_candle(t0, complete=True), _candle(t1, complete=False)],
    )
    completed = frame.completed_only()
    assert len(completed) == 1
    assert completed.df.index[0] == t0


def test_dedupe_policy_is_keep_last_documented():
    assert DEDUPE_POLICY == "keep_last"
    t = datetime(2024, 1, 2, 6, tzinfo=UTC)
    first = _candle(t, complete=True, bid_c="1.1000")
    second = _candle(t, complete=True, bid_c="1.2000")
    out, stats = dedupe_candles([first, second])
    assert len(out) == 1
    assert out[0].bid_c == Decimal("1.2000")
    assert stats.duplicates_dropped == 1

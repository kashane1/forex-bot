"""CAMPAIGN_029 data loader — range bars + M1 index + H4M1/D1AGG frames.

Builds the inputs the M1-resolved engine (``range_bar_execution``) needs from the
local Postgres research store, in **one streaming M1 pass** (no broker/network):

  * 10-pip USD_JPY range bars from **M1 mid** (``non_time_bars.build_range_bars``);
  * an :class:`M1Index` (numeric M1 view) for fill/stop resolution;
  * the **H4M1** context frame (granularity ``H4M1``, source ``m1_materialized``);
  * the **native-H4 → D1AGG** frame (``aggregate_h4_to_d1`` over native H4).

HTF frames are loaded from the corpus start (max EMA warmup) regardless of the
evidence window; range bars / decisions are restricted to the requested window.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime

import numpy as np

from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1
from forex_bot.data.m1_corpus_validation import _row_to_candle, iter_m1_chunks, pair_range
from forex_bot.data.non_time_bars import RangeBar, RangeBarConfig, pip_size, stream_range_bars
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.research.range_bar_execution import M1Index

INSTRUMENT = "USD_JPY"
THRESHOLD_PIPS = 10.0
MATERIALIZED_SOURCE = "m1_materialized"


@dataclass(frozen=True)
class Campaign029Inputs:
    range_bars: list[RangeBar]
    m1_index: M1Index
    h4_frame: CandleFrame
    d1agg_frame: CandleFrame | None
    decision_times: list[datetime]
    m1_rows_consumed: int


def _utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def build_range_bars_and_index(
    store: PostgresCandleStore, *, from_utc: datetime, to_utc: datetime, chunk_days: int = 14
) -> tuple[list[RangeBar], M1Index, int]:
    """Single streaming M1 pass: build range bars AND the numeric M1 index."""
    pip = float(pip_size(INSTRUMENT))
    times: list[datetime] = []
    lows: list[float] = []
    highs: list[float] = []
    opens: list[float] = []
    half_spreads: list[float] = []
    consumed = 0
    last_time: datetime | None = None

    def m1_stream() -> Iterator[Candle]:
        nonlocal consumed, last_time
        for chunk in iter_m1_chunks(
            store, instrument=INSTRUMENT, start_utc=from_utc, end_utc=to_utc, chunk_days=chunk_days
        ):
            for row in chunk:
                candle = _row_to_candle(row, instrument=INSTRUMENT)
                t = _utc(candle.time)
                if last_time is not None and t == last_time:
                    continue  # chunk-edge overlap
                last_time = t
                consumed += 1
                # record numeric M1 view
                bl, bh = candle.bid_l, candle.bid_h
                al, ah = candle.ask_l, candle.ask_h
                ml = candle.mid_l if candle.mid_l is not None else ((bl + al) / 2 if bl is not None and al is not None else None)
                mh = candle.mid_h if candle.mid_h is not None else ((bh + ah) / 2 if bh is not None and ah is not None else None)
                mo = candle.mid_o if candle.mid_o is not None else (
                    (candle.bid_o + candle.ask_o) / 2 if candle.bid_o is not None and candle.ask_o is not None else None
                )
                if ml is None or mh is None:
                    raise ValueError(f"missing M1 low/high at {t}")
                hs = float((candle.ask_o - candle.bid_o) / 2) / pip if candle.bid_o is not None and candle.ask_o is not None else 0.0
                times.append(t)
                lows.append(float(ml))
                highs.append(float(mh))
                opens.append(float(mo) if mo is not None else float("nan"))
                half_spreads.append(hs)
                yield candle

    cfg = RangeBarConfig(
        instrument=INSTRUMENT, threshold_pips=THRESHOLD_PIPS, price_basis="mid",
        emit_incomplete_final=False, require_sorted=True, duplicate_policy="reject",
    )
    range_bars = list(stream_range_bars(m1_stream(), cfg))
    index = M1Index(
        times=times,
        mid_low=np.array(lows),
        mid_high=np.array(highs),
        mid_open=np.array(opens),
        half_spread=np.array(half_spreads),
    )
    return range_bars, index, consumed


def load_h4m1_frame(store: PostgresCandleStore, *, from_utc: datetime, to_utc: datetime) -> CandleFrame:
    rows = store.query_candles(
        instrument=INSTRUMENT, granularity="H4M1", start_utc=from_utc, end_utc=to_utc, source=MATERIALIZED_SOURCE
    )
    candles = [
        _row_to_candle({**r, "granularity": "H4"}, instrument=INSTRUMENT) for r in rows if r.get("complete")
    ]
    candles.sort(key=lambda c: c.time)
    return CandleFrame.from_candles(INSTRUMENT, "H4", candles)


def build_d1agg_frame(store: PostgresCandleStore, *, from_utc: datetime, to_utc: datetime) -> CandleFrame | None:
    rows = store.query_candles(
        instrument=INSTRUMENT, granularity="H4", start_utc=from_utc, end_utc=to_utc, exclude_sources=(MATERIALIZED_SOURCE,)
    )
    native_h4 = [_row_to_candle({**r, "granularity": "H4"}, instrument=INSTRUMENT) for r in rows if r.get("complete")]
    if not native_h4:
        return None
    native_h4.sort(key=lambda c: c.time)
    agg = aggregate_h4_to_d1(native_h4, instrument=INSTRUMENT)
    d1_candles = [
        Candle(
            instrument=INSTRUMENT, granularity="D1AGG", time=_utc(c.time), complete=True, volume=c.volume,
            mid_o=c.mid_o, mid_h=c.mid_h, mid_l=c.mid_l, mid_c=c.mid_c,
            bid_o=c.bid_o, bid_h=c.bid_h, bid_l=c.bid_l, bid_c=c.bid_c,
            ask_o=c.ask_o, ask_h=c.ask_h, ask_l=c.ask_l, ask_c=c.ask_c,
        )
        for c in agg.candles
    ]
    return CandleFrame.from_candles(INSTRUMENT, "D1AGG", d1_candles)


def load_campaign_029_inputs(
    store: PostgresCandleStore, *, from_utc: datetime, to_utc: datetime, chunk_days: int = 14
) -> Campaign029Inputs:
    """Build all engine inputs. HTF frames span the full corpus (max EMA warmup)."""
    from_utc, to_utc = _utc(from_utc), _utc(to_utc)
    pr = pair_range(store, INSTRUMENT)
    htf_from = pr.start_utc  # full history for EMA warmup
    range_bars, m1_index, consumed = build_range_bars_and_index(
        store, from_utc=from_utc, to_utc=to_utc, chunk_days=chunk_days
    )
    h4_frame = load_h4m1_frame(store, from_utc=htf_from, to_utc=to_utc)
    d1agg_frame = build_d1agg_frame(store, from_utc=htf_from, to_utc=to_utc)
    decision_times = [b.close_time for b in range_bars if not b.incomplete]
    return Campaign029Inputs(
        range_bars=range_bars,
        m1_index=m1_index,
        h4_frame=h4_frame,
        d1agg_frame=d1agg_frame,
        decision_times=decision_times,
        m1_rows_consumed=consumed,
    )


def staleness_stats(
    decision_times: list[datetime],
    aligned: list[tuple[str, datetime | None, str | None]],
    *,
    max_staleness_seconds: float,
) -> dict:
    """Missing / stale counts + max staleness for one HTF input over decisions."""
    n = len(decision_times)
    missing = 0
    stale = 0
    max_gap = 0.0
    gaps: list[float] = []
    for dt, (_label, ftime, block) in zip(decision_times, aligned, strict=True):
        if ftime is None or block:
            missing += 1
            continue
        gap = (_utc(dt) - _utc(ftime)).total_seconds()
        gaps.append(gap)
        max_gap = max(max_gap, gap)
        if gap > max_staleness_seconds:
            stale += 1
    gaps.sort()
    p99 = gaps[min(len(gaps) - 1, int(0.99 * (len(gaps) - 1)))] if gaps else None
    return {
        "decisions": n,
        "missing": missing,
        "stale_over_bound": stale,
        "max_staleness_seconds": round(max_gap, 1),
        "p99_staleness_seconds": round(p99, 1) if p99 is not None else None,
        "max_staleness_bound_seconds": max_staleness_seconds,
        "available_and_fresh": n - missing - stale,
    }

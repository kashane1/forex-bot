"""CAMPAIGN_021 Postgres M1 → M15/H1/H4 + native H4→D1AGG frame loading."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1
from forex_bot.data.m1_corpus_validation import (
    MAJOR_PAIRS,
    _dedupe_candles_by_time,
    _row_to_candle,
    iter_m1_chunks,
)
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.timeframe_aggregation import aggregate_m1_candles
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.features.htf_align import align_last_completed
from forex_bot.features.ltf_htf_alignment import align_ltf_execution_context

D1AGG_SOURCE = "native_h4_derived_d1agg"

_INSTRUMENT_SPECS: dict[str, dict[str, Any]] = {
    "EUR_USD": {"pip_location": -4, "display_precision": 5, "margin_rate": "0.02"},
    "GBP_USD": {"pip_location": -4, "display_precision": 5, "margin_rate": "0.03"},
    "USD_JPY": {"pip_location": -2, "display_precision": 3, "margin_rate": "0.04"},
    "AUD_USD": {"pip_location": -4, "display_precision": 5, "margin_rate": "0.02"},
    "USD_CAD": {"pip_location": -4, "display_precision": 5, "margin_rate": "0.02"},
    "USD_CHF": {"pip_location": -4, "display_precision": 5, "margin_rate": "0.03"},
    "NZD_USD": {"pip_location": -4, "display_precision": 5, "margin_rate": "0.03"},
}


def instrument_for(name: str) -> Instrument:
    spec = _INSTRUMENT_SPECS.get(name)
    if spec is None:
        raise ValueError(f"unsupported instrument: {name}")
    return Instrument(
        name=name,
        type="CURRENCY",
        display_precision=int(spec["display_precision"]),
        pip_location=int(spec["pip_location"]),
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        maximum_order_units=Decimal("100000000"),
        margin_rate=Decimal(str(spec["margin_rate"])),
    )


@dataclass(frozen=True)
class C021Frames:
    instrument: str
    m15: CandleFrame
    h1: CandleFrame
    h4: CandleFrame
    d1agg: CandleFrame
    d1agg_source: str = D1AGG_SOURCE
    m1_row_count: int = 0


def _filter_completed_in_range(
    candles: list[Candle], *, from_dt: datetime, to_dt: datetime, granularity: str
) -> list[Candle]:
    out: list[Candle] = []
    for c in candles:
        if not c.complete:
            continue
        t = c.time.astimezone(UTC)
        if from_dt <= t <= to_dt:
            out.append(c)
    return sorted(out, key=lambda x: x.time)


def load_c021_frames(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_dt: datetime,
    to_dt: datetime,
) -> C021Frames:
    if instrument not in MAJOR_PAIRS:
        raise ValueError(f"instrument not in CAMPAIGN_021 universe: {instrument}")
    m15: list[Candle] = []
    h1: list[Candle] = []
    h4_m1: list[Candle] = []
    m1_rows = 0
    for chunk in iter_m1_chunks(
        store,
        instrument=instrument,
        start_utc=from_dt,
        end_utc=to_dt,
        chunk_days=30,
    ):
        m1_rows += len(chunk)
        candles = [_row_to_candle(row, instrument=instrument) for row in chunk]
        m15.extend(aggregate_m1_candles(candles, target="M15", missing_policy="omit").candles)
        h1.extend(aggregate_m1_candles(candles, target="H1", missing_policy="omit").candles)
        h4_m1.extend(aggregate_m1_candles(candles, target="H4", missing_policy="omit").candles)
    m15 = _filter_completed_in_range(
        _dedupe_candles_by_time(m15), from_dt=from_dt, to_dt=to_dt, granularity="M15"
    )
    h1 = _filter_completed_in_range(
        _dedupe_candles_by_time(h1), from_dt=from_dt, to_dt=to_dt, granularity="H1"
    )
    h4_m1 = _filter_completed_in_range(
        _dedupe_candles_by_time(h4_m1), from_dt=from_dt, to_dt=to_dt, granularity="H4"
    )
    native_rows = store.query_candles(
        instrument=instrument,
        granularity="H4",
        start_utc=from_dt,
        end_utc=to_dt,
    )
    native_h4 = [
        _row_to_candle({**r, "granularity": "H4"}, instrument=instrument)
        for r in native_rows
        if r.get("complete")
    ]
    d1_result = aggregate_h4_to_d1(native_h4, instrument=instrument)
    d1_candles = _filter_completed_in_range(
        d1_result.candles, from_dt=from_dt, to_dt=to_dt, granularity="D1AGG"
    )
    return C021Frames(
        instrument=instrument,
        m15=CandleFrame.from_candles(instrument, "M15", m15),
        h1=CandleFrame.from_candles(instrument, "H1", h1),
        h4=CandleFrame.from_candles(instrument, "H4", h4_m1),
        d1agg=CandleFrame.from_candles(instrument, "D1AGG", d1_candles),
        m1_row_count=m1_rows,
    )


def pair_data_preflight(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_dt: datetime,
    to_dt: datetime,
    sample_decisions: int = 200,
) -> dict[str, Any]:
    frames = load_c021_frames(store, instrument, from_dt=from_dt, to_dt=to_dt)
    m15_df = frames.m15.completed_only().df
    h1_df = frames.h1.completed_only().df
    h4_df = frames.h4.completed_only().df
    d1_df = frames.d1agg.completed_only().df
    blocked_htf = 0
    stale_htf = 0
    lookahead_violations = 0
    if len(m15_df) >= 10:
        step = max(1, len(m15_df) // sample_decisions)
        decisions = m15_df.index[::step]
        for ts in decisions:
            decision = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
            for frame, cols, prefix in (
                (h1_df.reset_index(), ["close"], "h1"),
                (h4_df.reset_index(), ["close"], "h4"),
                (d1_df.reset_index(), ["close"], "d1agg"),
            ):
                if frame.empty:
                    blocked_htf += 1
                    continue
                if "time" not in frame.columns:
                    frame = frame.rename(columns={frame.columns[0]: "time"})
                aligned = align_last_completed(
                    pd.DatetimeIndex([decision]),
                    frame,
                    cols,
                    prefix=prefix,
                )
                reason_col = f"{prefix}_blocked_reason"
                if reason_col in aligned.columns and aligned[reason_col].iloc[0]:
                    blocked_htf += 1
                time_col = f"{prefix}_{cols[0]}_time"
                if time_col in aligned.columns:
                    ft = aligned[time_col].iloc[0]
                    if ft is not None and hasattr(ft, "to_pydatetime"):
                        ft_dt = ft.to_pydatetime()
                        if ft_dt > decision:
                            lookahead_violations += 1
    return {
        "instrument": instrument,
        "from_utc": from_dt.isoformat(),
        "to_utc": to_dt.isoformat(),
        "m15_count": len(m15_df),
        "h1_count": len(h1_df),
        "h4_count": len(h4_df),
        "d1agg_count": len(d1_df),
        "d1agg_source": frames.d1agg_source,
        "m1_rows_loaded": frames.m1_row_count,
        "m15_first": m15_df.index.min().isoformat() if len(m15_df) else None,
        "m15_last": m15_df.index.max().isoformat() if len(m15_df) else None,
        "htf_blocked_samples": blocked_htf,
        "htf_stale_samples": stale_htf,
        "lookahead_violations": lookahead_violations,
        "status": "PASS"
        if len(m15_df) >= 120 and len(d1_df) >= 20 and lookahead_violations == 0
        else "FAIL",
    }


def build_data_feature_preflight(
    store: PostgresCandleStore,
    *,
    splits: dict[str, tuple[str, str]],
    pairs: list[str],
) -> dict[str, Any]:
    by_pair: dict[str, Any] = {}
    blocked: list[str] = []
    for instrument in pairs:
        train_from, train_to = splits["train"]
        from_dt = datetime.fromisoformat(train_from).replace(tzinfo=UTC)
        to_dt = datetime.fromisoformat(train_to).replace(hour=23, minute=59, tzinfo=UTC)
        report = pair_data_preflight(store, instrument, from_dt=from_dt, to_dt=to_dt)
        by_pair[instrument] = report
        if report["status"] != "PASS":
            blocked.append(instrument)
    return {
        "campaign_id": "CAMPAIGN_021",
        "d1agg_source": D1AGG_SOURCE,
        "m1_derived_d1agg_used": False,
        "pairs": by_pair,
        "blocked_pairs": blocked,
        "preflight_ok": not blocked,
        "not_approved": True,
    }

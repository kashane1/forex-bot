"""CAMPAIGN_024 frame loading — materialized M1-derived bars from Postgres.

M5 execution + M15/H1/H4 context come from the materialized M1-derived store
(``source=m1_materialized``); D1AGG comes from native-H4-derived aggregation.
M1-derived D1AGG is **not** used. This is scaffold infrastructure only — it loads
and shapes frames for the preflight; it does not run evidence.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pandas as pd

from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1
from forex_bot.data.m1_corpus_validation import MAJOR_PAIRS, _row_to_candle
from forex_bot.data.m1_timeframe_materialization import (
    MATERIALIZED_SOURCE,
    STORAGE_GRANULARITY,
    aggregate_m1_window,
)
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.features.htf_align import align_last_completed

D1AGG_SOURCE = "native_h4_derived_d1agg"
ALLOW_LIVE_AGGREGATION_ENV = "FOREX_BOT_ALLOW_LIVE_M1_AGGREGATION"

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


def live_aggregation_enabled() -> bool:
    return os.environ.get(ALLOW_LIVE_AGGREGATION_ENV, "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


@dataclass(frozen=True)
class C024Frames:
    instrument: str
    m5: CandleFrame
    m15: CandleFrame
    h1: CandleFrame
    h4: CandleFrame
    d1agg: CandleFrame
    d1agg_source: str = D1AGG_SOURCE
    materialized_source: str = MATERIALIZED_SOURCE


def _filter_completed_in_range(
    candles: list[Candle], *, from_dt: datetime, to_dt: datetime
) -> list[Candle]:
    out: list[Candle] = []
    for candle in candles:
        if not candle.complete:
            continue
        ts = candle.time.astimezone(UTC)
        if from_dt <= ts <= to_dt:
            out.append(candle)
    return sorted(out, key=lambda item: item.time)


def _load_materialized_granularity(
    store: PostgresCandleStore,
    instrument: str,
    storage_granularity: str,
    frame_granularity: str,
    *,
    from_dt: datetime,
    to_dt: datetime,
) -> list[Candle]:
    rows = store.query_candles(
        instrument=instrument,
        granularity=storage_granularity,
        start_utc=from_dt,
        end_utc=to_dt,
        source=MATERIALIZED_SOURCE,
    )
    candles = [
        _row_to_candle({**row, "granularity": frame_granularity}, instrument=instrument)
        for row in rows
    ]
    return _filter_completed_in_range(candles, from_dt=from_dt, to_dt=to_dt)


def _load_native_h4(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_dt: datetime,
    to_dt: datetime,
) -> list[Candle]:
    rows = store.query_candles(
        instrument=instrument,
        granularity="H4",
        start_utc=from_dt,
        end_utc=to_dt,
        exclude_sources=(MATERIALIZED_SOURCE,),
    )
    return _filter_completed_in_range(
        [
            _row_to_candle({**row, "granularity": "H4"}, instrument=instrument)
            for row in rows
            if row.get("complete")
        ],
        from_dt=from_dt,
        to_dt=to_dt,
    )


def check_materialized_coverage(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_dt: datetime,
    to_dt: datetime,
    min_m5: int = 500,
    min_m15: int = 120,
) -> dict[str, Any]:
    counts = {
        granularity: store.count_candles(
            instrument=instrument,
            granularity=STORAGE_GRANULARITY[granularity],
            source=MATERIALIZED_SOURCE,
            start_utc=from_dt,
            end_utc=to_dt,
        )
        for granularity in ("M5", "M15", "H1", "H4")
    }
    ok = (
        counts["M5"] >= min_m5
        and counts["M15"] >= min_m15
        and counts["H1"] > 0
        and counts["H4"] > 0
    )
    return {
        "instrument": instrument,
        "from_utc": from_dt.isoformat(),
        "to_utc": to_dt.isoformat(),
        "counts": counts,
        "materialized_source": MATERIALIZED_SOURCE,
        "status": "PASS" if ok else "FAIL",
    }


def load_c024_frames(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_dt: datetime,
    to_dt: datetime,
    allow_live_aggregation: bool | None = None,
) -> C024Frames:
    if instrument not in MAJOR_PAIRS:
        raise ValueError(f"instrument not in CAMPAIGN_024 universe: {instrument}")
    use_live = (
        live_aggregation_enabled()
        if allow_live_aggregation is None
        else allow_live_aggregation
    )
    coverage = check_materialized_coverage(store, instrument, from_dt=from_dt, to_dt=to_dt)
    if coverage["status"] != "PASS":
        if not use_live:
            raise SystemExit(
                f"BLOCKED_DATA_PRECONDITION: materialized coverage FAIL for "
                f"{instrument}: {coverage['counts']}. Run "
                "scripts/materialize_m1_derived_timeframes.py --all-majors or set "
                f"{ALLOW_LIVE_AGGREGATION_ENV}=1 for debug fallback."
            )
        live_frames = aggregate_m1_window(store, instrument, from_utc=from_dt, to_utc=to_dt)
        m5 = live_frames["M5"]
        m15 = live_frames["M15"]
        h1 = live_frames["H1"]
        h4 = live_frames["H4"]
    else:
        m5 = _load_materialized_granularity(
            store, instrument, STORAGE_GRANULARITY["M5"], "M5", from_dt=from_dt, to_dt=to_dt
        )
        m15 = _load_materialized_granularity(
            store, instrument, STORAGE_GRANULARITY["M15"], "M15", from_dt=from_dt, to_dt=to_dt
        )
        h1 = _load_materialized_granularity(
            store, instrument, STORAGE_GRANULARITY["H1"], "H1", from_dt=from_dt, to_dt=to_dt
        )
        h4 = _load_materialized_granularity(
            store, instrument, STORAGE_GRANULARITY["H4"], "H4", from_dt=from_dt, to_dt=to_dt
        )

    native_h4 = _load_native_h4(store, instrument, from_dt=from_dt, to_dt=to_dt)
    d1_result = aggregate_h4_to_d1(native_h4, instrument=instrument)
    d1_candles = _filter_completed_in_range(d1_result.candles, from_dt=from_dt, to_dt=to_dt)
    return C024Frames(
        instrument=instrument,
        m5=CandleFrame.from_candles(instrument, "M5", m5),
        m15=CandleFrame.from_candles(instrument, "M15", m15),
        h1=CandleFrame.from_candles(instrument, "H1", h1),
        h4=CandleFrame.from_candles(instrument, "H4", h4),
        d1agg=CandleFrame.from_candles(instrument, "D1AGG", d1_candles),
    )


def pair_data_preflight(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_dt: datetime,
    to_dt: datetime,
    sample_decisions: int = 200,
) -> dict[str, Any]:
    """Per-pair counts, ranges, and an HTF last-completed/no-lookahead probe."""
    frames = load_c024_frames(store, instrument, from_dt=from_dt, to_dt=to_dt)
    m5_df = frames.m5.completed_only().df
    m15_df = frames.m15.completed_only().df
    h1_df = frames.h1.completed_only().df
    h4_df = frames.h4.completed_only().df
    d1_df = frames.d1agg.completed_only().df
    blocked_htf = 0
    lookahead_violations = 0
    if len(m5_df) >= 10:
        step = max(1, len(m5_df) // sample_decisions)
        decisions = m5_df.index[::step]
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
                    pd.DatetimeIndex([decision]), frame, cols, prefix=prefix
                )
                reason_col = f"{prefix}_blocked_reason"
                if reason_col in aligned.columns and aligned[reason_col].iloc[0]:
                    blocked_htf += 1
                time_col = f"{prefix}_{cols[0]}_time"
                if time_col in aligned.columns:
                    ft = aligned[time_col].iloc[0]
                    if ft is not None and hasattr(ft, "to_pydatetime"):
                        if ft.to_pydatetime() > decision:
                            lookahead_violations += 1
    warmup_ok = len(m5_df) >= 60 and len(m15_df) >= 20 and len(h1_df) >= 52 and len(h4_df) >= 52
    return {
        "instrument": instrument,
        "from_utc": from_dt.isoformat(),
        "to_utc": to_dt.isoformat(),
        "m5_count": len(m5_df),
        "m15_count": len(m15_df),
        "h1_count": len(h1_df),
        "h4_count": len(h4_df),
        "d1agg_count": len(d1_df),
        "d1agg_source": frames.d1agg_source,
        "materialized_source": frames.materialized_source,
        "m5_first": m5_df.index.min().isoformat() if len(m5_df) else None,
        "m5_last": m5_df.index.max().isoformat() if len(m5_df) else None,
        "htf_blocked_samples": blocked_htf,
        "lookahead_violations": lookahead_violations,
        "warmup_ok": bool(warmup_ok),
        "status": "PASS"
        if (len(m5_df) >= 500 and len(d1_df) >= 20 and warmup_ok and lookahead_violations == 0)
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
    train_from, train_to = splits["train"]
    from_dt = datetime.fromisoformat(train_from).replace(tzinfo=UTC)
    to_dt = datetime.fromisoformat(train_to).replace(hour=23, minute=59, tzinfo=UTC)
    for instrument in pairs:
        try:
            report = pair_data_preflight(store, instrument, from_dt=from_dt, to_dt=to_dt)
        except SystemExit as exc:
            report = {"instrument": instrument, "status": "BLOCKED_DATA_PRECONDITION", "reason": str(exc)}
        by_pair[instrument] = report
        if report.get("status") != "PASS":
            blocked.append(instrument)
    return {
        "campaign_id": "CAMPAIGN_024",
        "d1agg_source": D1AGG_SOURCE,
        "m1_derived_d1agg_used": False,
        "materialized_source": MATERIALIZED_SOURCE,
        "pairs": by_pair,
        "blocked_pairs": blocked,
        "preflight_ok": not blocked,
        "not_approved": True,
        "strategy_evidence": False,
    }

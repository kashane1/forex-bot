"""CAMPAIGN_026 frame loading — variable execution timeframe (M3 / M15 / M30).

Generalizes the CAMPAIGN_025 loader for the timeframe-ladder diagnostic. The
execution timeframe and its context ladder come from the M1-derived materialized
store (``source=m1_materialized``); D1AGG comes from native-H4-derived aggregation
(M1-derived D1AGG is **not** used, matching C025). Infrastructure only — loads and
shapes frames; runs no strategy evidence and approves nothing.

Context ladder per execution timeframe (frozen, see TIMEFRAME_LADDER_SPEC):
  * M3  : local setup M15            ; trend H1 + H4M1 ; regime D1AGG
  * M15 : local setup M15 (internal) ; trend H1 + H4M1 ; regime D1AGG
  * M30 : local setup H1             ; trend H4M1      ; regime D1AGG

For M15 the local setup is computed on the execution frame itself (internal
pullback/compression), the spec-permitted alternative to an H1 local setup — this
avoids H1 doubling as both the local-setup frame and a trend gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1
from forex_bot.data.m1_corpus_validation import MAJOR_PAIRS, _row_to_candle
from forex_bot.data.m1_timeframe_materialization import (
    MATERIALIZED_SOURCE,
    STORAGE_GRANULARITY,
)
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.research.campaign_025_loader import (
    D1AGG_SOURCE,
    _filter_completed_in_range,
    _load_native_h4,
)

EXECUTION_TIMEFRAMES = ("M3", "M15", "M30")

# Frozen context ladder. "local" = the setup timeframe; "trend" = HTF trend gates;
# "regime" = the slow daily filter. Mirrors the C025 M5 family one rung up/down.
CONTEXT_LADDER: dict[str, dict[str, object]] = {
    "M3": {"local": "M15", "trend": ("H1", "H4"), "regime": "D1AGG"},
    "M15": {"local": "M15", "trend": ("H1", "H4"), "regime": "D1AGG"},
    "M30": {"local": "H1", "trend": ("H4",), "regime": "D1AGG"},
}

# Minimum materialized execution bars per timeframe to consider coverage sufficient
# for a window (rough warmup+signal floor; the real split lives in Phase 6).
_MIN_EXEC_BARS = {"M3": 2000, "M15": 800, "M30": 400}


@dataclass(frozen=True)
class C026Frames:
    instrument: str
    execution_tf: str
    execution: CandleFrame
    local: CandleFrame  # local-setup frame (M15 for M3; H1 for M15/M30)
    h1: CandleFrame
    h4: CandleFrame  # H4M1 (M1-derived H4)
    d1agg: CandleFrame
    d1agg_source: str = D1AGG_SOURCE
    materialized_source: str = MATERIALIZED_SOURCE


def _load_materialized(
    store: PostgresCandleStore,
    instrument: str,
    frame_granularity: str,
    *,
    from_dt: datetime,
    to_dt: datetime,
) -> list[Candle]:
    storage_granularity = STORAGE_GRANULARITY[frame_granularity]
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


def check_c026_coverage(
    store: PostgresCandleStore,
    instrument: str,
    execution_tf: str,
    *,
    from_dt: datetime,
    to_dt: datetime,
) -> dict[str, object]:
    if execution_tf not in EXECUTION_TIMEFRAMES:
        raise ValueError(f"unsupported execution timeframe: {execution_tf}")
    ladder = CONTEXT_LADDER[execution_tf]
    needed = {execution_tf, ladder["local"], *ladder["trend"]}
    needed.discard("D1AGG")  # native-derived, checked separately
    counts = {
        gran: store.count_candles(
            instrument=instrument,
            granularity=STORAGE_GRANULARITY[gran],
            source=MATERIALIZED_SOURCE,
            start_utc=from_dt,
            end_utc=to_dt,
        )
        for gran in sorted(needed)
    }
    ok = counts.get(execution_tf, 0) >= _MIN_EXEC_BARS[execution_tf] and all(
        c > 0 for c in counts.values()
    )
    return {
        "instrument": instrument,
        "execution_tf": execution_tf,
        "from_utc": from_dt.isoformat(),
        "to_utc": to_dt.isoformat(),
        "counts": counts,
        "materialized_source": MATERIALIZED_SOURCE,
        "status": "PASS" if ok else "FAIL",
    }


def load_c026_frames(
    store: PostgresCandleStore,
    instrument: str,
    execution_tf: str,
    *,
    from_dt: datetime,
    to_dt: datetime,
) -> C026Frames:
    if instrument not in MAJOR_PAIRS:
        raise ValueError(f"instrument not in CAMPAIGN_026 universe: {instrument}")
    if execution_tf not in EXECUTION_TIMEFRAMES:
        raise ValueError(f"unsupported execution timeframe: {execution_tf}")
    coverage = check_c026_coverage(
        store, instrument, execution_tf, from_dt=from_dt, to_dt=to_dt
    )
    if coverage["status"] != "PASS":
        raise SystemExit(
            f"BLOCKED_DATA_PRECONDITION: C026 materialized coverage FAIL for "
            f"{instrument}/{execution_tf}: {coverage['counts']}. Run "
            "scripts/materialize_campaign_026_m3_m30.py first (M3/M30) and ensure "
            "M15/H1/H4M1 are materialized."
        )
    ladder = CONTEXT_LADDER[execution_tf]
    execution = _load_materialized(store, instrument, execution_tf, from_dt=from_dt, to_dt=to_dt)
    local = _load_materialized(store, instrument, str(ladder["local"]), from_dt=from_dt, to_dt=to_dt)
    h1 = _load_materialized(store, instrument, "H1", from_dt=from_dt, to_dt=to_dt)
    h4 = _load_materialized(store, instrument, "H4", from_dt=from_dt, to_dt=to_dt)

    native_h4 = _load_native_h4(store, instrument, from_dt=from_dt, to_dt=to_dt)
    d1_result = aggregate_h4_to_d1(native_h4, instrument=instrument)
    d1_candles = _filter_completed_in_range(d1_result.candles, from_dt=from_dt, to_dt=to_dt)

    return C026Frames(
        instrument=instrument,
        execution_tf=execution_tf,
        execution=CandleFrame.from_candles(instrument, execution_tf, execution),
        local=CandleFrame.from_candles(instrument, str(ladder["local"]), local),
        h1=CandleFrame.from_candles(instrument, "H1", h1),
        h4=CandleFrame.from_candles(instrument, "H4", h4),
        d1agg=CandleFrame.from_candles(instrument, "D1AGG", d1_candles),
    )


def coverage_report(
    store: PostgresCandleStore,
    *,
    pairs: list[str],
    execution_tfs: tuple[str, ...] = EXECUTION_TIMEFRAMES,
    from_dt: datetime | None = None,
    to_dt: datetime | None = None,
) -> dict[str, object]:
    """Per-pair, per-execution-tf materialized coverage (for preflight / split)."""
    lo = from_dt or datetime(2021, 1, 1, tzinfo=UTC)
    hi = to_dt or datetime(2026, 12, 31, tzinfo=UTC)
    by_pair: dict[str, object] = {}
    blocked: list[str] = []
    for instrument in pairs:
        by_tf: dict[str, object] = {}
        for tf in execution_tfs:
            rep = check_c026_coverage(store, instrument, tf, from_dt=lo, to_dt=hi)
            by_tf[tf] = rep
            if rep["status"] != "PASS":
                blocked.append(f"{instrument}/{tf}")
        by_pair[instrument] = by_tf
    return {
        "campaign_id": "CAMPAIGN_026",
        "materialized_source": MATERIALIZED_SOURCE,
        "d1agg_source": D1AGG_SOURCE,
        "m1_derived_d1agg_used": False,
        "pairs": by_pair,
        "blocked": blocked,
        "preflight_ok": not blocked,
        "not_approved": True,
        "strategy_evidence": False,
    }

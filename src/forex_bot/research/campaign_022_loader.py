"""CAMPAIGN_022 frame loading — materialized M1-derived M15/H1/H4 only.

No D1 / D1AGG layer: H4 is the top timeframe. Reuses the materialized-load helper
and coverage check from the shared CAMPAIGN_021 loader, but deliberately loads only
M15 (execution) + H1/H4 (context) and never aggregates or queries any daily bar.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from forex_bot.data.m1_corpus_validation import MAJOR_PAIRS
from forex_bot.data.m1_timeframe_materialization import (
    MATERIALIZED_SOURCE,
    STORAGE_GRANULARITY,
)
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.domain.candles import CandleFrame
from forex_bot.research.campaign_021_loader import (
    _load_materialized_granularity,
    check_materialized_coverage,
    instrument_for,
)

__all__ = ["C022Frames", "instrument_for", "load_c022_frames"]


@dataclass(frozen=True)
class C022Frames:
    instrument: str
    m15: CandleFrame
    h1: CandleFrame
    h4: CandleFrame
    materialized_source: str = MATERIALIZED_SOURCE


def load_c022_frames(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_dt: datetime,
    to_dt: datetime,
) -> C022Frames:
    """Load completed materialized M15/H1/H4 frames for one pair/window (no D1)."""
    if instrument not in MAJOR_PAIRS:
        raise ValueError(f"instrument not in CAMPAIGN_022 universe: {instrument}")
    coverage = check_materialized_coverage(store, instrument, from_dt=from_dt, to_dt=to_dt)
    if coverage["status"] != "PASS":
        raise SystemExit(
            f"materialized coverage FAIL for {instrument}: {coverage['counts']}. "
            "Run scripts/materialize_m1_derived_timeframes.py --all-majors first."
        )
    m15 = _load_materialized_granularity(
        store, instrument, "M15", "M15", from_dt=from_dt, to_dt=to_dt
    )
    h1 = _load_materialized_granularity(
        store, instrument, "H1", "H1", from_dt=from_dt, to_dt=to_dt
    )
    h4 = _load_materialized_granularity(
        store, instrument, STORAGE_GRANULARITY["H4"], "H4", from_dt=from_dt, to_dt=to_dt
    )
    return C022Frames(
        instrument=instrument,
        m15=CandleFrame.from_candles(instrument, "M15", m15),
        h1=CandleFrame.from_candles(instrument, "H1", h1),
        h4=CandleFrame.from_candles(instrument, "H4", h4),
    )

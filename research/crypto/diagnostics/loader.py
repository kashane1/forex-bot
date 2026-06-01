"""Load canonical crypto materialized candles for Family C diagnostics."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import numpy as np

from forex_bot.data.postgres_candle_store import PostgresCandleStore
from research.crypto.registry import CANONICAL_INSTRUMENTS, validate_instrument
from research.crypto.trend_persistence import MATERIALIZED_SOURCE, TIMEFRAME_STORAGE

DEFAULT_START = datetime(2021, 5, 31, 0, 0, 0, tzinfo=UTC)
DEFAULT_END = datetime(2026, 5, 31, 23, 57, 53, tzinfo=UTC)


def storage_granularity(timeframe: str) -> str:
    if timeframe not in TIMEFRAME_STORAGE:
        raise ValueError(f"unsupported diagnostic timeframe: {timeframe}")
    return TIMEFRAME_STORAGE[timeframe]


def load_candle_rows(
    store: PostgresCandleStore,
    *,
    instrument: str,
    timeframe: str,
    start_utc: datetime = DEFAULT_START,
    end_utc: datetime = DEFAULT_END,
) -> list[dict[str, Any]]:
    validate_instrument(instrument)
    return store.query_candles(
        instrument=instrument,
        granularity=storage_granularity(timeframe),
        start_utc=start_utc,
        end_utc=end_utc,
        source=MATERIALIZED_SOURCE,
    )


def rows_to_ohlcv(rows: list[dict[str, Any]]) -> dict[str, np.ndarray]:
    if not rows:
        empty = np.array([], dtype=float)
        return {
            "times": np.array([], dtype=object),
            "open": empty,
            "high": empty,
            "low": empty,
            "close": empty,
        }
    times = np.array([r["time_utc"].astimezone(UTC) for r in rows], dtype=object)
    return {
        "times": times,
        "open": np.array([float(r["mid_o"]) for r in rows], dtype=float),
        "high": np.array([float(r["mid_h"]) for r in rows], dtype=float),
        "low": np.array([float(r["mid_l"]) for r in rows], dtype=float),
        "close": np.array([float(r["mid_c"]) for r in rows], dtype=float),
    }


def load_all_series(
    store: PostgresCandleStore,
    *,
    instruments: tuple[str, ...] = CANONICAL_INSTRUMENTS,
    timeframes: tuple[str, ...] = ("M15", "H1", "H4", "D1"),
    start_utc: datetime = DEFAULT_START,
    end_utc: datetime = DEFAULT_END,
) -> dict[str, dict[str, dict[str, np.ndarray]]]:
    out: dict[str, dict[str, dict[str, np.ndarray]]] = {}
    for instrument in instruments:
        validate_instrument(instrument)
        out[instrument] = {}
        for tf in timeframes:
            rows = load_candle_rows(
                store,
                instrument=instrument,
                timeframe=tf,
                start_utc=start_utc,
                end_utc=end_utc,
            )
            out[instrument][tf] = rows_to_ohlcv(rows)
    return out

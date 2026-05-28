"""Normalized trade-lifecycle records and loaders for research diagnostics.

Read-only. Loads existing campaign trade artifacts (per-pair `*_trades.csv`)
into a single normalized `TradeLifecycleRecord` so stop/exit and (later)
MFE/MAE diagnostics can run over heterogeneous campaigns without each tool
re-parsing raw CSV columns.

Design rules:
  * Every excursion / signal-feature field is **optional** — missingness is
    explicit (``None``) and counted, never fabricated.
  * Loading never mutates the source artifact (read-only file access).
  * Decimals in the source CSV (price, r_multiple) are parsed to ``float`` for
    diagnostics; this is lossy by design and only ever used for aggregate
    statistics, never to re-derive a verdict.

This module is infrastructure/diagnostics. It approves no strategy, changes no
verdict, and touches no broker/live path.
"""

from __future__ import annotations

import csv
from collections.abc import Iterator
from dataclasses import dataclass, field, fields
from datetime import datetime
from pathlib import Path

__all__ = [
    "TradeLifecycleRecord",
    "field_missingness",
    "load_trades_csv",
    "parse_lifecycle_row",
]


@dataclass(frozen=True)
class TradeLifecycleRecord:
    """One trade, normalized. Required fields first; everything else optional."""

    campaign_id: str
    strategy_name: str | None = None
    split: str | None = None
    instrument: str | None = None
    side: str | None = None

    entry_time: datetime | None = None
    exit_time: datetime | None = None
    entry_price: float | None = None
    exit_price: float | None = None

    initial_stop_price: float | None = None
    stop_distance_pips: float | None = None
    stop_distance_atr: float | None = None

    result_r: float | None = None
    exit_reason: str | None = None
    bars_held: int | None = None
    spread_pips: float | None = None

    mfe_r: float | None = None
    mae_r: float | None = None
    reached_plus_0_25r: bool | None = None
    reached_plus_0_5r: bool | None = None
    reached_plus_1_0r: bool | None = None
    touched_minus_0_5r: bool | None = None
    touched_minus_0_9r: bool | None = None

    h4_adx_at_entry: float | None = None
    h1_pullback_depth_atr: float | None = None
    m15_reclaim_distance_atr: float | None = None
    session_bucket: str | None = None
    volatility_regime: str | None = None

    # Provenance / passthrough of any source-specific extras (read-only).
    extra: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Parsing helpers (defensive: a missing/blank column yields None, not an error)
# ---------------------------------------------------------------------------

def _f(row: dict[str, str], *keys: str) -> float | None:
    for k in keys:
        v = row.get(k)
        if v is not None and v != "":
            try:
                return float(v)
            except ValueError:
                return None
    return None


def _i(row: dict[str, str], *keys: str) -> int | None:
    for k in keys:
        v = row.get(k)
        if v is not None and v != "":
            try:
                return int(float(v))
            except ValueError:
                return None
    return None


def _s(row: dict[str, str], *keys: str) -> str | None:
    for k in keys:
        v = row.get(k)
        if v is not None and v != "":
            return v
    return None


def _dt(row: dict[str, str], *keys: str) -> datetime | None:
    raw = _s(row, *keys)
    if raw is None:
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _pip_size(instrument: str | None) -> float:
    """Pip size for FX majors: 0.01 for JPY quote, else 0.0001."""
    if instrument and instrument.upper().endswith("JPY"):
        return 0.01
    return 0.0001


def parse_lifecycle_row(
    row: dict[str, str],
    *,
    campaign_id: str,
    split: str | None,
    strategy_name: str | None = None,
) -> TradeLifecycleRecord:
    """Normalize one CSV row (mapping of column->str) into a lifecycle record.

    Tolerant of missing columns. Recognized source columns are mapped to
    normalized fields; everything unrecognized is preserved in ``extra``.
    """
    instrument = _s(row, "instrument")
    entry_price = _f(row, "entry_price")
    stop_price = _f(row, "stop_price", "initial_stop_price")

    stop_distance_pips: float | None = None
    if entry_price is not None and stop_price is not None:
        stop_distance_pips = abs(entry_price - stop_price) / _pip_size(instrument)

    recognized = {
        "instrument",
        "side",
        "entry_time",
        "exit_time",
        "entry_price",
        "exit_price",
        "stop_price",
        "initial_stop_price",
        "r_multiple",
        "result_r",
        "exit_reason",
        "bars_held",
        "spread_paid_pips",
        "spread_pips",
        "protective_stop_arm_mfe_r",
        "mfe_r",
        "mae_r",
        "h4_adx_at_entry",
        "h1_pullback_depth_atr",
        "m15_reclaim_distance_atr",
        "session_bucket",
        "volatility_regime",
    }
    extra = {k: v for k, v in row.items() if k not in recognized and v not in (None, "")}

    return TradeLifecycleRecord(
        campaign_id=campaign_id,
        strategy_name=strategy_name,
        split=split,
        instrument=instrument,
        side=_s(row, "side"),
        entry_time=_dt(row, "entry_time"),
        exit_time=_dt(row, "exit_time"),
        entry_price=entry_price,
        exit_price=_f(row, "exit_price"),
        initial_stop_price=stop_price,
        stop_distance_pips=stop_distance_pips,
        result_r=_f(row, "r_multiple", "result_r"),
        exit_reason=_s(row, "exit_reason"),
        bars_held=_i(row, "bars_held"),
        spread_pips=_f(row, "spread_paid_pips", "spread_pips"),
        # Only a *conditional* partial MFE proxy exists in C022; full MFE/MAE
        # is absent and stays None unless a real column is present.
        mfe_r=_f(row, "mfe_r"),
        mae_r=_f(row, "mae_r"),
        h4_adx_at_entry=_f(row, "h4_adx_at_entry"),
        h1_pullback_depth_atr=_f(row, "h1_pullback_depth_atr"),
        m15_reclaim_distance_atr=_f(row, "m15_reclaim_distance_atr"),
        session_bucket=_s(row, "session_bucket"),
        volatility_regime=_s(row, "volatility_regime"),
        extra=extra,
    )


def load_trades_csv(
    path: str | Path,
    *,
    campaign_id: str,
    split: str | None = None,
    strategy_name: str | None = None,
) -> list[TradeLifecycleRecord]:
    """Load one per-pair trade CSV into normalized lifecycle records (read-only)."""
    p = Path(path)
    with p.open(newline="") as fh:
        reader = csv.DictReader(fh)
        return [
            parse_lifecycle_row(
                row,
                campaign_id=campaign_id,
                split=split,
                strategy_name=strategy_name,
            )
            for row in reader
        ]


def field_missingness(records: list[TradeLifecycleRecord]) -> dict[str, int]:
    """Count, per optional field, how many records have it missing (None).

    Required-but-None counts too — the point is an explicit missingness map so
    diagnostics can state coverage honestly.
    """
    counts: dict[str, int] = {}
    n = len(records)
    for f in fields(TradeLifecycleRecord):
        if f.name == "extra":
            continue
        missing = sum(1 for r in records if getattr(r, f.name) is None)
        if missing:
            counts[f.name] = missing
    counts["_total_records"] = n
    return counts


def iter_records(
    records: list[TradeLifecycleRecord],
    *,
    instrument: str | None = None,
    split: str | None = None,
) -> Iterator[TradeLifecycleRecord]:
    for r in records:
        if instrument is not None and r.instrument != instrument:
            continue
        if split is not None and r.split != split:
            continue
        yield r

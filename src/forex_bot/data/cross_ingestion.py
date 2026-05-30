"""Ingestion-support helpers for non-USD FX crosses.

Thin, reusable layer on top of the practice-only M1 ingestion script and
`PostgresCandleStore`. It resolves ingestion targets from the cross
registry and probes per-cross coverage/provenance so both the ingestion
script and the Phase-5 validation script can report a compact, honest
state — including a graceful `NOT_INGESTED` when a cross has no rows yet
(the expected state until a credentialed fetch is run).

No ingestion happens here and no credentials are read; this module only
*reads* coverage from a candle store via a minimal protocol, so it is
unit-testable without a database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol

from forex_bot.domain.cross_instruments import (
    NONUSD_CROSS_PAIRS,
    PRIMARY_CROSS_PAIRS,
    cross_spec,
    is_nonusd_cross,
)

# Source label written by scripts/ingest_oanda_m1_candles.py for native M1.
M1_SOURCE = "oanda-practice-m1"


class CandleCountStore(Protocol):
    """Minimal read-only surface of PostgresCandleStore used for coverage."""

    def count_candles(
        self, *, instrument: str, granularity: str, source: str | None = ...,
    ) -> int: ...

    def max_candle_time(
        self, *, instrument: str, granularity: str, source: str | None = ...,
    ) -> datetime | None: ...


def cross_ingestion_targets(*, scope: str = "primary") -> list[str]:
    """Resolve the cross ingestion target list for a scope.

    * ``"primary"`` — the four required wave-1 crosses.
    * ``"all"`` — every registered cross (primary + extended).
    """
    if scope == "primary":
        return list(PRIMARY_CROSS_PAIRS)
    if scope == "all":
        return list(NONUSD_CROSS_PAIRS)
    raise ValueError(f"unknown cross ingestion scope: {scope!r}")


@dataclass(frozen=True)
class CrossCoverage:
    """Compact per-cross ingestion coverage / provenance snapshot."""

    instrument: str
    granularity: str
    state: str  # "INGESTED" | "NOT_INGESTED"
    row_count: int
    last_timestamp: str | None
    tier: str
    cost_band: str
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "instrument": self.instrument,
            "granularity": self.granularity,
            "state": self.state,
            "row_count": self.row_count,
            "last_timestamp": self.last_timestamp,
            "tier": self.tier,
            "cost_band": self.cost_band,
            "notes": self.notes,
        }


def cross_coverage(
    store: CandleCountStore,
    instrument: str,
    *,
    granularity: str = "M1",
    source: str | None = M1_SOURCE,
) -> CrossCoverage:
    """Probe one registered cross's coverage in the store.

    Returns a `NOT_INGESTED` snapshot (never raises) when the cross has no
    rows — the expected state until a credentialed fetch is performed.
    """
    if not is_nonusd_cross(instrument):
        raise ValueError(f"not a registered non-USD cross: {instrument}")
    spec = cross_spec(instrument)
    count = store.count_candles(instrument=instrument, granularity=granularity, source=source)
    notes: list[str] = []
    if spec.structural_breaks:
        notes.extend(f"structural_break:{d.isoformat()}:{why}" for d, why in spec.structural_breaks)
    if count == 0:
        return CrossCoverage(
            instrument=instrument, granularity=granularity, state="NOT_INGESTED",
            row_count=0, last_timestamp=None, tier=spec.tier, cost_band=spec.cost_band,
            notes=notes,
        )
    last = store.max_candle_time(instrument=instrument, granularity=granularity, source=source)
    return CrossCoverage(
        instrument=instrument, granularity=granularity, state="INGESTED",
        row_count=count,
        last_timestamp=last.astimezone(UTC).isoformat() if last else None,
        tier=spec.tier, cost_band=spec.cost_band, notes=notes,
    )


def cross_coverage_report(
    store: CandleCountStore,
    *,
    scope: str = "primary",
    granularity: str = "M1",
    source: str | None = M1_SOURCE,
) -> dict[str, object]:
    """Compact coverage report across the scoped crosses (diagnostic only)."""
    targets = cross_ingestion_targets(scope=scope)
    rows = [cross_coverage(store, name, granularity=granularity, source=source) for name in targets]
    ingested = [r for r in rows if r.state == "INGESTED"]
    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "scope": scope,
        "granularity": granularity,
        "source": source,
        "target_count": len(targets),
        "ingested_count": len(ingested),
        "not_ingested": [r.instrument for r in rows if r.state == "NOT_INGESTED"],
        "crosses": [r.as_dict() for r in rows],
    }

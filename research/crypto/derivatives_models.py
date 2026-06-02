"""Canonical record dataclasses + cost helpers for the crypto derivatives layer.

Storage-agnostic contract (see CRYPTO_DERIVATIVES_DATA_MODEL.md). These records
are the durable interface between venue parsers, validation, and any future
Family E diagnostics. No execution / PnL modelling lives here beyond the single
funding cashflow sign helper.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

Side = Literal["long", "short"]


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


@dataclass(frozen=True)
class PerpOhlcvRecord:
    canonical_id: str
    venue: str
    venue_symbol: str
    granularity: str
    time_utc: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_ccy: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "time_utc", _utc(self.time_utc))


@dataclass(frozen=True)
class FundingRateRecord:
    canonical_id: str
    venue: str
    venue_symbol: str
    funding_time_utc: datetime
    funding_rate: float
    funding_interval_hours: int
    mark_price: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "funding_time_utc", _utc(self.funding_time_utc))


@dataclass(frozen=True)
class OpenInterestRecord:
    canonical_id: str
    venue: str
    time_utc: datetime
    interval: str
    open_interest_base: float | None = None
    open_interest_usd: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "time_utc", _utc(self.time_utc))


@dataclass(frozen=True)
class MarkIndexRecord:
    canonical_id: str
    venue: str
    granularity: str
    time_utc: datetime
    mark_close: float | None = None
    index_close: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "time_utc", _utc(self.time_utc))


@dataclass(frozen=True)
class BasisRecord:
    canonical_id: str
    spot_instrument: str
    perp_venue: str
    spot_venue: str
    granularity: str
    time_utc: datetime
    perp_close: float
    spot_close: float
    basis_abs: float
    basis_bps: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "time_utc", _utc(self.time_utc))


def funding_cashflow(funding_rate: float, notional: float, side: Side) -> float:
    """Funding PnL for a position held across one funding settlement.

    Sign convention (single source of truth, CRYPTO_DERIVATIVES_DATA_MODEL.md §5):
    when ``funding_rate > 0`` longs pay shorts. A long's funding PnL is therefore
    ``-funding_rate * notional`` and a short's is ``+funding_rate * notional``.
    """
    if side == "long":
        return -funding_rate * notional
    if side == "short":
        return funding_rate * notional
    raise ValueError(f"unknown side: {side!r}")


def compute_basis(perp_close: float, spot_close: float) -> tuple[float, float]:
    """Return ``(basis_abs, basis_bps)`` for a perp vs spot close pair."""
    if spot_close <= 0:
        raise ValueError("spot_close must be positive to compute basis")
    basis_abs = perp_close - spot_close
    basis_bps = 1e4 * basis_abs / spot_close
    return basis_abs, basis_bps

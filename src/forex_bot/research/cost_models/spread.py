"""Spread-cost model and diagnostics for non-USD FX crosses.

Spread cost for a cross is sourced from the registry's qualitative band
(`est_spread_pips`) until real ingested bid/ask data is available, at which
point `SpreadStats.from_bid_ask` measures the realised distribution. Both
are expressed in pips (using the cross's own pip size) so the model never
assumes a USD leg.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from forex_bot.domain.cross_instruments import cross_spec, is_nonusd_cross


@dataclass(frozen=True)
class SpreadStats:
    """Realised spread distribution (in pips) measured from bid/ask data."""

    instrument: str
    n: int
    median_pips: float
    p90_pips: float
    max_pips: float
    source: str = "measured"

    @classmethod
    def from_bid_ask(
        cls,
        instrument: str,
        bids: Sequence[float],
        asks: Sequence[float],
    ) -> SpreadStats:
        if not is_nonusd_cross(instrument):
            raise ValueError(f"not a registered non-USD cross: {instrument}")
        if len(bids) != len(asks):
            raise ValueError("bids and asks must be the same length")
        pip = float(cross_spec(instrument).pip_size)
        spreads = sorted(
            (a - b) / pip for b, a in zip(bids, asks, strict=True) if a is not None and b is not None
        )
        n = len(spreads)
        if n == 0:
            raise ValueError("no usable bid/ask pairs")

        def _q(q: float) -> float:
            idx = min(n - 1, max(0, round(q * (n - 1))))
            return spreads[idx]

        return cls(
            instrument=instrument, n=n,
            median_pips=_q(0.50), p90_pips=_q(0.90), max_pips=spreads[-1],
        )


class CrossSpreadCostModel:
    """Per-cross spread cost in pips / price / R.

    Defaults to the registry's qualitative estimate band; pass measured
    `SpreadStats` to use realised data instead. Cost is always expressed
    via the cross's own pip size — no USD assumption.
    """

    def __init__(self, instrument: str, *, measured: SpreadStats | None = None) -> None:
        if not is_nonusd_cross(instrument):
            raise ValueError(f"not a registered non-USD cross: {instrument}")
        self.instrument = instrument
        self.spec = cross_spec(instrument)
        self.measured = measured

    @property
    def source(self) -> str:
        return "measured" if self.measured is not None else "registry_estimate"

    def spread_pips(self, *, level: str = "typical") -> float:
        """Estimated one-way spread in pips.

        `level` ∈ {"low", "typical", "high"}. With measured data, "typical"
        maps to the median and "high" to p90; with the registry estimate it
        maps to the band endpoints / midpoint.
        """
        if self.measured is not None:
            if level == "low":
                return self.measured.median_pips
            if level == "high":
                return self.measured.p90_pips
            return self.measured.median_pips
        lo, hi = self.spec.est_spread_pips
        if level == "low":
            return lo
        if level == "high":
            return hi
        return (lo + hi) / 2.0

    def spread_price(self, *, level: str = "typical") -> Decimal:
        """One-way spread cost as a price distance (pips × pip size)."""
        return Decimal(str(self.spread_pips(level=level))) * self.spec.pip_size

    def spread_cost_r(
        self, risk_pips: float, *, level: str = "typical", round_trip: bool = True
    ) -> float:
        """Spread cost as a fraction of risk (R).

        `risk_pips` is the entry-to-stop distance in pips. `round_trip`
        charges the spread on both entry and exit (the realistic default).
        Quote currency cancels — no USD conversion needed.
        """
        if risk_pips <= 0:
            raise ValueError("risk_pips must be positive")
        legs = 2.0 if round_trip else 1.0
        return legs * self.spread_pips(level=level) / risk_pips

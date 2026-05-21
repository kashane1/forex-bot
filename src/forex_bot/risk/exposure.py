"""Exposure helpers used by the risk engine."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from forex_bot.domain.positions import Position


def has_open_position(positions: list[Position], instrument: str) -> bool:
    return any(p.instrument == instrument and not p.is_flat for p in positions)


def currency_exposure(positions: list[Position]) -> dict[str, Decimal]:
    """Net currency exposure in *units of the foreign currency*.

    Long EUR_USD with X units → +X EUR and -X*price USD; we approximate to
    +X for the base and -X for the quote, which is the rough signed
    direction we use to detect correlated positions in v0.
    """
    exposure: dict[str, Decimal] = defaultdict(Decimal)
    for pos in positions:
        if pos.is_flat:
            continue
        base, quote = pos.instrument.split("_", 1)
        net = pos.long_units + pos.short_units  # short_units already negative
        exposure[base] += net
        exposure[quote] -= net
    return dict(exposure)

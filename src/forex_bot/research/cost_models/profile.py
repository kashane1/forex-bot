"""Combined per-cross cost profile for future front-gate cost realism.

Bundles the spread and carry models plus structural-break flags into one
diagnostic dict a front-gate screen can consume. Everything is flagged as
ESTIMATE / diagnostic-only and is NOT strategy evidence.
"""

from __future__ import annotations

from forex_bot.domain.cross_instruments import cross_spec, is_nonusd_cross
from forex_bot.research.cost_models.carry import CrossCarryModel
from forex_bot.research.cost_models.spread import CrossSpreadCostModel, SpreadStats


def cross_cost_profile(
    instrument: str, *, measured_spread: SpreadStats | None = None
) -> dict[str, object]:
    """Return a compact, diagnostic-only cost profile for one cross."""
    if not is_nonusd_cross(instrument):
        raise ValueError(f"not a registered non-USD cross: {instrument}")
    spec = cross_spec(instrument)
    spread = CrossSpreadCostModel(instrument, measured=measured_spread)
    carry = CrossCarryModel(instrument)
    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "instrument": instrument,
        "base_currency": spec.base_currency,
        "quote_currency": spec.quote_currency,
        "pip_size": str(spec.pip_size),
        "tier": spec.tier,
        "spread": {
            "source": spread.source,
            "cost_band": spec.cost_band,
            "typical_pips": spread.spread_pips(level="typical"),
            "high_pips": spread.spread_pips(level="high"),
        },
        "carry": carry.metadata(),
        "structural_breaks": [
            {"date": d.isoformat(), "reason": why} for d, why in spec.structural_breaks
        ],
    }

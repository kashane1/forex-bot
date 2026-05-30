"""Instrument-specific cost models for non-USD FX crosses.

The seven USD majors model spread cost via `backtesting.fills.FillModel`
and financing via `forex_bot.financing` (a conservative per-pair bp/day
stress overlay). Both encode a hidden assumption — *one leg is USD* — that
is WRONG for crosses:

  * `financing.notional_usd` returns units*price (treated as USD) for a
    cross like EUR_JPY, but that product is in JPY, not USD.
  * `financing.risk_usd` likewise assumes the quote currency is USD.
  * A single per-pair bp/day copied from a major ignores that a cross's
    carry is genuinely two-legged (base-leg rate minus quote-leg rate).

This package therefore does NOT reuse the majors' assumptions. Instead it
works in units where the cross's quote currency *cancels* (R = fraction of
risk) so no spurious USD conversion is introduced, sources cost figures
from the cross registry's explicit per-cross estimates, and is honest that
converting a cross debit to USD needs a separate quote/USD rate.

Everything here is diagnostic/cost-realism infrastructure for a future
front gate — NOT strategy evidence, and nothing is approved.
"""

from __future__ import annotations

from forex_bot.research.cost_models.carry import (
    CrossCarryModel,
    CrossCarryTreatment,
)
from forex_bot.research.cost_models.profile import cross_cost_profile
from forex_bot.research.cost_models.spread import (
    CrossSpreadCostModel,
    SpreadStats,
)

__all__ = [
    "CrossCarryModel",
    "CrossCarryTreatment",
    "CrossSpreadCostModel",
    "SpreadStats",
    "cross_cost_profile",
]

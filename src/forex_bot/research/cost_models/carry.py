"""Two-legged carry / financing stress model for non-USD FX crosses.

WHY THIS IS NOT THE MAJORS' FINANCING MODEL
-------------------------------------------
`forex_bot.financing` models a USD-major's carry as a single per-pair
bp/day debit and computes notional/risk in USD assuming one leg IS USD.
For a cross neither leg is USD, so:

  * A cross's carry is genuinely **two-legged** — long the cross you earn
    the base-leg rate and pay the quote-leg rate; the realised carry is
    their differential. The registry's `conservative_bp_per_day` is an
    explicit per-cross estimate of that net differential (worse side),
    NOT a value copied from any major.
  * P&L accrues in the **quote currency**, which is not USD. Converting a
    debit to USD needs a separate quote/USD rate. Rather than fabricate
    one, this model works in **R** (fraction of the trade's risk), in
    which the quote currency cancels exactly, and exposes the raw
    **quote-currency** debit for callers that have a conversion rate.

Like the majors' model this is a CONSERVATIVE STRESS overlay (always a
cost, never a credit) and is ESTIMATED, never MODELED — OANDA exposes no
historical cross financing series, so it can never gate live promotion.
"""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from forex_bot.domain.cross_instruments import cross_spec, is_nonusd_cross


class CrossCarryTreatment(StrEnum):
    """How a cross's carry is treated (mirrors financing.FinancingTreatment).

    Only ESTIMATED is reachable here: a conservative stress overlay, never
    a real modelled rate, so it never lifts the live-financing blocker.
    """

    ESTIMATED = "estimated"
    UNMODELED = "unmodeled"


def holding_days(bars_held: int, hours_per_bar: int = 4) -> float:
    """Calendar days a position was open, from the bar count."""
    return bars_held * hours_per_bar / 24.0


class CrossCarryModel:
    """Conservative two-legged carry stress for one registered cross."""

    treatment = CrossCarryTreatment.ESTIMATED

    def __init__(self, instrument: str) -> None:
        if not is_nonusd_cross(instrument):
            raise ValueError(f"not a registered non-USD cross: {instrument}")
        self.instrument = instrument
        self.spec = cross_spec(instrument)

    @property
    def bp_per_day(self) -> float:
        """Conservative net two-leg carry, bp of notional per day."""
        return self.spec.conservative_bp_per_day

    @property
    def carry_legs(self) -> tuple[str, str]:
        """(long-leg, short-leg) currencies whose differential is the carry."""
        return self.spec.carry_legs

    def notional_quote(self, units: Decimal, entry_price: Decimal) -> float:
        """Position notional in the QUOTE currency (units × price).

        This is honest about the denomination — it is NOT USD unless the
        quote currency happens to be USD (which it never is for a cross).
        """
        return float(abs(units) * entry_price)

    def debit_quote(
        self, units: Decimal, entry_price: Decimal, bars_held: int, *, hours_per_bar: int = 4,
    ) -> float:
        """Conservative carry debit in the QUOTE currency for one trade.

        Always >= 0 (a stress cost, never a credit). Convert to USD with a
        quote/USD rate if a portfolio-USD figure is needed — not assumed."""
        days = holding_days(bars_held, hours_per_bar)
        return days * (self.bp_per_day / 10_000.0) * self.notional_quote(units, entry_price)

    def debit_r(
        self,
        units: Decimal,
        entry_price: Decimal,
        stop_price: Decimal,
        bars_held: int,
        *,
        hours_per_bar: int = 4,
    ) -> float:
        """Carry debit as a fraction of the trade's risk (R).

        risk_quote = |entry - stop| × |units| (quote currency). Since the
        debit is also in quote currency, the quote currency cancels and the
        result needs NO USD rate. Returns 0.0 for a degenerate (zero-risk)
        trade."""
        risk_quote = float(abs(entry_price - stop_price) * abs(units))
        if risk_quote <= 0:
            return 0.0
        return self.debit_quote(units, entry_price, bars_held, hours_per_bar=hours_per_bar) / risk_quote

    def metadata(self) -> dict[str, object]:
        """Report-ready cost metadata; never silently optimistic."""
        return {
            "instrument": self.instrument,
            "carry_model": "cross_conservative_stress",
            "carry_treatment": self.treatment.value,
            "carry_legs": list(self.carry_legs),
            "conservative_bp_per_day": self.bp_per_day,
            "is_carry_cross": self.spec.is_carry_cross,
            "financing_in_engine_pnl": False,
            "financing_is_live_blocker": True,
            "denomination": f"quote_currency:{self.spec.quote_currency}",
            "note": "ESTIMATED stress only; quote→USD needs a separate rate (not assumed).",
        }

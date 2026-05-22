"""Conservative financing / rollover stress model.

WHY THIS IS A STRESS MODEL, NOT A REAL ONE
------------------------------------------
Accurate *historical* financing cannot be modeled with the current
stack. Investigation (CAMPAIGN_004, Step 1):

  * `GET /v3/accounts/{id}/instruments` exposes a `financing` object,
    but on the OANDA *practice* account `longRate` and `shortRate` are
    both 0 — practice accounts do not carry real financing rates.
  * OANDA's v20 REST API publishes no historical financing-rate time
    series; there is nothing to backtest against for 2020-2026.
  * `DAILY_FINANCING` transactions exist only for trades actually held
    on an account. This research bot has submitted no orders, so there
    is no empirical financing history to fit.

Therefore financing remains UNMODELED in the backtest engine's PnL.
This module instead provides a deliberately CONSERVATIVE stress
overlay: a per-pair basis-points-per-day debit (the worse of the long
and short side) that overstates the cost in the average case. Campaign
reports apply it as an after-the-fact stress column and gate on the
financing-stressed result.

Financing remains a hard blocker for any live promotion until a real
financing model exists (hypothesis H-09). A passing stress test does
NOT lift that blocker — it only shows the result is not *additionally*
killed by a pessimistic financing assumption.

The bp/day figures come from `docs/financing_decision.md` and reflect
worst-case carry over 2020-2026 interest-rate differentials.
"""

from __future__ import annotations

from decimal import Decimal

# Conservative carry cost, basis points of notional per calendar day a
# position is open. Each value is the worse (more expensive) of the long
# and short side for that pair — see docs/financing_decision.md.
CONSERVATIVE_BP_PER_DAY: dict[str, float] = {
    "EUR_USD": 0.6,
    "GBP_USD": 0.7,
    "USD_JPY": 1.2,
    "AUD_USD": 0.7,
    "USD_CAD": 0.5,
    "USD_CHF": 0.9,
    "NZD_USD": 0.7,
}
# Default for any pair not listed: the table maximum, to stay conservative.
_DEFAULT_BP_PER_DAY = 1.2

# Pairs whose BASE currency is USD — units are already denominated in USD.
_USD_BASE = {"USD_JPY", "USD_CAD", "USD_CHF"}


def holding_days(bars_held: int, hours_per_bar: int = 4) -> float:
    """Calendar days a position was open, from the bar count."""
    return bars_held * hours_per_bar / 24.0


def notional_usd(instrument: str, units: Decimal, entry_price: Decimal) -> float:
    """Approximate position notional in USD.

    For USD-base pairs (USD_JPY/CAD/CHF) `units` is already USD. For
    USD-quote pairs the USD notional is units * price.
    """
    u = abs(units)
    if instrument in _USD_BASE:
        return float(u)
    return float(u * entry_price)


def bp_per_day(instrument: str) -> float:
    return CONSERVATIVE_BP_PER_DAY.get(instrument, _DEFAULT_BP_PER_DAY)


def financing_debit_usd(
    instrument: str,
    units: Decimal,
    entry_price: Decimal,
    bars_held: int,
    hours_per_bar: int = 4,
) -> float:
    """Conservative financing debit in USD for one closed trade.

    debit = holding_days * (bp_per_day / 10000) * notional_usd

    Always >= 0 — a stress *cost*, never a credit (even when real
    financing would be a credit for the favourable carry side, the
    stress model refuses to assume a benefit).
    """
    days = holding_days(bars_held, hours_per_bar)
    notional = notional_usd(instrument, units, entry_price)
    return days * (bp_per_day(instrument) / 10_000.0) * notional


def risk_usd(
    instrument: str,
    units: Decimal,
    entry_price: Decimal,
    stop_price: Decimal,
) -> float:
    """The trade's risk (entry-to-initial-stop distance × units) in USD."""
    risk_quote = abs(entry_price - stop_price) * abs(units)
    if instrument in _USD_BASE:
        # quote currency P&L converted to USD at the entry price
        return float(risk_quote / entry_price) if entry_price else 0.0
    return float(risk_quote)


def financing_debit_r(
    instrument: str,
    units: Decimal,
    entry_price: Decimal,
    stop_price: Decimal,
    bars_held: int,
    hours_per_bar: int = 4,
) -> float:
    """Financing debit expressed in R (fraction of the trade's risk).

    Returns 0.0 if the risk is non-positive (degenerate trade).
    """
    r = risk_usd(instrument, units, entry_price, stop_price)
    if r <= 0:
        return 0.0
    return financing_debit_usd(instrument, units, entry_price, bars_held, hours_per_bar) / r

"""Position sizing.

Formula (per spec):
    risk_amount_home = nav_home * risk_pct / 100
    stop_distance_price = |entry - stop|
    pip_size = 10 ** pip_location
    stop_distance_pips = stop_distance_price / pip_size
    pip_value_per_unit_home = f(instrument, account_currency, prices)
    raw_units = risk_amount_home / (stop_distance_pips * pip_value_per_unit_home)
    units = round_down_to_trade_units_precision(raw_units)
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import Quote


@dataclass(frozen=True)
class SizingResult:
    units: Decimal
    raw_units: Decimal
    pip_value_per_unit_home: Decimal
    stop_distance_pips: Decimal
    risk_amount_home: Decimal
    estimated_margin_home: Decimal


def compute_pip_value_home(
    instrument: Instrument,
    account_currency: str,
    quotes_by_instrument: dict[str, Quote],
) -> Decimal | None:
    """Pip value in account-currency terms for 1 unit of the base currency.

    Cases:
      * quote == account currency  → pip_value = pip_size (in quote ≡ home)
      * base  == account currency  → pip_value = pip_size / mid
      * cross (neither side is home) → pip_value = pip_size / cross_mid,
        where cross_mid is the *quote→home* price obtained from
        `<quote>_<home>` or `<home>_<quote>` quotes in `quotes_by_instrument`.

    Returns None if we cannot compute the conversion (which the risk
    engine treats as PIP_VALUE_UNAVAILABLE).
    """
    pip = instrument.pip_size
    base = instrument.base_currency
    quote = instrument.quote_currency
    home = account_currency.upper()

    if quote == home:
        return pip

    if base == home:
        own = quotes_by_instrument.get(instrument.name)
        if own is None or own.mid == 0:
            return None
        return pip / own.mid

    direct = quotes_by_instrument.get(f"{quote}_{home}")
    if direct is not None and direct.mid != 0:
        return pip * direct.mid

    inverse = quotes_by_instrument.get(f"{home}_{quote}")
    if inverse is not None and inverse.mid != 0:
        return pip / inverse.mid

    return None


def size_position(
    *,
    instrument: Instrument,
    account_currency: str,
    nav_home: Decimal,
    risk_per_trade_pct: Decimal,
    entry_price: Decimal,
    stop_price: Decimal,
    quotes_by_instrument: dict[str, Quote],
) -> SizingResult | None:
    if nav_home <= 0:
        return None
    stop_distance_price = (entry_price - stop_price).copy_abs()
    if stop_distance_price <= 0:
        return None

    pip_size = instrument.pip_size
    stop_distance_pips = stop_distance_price / pip_size

    pip_value = compute_pip_value_home(instrument, account_currency, quotes_by_instrument)
    if pip_value is None or pip_value <= 0:
        return None

    risk_amount_home = nav_home * (risk_per_trade_pct / Decimal("100"))
    raw_units = risk_amount_home / (stop_distance_pips * pip_value)
    units = instrument.round_units(raw_units)

    # pip_value/pip_size = home currency per 1 unit of quote currency. Notional
    # in home = units (base) * price (quote/base) * (home/quote). For instruments
    # where base == home this simplifies to `units` (entry * home_per_quote == 1).
    home_per_quote = pip_value / pip_size
    notional_home = (units * entry_price * home_per_quote).copy_abs()
    estimated_margin = (notional_home * instrument.margin_rate).copy_abs()

    return SizingResult(
        units=units,
        raw_units=raw_units,
        pip_value_per_unit_home=pip_value,
        stop_distance_pips=stop_distance_pips,
        risk_amount_home=risk_amount_home,
        estimated_margin_home=estimated_margin,
    )

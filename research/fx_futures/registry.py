"""Futures instrument registry — frozen design from FX_FUTURES_UNIVERSE_DESIGN.md.

Seven full-size CME FX futures mapped to the seven spot majors' currencies.

Quote convention (decisive): every CME FX future quotes the FOREIGN currency as
base, i.e. USD per 1 foreign unit (XXX/USD). So each contract's price *is* the
USD value of one unit of that currency — exactly the quantity the carry factor's
per-currency USD-level matrix needs. No inversion is required to build USD levels
(unlike spot, where USD_JPY etc. needed 1/price).

The ``spot_inverted`` flag records that the contract is quoted the OPPOSITE way
to the spot corpus's USD-base pairs (USD_JPY/USD_CHF/USD_CAD): long the future is
long-foreign/short-USD, the sign-opposite of a long-USD_xxx spot position. This
flag is documentation/round-trip-mapping only; the carry diagnostic consumes the
contract prices directly as USD-per-currency.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FuturesContract:
    root: str            # CME root, e.g. "6E"
    yahoo_symbol: str    # Yahoo continuous front-month symbol, e.g. "6E=F"
    currency: str        # foreign currency the contract delivers, e.g. "EUR"
    spot_major: str      # spot-corpus analogue pair
    spot_inverted: bool  # True if spot pair is USD_xxx (opposite quote to future)
    # Contract spec is design metadata only (NOT used in the gross diagnostic).
    contract_size: float
    tick_size: float
    tick_value_usd: float


# Frozen universe (full-size contracts; E-micros excluded per the design).
CONTRACTS: dict[str, FuturesContract] = {
    "EUR": FuturesContract("6E", "6E=F", "EUR", "EUR_USD", False, 125_000, 0.00005, 6.25),
    "GBP": FuturesContract("6B", "6B=F", "GBP", "GBP_USD", False, 62_500, 0.0001, 6.25),
    "JPY": FuturesContract("6J", "6J=F", "JPY", "USD_JPY", True, 12_500_000, 0.0000005, 6.25),
    "CHF": FuturesContract("6S", "6S=F", "CHF", "USD_CHF", True, 125_000, 0.0001, 12.50),
    "AUD": FuturesContract("6A", "6A=F", "AUD", "AUD_USD", False, 100_000, 0.00005, 5.00),
    "CAD": FuturesContract("6C", "6C=F", "CAD", "USD_CAD", True, 100_000, 0.00005, 5.00),
    "NZD": FuturesContract("6N", "6N=F", "NZD", "NZD_USD", False, 100_000, 0.0001, 10.00),
}

# Order matches the carry factor's non-USD currency set (USD is the numeraire).
FUTURES_CURRENCIES = ["EUR", "GBP", "JPY", "AUD", "NZD", "CHF", "CAD"]


def yahoo_symbols() -> dict[str, str]:
    """currency -> Yahoo continuous symbol."""
    return {c: CONTRACTS[c].yahoo_symbol for c in FUTURES_CURRENCIES}

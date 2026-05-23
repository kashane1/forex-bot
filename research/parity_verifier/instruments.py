"""Static instrument metadata for the CAMPAIGN_002 H4 universe.

Re-derived here from the FX-major convention (JPY quote = pip 0.01,
all other USD-quote majors = pip 0.0001) so the verifier does not
import the bespoke engine's instrument-metadata module.
"""

from __future__ import annotations

from research.parity_verifier.models import InstrumentSpec

CAMPAIGN_002_INSTRUMENTS: dict[str, InstrumentSpec] = {
    "EUR_USD": InstrumentSpec(name="EUR_USD", pip_size=0.0001, base_currency="EUR", quote_currency="USD"),
    "GBP_USD": InstrumentSpec(name="GBP_USD", pip_size=0.0001, base_currency="GBP", quote_currency="USD"),
    "USD_JPY": InstrumentSpec(name="USD_JPY", pip_size=0.01, base_currency="USD", quote_currency="JPY"),
    "AUD_USD": InstrumentSpec(name="AUD_USD", pip_size=0.0001, base_currency="AUD", quote_currency="USD"),
    "USD_CAD": InstrumentSpec(name="USD_CAD", pip_size=0.0001, base_currency="USD", quote_currency="CAD"),
    "USD_CHF": InstrumentSpec(name="USD_CHF", pip_size=0.0001, base_currency="USD", quote_currency="CHF"),
    "NZD_USD": InstrumentSpec(name="NZD_USD", pip_size=0.0001, base_currency="NZD", quote_currency="USD"),
}


def get_instrument(name: str) -> InstrumentSpec:
    """Return the instrument spec; raise KeyError with a clear message
    if the verifier is asked to run on something outside CAMPAIGN_002."""

    try:
        return CAMPAIGN_002_INSTRUMENTS[name]
    except KeyError as exc:
        raise KeyError(
            f"{name!r} is not in the CAMPAIGN_002 H4 universe; "
            f"known: {sorted(CAMPAIGN_002_INSTRUMENTS)}"
        ) from exc

"""Financing rate sources.

Two v1 implementations:

* ``TableRateSource`` — wraps an explicit table of
  ``(date, instrument) -> RatePair`` entries. Used by hand-built
  fixtures and (in the future) by a host script that converts
  observed ``DAILY_FINANCING`` events into per-date rates.
* ``ConservativeStressRateSource`` — returns a debit-only,
  side-symmetric pessimistic bp/day for every date. The default
  table mirrors the bp/day values in
  ``src/forex_bot/financing.py`` (re-stated locally to preserve
  import isolation).

Both sources are ``ESTIMATED`` — neither produces ``MODELED``
financing. See ``docs/research/FINANCING_MODEL_PROTOCOL.md`` §13.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from research.financing.models import FinancingTreatment, FinancingSourceType, RatePair

# Mirrored from src/forex_bot/financing.CONSERVATIVE_BP_PER_DAY.
#
# The existing per-trade overlay uses a single bp/day per pair
# (the worse of long and short). The stress source here treats
# long and short symmetrically by debiting that worse value on
# both sides — the same conservatism, expressed in this module's
# per-side schema.
CONSERVATIVE_BP_PER_DAY: dict[str, float] = {
    "EUR_USD": 0.6,
    "GBP_USD": 0.7,
    "USD_JPY": 1.2,
    "AUD_USD": 0.7,
    "USD_CAD": 0.5,
    "USD_CHF": 0.9,
    "NZD_USD": 0.7,
}

# Default for any pair not listed: the table maximum, stays
# conservative. Mirrors src/forex_bot/financing._DEFAULT_BP_PER_DAY.
_DEFAULT_BP_PER_DAY = 1.2

_DAYS_PER_YEAR = 365


def _bp_per_day_to_annual_bp(bp_per_day: float) -> float:
    return bp_per_day * _DAYS_PER_YEAR


class FinancingRateSource(ABC):
    """Pluggable source of per-date, per-instrument financing
    rates. ``rate_for`` may return ``None`` to signal "no rate
    known for this date" — the calculator handles the fallback
    per ``FinancingCalculatorConfig.missing_rate_policy``.

    Sources declare their ``treatment`` so the run report can
    embed it. **Neither v1 source is ``MODELED``.**
    """

    name: str = "abstract"
    treatment: FinancingTreatment = FinancingTreatment.UNMODELED
    source_type: FinancingSourceType = FinancingSourceType.SYNTHETIC_FIXTURE

    @abstractmethod
    def rate_for(self, date_utc: date, instrument: str) -> RatePair | None:
        """Return the rate pair for one (date, instrument), or
        ``None`` if no rate is available."""


class TableRateSource(FinancingRateSource):
    """An explicit per-(date, instrument) table of rates.

    Missing entries return ``None``. ``treatment`` defaults to
    ``ESTIMATED`` since hand-built or fixture tables are by
    construction not reconciled-modeled data; callers may
    construct with ``treatment=UNMODELED`` for opt-out tests.

    Callers must not pass ``treatment=MODELED`` — that path is
    reserved for ``src/forex_bot/financing.FutureOandaObservedFinancingModel``.
    """

    def __init__(
        self,
        table: dict[tuple[date, str], RatePair],
        *,
        name: str = "table",
        treatment: FinancingTreatment = FinancingTreatment.ESTIMATED,
        source_type: FinancingSourceType = FinancingSourceType.SYNTHETIC_FIXTURE,
    ) -> None:
        if treatment == FinancingTreatment.MODELED:
            raise ValueError(
                "TableRateSource may not declare treatment=MODELED. "
                "MODELED is reserved for the future observed-rate path "
                "in src/forex_bot/financing.py."
            )
        self._table = dict(table)
        self.name = name
        self.treatment = treatment
        self.source_type = source_type

    def rate_for(self, date_utc: date, instrument: str) -> RatePair | None:
        return self._table.get((date_utc, instrument))


class ConservativeStressRateSource(FinancingRateSource):
    """Constant per-pair pessimistic bp/day, side-symmetric,
    debit-only. Returns the same value on every date.

    ``long_annual_bp`` and ``short_annual_bp`` on the returned
    ``RatePair`` are both **negative** (debit) — the stress view
    never assumes a credit.
    """

    treatment = FinancingTreatment.ESTIMATED
    source_type = FinancingSourceType.SYNTHETIC_FIXTURE

    def __init__(
        self,
        bp_per_day_table: dict[str, float] | None = None,
        *,
        default_bp_per_day: float = _DEFAULT_BP_PER_DAY,
        name: str = "conservative_stress",
    ) -> None:
        self._table = dict(bp_per_day_table or CONSERVATIVE_BP_PER_DAY)
        self._default = default_bp_per_day
        self.name = name

    def _bp_per_day(self, instrument: str) -> float:
        return self._table.get(instrument, self._default)

    def rate_for(self, _date_utc: date, instrument: str) -> RatePair | None:
        annual_bp = _bp_per_day_to_annual_bp(self._bp_per_day(instrument))
        # Debit on both sides — the stress view never credits.
        return RatePair(
            long_annual_bp=-annual_bp,
            short_annual_bp=-annual_bp,
        )


def default_stress_rate_source() -> ConservativeStressRateSource:
    """The default research-mode rate source: the bp/day stress
    table above, debit-only, ``ESTIMATED``."""
    return ConservativeStressRateSource()

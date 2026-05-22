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

from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum

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


# ---------------------------------------------------------------------------
# Financing-model interface (infra-foundation-001, Phase 2)
# ---------------------------------------------------------------------------
#
# The functions above ARE the conservative stress overlay. The classes
# below wrap financing treatment in an explicit interface so future
# campaigns and reports can state — and gate approval on — exactly how
# financing is handled. Financing is still NOT in the backtest engine's
# PnL; the engine's behaviour corresponds to NoFinancingModel (UNMODELED).


class FinancingTreatment(str, Enum):
    """How financing is treated for a backtest / campaign / approval.

    * MODELED   — real per-day financing is in the engine's PnL. No
                  model in this repo produces this yet.
    * ESTIMATED — financing is applied as the conservative stress
                  overlay only (not in engine PnL). Enough to gate paper
                  research; never enough for live.
    * UNMODELED — financing is not accounted for at all. A hard blocker
                  for any strategy approval.
    """

    MODELED = "modeled"
    ESTIMATED = "estimated"
    UNMODELED = "unmodeled"


class FinancingModel(ABC):
    """Interface for a financing-cost model used by research and reports.

    `treatment` declares how the model must be described in report
    metadata and how it interacts with strategy approval. `debit_r` and
    `debit_usd` return one closed trade's financing cost (in R and in
    USD). Costs are always >= 0 — a stress model never assumes a
    financing *credit*.
    """

    name: str = "abstract"
    treatment: FinancingTreatment = FinancingTreatment.UNMODELED

    @abstractmethod
    def debit_r(
        self, instrument: str, units: Decimal, entry_price: Decimal,
        stop_price: Decimal, bars_held: int, *, hours_per_bar: int = 4,
    ) -> float:
        """Financing debit for one closed trade, in R (fraction of risk)."""

    @abstractmethod
    def debit_usd(
        self, instrument: str, units: Decimal, entry_price: Decimal,
        bars_held: int, *, hours_per_bar: int = 4,
    ) -> float:
        """Financing debit for one closed trade, in USD."""


class NoFinancingModel(FinancingModel):
    """Financing is not accounted for at all — the backtest engine's
    current behaviour. An honest UNMODELED state, and a hard blocker for
    any strategy approval."""

    name = "none"
    treatment = FinancingTreatment.UNMODELED

    def debit_r(
        self, instrument: str, units: Decimal, entry_price: Decimal,
        stop_price: Decimal, bars_held: int, *, hours_per_bar: int = 4,
    ) -> float:
        return 0.0

    def debit_usd(
        self, instrument: str, units: Decimal, entry_price: Decimal,
        bars_held: int, *, hours_per_bar: int = 4,
    ) -> float:
        return 0.0


class ConservativeStressFinancingModel(FinancingModel):
    """The conservative per-pair bp/day stress overlay. Financing is NOT
    in engine PnL; this model supplies the after-the-fact stress debit
    that campaign reports deduct. ESTIMATED — enough to gate paper
    research, never enough for live."""

    name = "conservative_stress"
    treatment = FinancingTreatment.ESTIMATED

    def debit_r(
        self, instrument: str, units: Decimal, entry_price: Decimal,
        stop_price: Decimal, bars_held: int, *, hours_per_bar: int = 4,
    ) -> float:
        return financing_debit_r(
            instrument, units, entry_price, stop_price, bars_held, hours_per_bar,
        )

    def debit_usd(
        self, instrument: str, units: Decimal, entry_price: Decimal,
        bars_held: int, *, hours_per_bar: int = 4,
    ) -> float:
        return financing_debit_usd(
            instrument, units, entry_price, bars_held, hours_per_bar,
        )


class FutureOandaObservedFinancingModel(FinancingModel):
    """PLACEHOLDER — not implemented. Marks the seam where a real,
    OANDA-observed financing model would live.

    `treatment` is MODELED to document the *target*, but the class
    cannot be instantiated, so no report or approval can reach a false
    MODELED state through it. See docs/research/FINANCING_MODEL_DESIGN.md
    for what implementing it would require."""

    name = "future_oanda_observed"
    treatment = FinancingTreatment.MODELED  # aspirational; __init__ refuses

    def __init__(self) -> None:
        raise NotImplementedError(
            "FutureOandaObservedFinancingModel is a placeholder. OANDA "
            "exposes no historical financing-rate series and this bot has "
            "no DAILY_FINANCING history, so a real financing model cannot "
            "be built yet. See docs/research/FINANCING_MODEL_DESIGN.md."
        )

    def debit_r(
        self, instrument: str, units: Decimal, entry_price: Decimal,
        stop_price: Decimal, bars_held: int, *, hours_per_bar: int = 4,
    ) -> float:
        raise NotImplementedError("FutureOandaObservedFinancingModel is not implemented.")

    def debit_usd(
        self, instrument: str, units: Decimal, entry_price: Decimal,
        bars_held: int, *, hours_per_bar: int = 4,
    ) -> float:
        raise NotImplementedError("FutureOandaObservedFinancingModel is not implemented.")


def default_financing_model() -> FinancingModel:
    """The default financing model for research and reports: the
    conservative stress overlay. Deliberately ESTIMATED — research must
    always at least stress financing, never silently ignore it."""
    return ConservativeStressFinancingModel()


def financing_treatment_blocks_approval(
    treatment: FinancingTreatment,
    mode: str,
    *,
    human_override: bool = False,
) -> bool:
    """True if `treatment` blocks approving a strategy for loop `mode`.

    Rules:
      * MODELED   — never blocks on financing grounds.
      * live mode — always blocked unless financing is MODELED. Live
        trading unconditionally requires a real financing model; no
        `human_override` can bypass this.
      * ESTIMATED — does not block paper / demo.
      * UNMODELED — blocks paper / demo unless an explicit
        `human_override` is given (a deliberate, documented human call).

    This is a building block; Phase 5's approval-registry validation
    calls it. It governs only the financing dimension — live mode also
    has the existing config-layer live gates on top.
    """
    if treatment == FinancingTreatment.MODELED:
        return False
    if mode == "live":
        return True  # live unconditionally requires modeled financing
    if treatment == FinancingTreatment.ESTIMATED:
        return False
    # UNMODELED, non-live mode.
    return not human_override


def financing_metadata(model: FinancingModel) -> dict[str, object]:
    """Report-ready metadata describing the financing treatment.

    Every research report should embed this block so the financing
    posture is explicit, auditable, and never silently optimistic.
    """
    return {
        "financing_model": model.name,
        "financing_treatment": model.treatment.value,
        "financing_in_engine_pnl": model.treatment == FinancingTreatment.MODELED,
        "financing_is_live_blocker": model.treatment != FinancingTreatment.MODELED,
    }

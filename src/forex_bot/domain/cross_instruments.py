"""Non-USD FX cross registry — single source of truth for cross metadata.

This module is the registry for the first multi-market expansion: non-USD
FX crosses (EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY, ...). It is deliberately
*additive* and independent of the seven USD majors:

  * `forex_bot.data.m1_corpus_validation.MAJOR_PAIRS` stays the unchanged
    control/baseline universe.
  * This module supplies cross metadata (pip conventions, quote/settlement
    currency, carry legs, qualitative cost band, structural breaks) and a
    factory that reuses the existing tested `Instrument` model so pip and
    display-precision handling flow through one code path.

WHY A CROSS IS NOT A MAJOR (cost/financing)
-------------------------------------------
A "cross" here means neither leg is USD. That matters for cost modelling:

  * Spreads are generally *wider* (roughly the two underlying legs
    compounded) — see `cost_band` / `est_spread_pips`.
  * P&L accrues in the QUOTE currency, which is not USD, so converting risk
    or notional to USD needs a separate quote/USD rate. The majors'
    `financing.notional_usd` / `risk_usd` assume USD is one leg and are
    therefore WRONG for crosses — they must not be reused as-is.
  * Carry is genuinely two-legged (base-leg rate minus quote-leg rate); a
    single per-pair bp/day figure copied from a major is not valid.

Cost figures here are *qualitative retail estimates* carried from the
feasibility study (`docs/research/NON_USD_CROSS_FEASIBILITY_STUDY.md`),
labelled as estimates, to be replaced by real ingested-data diagnostics.
Nothing in this module is strategy evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from forex_bot.domain.instruments import Instrument

# Qualitative cost bands from the feasibility study. Ordering tightest →
# widest. These are ESTIMATES pending real ingested spread diagnostics.
CostBand = str  # "near_major" | "moderate" | "wide"


@dataclass(frozen=True)
class CrossSpec:
    """Static metadata for one non-USD FX cross.

    All price-convention fields follow OANDA conventions and are validated
    in `__post_init__`: JPY-quote crosses use pip_location -2 / display
    precision 3; all others use -4 / 5.
    """

    name: str
    tier: str  # "primary" (wave-1 required) | "extended" (wave-1 optional)
    cost_band: CostBand
    est_spread_pips: tuple[float, float]  # (low, high) qualitative estimate
    # Conservative carry stress, bp of notional per day, EXPLICIT per cross
    # (not the majors' table-max fallback). Estimate pending real data.
    conservative_bp_per_day: float
    is_carry_cross: bool  # classic positive-carry FX cross (e.g. AUD_JPY)
    structural_breaks: tuple[tuple[date, str], ...] = ()
    notes: str = ""
    # Filled by __post_init__ from the name.
    base_currency: str = field(default="", init=False)
    quote_currency: str = field(default="", init=False)
    pip_location: int = field(default=0, init=False)
    display_precision: int = field(default=0, init=False)
    is_jpy_cross: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        parts = self.name.split("_")
        if len(parts) != 2 or not all(len(p) == 3 and p.isalpha() and p.isupper() for p in parts):
            raise ValueError(f"cross name must be 'AAA_BBB' uppercase: {self.name!r}")
        base, quote = parts
        if "USD" in parts:
            raise ValueError(f"not a non-USD cross (has a USD leg): {self.name!r}")
        if base == quote:
            raise ValueError(f"degenerate pair: {self.name!r}")
        jpy = quote == "JPY"
        object.__setattr__(self, "base_currency", base)
        object.__setattr__(self, "quote_currency", quote)
        object.__setattr__(self, "is_jpy_cross", "JPY" in parts)
        object.__setattr__(self, "pip_location", -2 if jpy else -4)
        object.__setattr__(self, "display_precision", 3 if jpy else 5)
        if self.cost_band not in ("near_major", "moderate", "wide"):
            raise ValueError(f"unknown cost band {self.cost_band!r} for {self.name}")
        if self.conservative_bp_per_day < 0:
            raise ValueError(f"conservative_bp_per_day must be >= 0 for {self.name}")
        lo, hi = self.est_spread_pips
        if lo < 0 or hi < lo:
            raise ValueError(f"bad est_spread_pips {self.est_spread_pips} for {self.name}")

    @property
    def pip_size(self) -> Decimal:
        return Decimal(10) ** self.pip_location

    @property
    def carry_legs(self) -> tuple[str, str]:
        """The (long-leg, short-leg) currencies whose rate differential is
        the cross's carry. Held long, you earn base-leg rate and pay
        quote-leg rate; the realised carry is two-legged."""
        return (self.base_currency, self.quote_currency)

    def to_instrument(self, *, margin_rate: Decimal = Decimal("0.05")) -> Instrument:
        """Build a domain `Instrument` using the existing tested model.

        `margin_rate` defaults to the conservative model default; the real
        per-account rate comes from OANDA at ingestion time and is
        informational only (never gates research)."""
        return Instrument(
            name=self.name,
            type="CURRENCY",
            display_name=f"{self.base_currency}/{self.quote_currency}",
            display_precision=self.display_precision,
            pip_location=self.pip_location,
            trade_units_precision=0,
            minimum_trade_size=Decimal("1"),
            margin_rate=margin_rate,
        )


# Wave-1 registry. Cost bands / spread estimates / bp-per-day are
# qualitative estimates from the feasibility study, NOT measured values.
_WAVE1: tuple[CrossSpec, ...] = (
    CrossSpec(
        name="EUR_GBP", tier="primary", cost_band="near_major",
        est_spread_pips=(1.0, 2.0), conservative_bp_per_day=0.5,
        is_carry_cross=False,
        notes="Tightest cross; both legs low-rate; best cost candidate.",
    ),
    CrossSpec(
        name="EUR_JPY", tier="primary", cost_band="near_major",
        est_spread_pips=(1.0, 2.0), conservative_bp_per_day=0.8,
        is_carry_cross=True,
        notes="JPY-funded; near-major spread; mild positive carry.",
    ),
    CrossSpec(
        name="GBP_JPY", tier="primary", cost_band="wide",
        est_spread_pips=(2.5, 4.0), conservative_bp_per_day=1.0,
        is_carry_cross=True,
        notes="Volatile ('the Beast'); valued for breadth not cost.",
    ),
    CrossSpec(
        name="AUD_JPY", tier="primary", cost_band="moderate",
        est_spread_pips=(1.5, 3.0), conservative_bp_per_day=1.2,
        is_carry_cross=True,
        notes="Classic risk-on carry cross; financing is first-order.",
    ),
    CrossSpec(
        name="NZD_JPY", tier="extended", cost_band="wide",
        est_spread_pips=(2.5, 4.0), conservative_bp_per_day=1.2,
        is_carry_cross=True,
        notes="Carry cross; thinner liquidity, wider spread than AUD_JPY.",
    ),
    CrossSpec(
        name="EUR_CHF", tier="extended", cost_band="moderate",
        est_spread_pips=(1.5, 3.0), conservative_bp_per_day=0.7,
        is_carry_cross=False,
        structural_breaks=((date(2015, 1, 15), "SNB removed the 1.20 EUR/CHF floor"),),
        notes="Hard discontinuity 2015-01-15; window any pre-2015 study.",
    ),
    CrossSpec(
        name="GBP_CHF", tier="extended", cost_band="wide",
        est_spread_pips=(2.5, 4.0), conservative_bp_per_day=0.9,
        is_carry_cross=False,
        notes="Thin, wide; safe-haven CHF co-moves with JPY crosses risk-off.",
    ),
    CrossSpec(
        name="EUR_AUD", tier="extended", cost_band="moderate",
        est_spread_pips=(1.5, 3.0), conservative_bp_per_day=0.8,
        is_carry_cross=False,
        notes="Cross-region breadth (Europe vs Australasia).",
    ),
)

_REGISTRY: dict[str, CrossSpec] = {spec.name: spec for spec in _WAVE1}

# Convenience tuples (registry order preserved).
NONUSD_CROSS_PAIRS: tuple[str, ...] = tuple(_REGISTRY)
PRIMARY_CROSS_PAIRS: tuple[str, ...] = tuple(s.name for s in _WAVE1 if s.tier == "primary")
EXTENDED_CROSS_PAIRS: tuple[str, ...] = tuple(s.name for s in _WAVE1 if s.tier == "extended")


def registered_crosses() -> tuple[str, ...]:
    """All registered non-USD cross names, in registry order."""
    return NONUSD_CROSS_PAIRS


def is_nonusd_cross(instrument: str) -> bool:
    """True if `instrument` is a registered non-USD cross."""
    return instrument in _REGISTRY


def cross_spec(instrument: str) -> CrossSpec:
    """Return the `CrossSpec` for a registered cross, else raise KeyError."""
    return _REGISTRY[instrument]


def cross_instrument(instrument: str, *, margin_rate: Decimal = Decimal("0.05")) -> Instrument:
    """Build a domain `Instrument` for a registered cross."""
    return _REGISTRY[instrument].to_instrument(margin_rate=margin_rate)


def cross_pip_location(instrument: str) -> int:
    """Pip location for a registered cross (-2 for JPY-quote, else -4)."""
    return _REGISTRY[instrument].pip_location


def cross_display_precision(instrument: str) -> int:
    """Display precision for a registered cross (3 for JPY-quote, else 5)."""
    return _REGISTRY[instrument].display_precision

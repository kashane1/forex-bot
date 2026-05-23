"""Financing calculator domain models.

Pydantic models pin the shapes the calculator consumes and emits.
``extra="forbid"`` catches schema drift. The
``strategy_evidence: false`` rail on ``FinancingRunReport`` is
enforced by a Pydantic validator — constructing a report with the
flag flipped raises ``ValidationError``.

See ``docs/research/FINANCING_MODEL_PROTOCOL.md`` for the
field-by-field protocol.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_INSTRUMENT_RE = re.compile(r"^[A-Z]{3}_[A-Z]{3}$")
_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")


class FinancingTreatment(str, Enum):
    """How financing is treated.

    Mirrored from ``src/forex_bot/financing.py`` so this module
    stays import-isolated. The values match the canonical enum
    so report metadata interoperates.

    * ``MODELED``   — real per-day financing in engine PnL. **No
                      source in this module produces this.** It
                      exists only so report consumers can compare
                      against the canonical enum's values.
    * ``ESTIMATED`` — stress overlay applied off-engine. The best
                      this module can claim.
    * ``UNMODELED`` — financing not accounted for at all. Used by
                      callers who explicitly opt out.
    """

    MODELED = "modeled"
    ESTIMATED = "estimated"
    UNMODELED = "unmodeled"


class MissingRatePolicy(str, Enum):
    """How the calculator handles a ``rate_source`` returning
    ``None`` for a given (date, instrument).

    * ``CONSERVATIVE`` — apply the configured conservative
                         fallback bp/day as a debit; default.
    * ``SKIP``         — emit no event for that date; mark the
                         summary's ``rate_was_missing_any`` True.
    * ``ERROR``        — raise ``MissingFinancingRateError``.
    """

    CONSERVATIVE = "conservative"
    SKIP = "skip"
    ERROR = "error"


class RatePair(BaseModel):
    """Annualized financing rates in basis points for one (date,
    instrument). ``long_annual_bp`` is what a *long* position
    pays / receives per year as a fraction of notional;
    ``short_annual_bp`` is the same for a *short* position.

    Signs follow the §4 convention: negative ⇒ the position pays
    (debit); positive ⇒ the position receives (credit). A symmetric
    stress source returns ``long = short = -|bp|`` (debit-only).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    long_annual_bp: float
    short_annual_bp: float


class PositionInterval(BaseModel):
    """One closed position the calculator computes financing for."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    position_id: str = Field(min_length=1, max_length=128)
    instrument: str
    side: str
    units: Decimal
    entry_price: Decimal
    open_time: datetime
    close_time: datetime
    home_currency: str = "USD"

    @field_validator("instrument")
    @classmethod
    def _check_instrument(cls, v: str) -> str:
        if not _INSTRUMENT_RE.fullmatch(v):
            raise ValueError(
                f"instrument must match {_INSTRUMENT_RE.pattern}, got {v!r}"
            )
        return v

    @field_validator("home_currency")
    @classmethod
    def _check_home(cls, v: str) -> str:
        if not _CURRENCY_RE.fullmatch(v):
            raise ValueError(
                f"home_currency must match {_CURRENCY_RE.pattern}, got {v!r}"
            )
        return v

    @field_validator("side")
    @classmethod
    def _check_side(cls, v: str) -> str:
        if v not in {"long", "short"}:
            raise ValueError(f"side must be 'long' or 'short', got {v!r}")
        return v

    @field_validator("units", "entry_price")
    @classmethod
    def _check_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError(f"must be > 0, got {v}")
        return v

    @model_validator(mode="after")
    def _check_times(self) -> PositionInterval:
        if self.open_time.tzinfo is None or self.close_time.tzinfo is None:
            raise ValueError("open_time and close_time must be timezone-aware")
        if self.close_time <= self.open_time:
            raise ValueError(
                f"close_time {self.close_time} must be strictly after "
                f"open_time {self.open_time}"
            )
        return self

    @property
    def base_currency(self) -> str:
        return self.instrument.split("_", 1)[0]

    @property
    def quote_currency(self) -> str:
        return self.instrument.split("_", 1)[1]


class FinancingCalculatorConfig(BaseModel):
    """Calculator-wide configuration. Defaults match the protocol's
    v1 conservative defaults."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    rollover_hour_utc: int = Field(default=21, ge=0, le=23)
    triple_swap_weekday: int | None = Field(default=2, ge=0, le=6)
    skip_weekends: bool = True
    missing_rate_policy: MissingRatePolicy = MissingRatePolicy.CONSERVATIVE
    home_currency: str = "USD"
    conservative_fallback_bp_per_day: float = Field(default=1.2, gt=0)

    @field_validator("home_currency")
    @classmethod
    def _check_home(cls, v: str) -> str:
        if not _CURRENCY_RE.fullmatch(v):
            raise ValueError(
                f"home_currency must match {_CURRENCY_RE.pattern}, got {v!r}"
            )
        return v


class DailyFinancingEvent(BaseModel):
    """One rollover event for one position."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    position_id: str
    instrument: str
    date_utc: date
    weekday: int = Field(ge=0, le=6)
    rollover_multiplier: int = Field(ge=1)
    rate_long_annual_bp: float | None
    rate_short_annual_bp: float | None
    applied_side: str
    applied_rate_bp_per_day: float
    notional_home: float
    cashflow_home: float
    cashflow_home_stress: float
    rate_source_name: str
    rate_was_missing: bool
    notes: list[str] = Field(default_factory=list)

    @field_validator("applied_side")
    @classmethod
    def _check_side(cls, v: str) -> str:
        if v not in {"long", "short"}:
            raise ValueError(f"applied_side must be 'long' or 'short', got {v!r}")
        return v

    @model_validator(mode="after")
    def _check_stress_le_zero(self) -> DailyFinancingEvent:
        if self.cashflow_home_stress > 0:
            raise ValueError(
                "cashflow_home_stress must be <= 0 — the stress view "
                "never assumes a financing credit"
            )
        return self


class PositionFinancingSummary(BaseModel):
    """One row per ``PositionInterval``."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    position_id: str
    instrument: str
    side: str
    events: list[DailyFinancingEvent]
    rollovers: int = Field(ge=0)
    cashflow_home_total: float
    cashflow_home_stress_total: float
    rate_was_missing_any: bool

    @model_validator(mode="after")
    def _check_rollover_count_matches(self) -> PositionFinancingSummary:
        if self.rollovers != len(self.events):
            raise ValueError(
                f"rollovers={self.rollovers} but events has "
                f"{len(self.events)} entries"
            )
        return self


class FinancingRunReport(BaseModel):
    """Position-set aggregate, ready for dump.

    ``strategy_evidence`` is pinned to ``False`` by a Pydantic
    validator — constructing a report with the flag flipped is a
    ``ValidationError``. ``financing_in_engine_pnl`` and
    ``financing_is_live_blocker`` are similarly pinned: this
    module is **never** the source of MODELED financing.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    config: FinancingCalculatorConfig
    rate_source_name: str
    rate_source_treatment: FinancingTreatment
    home_currency: str
    positions: list[PositionFinancingSummary]
    event_count: int = Field(ge=0)
    cashflow_home_total: float
    cashflow_home_stress_total: float
    missing_rate_event_count: int = Field(ge=0)
    strategy_evidence: bool = False
    financing_treatment: FinancingTreatment
    financing_in_engine_pnl: bool = False
    financing_is_live_blocker: bool = True
    generated_at_utc: datetime = Field(
        default_factory=lambda: datetime.now(UTC).replace(microsecond=0),
    )

    @field_validator("strategy_evidence")
    @classmethod
    def _pin_strategy_evidence(cls, v: bool) -> bool:
        if v:
            raise ValueError(
                "strategy_evidence must be False — this calculator is "
                "research-only and never produces strategy evidence"
            )
        return v

    @field_validator("financing_in_engine_pnl")
    @classmethod
    def _pin_engine_pnl(cls, v: bool) -> bool:
        if v:
            raise ValueError(
                "financing_in_engine_pnl must be False — this module "
                "does not modify the bespoke engine's PnL stream"
            )
        return v

    @field_validator("financing_is_live_blocker")
    @classmethod
    def _pin_live_blocker(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "financing_is_live_blocker must be True — this module "
                "is never the source of MODELED financing, so it never "
                "lifts the live-promotion blocker"
            )
        return v

    @model_validator(mode="after")
    def _check_treatment_matches(self) -> FinancingRunReport:
        if self.financing_treatment != self.rate_source_treatment:
            raise ValueError(
                "financing_treatment must equal rate_source_treatment "
                f"(report={self.financing_treatment!r}, "
                f"source={self.rate_source_treatment!r})"
            )
        if self.financing_treatment == FinancingTreatment.MODELED:
            raise ValueError(
                "financing_treatment must not be MODELED — research/financing "
                "never produces MODELED financing"
            )
        if self.event_count != sum(p.rollovers for p in self.positions):
            raise ValueError(
                f"event_count={self.event_count} but positions report "
                f"{sum(p.rollovers for p in self.positions)} rollovers"
            )
        return self

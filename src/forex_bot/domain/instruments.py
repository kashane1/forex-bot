"""Instrument metadata as exposed by OANDA per account."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Instrument(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    name: str
    type: str
    display_name: str | None = None
    display_precision: int
    pip_location: int
    trade_units_precision: int
    minimum_trade_size: Decimal = Field(default=Decimal("1"))
    maximum_order_units: Decimal | None = None
    maximum_position_size: Decimal | None = None
    margin_rate: Decimal = Field(default=Decimal("0.05"))
    minimum_trailing_stop_distance: Decimal | None = None
    maximum_trailing_stop_distance: Decimal | None = None

    @property
    def base_currency(self) -> str:
        return self.name.split("_", 1)[0]

    @property
    def quote_currency(self) -> str:
        return self.name.split("_", 1)[1]

    @property
    def pip_size(self) -> Decimal:
        return Decimal(10) ** self.pip_location

    def round_units(self, units: Decimal) -> Decimal:
        """Round toward zero to the broker-allowed trade units precision."""
        if self.trade_units_precision <= 0:
            return units.to_integral_value(rounding="ROUND_DOWN")
        quant = Decimal(1).scaleb(-self.trade_units_precision)
        return units.quantize(quant, rounding="ROUND_DOWN")

    def round_price(self, price: Decimal) -> Decimal:
        quant = Decimal(1).scaleb(-self.display_precision)
        return price.quantize(quant, rounding="ROUND_HALF_UP")

    def price_to_pips(self, distance: Decimal) -> Decimal:
        return (distance / self.pip_size).copy_abs()

    def pips_to_price(self, pips: Decimal) -> Decimal:
        return pips * self.pip_size

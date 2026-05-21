"""Fill model: long entry = ask, long exit = bid, short mirror, with
configurable slippage applied in the unfavourable direction."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class FillModel:
    fixed_slippage_pips: Decimal
    spread_slippage_multiplier: Decimal

    def entry_price(
        self,
        *,
        side: str,
        bid: Decimal,
        ask: Decimal,
        pip_size: Decimal,
    ) -> Decimal:
        spread_pips = (ask - bid) / pip_size
        slip_pips = max(
            self.fixed_slippage_pips,
            spread_pips * self.spread_slippage_multiplier,
        )
        slip = slip_pips * pip_size
        if side == "long":
            return ask + slip
        return bid - slip

    def exit_price(
        self,
        *,
        side: str,
        bid: Decimal,
        ask: Decimal,
        pip_size: Decimal,
    ) -> Decimal:
        spread_pips = (ask - bid) / pip_size
        slip_pips = max(
            self.fixed_slippage_pips,
            spread_pips * self.spread_slippage_multiplier,
        )
        slip = slip_pips * pip_size
        if side == "long":
            return bid - slip
        return ask + slip

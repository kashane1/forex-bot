"""Strategy interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from forex_bot.domain.candles import CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState
from forex_bot.domain.positions import Position
from forex_bot.domain.signals import Signal


@dataclass(frozen=True)
class StrategyContext:
    """Per-call inputs the strategy is allowed to read."""

    instrument: Instrument
    candles: CandleFrame
    market_state: MarketState
    open_positions: list[Position]
    config: dict[str, Any]


class Strategy(Protocol):
    name: str
    version: str

    def warmup_bars_required(self) -> int: ...
    def generate_signal(self, ctx: StrategyContext) -> Signal | None: ...

"""Strategies. Each strategy returns Signal objects only — never an order."""

from forex_bot.strategies.base import Strategy, StrategyContext
from forex_bot.strategies.mean_reversion import MeanReversionStrategy
from forex_bot.strategies.trend_following import TrendFollowingStrategy
from forex_bot.strategies.volatility_breakout import VolatilityBreakoutStrategy

__all__ = [
    "MeanReversionStrategy",
    "Strategy",
    "StrategyContext",
    "TrendFollowingStrategy",
    "VolatilityBreakoutStrategy",
]

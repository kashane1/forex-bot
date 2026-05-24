"""Strategies. Each strategy returns Signal objects only — never an order."""

from forex_bot.strategies.base import Strategy, StrategyContext
from forex_bot.strategies.mean_reversion import MeanReversionStrategy
from forex_bot.strategies.pullback_continuation import PullbackContinuationStrategy
from forex_bot.strategies.random_entry_anchor import RandomEntryAnchorStrategy
from forex_bot.strategies.regime_switcher_atr_percentile import (
    RegimeSwitcherAtrPercentileStrategy,
)
from forex_bot.strategies.session_breakout import SessionBreakoutStrategy
from forex_bot.strategies.trend_following import TrendFollowingStrategy
from forex_bot.strategies.volatility_breakout import VolatilityBreakoutStrategy

__all__ = [
    "MeanReversionStrategy",
    "PullbackContinuationStrategy",
    "RandomEntryAnchorStrategy",
    "RegimeSwitcherAtrPercentileStrategy",
    "SessionBreakoutStrategy",
    "Strategy",
    "StrategyContext",
    "TrendFollowingStrategy",
    "VolatilityBreakoutStrategy",
]

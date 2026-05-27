"""CAMPAIGN_019 — mean reversion with z-score thesis-invalidation exit.

RESEARCH ONLY. Entry logic is identical to C008. Thesis invalidation is
applied by the backtest engine when ``thesis_invalidation_enabled`` is wired.
"""

from __future__ import annotations

from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.mean_reversion import MeanReversionStrategy
from forex_bot.strategies.mean_reversion_protective_stop import (
    C008_ENTRY_KEYS,
    c008_entry_params,
)

__all__ = ["C008_ENTRY_KEYS", "MeanReversionThesisInvalidationStrategy", "c008_entry_params"]


class MeanReversionThesisInvalidationStrategy:
    """``mean_reversion_thesis_invalidation 0.1.0-c019`` — CAMPAIGN_019."""

    name: str = "mean_reversion_thesis_invalidation"
    paper_only: bool = True

    def __init__(self, version: str = "0.1.0-c019") -> None:
        self.version = version
        self._entry = MeanReversionStrategy(version=version)

    def warmup_bars_required(self) -> int:
        return self._entry.warmup_bars_required()

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        cfg = dict(ctx.config)
        cfg["midline_exit"] = False
        entry_ctx = StrategyContext(
            instrument=ctx.instrument,
            candles=ctx.candles,
            market_state=ctx.market_state,
            open_positions=ctx.open_positions,
            config=cfg,
        )
        sig = self._entry.generate_signal(entry_ctx)
        if sig is None:
            return None
        return sig.model_copy(
            update={
                "strategy_name": self.name,
                "strategy_version": self.version,
                "take_profit_price": None,
                "exit_model": "hard_stop_thesis_invalidation_or_time",
            }
        )

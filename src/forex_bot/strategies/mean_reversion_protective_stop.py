"""CAMPAIGN_018 — mean reversion with protective stop after +1R MFE.

RESEARCH ONLY. Entry logic is identical to C008 (`mean_reversion 0.1.0-c008`).
The protective stop transition is applied by the backtest engine when
`protective_stop_after_r=1.0` is wired — not by the live executor.
"""

from __future__ import annotations

from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.mean_reversion import MeanReversionStrategy

C008_ENTRY_KEYS = (
    "atr_lookback",
    "zscore_lookback",
    "zscore_long_threshold",
    "zscore_short_threshold",
    "rsi_lookback",
    "regime_ema",
    "adx_lookback",
    "adx_max",
    "atr_stop_multiple",
    "trailing_stop_atr_multiple",
    "max_bars_in_trade",
    "min_atr_pips",
    "timeframe",
)


class MeanReversionProtectiveStopStrategy:
    """`mean_reversion_protective_stop 0.1.0-c018` — CAMPAIGN_018."""

    name: str = "mean_reversion_protective_stop"
    paper_only: bool = True

    def __init__(self, version: str = "0.1.0-c018") -> None:
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
                "exit_model": "hard_stop_protective_or_time",
            }
        )


def c008_entry_params(cfg: dict) -> dict:
    """Extract entry-parameter subset for parity checks vs C008."""
    return {k: cfg.get(k) for k in C008_ENTRY_KEYS}

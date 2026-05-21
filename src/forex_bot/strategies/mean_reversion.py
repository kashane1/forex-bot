"""Mean reversion strategy. PAPER-ONLY in v0. The strategy never opens
trades against a trend, requires a hard stop, and is automatically
disabled by the risk engine in live/practice mode."""

from __future__ import annotations

import hashlib
from datetime import UTC
from decimal import Decimal

import pandas as pd

from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import atr, ema, rsi, zscore


class MeanReversionStrategy:
    name: str = "mean_reversion"
    paper_only: bool = True

    def __init__(self, version: str = "0.1.0") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        return 220

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        z_len = int(cfg.get("zscore_lookback", 20))
        z_long_threshold = float(cfg.get("zscore_long_threshold", -2.0))
        z_short_threshold = float(cfg.get("zscore_short_threshold", 2.0))
        atr_len = int(cfg.get("atr_lookback", 14))
        atr_multiple = float(cfg.get("atr_stop_multiple", 1.5))
        rsi_len = int(cfg.get("rsi_lookback", 14))
        regime_ema = int(cfg.get("regime_ema", 200))
        timeframe = cfg.get("timeframe", "H4")

        needed = max(regime_ema, z_len, atr_len, rsi_len) + 2
        if len(df) < needed:
            return None

        close = df["close"]
        high = df["high"]
        low = df["low"]
        z = zscore(close, z_len)
        r = rsi(close, rsi_len)
        regime = ema(close, regime_ema)
        atr_series = atr(high, low, close, atr_len)
        regime_slope = regime.diff().rolling(window=20, min_periods=20).mean()

        last_z = float(z.iloc[-1])
        last_r = float(r.iloc[-1])
        last_close = float(close.iloc[-1])
        last_atr = float(atr_series.iloc[-1])
        last_slope = float(regime_slope.iloc[-1])

        if abs(last_slope) > last_atr * 0.05:
            return None

        side: str | None = None
        if last_z <= z_long_threshold and last_r < 35:
            side = "long"
            stop = last_close - atr_multiple * last_atr
        elif last_z >= z_short_threshold and last_r > 65:
            side = "short"
            stop = last_close + atr_multiple * last_atr
        else:
            return None

        if any(not pos.is_flat and pos.instrument == ctx.instrument.name for pos in ctx.open_positions):
            return None

        timestamp = pd.Timestamp(df.index[-1]).tz_convert(UTC).to_pydatetime()
        return Signal(
            signal_id=hashlib.sha1(
                f"{self.name}|{self.version}|{ctx.instrument.name}|{timestamp.isoformat()}|{side}".encode()
            ).hexdigest()[:24],
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe=timeframe,
            timestamp=timestamp,
            side=side,  # type: ignore[arg-type]
            entry_intent="market",
            stop_model=f"ATR{atr_len}*{atr_multiple}",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="midline_or_time",
            features={"z": last_z, "rsi": last_r, "regime_slope": last_slope},
            reason="z-score reversion in non-trending regime",
        )

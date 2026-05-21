"""Volatility breakout strategy.

Trades a break of a compressed Donchian range. Compression is defined as
current Donchian width below a percentile of recent widths. The break
direction also has to agree with the higher-timeframe EMA regime.
"""

from __future__ import annotations

import hashlib
from datetime import UTC
from decimal import Decimal
from typing import Any

import pandas as pd

from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import atr, donchian_high, donchian_low, ema


class VolatilityBreakoutStrategy:
    name: str = "volatility_breakout"

    def __init__(self, version: str = "0.1.0") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        return 240

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        donchian_len = int(cfg.get("donchian_lookback", 20))
        compression_lookback = int(cfg.get("compression_lookback", 60))
        compression_pct = float(cfg.get("compression_percentile", 25.0))
        atr_len = int(cfg.get("atr_lookback", 14))
        atr_multiple = float(cfg.get("atr_stop_multiple", 2.0))
        regime_ema = int(cfg.get("regime_ema", 200))
        timeframe = cfg.get("timeframe", "H4")

        needed = max(regime_ema, compression_lookback, donchian_len, atr_len) + 2
        if len(df) < needed:
            return None

        close = df["close"]
        high = df["high"]
        low = df["low"]
        d_high = donchian_high(high, donchian_len)
        d_low = donchian_low(low, donchian_len)
        widths = (d_high - d_low).dropna()
        if len(widths) < compression_lookback:
            return None
        recent_widths = widths.iloc[-compression_lookback:]
        last_width = float(widths.iloc[-1])
        threshold = float(recent_widths.quantile(compression_pct / 100.0))
        if last_width > threshold:
            return None

        atr_series = atr(high, low, close, atr_len)
        regime = ema(close, regime_ema)
        last_close = float(close.iloc[-1])
        last_dh = float(d_high.iloc[-1])
        last_dl = float(d_low.iloc[-1])
        last_atr = float(atr_series.iloc[-1])
        last_regime = float(regime.iloc[-1])

        side: str | None = None
        if last_close > last_dh and last_close > last_regime:
            side = "long"
        elif last_close < last_dl and last_close < last_regime:
            side = "short"
        else:
            return None

        if side == "long":
            stop = min(last_dl, last_close - atr_multiple * last_atr)
        else:
            stop = max(last_dh, last_close + atr_multiple * last_atr)

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
            stop_model=f"compressed_range_or_ATR{atr_len}*{atr_multiple}",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="trailing_or_time",
            features={
                "last_width": last_width,
                "compression_threshold": threshold,
                "regime_ema": last_regime,
            },
            reason="compression break with regime agreement",
        )


def _isnan(v: Any) -> bool:
    try:
        return v != v
    except TypeError:
        return False

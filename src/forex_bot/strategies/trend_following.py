"""Trend-following breakout strategy.

Long: EMA fast > EMA slow AND prior-bar Donchian high broken AND ATR
floor met. Short: mirror. Stop is ATR-based; the strategy emits stop_price
but never sizes the position (that is the risk engine's job).
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


class TrendFollowingStrategy:
    name: str = "trend_following"

    def __init__(self, version: str = "0.1.0") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        return 220  # ema_slow=200 + buffer

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        ema_fast_len = int(cfg.get("ema_fast", 50))
        ema_slow_len = int(cfg.get("ema_slow", 200))
        donchian_len = int(cfg.get("donchian_lookback", 20))
        atr_len = int(cfg.get("atr_lookback", 14))
        atr_multiple = float(cfg.get("atr_stop_multiple", 2.5))
        timeframe = cfg.get("timeframe", "H4")
        min_atr_pips_by_pair = cfg.get("min_atr_pips", {}) or {}
        min_atr_pips = float(min_atr_pips_by_pair.get(ctx.instrument.name, 0.0))

        needed = max(ema_slow_len, donchian_len, atr_len) + 2
        if len(df) < needed:
            return None

        close = df["close"]
        high = df["high"]
        low = df["low"]

        ef = ema(close, ema_fast_len)
        es = ema(close, ema_slow_len)
        d_high = donchian_high(high, donchian_len)
        d_low = donchian_low(low, donchian_len)
        atr_series = atr(high, low, close, atr_len)

        last_idx = df.index[-1]
        last_close = float(close.iloc[-1])
        last_ef = float(ef.iloc[-1])
        last_es = float(es.iloc[-1])
        last_dh = float(d_high.iloc[-1])
        last_dl = float(d_low.iloc[-1])
        last_atr = float(atr_series.iloc[-1])

        if any(_isnan(v) for v in (last_ef, last_es, last_dh, last_dl, last_atr)):
            return None

        # Block new entries if we already have a position in this instrument.
        if any(not pos.is_flat and pos.instrument == ctx.instrument.name for pos in ctx.open_positions):
            return None

        pip_size = float(ctx.instrument.pip_size)
        atr_pips = last_atr / pip_size if pip_size else 0.0
        if atr_pips < min_atr_pips:
            return None

        side: str | None = None
        reason = ""
        if last_ef > last_es and last_close > last_dh:
            side = "long"
            reason = f"breakout above Donchian-{donchian_len} ({last_dh:.5f}) with fast>slow"
        elif last_ef < last_es and last_close < last_dl:
            side = "short"
            reason = f"breakdown below Donchian-{donchian_len} ({last_dl:.5f}) with fast<slow"
        else:
            return None

        if side == "long":
            stop = last_close - atr_multiple * last_atr
        else:
            stop = last_close + atr_multiple * last_atr

        signal_id = _stable_signal_id(
            self.name,
            self.version,
            ctx.instrument.name,
            timeframe,
            last_idx,
            side,
        )

        return Signal(
            signal_id=signal_id,
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe=timeframe,
            timestamp=pd.Timestamp(last_idx).tz_convert(UTC).to_pydatetime(),
            side=side,  # type: ignore[arg-type]
            entry_intent="market",
            stop_model=f"ATR{atr_len}*{atr_multiple}",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="trailing_or_opposite_breakout_or_time",
            features={
                "ema_fast": last_ef,
                "ema_slow": last_es,
                "donchian_high": last_dh,
                "donchian_low": last_dl,
                "atr": last_atr,
                "atr_pips": atr_pips,
                "last_close": last_close,
            },
            reason=reason,
        )


def _isnan(v: Any) -> bool:
    try:
        return v != v  # NaN check without importing math
    except TypeError:
        return False


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]

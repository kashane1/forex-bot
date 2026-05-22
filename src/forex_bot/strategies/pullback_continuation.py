"""Pullback-continuation strategy — `pullback_continuation 0.1.0-c007`.

CAMPAIGN_007. A genuinely different entry from the Donchian breakout:
instead of buying a fresh extreme (which CAMPAIGN_002-004 showed buys
exhaustion), this enters *after* price has pulled back toward the trend
EMA and then *resumes* the trend.

Entry logic (completed bars only, prior bars only, no lookahead) at the
latest completed bar `t`:

  1. Trend regime: EMA-fast > EMA-slow (uptrend) or < (downtrend).
  2. Pullback: within the last `pullback_lookback` bars *before* `t`,
     price came within `pullback_band` × ATR of EMA-fast (it retraced
     to the moving average).
  3. Continuation: bar `t` resumes the trend — for a long, close[t] >
     high[t-1] AND close[t] > EMA-fast[t]; mirror for a short.

No Donchian channel anywhere. Stop = `atr_stop_multiple` × ATR-14; an
optional ATR trailing stop is applied by the engine.

Predeclared parameters and rationale:
docs/research/CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md.
"""

from __future__ import annotations

import hashlib
from datetime import UTC
from decimal import Decimal
from typing import Any

import pandas as pd

from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import atr, ema


class PullbackContinuationStrategy:
    name: str = "pullback_continuation"

    def __init__(self, version: str = "0.1.0-c007") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        return 220  # ema_slow 200 + buffer

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        ema_fast_len = int(cfg.get("ema_fast", 50))
        ema_slow_len = int(cfg.get("ema_slow", 200))
        atr_len = int(cfg.get("atr_lookback", 14))
        pullback_lookback = int(cfg.get("pullback_lookback", 6))
        pullback_band = float(cfg.get("pullback_band", 0.5))
        atr_multiple = float(cfg.get("atr_stop_multiple", 2.0))
        timeframe = cfg.get("timeframe", "H4")
        min_atr_pips_by_pair = cfg.get("min_atr_pips", {}) or {}
        min_atr_pips = float(min_atr_pips_by_pair.get(ctx.instrument.name, 0.0))

        needed = max(ema_slow_len, atr_len, pullback_lookback) + 3
        if len(df) < needed:
            return None

        close = df["close"]
        high = df["high"]
        low = df["low"]

        ef = ema(close, ema_fast_len)
        es = ema(close, ema_slow_len)
        atr_series = atr(high, low, close, atr_len)

        last_close = float(close.iloc[-1])
        prev_high = float(high.iloc[-2])
        prev_low = float(low.iloc[-2])
        last_ef = float(ef.iloc[-1])
        last_es = float(es.iloc[-1])
        last_atr = float(atr_series.iloc[-1])

        if any(_isnan(v) for v in (last_ef, last_es, last_atr)):
            return None

        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        pip_size = float(ctx.instrument.pip_size)
        atr_pips = last_atr / pip_size if pip_size else 0.0
        if atr_pips < min_atr_pips:
            return None

        band = pullback_band * last_atr
        # Pullback window: the `pullback_lookback` bars BEFORE bar t.
        win_low = low.iloc[-(pullback_lookback + 1):-1]
        win_high = high.iloc[-(pullback_lookback + 1):-1]
        ef_window = ef.iloc[-(pullback_lookback + 1):-1]
        if win_low.isna().any() or ef_window.isna().any():
            return None

        side: str | None = None
        reason = ""
        if last_ef > last_es:
            # Uptrend. Did price pull back to within `band` of EMA-fast?
            pulled_back = bool((win_low <= (ef_window + band)).any())
            continuation = last_close > prev_high and last_close > last_ef
            if pulled_back and continuation:
                side = "long"
                reason = (
                    f"uptrend pullback-continuation: low retraced within "
                    f"{pullback_band}*ATR of EMA{ema_fast_len}, "
                    f"close>{prev_high:.5f} (prior high) & >EMA{ema_fast_len}"
                )
        elif last_ef < last_es:
            pulled_back = bool((win_high >= (ef_window - band)).any())
            continuation = last_close < prev_low and last_close < last_ef
            if pulled_back and continuation:
                side = "short"
                reason = (
                    f"downtrend pullback-continuation: high retraced within "
                    f"{pullback_band}*ATR of EMA{ema_fast_len}, "
                    f"close<{prev_low:.5f} (prior low) & <EMA{ema_fast_len}"
                )

        if side is None:
            return None

        if side == "long":
            stop = last_close - atr_multiple * last_atr
        else:
            stop = last_close + atr_multiple * last_atr

        last_idx = df.index[-1]
        return Signal(
            signal_id=_stable_signal_id(
                self.name, self.version, ctx.instrument.name, timeframe,
                last_idx, side,
            ),
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe=timeframe,
            timestamp=pd.Timestamp(last_idx).tz_convert(UTC).to_pydatetime(),
            side=side,  # type: ignore[arg-type]
            entry_intent="market",
            stop_model=f"ATR{atr_len}*{atr_multiple}",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="atr_trailing_or_time",
            features={
                "ema_fast": last_ef,
                "ema_slow": last_es,
                "atr": last_atr,
                "atr_pips": atr_pips,
                "last_close": last_close,
            },
            reason=reason,
        )


def _isnan(v: Any) -> bool:
    try:
        return v != v
    except TypeError:
        return False


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]

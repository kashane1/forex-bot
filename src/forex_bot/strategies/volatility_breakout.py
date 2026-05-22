"""Volatility-breakout strategy — a genuinely different entry family.

`volatility_breakout 0.1.0-c004` (CAMPAIGN_004). This is NOT a Donchian
trend rescue: it does not use an EMA 50/200 regime filter. It trades a
breakout that occurs *out of a volatility-compressed regime*.

Entry logic (all prior-bars-only, no lookahead) at the latest completed
bar `t`:

  1. Compression: ATR-14 at bar `t-1` is at or below the
     `compression_percentile` of the ATR-14 distribution over the
     `compression_lookback` bars ending at `t-1`. I.e. the regime going
     *into* the breakout bar was quiet.
  2. Breakout: `close[t]` closes beyond the `breakout_lookback`-bar
     Donchian channel built from bars strictly before `t`.
  3. Direction = the breakout direction. No trend filter.

Stop: `atr_stop_multiple` × ATR-14, with an optional ATR trailing stop.
The strategy emits stop_price only; the RiskEngine sizes the position.

Predeclared parameters and rationale: docs/research/CAMPAIGN_004_PRECOMMIT.md.
"""

from __future__ import annotations

import hashlib
from datetime import UTC
from decimal import Decimal
from typing import Any

import pandas as pd

from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import atr, donchian_high, donchian_low


class VolatilityBreakoutStrategy:
    name: str = "volatility_breakout"

    def __init__(self, version: str = "0.1.0-c004") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        # compression_lookback (default 60) + ATR warmup + buffer. The
        # per-call `needed` check below is the real correctness guard.
        return 120

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        atr_len = int(cfg.get("atr_lookback", 14))
        breakout_len = int(cfg.get("breakout_lookback", 20))
        compression_len = int(cfg.get("compression_lookback", 60))
        compression_pct = float(cfg.get("compression_percentile", 40.0))
        atr_multiple = float(cfg.get("atr_stop_multiple", 2.0))
        timeframe = cfg.get("timeframe", "H4")
        min_atr_pips_by_pair = cfg.get("min_atr_pips", {}) or {}
        min_atr_pips = float(min_atr_pips_by_pair.get(ctx.instrument.name, 0.0))

        needed = max(atr_len + compression_len, breakout_len) + 3
        if len(df) < needed:
            return None

        close = df["close"]
        high = df["high"]
        low = df["low"]

        atr_series = atr(high, low, close, atr_len)
        d_high = donchian_high(high, breakout_len)  # prior bars only
        d_low = donchian_low(low, breakout_len)

        last_close = float(close.iloc[-1])
        last_dh = float(d_high.iloc[-1])
        last_dl = float(d_low.iloc[-1])
        last_atr = float(atr_series.iloc[-1])
        prior_atr = float(atr_series.iloc[-2])  # ATR at bar t-1

        if any(_isnan(v) for v in (last_dh, last_dl, last_atr, prior_atr)):
            return None

        # Block new entries if a position is already open in this instrument.
        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        pip_size = float(ctx.instrument.pip_size)
        atr_pips = last_atr / pip_size if pip_size else 0.0
        if atr_pips < min_atr_pips:
            return None

        # ---- Step 1: compression as of bar t-1 (prior bars only) ----
        # The window is the `compression_len` ATR values ending at t-1.
        comp_window = atr_series.iloc[-(compression_len + 1):-1]
        if len(comp_window) < compression_len or comp_window.isna().any():
            return None
        threshold = float(comp_window.quantile(compression_pct / 100.0))
        if prior_atr > threshold:
            return None  # regime going into bar t was NOT compressed

        # ---- Step 2 + 3: breakout out of the compressed regime ----
        side: str | None = None
        reason = ""
        if last_close > last_dh:
            side = "long"
            reason = (
                f"expansion long: close>{last_dh:.5f} (Donchian-{breakout_len}) "
                f"out of ATR compression (prior ATR {prior_atr:.6f} <= p"
                f"{compression_pct:.0f} {threshold:.6f})"
            )
        elif last_close < last_dl:
            side = "short"
            reason = (
                f"expansion short: close<{last_dl:.5f} (Donchian-{breakout_len}) "
                f"out of ATR compression (prior ATR {prior_atr:.6f} <= p"
                f"{compression_pct:.0f} {threshold:.6f})"
            )
        else:
            return None

        if side == "long":
            stop = last_close - atr_multiple * last_atr
        else:
            stop = last_close + atr_multiple * last_atr

        last_idx = df.index[-1]
        signal_id = _stable_signal_id(
            self.name, self.version, ctx.instrument.name, timeframe, last_idx, side
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
            exit_model="atr_trailing_or_time",
            features={
                "atr": last_atr,
                "atr_pips": atr_pips,
                "prior_atr": prior_atr,
                "compression_threshold": threshold,
                "donchian_high": last_dh,
                "donchian_low": last_dl,
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

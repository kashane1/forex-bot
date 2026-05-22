"""Range mean-reversion strategy — `mean_reversion 0.1.0-c008`.

CAMPAIGN_008, RESEARCH ONLY. Mean reversion has fat-tailed loss risk
(a range that breaks into a trend is catastrophic for a reversion
trade). This strategy therefore:

  * only acts in a *low-trend* regime (ADX-14 below a threshold),
  * always carries a hard ATR stop,
  * never averages down, never grids, never adds to a loser (it emits a
    single Signal; the RiskEngine enforces one position per instrument),

and it **cannot be promoted beyond REVISE without human review** —
`paper_only = True`, and the marathon caps its report at REVISE.

Entry logic (completed bars only, prior bars only, no lookahead) at the
latest completed bar `t`:

  1. Range regime: ADX-`adx_lookback` < `adx_max` (no strong trend).
  2. Over-extension: the z-score of close over `zscore_lookback` bars is
     beyond `zscore_long_threshold` / `zscore_short_threshold`, with an
     RSI confirmation.
  3. Direction is *counter* to the extension (buy the dip, sell the
     rip) — reversion toward the mean.

Stop = `atr_stop_multiple` × ATR-14. Exit is the hard stop or the
`max_bars_in_trade` time stop (the engine has no midline-target exit;
the time stop is the reversion horizon).
"""

from __future__ import annotations

import hashlib
from datetime import UTC
from decimal import Decimal
from typing import Any

import pandas as pd

from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import adx, atr, rsi, zscore


class MeanReversionStrategy:
    name: str = "mean_reversion"
    paper_only: bool = True  # research-only — never auto-promoted to live

    def __init__(self, version: str = "0.1.0-c008") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        return 220  # regime_ema 200 + buffer

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        atr_len = int(cfg.get("atr_lookback", 14))
        z_len = int(cfg.get("zscore_lookback", 20))
        z_long = float(cfg.get("zscore_long_threshold", -2.0))
        z_short = float(cfg.get("zscore_short_threshold", 2.0))
        rsi_len = int(cfg.get("rsi_lookback", 14))
        regime_ema = int(cfg.get("regime_ema", 200))
        adx_len = int(cfg.get("adx_lookback", 14))
        adx_max = float(cfg.get("adx_max", 20.0))
        atr_multiple = float(cfg.get("atr_stop_multiple", 1.5))
        timeframe = cfg.get("timeframe", "H4")
        min_atr_pips_by_pair = cfg.get("min_atr_pips", {}) or {}
        min_atr_pips = float(min_atr_pips_by_pair.get(ctx.instrument.name, 0.0))

        needed = max(regime_ema, z_len, atr_len, rsi_len, adx_len) + 3
        if len(df) < needed:
            return None

        close = df["close"]
        high = df["high"]
        low = df["low"]

        atr_series = atr(high, low, close, atr_len)
        z = zscore(close, z_len)
        r = rsi(close, rsi_len)
        adx_series = adx(high, low, close, adx_len)

        last_close = float(close.iloc[-1])
        last_atr = float(atr_series.iloc[-1])
        last_z = float(z.iloc[-1])
        last_rsi = float(r.iloc[-1])
        last_adx = float(adx_series.iloc[-1])

        if any(_isnan(v) for v in (last_atr, last_z, last_rsi, last_adx)):
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

        # Range regime gate — no strong trend.
        if last_adx >= adx_max:
            return None

        side: str | None = None
        reason = ""
        if last_z <= z_long and last_rsi < 35.0:
            side = "long"  # buy the oversold dip — revert up
            reason = (
                f"range mean-reversion long: ADX{adx_len}={last_adx:.1f}<{adx_max}, "
                f"z={last_z:.2f}<={z_long}, RSI={last_rsi:.1f}<35"
            )
        elif last_z >= z_short and last_rsi > 65.0:
            side = "short"  # sell the overbought rip — revert down
            reason = (
                f"range mean-reversion short: ADX{adx_len}={last_adx:.1f}<{adx_max}, "
                f"z={last_z:.2f}>={z_short}, RSI={last_rsi:.1f}>65"
            )
        else:
            return None

        # Hard stop — mandatory. Reversion against a breakout is the tail
        # risk; the stop is the only thing bounding it.
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
            exit_model="hard_stop_or_time",
            features={
                "atr": last_atr,
                "atr_pips": atr_pips,
                "zscore": last_z,
                "rsi": last_rsi,
                "adx": last_adx,
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

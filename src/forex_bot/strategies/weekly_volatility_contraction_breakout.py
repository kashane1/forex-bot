"""Weekly volatility contraction breakout — ``weekly_volatility_contraction_breakout 0.1.0-c017``.

CAMPAIGN_017 research candidate. CANDIDATE SCAFFOLD ONLY — not approved
for paper / demo / live trading.

After multi-week volatility contraction (weekly true range at or below
the 25th percentile of trailing 12 weeks), trade confirmed H4 breakouts
from the compressed week's high/low with an ATR buffer. Stop at the
opposite side of the compressed range.
"""

from __future__ import annotations

import hashlib
import math
from datetime import UTC
from decimal import Decimal

import pandas as pd

from forex_bot.domain.signals import Signal
from forex_bot.features.weekly_volatility import (
    aggregate_h4_to_weekly_ohlc,
    breakout_already_consumed,
    compute_h4_atr_buffer,
    label_weekly_compression,
    latest_completed_compressed_week,
)
from forex_bot.strategies.base import StrategyContext


class WeeklyVolatilityContractionBreakoutStrategy:
    name: str = "weekly_volatility_contraction_breakout"

    def __init__(self, version: str = "0.1.0-c017") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        # 12 compression weeks (~504 H4 bars) + ATR burn-in.
        return 520

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config

        compression_weeks = int(cfg.get("compression_lookback_weeks", 12))
        compression_pct = float(cfg.get("compression_percentile_threshold", 25))
        buffer_mult = float(cfg.get("breakout_buffer_atr_multiple", 0.25))
        atr_len = int(cfg.get("atr_lookback_h4", 14))
        spread_to_atr_max = float(cfg.get("spread_to_atr_max", 0.15))
        timeframe = cfg.get("timeframe", "H4")
        min_atr_pips_by_pair = cfg.get("min_atr_pips", {}) or {}
        min_atr_pips = float(min_atr_pips_by_pair.get(ctx.instrument.name, 0.0))

        if len(df) < self.warmup_bars_required():
            return None

        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        high = df["high"]
        low = df["low"]
        close = df["close"]
        open_ = df["open"]
        bar_ts = df.index[-1]

        last_atr, buffer = compute_h4_atr_buffer(
            high, low, close, atr_len, buffer_mult,
        )
        if last_atr is None or buffer is None:
            return None

        pip_size = float(ctx.instrument.pip_size)
        atr_pips = last_atr / pip_size if pip_size else 0.0
        if atr_pips < min_atr_pips:
            return None

        spread_pips = float(getattr(ctx, "spread_pips", 0.0) or 0.0)
        if spread_pips / last_atr > spread_to_atr_max:
            return None

        weekly = aggregate_h4_to_weekly_ohlc(
            df.index, open_, high, low, close,
        )
        weekly = label_weekly_compression(
            weekly,
            compression_lookback_weeks=compression_weeks,
            compression_percentile_threshold=compression_pct,
        )
        cw = latest_completed_compressed_week(weekly, bar_ts)
        if cw is None:
            return None

        cw_high = float(cw["compressed_week_high"])
        cw_low = float(cw["compressed_week_low"])
        cw_start = pd.Timestamp(cw["compressed_week_start"])
        cw_end = pd.Timestamp(cw["compressed_week_end"])

        if bar_ts <= cw_end:
            return None

        if breakout_already_consumed(
            timestamps=df.index,
            closes=close,
            week_end=cw_end,
            current_index=bar_ts,
            compressed_high=cw_high,
            compressed_low=cw_low,
            buffer=buffer,
        ):
            return None

        last_close = float(close.iloc[-1])
        if not math.isfinite(last_close):
            return None

        long_trigger = cw_high + buffer
        short_trigger = cw_low - buffer
        side: str | None = None
        if last_close > long_trigger:
            side = "long"
        elif last_close < short_trigger:
            side = "short"
        else:
            return None

        if side == "long":
            stop = cw_low - buffer
            stop_distance = last_close - stop
        else:
            stop = cw_high + buffer
            stop_distance = stop - last_close

        if stop_distance <= 0 or not math.isfinite(stop_distance):
            return None

        signal_id = _stable_signal_id(
            self.name,
            self.version,
            ctx.instrument.name,
            timeframe,
            cw_start,
            side,
        )
        return Signal(
            signal_id=signal_id,
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe=timeframe,
            timestamp=pd.Timestamp(bar_ts).tz_convert(UTC).to_pydatetime(),
            side=side,  # type: ignore[arg-type]
            entry_intent="market",
            stop_model="compressed_range_opposite_side",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="hard_stop_or_time",
            features={
                "compressed_week_start": cw_start.isoformat(),
                "compressed_week_end": cw_end.isoformat(),
                "compressed_week_high": cw_high,
                "compressed_week_low": cw_low,
                "compression_percentile": float(cw["compression_percentile"]),
                "weekly_true_range": float(cw["weekly_true_range"]),
                "atr_h4": last_atr,
                "breakout_buffer": buffer,
                "breakout_side": side,
                "stop_distance": stop_distance,
                "breakout_buffer_atr_multiple": buffer_mult,
            },
        )


def _stable_signal_id(
    strategy: str,
    version: str,
    instrument: str,
    timeframe: str,
    compressed_week_start: pd.Timestamp,
    side: str,
) -> str:
    payload = (
        f"{strategy}|{version}|{instrument}|{timeframe}|"
        f"{compressed_week_start.isoformat()}|{side}"
    )
    digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return f"{strategy}-{digest}"

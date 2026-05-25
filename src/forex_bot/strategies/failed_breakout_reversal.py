"""Failed-breakout reversal — `failed_breakout_reversal 0.1.0-c015`.

CAMPAIGN_015 research candidate. CANDIDATE SCAFFOLD ONLY — not approved
for paper / demo / live trading. `configs/approved_strategies.yaml`
remains `approved: []`; every prior campaign verdict is untouched.

Entry logic (all prior-bars-only, no lookahead) at the latest *completed*
H4 bar ``t`` taken from ``ctx.candles.completed_only().df``:

  1. The prior 20-bar range is taken over bars ``[t-20, t-1]``
     (i.e. strictly excluding ``t``). ``prior_high = max(high[t-N..t-1])``
     and ``prior_low = min(low[t-N..t-1])``.
  2. ATR(14) and ADX(14) are Wilder-smoothed series consuming completed
     candles only. Their values *at index ``-1``* (i.e. at bar ``t``) are
     used (ATR / ADX are defined using bar ``t``'s true range; they do
     not peek into ``t+1``).
  3. Reject if ``adx > adx_max`` (range is not "quiet enough").
  4. Reject if ``range_width / atr`` is outside
     ``[min_range_atr_multiple, max_range_atr_multiple]``.
  5. Short setup: ``high[t] > prior_high + sweep_buffer_atr * atr`` AND
     ``close[t] < prior_high`` → ``side = short``;
     stop = ``high[t] + stop_buffer_atr * atr`` (beyond sweep extreme).
  6. Long setup: ``low[t] < prior_low - sweep_buffer_atr * atr`` AND
     ``close[t] > prior_low`` → ``side = long``;
     stop = ``low[t] - stop_buffer_atr * atr``.
  7. If both setups would trigger on the same bar (pathological gap),
     emit no signal — defense in depth.
  8. Stop-distance gate: ``stop_distance_atr = |close[t] - stop| / atr``
     must lie in ``[min_stop_atr_multiple, max_stop_atr_multiple]``.

Fill timing: primary campaign evidence path is ``next_bar_open`` —
the bespoke engine fills at the open of the bar following the signal
bar. The strategy module reports ``close[t]`` in features as a stable
diagnostic entry reference; the engine's realized fill is what enters
the trade book.

Exit: hard stop OR ``max_bars_in_trade`` time stop. No midline target,
no take-profit, no trailing. Adverse stop wins on same-bar ambiguity
(``same_bar_adverse_stop_wins = True``).

The strategy module imports nothing from ``forex_bot.broker``; this is
verified by ``tests/unit/test_failed_breakout_reversal.py``.
"""

from __future__ import annotations

import hashlib
import math
from datetime import UTC
from decimal import Decimal
from typing import Any

import pandas as pd

from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import adx, atr


class FailedBreakoutReversalStrategy:
    name: str = "failed_breakout_reversal"

    def __init__(self, version: str = "0.1.0-c015") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        # ATR / ADX (14) need ~ 14 + 1 bars to stabilize, prior-range window
        # is 20 bars, plus a small buffer for indicator burn-in.
        return 64

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        range_lookback = int(cfg.get("range_lookback", 20))
        atr_len = int(cfg.get("atr_lookback", 14))
        adx_len = int(cfg.get("adx_lookback", 14))
        adx_max = float(cfg.get("adx_max", 20.0))
        sweep_buffer_atr = float(cfg.get("sweep_buffer_atr", 0.10))
        min_range_atr = float(cfg.get("min_range_atr_multiple", 1.25))
        max_range_atr = float(cfg.get("max_range_atr_multiple", 5.00))
        stop_buffer_atr = float(cfg.get("stop_buffer_atr", 0.10))
        min_stop_atr = float(cfg.get("min_stop_atr_multiple", 0.80))
        max_stop_atr = float(cfg.get("max_stop_atr_multiple", 2.20))
        timeframe = cfg.get("timeframe", "H4")
        min_atr_pips_by_pair = cfg.get("min_atr_pips", {}) or {}
        min_atr_pips = float(min_atr_pips_by_pair.get(ctx.instrument.name, 0.0))

        # R1: warm-up — need range_lookback + ATR/ADX burn-in + 1 current bar.
        needed = max(range_lookback, atr_len, adx_len) + 2
        if len(df) < needed:
            return None

        # R2: block re-entry while a position is open in the instrument.
        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        high = df["high"]
        low = df["low"]
        close = df["close"]

        atr_series = atr(high, low, close, atr_len)
        adx_series = adx(high, low, close, adx_len)
        last_atr = float(atr_series.iloc[-1])
        last_adx = float(adx_series.iloc[-1])

        # R3: ATR / ADX must be finite + positive.
        if not (math.isfinite(last_atr) and last_atr > 0):
            return None
        if not math.isfinite(last_adx):
            return None

        # R4: ADX-quiet gate.
        if last_adx > adx_max:
            return None

        # R5: prior-N-bar range, strictly excluding bar t.
        prior_window_high = high.iloc[-(range_lookback + 1):-1]
        prior_window_low = low.iloc[-(range_lookback + 1):-1]
        if len(prior_window_high) < range_lookback:
            return None
        prior_high = float(prior_window_high.max())
        prior_low = float(prior_window_low.min())
        if not (math.isfinite(prior_high) and math.isfinite(prior_low)):
            return None
        range_width = prior_high - prior_low
        if range_width <= 0:
            return None

        # R6: range/ATR gates.
        range_width_atr = range_width / last_atr
        if range_width_atr < min_range_atr:
            return None
        if range_width_atr > max_range_atr:
            return None

        # R7: optional per-pair ATR-pip floor (default 0 → never trips).
        pip_size = float(ctx.instrument.pip_size)
        atr_pips = last_atr / pip_size if pip_size else 0.0
        if atr_pips < min_atr_pips:
            return None

        # R8: signal-bar geometry.
        last_high = float(high.iloc[-1])
        last_low = float(low.iloc[-1])
        last_close = float(close.iloc[-1])
        if not all(
            math.isfinite(v) for v in (last_high, last_low, last_close)
        ):
            return None

        sweep_buffer = sweep_buffer_atr * last_atr
        stop_buffer = stop_buffer_atr * last_atr

        short_swept = last_high > prior_high + sweep_buffer
        short_rejected = last_close < prior_high
        long_swept = last_low < prior_low - sweep_buffer
        long_rejected = last_close > prior_low

        short_setup = short_swept and short_rejected
        long_setup = long_swept and long_rejected

        # R9: dual-trigger ambiguity — defense in depth, no signal.
        if short_setup and long_setup:
            return None
        if not (short_setup or long_setup):
            return None

        side: str
        stop: float
        sweep_distance_atr: float
        if short_setup:
            side = "short"
            stop = last_high + stop_buffer
            sweep_distance_atr = (last_high - prior_high) / last_atr
        else:
            side = "long"
            stop = last_low - stop_buffer
            sweep_distance_atr = (prior_low - last_low) / last_atr

        # R10: stop-distance gate (uses close[t] as diagnostic entry ref).
        stop_distance = abs(last_close - stop)
        stop_distance_atr = stop_distance / last_atr
        if stop_distance_atr < min_stop_atr:
            return None
        if stop_distance_atr > max_stop_atr:
            return None

        last_idx = df.index[-1]
        signal_id = _stable_signal_id(
            self.name, self.version, ctx.instrument.name, timeframe, last_idx, side
        )
        reason = (
            f"failed-breakout reversal {side}: "
            f"range[{range_lookback}]=[{prior_low:.5f},{prior_high:.5f}] "
            f"width_atr={range_width_atr:.2f} "
            f"sweep_atr={sweep_distance_atr:.2f} "
            f"stop_atr={stop_distance_atr:.2f} adx={last_adx:.1f}"
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
            stop_model=(
                f"sweep_extreme+{stop_buffer_atr}*ATR{atr_len} "
                f"(range{range_lookback}, adx_max={adx_max})"
            ),
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="hard_stop_or_time_stop",
            features={
                "prior_high": prior_high,
                "prior_low": prior_low,
                "range_width": range_width,
                "range_width_atr": range_width_atr,
                "atr": last_atr,
                "adx": last_adx,
                "sweep_distance_atr": sweep_distance_atr,
                "stop_distance_atr": stop_distance_atr,
                "last_close": last_close,
                "last_high": last_high,
                "last_low": last_low,
                "atr_pips": atr_pips,
            },
            reason=reason,
        )


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]

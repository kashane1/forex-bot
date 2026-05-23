"""Asian-range / London-open session breakout — `session_breakout 0.1.0-c010`.

CAMPAIGN_010 research candidate. CANDIDATE SCAFFOLD ONLY — not approved for
paper / demo / live trading. `configs/approved_strategies.yaml` remains
`approved: []`; CAMPAIGN_002 remains REJECT.

Entry logic (all prior-bars-only, no lookahead) at the latest *completed*
bar ``t`` taken from ``ctx.candles.completed_only().df``:

  1. ``t`` is inside the London window (UTC hour in
     ``[london_session_hours_utc_start, london_session_hours_utc_end)``).
  2. ``t-1`` is inside the Asian window (UTC hour in the
     ``[asian_session_hours_utc_start, asian_session_hours_utc_end)``
     interval — which wraps midnight when ``start > end``).
  3. The Asian-bar range ``high[t-1] - low[t-1]`` is at least
     ``min_asian_range_atr_fraction * atr_14[t-1]``.
  4. Direction is the breakout direction:
       * ``close[t] > high[t-1]`` → long;
       * ``close[t] < low[t-1]`` → short;
       * equal → no signal.

Stop: ``atr_stop_multiple * atr_14[t-1]`` on the opposite side of ``close[t]``.
The strategy emits ``stop_price`` only; the ``RiskEngine`` sizes the position.

Implementation notes (binding — see
``docs/research/ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md``):

* At bar ``t``, **only** ``close[t]`` is read; bar ``t``'s ``high`` /
  ``low`` / ``open`` / ``volume`` are deliberately not consulted by the
  entry rule (no same-bar lookahead).
* ATR is computed once over the full series; the value at index ``-2``
  (i.e. as of bar ``t-1``) is used.
* The strategy module imports nothing from ``forex_bot.broker`` (verified
  by a grep test in ``tests/unit/test_session_breakout.py``).
* DST limitation: the candidate uses fixed UTC session windows. Under
  NY-DST H4 alignment, the eligible "London open" bar starts at
  09:00 UTC with the Asian bar at 05:00 UTC; under NY-standard it
  starts at 06:00 UTC with the Asian bar at 02:00 UTC. Bars outside
  these alignments simply emit no signal — failure mode is silent
  fail-closed, not a wrong signal.
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
from forex_bot.strategies.indicators import atr


def in_asian_window(hour: int, start: int, end: int) -> bool:
    """Half-open ``[start, end)``; wraps midnight when ``start > end``."""
    if start == end:
        return False
    if start > end:
        return hour >= start or hour < end
    return start <= hour < end


def in_london_window(hour: int, start: int, end: int) -> bool:
    """Half-open ``[start, end)``; never wraps in v1 (validated in config)."""
    return start <= hour < end


class SessionBreakoutStrategy:
    name: str = "session_breakout"

    def __init__(self, version: str = "0.1.0-c010") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        # ATR(14) needs >=15 bars; +1 for accessing index -2; small buffer.
        return 32

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        atr_len = int(cfg.get("atr_lookback", 14))
        atr_multiple = float(cfg.get("atr_stop_multiple", 2.0))
        min_range_fraction = float(cfg.get("min_asian_range_atr_fraction", 0.30))
        timeframe = cfg.get("timeframe", "H4")
        asian_start = int(cfg.get("asian_session_hours_utc_start", 22))
        asian_end = int(cfg.get("asian_session_hours_utc_end", 6))
        london_start = int(cfg.get("london_session_hours_utc_start", 6))
        london_end = int(cfg.get("london_session_hours_utc_end", 12))
        min_atr_pips_by_pair = cfg.get("min_atr_pips", {}) or {}
        min_atr_pips = float(min_atr_pips_by_pair.get(ctx.instrument.name, 0.0))

        # R1: sufficient warm-up.
        if len(df) < atr_len + 2:
            return None

        # R2: block re-entry if a position already exists.
        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        # Session windows derived from UTC bar-open timestamps.
        idx_t = df.index[-1]
        idx_prev = df.index[-2]
        t_hour = pd.Timestamp(idx_t).tz_convert(UTC).hour
        prev_hour = pd.Timestamp(idx_prev).tz_convert(UTC).hour

        # R3 / R4: session gating.
        if not in_london_window(t_hour, london_start, london_end):
            return None
        if not in_asian_window(prev_hour, asian_start, asian_end):
            return None

        # Bar `t` reads close only. Bar `t-1` reads high / low / ATR.
        last_close = float(df["close"].iloc[-1])
        prior_high = float(df["high"].iloc[-2])
        prior_low = float(df["low"].iloc[-2])

        atr_series = atr(df["high"], df["low"], df["close"], atr_len)
        prior_atr = float(atr_series.iloc[-2])

        # R5: fail closed on NaN / non-finite inputs.
        if not all(math.isfinite(v) for v in (last_close, prior_high, prior_low, prior_atr)):
            return None

        prior_range = prior_high - prior_low

        # R6: Asian range gate.
        if prior_atr <= 0:
            return None
        if prior_range < min_range_fraction * prior_atr:
            return None

        # R8: optional min_atr_pips floor (default 0 → never trips).
        pip_size = float(ctx.instrument.pip_size)
        atr_pips = prior_atr / pip_size if pip_size else 0.0
        if atr_pips < min_atr_pips:
            return None

        # R7: direction from breakout.
        side: str | None = None
        reason = ""
        if last_close > prior_high:
            side = "long"
            reason = (
                f"London breakout long: close={last_close:.5f} > prior Asian "
                f"high={prior_high:.5f} (range {prior_range:.5f} >= "
                f"{min_range_fraction:.2f}*ATR{atr_len}={prior_atr:.5f})"
            )
        elif last_close < prior_low:
            side = "short"
            reason = (
                f"London breakout short: close={last_close:.5f} < prior Asian "
                f"low={prior_low:.5f} (range {prior_range:.5f} >= "
                f"{min_range_fraction:.2f}*ATR{atr_len}={prior_atr:.5f})"
            )
        else:
            return None

        # R9: stop on the opposite side of `close[t]`.
        if side == "long":
            stop = last_close - atr_multiple * prior_atr
        else:
            stop = last_close + atr_multiple * prior_atr
        if stop == last_close:
            # Defense in depth — should be unreachable given prior_atr > 0.
            return None

        signal_id = _stable_signal_id(
            self.name, self.version, ctx.instrument.name, timeframe, idx_t, side
        )
        return Signal(
            signal_id=signal_id,
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe=timeframe,
            timestamp=pd.Timestamp(idx_t).tz_convert(UTC).to_pydatetime(),
            side=side,  # type: ignore[arg-type]
            entry_intent="market",
            stop_model=f"ATR{atr_len}*{atr_multiple}",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="time_stop_only",
            features={
                "prior_high": prior_high,
                "prior_low": prior_low,
                "prior_range": prior_range,
                "prior_atr": prior_atr,
                "last_close": last_close,
                "range_fraction": prior_range / prior_atr,
                "prior_hour_utc": prev_hour,
                "current_hour_utc": t_hour,
                "atr_pips": atr_pips,
            },
            reason=reason,
        )


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]

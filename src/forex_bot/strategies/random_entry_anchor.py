"""Random-entry diagnostic anchor — ``random_entry_anchor 0.1.0-c011``.

CAMPAIGN_011 research candidate (the C5 diagnostic / null-model anchor).
**NULL MODEL BY DESIGN — cannot be approved, cannot be deployed, cannot
be used for paper / demo / live trading.** Its purpose is to validate
the research evidence pipeline and establish a deterministic random-entry
baseline that any future "real" candidate must beat by a meaningful
margin to count as evidence of an edge.

`configs/approved_strategies.yaml` remains `approved: []`; CAMPAIGN_002
remains REJECT; CAMPAIGN_010 remains REJECT.

Entry logic (R1-R8; binding — see
``docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md``)
at the latest *completed* bar ``t`` taken from
``ctx.candles.completed_only().df``:

  R1. ``len(df) >= atr_lookback + 2`` (warm-up).
  R2. No open position for ``ctx.instrument``.
  R3. Seed input is the deterministic string
      ``f"{master_seed}|{instrument_name}|{bar_timestamp_iso}"``;
      hashed with SHA-256; ``bar_random`` = high 64 bits;
      ``gate_random`` = next 64 bits. **The seed input contains NO
      bar-t price data and NO ATR.**
  R4. Entry-probability gate: ``gate_random / 2**64 < entry_probability_per_bar``.
  R5. Fail-closed on NaN / non-finite / zero ``prior_atr`` (ATR at
      index ``-2``).
  R6. Spread filter delegated to ``RiskEngine`` (not enforced here).
  R7. Direction = ``"long"`` if ``bar_random & 1 == 0`` else ``"short"``.
      ``stop = close[t] -/+ atr_stop_multiple * prior_atr``. ``close[t]``
      is read ONLY for stop placement; the entry decision is fully
      determined by R3 / R4 / direction before ``close[t]`` is consulted.
  R8. Emit ``Signal`` with deterministic ``signal_id`` and
      ``exit_model="time_stop_only"``.

Implementation notes (binding):

* No use of ``random.random``, ``numpy.random``, or Python's built-in
  ``hash()`` — only SHA-256 over deterministic UTF-8 strings.
* No import from ``forex_bot.broker`` / ``forex_bot.execution`` /
  ``forex_bot.loops`` (structural unit tests grep for these).
* No reference to CAMPAIGN_002 / ``trend_following`` / ``Donchian`` /
  ``EMA`` parameters (verified by source-grep).
* No reference to CAMPAIGN_010 / ``session_breakout`` / ``Asian`` /
  ``London`` parameters (verified by source-grep).
* Strategy module never mutates the strategy config dict.
* ``RandomEntryAnchorStrategy`` exposes no approval-shaped field /
  method.
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


def _derive_random_pair(
    master_seed: int,
    instrument_name: str,
    bar_timestamp_iso: str,
) -> tuple[int, int]:
    """Deterministic SHA-256-based random pair.

    Returns ``(bar_random, gate_random)`` where each is a 64-bit
    unsigned integer drawn from disjoint halves of the SHA-256 digest
    of ``f"{master_seed}|{instrument_name}|{bar_timestamp_iso}"``.

    **Binding invariant (no-lookahead rail):** the seed input
    contains only the three arguments above. It MUST NOT include
    bar price data (close, high, low, open, volume) or any ATR
    value or any other derived feature. The structural unit test
    in ``tests/unit/test_random_entry_anchor.py`` enforces this
    by introspecting the function's signature and source.
    """
    seed_input = f"{master_seed}|{instrument_name}|{bar_timestamp_iso}"
    digest = hashlib.sha256(seed_input.encode("utf-8")).digest()
    bar_random = int.from_bytes(digest[:8], "big")
    gate_random = int.from_bytes(digest[8:16], "big")
    return bar_random, gate_random


class RandomEntryAnchorStrategy:
    """Null-model diagnostic anchor — CANNOT be approved by design."""

    name: str = "random_entry_anchor"

    def __init__(self, version: str = "0.1.0-c011") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        # ATR(14) needs >=15 bars; +1 for accessing index -2; small buffer.
        return 32

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        master_seed = int(cfg.get("master_seed", 20260523))
        entry_probability_per_bar = float(
            cfg.get("entry_probability_per_bar", 0.05)
        )
        atr_len = int(cfg.get("atr_lookback", 14))
        atr_multiple = float(cfg.get("atr_stop_multiple", 2.0))
        timeframe = cfg.get("timeframe", "H4")

        # R1: sufficient warm-up.
        if len(df) < atr_len + 2:
            return None

        # R2: block re-entry if a position already exists.
        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        # R3: deterministic seed input + score derivation.
        idx_t = df.index[-1]
        bar_timestamp_iso = pd.Timestamp(idx_t).tz_convert(UTC).isoformat()
        bar_random, gate_random = _derive_random_pair(
            master_seed, ctx.instrument.name, bar_timestamp_iso
        )

        # R4: entry-probability gate.
        gate_value = gate_random / float(2**64)
        if gate_value >= entry_probability_per_bar:
            return None

        # R5: fail-closed on NaN / non-finite / zero prior_atr.
        atr_series = atr(df["high"], df["low"], df["close"], atr_len)
        prior_atr = float(atr_series.iloc[-2])
        if not math.isfinite(prior_atr) or prior_atr <= 0:
            return None

        # R7: direction selection + ATR-stop placement.
        side: str = "long" if (bar_random & 1) == 0 else "short"

        # close[t] is read ONLY for stop placement; the entry decision
        # (direction + gate) was fully determined by R3 / R4 above
        # without consulting bar-t price data.
        last_close = float(df["close"].iloc[-1])

        if side == "long":
            stop = last_close - atr_multiple * prior_atr
        else:
            stop = last_close + atr_multiple * prior_atr
        if stop == last_close:
            # Defense in depth — unreachable given prior_atr > 0 in R5.
            return None

        # R8: emit deterministic Signal.
        signal_id = _stable_signal_id(
            self.name,
            self.version,
            ctx.instrument.name,
            timeframe,
            bar_timestamp_iso,
            side,
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
                "bar_random": int(bar_random),
                "gate_random": int(gate_random),
                "gate_value": float(gate_value),
                "prior_atr": float(prior_atr),
                "last_close": float(last_close),
                "entry_probability_per_bar": float(entry_probability_per_bar),
                "master_seed": int(master_seed),
            },
            reason=(
                f"Random null-model entry: side={side} "
                f"(bar_random={bar_random}, gate_value={gate_value:.6f} "
                f"< entry_probability={entry_probability_per_bar:.4f}). "
                f"CAMPAIGN_011 diagnostic anchor — not a trading recommendation."
            ),
        )


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]

"""Fill model: long entry = ask, long exit = bid, short mirror, with
configurable slippage applied in the unfavourable direction.

`FillModel` is *price* — how a fill price is derived from a bid/ask
quote. `FillTiming` is *time* — which bar's quote the entry fills
against. See docs/research/FILL_TIMING_MODEL.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

# When a backtest entry fills, relative to the bar the signal is computed on:
#   * signal_bar_close — fill at the close of the completed signal bar N.
#     Optimistic: the signal is only *known* once bar N has closed, so
#     filling at that same close assumes a zero-latency fill at a price
#     that, in live trading, has already passed.
#   * next_bar_open — fill at the open of bar N+1. The honest timing for a
#     bar-close signal; no future data is used (bar N+1's open is the
#     first tradeable price after the signal is known).
FillTiming = Literal["signal_bar_close", "next_bar_open"]
FILL_TIMINGS: frozenset[str] = frozenset({"signal_bar_close", "next_bar_open"})

# Recorded as a rejected/skipped signal when next_bar_open is selected but
# the signal fired on the final bar, so there is no bar N+1 to fill at.
NEXT_BAR_OPEN_UNAVAILABLE = "NEXT_BAR_OPEN_UNAVAILABLE"

# Whether the backtest engine adjusts stop / TP exit fills for a bar that
# OPENED past the level (a weekend gap, news jump, or session-open jump).
#   * none — current default: stops/TPs always fill at exactly the level;
#     a gap-through bar is filled at `stop_price` / `tp_price` regardless
#     of the bar's open. Preserves byte-identical config_hash for every
#     CAMPAIGN_001–009 artifact.
#   * gap_through — opt-in: when bid_open is already past the level (long
#     stop: bid_open < stop_price; long tp: bid_open > tp_price; mirror
#     for short), fill at the bar's open instead of at the level. The
#     stop-side change is ADVERSE (worse than stop); the tp-side change
#     is FAVORABLE (better than tp). Mirrors how real stop-market and
#     limit orders fill when price has already moved through the level.
# See docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md.
GapFillPolicy = Literal["none", "gap_through"]
GAP_FILL_POLICIES: frozenset[str] = frozenset({"none", "gap_through"})


@dataclass(frozen=True)
class FillModel:
    fixed_slippage_pips: Decimal
    spread_slippage_multiplier: Decimal

    def entry_price(
        self,
        *,
        side: str,
        bid: Decimal,
        ask: Decimal,
        pip_size: Decimal,
    ) -> Decimal:
        spread_pips = (ask - bid) / pip_size
        slip_pips = max(
            self.fixed_slippage_pips,
            spread_pips * self.spread_slippage_multiplier,
        )
        slip = slip_pips * pip_size
        if side == "long":
            return ask + slip
        return bid - slip

    def exit_price(
        self,
        *,
        side: str,
        bid: Decimal,
        ask: Decimal,
        pip_size: Decimal,
    ) -> Decimal:
        spread_pips = (ask - bid) / pip_size
        slip_pips = max(
            self.fixed_slippage_pips,
            spread_pips * self.spread_slippage_multiplier,
        )
        slip = slip_pips * pip_size
        if side == "long":
            return bid - slip
        return ask + slip

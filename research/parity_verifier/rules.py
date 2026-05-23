"""Independent rule evaluation for CAMPAIGN_002 H4 trend_following 0.1.0.

These functions implement the strategy logic described in
``docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md`` §4–§6 from the
spec text, not by importing ``src/forex_bot/strategies/trend_following.py``.

Conventions (pinned by the spec):

- Long if ``EMA_fast > EMA_slow`` *and* ``close > donchian_high``.
- Short if ``EMA_fast < EMA_slow`` *and* ``close < donchian_low``.
- ``min_atr_pips`` is ``{}`` (empty) for CAMPAIGN_002 — the floor is
  disabled and never blocks an entry. The arg is accepted in case a
  future verifier re-runs with the gate enabled.
- Initial stop: long ``close - atr × atr_stop_multiple``;
  short ``close + atr × atr_stop_multiple``.
- Trailing-stop ratchet: long uses the current bar's ``bid_close``,
  short uses ``ask_close`` (the spec §5 wording).
- Exit precedence on each bar after entry: trailing-stop update, then
  adverse-stop, then time-stop, then end-of-data. Take-profit and
  opposite-signal exits do not exist for ``trend_following``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from research.parity_verifier.models import Side, TradeExitReason


def round_price(price: float, display_precision: int) -> float:
    """Round ``price`` to the instrument's display precision.

    Matches ``forex_bot.domain.instruments.Instrument.round_price``:
    converts the float to a ``Decimal`` via ``str`` (preserving the
    float's shortest unambiguous string representation), then
    ``quantize``s with ``ROUND_HALF_UP`` at
    ``10 ** (-display_precision)``. The result is cast back to float
    so the verifier remains float-based outside this rounding step.

    For EUR_USD (``display_precision=5``):
        ``round_price(1.1403658, 5) == 1.14037``  (6th decimal is 5 → up)
        ``round_price(1.140012,  5) == 1.14001``  (6th decimal is 2 → down)

    For USD_JPY (``display_precision=3``):
        ``round_price(150.0046, 3) == 150.005``
        ``round_price(150.0044, 3) == 150.004``

    See ``docs/research/FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md``
    §6 (mismatch M1) for the divergence this closes.
    """

    if display_precision <= 0:
        raise ValueError("display_precision must be > 0")
    quant = Decimal(1).scaleb(-display_precision)
    rounded = Decimal(str(price)).quantize(quant, rounding="ROUND_HALF_UP")
    return float(rounded)


@dataclass(frozen=True)
class EntryDecision:
    """Result of evaluating an entry on one completed bar."""

    side: Side
    is_entry: bool


def evaluate_entry(
    *,
    ema_fast: float,
    ema_slow: float,
    close: float,
    donchian_high_val: float,
    donchian_low_val: float,
    atr_value: float,
    atr_floor_pips: float | None,
    pip_size: float,
    in_position: bool,
) -> EntryDecision:
    """Apply the CAMPAIGN_002 entry rules to one bar of state.

    Any non-finite indicator value (NaN from warmup) returns no entry.
    ``in_position`` short-circuits — no new entry while one is open.
    """

    if in_position:
        return EntryDecision(side=Side.FLAT, is_entry=False)
    for value in (ema_fast, ema_slow, close, donchian_high_val, donchian_low_val, atr_value):
        if value != value:  # NaN check without importing math
            return EntryDecision(side=Side.FLAT, is_entry=False)
    if atr_floor_pips is not None and (atr_value / pip_size) < atr_floor_pips:
        return EntryDecision(side=Side.FLAT, is_entry=False)
    if ema_fast > ema_slow and close > donchian_high_val:
        return EntryDecision(side=Side.LONG, is_entry=True)
    if ema_fast < ema_slow and close < donchian_low_val:
        return EntryDecision(side=Side.SHORT, is_entry=True)
    return EntryDecision(side=Side.FLAT, is_entry=False)


def initial_stop_price(
    *,
    side: Side,
    close_price: float,
    atr_value: float,
    atr_stop_multiple: float,
) -> float:
    """Initial hard stop placement from the strategy spec §5.

    Per ``src/forex_bot/strategies/trend_following.py`` (the strategy
    that emits ``signal.stop_price``), the stop is anchored at the
    **bar's mid close**, *not* at the post-slippage entry price:

        long:  stop = close - atr_multiple * atr
        short: stop = close + atr_multiple * atr

    The bespoke engine then carries that ``signal.stop_price`` through
    sizing and into the open trade without re-deriving it from the
    fill. Using the post-slippage entry price here would offset the
    stop by ``slip`` pips, which manifests as a systematic divergence
    in stop-hit timing and per-trade R magnitude. See
    ``docs/research/FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md``
    Bug #1 for the trace.
    """

    distance = atr_value * atr_stop_multiple
    if side is Side.LONG:
        return close_price - distance
    if side is Side.SHORT:
        return close_price + distance
    raise ValueError(f"initial_stop_price: invalid side {side!r}")


def ratchet_trailing_stop(
    *,
    side: Side,
    current_stop: float,
    bid_close: float,
    ask_close: float,
    atr_value: float,
    trailing_stop_atr_multiple: float,
) -> tuple[float, bool]:
    """Compute the new trailing stop and whether it ratcheted.

    Long: ``new = bid_close - atr × trailing_multiple``; raise only.
    Short: ``new = ask_close + atr × trailing_multiple``; lower only.
    Returns ``(new_stop, has_moved)`` — ``has_moved`` is True iff the
    stop actually changed in this call.
    """

    distance = atr_value * trailing_stop_atr_multiple
    if side is Side.LONG:
        candidate = bid_close - distance
        if candidate > current_stop:
            return candidate, True
        return current_stop, False
    if side is Side.SHORT:
        candidate = ask_close + distance
        if candidate < current_stop:
            return candidate, True
        return current_stop, False
    raise ValueError(f"ratchet_trailing_stop: invalid side {side!r}")


@dataclass(frozen=True)
class ExitDecision:
    """Result of evaluating exits on one bar after entry."""

    exit_now: bool
    exit_price: float = 0.0
    exit_reason: TradeExitReason = TradeExitReason.UNKNOWN


def evaluate_exit(
    *,
    side: Side,
    bid_high: float,
    bid_low: float,
    bid_close: float,
    ask_high: float,
    ask_low: float,
    ask_close: float,
    stop_price: float,
    has_trailed: bool,
    bars_held: int,
    max_bars_in_trade: int,
    is_last_bar: bool,
) -> ExitDecision:
    """Apply the §5 exit ladder: adverse-stop → time-stop → end-of-data.

    The trailing-stop update is done *before* this call; the
    ``has_trailed`` flag controls the stop-reason label (stop vs
    trailing_stop)."""

    if side is Side.LONG:
        if bid_low <= stop_price:
            return ExitDecision(
                exit_now=True,
                exit_price=stop_price,
                exit_reason=TradeExitReason.TRAILING_STOP if has_trailed else TradeExitReason.STOP,
            )
    elif side is Side.SHORT:
        if ask_high >= stop_price:
            return ExitDecision(
                exit_now=True,
                exit_price=stop_price,
                exit_reason=TradeExitReason.TRAILING_STOP if has_trailed else TradeExitReason.STOP,
            )
    else:
        raise ValueError(f"evaluate_exit: invalid side {side!r}")
    if bars_held >= max_bars_in_trade:
        exit_price = bid_close if side is Side.LONG else ask_close
        return ExitDecision(
            exit_now=True, exit_price=exit_price, exit_reason=TradeExitReason.TIME
        )
    if is_last_bar:
        exit_price = bid_close if side is Side.LONG else ask_close
        return ExitDecision(
            exit_now=True, exit_price=exit_price, exit_reason=TradeExitReason.EOD
        )
    return ExitDecision(exit_now=False)


def fill_entry_price(
    *,
    side: Side,
    bid_close: float,
    ask_close: float,
    spread_slippage_multiplier: float,
    fixed_slippage_pips: float,
    pip_size: float,
) -> float:
    """Bid/ask-aware fill at the signal bar's own close (mapping spec §7).

    spread_pips = (ask - bid) / pip_size
    slip_pips   = max(fixed_slippage_pips, spread_pips * multiplier)
    long entry  = ask_close + slip_pips × pip_size
    short entry = bid_close - slip_pips × pip_size
    """

    spread_pips = (ask_close - bid_close) / pip_size
    slip_pips = max(fixed_slippage_pips, spread_pips * spread_slippage_multiplier)
    slip = slip_pips * pip_size
    if side is Side.LONG:
        return ask_close + slip
    if side is Side.SHORT:
        return bid_close - slip
    raise ValueError(f"fill_entry_price: invalid side {side!r}")


def size_position(
    *,
    nav: float,
    risk_per_trade_pct: float,
    entry_price: float,
    stop_price: float,
    pip_size: float,
    quote_currency: str,
    base_currency: str,
    mid_price: float,
) -> int:
    """0.25%-of-equity sizing (mapping spec §6).

    Returns whole units (floored to integer); zero if stop_distance is
    non-positive."""

    risk_amount = nav * risk_per_trade_pct / 100.0
    stop_distance_pips = abs(entry_price - stop_price) / pip_size
    if stop_distance_pips <= 0:
        return 0
    if quote_currency == "USD":
        pip_value_home = pip_size
    elif base_currency == "USD":
        pip_value_home = pip_size / mid_price
    else:
        raise ValueError(
            f"size_position only supports USD-quote or USD-base pairs; "
            f"got base={base_currency} quote={quote_currency}"
        )
    raw = risk_amount / (stop_distance_pips * pip_value_home)
    return int(raw)  # floor toward zero, units precision 0


def trade_pnl(
    *,
    side: Side,
    entry_price: float,
    exit_price: float,
    units: int,
    quote_currency: str,
    base_currency: str,
) -> float:
    """Realised PnL in account currency (mapping spec §6)."""

    diff = (exit_price - entry_price) if side is Side.LONG else (entry_price - exit_price)
    gross_quote = diff * units
    if quote_currency == "USD":
        return gross_quote
    if base_currency == "USD":
        return gross_quote / exit_price
    raise ValueError(
        f"trade_pnl only supports USD-quote or USD-base pairs; got base={base_currency} quote={quote_currency}"
    )

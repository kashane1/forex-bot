"""Minimal independent event loop.

One pair, one position at a time. The loop is bar-by-bar over completed
H4 candles: indicators → entry decision → fill → loop body checks
trailing/exit on subsequent bars. No look-ahead, no broker side-effects,
no bespoke-engine imports.

The loop is intentionally written from the mapping spec, not from the
bespoke engine — see ``rules.py`` and ``indicators.py`` for the
re-derived primitives.
"""

from __future__ import annotations

from research.parity_verifier.indicators import atr, donchian_high, donchian_low, ema
from research.parity_verifier.instruments import InstrumentSpec
from research.parity_verifier.models import (
    CandleSeries,
    PairResult,
    Side,
    StopState,
    Trade,
    VerifierConfig,
)
from research.parity_verifier.rules import (
    evaluate_entry,
    evaluate_exit,
    fill_entry_price,
    initial_stop_price,
    ratchet_trailing_stop,
    size_position,
    trade_pnl,
)


def run_pair(
    *,
    candles: CandleSeries,
    instrument: InstrumentSpec,
    config: VerifierConfig,
    starting_equity_usd: float | None = None,
) -> tuple[PairResult, list[Trade]]:
    """Run the verifier on one pair's candle series.

    Returns the per-pair summary and the list of closed trades. NAV
    compounds bar-by-bar at trade close, exactly as the bespoke engine
    does in the no-RiskEngine path (mapping spec §6).
    """

    bars = candles.bars
    n = len(bars)
    if n == 0:
        return (
            PairResult(
                instrument=instrument.name,
                candle_count=0,
                trades=0,
                expectancy_r=None,
                return_pct=None,
                profit_factor=None,
                win_rate=None,
            ),
            [],
        )

    highs = [b.high for b in bars]
    lows = [b.low for b in bars]
    closes = [b.close for b in bars]
    ema_fast = ema(closes, config.ema_fast)
    ema_slow = ema(closes, config.ema_slow)
    atr_series = atr(highs, lows, closes, config.atr_lookback)
    dch = donchian_high(highs, config.donchian_lookback)
    dcl = donchian_low(lows, config.donchian_lookback)

    nav = starting_equity_usd if starting_equity_usd is not None else config.starting_equity_usd
    starting_nav = nav
    trades: list[Trade] = []

    in_position = False
    side = Side.FLAT
    entry_time = bars[0].time
    entry_price = 0.0
    stop_state = StopState(initial_stop_price=0.0, stop_price=0.0, has_trailed=False)
    bars_held = 0
    units = 0
    initial_stop_distance = 0.0
    floor_pips = config.min_atr_pips.get(instrument.name)

    for i, bar in enumerate(bars):
        is_last_bar = i == n - 1
        if not in_position:
            decision = evaluate_entry(
                ema_fast=ema_fast[i],
                ema_slow=ema_slow[i],
                close=bar.close,
                donchian_high_val=dch[i],
                donchian_low_val=dcl[i],
                atr_value=atr_series[i],
                atr_floor_pips=floor_pips,
                pip_size=instrument.pip_size,
                in_position=False,
            )
            if not decision.is_entry:
                continue
            side = decision.side
            entry_time = bar.time
            entry_price = fill_entry_price(
                side=side,
                bid_close=bar.bid_close,
                ask_close=bar.ask_close,
                spread_slippage_multiplier=config.spread_slippage_multiplier,
                fixed_slippage_pips=config.fixed_slippage_pips,
                pip_size=instrument.pip_size,
            )
            stop_price = initial_stop_price(
                side=side,
                entry_price=entry_price,
                atr_value=atr_series[i],
                atr_stop_multiple=config.atr_stop_multiple,
            )
            stop_state = StopState(
                initial_stop_price=stop_price, stop_price=stop_price, has_trailed=False
            )
            initial_stop_distance = abs(entry_price - stop_price)
            units = size_position(
                nav=nav,
                risk_per_trade_pct=config.risk_per_trade_pct,
                entry_price=entry_price,
                stop_price=stop_price,
                pip_size=instrument.pip_size,
                quote_currency=instrument.quote_currency,
                base_currency=instrument.base_currency,
                mid_price=bar.close,
            )
            in_position = True
            bars_held = 0
            continue

        bars_held += 1
        new_stop, moved = ratchet_trailing_stop(
            side=side,
            current_stop=stop_state.stop_price,
            bid_close=bar.bid_close,
            ask_close=bar.ask_close,
            atr_value=atr_series[i],
            trailing_stop_atr_multiple=config.trailing_stop_atr_multiple,
        )
        if moved:
            stop_state = StopState(
                initial_stop_price=stop_state.initial_stop_price,
                stop_price=new_stop,
                has_trailed=True,
            )
        exit_decision = evaluate_exit(
            side=side,
            bid_high=bar.bid_high,
            bid_low=bar.bid_low,
            bid_close=bar.bid_close,
            ask_high=bar.ask_high,
            ask_low=bar.ask_low,
            ask_close=bar.ask_close,
            stop_price=stop_state.stop_price,
            has_trailed=stop_state.has_trailed,
            bars_held=bars_held,
            max_bars_in_trade=config.max_bars_in_trade,
            is_last_bar=is_last_bar,
        )
        if not exit_decision.exit_now:
            continue
        pnl = trade_pnl(
            side=side,
            entry_price=entry_price,
            exit_price=exit_decision.exit_price,
            units=units,
            quote_currency=instrument.quote_currency,
            base_currency=instrument.base_currency,
        )
        if initial_stop_distance > 0 and units > 0:
            risk_home = initial_stop_distance * units
            if instrument.base_currency == "USD":
                risk_home = risk_home / exit_decision.exit_price
            r_mult = pnl / risk_home if risk_home > 0 else 0.0
        else:
            r_mult = 0.0
        return_pct = (pnl / nav) * 100.0 if nav > 0 else 0.0
        trades.append(
            Trade(
                instrument=instrument.name,
                side=side,
                entry_time=entry_time,
                entry_price=entry_price,
                exit_time=bar.time,
                exit_price=exit_decision.exit_price,
                exit_reason=exit_decision.exit_reason,
                units=units,
                initial_stop_price=stop_state.initial_stop_price,
                final_stop_price=stop_state.stop_price,
                bars_held=bars_held,
                r_multiple=r_mult,
                return_pct=return_pct,
            )
        )
        nav += pnl
        in_position = False
        side = Side.FLAT
        bars_held = 0
        units = 0

    return _summarize(instrument.name, n, trades, starting_nav, nav), trades


def _summarize(
    instrument: str,
    candle_count: int,
    trades: list[Trade],
    starting_nav: float,
    ending_nav: float,
) -> PairResult:
    if not trades:
        return PairResult(
            instrument=instrument,
            candle_count=candle_count,
            trades=0,
            expectancy_r=None,
            return_pct=None,
            profit_factor=None,
            win_rate=None,
        )
    rs = [t.r_multiple for t in trades]
    expectancy_r = sum(rs) / len(rs)
    return_pct = (ending_nav / starting_nav - 1.0) * 100.0 if starting_nav > 0 else 0.0
    wins = [r for r in rs if r > 0]
    win_rate = len(wins) / len(rs) if rs else 0.0
    sum_gain = sum(r for r in rs if r > 0)
    sum_loss = -sum(r for r in rs if r < 0)
    profit_factor: float | None
    if sum_loss > 0:
        profit_factor = sum_gain / sum_loss
    elif sum_gain > 0:
        profit_factor = float("inf")
    else:
        profit_factor = None
    return PairResult(
        instrument=instrument,
        candle_count=candle_count,
        trades=len(trades),
        expectancy_r=round(expectancy_r, 4),
        return_pct=round(return_pct, 4),
        profit_factor=round(profit_factor, 4) if profit_factor not in (None, float("inf")) else profit_factor,
        win_rate=round(win_rate, 4),
    )

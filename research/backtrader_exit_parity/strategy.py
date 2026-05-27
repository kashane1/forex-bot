"""Backtrader mean-reversion exit-parity strategy (C008/C009/C018).

Uses ``MeanReversionStrategy`` / ``MeanReversionProtectiveStopStrategy`` for
entries (shared strategy module — not the bespoke engine loop) and
``exit_logic.process_bar_exit`` for independent exit handling.

Fill timing: ``signal_bar_close`` (matches deduped forensic replay).
Gap-fill policy: ``none``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

import backtrader as bt
import pandas as pd

from forex_bot.backtesting.fills import FillModel
from forex_bot.domain.candles import CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.risk.policy import RiskEngine, RiskInputs
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.mean_reversion import MeanReversionStrategy
from forex_bot.strategies.mean_reversion_protective_stop import (
    MeanReversionProtectiveStopStrategy,
)
from research.backtrader_exit_parity.data_feed import DedupedBidAskFeed, prepare_candle_window
from research.backtrader_exit_parity.exit_logic import OpenTrade, process_bar_exit


@dataclass
class ParityTrade:
    instrument: str
    side: str
    units: int
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    exit_reason: str
    bars_held: int
    r_multiple: float
    protective_stop_armed: bool = False
    protective_stop_exit: bool = False


@dataclass
class PairParityResult:
    instrument: str
    trades: list[ParityTrade] = field(default_factory=list)
    candle_count: int = 0


def _synthetic_account_snapshot(ts: pd.Timestamp, equity: float):
    from forex_bot.domain.account import AccountSnapshot

    return AccountSnapshot(
        account_id="backtest",
        currency="USD",
        balance=Decimal(str(equity)),
        nav=Decimal(str(equity)),
        margin_used=Decimal("0"),
        margin_available=Decimal(str(equity)),
        open_trade_count=0,
        open_position_count=0,
        pending_order_count=0,
        unrealized_pl=Decimal("0"),
        pl=Decimal("0"),
        time=ts.to_pydatetime(),
    )


def _pnl(trade: OpenTrade, exit_price: Decimal, instrument: Instrument) -> Decimal:
    if trade.side == "long":
        return (exit_price - trade.entry_price) * trade.units
    return (trade.entry_price - exit_price) * trade.units


def run_mean_reversion_exit_parity(
    df: pd.DataFrame,
    *,
    instrument: Instrument,
    strategy_cfg: dict[str, Any],
    settings: Any,
    campaign: str,
    midline_exit: bool,
    protective_stop_after_r: float | None,
    fill_model: FillModel,
    risk_engine: RiskEngine | None,
    max_bars_in_trade: int,
    starting_equity: float,
) -> PairParityResult:
    """Drive one instrument through Backtrader with exit-parity logic."""
    trades_out: list[ParityTrade] = []

    if campaign == "C018":
        strategy = MeanReversionProtectiveStopStrategy(
            version=strategy_cfg.get("version", "0.1.0-c018")
        )
    else:
        strategy = MeanReversionStrategy(version=strategy_cfg.get("version", "0.1.0-c008"))

    cfg = dict(strategy_cfg)
    cfg["midline_exit"] = midline_exit

    class _Strategy(bt.Strategy):
        def __init__(self) -> None:
            self._equity = starting_equity
            self._open: OpenTrade | None = None
            self._realized: list[tuple[datetime, Decimal]] = []
            self._equity_bars: list[tuple[datetime, float]] = []
            self._bar_idx = -1
            self._full_df = df.copy()
            self._warmup = max(strategy.warmup_bars_required(), 5)

        def next(self) -> None:
            self._bar_idx += 1
            i = self._bar_idx
            if i < self._warmup:
                return

            row = self._full_df.iloc[i]
            ts = self._full_df.index[i]
            window = prepare_candle_window(self._full_df.iloc[: i + 1])

            if self._open is not None:
                exit_res = process_bar_exit(
                    self._open,
                    row,
                    ts,
                    max_bars_in_trade=max_bars_in_trade,
                    protective_stop_after_r=protective_stop_after_r,
                    pip_size=instrument.pip_size,
                    gap_fill_policy="none",
                    trailing_stop_atr_multiple=cfg.get("trailing_stop_atr_multiple"),
                    atr_value=None,
                )
                if exit_res is not None:
                    pnl = _pnl(self._open, exit_res.exit_price, instrument)
                    self._equity += float(pnl)
                    self._realized.append((ts.to_pydatetime(), pnl))
                    risk_dist = (
                        (self._open.entry_price - self._open.initial_stop_price).copy_abs()
                        * self._open.units
                    )
                    r = float(pnl / risk_dist) if risk_dist > 0 else 0.0
                    trades_out.append(
                        ParityTrade(
                            instrument=instrument.name,
                            side=self._open.side,
                            units=self._open.units,
                            entry_time=self._open.entry_time.to_pydatetime(),
                            exit_time=ts.to_pydatetime(),
                            entry_price=float(self._open.entry_price),
                            exit_price=float(exit_res.exit_price),
                            exit_reason=exit_res.exit_reason,
                            bars_held=self._open.bars_held,
                            r_multiple=r,
                            protective_stop_armed=self._open.protective_armed,
                            protective_stop_exit=exit_res.exit_reason == "protective_stop",
                        )
                    )
                    self._open = None

            self._equity_bars.append((ts.to_pydatetime(), self._equity))
            if self._open is not None:
                return

            window_frame = CandleFrame(
                instrument=instrument.name,
                granularity="H4",
                df=window,
            )
            mid_close = Decimal(str(row["close"]))
            bid_close = (
                Decimal(str(row["bid_close"]))
                if pd.notna(row.get("bid_close"))
                else mid_close
            )
            ask_close = (
                Decimal(str(row["ask_close"]))
                if pd.notna(row.get("ask_close"))
                else mid_close
            )
            quote = Quote(
                instrument=instrument.name,
                time=ts.to_pydatetime(),
                bid=bid_close,
                ask=ask_close,
            )
            spread_pips = (ask_close - bid_close) / instrument.pip_size
            market_state = MarketState(
                quote=quote,
                spread_snapshot=SpreadSnapshot(
                    instrument=instrument.name,
                    time=quote.time,
                    bid=bid_close,
                    ask=ask_close,
                    spread_pips=spread_pips,
                ),
            )
            ctx = StrategyContext(
                instrument=instrument,
                candles=window_frame,
                market_state=market_state,
                open_positions=[Position(instrument=instrument.name)],
                config=cfg,
            )
            signal = strategy.generate_signal(ctx)
            if signal is None:
                return

            entry = fill_model.entry_price(
                side=signal.side,
                bid=bid_close,
                ask=ask_close,
                pip_size=instrument.pip_size,
            )
            quotes_for_sizing = {instrument.name: quote}
            units = 0
            stop_price_to_use = signal.stop_price

            if risk_engine is not None:
                realized_today = Decimal("0")
                realized_week = Decimal("0")
                for t, p in self._realized:
                    if t.date() == ts.date():
                        realized_today += p
                week_start = ts.to_pydatetime().date()
                for t, p in self._realized:
                    if (week_start - t.date()).days < 7:
                        realized_week += p
                peak = max((e for _, e in self._equity_bars), default=starting_equity)
                dd_pct = (peak - self._equity) / peak * 100 if peak > 0 else 0.0
                atr_pips_val = signal.features.get("atr_pips")
                inputs = RiskInputs(
                    signal=signal,
                    instrument=instrument,
                    account=_synthetic_account_snapshot(ts, self._equity),
                    market_state=market_state,
                    positions=[],
                    quotes_by_instrument=quotes_for_sizing,
                    realized_pl_today=realized_today,
                    realized_pl_week=realized_week,
                    drawdown_pct=Decimal(str(dd_pct)),
                    atr_pips=(
                        Decimal(str(atr_pips_val)) if atr_pips_val is not None else None
                    ),
                    reconciled=True,
                )
                decision, plan = risk_engine.evaluate(inputs)
                if not decision.approved or plan is None:
                    return
                units = plan.units
                stop_price_to_use = plan.stop_loss_price
            else:
                from forex_bot.risk.sizing import size_position

                sizing = size_position(
                    instrument=instrument,
                    account_currency=settings.market.account_currency,
                    nav_home=Decimal(str(self._equity)),
                    risk_per_trade_pct=Decimal(str(settings.risk.risk_per_trade_pct)),
                    entry_price=entry,
                    stop_price=signal.stop_price,
                    quotes_by_instrument=quotes_for_sizing,
                )
                if sizing is None or sizing.units <= 0:
                    return
                units = sizing.units
                stop_price_to_use = signal.stop_price

            tp_price = signal.take_profit_price
            if tp_price is not None and (
                (signal.side == "long" and tp_price <= entry)
                or (signal.side == "short" and tp_price >= entry)
            ):
                tp_price = None

            self._open = OpenTrade(
                side=signal.side,
                units=units,
                entry_price=entry,
                entry_time=ts,
                stop_price=stop_price_to_use,
                initial_stop_price=stop_price_to_use,
                spread_pips_at_entry=spread_pips,
                take_profit_price=tp_price,
            )

        def stop(self) -> None:
            if self._open is None:
                return
            last_row = self._full_df.iloc[-1]
            ts = self._full_df.index[-1]
            bid_close = (
                Decimal(str(last_row["bid_close"]))
                if pd.notna(last_row.get("bid_close"))
                else Decimal(str(last_row["close"]))
            )
            ask_close = (
                Decimal(str(last_row["ask_close"]))
                if pd.notna(last_row.get("ask_close"))
                else Decimal(str(last_row["close"]))
            )
            exit_price = bid_close if self._open.side == "long" else ask_close
            pnl = _pnl(self._open, exit_price, instrument)
            risk_dist = (
                (self._open.entry_price - self._open.initial_stop_price).copy_abs()
                * self._open.units
            )
            r = float(pnl / risk_dist) if risk_dist > 0 else 0.0
            trades_out.append(
                ParityTrade(
                    instrument=instrument.name,
                    side=self._open.side,
                    units=self._open.units,
                    entry_time=self._open.entry_time.to_pydatetime(),
                    exit_time=ts.to_pydatetime(),
                    entry_price=float(self._open.entry_price),
                    exit_price=float(exit_price),
                    exit_reason="eod",
                    bars_held=self._open.bars_held,
                    r_multiple=r,
                    protective_stop_armed=self._open.protective_armed,
                    protective_stop_exit=False,
                )
            )

    cerebro = bt.Cerebro(stdstats=False)
    feed_df = df.copy()
    feed = DedupedBidAskFeed(dataname=feed_df)
    cerebro.adddata(feed)
    cerebro.addstrategy(_Strategy)
    cerebro.run()
    return PairParityResult(instrument=instrument.name, trades=trades_out, candle_count=len(df))

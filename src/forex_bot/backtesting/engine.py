"""Backtest engine. Single-instrument, single-position-at-a-time. Replays
the strategy bar-by-bar over completed candles, using bid/ask-aware fills
and the same Decimal sizing as live."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

import pandas as pd

from forex_bot.backtesting.fills import FillModel
from forex_bot.backtesting.metrics import (
    BacktestMetrics,
    TradeRecord,
    _EquityBar,
    compute_metrics,
)
from forex_bot.domain.candles import CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.risk.sizing import size_position
from forex_bot.strategies.base import Strategy, StrategyContext
from forex_bot.strategies.indicators import atr


@dataclass
class BacktestResult:
    metrics: BacktestMetrics
    trades: list[TradeRecord] = field(default_factory=list)
    equity_curve: list[_EquityBar] = field(default_factory=list)
    config_hash: str = ""
    data_request_hash: str = ""
    instrument: str = ""
    strategy_name: str = ""
    strategy_version: str = ""
    granularity: str = ""
    from_time: str | None = None
    to_time: str | None = None
    fill_model_repr: str = ""
    notes: str = ""


@dataclass
class _OpenTrade:
    side: str
    units: Decimal
    entry_price: Decimal
    entry_time: pd.Timestamp
    stop_price: Decimal
    initial_stop_price: Decimal
    spread_pips_at_entry: Decimal
    bars_held: int = 0


class BacktestEngine:
    def __init__(
        self,
        *,
        instrument: Instrument,
        strategy: Strategy,
        strategy_config: dict[str, Any],
        fill_model: FillModel,
        starting_equity: Decimal,
        account_currency: str = "USD",
        risk_per_trade_pct: Decimal = Decimal("0.25"),
        max_bars_in_trade: int = 80,
        commission_per_unit: Decimal = Decimal("0"),
        trailing_stop_atr_multiple: float | None = None,
        atr_lookback: int = 14,
    ) -> None:
        self.instrument = instrument
        self.strategy = strategy
        self.strategy_config = strategy_config
        self.fill_model = fill_model
        self.starting_equity = starting_equity
        self.account_currency = account_currency
        self.risk_per_trade_pct = risk_per_trade_pct
        self.max_bars_in_trade = max_bars_in_trade
        self.commission_per_unit = commission_per_unit
        self.trailing_stop_atr_multiple = trailing_stop_atr_multiple
        self.atr_lookback = atr_lookback

    def run(
        self,
        candle_frame: CandleFrame,
        *,
        data_request_hash: str = "",
    ) -> BacktestResult:
        df = candle_frame.completed_only().df
        meta = dict(
            instrument=self.instrument.name,
            strategy_name=getattr(self.strategy, "name", ""),
            strategy_version=getattr(self.strategy, "version", ""),
            granularity=candle_frame.granularity,
            from_time=df.index[0].isoformat() if not df.empty else None,
            to_time=df.index[-1].isoformat() if not df.empty else None,
            fill_model_repr=repr(self.fill_model),
            data_request_hash=data_request_hash,
            config_hash=_hash({
                "strategy_config": self.strategy_config,
                "risk_pct": str(self.risk_per_trade_pct),
                "max_bars": self.max_bars_in_trade,
                "commission": str(self.commission_per_unit),
                "trail_atr": self.trailing_stop_atr_multiple,
                "atr_lookback": self.atr_lookback,
                "fill_model": repr(self.fill_model),
            }),
        )

        if df.empty:
            return BacktestResult(
                metrics=compute_metrics([], [], float(self.starting_equity)),
                **meta,
            )

        warmup = max(self.strategy.warmup_bars_required(), 5)
        trades: list[TradeRecord] = []
        equity_bars: list[_EquityBar] = []
        equity = float(self.starting_equity)
        open_trade: _OpenTrade | None = None

        atr_series = (
            atr(df["high"], df["low"], df["close"], self.atr_lookback)
            if self.trailing_stop_atr_multiple is not None
            else None
        )

        for i in range(warmup, len(df)):
            window = df.iloc[: i + 1]
            row = df.iloc[i]
            ts = window.index[-1]

            # ---- mark-to-market / exit checks for open trade ----
            if open_trade is not None:
                open_trade.bars_held += 1
                bid_low = (
                    Decimal(str(row["bid_low"]))
                    if row["bid_low"] is not None
                    else Decimal(str(row["low"]))
                )
                ask_high = (
                    Decimal(str(row["ask_high"]))
                    if row["ask_high"] is not None
                    else Decimal(str(row["high"]))
                )
                bid_close = (
                    Decimal(str(row["bid_close"]))
                    if row["bid_close"] is not None
                    else Decimal(str(row["close"]))
                )
                ask_close = (
                    Decimal(str(row["ask_close"]))
                    if row["ask_close"] is not None
                    else Decimal(str(row["close"]))
                )

                # Trail the stop ONLY in the favourable direction.
                if (
                    self.trailing_stop_atr_multiple is not None
                    and atr_series is not None
                    and pd.notna(atr_series.iloc[i])
                ):
                    cur_atr = Decimal(str(atr_series.iloc[i]))
                    if open_trade.side == "long":
                        new_stop = bid_close - cur_atr * Decimal(str(self.trailing_stop_atr_multiple))
                        if new_stop > open_trade.stop_price:
                            open_trade.stop_price = new_stop
                    else:
                        new_stop = ask_close + cur_atr * Decimal(str(self.trailing_stop_atr_multiple))
                        if new_stop < open_trade.stop_price:
                            open_trade.stop_price = new_stop

                exit_reason: str | None = None
                exit_price: Decimal | None = None

                if open_trade.side == "long":
                    if bid_low <= open_trade.stop_price:
                        exit_reason = (
                            "trailing_stop"
                            if open_trade.stop_price != open_trade.initial_stop_price
                            else "stop"
                        )
                        exit_price = open_trade.stop_price
                    elif open_trade.bars_held >= self.max_bars_in_trade:
                        exit_reason = "time"
                        exit_price = bid_close
                else:
                    if ask_high >= open_trade.stop_price:
                        exit_reason = (
                            "trailing_stop"
                            if open_trade.stop_price != open_trade.initial_stop_price
                            else "stop"
                        )
                        exit_price = open_trade.stop_price
                    elif open_trade.bars_held >= self.max_bars_in_trade:
                        exit_reason = "time"
                        exit_price = ask_close

                if exit_reason and exit_price is not None:
                    pnl = self._pnl(open_trade, exit_price)
                    equity += float(pnl)
                    risk_distance = (
                        (open_trade.entry_price - open_trade.initial_stop_price).copy_abs()
                        * open_trade.units
                    )
                    r = pnl / risk_distance if risk_distance > 0 else Decimal("0")
                    trades.append(
                        TradeRecord(
                            instrument=self.instrument.name,
                            side=open_trade.side,
                            units=open_trade.units,
                            entry_time=open_trade.entry_time.to_pydatetime(),
                            exit_time=ts.to_pydatetime(),
                            entry_price=open_trade.entry_price,
                            exit_price=exit_price,
                            stop_price=open_trade.initial_stop_price,
                            pnl=pnl,
                            r_multiple=r,
                            bars_held=open_trade.bars_held,
                            spread_paid_pips=open_trade.spread_pips_at_entry,
                            exit_reason=exit_reason,
                        )
                    )
                    open_trade = None

            equity_bars.append(_EquityBar(ts.to_pydatetime(), equity))

            # ---- consider a new entry ----
            if open_trade is not None:
                continue

            window_frame = CandleFrame(
                instrument=self.instrument.name,
                granularity=candle_frame.granularity,
                df=window,
            )
            mid_close = Decimal(str(row["close"]))
            bid_close = (
                Decimal(str(row["bid_close"])) if row["bid_close"] is not None else mid_close
            )
            ask_close = (
                Decimal(str(row["ask_close"])) if row["ask_close"] is not None else mid_close
            )
            quote = Quote(
                instrument=self.instrument.name,
                time=ts.to_pydatetime(),
                bid=bid_close,
                ask=ask_close,
            )
            spread_pips = (ask_close - bid_close) / self.instrument.pip_size
            market_state = MarketState(
                quote=quote,
                spread_snapshot=SpreadSnapshot(
                    instrument=self.instrument.name,
                    time=quote.time,
                    bid=bid_close,
                    ask=ask_close,
                    spread_pips=spread_pips,
                ),
            )
            ctx = StrategyContext(
                instrument=self.instrument,
                candles=window_frame,
                market_state=market_state,
                open_positions=[Position(instrument=self.instrument.name)],
                config=self.strategy_config,
            )
            signal = self.strategy.generate_signal(ctx)
            if signal is None:
                continue
            entry = self.fill_model.entry_price(
                side=signal.side,
                bid=bid_close,
                ask=ask_close,
                pip_size=self.instrument.pip_size,
            )
            quotes_for_sizing = {self.instrument.name: quote}
            sizing = size_position(
                instrument=self.instrument,
                account_currency=self.account_currency,
                nav_home=Decimal(str(equity)),
                risk_per_trade_pct=self.risk_per_trade_pct,
                entry_price=entry,
                stop_price=signal.stop_price,
                quotes_by_instrument=quotes_for_sizing,
            )
            if sizing is None or sizing.units <= 0:
                continue
            open_trade = _OpenTrade(
                side=signal.side,
                units=sizing.units,
                entry_price=entry,
                entry_time=ts,
                stop_price=signal.stop_price,
                initial_stop_price=signal.stop_price,
                spread_pips_at_entry=spread_pips,
            )
            equity -= float(self.commission_per_unit * sizing.units)

        # Close any open trade at the last close for accounting honesty.
        if open_trade is not None:
            last_row = df.iloc[-1]
            bid_close = (
                Decimal(str(last_row["bid_close"]))
                if last_row["bid_close"] is not None
                else Decimal(str(last_row["close"]))
            )
            ask_close = (
                Decimal(str(last_row["ask_close"]))
                if last_row["ask_close"] is not None
                else Decimal(str(last_row["close"]))
            )
            exit_price = bid_close if open_trade.side == "long" else ask_close
            pnl = self._pnl(open_trade, exit_price)
            equity += float(pnl)
            risk_distance = (
                (open_trade.entry_price - open_trade.initial_stop_price).copy_abs()
                * open_trade.units
            )
            r = pnl / risk_distance if risk_distance > 0 else Decimal("0")
            trades.append(
                TradeRecord(
                    instrument=self.instrument.name,
                    side=open_trade.side,
                    units=open_trade.units,
                    entry_time=open_trade.entry_time.to_pydatetime(),
                    exit_time=df.index[-1].to_pydatetime(),
                    entry_price=open_trade.entry_price,
                    exit_price=exit_price,
                    stop_price=open_trade.initial_stop_price,
                    pnl=pnl,
                    r_multiple=r,
                    bars_held=open_trade.bars_held,
                    spread_paid_pips=open_trade.spread_pips_at_entry,
                    exit_reason="eod",
                )
            )
            equity_bars.append(_EquityBar(df.index[-1].to_pydatetime(), equity))

        metrics = compute_metrics(trades, equity_bars, float(self.starting_equity))
        return BacktestResult(
            metrics=metrics,
            trades=trades,
            equity_curve=equity_bars,
            **meta,
        )

    def _pnl(self, trade: _OpenTrade, exit_price: Decimal) -> Decimal:
        diff_quote = (
            (exit_price - trade.entry_price)
            if trade.side == "long"
            else (trade.entry_price - exit_price)
        )
        gross_quote = diff_quote * trade.units

        home = self.account_currency.upper()
        if self.instrument.quote_currency == home:
            gross_home = gross_quote
        elif self.instrument.base_currency == home:
            # For USD_JPY with USD home, PnL accrues in JPY: convert with exit
            # mid price. e.g. 500 JPY / 142 ≈ $3.52. Without this conversion
            # the engine overstates JPY PnL by ~100×.
            gross_home = gross_quote / exit_price
        else:
            # Cross pair without a runtime cross-quote — leave as the
            # approximation, but mark it. Real backtests should not hit this
            # branch because the engine doesn't accept cross pairs from
            # configs without their conversion quote being available.
            gross_home = gross_quote

        return gross_home - self.commission_per_unit * trade.units


def _hash(payload: Any) -> str:
    return hashlib.sha1(repr(payload).encode("utf-8")).hexdigest()[:16]


def compute_data_request_hash(
    instrument: str,
    granularity: str,
    from_time: str | None,
    to_time: str | None,
    source: str,
    candle_count: int,
) -> str:
    payload = f"{instrument}|{granularity}|{from_time}|{to_time}|{source}|{candle_count}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]

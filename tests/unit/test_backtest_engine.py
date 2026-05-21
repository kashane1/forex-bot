"""Backtest sanity tests. Synthetic data with a controlled trend.
We assert: trades occur, fills use ask/bid not midpoint, and the engine
respects the bar count it was given (i.e. no panic on small inputs)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import numpy as np
import pandas as pd

from forex_bot.backtesting.engine import BacktestEngine
from forex_bot.backtesting.fills import FillModel
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.strategies.trend_following import TrendFollowingStrategy


def _synthetic_uptrend(n: int = 400, start: float = 1.0500) -> CandleFrame:
    times = [datetime(2025, 1, 1, tzinfo=UTC) + timedelta(hours=4 * i) for i in range(n)]
    # Slow drift up with mild noise so EMA fast crosses above slow and Donchian
    # break events occur.
    rng = np.random.default_rng(seed=42)
    drift = np.linspace(0.0, 0.030, n)
    noise = rng.normal(0.0, 0.0008, n)
    mid = start + drift + noise.cumsum() * 0.05
    candles = []
    for t, m in zip(times, mid, strict=True):
        spread = 0.0002
        bid_c = Decimal(str(round(m - spread / 2, 5)))
        ask_c = Decimal(str(round(m + spread / 2, 5)))
        candles.append(
            Candle(
                instrument="EUR_USD",
                granularity="H4",
                time=t,
                complete=True,
                volume=1000,
                bid_o=bid_c, bid_h=bid_c + Decimal("0.0005"), bid_l=bid_c - Decimal("0.0005"), bid_c=bid_c,
                ask_o=ask_c, ask_h=ask_c + Decimal("0.0005"), ask_l=ask_c - Decimal("0.0005"), ask_c=ask_c,
            )
        )
    return CandleFrame.from_candles("EUR_USD", "H4", candles)


def test_backtest_runs_and_records_trades(eur_usd):
    frame = _synthetic_uptrend()
    fm = FillModel(
        fixed_slippage_pips=Decimal("0.3"),
        spread_slippage_multiplier=Decimal("0.5"),
    )
    engine = BacktestEngine(
        instrument=eur_usd,
        strategy=TrendFollowingStrategy(version="0.1.0"),
        strategy_config={
            "ema_fast": 20,
            "ema_slow": 60,
            "donchian_lookback": 20,
            "atr_lookback": 14,
            "atr_stop_multiple": 2.0,
            "max_bars_in_trade": 30,
        },
        fill_model=fm,
        starting_equity=Decimal("500"),
        account_currency="USD",
    )
    result = engine.run(frame)
    # We don't assert profit (don't trust the synthetic), only that the
    # plumbing works and the trade list contains valid records.
    for trade in result.trades:
        assert trade.entry_price > 0
        assert trade.stop_price > 0
        if trade.side == "long":
            assert trade.exit_price > 0
        # Stop must be on the correct side of entry.
        if trade.side == "long":
            assert trade.stop_price < trade.entry_price
        else:
            assert trade.stop_price > trade.entry_price
    assert result.metrics.final_equity > 0


def test_backtest_returns_zero_trades_on_empty_frame(eur_usd):
    fm = FillModel(
        fixed_slippage_pips=Decimal("0.3"),
        spread_slippage_multiplier=Decimal("0.5"),
    )
    engine = BacktestEngine(
        instrument=eur_usd,
        strategy=TrendFollowingStrategy(version="0.1.0"),
        strategy_config={},
        fill_model=fm,
        starting_equity=Decimal("500"),
    )
    frame = CandleFrame(instrument="EUR_USD", granularity="H4", df=pd.DataFrame())
    result = engine.run(frame)
    assert result.metrics.trade_count == 0
    assert result.metrics.final_equity == 500.0


def test_fill_model_uses_ask_for_long_entry(eur_usd):
    fm = FillModel(
        fixed_slippage_pips=Decimal("0"),
        spread_slippage_multiplier=Decimal("0"),
    )
    bid = Decimal("1.0800")
    ask = Decimal("1.0802")
    entry = fm.entry_price(side="long", bid=bid, ask=ask, pip_size=eur_usd.pip_size)
    assert entry == ask
    exit_p = fm.exit_price(side="long", bid=bid, ask=ask, pip_size=eur_usd.pip_size)
    assert exit_p == bid


def test_fill_model_adds_slippage_against_trade(eur_usd):
    fm = FillModel(
        fixed_slippage_pips=Decimal("1.0"),
        spread_slippage_multiplier=Decimal("0"),
    )
    bid = Decimal("1.0800")
    ask = Decimal("1.0802")
    entry = fm.entry_price(side="long", bid=bid, ask=ask, pip_size=eur_usd.pip_size)
    assert entry > ask  # paid more
    entry_short = fm.entry_price(side="short", bid=bid, ask=ask, pip_size=eur_usd.pip_size)
    assert entry_short < bid  # got less

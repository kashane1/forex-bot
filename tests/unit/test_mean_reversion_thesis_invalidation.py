"""Unit tests for CAMPAIGN_019 thesis-invalidation engine behavior."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pandas as pd
from research.backtrader_exit_parity.exit_logic import OpenTrade, process_bar_exit

from forex_bot.backtesting.engine import BacktestEngine
from forex_bot.backtesting.fills import FillModel
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.mean_reversion_thesis_invalidation import c008_entry_params

_EUR = Instrument(
    name="EUR_USD",
    type="CURRENCY",
    display_precision=5,
    pip_location=-4,
    trade_units_precision=0,
    minimum_trade_size=Decimal("1"),
    maximum_position_size=Decimal("10000000"),
    margin_rate=Decimal("0.02"),
)


class _OneShotLongStrategy:
    name = "one_shot"
    version = "0.0.0"

    def __init__(self, entry: float, stop: float) -> None:
        self._entry = entry
        self._stop = stop
        self._fired = False

    def warmup_bars_required(self) -> int:
        return 2

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        if self._fired:
            return None
        self._fired = True
        ts = ctx.candles.completed_only().df.index[-1]
        return Signal(
            signal_id="test",
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe="H4",
            timestamp=ts.to_pydatetime(),
            side="long",
            stop_model="fixed",
            stop_price=Decimal(str(self._stop)),
            exit_model="test",
            reason="test",
        )


def _candle(t: datetime, o: float, h: float, low: float, c: float) -> Candle:
    half = 0.00005
    return Candle(
        instrument="EUR_USD",
        granularity="H4",
        time=t,
        complete=True,
        volume=1000,
        bid_o=Decimal(str(o - half)),
        bid_h=Decimal(str(h - half)),
        bid_l=Decimal(str(low - half)),
        bid_c=Decimal(str(c - half)),
        ask_o=Decimal(str(o + half)),
        ask_h=Decimal(str(h + half)),
        ask_l=Decimal(str(low + half)),
        ask_c=Decimal(str(c + half)),
    )


def _frame(rows: list[tuple[float, float, float, float]]) -> CandleFrame:
    start = datetime(2020, 1, 1, tzinfo=UTC)
    candles = [
        _candle(start + timedelta(hours=4 * i), *row) for i, row in enumerate(rows)
    ]
    return CandleFrame.from_candles("EUR_USD", "H4", candles)


def test_c019_entry_params_match_c008_config():
    from forex_bot.config import load_settings

    c008 = load_settings("configs/campaign_008_range_mean_reversion.yaml")
    c019 = load_settings("configs/campaign_019_mean_reversion_thesis_invalidation.yaml")
    c008_cfg = c008.strategy.mean_reversion.model_dump()
    c019_cfg = c019.strategy.mean_reversion_thesis_invalidation.model_dump()
    assert c008_entry_params(c019_cfg) == c008_entry_params(c008_cfg)
    ti = c019_cfg["thesis_invalidation"]
    assert ti["long_exit_zscore"] == -3.0
    assert ti["short_exit_zscore"] == 3.0
    assert c019_cfg["midline_exit"] is False
    assert c019_cfg["atr_stop_multiple"] == 1.5
    assert c019_cfg["max_bars_in_trade"] == 40


def test_process_bar_exit_thesis_invalidation_long_at_z_minus_3():
    trade = OpenTrade(
        side="long",
        units=1000,
        entry_price=Decimal("1.0800"),
        entry_time=pd.Timestamp("2020-01-01T00:00:00Z"),
        stop_price=Decimal("1.0700"),
        initial_stop_price=Decimal("1.0700"),
        spread_pips_at_entry=Decimal("1.0"),
    )
    row = pd.Series(
        {
            "open": 1.0750,
            "high": 1.0760,
            "low": 1.0740,
            "close": 1.0750,
            "bid_open": 1.07495,
            "bid_high": 1.07595,
            "bid_low": 1.07395,
            "bid_close": 1.07495,
            "ask_open": 1.07505,
            "ask_high": 1.07605,
            "ask_low": 1.07405,
            "ask_close": 1.07505,
        }
    )
    res = process_bar_exit(
        trade,
        row,
        pd.Timestamp("2020-01-02T00:00:00Z"),
        max_bars_in_trade=40,
        protective_stop_after_r=None,
        pip_size=Decimal("0.0001"),
        thesis_invalidation_long_z=-3.0,
        thesis_invalidation_short_z=3.0,
        bar_zscore=-3.1,
    )
    assert res is not None
    assert res.exit_reason == "thesis_invalidation"


def test_process_bar_exit_short_thesis_invalidation_at_z_plus_3():
    trade = OpenTrade(
        side="short",
        units=1000,
        entry_price=Decimal("1.1200"),
        entry_time=pd.Timestamp("2020-01-01T00:00:00Z"),
        stop_price=Decimal("1.1300"),
        initial_stop_price=Decimal("1.1300"),
        spread_pips_at_entry=Decimal("1.0"),
    )
    row = pd.Series(
        {
            "open": 1.1250,
            "high": 1.1260,
            "low": 1.1240,
            "close": 1.1250,
            "bid_open": 1.12495,
            "bid_high": 1.12595,
            "bid_low": 1.12395,
            "bid_close": 1.12495,
            "ask_open": 1.12505,
            "ask_high": 1.12605,
            "ask_low": 1.12405,
            "ask_close": 1.12505,
        }
    )
    res = process_bar_exit(
        trade,
        row,
        pd.Timestamp("2020-01-02T00:00:00Z"),
        max_bars_in_trade=40,
        protective_stop_after_r=None,
        pip_size=Decimal("0.0001"),
        thesis_invalidation_long_z=-3.0,
        thesis_invalidation_short_z=3.0,
        bar_zscore=3.2,
    )
    assert res is not None
    assert res.exit_reason == "thesis_invalidation"


def test_thesis_invalidation_priority_before_stop():
    trade = OpenTrade(
        side="long",
        units=1000,
        entry_price=Decimal("1.0800"),
        entry_time=pd.Timestamp("2020-01-01T00:00:00Z"),
        stop_price=Decimal("1.0700"),
        initial_stop_price=Decimal("1.0700"),
        spread_pips_at_entry=Decimal("1.0"),
    )
    row = pd.Series(
        {
            "open": 1.0690,
            "high": 1.0700,
            "low": 1.0680,
            "close": 1.0690,
            "bid_open": 1.06895,
            "bid_high": 1.06995,
            "bid_low": 1.06795,
            "bid_close": 1.06895,
            "ask_open": 1.06905,
            "ask_high": 1.07005,
            "ask_low": 1.06805,
            "ask_close": 1.06905,
        }
    )
    res = process_bar_exit(
        trade,
        row,
        pd.Timestamp("2020-01-02T00:00:00Z"),
        max_bars_in_trade=40,
        protective_stop_after_r=None,
        pip_size=Decimal("0.0001"),
        thesis_invalidation_long_z=-3.0,
        thesis_invalidation_short_z=3.0,
        bar_zscore=-3.5,
    )
    assert res is not None
    assert res.exit_reason == "thesis_invalidation"


def test_engine_thesis_invalidation_runs_without_error():
    rows = [(1.0800, 1.0810, 1.0790, 1.0800)] * 25
    rows += [(1.0700 - i * 0.002, 1.0710, 1.0690, 1.0700 - i * 0.002) for i in range(25)]
    frame = _frame(rows)
    engine = BacktestEngine(
        instrument=_EUR,
        strategy=_OneShotLongStrategy(entry=1.0800, stop=1.0500),
        strategy_config={},
        fill_model=FillModel(
            fixed_slippage_pips=Decimal("0"),
            spread_slippage_multiplier=Decimal("0"),
        ),
        starting_equity=Decimal("10000"),
        max_bars_in_trade=40,
        thesis_invalidation_enabled=True,
        thesis_invalidation_long_z=-3.0,
        thesis_invalidation_short_z=3.0,
        thesis_invalidation_zscore_lookback=20,
    )
    result = engine.run(frame)
    assert result.trades

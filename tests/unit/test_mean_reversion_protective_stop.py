"""Unit tests for CAMPAIGN_018 protective stop engine behavior."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from forex_bot.backtesting.engine import BacktestEngine
from forex_bot.backtesting.fills import FillModel
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.mean_reversion import MeanReversionStrategy
from forex_bot.strategies.mean_reversion_protective_stop import (
    MeanReversionProtectiveStopStrategy,
    c008_entry_params,
)

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


def test_c018_entry_params_match_c008_config():
    from forex_bot.config import load_settings

    c008 = load_settings("configs/campaign_008_range_mean_reversion.yaml")
    c018 = load_settings("configs/campaign_018_mean_reversion_protective_stop.yaml")
    c008_cfg = c008.strategy.mean_reversion.model_dump()
    c018_cfg = c018.strategy.mean_reversion_protective_stop.model_dump()
    assert c008_entry_params(c008_cfg) == c008_entry_params(c018_cfg)
    assert c018_cfg["protective_stop"]["favorable_excursion_r_threshold"] == 1.0
    assert c018_cfg["midline_exit"] is False


def test_protective_stop_arms_after_1r_mfe():
    entry, stop = 1.1000, 1.0950  # 50 pip risk
    pad = [(1.1000, 1.1005, 1.0995, 1.1000)] * 6
    rows = pad + [
        (1.1000, 1.1005, 1.0995, 1.1000),  # entry bar
        (1.1000, 1.1065, 1.0990, 1.1040),  # MFE >= 1R, arm BE
        (1.1040, 1.1040, 1.0995, 1.1000),  # retrace to entry
        (1.1000, 1.1005, 1.0995, 1.1000),
    ]
    engine = BacktestEngine(
        instrument=_EUR,
        strategy=_OneShotLongStrategy(entry, stop),
        strategy_config={},
        fill_model=FillModel(
            fixed_slippage_pips=Decimal("0"),
            spread_slippage_multiplier=Decimal("0"),
        ),
        starting_equity=Decimal("500"),
        max_bars_in_trade=40,
        protective_stop_after_r=1.0,
        risk_engine=None,
    )
    result = engine.run(_frame(rows))
    assert len(result.trades) == 1
    t = result.trades[0]
    assert t.protective_stop_armed is True
    assert t.exit_reason == "protective_stop"
    assert t.protective_stop_exit is True


def test_no_protective_arm_below_1r():
    entry, stop = 1.1000, 1.0950
    pad = [(1.1000, 1.1005, 1.0995, 1.1000)] * 6
    rows = pad + [
        (1.1000, 1.1005, 1.0995, 1.1000),
        (1.1000, 1.1020, 1.0945, 1.0945),  # hits stop before 1R
        (1.0945, 1.0950, 1.0940, 1.0945),
    ]
    engine = BacktestEngine(
        instrument=_EUR,
        strategy=_OneShotLongStrategy(entry, stop),
        strategy_config={},
        fill_model=FillModel(
            fixed_slippage_pips=Decimal("0"),
            spread_slippage_multiplier=Decimal("0"),
        ),
        starting_equity=Decimal("500"),
        max_bars_in_trade=40,
        protective_stop_after_r=1.0,
        risk_engine=None,
    )
    result = engine.run(_frame(rows))
    assert len(result.trades) == 1
    t = result.trades[0]
    assert t.protective_stop_armed is False
    assert t.exit_reason == "stop"


def test_c018_strategy_no_target_and_paper_only():
    assert MeanReversionProtectiveStopStrategy().paper_only is True
    strat = MeanReversionProtectiveStopStrategy()
    assert strat.name == "mean_reversion_protective_stop"
    assert strat.version == "0.1.0-c018"


def test_c008_strategy_unchanged_version():
    assert MeanReversionStrategy(version="0.1.0-c008").version == "0.1.0-c008"

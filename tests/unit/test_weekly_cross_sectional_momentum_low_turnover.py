"""Tests for weekly_cross_sectional_momentum_low_turnover 0.1.0-c016."""

from __future__ import annotations

import pathlib
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pandas as pd

from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.weekly_cross_sectional_momentum_low_turnover import (
    EXPECTED_PAIRS,
    WeeklyCrossSectionalMomentumLowTurnoverStrategy,
    _apply_usd_exposure_gate,
    _stable_signal_id,
)

_CFG: dict = {
    "momentum_lookback_fast_weeks": 4,
    "momentum_lookback_slow_weeks": 12,
    "momentum_blend_fast": 0.5,
    "momentum_blend_slow": 0.5,
    "volatility_lookback_weeks": 12,
    "volatility_floor": 1.0e-8,
    "max_same_currency_exposure": 1,
    "atr_lookback": 14,
    "atr_stop_multiple": 2.5,
    "max_bars_in_trade": 42,
    "spread_to_atr_max": 0.15,
    "timeframe": "H4",
    "min_atr_pips": {},
}


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


def _ctx(
    eur_usd: Instrument,
    candles: list[Candle],
    cross_pair: dict[str, pd.Series],
) -> StrategyContext:
    frame = CandleFrame.from_candles("EUR_USD", "H4", candles)
    last = float(frame.df["close"].iloc[-1])
    q = Quote(
        instrument="EUR_USD",
        time=frame.df.index[-1].to_pydatetime(),
        bid=Decimal(str(last - 0.00005)),
        ask=Decimal(str(last + 0.00005)),
    )
    return StrategyContext(
        instrument=eur_usd,
        candles=frame,
        market_state=MarketState(
            quote=q,
            spread_snapshot=SpreadSnapshot(
                instrument="EUR_USD",
                time=q.time,
                bid=q.bid,
                ask=q.ask,
                spread_pips=Decimal("1.0"),
            ),
        ),
        open_positions=[],
        config={**_CFG, "cross_pair_h4_closes": cross_pair},
    )


def test_no_broker_imports_in_strategy_module():
    text = (
        pathlib.Path(__file__).resolve().parents[2]
        / "src/forex_bot/strategies/weekly_cross_sectional_momentum_low_turnover.py"
    ).read_text(encoding="utf-8")
    assert "forex_bot.broker" not in text
    assert "forex_bot.execution" not in text
    assert "forex_bot.loops" not in text


def test_stable_signal_id_deterministic():
    a = _stable_signal_id("s", "0.1.0-c016", "EUR_USD", "H4", "2024-01-01", "long")
    b = _stable_signal_id("s", "0.1.0-c016", "EUR_USD", "H4", "2024-01-01", "long")
    c = _stable_signal_id("s", "0.1.0-c016", "EUR_USD", "H4", "2024-01-08", "long")
    assert a == b
    assert a != c


def test_usd_exposure_gate_blocks_conflict():
    long_p, short_p, reason = _apply_usd_exposure_gate(
        "EUR_USD", "USD_JPY", max_same_currency_exposure=1,
    )
    assert long_p is None and short_p is None
    assert reason == "usd_exposure_conflict_both_blocked"


def test_no_signal_before_warmup(eur_usd: Instrument):
    strat = WeeklyCrossSectionalMomentumLowTurnoverStrategy()
    t0 = datetime(2024, 1, 1, tzinfo=UTC)
    candles = [
        _candle(t0 + timedelta(hours=4 * i), 1.1, 1.11, 1.09, 1.105)
        for i in range(50)
    ]
    idx = pd.DatetimeIndex([c.time for c in candles], tz="UTC")
    series = pd.Series([1.1 + 0.001 * i for i in range(50)], index=idx)
    cross = {p: series for p in EXPECTED_PAIRS}
    sig = strat.generate_signal(_ctx(eur_usd, candles, cross))
    assert sig is None


def test_volatility_floor_blocks_via_missing_scores(eur_usd: Instrument):
    strat = WeeklyCrossSectionalMomentumLowTurnoverStrategy()
    n = strat.warmup_bars_required() + 5
    t0 = datetime(2024, 1, 1, tzinfo=UTC)
    candles = [
        _candle(t0 + timedelta(hours=4 * i), 1.1, 1.1, 1.1, 1.1)
        for i in range(n)
    ]
    idx = pd.DatetimeIndex([c.time for c in candles], tz="UTC")
    cross = {p: pd.Series([1.1] * n, index=idx) for p in EXPECTED_PAIRS}
    sig = strat.generate_signal(_ctx(eur_usd, candles, cross))
    assert sig is None

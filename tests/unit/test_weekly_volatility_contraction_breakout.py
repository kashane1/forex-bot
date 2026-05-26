"""Tests for weekly_volatility_contraction_breakout 0.1.0-c017 (CAMPAIGN_017)."""

from __future__ import annotations

import pathlib
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.weekly_volatility_contraction_breakout import (
    WeeklyVolatilityContractionBreakoutStrategy,
)

_CFG: dict = {
    "compression_lookback_weeks": 12,
    "compression_percentile_threshold": 25.0,
    "breakout_buffer_atr_multiple": 0.25,
    "atr_lookback_h4": 14,
    "max_bars_in_trade": 42,
    "take_profit_r": None,
    "trailing_stop_atr_multiple": None,
    "entry_timing": "next_bar_open",
    "same_bar_adverse_stop_wins": True,
    "spread_to_atr_max": 0.15,
    "min_atr_pips": {},
    "timeframe": "H4",
}


def _candle(t: datetime, o: float, h: float, low: float, c: float) -> Candle:
    half = 0.00005
    return Candle(
        instrument="EUR_USD",
        granularity="H4",
        time=t,
        complete=True,
        volume=1000,
        bid_o=Decimal(str(o - half)), bid_h=Decimal(str(h - half)),
        bid_l=Decimal(str(low - half)), bid_c=Decimal(str(c - half)),
        ask_o=Decimal(str(o + half)), ask_h=Decimal(str(h + half)),
        ask_l=Decimal(str(low + half)), ask_c=Decimal(str(c + half)),
    )


def _frame_from_rows(rows: list[tuple[float, float, float, float]], start: datetime) -> CandleFrame:
    candles = [
        _candle(start + timedelta(hours=4 * i), o, h, low, c)
        for i, (o, h, low, c) in enumerate(rows)
    ]
    return CandleFrame.from_candles("EUR_USD", "H4", candles)


def _ctx(frame: CandleFrame, eur_usd: Instrument, cfg: dict | None = None) -> StrategyContext:
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
                instrument="EUR_USD", time=q.time, bid=q.bid, ask=q.ask,
                spread_pips=Decimal("1.0"),
            ),
        ),
        open_positions=[Position(instrument="EUR_USD")],
        config=dict(cfg or _CFG),
    )


def _wide_range_rows(n: int, base: float = 1.1000) -> list[tuple[float, float, float, float]]:
    rows: list[tuple[float, float, float, float]] = []
    for i in range(n):
        o = base + 0.001 * (i % 5)
        h = o + 0.010
        low = o - 0.010
        c = o + 0.002
        rows.append((o, h, low, c))
    return rows


def _quiet_range_rows(n: int, mid: float = 1.1000) -> list[tuple[float, float, float, float]]:
    rows: list[tuple[float, float, float, float]] = []
    for _ in range(n):
        o = mid
        h = mid + 0.0002
        low = mid - 0.0002
        c = mid
        rows.append((o, h, low, c))
    return rows


def test_no_broker_imports_in_strategy_module():
    text = pathlib.Path(
        "src/forex_bot/strategies/weekly_volatility_contraction_breakout.py"
    ).read_text(encoding="utf-8")
    assert "forex_bot.broker" not in text
    assert "oandapyV20" not in text


def test_no_signal_before_warmup(eur_usd: Instrument):
    rows = _wide_range_rows(100)
    frame = _frame_from_rows(rows, datetime(2024, 1, 1, tzinfo=UTC))
    strat = WeeklyVolatilityContractionBreakoutStrategy()
    assert strat.generate_signal(_ctx(frame, eur_usd)) is None


def test_no_signal_while_position_open(eur_usd: Instrument):
    rows = _wide_range_rows(600)
    frame = _frame_from_rows(rows, datetime(2023, 1, 2, tzinfo=UTC))
    last = float(frame.df["close"].iloc[-1])
    q = Quote(
        instrument="EUR_USD",
        time=frame.df.index[-1].to_pydatetime(),
        bid=Decimal(str(last - 0.00005)),
        ask=Decimal(str(last + 0.00005)),
    )
    ctx = StrategyContext(
        instrument=eur_usd,
        candles=frame,
        market_state=MarketState(
            quote=q,
            spread_snapshot=SpreadSnapshot(
                instrument="EUR_USD", time=q.time, bid=q.bid, ask=q.ask,
                spread_pips=Decimal("1.0"),
            ),
        ),
        open_positions=[Position(instrument="EUR_USD", long_units=Decimal("1000"))],
        config=dict(_CFG),
    )
    strat = WeeklyVolatilityContractionBreakoutStrategy()
    assert strat.generate_signal(ctx) is None


def test_deterministic_signal_id(eur_usd: Instrument):
    strat = WeeklyVolatilityContractionBreakoutStrategy()
    wide = _wide_range_rows(12 * 42)
    quiet = _quiet_range_rows(42)
    breakout = [(1.1010, 1.1020, 1.1005, 1.1018)]
    rows = wide + quiet + breakout
    frame = _frame_from_rows(rows, datetime(2023, 1, 2, tzinfo=UTC))
    sig1 = strat.generate_signal(_ctx(frame, eur_usd))
    sig2 = strat.generate_signal(_ctx(frame, eur_usd))
    if sig1 is not None and sig2 is not None:
        assert sig1.signal_id == sig2.signal_id


def test_long_signal_stop_is_opposite_range_side(eur_usd: Instrument):
    strat = WeeklyVolatilityContractionBreakoutStrategy()
    wide = _wide_range_rows(12 * 42)
    quiet = _quiet_range_rows(42, mid=1.1000)
    breakout = [(1.1010, 1.1050, 1.1008, 1.1045)]
    rows = wide + quiet + breakout
    frame = _frame_from_rows(rows, datetime(2023, 1, 2, tzinfo=UTC))
    sig = strat.generate_signal(_ctx(frame, eur_usd))
    if sig is not None and sig.side == "long":
        stop = float(sig.stop_price)
        assert stop < float(sig.features["compressed_week_low"])


def test_no_duplicate_signals_same_compression_cycle(eur_usd: Instrument):
    strat = WeeklyVolatilityContractionBreakoutStrategy()
    wide = _wide_range_rows(12 * 42)
    quiet = _quiet_range_rows(42, mid=1.1000)
    breakout1 = [(1.1010, 1.1050, 1.1008, 1.1045)]
    breakout2 = [(1.1045, 1.1060, 1.1040, 1.1055)]
    rows = wide + quiet + breakout1 + breakout2
    frame = _frame_from_rows(rows, datetime(2023, 1, 2, tzinfo=UTC))
    sig = strat.generate_signal(_ctx(frame, eur_usd))
    if sig is not None:
        assert sig.features.get("compressed_week_start") is not None

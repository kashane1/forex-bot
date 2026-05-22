"""Tests for volatility_breakout 0.1.0-c004.

Verifies the compression→expansion entry: a breakout is only signalled
when (a) the regime going into the breakout bar was ATR-compressed and
(b) the close breaks the prior-bar Donchian channel. No EMA filter, no
lookahead.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.volatility_breakout import VolatilityBreakoutStrategy

_CFG = {
    "atr_lookback": 14,
    "breakout_lookback": 20,
    "compression_lookback": 60,
    "compression_percentile": 40.0,
    "atr_stop_multiple": 2.0,
    "trailing_stop_atr_multiple": 2.0,
    "max_bars_in_trade": 120,
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


def _frame(rows: list[tuple[float, float, float, float]]) -> CandleFrame:
    t0 = datetime(2025, 1, 1, tzinfo=UTC)
    candles = [
        _candle(t0 + timedelta(hours=4 * i), o, h, low, c)
        for i, (o, h, low, c) in enumerate(rows)
    ]
    return CandleFrame.from_candles("EUR_USD", "H4", candles)


def _ctx(frame: CandleFrame, eur_usd: Instrument) -> StrategyContext:
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
        config=dict(_CFG),
    )


def test_compressed_then_breakout_emits_long(eur_usd):
    """90 quiet bars in a tight range (compression), then a bar that
    closes well above the 20-bar high → long signal."""
    rows: list[tuple[float, float, float, float]] = []
    base = 1.1000
    # 90 compressed bars: tiny 5-pip range, flat.
    for i in range(90):
        c = base + (0.00005 if i % 2 else -0.00005)
        rows.append((base, base + 0.0003, base - 0.0003, c))
    # Breakout bar: closes 60 pips above the channel.
    rows.append((base, base + 0.0065, base - 0.0002, base + 0.0060))
    frame = _frame(rows)
    sig = VolatilityBreakoutStrategy(version="0.1.0-c004").generate_signal(
        _ctx(frame, eur_usd)
    )
    assert sig is not None
    assert sig.side == "long"
    assert sig.stop_price < Decimal(str(sig.features["last_close"]))
    assert sig.strategy_name == "volatility_breakout"


def test_breakout_without_preceding_compression_no_signal(eur_usd):
    """If volatility has ALREADY expanded before the breakout bar, the
    bar going into the breakout is not ATR-compressed (its ATR sits in
    the upper part of the recent distribution) → no signal. The
    strategy requires compression to *precede* expansion."""
    rows: list[tuple[float, float, float, float]] = []
    base = 1.1000
    # 85 quiet bars.
    for i in range(85):
        c = base + (0.00005 if i % 2 else -0.00005)
        rows.append((base, base + 0.0003, base - 0.0003, c))
    # 5 progressively larger bars — volatility expands BEFORE the break,
    # so ATR at t-1 is already elevated (top of its 60-bar window).
    for k in range(1, 6):
        swing = 0.0010 * k
        c = base + (swing if k % 2 else -swing)
        rows.append((base, base + swing, base - swing, c))
    # Breakout bar — but the prior bar was no longer compressed.
    rows.append((base, base + 0.0090, base - 0.0010, base + 0.0085))
    frame = _frame(rows)
    sig = VolatilityBreakoutStrategy(version="0.1.0-c004").generate_signal(
        _ctx(frame, eur_usd)
    )
    assert sig is None


def test_compressed_but_no_breakout_no_signal(eur_usd):
    """Compressed regime but the final bar stays inside the channel →
    no breakout, no signal."""
    rows: list[tuple[float, float, float, float]] = []
    base = 1.1000
    for i in range(91):
        c = base + (0.00005 if i % 2 else -0.00005)
        rows.append((base, base + 0.0003, base - 0.0003, c))
    frame = _frame(rows)
    sig = VolatilityBreakoutStrategy(version="0.1.0-c004").generate_signal(
        _ctx(frame, eur_usd)
    )
    assert sig is None


def test_warmup_returns_none(eur_usd):
    frame = _frame([(1.10, 1.1010, 1.0990, 1.10) for _ in range(20)])
    sig = VolatilityBreakoutStrategy(version="0.1.0-c004").generate_signal(
        _ctx(frame, eur_usd)
    )
    assert sig is None


def test_breakdown_emits_short(eur_usd):
    """Compression then a close below the channel → short."""
    rows: list[tuple[float, float, float, float]] = []
    base = 1.1000
    for i in range(90):
        c = base + (0.00005 if i % 2 else -0.00005)
        rows.append((base, base + 0.0003, base - 0.0003, c))
    rows.append((base, base + 0.0002, base - 0.0065, base - 0.0060))
    frame = _frame(rows)
    sig = VolatilityBreakoutStrategy(version="0.1.0-c004").generate_signal(
        _ctx(frame, eur_usd)
    )
    assert sig is not None
    assert sig.side == "short"
    assert sig.stop_price > Decimal(str(sig.features["last_close"]))


def test_no_signal_when_position_open(eur_usd):
    rows: list[tuple[float, float, float, float]] = []
    base = 1.1000
    for i in range(90):
        c = base + (0.00005 if i % 2 else -0.00005)
        rows.append((base, base + 0.0003, base - 0.0003, c))
    rows.append((base, base + 0.0065, base - 0.0002, base + 0.0060))
    frame = _frame(rows)
    ctx = _ctx(frame, eur_usd)
    ctx = StrategyContext(
        instrument=ctx.instrument,
        candles=ctx.candles,
        market_state=ctx.market_state,
        open_positions=[Position(instrument="EUR_USD", long_units=Decimal("100"))],
        config=ctx.config,
    )
    assert VolatilityBreakoutStrategy(version="0.1.0-c004").generate_signal(ctx) is None

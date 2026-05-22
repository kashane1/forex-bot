"""Tests for mean_reversion 0.1.0-c008 (CAMPAIGN_008, research-only).

Verifies: a reversion long fires only in a low-ADX range regime when
price is oversold; no signal in a strong trend even at an extreme; the
strategy is paper-only; entries always carry a hard stop on the correct
side.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.mean_reversion import MeanReversionStrategy

_CFG = {
    "atr_lookback": 14,
    "zscore_lookback": 20,
    "zscore_long_threshold": -2.0,
    "zscore_short_threshold": 2.0,
    "rsi_lookback": 14,
    "regime_ema": 200,
    "adx_lookback": 14,
    "adx_max": 20.0,
    "atr_stop_multiple": 1.5,
    "trailing_stop_atr_multiple": None,
    "max_bars_in_trade": 40,
    "min_atr_pips": {},
    "timeframe": "H4",
}


def _candle(t: datetime, o: float, h: float, low: float, c: float) -> Candle:
    half = 0.00005
    return Candle(
        instrument="EUR_USD", granularity="H4", time=t, complete=True, volume=1000,
        bid_o=Decimal(str(o-half)), bid_h=Decimal(str(h-half)),
        bid_l=Decimal(str(low-half)), bid_c=Decimal(str(c-half)),
        ask_o=Decimal(str(o+half)), ask_h=Decimal(str(h+half)),
        ask_l=Decimal(str(low+half)), ask_c=Decimal(str(c+half)),
    )


def _frame(rows: list[tuple[float, float, float, float]]) -> CandleFrame:
    t0 = datetime(2025, 1, 1, tzinfo=UTC)
    return CandleFrame.from_candles(
        "EUR_USD", "H4",
        [_candle(t0 + timedelta(hours=4*i), *r) for i, r in enumerate(rows)],
    )


def _ctx(frame: CandleFrame, eur_usd: Instrument) -> StrategyContext:
    last = float(frame.df["close"].iloc[-1])
    q = Quote(instrument="EUR_USD", time=frame.df.index[-1].to_pydatetime(),
              bid=Decimal(str(last-0.00005)), ask=Decimal(str(last+0.00005)))
    return StrategyContext(
        instrument=eur_usd, candles=frame,
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


def test_strategy_is_paper_only():
    assert MeanReversionStrategy().paper_only is True


def test_range_oversold_emits_long(eur_usd):
    """A flat, range-bound series (low ADX) with a sharp final dip
    (oversold z-score) → reversion long."""
    rows: list[tuple[float, float, float, float]] = []
    base = 1.1000
    import random
    rng = random.Random(7)
    for _ in range(250):
        # tight mean-reverting noise → low ADX, range regime
        m = base + rng.uniform(-0.0010, 0.0010)
        rows.append((m, m + 0.0006, m - 0.0006, m))
    # sharp multi-bar dip → strongly negative z-score, low RSI
    for k in range(1, 8):
        m = base - 0.0009 * k
        rows.append((m + 0.0002, m + 0.0004, m - 0.0004, m))
    frame = _frame(rows)
    sig = MeanReversionStrategy(version="0.1.0-c008").generate_signal(
        _ctx(frame, eur_usd)
    )
    assert sig is not None
    assert sig.side == "long"
    assert sig.stop_price < Decimal(str(sig.features["last_close"]))
    assert sig.features["adx"] < 20.0


def test_strong_trend_blocks_signal(eur_usd):
    """In a strong steady downtrend ADX is high → range gate blocks the
    reversion entry even though price is making new lows."""
    rows = []
    base = 1.2000
    for i in range(280):
        m = base - 0.0010 * i
        rows.append((m, m + 0.0004, m - 0.0006, m - 0.0004))
    frame = _frame(rows)
    sig = MeanReversionStrategy(version="0.1.0-c008").generate_signal(
        _ctx(frame, eur_usd)
    )
    assert sig is None


def test_warmup_returns_none(eur_usd):
    frame = _frame([(1.10, 1.1010, 1.0990, 1.10) for _ in range(60)])
    assert MeanReversionStrategy(version="0.1.0-c008").generate_signal(
        _ctx(frame, eur_usd)
    ) is None


def test_no_signal_when_position_open(eur_usd):
    rows: list[tuple[float, float, float, float]] = []
    base = 1.1000
    import random
    rng = random.Random(7)
    for _ in range(250):
        m = base + rng.uniform(-0.0010, 0.0010)
        rows.append((m, m + 0.0006, m - 0.0006, m))
    for k in range(1, 8):
        m = base - 0.0009 * k
        rows.append((m + 0.0002, m + 0.0004, m - 0.0004, m))
    frame = _frame(rows)
    ctx = _ctx(frame, eur_usd)
    ctx = StrategyContext(
        instrument=ctx.instrument, candles=ctx.candles,
        market_state=ctx.market_state,
        open_positions=[Position(instrument="EUR_USD", short_units=Decimal("-100"))],
        config=ctx.config,
    )
    assert MeanReversionStrategy(version="0.1.0-c008").generate_signal(ctx) is None

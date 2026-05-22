"""Tests for pullback_continuation 0.1.0-c007 (CAMPAIGN_007).

Verifies: a long fires only after an uptrend + a pullback toward the
EMA + a continuation bar; no signal without the pullback; no signal
without the continuation; no Donchian breakout involved.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.pullback_continuation import PullbackContinuationStrategy

_CFG = {
    "ema_fast": 50,
    "ema_slow": 200,
    "atr_lookback": 14,
    "pullback_lookback": 6,
    "pullback_band": 0.5,
    "atr_stop_multiple": 2.0,
    "trailing_stop_atr_multiple": 2.0,
    "max_bars_in_trade": 120,
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


def _uptrend_with_pullback(continuation: bool) -> CandleFrame:
    """300 bars rising slowly enough that EMA50 stays near price, an
    8-bar pullback deep enough to reach the EMA, then a final bar that
    either resumes (continuation) or does not.

    Rise rate 0.0004/bar → in steady state EMA50 trails ≈25×0.0004 =
    0.010 below price. An 8-bar pullback of 0.0018/bar drops 0.0144 —
    enough to puncture the EMA so the pullback low is well within band.
    """
    rows: list[tuple[float, float, float, float]] = []
    base = 1.0000
    for i in range(300):
        m = base + 0.0004 * i
        rows.append((m, m + 0.0005, m - 0.0003, m + 0.0003))
    top = rows[-1][3]
    for k in range(1, 9):  # 8-bar pullback
        m = top - 0.0018 * k
        rows.append((m + 0.0004, m + 0.0006, m - 0.0004, m))
    pulled_low = rows[-1][2]
    prior_high = rows[-1][1]
    if continuation:
        # Resumption bar: closes above the prior high and back above EMA50.
        rows.append((pulled_low, prior_high + 0.0090, pulled_low - 0.0002,
                     prior_high + 0.0085))
    else:
        m = pulled_low - 0.0006
        rows.append((m, m + 0.0003, m - 0.0004, m - 0.0002))
    return _frame(rows)


def test_pullback_then_continuation_emits_long(eur_usd):
    frame = _uptrend_with_pullback(continuation=True)
    sig = PullbackContinuationStrategy(version="0.1.0-c007").generate_signal(
        _ctx(frame, eur_usd)
    )
    assert sig is not None
    assert sig.side == "long"
    assert sig.strategy_name == "pullback_continuation"
    assert sig.stop_price < Decimal(str(sig.features["last_close"]))
    assert "pullback-continuation" in sig.reason


def test_pullback_without_continuation_no_signal(eur_usd):
    frame = _uptrend_with_pullback(continuation=False)
    sig = PullbackContinuationStrategy(version="0.1.0-c007").generate_signal(
        _ctx(frame, eur_usd)
    )
    assert sig is None


def test_uptrend_no_pullback_no_signal(eur_usd):
    """A clean uninterrupted uptrend never pulls back to the EMA → no
    pullback-continuation entry (this strategy does NOT chase breakouts)."""
    rows = []
    base = 1.0000
    for i in range(280):
        m = base + 0.0010 * i
        rows.append((m, m + 0.0006, m - 0.0002, m + 0.0005))
    frame = _frame(rows)
    sig = PullbackContinuationStrategy(version="0.1.0-c007").generate_signal(
        _ctx(frame, eur_usd)
    )
    assert sig is None


def test_warmup_returns_none(eur_usd):
    frame = _frame([(1.10, 1.1010, 1.0990, 1.10) for _ in range(50)])
    sig = PullbackContinuationStrategy(version="0.1.0-c007").generate_signal(
        _ctx(frame, eur_usd)
    )
    assert sig is None


def test_no_signal_when_position_open(eur_usd):
    frame = _uptrend_with_pullback(continuation=True)
    ctx = _ctx(frame, eur_usd)
    ctx = StrategyContext(
        instrument=ctx.instrument, candles=ctx.candles,
        market_state=ctx.market_state,
        open_positions=[Position(instrument="EUR_USD", long_units=Decimal("100"))],
        config=ctx.config,
    )
    assert PullbackContinuationStrategy(version="0.1.0-c007").generate_signal(ctx) is None

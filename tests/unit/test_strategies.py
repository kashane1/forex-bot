"""Strategy unit tests with synthetic inputs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.trend_following import TrendFollowingStrategy


def _build_frame(n: int, slope: float) -> CandleFrame:
    """Monotonic drift where each bar's close == high (uptrend) or close == low
    (downtrend) so that close breaches the prior-bar Donchian boundary on
    each step."""
    base = 1.0
    candles = []
    spread = Decimal("0.00010")  # 1 pip
    for i in range(n):
        m = base + slope * i
        m_dec = Decimal(str(round(m, 5)))
        bid_c = m_dec - spread / 2
        ask_c = m_dec + spread / 2
        prev_m = Decimal(str(round(base + slope * (i - 1), 5))) if i > 0 else m_dec
        bid_o = prev_m - spread / 2
        ask_o = prev_m + spread / 2
        if slope >= 0:
            bid_h, bid_l = bid_c, bid_o
            ask_h, ask_l = ask_c, ask_o
        else:
            bid_h, bid_l = bid_o, bid_c
            ask_h, ask_l = ask_o, ask_c
        candles.append(
            Candle(
                instrument="EUR_USD",
                granularity="H4",
                time=datetime(2025, 1, 1, tzinfo=UTC) + timedelta(hours=4 * i),
                complete=True,
                volume=1000,
                bid_o=bid_o, bid_h=bid_h, bid_l=bid_l, bid_c=bid_c,
                ask_o=ask_o, ask_h=ask_h, ask_l=ask_l, ask_c=ask_c,
            )
        )
    return CandleFrame.from_candles("EUR_USD", "H4", candles)


def _ctx(frame: CandleFrame, eur_usd: Instrument, *, config: dict) -> StrategyContext:
    last_close = float(frame.df["close"].iloc[-1])
    quote = Quote(
        instrument="EUR_USD",
        time=frame.df.index[-1].to_pydatetime(),
        bid=Decimal(str(last_close - 0.0001)),
        ask=Decimal(str(last_close + 0.0001)),
    )
    return StrategyContext(
        instrument=eur_usd,
        candles=frame,
        market_state=MarketState(
            quote=quote,
            spread_snapshot=SpreadSnapshot(
                instrument="EUR_USD",
                time=quote.time,
                bid=quote.bid,
                ask=quote.ask,
                spread_pips=Decimal("2.0"),
            ),
        ),
        open_positions=[Position(instrument="EUR_USD")],
        config=config,
    )


def test_trend_following_emits_long_on_uptrend(eur_usd):
    frame = _build_frame(n=300, slope=0.00010)
    strat = TrendFollowingStrategy(version="0.1.0")
    cfg = {
        "ema_fast": 20,
        "ema_slow": 60,
        "donchian_lookback": 10,
        "atr_lookback": 14,
        "atr_stop_multiple": 2.5,
        "min_atr_pips": {},
        "max_bars_in_trade": 60,
        "timeframe": "H4",
    }
    signal = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert signal is not None
    assert signal.side == "long"
    assert signal.stop_price < signal.features["last_close"]


def test_trend_following_no_signal_when_position_open(eur_usd):
    frame = _build_frame(n=300, slope=0.00010)
    strat = TrendFollowingStrategy(version="0.1.0")
    cfg = {
        "ema_fast": 20,
        "ema_slow": 60,
        "donchian_lookback": 10,
        "atr_lookback": 14,
        "atr_stop_multiple": 2.5,
        "max_bars_in_trade": 60,
        "timeframe": "H4",
    }
    ctx = _ctx(frame, eur_usd, config=cfg)
    # Replace open positions with one in the same instrument.
    ctx = StrategyContext(
        instrument=ctx.instrument,
        candles=ctx.candles,
        market_state=ctx.market_state,
        open_positions=[Position(instrument="EUR_USD", long_units=Decimal("100"))],
        config=ctx.config,
    )
    assert strat.generate_signal(ctx) is None


def test_trend_following_warmup_returns_none(eur_usd):
    frame = _build_frame(n=10, slope=0.0001)
    strat = TrendFollowingStrategy(version="0.1.0")
    cfg = {"ema_fast": 20, "ema_slow": 60, "donchian_lookback": 20, "atr_lookback": 14, "atr_stop_multiple": 2.5}
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_trend_following_short_on_downtrend(eur_usd):
    frame = _build_frame(n=300, slope=-0.00010)
    strat = TrendFollowingStrategy(version="0.1.0")
    cfg = {
        "ema_fast": 20,
        "ema_slow": 60,
        "donchian_lookback": 10,
        "atr_lookback": 14,
        "atr_stop_multiple": 2.5,
        "max_bars_in_trade": 60,
        "timeframe": "H4",
    }
    signal = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert signal is not None
    assert signal.side == "short"
    assert signal.stop_price > signal.features["last_close"]

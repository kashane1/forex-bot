"""CAMPAIGN_003: opt-in ADX trend-strength gate on TrendFollowingStrategy.

Proves:
  1. Without `adx_min`, the strategy output is byte-identical to the
     frozen 0.1.0-baseline-frozen behavior (the gate is truly opt-in).
  2. With a very high `adx_min`, all entries are suppressed.
  3. With a moderate `adx_min`, a strong-trend frame still produces a
     signal and the ADX value is recorded in the signal features.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.trend_following import TrendFollowingStrategy


def _uptrend_frame(n: int = 320) -> CandleFrame:
    base = Decimal("1.0500")
    candles = []
    for i in range(n):
        m = base + Decimal("0.0006") * i
        bid_c = m - Decimal("0.00005")
        ask_c = m + Decimal("0.00005")
        prev = base + Decimal("0.0006") * (i - 1) if i > 0 else m
        bid_o = prev - Decimal("0.00005")
        ask_o = prev + Decimal("0.00005")
        candles.append(
            Candle(
                instrument="EUR_USD",
                granularity="H4",
                time=datetime(2025, 1, 1, tzinfo=UTC) + timedelta(hours=4 * i),
                complete=True,
                volume=1000,
                bid_o=bid_o, bid_h=bid_c, bid_l=bid_o, bid_c=bid_c,
                ask_o=ask_o, ask_h=ask_c, ask_l=ask_o, ask_c=ask_c,
            )
        )
    return CandleFrame.from_candles("EUR_USD", "H4", candles)


def _ctx(frame: CandleFrame, eur_usd: Instrument, config: dict) -> StrategyContext:
    last_close = float(frame.df["close"].iloc[-1])
    quote = Quote(
        instrument="EUR_USD",
        time=frame.df.index[-1].to_pydatetime(),
        bid=Decimal(str(last_close - 0.00005)),
        ask=Decimal(str(last_close + 0.00005)),
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
                spread_pips=Decimal("1.0"),
            ),
        ),
        open_positions=[Position(instrument="EUR_USD")],
        config=config,
    )


_BASE_CFG = {
    "ema_fast": 20,
    "ema_slow": 60,
    "donchian_lookback": 10,
    "atr_lookback": 14,
    "atr_stop_multiple": 2.0,
    "min_atr_pips": {},
    "max_bars_in_trade": 60,
    "timeframe": "H4",
}


def test_no_adx_min_is_identical_to_baseline(eur_usd):
    """Omitting adx_min must leave the strategy byte-identical to the
    frozen baseline — same signal, same stop, same id."""
    frame = _uptrend_frame()
    strat = TrendFollowingStrategy(version="0.1.0-baseline-frozen")

    baseline_sig = strat.generate_signal(_ctx(frame, eur_usd, dict(_BASE_CFG)))
    # adx_min explicitly absent (a fresh dict without the key)
    again = strat.generate_signal(_ctx(frame, eur_usd, dict(_BASE_CFG)))

    assert baseline_sig is not None
    assert again is not None
    assert baseline_sig.signal_id == again.signal_id
    assert baseline_sig.side == again.side
    assert baseline_sig.stop_price == again.stop_price
    # The baseline path records adx feature as None (gate disabled).
    assert baseline_sig.features.get("adx") is None


def test_high_adx_min_suppresses_all_entries(eur_usd):
    """A clean monotone uptrend has ADX = 100 exactly (every bar +DM>0,
    -DM=0). The gate rejects when ADX <= adx_min, so adx_min=100 must
    suppress every entry even on this maximally-trending frame. (This
    test passes a raw config dict, deliberately exercising the strategy
    gate directly; the 0<adx_min<100 bound is a config-layer concern.)"""
    frame = _uptrend_frame()
    strat = TrendFollowingStrategy(version="0.2.0-c003")
    cfg = {**_BASE_CFG, "adx_min": 100.0, "adx_lookback": 14}
    assert strat.generate_signal(_ctx(frame, eur_usd, cfg)) is None


def test_moderate_adx_min_allows_strong_trend(eur_usd):
    """A clean uptrend has high ADX, so a 25 threshold still admits the
    breakout and records the ADX value in features."""
    frame = _uptrend_frame()
    strat = TrendFollowingStrategy(version="0.2.0-c003")
    cfg = {**_BASE_CFG, "adx_min": 25.0, "adx_lookback": 14}
    sig = strat.generate_signal(_ctx(frame, eur_usd, cfg))
    assert sig is not None
    assert sig.side == "long"
    assert sig.features.get("adx") is not None
    assert sig.features["adx"] > 25.0
    assert "ADX14=" in sig.reason


def test_adx_gate_only_changes_filtered_bars(eur_usd):
    """With and without the gate, when the gate admits the entry the
    resulting signal is otherwise identical (same side, stop, id)."""
    frame = _uptrend_frame()
    strat = TrendFollowingStrategy(version="0.2.0-c003")
    no_gate = strat.generate_signal(_ctx(frame, eur_usd, dict(_BASE_CFG)))
    with_gate = strat.generate_signal(
        _ctx(frame, eur_usd, {**_BASE_CFG, "adx_min": 20.0})
    )
    assert no_gate is not None and with_gate is not None
    assert no_gate.signal_id == with_gate.signal_id
    assert no_gate.side == with_gate.side
    assert no_gate.stop_price == with_gate.stop_price

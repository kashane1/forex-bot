"""Tests for mean_reversion 0.1.0-c008 (CAMPAIGN_008, research-only).

Verifies: a reversion long fires only in a low-ADX range regime when
price is oversold; no signal in a strong trend even at an extreme; the
strategy is paper-only; entries always carry a hard stop on the correct
side.
"""

from __future__ import annotations

import random
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


def _oversold_range_rows() -> list[tuple[float, float, float, float]]:
    """A flat, low-ADX range followed by a sharp 7-bar dip — the canonical
    reversion-long setup (strongly negative z-score, low RSI, low ADX)."""
    rows: list[tuple[float, float, float, float]] = []
    base = 1.1000
    rng = random.Random(7)
    for _ in range(250):
        m = base + rng.uniform(-0.0010, 0.0010)
        rows.append((m, m + 0.0006, m - 0.0006, m))
    for k in range(1, 8):
        m = base - 0.0009 * k
        rows.append((m + 0.0002, m + 0.0004, m - 0.0004, m))
    return rows


def test_midline_exit_off_keeps_c008_signal(eur_usd):
    """With midline_exit absent (the c008 default) the Signal is identical
    to CAMPAIGN_008: no take_profit_price, exit_model unchanged, no midline
    feature. Proves CAMPAIGN_009's change is strictly opt-in."""
    frame = _frame(_oversold_range_rows())
    sig = MeanReversionStrategy(version="0.1.0-c008").generate_signal(
        _ctx(frame, eur_usd)
    )
    assert sig is not None
    assert sig.side == "long"
    assert sig.take_profit_price is None
    assert sig.exit_model == "hard_stop_or_time"
    assert "midline" not in sig.features


def test_midline_exit_sets_take_profit_target(eur_usd):
    """CAMPAIGN_009: with midline_exit=True a reversion long carries a
    take_profit_price at the rolling mean — above the oversold close and
    above the hard stop — so the engine can exit at the mean instead of
    waiting out the time stop."""
    frame = _frame(_oversold_range_rows())
    base_ctx = _ctx(frame, eur_usd)
    cfg = dict(_CFG)
    cfg["midline_exit"] = True
    ctx = StrategyContext(
        instrument=base_ctx.instrument, candles=base_ctx.candles,
        market_state=base_ctx.market_state,
        open_positions=base_ctx.open_positions, config=cfg,
    )
    sig = MeanReversionStrategy(version="0.2.0-c009").generate_signal(ctx)
    assert sig is not None
    assert sig.side == "long"
    assert sig.take_profit_price is not None
    last_close = Decimal(str(sig.features["last_close"]))
    # a sane long bracket: hard stop below entry, midline target above it
    assert sig.stop_price < last_close < sig.take_profit_price
    assert sig.exit_model == "hard_stop_target_or_time"
    assert "midline" in sig.features
    assert abs(sig.features["midline"] - float(sig.take_profit_price)) < 1e-4

"""Unit tests for CAMPAIGN_025 M5 Donchian + HTF confluence breakout scaffold."""

from __future__ import annotations

import inspect
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.signals import validate_signal_provenance
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import donchian_high, donchian_low
from forex_bot.strategies.m5_donchian_htf_confluence_breakout import (
    D1AGG_SOURCE_M1,
    D1AGG_SOURCE_NATIVE,
    EXIT_EOD,
    EXIT_STOP,
    EXIT_TIME,
    M5DonchianHtfConfluenceBreakoutStrategy,
    aligned_h1_trend,
    compute_stop,
    d1agg_allows,
    m5_breakout_side,
    m15_setup_present,
    resolve_exit,
    validate_c025_data_provenance,
)

_MODULE = "forex_bot.strategies.m5_donchian_htf_confluence_breakout"
_REPO_ROOT = Path(__file__).resolve().parents[2]
_STRATEGY_SOURCE = (
    _REPO_ROOT / "src" / "forex_bot" / "strategies" / "m5_donchian_htf_confluence_breakout.py"
).read_text(encoding="utf-8")

_PROVENANCE = {
    "execution_m5": "m1_derived",
    "context_m15": "m1_derived",
    "context_h1": "m1_derived",
    "context_h4": "m1_derived",
    "d1agg_context": D1AGG_SOURCE_NATIVE,
    "m1_derived_d1agg_allowed": False,
}


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #
def _candle(
    time: datetime,
    *,
    o: float,
    h: float,
    lo: float,
    c: float,
    instrument: str = "EUR_USD",
    granularity: str = "M5",
) -> Candle:
    spread = Decimal("0.00010")
    mo, mh, ml, mc = (Decimal(str(round(v, 5))) for v in (o, h, lo, c))
    return Candle(
        instrument=instrument,
        granularity=granularity,
        time=time,
        complete=True,
        volume=1000,
        bid_o=mo - spread / 2, bid_h=mh - spread / 2, bid_l=ml - spread / 2, bid_c=mc - spread / 2,
        ask_o=mo + spread / 2, ask_h=mh + spread / 2, ask_l=ml + spread / 2, ask_c=mc + spread / 2,
    )


def _trending(n: int, *, granularity: str, minutes_step: int, base_price: float = 1.0, drift: float = 0.0005) -> list[Candle]:
    base = datetime(2024, 1, 2, 0, 0, 0, tzinfo=UTC)
    out: list[Candle] = []
    price = base_price
    for i in range(n):
        t = base + timedelta(minutes=minutes_step * i)
        o = price
        price += drift
        out.append(_candle(t, o=o, h=price + 0.0003, lo=o - 0.0003, c=price, granularity=granularity))
    return out


def _flat_then_breakout_m5(n: int = 80) -> list[Candle]:
    """A flat M5 channel followed by a single decisive upside breakout bar."""
    base = datetime(2024, 1, 2, 0, 0, 0, tzinfo=UTC)
    out: list[Candle] = []
    for i in range(n - 1):
        t = base + timedelta(minutes=5 * i)
        out.append(_candle(t, o=1.0, h=1.0005, lo=0.9995, c=1.0, granularity="M5"))
    t = base + timedelta(minutes=5 * (n - 1))
    out.append(_candle(t, o=1.0, h=1.0050, lo=1.0, c=1.0050, granularity="M5"))  # breakout
    return out


def _ctx(
    m5: list[Candle],
    instrument: Instrument,
    *,
    config: dict | None = None,
    m15: list[Candle] | None = None,
    h1: list[Candle] | None = None,
    h4: list[Candle] | None = None,
    d1agg: list[Candle] | None = None,
) -> StrategyContext:
    frame = CandleFrame.from_candles("EUR_USD", "M5", m5)
    last_close = float(frame.df["close"].iloc[-1])
    qt = frame.df.index[-1].to_pydatetime()
    quote = Quote(instrument="EUR_USD", time=qt, bid=Decimal(str(last_close - 0.0001)), ask=Decimal(str(last_close + 0.0001)))
    cfg = dict(config or {})
    cfg.setdefault("data_provenance", _PROVENANCE)
    cfg["context_frames"] = {
        "M15": CandleFrame.from_candles("EUR_USD", "M15", m15 or _trending(200, granularity="M15", minutes_step=15)),
        "H1": CandleFrame.from_candles("EUR_USD", "H1", h1 or _trending(200, granularity="H1", minutes_step=60)),
        "H4": CandleFrame.from_candles("EUR_USD", "H4", h4 or _trending(200, granularity="H4", minutes_step=240)),
        "D1AGG": CandleFrame.from_candles("EUR_USD", "D1AGG", d1agg or _trending(80, granularity="D1AGG", minutes_step=1440)),
    }
    return StrategyContext(
        instrument=instrument,
        candles=frame,
        market_state=MarketState(
            quote=quote,
            spread_snapshot=SpreadSnapshot(instrument="EUR_USD", time=quote.time, bid=quote.bid, ask=quote.ask, spread_pips=Decimal("1.0")),
        ),
        open_positions=[],
        config=cfg,
    )


def _patch_all_gates_pass(monkeypatch, side: str, decision: datetime) -> None:
    trend = "bullish" if side == "long" else "bearish"
    monkeypatch.setattr(f"{_MODULE}.aligned_h4_trend", lambda *a, **k: (trend, decision, None))
    monkeypatch.setattr(f"{_MODULE}.aligned_h1_trend", lambda *a, **k: (trend, decision, None))
    monkeypatch.setattr(f"{_MODULE}.aligned_d1agg_regime", lambda *a, **k: ("both", decision, None))
    monkeypatch.setattr(f"{_MODULE}.m15_setup_present", lambda **k: (True, True, False))


# --------------------------------------------------------------------------- #
# provenance
# --------------------------------------------------------------------------- #
def test_provenance_rejects_m1_derived_d1agg() -> None:
    bad = dict(_PROVENANCE)
    bad["d1agg_context"] = D1AGG_SOURCE_M1
    with pytest.raises(ValueError, match="rejects m1_derived_d1agg"):
        validate_c025_data_provenance(bad)


def test_provenance_requires_native_d1agg_and_m1_derived_streams() -> None:
    validate_c025_data_provenance(_PROVENANCE)
    with pytest.raises(ValueError):
        validate_c025_data_provenance({"d1agg_context": "other"})
    missing = dict(_PROVENANCE)
    missing["context_m15"] = "native"
    with pytest.raises(ValueError, match="context_m15"):
        validate_c025_data_provenance(missing)


# --------------------------------------------------------------------------- #
# Donchian breakout (prior-bars-only)
# --------------------------------------------------------------------------- #
def test_donchian_uses_prior_completed_bars_only() -> None:
    # The channel high at bar i must equal max(high) of bars [i-length, i-1],
    # never including bar i itself.
    high = pd.Series([1.0, 1.1, 1.2, 1.05, 1.3, 1.4])
    dh = donchian_high(high, 2)
    assert pd.isna(dh.iloc[0]) and pd.isna(dh.iloc[1])
    assert dh.iloc[2] == pytest.approx(1.1)   # max(1.0, 1.1)
    assert dh.iloc[4] == pytest.approx(1.2)   # max(1.2, 1.05) — excludes 1.3 itself
    assert dh.iloc[5] == pytest.approx(1.3)   # max(1.05, 1.3) — excludes 1.4 itself


def test_no_breakout_when_current_bar_only_creates_channel_high() -> None:
    # last_close is the highest value but the *prior* channel high is below it
    # → breakout fires only because the current bar is excluded from its channel.
    high = pd.Series([1.0, 1.0, 1.0, 1.0, 1.5])
    low = pd.Series([0.9, 0.9, 0.9, 0.9, 0.9])
    prior_dc_high = float(donchian_high(high, 3).iloc[-1])  # = 1.0 (excludes 1.5)
    prior_dc_low = float(donchian_low(low, 3).iloc[-1])
    # A close that does NOT exceed the prior channel → no breakout.
    assert m5_breakout_side(last_close=1.0, prior_donchian_high=prior_dc_high, prior_donchian_low=prior_dc_low) is None
    # A close above the prior channel → long.
    assert m5_breakout_side(last_close=1.01, prior_donchian_high=prior_dc_high, prior_donchian_low=prior_dc_low) == "long"


def test_breakout_side_short() -> None:
    assert m5_breakout_side(last_close=0.5, prior_donchian_high=1.0, prior_donchian_low=0.6) == "short"
    assert m5_breakout_side(last_close=0.8, prior_donchian_high=1.0, prior_donchian_low=0.6) is None


# --------------------------------------------------------------------------- #
# HTF context requirements
# --------------------------------------------------------------------------- #
def test_long_signal_requires_h4_and_h1_bullish(monkeypatch, eur_usd: Instrument) -> None:
    m5 = _flat_then_breakout_m5()
    decision = m5[-1].time
    # H1 neutral blocks even with H4 bullish.
    monkeypatch.setattr(f"{_MODULE}.aligned_h4_trend", lambda *a, **k: ("bullish", decision, None))
    monkeypatch.setattr(f"{_MODULE}.aligned_h1_trend", lambda *a, **k: ("neutral", decision, None))
    monkeypatch.setattr(f"{_MODULE}.aligned_d1agg_regime", lambda *a, **k: ("both", decision, None))
    monkeypatch.setattr(f"{_MODULE}.m15_setup_present", lambda **k: (True, True, False))
    strat = M5DonchianHtfConfluenceBreakoutStrategy()
    assert strat.generate_signal(_ctx(m5, eur_usd)) is None


def test_long_signal_emitted_when_all_gates_pass(monkeypatch, eur_usd: Instrument) -> None:
    m5 = _flat_then_breakout_m5()
    decision = m5[-1].time.astimezone(UTC)
    _patch_all_gates_pass(monkeypatch, "long", decision)
    strat = M5DonchianHtfConfluenceBreakoutStrategy()
    sig = strat.generate_signal(_ctx(m5, eur_usd))
    assert sig is not None
    assert sig.side == "long"
    assert sig.campaign_id == "CAMPAIGN_025"
    assert sig.timeframe == "M5"
    assert sig.take_profit_price is None
    assert validate_signal_provenance(sig) == []
    for ts in (sig.htf_feature_times or {}).values():
        assert ts <= sig.decision_time


def test_short_signal_requires_bearish_context(monkeypatch, eur_usd: Instrument) -> None:
    # downside breakout bar
    base = datetime(2024, 1, 2, 0, 0, 0, tzinfo=UTC)
    m5 = [_candle(base + timedelta(minutes=5 * i), o=1.0, h=1.0005, lo=0.9995, c=1.0) for i in range(79)]
    m5.append(_candle(base + timedelta(minutes=5 * 79), o=1.0, h=1.0, lo=0.9950, c=0.9950))
    decision = m5[-1].time.astimezone(UTC)
    _patch_all_gates_pass(monkeypatch, "short", decision)
    strat = M5DonchianHtfConfluenceBreakoutStrategy()
    sig = strat.generate_signal(_ctx(m5, eur_usd))
    assert sig is not None and sig.side == "short"
    # But if context is bullish, the short breakout is blocked.
    monkeypatch.setattr(f"{_MODULE}.aligned_h4_trend", lambda *a, **k: ("bullish", decision, None))
    monkeypatch.setattr(f"{_MODULE}.aligned_h1_trend", lambda *a, **k: ("bullish", decision, None))
    assert strat.generate_signal(_ctx(m5, eur_usd)) is None


# --------------------------------------------------------------------------- #
# D1AGG regime
# --------------------------------------------------------------------------- #
def test_d1agg_allows_matrix() -> None:
    assert d1agg_allows("both", "long") and d1agg_allows("both", "short")
    assert d1agg_allows("not_bearish_only", "long")
    assert not d1agg_allows("not_bearish_only", "short")
    assert d1agg_allows("not_bullish_only", "short")
    assert not d1agg_allows("not_bullish_only", "long")
    assert not d1agg_allows("neither", "long")
    assert not d1agg_allows("neither", "short")


def test_d1agg_unavailable_blocks_trade(monkeypatch, eur_usd: Instrument) -> None:
    m5 = _flat_then_breakout_m5()
    decision = m5[-1].time
    monkeypatch.setattr(f"{_MODULE}.aligned_h4_trend", lambda *a, **k: ("bullish", decision, None))
    monkeypatch.setattr(f"{_MODULE}.aligned_h1_trend", lambda *a, **k: ("bullish", decision, None))
    monkeypatch.setattr(f"{_MODULE}.aligned_d1agg_regime", lambda *a, **k: ("neither", None, "HTF_UNAVAILABLE"))
    monkeypatch.setattr(f"{_MODULE}.m15_setup_present", lambda **k: (True, True, False))
    strat = M5DonchianHtfConfluenceBreakoutStrategy()
    assert strat.generate_signal(_ctx(m5, eur_usd)) is None


# --------------------------------------------------------------------------- #
# M15 setup (anti-chasing)
# --------------------------------------------------------------------------- #
def test_m15_setup_blocks_when_no_pullback_or_compression() -> None:
    # rising series, no pullback below EMA20, and a wide Donchian width → no setup
    n = 30
    high = pd.Series([1.0 + i * 0.01 for i in range(n)])
    low = high - 0.001
    ema_fast = pd.Series([0.5 + i * 0.001 for i in range(n)])  # far below price → no touch
    setup, pb, comp = m15_setup_present(
        side="long", high=high, low=low, ema_fast=ema_fast,
        pullback_lookback=8, donchian_width=1.0, atr_value=0.001,
        compression_width_atr_max=3.0,
    )
    assert not setup and not pb and not comp


def test_m15_setup_pullback_detected() -> None:
    n = 30
    high = pd.Series([1.0 + i * 0.001 for i in range(n)])
    low = high - 0.001
    ema_fast = high + 0.0005  # price dips below EMA20 → pullback
    setup, pb, comp = m15_setup_present(
        side="long", high=high, low=low, ema_fast=ema_fast,
        pullback_lookback=8, donchian_width=10.0, atr_value=0.001,
        compression_width_atr_max=3.0,
    )
    assert setup and pb


def test_m15_setup_compression_detected() -> None:
    n = 30
    high = pd.Series([1.0] * n)
    low = high - 0.001
    ema_fast = pd.Series([0.5] * n)  # no pullback touch
    setup, pb, comp = m15_setup_present(
        side="long", high=high, low=low, ema_fast=ema_fast,
        pullback_lookback=8, donchian_width=0.001, atr_value=0.001,  # width/atr = 1.0 <= 3.0
        compression_width_atr_max=3.0,
    )
    assert setup and comp and not pb


def test_strategy_blocks_when_m15_setup_absent(monkeypatch, eur_usd: Instrument) -> None:
    m5 = _flat_then_breakout_m5()
    decision = m5[-1].time
    monkeypatch.setattr(f"{_MODULE}.aligned_h4_trend", lambda *a, **k: ("bullish", decision, None))
    monkeypatch.setattr(f"{_MODULE}.aligned_h1_trend", lambda *a, **k: ("bullish", decision, None))
    monkeypatch.setattr(f"{_MODULE}.aligned_d1agg_regime", lambda *a, **k: ("both", decision, None))
    monkeypatch.setattr(f"{_MODULE}.m15_setup_present", lambda **k: (False, False, False))
    strat = M5DonchianHtfConfluenceBreakoutStrategy()
    assert strat.generate_signal(_ctx(m5, eur_usd)) is None


# --------------------------------------------------------------------------- #
# next_bar_open / no same-bar entry
# --------------------------------------------------------------------------- #
def test_signal_timestamp_is_completed_bar_and_next_open_is_after(monkeypatch, eur_usd: Instrument) -> None:
    m5 = _flat_then_breakout_m5()
    decision = m5[-1].time.astimezone(UTC)
    _patch_all_gates_pass(monkeypatch, "long", decision)
    strat = M5DonchianHtfConfluenceBreakoutStrategy()
    sig = strat.generate_signal(_ctx(m5, eur_usd))
    assert sig is not None
    # signal stamped at the completed signal bar; the next M5 open (entry) is strictly later
    assert sig.timestamp == decision
    next_bar_open_time = decision + timedelta(minutes=5)
    assert next_bar_open_time > sig.timestamp


# --------------------------------------------------------------------------- #
# stop determinism & farther-of rule
# --------------------------------------------------------------------------- #
def test_stop_is_deterministic_and_takes_farther_level() -> None:
    # ATR stop distance = 2*0.001 = 0.002; structure distance = 0.010 → structure wins
    s1 = compute_stop(side="long", signal_close=1.05, prior_atr=0.001, atr_multiple=2.0, structure_level=1.04)
    s2 = compute_stop(side="long", signal_close=1.05, prior_atr=0.001, atr_multiple=2.0, structure_level=1.04)
    assert s1 == s2 == pytest.approx(1.04)  # farther = structure level
    # ATR wins when it is farther
    s3 = compute_stop(side="long", signal_close=1.05, prior_atr=0.010, atr_multiple=2.0, structure_level=1.049)
    assert s3 == pytest.approx(1.05 - 0.02)
    # short mirrors
    s4 = compute_stop(side="short", signal_close=1.0, prior_atr=0.001, atr_multiple=2.0, structure_level=1.01)
    assert s4 == pytest.approx(1.01)


# --------------------------------------------------------------------------- #
# exit resolver: stop -> time -> eod, no target/trailing/protective
# --------------------------------------------------------------------------- #
def test_time_stop_fires_at_exact_bar_count() -> None:
    # never hits stop → time stop at exactly entry+48
    highs = [1.0] * 200
    lows = [0.5] * 200  # never reaches a far stop
    reason, idx = resolve_exit(side="long", stop_price=0.0, entry_index=10, highs=highs, lows=lows, max_bars_in_trade=48)
    assert reason == EXIT_TIME
    assert idx == 10 + 48


def test_stop_takes_priority_over_time() -> None:
    highs = [1.0] * 60
    lows = [1.0] * 60
    lows[12] = 0.90  # stop hit at bar 12 (before time stop)
    reason, idx = resolve_exit(side="long", stop_price=0.95, entry_index=10, highs=highs, lows=lows, max_bars_in_trade=48)
    assert reason == EXIT_STOP and idx == 12


def test_eod_when_data_runs_out_before_time_stop() -> None:
    highs = [1.0] * 20
    lows = [0.99] * 20  # never hits a low stop
    reason, idx = resolve_exit(side="long", stop_price=0.5, entry_index=10, highs=highs, lows=lows, max_bars_in_trade=48)
    assert reason == EXIT_EOD and idx == 19


def test_no_target_trailing_protective_exit_in_module() -> None:
    # the exit vocabulary is exactly stop/time/eod
    assert {EXIT_STOP, EXIT_TIME, EXIT_EOD} == {"stop", "time", "eod"}
    lowered = _STRATEGY_SOURCE.lower()
    assert "take_profit" not in lowered.replace("take_profit_price=none", "")
    assert "trailing" not in lowered
    assert "protective" not in lowered


# --------------------------------------------------------------------------- #
# no lookahead in HTF alignment
# --------------------------------------------------------------------------- #
def test_h1_trend_ignores_future_bars() -> None:
    base = datetime(2024, 1, 2, 0, 0, 0, tzinfo=UTC)
    candles: list[Candle] = []
    price = 1.0
    for i in range(80):
        price += 0.0010
        candles.append(_candle(base + timedelta(hours=i), o=price - 0.001, h=price + 0.0002, lo=price - 0.0002, c=price, granularity="H1"))
    decision_time = candles[-1].time
    # falling bars AFTER the decision must not flip the trend
    for j in range(40):
        price -= 0.0030
        candles.append(_candle(base + timedelta(hours=80 + j), o=price + 0.003, h=price + 0.0002, lo=price - 0.0002, c=price, granularity="H1"))
    frame = CandleFrame.from_candles("EUR_USD", "H1", candles)
    trend, ts, block = aligned_h1_trend(frame, decision_time, slope_bars=3)
    assert block is None
    assert trend == "bullish"
    assert ts is not None and ts <= decision_time


# --------------------------------------------------------------------------- #
# hygiene
# --------------------------------------------------------------------------- #
def test_wrong_execution_granularity_raises(eur_usd: Instrument) -> None:
    h4 = _trending(200, granularity="H4", minutes_step=240)
    frame = CandleFrame.from_candles("EUR_USD", "H4", h4)
    ctx = _ctx(_flat_then_breakout_m5(), eur_usd)
    bad_ctx = StrategyContext(
        instrument=eur_usd, candles=frame, market_state=ctx.market_state,
        open_positions=[], config=ctx.config,
    )
    strat = M5DonchianHtfConfluenceBreakoutStrategy()
    with pytest.raises(ValueError, match="execution frame must be M5"):
        strat.generate_signal(bad_ctx)


def test_no_signal_before_warmup(eur_usd: Instrument) -> None:
    m5 = _flat_then_breakout_m5(n=30)
    strat = M5DonchianHtfConfluenceBreakoutStrategy()
    assert strat.generate_signal(_ctx(m5, eur_usd)) is None


def test_strategy_has_no_broker_or_oanda_imports() -> None:
    assert "forex_bot.broker" not in _STRATEGY_SOURCE
    assert "forex_bot.execution" not in _STRATEGY_SOURCE
    assert "forex_bot.loops" not in _STRATEGY_SOURCE
    assert "oanda" not in _STRATEGY_SOURCE.lower()


def test_open_position_blocks_new_signal(monkeypatch, eur_usd: Instrument) -> None:
    from forex_bot.domain.positions import Position

    m5 = _flat_then_breakout_m5()
    decision = m5[-1].time.astimezone(UTC)
    _patch_all_gates_pass(monkeypatch, "long", decision)
    ctx = _ctx(m5, eur_usd)
    held = Position(instrument="EUR_USD", long_units=Decimal("1000"), long_average_price=Decimal("1.0"))
    ctx2 = StrategyContext(
        instrument=ctx.instrument, candles=ctx.candles, market_state=ctx.market_state,
        open_positions=[held], config=ctx.config,
    )
    strat = M5DonchianHtfConfluenceBreakoutStrategy()
    assert strat.generate_signal(ctx2) is None


def test_strategy_module_self_documents_scaffold_only() -> None:
    src = inspect.getsource(M5DonchianHtfConfluenceBreakoutStrategy)
    assert "scaffold only" in src.lower()

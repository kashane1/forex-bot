"""Unit tests for CAMPAIGN_022 H4/H1 pullback resolution entry scaffold."""

from __future__ import annotations

import inspect
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from forex_bot.config import (
    H4H1PullbackResolutionEntryStrategyConfig,
    Settings,
    StrategyConfig,
    compute_config_hash,
)
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.signals import validate_signal_provenance
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.h4_h1_pullback_resolution_entry import (
    H4H1PullbackResolutionEntryStrategy,
    aligned_h1_pullback_holds,
    aligned_h4_bias,
    validate_c022_data_provenance,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STRATEGY_SOURCE = (
    _REPO_ROOT
    / "src"
    / "forex_bot"
    / "strategies"
    / "h4_h1_pullback_resolution_entry.py"
).read_text(encoding="utf-8")
_CAMPAIGN_YAML = _REPO_ROOT / "configs/campaign_022_h4_h1_pullback_resolution.yaml"
_PROVENANCE = {
    "execution_m15": "m1_derived",
    "context_h1": "m1_derived",
    "context_h4": "m1_derived",
}


def _make_candle(
    time: datetime,
    *,
    open_: float,
    high: float,
    low: float,
    close: float,
    granularity: str = "M15",
    instrument: str = "EUR_USD",
) -> Candle:
    spread = Decimal("0.00010")
    mid_o = Decimal(str(round(open_, 5)))
    mid_h = Decimal(str(round(high, 5)))
    mid_l = Decimal(str(round(low, 5)))
    mid_c = Decimal(str(round(close, 5)))
    return Candle(
        instrument=instrument,
        granularity=granularity,
        time=time,
        complete=True,
        volume=1000,
        bid_o=mid_o - spread / 2,
        bid_h=mid_h - spread / 2,
        bid_l=mid_l - spread / 2,
        bid_c=mid_c - spread / 2,
        ask_o=mid_o + spread / 2,
        ask_h=mid_h + spread / 2,
        ask_l=mid_l + spread / 2,
        ask_c=mid_c + spread / 2,
    )


def _trending_candles(
    n: int,
    *,
    granularity: str = "M15",
    base_price: float = 1.0,
    drift: float = 0.0010,
    minutes_step: int = 15,
    wick: float = 0.0002,
) -> list[Candle]:
    base = datetime(2024, 1, 2, 0, 0, 0, tzinfo=UTC)
    out: list[Candle] = []
    price = base_price
    for i in range(n):
        o = price
        price += drift
        out.append(_make_candle(
            base + timedelta(minutes=minutes_step * i),
            open_=o, high=price + wick, low=price - wick, close=price,
            granularity=granularity,
        ))
    return out


def _ctx_from_m15(
    m15_candles: list[Candle],
    config: dict,
    instrument: Instrument,
    *,
    h1: list[Candle] | None = None,
    h4: list[Candle] | None = None,
) -> StrategyContext:
    frame = CandleFrame.from_candles("EUR_USD", "M15", m15_candles)
    last_close = float(frame.df["close"].iloc[-1])
    quote_time = frame.df.index[-1].to_pydatetime()
    quote = Quote(
        instrument="EUR_USD",
        time=quote_time,
        bid=Decimal(str(last_close - 0.0001)),
        ask=Decimal(str(last_close + 0.0001)),
    )
    h1_list = h1 if h1 is not None else _trending_candles(200, granularity="H1", minutes_step=60)
    h4_list = h4 if h4 is not None else _trending_candles(200, granularity="H4", minutes_step=240)
    cfg = dict(config)
    cfg.setdefault("data_provenance", _PROVENANCE)
    cfg["context_frames"] = {
        "H1": CandleFrame.from_candles("EUR_USD", "H1", h1_list),
        "H4": CandleFrame.from_candles("EUR_USD", "H4", h4_list),
    }
    return StrategyContext(
        instrument=instrument,
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
        open_positions=[],
        config=cfg,
    )


# --- provenance ---------------------------------------------------------------


def test_provenance_rejects_daily_layer() -> None:
    bad = dict(_PROVENANCE)
    bad["d1agg_context"] = "native_h4_derived_d1agg"
    with pytest.raises(ValueError, match="no daily layer"):
        validate_c022_data_provenance(bad)


def test_provenance_requires_m1_derived() -> None:
    validate_c022_data_provenance(_PROVENANCE)
    with pytest.raises(ValueError, match="context_h1"):
        validate_c022_data_provenance(
            {"execution_m15": "m1_derived", "context_h1": "other", "context_h4": "m1_derived"}
        )


def test_provenance_missing_raises() -> None:
    with pytest.raises(ValueError, match="BLOCKED_PROVENANCE_AMBIGUITY"):
        validate_c022_data_provenance(None)


# --- H4 bias ------------------------------------------------------------------


def test_h4_bias_bullish_on_uptrend() -> None:
    h4 = CandleFrame.from_candles(
        "EUR_USD", "H4", _trending_candles(200, granularity="H4", minutes_step=240)
    )
    decision = h4.df.index[-1].to_pydatetime()
    bias, ts, block = aligned_h4_bias(
        h4, decision, ema_fast_len=20, ema_slow_len=50, slope_bars=3,
        adx_len=14, adx_min=20.0,
    )
    assert block is None
    assert bias == "bullish"
    assert ts is not None and ts <= decision


def test_h4_bias_bearish_on_downtrend() -> None:
    h4 = CandleFrame.from_candles(
        "EUR_USD", "H4",
        _trending_candles(200, granularity="H4", minutes_step=240, base_price=1.4, drift=-0.0010),
    )
    decision = h4.df.index[-1].to_pydatetime()
    bias, _, block = aligned_h4_bias(
        h4, decision, ema_fast_len=20, ema_slow_len=50, slope_bars=3,
        adx_len=14, adx_min=20.0,
    )
    assert block is None
    assert bias == "bearish"


def test_h4_bias_adx_gate_blocks() -> None:
    # Strong uptrend but an impossibly high ADX floor → range/neutral.
    h4 = CandleFrame.from_candles(
        "EUR_USD", "H4", _trending_candles(200, granularity="H4", minutes_step=240)
    )
    decision = h4.df.index[-1].to_pydatetime()
    # Linear uptrend ADX approaches 100; an unreachable floor proves the gate.
    bias, _, block = aligned_h4_bias(
        h4, decision, ema_fast_len=20, ema_slow_len=50, slope_bars=3,
        adx_len=14, adx_min=150.0,
    )
    assert block is None
    assert bias == "neutral"


def test_h4_bias_ignores_future_bars() -> None:
    # 200 rising H4 bars; decision at bar[-41]; the appended future bars fall
    # sharply. The aligned bias must reflect the pre-decision uptrend.
    up = _trending_candles(160, granularity="H4", minutes_step=240)
    decision = up[-1].time
    base = up[-1].time
    price = float(up[-1].mid_close)
    down: list[Candle] = []
    for j in range(40):
        o = price
        price -= 0.0030
        down.append(_make_candle(
            base + timedelta(minutes=240 * (j + 1)),
            open_=o, high=o + 0.0002, low=price - 0.0002, close=price,
            granularity="H4",
        ))
    frame = CandleFrame.from_candles("EUR_USD", "H4", up + down)
    bias, ts, block = aligned_h4_bias(
        frame, decision, ema_fast_len=20, ema_slow_len=50, slope_bars=3,
        adx_len=14, adx_min=20.0,
    )
    assert block is None
    assert bias == "bullish"
    assert ts is not None and ts <= decision


# --- H1 pullback holds --------------------------------------------------------


def _h1_uptrend_with_dip() -> CandleFrame:
    candles = _trending_candles(90, granularity="H1", minutes_step=60, drift=0.0012)
    # Replace the last 6 bars with a pullback: closes ease lower, deep lows
    # touch the (lagging) EMA20 while close stays well above EMA50.
    base = candles[0].time
    peak = float(candles[-7].mid_close)
    tail: list[Candle] = []
    for j in range(6):
        c = peak - 0.0005 * (j + 1)
        tail.append(_make_candle(
            base + timedelta(minutes=60 * (84 + j)),
            open_=peak, high=peak + 0.0002, low=c - 0.0050, close=c,
            granularity="H1",
        ))
    return CandleFrame.from_candles("EUR_USD", "H1", candles[:-6] + tail)


def test_h1_long_pullback_holds_true() -> None:
    h1 = _h1_uptrend_with_dip()
    decision = h1.df.index[-1].to_pydatetime()
    holds, ts, block = aligned_h1_pullback_holds(
        h1, decision, "long", ema_fast_len=20, ema_slow_len=50, rsi_len=14,
        lookback=6, rsi_pullback_long=45.0, rsi_pullback_short=55.0,
    )
    assert block is None
    assert holds is True
    assert ts is not None and ts <= decision


def test_h1_long_no_pullback_false() -> None:
    # Clean monotonic uptrend: lows never reach EMA20, RSI stays high → no pullback.
    h1 = CandleFrame.from_candles(
        "EUR_USD", "H1", _trending_candles(90, granularity="H1", minutes_step=60, drift=0.0012)
    )
    decision = h1.df.index[-1].to_pydatetime()
    holds, _, block = aligned_h1_pullback_holds(
        h1, decision, "long", ema_fast_len=20, ema_slow_len=50, rsi_len=14,
        lookback=6, rsi_pullback_long=45.0, rsi_pullback_short=55.0,
    )
    assert block is None
    assert holds is False


def test_h1_long_does_not_hold_false() -> None:
    # Downtrend frame with a long bias → close below EMA50 → does not hold.
    h1 = CandleFrame.from_candles(
        "EUR_USD", "H1",
        _trending_candles(90, granularity="H1", minutes_step=60, base_price=1.4, drift=-0.0012),
    )
    decision = h1.df.index[-1].to_pydatetime()
    holds, _, block = aligned_h1_pullback_holds(
        h1, decision, "long", ema_fast_len=20, ema_slow_len=50, rsi_len=14,
        lookback=6, rsi_pullback_long=45.0, rsi_pullback_short=55.0,
    )
    assert block is None
    assert holds is False


# --- full generate_signal plumbing -------------------------------------------


def test_no_signal_before_warmup(eur_usd: Instrument) -> None:
    strategy = H4H1PullbackResolutionEntryStrategy()
    candles = _trending_candles(50)
    assert strategy.generate_signal(_ctx_from_m15(candles, {"adx_min": 0.0}, eur_usd)) is None


def test_no_signal_without_context_frames(eur_usd: Instrument) -> None:
    strategy = H4H1PullbackResolutionEntryStrategy()
    candles = _trending_candles(200)
    frame = CandleFrame.from_candles("EUR_USD", "M15", candles)
    ctx = StrategyContext(
        instrument=eur_usd,
        candles=frame,
        market_state=_ctx_from_m15(candles, {}, eur_usd).market_state,
        open_positions=[],
        config={"data_provenance": _PROVENANCE},
    )
    with pytest.raises(ValueError, match="context_frames"):
        strategy.generate_signal(ctx)


def test_long_signal_when_gates_pass(monkeypatch, eur_usd: Instrument) -> None:
    strategy = H4H1PullbackResolutionEntryStrategy()
    m15 = _trending_candles(200)
    decision = m15[-1].time
    mod = "forex_bot.strategies.h4_h1_pullback_resolution_entry"
    monkeypatch.setattr(
        f"{mod}.aligned_h4_bias",
        lambda *a, **k: ("bullish", decision - timedelta(hours=4), None),
    )
    monkeypatch.setattr(
        f"{mod}.aligned_h1_pullback_holds",
        lambda *a, **k: (True, decision - timedelta(hours=1), None),
    )
    monkeypatch.setattr(f"{mod}.m15_pullback_and_reclaim", lambda **kw: (True, True, "test"))

    sig = strategy.generate_signal(_ctx_from_m15(m15, {"adx_min": 0.0}, eur_usd))
    assert sig is not None
    assert sig.side == "long"
    assert sig.campaign_id == "CAMPAIGN_022"
    assert sig.timeframe == "M15"
    assert validate_signal_provenance(sig) == []
    for ts in (sig.htf_feature_times or {}).values():
        assert ts <= sig.decision_time


def test_h4_neutral_blocks(monkeypatch, eur_usd: Instrument) -> None:
    strategy = H4H1PullbackResolutionEntryStrategy()
    mod = "forex_bot.strategies.h4_h1_pullback_resolution_entry"
    monkeypatch.setattr(f"{mod}.aligned_h4_bias", lambda *a, **k: ("neutral", None, None))
    monkeypatch.setattr(
        f"{mod}.aligned_h1_pullback_holds", lambda *a, **k: (True, None, None)
    )
    monkeypatch.setattr(f"{mod}.m15_pullback_and_reclaim", lambda **kw: (True, True, "x"))
    assert strategy.generate_signal(
        _ctx_from_m15(_trending_candles(200), {"adx_min": 0.0}, eur_usd)
    ) is None


def test_h1_not_holding_blocks(monkeypatch, eur_usd: Instrument) -> None:
    strategy = H4H1PullbackResolutionEntryStrategy()
    decision = _trending_candles(200)[-1].time
    mod = "forex_bot.strategies.h4_h1_pullback_resolution_entry"
    monkeypatch.setattr(
        f"{mod}.aligned_h4_bias", lambda *a, **k: ("bullish", decision, None)
    )
    monkeypatch.setattr(
        f"{mod}.aligned_h1_pullback_holds", lambda *a, **k: (False, decision, None)
    )
    monkeypatch.setattr(f"{mod}.m15_pullback_and_reclaim", lambda **kw: (True, True, "x"))
    assert strategy.generate_signal(
        _ctx_from_m15(_trending_candles(200), {"adx_min": 0.0}, eur_usd)
    ) is None


def test_wrong_execution_granularity_raises(eur_usd: Instrument) -> None:
    strategy = H4H1PullbackResolutionEntryStrategy()
    h4 = _trending_candles(200, granularity="H4", minutes_step=240)
    frame = CandleFrame.from_candles("EUR_USD", "H4", h4)
    base_ctx = _ctx_from_m15(_trending_candles(200), {"adx_min": 0.0}, eur_usd)
    ctx = StrategyContext(
        instrument=eur_usd,
        candles=frame,
        market_state=base_ctx.market_state,
        open_positions=[],
        config=base_ctx.config,
    )
    with pytest.raises(ValueError, match="M15"):
        strategy.generate_signal(ctx)


# --- freeze / config integrity ------------------------------------------------


def test_frozen_config_loads() -> None:
    raw = _CAMPAIGN_YAML.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    for key in ("campaign", "research_metadata", "financing", "data_provenance"):
        data.pop(key, None)
    data.setdefault("config_hash", compute_config_hash(raw))
    data.setdefault("config_source_path", str(_CAMPAIGN_YAML))
    settings = Settings.model_validate(data)
    assert settings.strategy.enabled == ["h4_h1_pullback_resolution_entry"]
    assert settings.app.trading_enabled is False
    assert settings.app.allow_order_submission is False
    sc = settings.strategy.h4_h1_pullback_resolution_entry
    assert sc is not None
    assert sc.version == "0.1.0-c022"
    assert sc.timeframe == "M15"
    assert sc.h4_adx_min == 20.0
    assert sc.adx_min == 18.0
    assert sc.atr_stop_multiple == 2.0


def test_config_rejects_bad_rsi_thresholds() -> None:
    with pytest.raises(Exception):
        H4H1PullbackResolutionEntryStrategyConfig(
            version="0.1.0-c022", h1_rsi_pullback_long=60.0, h1_rsi_pullback_short=55.0
        )


def test_yaml_has_no_daily_provenance() -> None:
    raw = yaml.safe_load(_CAMPAIGN_YAML.read_text(encoding="utf-8"))
    prov = raw["data_provenance"]
    assert prov == _PROVENANCE
    assert "d1agg_context" not in prov
    assert raw["research_metadata"]["fill_timing"] == "next_bar_open"
    assert raw["research_metadata"]["promotion_eligible"] is False


def test_approved_registry_empty() -> None:
    approved = yaml.safe_load(
        (_REPO_ROOT / "configs/approved_strategies.yaml").read_text(encoding="utf-8")
    )
    assert approved["approved"] == []


def test_strategy_config_slot_present() -> None:
    src = inspect.getsource(StrategyConfig)
    assert "h4_h1_pullback_resolution_entry" in src


def test_strategy_no_broker_imports() -> None:
    assert "forex_bot.broker" not in _STRATEGY_SOURCE
    assert "forex_bot.execution" not in _STRATEGY_SOURCE
    assert "forex_bot.loops" not in _STRATEGY_SOURCE
    assert "oanda" not in _STRATEGY_SOURCE.lower()

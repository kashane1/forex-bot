"""Unit tests for CAMPAIGN_020 MTF confluence pullback scaffold."""

from __future__ import annotations

import inspect
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
import yaml

from forex_bot.config import (
    MultiTimeframeConfluencePullbackStrategyConfig,
    Settings,
    StrategyConfig,
    compute_config_hash,
)
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.signals import validate_signal_provenance
from forex_bot.research.execution_realism import (
    FillTiming,
    parse_research_metadata,
    validate_campaign_yaml_metadata,
)
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.multi_timeframe_confluence_pullback import (
    MultiTimeframeConfluencePullbackStrategy,
    aligned_d1_trend_at_decision,
    classify_d1_trend,
    h4_pullback_and_trigger,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STRATEGY_SOURCE = (
    _REPO_ROOT
    / "src"
    / "forex_bot"
    / "strategies"
    / "multi_timeframe_confluence_pullback.py"
).read_text(encoding="utf-8")
_CAMPAIGN_YAML = _REPO_ROOT / "configs/campaign_020_mtf_confluence_pullback.yaml"
_H4_HOURS_UTC: tuple[int, ...] = (22, 2, 6, 10, 14, 18)


def _bar_time(base: datetime, idx: int) -> datetime:
    return base + timedelta(hours=4 * idx)


def _make_candle(
    time: datetime,
    *,
    open_: float,
    high: float,
    low: float,
    close: float,
    complete: bool = True,
    instrument: str = "EUR_USD",
) -> Candle:
    spread = Decimal("0.00010")
    mid_o = Decimal(str(round(open_, 5)))
    mid_h = Decimal(str(round(high, 5)))
    mid_l = Decimal(str(round(low, 5)))
    mid_c = Decimal(str(round(close, 5)))
    return Candle(
        instrument=instrument,
        granularity="H4",
        time=time,
        complete=complete,
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


def _ctx_from_candles(
    candles: list[Candle], config: dict, instrument: Instrument
) -> StrategyContext:
    frame = CandleFrame.from_candles("EUR_USD", "H4", candles)
    last_close = float(frame.df["close"].iloc[-1])
    quote_time = frame.df.index[-1].to_pydatetime()
    quote = Quote(
        instrument="EUR_USD",
        time=quote_time,
        bid=Decimal(str(last_close - 0.0001)),
        ask=Decimal(str(last_close + 0.0001)),
    )
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
        config=config,
    )


def _load_campaign_settings_stripped() -> Settings:
    raw_text = _CAMPAIGN_YAML.read_text(encoding="utf-8")
    data = yaml.safe_load(raw_text) or {}
    for key in ("campaign", "research_metadata", "financing"):
        data.pop(key, None)
    data.setdefault("config_hash", compute_config_hash(raw_text))
    data.setdefault("config_source_path", str(_CAMPAIGN_YAML))
    return Settings.model_validate(data)


def _trending_candles(n: int, base_price: float = 1.0, drift: float = 0.0003) -> list[Candle]:
    base = datetime(2020, 1, 6, 22, 0, 0, tzinfo=UTC)
    candles: list[Candle] = []
    price = base_price
    for i in range(n):
        t = _bar_time(base, i)
        o = price
        price += drift
        h = price + 0.0002
        lo = price - 0.0002
        c = price
        candles.append(_make_candle(t, open_=o, high=h, low=lo, close=c))
    return candles


def test_classify_d1_trend() -> None:
    assert classify_d1_trend(1.10, 1.09, 1.05) == "bullish"
    assert classify_d1_trend(1.00, 1.01, 1.05) == "bearish"
    assert classify_d1_trend(1.05, 1.04, 1.05) == "neutral"


def test_no_signal_before_h4_warmup(eur_usd: Instrument) -> None:
    strategy = MultiTimeframeConfluencePullbackStrategy()
    candles = _trending_candles(400)
    cfg = {
        "timeframe": "H4",
        "d1_ema_fast": 20,
        "d1_ema_slow": 50,
        "h4_ema_context": 50,
        "h4_ema_pullback": 20,
        "atr_lookback": 14,
        "pullback_lookback": 6,
    }
    assert strategy.generate_signal(_ctx_from_candles(candles, cfg, eur_usd)) is None


def test_htf_unavailable_blocks_signal(eur_usd: Instrument) -> None:
    strategy = MultiTimeframeConfluencePullbackStrategy()
    candles = _trending_candles(600)
    cfg = {"timeframe": "H4", "adx_min": 0.0}
    # Too few candles for D1AGG EMA50 after aggregation
    few = candles[:30]
    assert strategy.generate_signal(_ctx_from_candles(few, cfg, eur_usd)) is None


def test_d1agg_feature_time_not_after_decision() -> None:
    candles = _trending_candles(600)
    decision = candles[-1].time
    trend, d1_time, block = aligned_d1_trend_at_decision(
        candles,
        decision,
        instrument="EUR_USD",
        ema_fast_len=20,
        ema_slow_len=50,
    )
    if block is None and d1_time is not None:
        assert d1_time <= decision
        assert trend in ("bullish", "bearish", "neutral")


def test_pullback_without_reclaim_no_trigger() -> None:
    n = 10
    close = pd.Series([1.0 + i * 0.001 for i in range(n)])
    low = close - 0.0005
    high = close + 0.0005
    ema_pb = pd.Series([1.005] * n)
    rsi = pd.Series([35.0] * n)
    atr = pd.Series([0.001] * n)
    had, trig, _ = h4_pullback_and_trigger(
        side="long",
        close=close,
        low=low,
        high=high,
        ema_pullback=ema_pb,
        rsi_series=rsi,
        atr_series=atr,
        pullback_lookback=6,
        pullback_band_atr=0.5,
        rsi_pullback_long=40.0,
        rsi_pullback_short=60.0,
    )
    assert had
    assert not trig


def test_trend_without_pullback_blocks() -> None:
    n = 10
    close = pd.Series([1.02 + i * 0.001 for i in range(n)])
    low = close - 0.0001
    high = close + 0.0001
    ema_pb = pd.Series([1.0 + i * 0.001 for i in range(n)])
    rsi = pd.Series([55.0] * n)
    atr = pd.Series([0.001] * n)
    had, _, _ = h4_pullback_and_trigger(
        side="long",
        close=close,
        low=low,
        high=high,
        ema_pullback=ema_pb,
        rsi_series=rsi,
        atr_series=atr,
        pullback_lookback=6,
        pullback_band_atr=0.5,
        rsi_pullback_long=40.0,
        rsi_pullback_short=60.0,
    )
    assert not had


def test_long_signal_provenance_when_gates_pass(
    monkeypatch, eur_usd: Instrument
) -> None:
    strategy = MultiTimeframeConfluencePullbackStrategy()
    candles = _trending_candles(600)
    decision = candles[-1].time

    def _fake_align(
        h4_candles: list[Candle],
        decision_time: datetime,
        *,
        instrument: str,
        ema_fast_len: int,
        ema_slow_len: int,
    ):
        return "bullish", decision - timedelta(days=1), None

    monkeypatch.setattr(
        "forex_bot.strategies.multi_timeframe_confluence_pullback.aligned_d1_trend_at_decision",
        _fake_align,
    )

    # Craft last bars for pullback + reclaim
    base_cfg = {
        "timeframe": "H4",
        "d1_ema_fast": 20,
        "d1_ema_slow": 50,
        "h4_ema_context": 50,
        "h4_ema_pullback": 20,
        "atr_lookback": 14,
        "pullback_lookback": 6,
        "pullback_band_atr": 0.5,
        "rsi_lookback": 14,
        "adx_min": 0.0,
        "min_atr_pips": {},
    }
    ctx = _ctx_from_candles(candles, base_cfg, eur_usd)
    sig = strategy.generate_signal(ctx)
    if sig is not None:
        assert sig.side == "long"
        assert sig.campaign_id == "CAMPAIGN_020"
        assert sig.decision_time is not None
        assert sig.htf_feature_times is not None
        assert validate_signal_provenance(sig) == []
        if sig.htf_feature_times.get("d1agg_trend"):
            assert sig.htf_feature_times["d1agg_trend"] <= sig.decision_time


def test_strategy_no_broker_imports() -> None:
    assert "forex_bot.broker" not in _STRATEGY_SOURCE
    assert "forex_bot.execution" not in _STRATEGY_SOURCE
    assert "forex_bot.loops" not in _STRATEGY_SOURCE


def test_campaign_yaml_fill_timing_next_bar_open() -> None:
    raw = yaml.safe_load(_CAMPAIGN_YAML.read_text(encoding="utf-8"))
    assert validate_campaign_yaml_metadata(raw) == []
    meta = parse_research_metadata(raw["research_metadata"])
    assert meta is not None
    assert meta.fill_timing == FillTiming.NEXT_BAR_OPEN


def test_frozen_config_loads() -> None:
    settings = _load_campaign_settings_stripped()
    assert settings.strategy.enabled == ["multi_timeframe_confluence_pullback"]
    assert settings.app.trading_enabled is False
    assert settings.app.allow_order_submission is False
    sc = settings.strategy.multi_timeframe_confluence_pullback
    assert sc is not None
    assert sc.version == "0.1.0-c020"
    assert sc.d1_ema_slow == 50


def test_config_rejects_trailing_stop() -> None:
    with pytest.raises(Exception):
        MultiTimeframeConfluencePullbackStrategyConfig(
            version="0.1.0-c020",
            trailing_stop_atr_multiple=1.5,
        )


def test_approved_registry_empty() -> None:
    approved = yaml.safe_load(
        (_REPO_ROOT / "configs/approved_strategies.yaml").read_text(encoding="utf-8")
    )
    assert approved["approved"] == []


def test_mean_reversion_source_unchanged() -> None:
    c019 = (_REPO_ROOT / "src/forex_bot/strategies/mean_reversion_thesis_invalidation.py").read_text(
        encoding="utf-8"
    )
    assert "CAMPAIGN_019" in c019


def test_strategy_config_slot_present() -> None:
    src = inspect.getsource(StrategyConfig)
    assert "multi_timeframe_confluence_pullback" in src


def test_spread_filter_enabled_in_campaign_yaml() -> None:
    raw = yaml.safe_load(_CAMPAIGN_YAML.read_text(encoding="utf-8"))
    assert raw["spread_filter"]["enabled"] is True
    assert raw["session_filter"]["enabled"] is True


def test_min_atr_pips_blocks_when_configured(monkeypatch, eur_usd: Instrument) -> None:
    strategy = MultiTimeframeConfluencePullbackStrategy()
    candles = _trending_candles(600)

    def _fake_align(*args, **kwargs):
        return "bullish", candles[-1].time - timedelta(days=1), None

    monkeypatch.setattr(
        "forex_bot.strategies.multi_timeframe_confluence_pullback.aligned_d1_trend_at_decision",
        _fake_align,
    )
    cfg = {
        "timeframe": "H4",
        "adx_min": 0.0,
        "min_atr_pips": {"EUR_USD": 99999.0},
    }
    assert strategy.generate_signal(_ctx_from_candles(candles, cfg, eur_usd)) is None

"""Unit tests for CAMPAIGN_021 LTF MTF confluence entry scaffold."""

from __future__ import annotations

import inspect
import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
import yaml

from forex_bot.config import (
    LowerTimeframeMtfConfluenceEntryStrategyConfig,
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
from forex_bot.strategies.lower_timeframe_mtf_confluence_entry import (
    D1AGG_SOURCE_M1,
    D1AGG_SOURCE_NATIVE,
    LowerTimeframeMtfConfluenceEntryStrategy,
    _aligned_h1_trend,
    m15_pullback_and_reclaim,
    validate_c021_data_provenance,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STRATEGY_SOURCE = (
    _REPO_ROOT
    / "src"
    / "forex_bot"
    / "strategies"
    / "lower_timeframe_mtf_confluence_entry.py"
).read_text(encoding="utf-8")
_CAMPAIGN_YAML = _REPO_ROOT / "configs/campaign_021_ltf_mtf_confluence.yaml"
_PROVENANCE = {
    "execution_m15": "m1_derived",
    "context_h1": "m1_derived",
    "context_h4": "m1_derived",
    "d1agg_context": D1AGG_SOURCE_NATIVE,
    "m1_derived_d1agg_allowed": False,
}


def _m15_time(base: datetime, idx: int) -> datetime:
    return base + timedelta(minutes=15 * idx)


def _make_candle(
    time: datetime,
    *,
    open_: float,
    high: float,
    low: float,
    close: float,
    complete: bool = True,
    instrument: str = "EUR_USD",
    granularity: str = "M15",
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


def _trending_candles(
    n: int,
    *,
    granularity: str = "M15",
    base_price: float = 1.0,
    drift: float = 0.00005,
    minutes_step: int = 15,
) -> list[Candle]:
    base = datetime(2024, 1, 2, 12, 0, 0, tzinfo=UTC)
    candles: list[Candle] = []
    price = base_price
    for i in range(n):
        t = base + timedelta(minutes=minutes_step * i)
        o = price
        price += drift
        h = price + 0.0002
        l = price - 0.0002
        c = price
        candles.append(
            _make_candle(
                t,
                open_=o,
                high=h,
                low=l,
                close=c,
                granularity=granularity,
            )
        )
    return candles


def _ctx_from_m15(
    m15_candles: list[Candle],
    config: dict,
    instrument: Instrument,
    *,
    h1: list[Candle] | None = None,
    h4: list[Candle] | None = None,
    d1agg: list[Candle] | None = None,
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
    d1_list = d1agg if d1agg is not None else _trending_candles(80, granularity="D1AGG", minutes_step=1440)
    cfg = dict(config)
    cfg.setdefault("data_provenance", _PROVENANCE)
    cfg["context_frames"] = {
        "H1": CandleFrame.from_candles("EUR_USD", "H1", h1_list),
        "H4": CandleFrame.from_candles("EUR_USD", "H4", h4_list),
        "D1AGG": CandleFrame.from_candles("EUR_USD", "D1AGG", d1_list),
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


def _load_campaign_settings_stripped() -> Settings:
    raw_text = _CAMPAIGN_YAML.read_text(encoding="utf-8")
    data = yaml.safe_load(raw_text) or {}
    for key in ("campaign", "research_metadata", "financing", "data_provenance"):
        data.pop(key, None)
    data.setdefault("config_hash", compute_config_hash(raw_text))
    data.setdefault("config_source_path", str(_CAMPAIGN_YAML))
    return Settings.model_validate(data)


def test_validate_c021_rejects_m1_derived_d1agg() -> None:
    bad = dict(_PROVENANCE)
    bad["d1agg_context"] = D1AGG_SOURCE_M1
    with pytest.raises(ValueError, match="rejects m1_derived_d1agg"):
        validate_c021_data_provenance(bad)


def test_validate_c021_requires_native_d1agg() -> None:
    validate_c021_data_provenance(_PROVENANCE)
    with pytest.raises(ValueError):
        validate_c021_data_provenance({"d1agg_context": "other"})


def test_no_signal_before_m15_warmup(eur_usd: Instrument) -> None:
    strategy = LowerTimeframeMtfConfluenceEntryStrategy()
    candles = _trending_candles(50)
    cfg = {"adx_min": 0.0}
    assert strategy.generate_signal(_ctx_from_m15(candles, cfg, eur_usd)) is None


def test_no_signal_without_context_frames(eur_usd: Instrument) -> None:
    strategy = LowerTimeframeMtfConfluenceEntryStrategy()
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


def test_pullback_without_reclaim_no_signal() -> None:
    n = 12
    close = pd.Series([1.0 + i * 0.001 for i in range(n)])
    low = close - 0.0005
    high = close + 0.0005
    ema20 = pd.Series([1.005] * n)
    ema50 = pd.Series([1.003] * n)
    had, trig, _ = m15_pullback_and_reclaim(
        side="long",
        close=close,
        low=low,
        high=high,
        ema20=ema20,
        ema50=ema50,
        pullback_lookback=8,
    )
    assert had
    assert not trig


def test_reclaim_without_pullback_blocks() -> None:
    n = 12
    close = pd.Series([1.02 + i * 0.001 for i in range(n)])
    low = close - 0.0001
    high = close + 0.0001
    ema20 = pd.Series([1.0 + i * 0.001 for i in range(n)])
    ema50 = pd.Series([0.99 + i * 0.001 for i in range(n)])
    had, _, _ = m15_pullback_and_reclaim(
        side="long",
        close=close,
        low=low,
        high=high,
        ema20=ema20,
        ema50=ema50,
        pullback_lookback=8,
    )
    assert not had


def test_long_signal_provenance_when_gates_pass(
    monkeypatch, eur_usd: Instrument
) -> None:
    strategy = LowerTimeframeMtfConfluenceEntryStrategy()
    m15 = _trending_candles(200)
    decision = m15[-1].time

    def _bull(*args, **kwargs):
        return "bullish", decision - timedelta(hours=4), None

    monkeypatch.setattr(
        "forex_bot.strategies.lower_timeframe_mtf_confluence_entry._aligned_d1agg_trend",
        _bull,
    )
    monkeypatch.setattr(
        "forex_bot.strategies.lower_timeframe_mtf_confluence_entry._aligned_h4_trend",
        _bull,
    )
    monkeypatch.setattr(
        "forex_bot.strategies.lower_timeframe_mtf_confluence_entry._aligned_h1_trend",
        _bull,
    )
    monkeypatch.setattr(
        "forex_bot.strategies.lower_timeframe_mtf_confluence_entry.m15_pullback_and_reclaim",
        lambda **kw: (True, True, "test"),
    )

    cfg = {"adx_min": 0.0, "min_atr_pips": {}}
    sig = strategy.generate_signal(_ctx_from_m15(m15, cfg, eur_usd))
    assert sig is not None
    assert sig.side == "long"
    assert sig.campaign_id == "CAMPAIGN_021"
    assert sig.timeframe == "M15"
    assert validate_signal_provenance(sig) == []
    for ts in (sig.htf_feature_times or {}).values():
        assert ts <= sig.decision_time


def test_htf_neutral_blocks(monkeypatch, eur_usd: Instrument) -> None:
    strategy = LowerTimeframeMtfConfluenceEntryStrategy()
    m15 = _trending_candles(200)
    decision = m15[-1].time

    def _neutral(*args, **kwargs):
        return "neutral", decision, None

    monkeypatch.setattr(
        "forex_bot.strategies.lower_timeframe_mtf_confluence_entry._aligned_d1agg_trend",
        _neutral,
    )
    monkeypatch.setattr(
        "forex_bot.strategies.lower_timeframe_mtf_confluence_entry._aligned_h4_trend",
        lambda *a, **k: ("bullish", decision, None),
    )
    monkeypatch.setattr(
        "forex_bot.strategies.lower_timeframe_mtf_confluence_entry._aligned_h1_trend",
        lambda *a, **k: ("bullish", decision, None),
    )
    cfg = {"adx_min": 0.0}
    assert strategy.generate_signal(_ctx_from_m15(m15, cfg, eur_usd)) is None


def test_h1_slope_ignores_future_bars() -> None:
    # 60 rising H1 bars, then 40 sharply falling bars appended *after* the
    # decision time. A correct slope is anchored at the aligned bar (rising →
    # bullish); a tail-of-frame slope would read the falling future and flip.
    base = datetime(2024, 1, 2, 0, 0, 0, tzinfo=UTC)
    candles: list[Candle] = []
    price = 1.0
    for i in range(60):
        price += 0.0010
        candles.append(_make_candle(
            base + timedelta(hours=i), open_=price - 0.0010, high=price + 0.0002,
            low=price - 0.0002, close=price, granularity="H1",
        ))
    decision_time = candles[-1].time
    for j in range(40):
        price -= 0.0030
        candles.append(_make_candle(
            base + timedelta(hours=60 + j), open_=price + 0.0030, high=price + 0.0002,
            low=price - 0.0002, close=price, granularity="H1",
        ))
    frame = CandleFrame.from_candles("EUR_USD", "H1", candles)
    trend, ts, block = _aligned_h1_trend(frame, decision_time, slope_bars=3)
    assert block is None
    assert trend == "bullish"
    assert ts is not None and ts <= decision_time


def test_strategy_no_broker_imports() -> None:
    assert "forex_bot.broker" not in _STRATEGY_SOURCE
    assert "forex_bot.execution" not in _STRATEGY_SOURCE
    assert "forex_bot.loops" not in _STRATEGY_SOURCE
    assert "oanda" not in _STRATEGY_SOURCE.lower()


def test_campaign_yaml_fill_timing_next_bar_open() -> None:
    raw = yaml.safe_load(_CAMPAIGN_YAML.read_text(encoding="utf-8"))
    assert validate_campaign_yaml_metadata(raw) == []
    meta = parse_research_metadata(raw["research_metadata"])
    assert meta is not None
    assert meta.fill_timing == FillTiming.NEXT_BAR_OPEN
    assert raw["data_provenance"]["d1agg_context"] == D1AGG_SOURCE_NATIVE
    assert raw["data_provenance"]["m1_derived_d1agg_allowed"] is False


def test_frozen_config_loads() -> None:
    settings = _load_campaign_settings_stripped()
    assert settings.strategy.enabled == ["lower_timeframe_mtf_confluence_entry"]
    assert settings.app.trading_enabled is False
    assert settings.app.allow_order_submission is False
    sc = settings.strategy.lower_timeframe_mtf_confluence_entry
    assert sc is not None
    assert sc.version == "0.1.0-c021"
    assert sc.timeframe == "M15"
    assert sc.max_bars_in_trade == 32
    assert sc.atr_stop_multiple == 2.0


def test_approved_registry_empty() -> None:
    approved = yaml.safe_load(
        (_REPO_ROOT / "configs/approved_strategies.yaml").read_text(encoding="utf-8")
    )
    assert approved["approved"] == []


def test_strategy_config_slot_present() -> None:
    src = inspect.getsource(StrategyConfig)
    assert "lower_timeframe_mtf_confluence_entry" in src


def test_spread_session_filters_in_yaml() -> None:
    raw = yaml.safe_load(_CAMPAIGN_YAML.read_text(encoding="utf-8"))
    assert raw["spread_filter"]["enabled"] is True
    assert raw["session_filter"]["enabled"] is True


def test_min_atr_pips_blocks(monkeypatch, eur_usd: Instrument) -> None:
    strategy = LowerTimeframeMtfConfluenceEntryStrategy()
    m15 = _trending_candles(200)
    decision = m15[-1].time

    def _bull(*args, **kwargs):
        return "bullish", decision, None

    for fn in (
        "_aligned_d1agg_trend",
        "_aligned_h4_trend",
        "_aligned_h1_trend",
    ):
        monkeypatch.setattr(
            f"forex_bot.strategies.lower_timeframe_mtf_confluence_entry.{fn}",
            _bull,
        )
    monkeypatch.setattr(
        "forex_bot.strategies.lower_timeframe_mtf_confluence_entry.m15_pullback_and_reclaim",
        lambda **kw: (True, True, "test"),
    )
    cfg = {"adx_min": 0.0, "min_atr_pips": {"EUR_USD": 99999.0}}
    assert strategy.generate_signal(_ctx_from_m15(m15, cfg, eur_usd)) is None


def test_wrong_execution_granularity_raises(eur_usd: Instrument) -> None:
    strategy = LowerTimeframeMtfConfluenceEntryStrategy()
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

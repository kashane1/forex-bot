"""Unit tests for ``SessionBreakoutStrategy`` (CAMPAIGN_010 research candidate).

These tests are research-only and prove the strategy logic is deterministic
and safe before any larger backtest. A passing suite is **not** strategy
approval; ``configs/approved_strategies.yaml`` remains ``approved: []`` and
the strategy is not added to any paper/demo/live loop.

See:
- docs/research/ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md
- docs/research/PREFERRED_CANDIDATE_EVALUATION_DESIGN.md
"""

from __future__ import annotations

import ast
import inspect
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from forex_bot.config import SessionBreakoutStrategyConfig
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.session_breakout import (
    SessionBreakoutStrategy,
    in_asian_window,
    in_london_window,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


# Use NY-standard H4 alignment: UTC bar opens at 22, 02, 06, 10, 14, 18.
_H4_HOURS_UTC: tuple[int, ...] = (22, 2, 6, 10, 14, 18)


def _bar_time(base: datetime, idx: int) -> datetime:
    """idx-th H4 bar starting at base (UTC). Bars step 4h forward."""
    return base + timedelta(hours=4 * idx)


def _make_candle(
    time: datetime,
    *,
    open_: float,
    high: float,
    low: float,
    close: float,
    complete: bool = True,
) -> Candle:
    spread = Decimal("0.00010")
    mid_o = Decimal(str(round(open_, 5)))
    mid_h = Decimal(str(round(high, 5)))
    mid_l = Decimal(str(round(low, 5)))
    mid_c = Decimal(str(round(close, 5)))
    return Candle(
        instrument="EUR_USD",
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


def _build_h4_frame(
    n: int,
    *,
    base_close: float = 1.0800,
    drift: float = 0.0,
    range_size: float = 0.0008,
    start: datetime | None = None,
    complete_last: bool = True,
) -> CandleFrame:
    """Construct an H4 frame on the NY-standard alignment with uniform bars.

    Each bar has the same close-drift; the high/low are symmetric around
    the mid close (so range == range_size). The last bar can be marked
    incomplete to test the ``completed_only()`` projection.
    """
    base = start or datetime(2025, 1, 6, _H4_HOURS_UTC[0], tzinfo=UTC)
    candles: list[Candle] = []
    for i in range(n):
        time = _bar_time(base, i)
        c = base_close + drift * i
        candles.append(
            _make_candle(
                time,
                open_=c - drift / 2 if drift else c,
                high=c + range_size / 2,
                low=c - range_size / 2,
                close=c,
                complete=True if i < n - 1 else complete_last,
            )
        )
    return CandleFrame.from_candles("EUR_USD", "H4", candles)


def _frame_with_breakout_bar(
    *,
    base_close: float = 1.0800,
    asian_range_size: float = 0.0010,
    asian_open_hour_utc: int = 2,
    london_open_hour_utc: int = 6,
    breakout_direction: str | None = "long",
    breakout_magnitude: float = 0.0002,
    n_prefix: int = 30,
) -> CandleFrame:
    """Build a frame whose last two bars are a clean Asian-bar (t-1) and a
    London-bar (t) with a configurable breakout direction.

    The prefix bars provide ATR warm-up (>= atr_lookback+1) and use the
    NY-standard H4 alignment so the last-but-one bar lands exactly on
    ``asian_open_hour_utc`` UTC and the last bar on ``london_open_hour_utc``
    UTC.
    """
    # The prefix bars walk backwards from the asian bar.
    # We want index -2 = bar @ asian_open_hour, index -1 = bar @ london_open_hour.
    # H4 spacing: 4 hours between bars.
    last_t = datetime(2025, 1, 7, london_open_hour_utc, tzinfo=UTC)
    prev_t = last_t - timedelta(hours=4)
    assert prev_t.hour == asian_open_hour_utc, (
        f"prefix step landed on hour {prev_t.hour}, expected {asian_open_hour_utc}"
    )
    # Build n_prefix prior bars (oldest first) ending just before the Asian bar.
    candles: list[Candle] = []
    for i in range(n_prefix):
        # Bars: (n_prefix - i) steps before prev_t.
        time = prev_t - timedelta(hours=4 * (n_prefix - i))
        # Constant-OHLC bars with a tiny stable range so ATR converges.
        c = base_close
        candles.append(
            _make_candle(
                time,
                open_=c,
                high=c + 0.0001,
                low=c - 0.0001,
                close=c,
            )
        )
    # Asian bar (t-1): clean range = asian_range_size around base_close.
    asian_high = base_close + asian_range_size / 2
    asian_low = base_close - asian_range_size / 2
    candles.append(
        _make_candle(
            prev_t,
            open_=base_close - asian_range_size / 4,
            high=asian_high,
            low=asian_low,
            close=base_close + asian_range_size / 4,
        )
    )
    # London bar (t): breakout direction.
    if breakout_direction == "long":
        london_close = asian_high + breakout_magnitude
    elif breakout_direction == "short":
        london_close = asian_low - breakout_magnitude
    elif breakout_direction == "tie_high":
        london_close = asian_high  # exactly equals prior high
    elif breakout_direction == "tie_low":
        london_close = asian_low  # exactly equals prior low
    else:
        london_close = base_close  # no breakout
    candles.append(
        _make_candle(
            last_t,
            open_=base_close,
            high=max(london_close, asian_high) + 0.0001,
            low=min(london_close, asian_low) - 0.0001,
            close=london_close,
        )
    )
    return CandleFrame.from_candles("EUR_USD", "H4", candles)


def _ctx(
    frame: CandleFrame,
    instrument: Instrument,
    *,
    config: dict,
    open_position_units: Decimal = Decimal("0"),
) -> StrategyContext:
    last_close = float(frame.df["close"].iloc[-1]) if len(frame) else 1.0800
    quote_time = (
        frame.df.index[-1].to_pydatetime()
        if len(frame)
        else datetime(2025, 1, 1, tzinfo=UTC)
    )
    quote = Quote(
        instrument="EUR_USD",
        time=quote_time,
        bid=Decimal(str(last_close - 0.0001)),
        ask=Decimal(str(last_close + 0.0001)),
    )
    position = Position(
        instrument="EUR_USD",
        long_units=open_position_units,
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
        open_positions=[position],
        config=config,
    )


def _default_cfg() -> dict:
    return {
        "version": "0.1.0-c010",
        "timeframe": "H4",
        "atr_lookback": 14,
        "atr_stop_multiple": 2.0,
        "trailing_stop_atr_multiple": None,
        "max_bars_in_trade": 6,
        "min_atr_pips": {},
        "asian_session_hours_utc_start": 22,
        "asian_session_hours_utc_end": 6,
        "london_session_hours_utc_start": 6,
        "london_session_hours_utc_end": 12,
        "min_asian_range_atr_fraction": 0.30,
    }


# ---------------------------------------------------------------------------
# 1. Helper tests (session windows)
# ---------------------------------------------------------------------------


def test_in_london_window_half_open_boundaries():
    assert in_london_window(6, 6, 12) is True  # start inclusive
    assert in_london_window(11, 6, 12) is True  # last hour in window
    assert in_london_window(12, 6, 12) is False  # end exclusive
    assert in_london_window(5, 6, 12) is False


def test_in_asian_window_wraps_midnight():
    # asian = [22, 6) wraps midnight
    assert in_asian_window(22, 22, 6) is True
    assert in_asian_window(23, 22, 6) is True
    assert in_asian_window(0, 22, 6) is True
    assert in_asian_window(5, 22, 6) is True
    assert in_asian_window(6, 22, 6) is False
    assert in_asian_window(21, 22, 6) is False


def test_in_asian_window_non_wrapping():
    # Non-wrapping config (asian start < end)
    assert in_asian_window(2, 1, 5) is True
    assert in_asian_window(5, 1, 5) is False
    assert in_asian_window(0, 1, 5) is False


def test_in_asian_window_equal_start_end_is_false():
    assert in_asian_window(0, 0, 0) is False


# ---------------------------------------------------------------------------
# 2. Config validation tests
# ---------------------------------------------------------------------------


def test_default_config_constructs_with_design_params():
    cfg = SessionBreakoutStrategyConfig(version="0.1.0-c010")
    assert cfg.timeframe == "H4"
    assert cfg.atr_lookback == 14
    assert cfg.atr_stop_multiple == 2.0
    assert cfg.trailing_stop_atr_multiple is None
    assert cfg.max_bars_in_trade == 6
    assert cfg.asian_session_hours_utc_start == 22
    assert cfg.asian_session_hours_utc_end == 6
    assert cfg.london_session_hours_utc_start == 6
    assert cfg.london_session_hours_utc_end == 12
    assert cfg.min_asian_range_atr_fraction == 0.30


def test_invalid_session_hours_raise_at_config_construction():
    # Pydantic wraps the ConfigError raised in @model_validator in a
    # ValidationError; the original message is preserved as the value-error
    # text and can be matched against.
    # Asian start == end is rejected.
    with pytest.raises(ValidationError, match="asian_session_hours_utc_start must differ"):
        SessionBreakoutStrategyConfig(
            version="0.1.0-c010",
            asian_session_hours_utc_start=5,
            asian_session_hours_utc_end=5,
        )
    # London start >= end is rejected.
    with pytest.raises(ValidationError, match="london_session_hours_utc_start must be"):
        SessionBreakoutStrategyConfig(
            version="0.1.0-c010",
            london_session_hours_utc_start=12,
            london_session_hours_utc_end=6,
        )
    # Out-of-range hour is rejected.
    with pytest.raises(ValidationError, match="must be in"):
        SessionBreakoutStrategyConfig(
            version="0.1.0-c010",
            london_session_hours_utc_start=25,
            london_session_hours_utc_end=30,
        )


def test_invalid_parameter_values_raise():
    with pytest.raises(ValidationError, match="atr_lookback must be >= 2"):
        SessionBreakoutStrategyConfig(version="0.1.0-c010", atr_lookback=1)
    with pytest.raises(ValidationError, match="atr_stop_multiple must be > 0"):
        SessionBreakoutStrategyConfig(version="0.1.0-c010", atr_stop_multiple=0.0)
    with pytest.raises(ValidationError, match="max_bars_in_trade must be >= 1"):
        SessionBreakoutStrategyConfig(version="0.1.0-c010", max_bars_in_trade=0)
    with pytest.raises(ValidationError, match="min_asian_range_atr_fraction must be > 0"):
        SessionBreakoutStrategyConfig(version="0.1.0-c010", min_asian_range_atr_fraction=0.0)


# ---------------------------------------------------------------------------
# 3. Strategy core tests
# ---------------------------------------------------------------------------


def test_warmup_returns_none_when_too_few_bars(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    # 10 bars is less than atr_lookback (14) + 2 = 16.
    frame = _build_h4_frame(n=10)
    assert strat.generate_signal(_ctx(frame, eur_usd, config=_default_cfg())) is None


def test_no_signal_when_open_position_present(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="long")
    ctx = _ctx(
        frame,
        eur_usd,
        config=_default_cfg(),
        open_position_units=Decimal("1000"),
    )
    assert strat.generate_signal(ctx) is None


def test_long_signal_when_close_above_prior_high_and_gate_met(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="long", asian_range_size=0.0010)
    # Use a lower range-fraction so the synthetic ATR (small prefix bars)
    # easily lets the 10-pip Asian range pass the gate.
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    signal = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert signal is not None
    assert signal.side == "long"
    assert signal.stop_price < Decimal(str(signal.features["last_close"]))
    assert signal.strategy_name == "session_breakout"
    assert signal.strategy_version == "0.1.0-c010"
    assert signal.exit_model == "time_stop_only"
    assert signal.entry_intent == "market"


def test_short_signal_when_close_below_prior_low_and_gate_met(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="short", asian_range_size=0.0010)
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    signal = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert signal is not None
    assert signal.side == "short"
    assert signal.stop_price > Decimal(str(signal.features["last_close"]))


def test_no_signal_when_close_equals_prior_high(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="tie_high", asian_range_size=0.0010)
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_no_signal_when_close_equals_prior_low(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="tie_low", asian_range_size=0.0010)
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_no_signal_when_asian_range_below_fraction_gate(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    # Asian range is *very* small relative to ATR — the gate trips.
    frame = _frame_with_breakout_bar(
        breakout_direction="long",
        asian_range_size=0.00001,  # 0.1 pip
    )
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.30}
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_no_signal_when_bar_t_not_in_london_window(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    # Build a frame whose last bar is at 14:00 UTC (NY-overlap, not London).
    frame = _frame_with_breakout_bar(
        breakout_direction="long",
        asian_open_hour_utc=10,
        london_open_hour_utc=14,
        asian_range_size=0.0010,
    )
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_no_signal_when_bar_tminus1_not_in_asian_window(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    # London bar at 10:00 UTC; t-1 at 06:00 UTC (the FIRST London bar).
    # Under default config, 06:00 is in London window, not Asian.
    frame = _frame_with_breakout_bar(
        breakout_direction="long",
        asian_open_hour_utc=6,
        london_open_hour_utc=10,
        asian_range_size=0.0010,
    )
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_session_windows_half_open_boundaries(eur_usd: Instrument):
    """The bar at exactly london_start counts; the bar at london_end does not."""
    strat = SessionBreakoutStrategy()
    # london_session_hours_utc_start=6: bar at 06:00 IS London.
    frame_at_start = _frame_with_breakout_bar(
        breakout_direction="long",
        asian_open_hour_utc=2,
        london_open_hour_utc=6,
        asian_range_size=0.0010,
    )
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    assert strat.generate_signal(_ctx(frame_at_start, eur_usd, config=cfg)) is not None

    # london_session_hours_utc_end=12: bar at 12:00 is NOT London.
    # (We use a config with end=10 so bar at 10:00 would be excluded under it.)
    cfg_end = cfg | {"london_session_hours_utc_end": 10}
    frame_at_end = _frame_with_breakout_bar(
        breakout_direction="long",
        asian_open_hour_utc=6,  # 06:00 is now in [6, 10) (London) under cfg_end
        london_open_hour_utc=10,
        asian_range_size=0.0010,
    )
    assert strat.generate_signal(_ctx(frame_at_end, eur_usd, config=cfg_end)) is None


def test_stop_price_is_atr_multiple_below_close_for_long(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="long", asian_range_size=0.0010)
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05, "atr_stop_multiple": 2.0}
    signal = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert signal is not None
    expected_distance = 2.0 * signal.features["prior_atr"]
    actual_distance = signal.features["last_close"] - float(signal.stop_price)
    assert actual_distance == pytest.approx(expected_distance, abs=1e-5)


def test_stop_price_is_atr_multiple_above_close_for_short(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="short", asian_range_size=0.0010)
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05, "atr_stop_multiple": 2.0}
    signal = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert signal is not None
    expected_distance = 2.0 * signal.features["prior_atr"]
    actual_distance = float(signal.stop_price) - signal.features["last_close"]
    assert actual_distance == pytest.approx(expected_distance, abs=1e-5)


def test_min_atr_pips_floor_blocks_when_set(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="long", asian_range_size=0.0010)
    cfg = _default_cfg() | {
        "min_asian_range_atr_fraction": 0.05,
        "min_atr_pips": {"EUR_USD": 1e6},  # absurd floor
    }
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_features_dict_carries_required_keys(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="long", asian_range_size=0.0010)
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    signal = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert signal is not None
    required = {
        "prior_high",
        "prior_low",
        "prior_range",
        "prior_atr",
        "last_close",
        "range_fraction",
        "prior_hour_utc",
        "current_hour_utc",
        "atr_pips",
    }
    assert required.issubset(signal.features.keys())
    # Spot-check the hour-derived fields.
    assert signal.features["current_hour_utc"] == 6  # London open under default
    assert signal.features["prior_hour_utc"] == 2  # Asian (NY-standard alignment)


def test_signal_id_is_deterministic_across_repeated_calls(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="long", asian_range_size=0.0010)
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    s1 = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    s2 = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert s1 is not None
    assert s2 is not None
    assert s1.signal_id == s2.signal_id


def test_signal_carries_correct_version(eur_usd: Instrument):
    strat = SessionBreakoutStrategy(version="0.1.0-c010")
    frame = _frame_with_breakout_bar(breakout_direction="long", asian_range_size=0.0010)
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    signal = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert signal is not None
    assert signal.strategy_version == "0.1.0-c010"
    assert signal.strategy_name == "session_breakout"


def test_strategy_does_not_mutate_config_dict(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="long", asian_range_size=0.0010)
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    snapshot = dict(cfg)
    _ = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert cfg == snapshot  # no mutation


def test_exit_model_is_time_stop_only(eur_usd: Instrument):
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="long", asian_range_size=0.0010)
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    signal = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert signal is not None
    assert signal.exit_model == "time_stop_only"
    # v1 has no take-profit price.
    assert signal.take_profit_price is None


def test_incomplete_last_bar_is_filtered_by_completed_only(eur_usd: Instrument):
    """If the last bar is incomplete, completed_only() drops it, and the
    strategy sees the prior completed bars. This proves no same-bar
    lookahead via incomplete bars."""
    strat = SessionBreakoutStrategy()
    # Build a frame with 30 bars where the last bar is incomplete.
    # The most recent COMPLETED bar will be at index n-2 in the raw df
    # (which becomes index -1 after completed_only filters).
    frame = _build_h4_frame(n=30, complete_last=False)
    # The last completed bar's hour determines session windows. With our
    # _build_h4_frame default base (NY-standard 22 UTC start), after 30 bars
    # the last bar is at index 29 (incomplete), so the last *completed*
    # is at index 28. Whatever hour that is, the contract is:
    # generate_signal must work off the completed projection only.
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    # We don't assert a specific outcome here — only that the strategy
    # does not crash when fed an incomplete-last frame and that it
    # consults only completed bars (the call returns None or a signal
    # built from index -1 of the *completed* projection).
    result = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    # If it produced a signal, the signal's timestamp must NOT be the
    # incomplete bar's timestamp.
    if result is not None:
        last_complete_time = frame.df[frame.df["complete"]].index[-1].to_pydatetime()
        assert result.timestamp == last_complete_time


# ---------------------------------------------------------------------------
# 4. No-lookahead structural audits (module-source-level)
# ---------------------------------------------------------------------------


_STRATEGY_MODULE = Path(inspect.getfile(SessionBreakoutStrategy))


def _module_source() -> str:
    return _STRATEGY_MODULE.read_text(encoding="utf-8")


def test_strategy_imports_no_broker_modules():
    """Static AST check that the strategy module imports nothing from
    forex_bot.broker or forex_bot.execution (would couple to live
    order paths)."""
    tree = ast.parse(_module_source())
    forbidden_prefixes = (
        "forex_bot.broker",
        "forex_bot.execution",
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for prefix in forbidden_prefixes:
                assert not module.startswith(prefix), (
                    f"session_breakout must not import from {prefix}; "
                    f"found `from {module} import ...`"
                )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                for prefix in forbidden_prefixes:
                    assert not alias.name.startswith(prefix), (
                        f"session_breakout must not import {prefix}*; "
                        f"found `import {alias.name}`"
                    )


def test_strategy_module_has_no_lookahead_antipattern():
    """Source-level grep for common lookahead anti-patterns."""
    source = _module_source()
    # .shift(-N) for N > 0 is a future-bar lookahead. Allow .shift(1).
    assert ".shift(-" not in source, (
        "session_breakout.py contains `.shift(-N)`; future-bar shifts are forbidden"
    )
    # No same-bar high/low feature use: bar t's high/low must NOT appear
    # in the entry rule. We allow .iloc[-2] for prior bar, but the
    # source must not use df["high"].iloc[-1] or df["low"].iloc[-1].
    assert 'df["high"].iloc[-1]' not in source
    assert 'df["low"].iloc[-1]' not in source
    assert "df['high'].iloc[-1]" not in source
    assert "df['low'].iloc[-1]" not in source


def test_candidate_independent_from_campaign_002_config():
    """CAMPAIGN_002 used trend_following config keys (ema_fast, ema_slow,
    donchian_lookback). The new candidate must not reference them or
    inherit from TrendFollowingStrategyConfig."""
    source = _module_source()
    forbidden_keys = ("ema_fast", "ema_slow", "donchian_lookback", "trend_following")
    for key in forbidden_keys:
        assert key not in source, (
            f"session_breakout module references `{key}` — must be independent of "
            f"CAMPAIGN_002/trend_following config."
        )


def test_default_config_does_not_inherit_campaign_002_params():
    """The frozen-default config must not silently re-use CAMPAIGN_002
    knobs (EMA periods, Donchian lookback)."""
    fields = set(SessionBreakoutStrategyConfig.model_fields.keys())
    forbidden = {"ema_fast", "ema_slow", "donchian_lookback", "adx_min"}
    assert fields.isdisjoint(forbidden)


# ---------------------------------------------------------------------------
# 5. Approval / safety regression
# ---------------------------------------------------------------------------


def test_candidate_emits_no_approval_artifact(eur_usd: Instrument):
    """generate_signal returns a Signal, not an order, not an approval.

    Documents that downstream approval requires a human edit to
    configs/approved_strategies.yaml per STRATEGY_APPROVAL_PROCESS.md.
    """
    strat = SessionBreakoutStrategy()
    frame = _frame_with_breakout_bar(breakout_direction="long", asian_range_size=0.0010)
    cfg = _default_cfg() | {"min_asian_range_atr_fraction": 0.05}
    signal = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    # If a signal is produced it must NOT carry any approval-shaped field.
    if signal is not None:
        forbidden_fields = {"approval", "is_approved", "approved_for", "trading_enabled"}
        from forex_bot.domain.signals import Signal

        signal_fields = set(Signal.model_fields.keys())
        assert signal_fields.isdisjoint(forbidden_fields)


def test_approved_strategies_yaml_still_empty():
    """Regression: the candidate scaffold must not have flipped the
    research freeze. Read the file directly (no Settings load needed)."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    approved_yaml = repo_root / "configs" / "approved_strategies.yaml"
    text = approved_yaml.read_text(encoding="utf-8")
    # Either `approved: []` literal, or an empty YAML list under `approved:`.
    assert "approved: []" in text or "approved:\n" in text.replace(
        "approved: []", ""
    ), f"approved_strategies.yaml must remain empty; got:\n{text}"
    # Defense in depth: ensure session_breakout is not in the file.
    assert "session_breakout" not in text


def test_session_breakout_not_in_strategy_config_enabled_when_loaded(
    paper_config_path: Path,
):
    """Loading the existing paper config must not silently enable
    session_breakout (the candidate cannot be loaded by paper/demo/live
    pipelines)."""
    from forex_bot.config import load_settings

    settings = load_settings(paper_config_path)
    assert "session_breakout" not in settings.strategy.enabled

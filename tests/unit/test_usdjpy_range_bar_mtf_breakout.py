"""Unit tests for CAMPAIGN_029 USD_JPY 10-pip range-bar MTF breakout scaffold."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from forex_bot.data.non_time_bars import RangeBar
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.signals import validate_signal_provenance
from forex_bot.strategies.usdjpy_range_bar_mtf_breakout import (
    D1AGG_SOURCE_M1,
    D1AGG_SOURCE_NATIVE,
    EXECUTION_BARS_PROVENANCE,
    EXIT_EOD,
    EXIT_STOP,
    EXIT_TIME,
    LiveTradingRefused,
    RangeBarMtfBreakoutConfig,
    UsdJpyRangeBarMtfBreakoutStrategy,
    is_extreme_overshoot,
    pullback_reclaim_side,
    resolve_exit,
    structural_stop,
    validate_c029_data_provenance,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC = (
    _REPO_ROOT / "src" / "forex_bot" / "strategies" / "usdjpy_range_bar_mtf_breakout.py"
).read_text(encoding="utf-8")

_DECISION = datetime(2024, 6, 3, 12, 0, 0, tzinfo=UTC)
_PROVENANCE = {
    "execution_bars": EXECUTION_BARS_PROVENANCE,
    "context_h4": "m1_derived",
    "d1agg_context": D1AGG_SOURCE_NATIVE,
    "m1_derived_d1agg_allowed": False,
}


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #
def _rb(
    close_time: datetime,
    reason: str,
    *,
    o: float,
    h: float,
    lo: float,
    c: float,
    thresholds: int = 1,
    overshoot: float = 0.0,
    instrument: str = "USD_JPY",
) -> RangeBar:
    return RangeBar(
        instrument=instrument,
        price_basis="mid",
        threshold_pips=10.0,
        open=o,
        high=h,
        low=lo,
        close=c,
        volume=1000,
        open_time=close_time - timedelta(minutes=10),
        close_time=close_time,
        source_count=10,
        source_start_time=close_time - timedelta(minutes=10),
        source_end_time=close_time,
        completion_reason=reason,
        thresholds_crossed=thresholds,
        overshoot_pips=overshoot,
        incomplete=False,
    )


def _long_range_series(*, trigger_thresholds: int = 1, instrument: str = "USD_JPY") -> list[RangeBar]:
    """7 completed bars: a pullback (range_down) then a range_up reclaim trigger."""
    reasons = ["range_up", "range_up", "range_down", "range_up", "range_down", "range_down", "range_up"]
    bars: list[RangeBar] = []
    for i, reason in enumerate(reasons):
        t = _DECISION - timedelta(minutes=10 * (len(reasons) - 1 - i))
        c = 150.10 + 0.10 * i
        bars.append(
            _rb(
                t,
                reason,
                o=c - 0.05,
                h=c + 0.06,
                lo=c - 0.06,
                c=c,
                thresholds=trigger_thresholds if i == len(reasons) - 1 else 1,
                instrument=instrument,
            )
        )
    return bars


def _short_range_series() -> list[RangeBar]:
    reasons = ["range_down", "range_down", "range_up", "range_down", "range_up", "range_up", "range_down"]
    bars: list[RangeBar] = []
    for i, reason in enumerate(reasons):
        t = _DECISION - timedelta(minutes=10 * (len(reasons) - 1 - i))
        c = 150.10 - 0.10 * i
        bars.append(_rb(t, reason, o=c + 0.05, h=c + 0.06, lo=c - 0.06, c=c))
    return bars


def _h4_candle(t: datetime, c: float) -> Candle:
    return Candle(
        instrument="USD_JPY",
        granularity="H4",
        time=t,
        complete=True,
        volume=1000,
        mid_o=Decimal(str(round(c - 0.02, 3))),
        mid_h=Decimal(str(round(c + 0.03, 3))),
        mid_l=Decimal(str(round(c - 0.03, 3))),
        mid_c=Decimal(str(round(c, 3))),
    )


def _h4_frame(direction: str, *, n: int = 60, extra_future: bool = False) -> CandleFrame:
    """n completed H4 bars ending at _DECISION - 4h; optional future bar to probe lookahead."""
    candles: list[Candle] = []
    start = _DECISION - timedelta(hours=4 * n)
    for i in range(n):
        t = start + timedelta(hours=4 * i)  # last == _DECISION - 4h
        c = 149.0 + 0.03 * i if direction == "bullish" else 152.0 - 0.03 * i
        candles.append(_h4_candle(t, c))
    if extra_future:
        # a bar that closes AFTER the decision with an extreme opposite value:
        # a lookahead-free strategy must ignore it.
        candles.append(_h4_candle(_DECISION + timedelta(hours=4), 100.0))
    return CandleFrame.from_candles("USD_JPY", "H4", candles)


def _config(**overrides: object) -> dict:
    return {"data_provenance": dict(_PROVENANCE), "strategy": {"usdjpy_range_bar_mtf_breakout": dict(overrides)}}


# --------------------------------------------------------------------------- #
# provenance + config
# --------------------------------------------------------------------------- #
def test_provenance_missing_raises() -> None:
    with pytest.raises(ValueError, match="data_provenance missing"):
        validate_c029_data_provenance(None)


def test_provenance_rejects_m1_derived_d1agg() -> None:
    bad = dict(_PROVENANCE, d1agg_context=D1AGG_SOURCE_M1)
    with pytest.raises(ValueError, match="m1_derived_d1agg"):
        validate_c029_data_provenance(bad)


def test_provenance_requires_range_execution_bars() -> None:
    bad = dict(_PROVENANCE, execution_bars="m5_m1_derived")
    with pytest.raises(ValueError, match="execution_bars"):
        validate_c029_data_provenance(bad)


def test_ten_pip_threshold_is_enforced() -> None:
    RangeBarMtfBreakoutConfig(range_threshold_pips=10.0)  # ok
    with pytest.raises(ValueError, match="10-pip range-bar"):
        RangeBarMtfBreakoutConfig(range_threshold_pips=8.0)
    with pytest.raises(ValueError, match="10-pip range-bar"):
        RangeBarMtfBreakoutConfig.from_config({"usdjpy_range_bar_mtf_breakout": {"range_threshold_pips": 20}})


# --------------------------------------------------------------------------- #
# pure trigger helpers
# --------------------------------------------------------------------------- #
def test_pullback_reclaim_side_long_and_short() -> None:
    assert pullback_reclaim_side(_long_range_series(), pullback_lookback=5) == "long"
    assert pullback_reclaim_side(_short_range_series(), pullback_lookback=5) == "short"


def test_pullback_reclaim_side_none_without_pullback() -> None:
    bars = [_rb(_DECISION - timedelta(minutes=10 * (4 - i)), "range_up", o=150 + i, h=150.1 + i, lo=149.9 + i, c=150 + i) for i in range(5)]
    assert pullback_reclaim_side(bars, pullback_lookback=5) is None  # all up, no pullback


def test_is_extreme_overshoot_follows_spec() -> None:
    normal = _rb(_DECISION, "range_up", o=150.0, h=150.12, lo=149.98, c=150.10, thresholds=1, overshoot=2.0)
    multi = _rb(_DECISION, "range_up", o=150.0, h=150.30, lo=149.98, c=150.28, thresholds=2, overshoot=8.0)
    big_overshoot = _rb(_DECISION, "range_up", o=150.0, h=150.30, lo=149.98, c=150.28, thresholds=1, overshoot=15.0)
    assert is_extreme_overshoot(normal, max_thresholds=1, max_overshoot_pips=10.0) is False
    assert is_extreme_overshoot(multi, max_thresholds=1, max_overshoot_pips=10.0) is True
    assert is_extreme_overshoot(big_overshoot, max_thresholds=1, max_overshoot_pips=10.0) is True


def test_structural_stop_uses_swing_or_floor() -> None:
    bars = _long_range_series()
    stop = structural_stop(bars, side="long", structure_lookback=5, range_threshold_pips=10.0, stop_range_multiple=2.0)
    trigger_close = bars[-1].close
    assert stop < trigger_close  # long stop is below
    # at least the 20-pip floor away
    assert trigger_close - stop >= 0.20 - 1e-9


def test_resolve_exit_priority_stop_time_eod() -> None:
    highs = [150.0, 150.5, 150.6, 150.7, 150.8]
    lows = [149.9, 149.4, 149.95, 149.96, 149.97]
    # long stop at 149.5 hit at index 1
    assert resolve_exit(side="long", stop_price=149.5, entry_index=0, highs=highs, lows=lows, max_bars_in_trade=4) == (EXIT_STOP, 1)
    # never hit, time stop at max_bars
    assert resolve_exit(side="long", stop_price=140.0, entry_index=0, highs=highs, lows=lows, max_bars_in_trade=2) == (EXIT_TIME, 2)
    # never hit, runs out of data
    assert resolve_exit(side="long", stop_price=140.0, entry_index=0, highs=highs, lows=lows, max_bars_in_trade=99) == (EXIT_EOD, 4)


def test_resolve_exit_never_checks_entry_bar() -> None:
    # a stop "already breached" on the entry bar must NOT trigger a same-bar exit.
    highs = [200.0, 150.1]
    lows = [100.0, 149.99]  # entry bar low 100 is far below the stop
    assert resolve_exit(side="long", stop_price=149.5, entry_index=0, highs=highs, lows=lows, max_bars_in_trade=4) == (EXIT_EOD, 1)


# --------------------------------------------------------------------------- #
# strategy signal generation
# --------------------------------------------------------------------------- #
def _strategy() -> UsdJpyRangeBarMtfBreakoutStrategy:
    return UsdJpyRangeBarMtfBreakoutStrategy()


def test_generates_long_signal_on_bullish_h4() -> None:
    sig = _strategy().generate_signal(_long_range_series(), h4_frame=_h4_frame("bullish"), config=_config())
    assert sig is not None
    assert sig.side == "long"
    assert sig.instrument == "USD_JPY"
    assert sig.campaign_id == "CAMPAIGN_029"
    assert sig.features["fill_timing"] == "next_bar_open"


def test_generates_short_signal_on_bearish_h4() -> None:
    sig = _strategy().generate_signal(_short_range_series(), h4_frame=_h4_frame("bearish"), config=_config())
    assert sig is not None
    assert sig.side == "short"


def test_no_signal_when_h4_opposes_trigger() -> None:
    # long trigger but bearish H4 → blocked
    assert _strategy().generate_signal(_long_range_series(), h4_frame=_h4_frame("bearish"), config=_config()) is None


def test_missing_htf_context_skips_signal() -> None:
    # too few H4 bars → H4 unavailable → no trade (mandatory bias)
    assert _strategy().generate_signal(_long_range_series(), h4_frame=_h4_frame("bullish", n=10), config=_config()) is None


def test_multi_threshold_overshoot_trigger_is_skipped() -> None:
    # identical bullish setup, but the trigger crossed >1 threshold (violent spike)
    bars = _long_range_series(trigger_thresholds=2)
    assert _strategy().generate_signal(bars, h4_frame=_h4_frame("bullish"), config=_config()) is None


def test_usd_jpy_only() -> None:
    bars = _long_range_series(instrument="EUR_USD")
    with pytest.raises(ValueError, match="USD_JPY-only"):
        _strategy().generate_signal(bars, h4_frame=_h4_frame("bullish"), config=_config())


def test_no_same_bar_fill_provenance() -> None:
    sig = _strategy().generate_signal(_long_range_series(), h4_frame=_h4_frame("bullish"), config=_config())
    assert sig is not None
    trigger_close = _DECISION
    # decision/cutoff/source all anchored to the trigger close; entry deferred.
    assert sig.timestamp == trigger_close
    assert sig.decision_time == trigger_close
    assert sig.available_data_cutoff == trigger_close
    assert sig.source_candle_timestamp == trigger_close
    assert sig.entry_intent == "market"  # filled at NEXT range-bar open by the engine
    assert sig.take_profit_price is None  # no profit target (precommit §6)


def test_htf_context_has_no_lookahead() -> None:
    # an extreme bearish H4 bar that closes AFTER the decision must be ignored.
    sig = _strategy().generate_signal(
        _long_range_series(), h4_frame=_h4_frame("bullish", extra_future=True), config=_config()
    )
    assert sig is not None
    assert sig.side == "long"  # future bearish bar did not flip the bias
    assert sig.htf_feature_times is not None
    assert sig.htf_feature_times["h4"] <= sig.decision_time
    assert validate_signal_provenance(sig) == []  # every htf feature time <= decision


def test_signal_generation_is_deterministic() -> None:
    s = _strategy()
    a = s.generate_signal(_long_range_series(), h4_frame=_h4_frame("bullish"), config=_config())
    b = s.generate_signal(_long_range_series(), h4_frame=_h4_frame("bullish"), config=_config())
    assert a is not None and b is not None
    assert a.signal_id == b.signal_id
    assert a.stop_price == b.stop_price
    assert a.side == b.side


def test_optional_d1agg_blocks_when_opposing() -> None:
    # bullish H4 long trigger, but a bearish D1AGG that opposes long → blocked.
    d1 = _h4_frame("bearish")  # reuse: a falling daily series → not_bullish_only
    sig = _strategy().generate_signal(
        _long_range_series(), h4_frame=_h4_frame("bullish"), d1agg_frame=d1, config=_config()
    )
    assert sig is None


def test_optional_d1agg_absent_is_permitted() -> None:
    sig = _strategy().generate_signal(
        _long_range_series(), h4_frame=_h4_frame("bullish"), d1agg_frame=None, config=_config()
    )
    assert sig is not None
    assert sig.features["d1agg_applied"] is False


# --------------------------------------------------------------------------- #
# scaffold-safety invariants
# --------------------------------------------------------------------------- #
def test_live_trading_is_refused() -> None:
    with pytest.raises(LiveTradingRefused):
        _strategy().for_live_trading()


def test_module_has_no_broker_or_executor_imports() -> None:
    import ast

    tree = ast.parse(_SRC)
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    joined = " ".join(modules).lower()
    for forbidden in ("oanda", "executor", "broker", "order", "requests", "http"):
        assert forbidden not in joined, f"scaffold must not import {forbidden!r} (imports: {modules})"


def test_strategy_not_registered_in_loop_registry() -> None:
    # deliberate scaffold boundary: range bars are not a Granularity, so this
    # module is NOT exported from strategies/__init__ and cannot reach a loop.
    init_src = (_REPO_ROOT / "src" / "forex_bot" / "strategies" / "__init__.py").read_text(encoding="utf-8")
    assert "usdjpy_range_bar_mtf_breakout" not in init_src
    assert "UsdJpyRangeBarMtfBreakoutStrategy" not in init_src

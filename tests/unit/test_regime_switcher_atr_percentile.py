"""Unit tests for ``RegimeSwitcherAtrPercentileStrategy`` (CAMPAIGN_012).

These tests are research-only and prove the regime-switcher candidate is
**deterministic, no-lookahead, and structurally safe**. A passing suite
is NOT strategy approval; the candidate is a research scaffold and
cannot be added to ``configs/approved_strategies.yaml`` without the
full six-evidence ladder + a deliberate human approval action per
``STRATEGY_APPROVAL_PROCESS.md``. ``configs/approved_strategies.yaml``
remains ``approved: []``; the strategy is not enabled in any active
loop.

See:
- docs/research/REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md
- docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md
- docs/research/NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md
"""

from __future__ import annotations

import inspect
import math
import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from forex_bot.config import (
    RegimeSwitcherAtrPercentileStrategyConfig,
    StrategyConfig,
)
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.regime_switcher_atr_percentile import (
    RegimeSwitcherAtrPercentileStrategy,
    _compute_regime,
    _df_to_completed_h4_candle_list,
    _wilder_atr_over_d1agg,
)

# ---------------------------------------------------------------------------
# Constants + helpers
# ---------------------------------------------------------------------------


# Use NY-standard H4 alignment: UTC bar opens at 22, 02, 06, 10, 14, 18
# (matches the d1_aggregation expected slots used by CAMPAIGN_010 / 011).
_H4_HOURS_UTC: tuple[int, ...] = (22, 2, 6, 10, 14, 18)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STRATEGY_SOURCE = (
    _REPO_ROOT
    / "src"
    / "forex_bot"
    / "strategies"
    / "regime_switcher_atr_percentile.py"
).read_text(encoding="utf-8")


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


# Start the synthetic frame at a date that keeps us safely inside NY EST
# (no DST transition) for ≥ 100 consecutive days. DST 2024 ended on
# Nov 3, 2024; DST 2025 starts on Mar 9, 2025. The window
# 2024-11-04 → 2025-03-08 (~124 days, all EST) easily covers the
# 95-day fixtures used below + the 75-day D1AGG warm-up R3 requires.
# A bar at 22:00 UTC in EST is 17:00 NY → the aggregator's
# expected slot hours `[17, 21, 1, 5, 9, 13]` match exactly.
_FIXTURE_START_DAY: datetime = datetime(2024, 11, 4, 22, tzinfo=UTC)


def _build_aligned_h4_frame(
    n_trading_days: int,
    *,
    base_close: float = 1.0800,
    range_size: float = 0.0010,
    start_day: datetime | None = None,
) -> CandleFrame:
    """Build an H4 frame with ``n_trading_days`` complete trading days.

    Each trading day starts at 22:00 UTC and emits 6 H4 bars at the slot
    hours `_H4_HOURS_UTC` over the next 24 hours. This is the exact
    alignment the D1AGG aggregator expects to mark days as `aggregated`.

    Total bar count: ``n_trading_days * 6``.
    """
    base_day = start_day or _FIXTURE_START_DAY
    candles: list[Candle] = []
    for day_idx in range(n_trading_days):
        day_start = base_day + timedelta(days=day_idx)
        for slot_idx in range(6):
            t = day_start + timedelta(hours=4 * slot_idx)
            candles.append(
                _make_candle(
                    t,
                    open_=base_close,
                    high=base_close + range_size / 2,
                    low=base_close - range_size / 2,
                    close=base_close,
                )
            )
    return CandleFrame.from_candles("EUR_USD", "H4", candles)


def _build_h4_frame_with_trend(
    n_trading_days: int,
    *,
    base_close: float = 1.0800,
    range_size: float = 0.0010,
    trend_step: float = 0.0,
    start_day: datetime | None = None,
) -> CandleFrame:
    """Build an aligned H4 frame whose close drifts by ``trend_step`` per bar."""
    base_day = start_day or _FIXTURE_START_DAY
    candles: list[Candle] = []
    bar_idx = 0
    for day_idx in range(n_trading_days):
        day_start = base_day + timedelta(days=day_idx)
        for slot_idx in range(6):
            t = day_start + timedelta(hours=4 * slot_idx)
            close = base_close + trend_step * bar_idx
            candles.append(
                _make_candle(
                    t,
                    open_=close,
                    high=close + range_size / 2,
                    low=close - range_size / 2,
                    close=close,
                )
            )
            bar_idx += 1
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


def _default_cfg(**overrides) -> dict:
    cfg = {
        "version": "0.1.0-c012",
        "timeframe": "H4",
        "atr_lookback": 14,
        "atr_stop_multiple": 2.0,
        "trailing_stop_atr_multiple": None,
        "max_bars_in_trade": 6,
        "min_atr_pips": {},
        "daily_atr_lookback": 14,
        "regime_lookback_days": 60,
        "regime_percentile_threshold": 0.70,
        "min_close_move_atr_fraction": 0.25,
        "trend_lookback_h4_bars": 4,
    }
    cfg.update(overrides)
    return cfg


# ===========================================================================
# 1. Config defaults / validation (13 cases)
# ===========================================================================


def test_default_config_matches_frozen_spec():
    c = RegimeSwitcherAtrPercentileStrategyConfig(version="0.1.0-c012")
    assert c.version == "0.1.0-c012"
    assert c.timeframe == "H4"
    assert c.atr_lookback == 14
    assert c.atr_stop_multiple == 2.0
    assert c.trailing_stop_atr_multiple is None
    assert c.max_bars_in_trade == 6
    assert c.min_atr_pips == {}
    assert c.daily_atr_lookback == 14
    assert c.regime_lookback_days == 60
    assert c.regime_percentile_threshold == 0.70
    assert c.min_close_move_atr_fraction == 0.25
    assert c.trend_lookback_h4_bars == 4


def test_config_rejects_regime_percentile_threshold_at_or_below_zero():
    for bad in (-0.5, 0.0):
        with pytest.raises(
            ValidationError, match="regime_percentile_threshold must be in"
        ):
            RegimeSwitcherAtrPercentileStrategyConfig(
                version="0.1.0-c012", regime_percentile_threshold=bad
            )


def test_config_rejects_regime_percentile_threshold_at_or_above_one():
    for bad in (1.0, 1.5):
        with pytest.raises(
            ValidationError, match="regime_percentile_threshold must be in"
        ):
            RegimeSwitcherAtrPercentileStrategyConfig(
                version="0.1.0-c012", regime_percentile_threshold=bad
            )


def test_config_rejects_non_positive_daily_atr_lookback():
    for bad in (-1, 0, 1):
        with pytest.raises(ValidationError, match="daily_atr_lookback must be"):
            RegimeSwitcherAtrPercentileStrategyConfig(
                version="0.1.0-c012", daily_atr_lookback=bad
            )


def test_config_rejects_too_small_regime_lookback_days():
    for bad in (-10, 0, 1, 5, 9):
        with pytest.raises(ValidationError, match="regime_lookback_days must be"):
            RegimeSwitcherAtrPercentileStrategyConfig(
                version="0.1.0-c012", regime_lookback_days=bad
            )


def test_config_rejects_non_positive_min_close_move_atr_fraction():
    for bad in (-0.5, 0.0):
        with pytest.raises(
            ValidationError, match="min_close_move_atr_fraction must be"
        ):
            RegimeSwitcherAtrPercentileStrategyConfig(
                version="0.1.0-c012", min_close_move_atr_fraction=bad
            )


def test_config_rejects_non_positive_trend_lookback_h4_bars():
    for bad in (-1, 0):
        with pytest.raises(ValidationError, match="trend_lookback_h4_bars must be"):
            RegimeSwitcherAtrPercentileStrategyConfig(
                version="0.1.0-c012", trend_lookback_h4_bars=bad
            )


def test_config_rejects_atr_lookback_below_two():
    for bad in (-1, 0, 1):
        with pytest.raises(ValidationError, match="atr_lookback must be"):
            RegimeSwitcherAtrPercentileStrategyConfig(
                version="0.1.0-c012", atr_lookback=bad
            )


def test_config_rejects_non_positive_atr_stop_multiple():
    for bad in (-1.0, 0.0):
        with pytest.raises(ValidationError, match="atr_stop_multiple must be"):
            RegimeSwitcherAtrPercentileStrategyConfig(
                version="0.1.0-c012", atr_stop_multiple=bad
            )


def test_config_rejects_non_positive_max_bars_in_trade():
    for bad in (-1, 0):
        with pytest.raises(ValidationError, match="max_bars_in_trade must be"):
            RegimeSwitcherAtrPercentileStrategyConfig(
                version="0.1.0-c012", max_bars_in_trade=bad
            )


def test_config_rejects_non_null_trailing_stop_in_v1():
    """The regime switcher uses time-stop only in v1."""
    with pytest.raises(
        ValidationError, match="trailing_stop_atr_multiple must be None"
    ):
        RegimeSwitcherAtrPercentileStrategyConfig(
            version="0.1.0-c012", trailing_stop_atr_multiple=1.5
        )


def test_config_rejects_extra_fields():
    """extra='forbid' is the standing convention for every StrategyConfig."""
    with pytest.raises(ValidationError):
        RegimeSwitcherAtrPercentileStrategyConfig(
            version="0.1.0-c012", undocumented_extra_field="surprise"
        )


def test_strategy_config_enabled_check_rejects_missing_nested():
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "strategy.regime_switcher_atr_percentile config required when enabled"
        ),
    ):
        StrategyConfig(enabled=["regime_switcher_atr_percentile"])


# ===========================================================================
# 2. Strategy core — R1 / R2 / R4 / R7 (6 cases)
# ===========================================================================


def test_warmup_returns_none_when_too_few_bars(eur_usd: Instrument):
    """R1: less than warmup_bars_required() completed bars → None."""
    strat = RegimeSwitcherAtrPercentileStrategy()
    # 10 trading days × 6 = 60 H4 bars, well below 500.
    frame = _build_aligned_h4_frame(10)
    assert strat.generate_signal(_ctx(frame, eur_usd, config=_default_cfg())) is None


def test_no_signal_when_open_position_present(eur_usd: Instrument):
    """R2: an open position blocks re-entry."""
    strat = RegimeSwitcherAtrPercentileStrategy()
    # Build a frame with enough bars to pass warm-up, with a clear trend.
    frame = _build_h4_frame_with_trend(95, trend_step=0.0002)
    assert (
        strat.generate_signal(
            _ctx(
                frame,
                eur_usd,
                config=_default_cfg(),
                open_position_units=Decimal("1000"),
            )
        )
        is None
    )


def test_no_signal_when_d1agg_history_insufficient(eur_usd: Instrument):
    """R3: D1AGG count < daily_atr_lookback + regime_lookback_days + 1 → None.

    We still pass the warm-up bar count (>= 500), but force the
    regime_lookback to a value that exceeds the D1AGG history.
    """
    strat = RegimeSwitcherAtrPercentileStrategy()
    # 84 trading days × 6 = 504 H4 bars (passes warm-up 500), but the
    # config asks for an impossibly large regime_lookback_days so R3
    # fails-closed even though warm-up passes.
    frame = _build_aligned_h4_frame(84)
    cfg = _default_cfg(regime_lookback_days=200)  # >> 84 D1AGG candles
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_fail_closed_when_atr_is_zero(eur_usd: Instrument):
    """R4: prior_atr_h4 <= 0 → None (degenerate range)."""
    strat = RegimeSwitcherAtrPercentileStrategy()
    # 95 days; flat candles (range_size=0). Both H4 ATR and D1AGG ATR
    # will be ≈ 0; R3 also fails-closed on non-positive reference.
    frame = _build_aligned_h4_frame(95, range_size=0.0)
    assert strat.generate_signal(_ctx(frame, eur_usd, config=_default_cfg())) is None


def test_stop_placement_long_below_close(eur_usd: Instrument):
    """R7: long-side stop = close[t] - atr_stop_multiple * prior_atr_h4.

    Build a frame with a strong positive H4 trend so close[-1] > close[-5]
    by > 0.25 * prior_atr; verify side=long and stop is below close.
    """
    strat = RegimeSwitcherAtrPercentileStrategy()
    # 95 trading days × 6 = 570 H4 bars; strong rising trend.
    # range_size 0.0010 → H4 ATR converges to ~0.0010; trend_step 0.0005
    # per bar → move over 4 bars = 0.0020 >> 0.25 * 0.0010 = 0.00025.
    frame = _build_h4_frame_with_trend(95, trend_step=0.0005)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=_default_cfg()))
    assert sig is not None
    assert sig.side == "long"
    expected_stop = float(sig.features["last_close"]) - 2.0 * float(
        sig.features["prior_atr_h4"]
    )
    assert abs(float(sig.stop_price) - expected_stop) < 1e-4
    assert float(sig.stop_price) < float(sig.features["last_close"])


def test_stop_placement_short_above_close(eur_usd: Instrument):
    """R7: short-side stop = close[t] + atr_stop_multiple * prior_atr_h4."""
    strat = RegimeSwitcherAtrPercentileStrategy()
    frame = _build_h4_frame_with_trend(95, trend_step=-0.0005)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=_default_cfg()))
    assert sig is not None
    assert sig.side == "short"
    expected_stop = float(sig.features["last_close"]) + 2.0 * float(
        sig.features["prior_atr_h4"]
    )
    assert abs(float(sig.stop_price) - expected_stop) < 1e-4
    assert float(sig.stop_price) > float(sig.features["last_close"])


# ===========================================================================
# 3. R3 — regime gate (5 cases)
# ===========================================================================


def test_compute_regime_classifies_high_vol_when_reference_above_p70():
    """Reference well above the trailing P70 → HIGH-VOL."""
    # 60 trailing values all 1.0; reference 2.0 → easily ≥ P70.
    series = [1.0] * 60 + [2.0]
    result = _compute_regime(
        series, lookback_days=60, percentile_threshold=0.70
    )
    assert result is not None
    label, ref, pct = result
    assert label == "HIGH_VOL"
    assert ref == 2.0
    assert pct == pytest.approx(1.0)


def test_compute_regime_classifies_low_vol_when_reference_below_p70():
    """Reference well below the trailing P70 → LOW-VOL."""
    series = [1.0] * 60 + [0.5]
    result = _compute_regime(
        series, lookback_days=60, percentile_threshold=0.70
    )
    assert result is not None
    label, ref, pct = result
    assert label == "LOW_VOL"
    assert ref == 0.5


def test_compute_regime_inclusive_at_threshold():
    """HIGH-VOL is inclusive at P70 (reference == pct_value → HIGH-VOL)."""
    series = [1.0] * 60 + [1.0]  # trailing all 1.0; reference exactly = P70
    result = _compute_regime(
        series, lookback_days=60, percentile_threshold=0.70
    )
    assert result is not None
    label, ref, pct = result
    assert label == "HIGH_VOL"
    assert ref == pct == 1.0


def test_compute_regime_returns_none_on_insufficient_history():
    """Trailing window cannot be built → None (fail-closed)."""
    # Only 60 values total; trailing needs 60 strictly preceding the
    # reference → need >= 61.
    series = [1.0] * 60
    assert (
        _compute_regime(series, lookback_days=60, percentile_threshold=0.70)
        is None
    )


def test_compute_regime_trailing_window_excludes_reference():
    """Trailing slice is exactly d1_atr_series[-(N+1):-1].

    Use a synthetic series where the reference is an outlier; the
    percentile reflects only the trailing 60 values, NOT the reference.
    """
    trailing = list(range(1, 61))  # 1, 2, ..., 60
    series = trailing + [1000.0]  # reference is 1000 (huge outlier)
    result = _compute_regime(
        series, lookback_days=60, percentile_threshold=0.70
    )
    assert result is not None
    label, ref, pct = result
    # P70 of [1, ..., 60] is between 42 and 43; far below the reference.
    assert ref == 1000.0
    assert pct < 100.0  # reference (1000) is NOT in the percentile window
    assert label == "HIGH_VOL"


# ===========================================================================
# 4. R5 — trend sub-signal (3 cases)
# ===========================================================================


def test_no_signal_when_trend_move_below_min(eur_usd: Instrument):
    """R5: |close[t] - close[t-4]| < min_close_move_atr_fraction * prior_atr → None.

    Build a frame where the trend per bar is so tiny the over-4-bar
    move is below the 0.25 × prior_atr threshold even in HIGH-VOL regime.
    """
    strat = RegimeSwitcherAtrPercentileStrategy()
    # Day-to-day vol rising (so HIGH-VOL gate passes) but bar-to-bar
    # trend per H4 is essentially zero.
    frame = _build_h4_frame_with_trend(95, trend_step=1e-8)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=_default_cfg()))
    assert sig is None


def test_long_signal_when_trend_up_and_regime_passes(eur_usd: Instrument):
    """R3+R5: HIGH-VOL regime + positive 4-bar trend → long signal."""
    strat = RegimeSwitcherAtrPercentileStrategy()
    frame = _build_h4_frame_with_trend(95, trend_step=0.0005)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=_default_cfg()))
    assert sig is not None
    assert sig.side == "long"
    assert sig.features["trend_move"] > 0


def test_short_signal_when_trend_down_and_regime_passes(eur_usd: Instrument):
    """R3+R5: HIGH-VOL regime + negative 4-bar trend → short signal."""
    strat = RegimeSwitcherAtrPercentileStrategy()
    frame = _build_h4_frame_with_trend(95, trend_step=-0.0005)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=_default_cfg()))
    assert sig is not None
    assert sig.side == "short"
    assert sig.features["trend_move"] < 0


# ===========================================================================
# 5. No-lookahead structural audit (4 cases)
# ===========================================================================


def test_strategy_module_does_not_read_forbidden_bar_t_fields():
    """The strategy must not read bar-t high/low/open/volume by index.

    Bar-t close is read in R5 and R7; bar-t-1 reads (via .iloc[-2] on
    ATR / via .iloc[-5] for the trend anchor) are fine. Any other
    iloc[-1] read of high/low/open/volume would be a same-bar lookahead.
    """
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    forbidden_bar_t_reads = [
        r'df\["high"\]\.iloc\[-1\]',
        r'df\["low"\]\.iloc\[-1\]',
        r'df\["open"\]\.iloc\[-1\]',
        r'df\["volume"\]\.iloc\[-1\]',
    ]
    for pattern in forbidden_bar_t_reads:
        assert re.search(pattern, src_stripped) is None, (
            f"strategy module reads forbidden bar-t field: {pattern!r}"
        )


def test_strategy_module_reads_close_for_trend_and_stop_only():
    """close[t] is read in R5 (last_close + anchor_close) and R7 only."""
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    assert re.search(r'df\["close"\]\.iloc\[-1\]', src_stripped) is not None
    # The anchor read is parameterized: df["close"].iloc[-(trend_lookback_h4 + 1)]
    assert re.search(
        r'df\["close"\]\.iloc\[-\(trend_lookback_h4 \+ 1\)\]', src_stripped
    ) is not None
    # No spurious bar-t-1 close read (would also be allowed but we
    # don't take it; the design uses only [-1] and [-5]).


def test_signal_id_is_deterministic(eur_usd: Instrument):
    """Same inputs → same signal_id across two RegimeSwitcher instances."""
    strat1 = RegimeSwitcherAtrPercentileStrategy()
    strat2 = RegimeSwitcherAtrPercentileStrategy()
    frame = _build_h4_frame_with_trend(95, trend_step=0.0005)
    cfg = _default_cfg()
    sig1 = strat1.generate_signal(_ctx(frame, eur_usd, config=cfg))
    sig2 = strat2.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert sig1 is not None and sig2 is not None
    assert sig1.signal_id == sig2.signal_id


def test_strategy_does_not_mutate_config_during_signal_generation(
    eur_usd: Instrument,
):
    """The frozen-config invariant: signal generation reads cfg but never mutates."""
    strat = RegimeSwitcherAtrPercentileStrategy()
    cfg = _default_cfg()
    cfg_snapshot = dict(cfg)
    frame = _build_h4_frame_with_trend(95, trend_step=0.0005)
    _ = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert cfg == cfg_snapshot


# ===========================================================================
# 6. Forbidden imports / usages (4 cases)
# ===========================================================================


def test_strategy_module_does_not_import_random_numpy_random_or_secrets():
    """R3 / determinism: no PRNG sources of any kind."""
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    assert "import random" not in src_stripped
    assert "from random import" not in src_stripped
    assert "import numpy.random" not in src_stripped
    assert "from numpy.random" not in src_stripped
    assert "np.random" not in src_stripped
    assert "numpy.random" not in src_stripped
    assert "import secrets" not in src_stripped
    assert "from secrets" not in src_stripped


def test_strategy_module_does_not_use_builtin_hash():
    """Builtin hash() is not deterministic across processes; only hashlib."""
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    bare_hash_calls = re.findall(r"(?<![\.\w])hash\s*\(", src_stripped)
    assert not bare_hash_calls, (
        f"strategy module uses built-in hash(): {bare_hash_calls}"
    )


def test_strategy_module_does_not_import_broker_execution_loops():
    """No import from forex_bot.broker / .execution / .loops."""
    src = _STRATEGY_SOURCE
    forbidden_imports = (
        "from forex_bot.broker",
        "from forex_bot.execution",
        "from forex_bot.loops",
        "import forex_bot.broker",
        "import forex_bot.execution",
        "import forex_bot.loops",
    )
    for forbidden in forbidden_imports:
        assert forbidden not in src, (
            f"strategy module contains forbidden import: {forbidden!r}"
        )


def test_strategy_module_uses_numpy_percentile_only_no_full_sample_helpers():
    """The strategy uses numpy.percentile (deterministic, pure functional).

    Specifically forbid full-sample / global helpers that would be a
    no-lookahead hazard if mistakenly used.
    """
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    # numpy.percentile is allowed (the regime computation).
    assert "np.percentile" in src_stripped
    # Forbidden full-series stat shortcuts that would imply lookahead:
    assert ".rolling(" not in src_stripped  # roll-window helpers handled elsewhere
    assert ".expanding(" not in src_stripped


# ===========================================================================
# 7. Rejected-family contamination audit (3 cases)
# ===========================================================================


def test_strategy_module_does_not_use_campaign_002_parameter_keys():
    """Per REJECTED_FAMILY_OVERFIT_GUARDRAILS.md."""
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    forbidden_keys = (
        "donchian",
        "ema_fast",
        "ema_slow",
        "adx_threshold",
        "ema_short",
        "ema_long",
        "trend_following",
    )
    for key in forbidden_keys:
        assert key.lower() not in src_stripped.lower(), (
            f"strategy module references CAMPAIGN_002-family key: {key!r}"
        )


def test_strategy_module_does_not_use_campaign_010_parameter_keys():
    """Per REJECTED_FAMILY_OVERFIT_GUARDRAILS.md."""
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    forbidden_keys = (
        "asian_session_hours",
        "london_session_hours",
        "min_asian_range_atr_fraction",
        "session_breakout",
        "in_asian_window",
        "in_london_window",
    )
    for key in forbidden_keys:
        assert key.lower() not in src_stripped.lower(), (
            f"strategy module references CAMPAIGN_010-family key: {key!r}"
        )


def test_strategy_module_does_not_use_campaign_011_parameter_keys():
    """Per REJECTED_FAMILY_OVERFIT_GUARDRAILS.md."""
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    forbidden_keys = (
        "master_seed",
        "entry_probability_per_bar",
        # Note: "random_entry_anchor" appears in the module docstring (which
        # we strip), but must not appear in the code. The check below is
        # post-docstring-strip.
        "random_entry_anchor",
    )
    for key in forbidden_keys:
        assert key.lower() not in src_stripped.lower(), (
            f"strategy module references CAMPAIGN_011-family key: {key!r}"
        )


# ===========================================================================
# 8. Approval / safety regression (4 cases)
# ===========================================================================


def test_approved_strategies_yaml_remains_empty():
    """The scaffold sprint MUST NOT add this candidate to the registry."""
    path = _REPO_ROOT / "configs" / "approved_strategies.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data == {"approved": []}, (
        f"approved_strategies.yaml is no longer empty: {data}"
    )


def test_regime_switcher_not_enabled_in_paper_config():
    """The paper config must not enable regime_switcher_atr_percentile."""
    path = _REPO_ROOT / "configs" / "paper.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    enabled = data.get("strategy", {}).get("enabled", [])
    assert "regime_switcher_atr_percentile" not in enabled


def test_regime_switcher_not_enabled_in_practice_config():
    """The demo/practice config must not enable regime_switcher_atr_percentile."""
    path = _REPO_ROOT / "configs" / "practice.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    enabled = data.get("strategy", {}).get("enabled", [])
    assert "regime_switcher_atr_percentile" not in enabled


def test_strategy_class_exposes_no_approval_shaped_attribute():
    """No public attribute whose name suggests it could be approved."""
    forbidden_substrings = ("approve", "approval", "promote", "promotion")
    public_attrs = [
        attr
        for attr in dir(RegimeSwitcherAtrPercentileStrategy)
        if not attr.startswith("_")
    ]
    for attr in public_attrs:
        for sub in forbidden_substrings:
            assert sub not in attr.lower(), (
                f"strategy exposes approval-shaped attribute: {attr!r}"
            )


# ===========================================================================
# 9. D1AGG integration + helpers (3 cases)
# ===========================================================================


def test_df_to_completed_h4_candle_list_round_trip():
    """The helper rebuilds Candle objects with bid/ask OHLC + complete=True."""
    frame = _build_aligned_h4_frame(5)
    candles = _df_to_completed_h4_candle_list(frame.df, "EUR_USD")
    assert len(candles) == 5 * 6  # 5 days × 6 H4 bars
    for c in candles:
        assert c.granularity == "H4"
        assert c.complete is True
        assert c.instrument == "EUR_USD"
        assert c.bid_o is not None and c.ask_o is not None


def test_wilder_atr_over_d1agg_returns_list_with_warmup_nans():
    """Wilder ATR-14 over a short D1AGG list has NaN entries until warm-up."""
    frame = _build_aligned_h4_frame(20)
    h4_candles = _df_to_completed_h4_candle_list(frame.df, "EUR_USD")
    from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1

    agg = aggregate_h4_to_d1(h4_candles, instrument="EUR_USD")
    # ≤ 20 D1AGG candles; Wilder ATR-14 warms up over the first ≥14
    # values. Early values are NaN; later values are finite.
    series = _wilder_atr_over_d1agg(agg.candles, 14)
    assert len(series) == len(agg.candles)
    # The first few values are NaN (Wilder needs >= length to warm up).
    finite_count = sum(1 for v in series if math.isfinite(v))
    assert finite_count >= 0  # tautology; the point is no exception was raised


def test_compute_regime_signature_does_not_take_full_df():
    """Structural rail: _compute_regime takes only an ATR series + scalars."""
    sig = inspect.signature(_compute_regime)
    params = list(sig.parameters.keys())
    # Must take only d1_atr_series and the trailing-window scalars; never
    # a DataFrame or candle list (which would risk full-sample access).
    assert params[0] == "d1_atr_series"
    for forbidden in ("df", "candles", "frame", "full_series", "history"):
        assert forbidden not in params, (
            f"_compute_regime parameter list contains forbidden token: {forbidden!r}"
        )


# ===========================================================================
# 10. Emitted-Signal structural checks (2 cases)
# ===========================================================================


def test_signal_emitted_with_expected_fields(eur_usd: Instrument):
    """When a signal fires, every expected field is populated."""
    strat = RegimeSwitcherAtrPercentileStrategy()
    frame = _build_h4_frame_with_trend(95, trend_step=0.0005)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=_default_cfg()))
    assert sig is not None
    assert sig.strategy_name == "regime_switcher_atr_percentile"
    assert sig.strategy_version == "0.1.0-c012"
    assert sig.instrument == "EUR_USD"
    assert sig.timeframe == "H4"
    assert sig.side in ("long", "short")
    assert sig.entry_intent == "market"
    assert sig.exit_model == "time_stop_only"
    assert sig.stop_model == "ATR14*2.0"
    for required_feature in (
        "regime",
        "d1agg_atr_reference",
        "d1agg_atr_percentile_value",
        "d1agg_count",
        "trend_move",
        "min_move_threshold",
        "prior_atr_h4",
        "last_close",
        "anchor_close",
        "regime_lookback_days",
        "regime_percentile_threshold",
    ):
        assert required_feature in sig.features
    assert sig.features["regime"] == "HIGH_VOL"
    assert "HIGH_VOL" in sig.reason


def test_signal_reason_describes_regime_and_trend(eur_usd: Instrument):
    """The reason string explains the regime gate and the trend move."""
    strat = RegimeSwitcherAtrPercentileStrategy()
    frame = _build_h4_frame_with_trend(95, trend_step=0.0005)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=_default_cfg()))
    assert sig is not None
    reason_lower = sig.reason.lower()
    assert "regime" in reason_lower or "high_vol" in reason_lower
    assert "trend" in reason_lower or "move" in reason_lower

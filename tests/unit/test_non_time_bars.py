"""Unit tests for non-time-based bar construction (range + volatility bars).

Covers correctness, provenance, determinism, ordering/duplicate handling,
multi-threshold crossing, both volatility proxies, ATR-scaled prior-only
thresholds, price-basis behaviour, and explicit no-lookahead (causal-prefix)
assertions. See docs/research/RANGE_BAR_CONSTRUCTION_SPEC.md and
docs/research/VOLATILITY_BAR_CONSTRUCTION_SPEC.md.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from forex_bot.data.non_time_bars import (
    RangeBarConfig,
    VolatilityBarConfig,
    build_range_bars,
    build_volatility_bars,
    pip_size,
)
from forex_bot.domain.candles import Candle

T0 = datetime(2024, 1, 1, tzinfo=UTC)


def mk(
    i: int,
    o: str,
    h: str,
    low: str,
    c: str,
    *,
    instrument: str = "EUR_USD",
    bid: tuple[str, str, str, str] | None = None,
    ask: tuple[str, str, str, str] | None = None,
    volume: int = 1,
    minute: int | None = None,
) -> Candle:
    """Build an M1 candle with mid OHLC (and optional bid/ask) from strings."""
    kwargs: dict = dict(
        instrument=instrument,
        granularity="M1",
        time=T0 + timedelta(minutes=i if minute is None else minute),
        complete=True,
        volume=volume,
        mid_o=Decimal(o),
        mid_h=Decimal(h),
        mid_l=Decimal(low),
        mid_c=Decimal(c),
    )
    if bid is not None:
        kwargs.update(bid_o=Decimal(bid[0]), bid_h=Decimal(bid[1]), bid_l=Decimal(bid[2]), bid_c=Decimal(bid[3]))
    if ask is not None:
        kwargs.update(ask_o=Decimal(ask[0]), ask_h=Decimal(ask[1]), ask_l=Decimal(ask[2]), ask_c=Decimal(ask[3]))
    return Candle(**kwargs)


# --------------------------------------------------------------------------- #
# pip conversion
# --------------------------------------------------------------------------- #


def test_pip_size_jpy_vs_non_jpy():
    assert pip_size("USD_JPY") == Decimal("0.01")
    assert pip_size("EUR_JPY") == Decimal("0.01")
    assert pip_size("EUR_USD") == Decimal("0.0001")
    assert pip_size("GBP_USD") == Decimal("0.0001")


# --------------------------------------------------------------------------- #
# Range bars — completion + OHLC
# --------------------------------------------------------------------------- #


def test_range_bar_fixed_pip_completion_non_jpy():
    rows = [
        mk(0, "1.0000", "1.0003", "0.9999", "1.0002"),
        mk(1, "1.0002", "1.0007", "1.0001", "1.0006"),
        mk(2, "1.0006", "1.0011", "1.0005", "1.0010"),
    ]
    bars = build_range_bars(rows, RangeBarConfig(instrument="EUR_USD", threshold_pips=10))
    assert len(bars) == 1
    bar = bars[0]
    assert bar.completion_reason == "range_up"
    assert bar.open == pytest.approx(1.0000)
    assert bar.high == pytest.approx(1.0011)  # true M1 extreme incl. overshoot
    assert bar.low == pytest.approx(0.9999)
    assert bar.close == pytest.approx(1.0010)
    assert bar.source_count == 3
    assert bar.thresholds_crossed == 1
    assert bar.overshoot_pips == pytest.approx(1.0)  # up_span 11 - threshold 10


def test_range_bar_jpy_pip_conversion():
    rows = [
        mk(0, "150.00", "150.05", "149.99", "150.04", instrument="USD_JPY"),
        mk(1, "150.04", "150.11", "150.03", "150.10", instrument="USD_JPY"),
    ]
    bars = build_range_bars(rows, RangeBarConfig(instrument="USD_JPY", threshold_pips=10))
    assert len(bars) == 1
    bar = bars[0]
    # up_span = (150.11 - 150.00) / 0.01 = 11 pips >= 10
    assert bar.completion_reason == "range_up"
    assert bar.thresholds_crossed == 1
    assert bar.overshoot_pips == pytest.approx(1.0)


def test_range_bar_down_completion_reason():
    rows = [
        mk(0, "1.0000", "1.0001", "0.9999", "1.0000"),
        mk(1, "1.0000", "1.0001", "0.9989", "0.9990"),  # down 11 pips
    ]
    bars = build_range_bars(rows, RangeBarConfig(instrument="EUR_USD", threshold_pips=10))
    assert len(bars) == 1
    assert bars[0].completion_reason == "range_down"
    assert bars[0].low == pytest.approx(0.9989)


def test_range_bar_ohlc_and_provenance_fields():
    rows = [
        mk(0, "1.0000", "1.0004", "0.9998", "1.0003", volume=5),
        mk(1, "1.0003", "1.0012", "1.0002", "1.0011", volume=7),
    ]
    bars = build_range_bars(rows, RangeBarConfig(instrument="EUR_USD", threshold_pips=10))
    assert len(bars) == 1
    bar = bars[0]
    assert bar.instrument == "EUR_USD"
    assert bar.price_basis == "mid"
    assert bar.threshold_pips == 10.0
    assert bar.volume == 12
    assert bar.open_time == T0
    assert bar.close_time == T0 + timedelta(minutes=1)
    assert bar.time == bar.close_time  # canonical timestamp
    assert bar.source_start_time == T0
    assert bar.source_end_time == T0 + timedelta(minutes=1)
    assert bar.source_count == 2
    assert bar.incomplete is False


def test_range_bar_multiple_thresholds_one_candle_deterministic():
    # A single 38-pip M1 candle with a 10-pip threshold: one bar, overshoot recorded.
    rows = [mk(0, "1.0000", "1.0038", "1.0000", "1.0038")]
    bars = build_range_bars(rows, RangeBarConfig(instrument="EUR_USD", threshold_pips=10))
    assert len(bars) == 1
    bar = bars[0]
    assert bar.source_count == 1
    assert bar.thresholds_crossed == 3  # floor(38 / 10)
    assert bar.overshoot_pips == pytest.approx(28.0)
    # Deterministic: identical re-run yields identical record.
    again = build_range_bars(rows, RangeBarConfig(instrument="EUR_USD", threshold_pips=10))
    assert again == bars


# --------------------------------------------------------------------------- #
# Range bars — incomplete final bar
# --------------------------------------------------------------------------- #


def test_incomplete_final_bar_dropped_by_default():
    rows = [
        mk(0, "1.0000", "1.0011", "0.9999", "1.0010"),  # completes one 10-pip bar
        mk(1, "1.0010", "1.0013", "1.0009", "1.0012"),  # only 3 pips — incomplete
    ]
    bars = build_range_bars(rows, RangeBarConfig(instrument="EUR_USD", threshold_pips=10))
    assert len(bars) == 1
    assert all(not b.incomplete for b in bars)


def test_incomplete_final_bar_emitted_when_configured():
    rows = [
        mk(0, "1.0000", "1.0011", "0.9999", "1.0010"),
        mk(1, "1.0010", "1.0013", "1.0009", "1.0012"),
    ]
    bars = build_range_bars(
        rows, RangeBarConfig(instrument="EUR_USD", threshold_pips=10, emit_incomplete_final=True)
    )
    assert len(bars) == 2
    assert bars[-1].incomplete is True
    assert bars[-1].completion_reason == "incomplete"
    assert bars[-1].thresholds_crossed == 0


# --------------------------------------------------------------------------- #
# Determinism + ordering + duplicates
# --------------------------------------------------------------------------- #


def _ramp(n: int) -> list[Candle]:
    rows = []
    price = Decimal("1.0000")
    for i in range(n):
        o = price
        h = price + Decimal("0.0004")
        low = price - Decimal("0.0002")
        c = price + Decimal("0.0003")
        rows.append(mk(i, str(o), str(h), str(low), str(c)))
        price = c
    return rows


def test_deterministic_output_same_input():
    rows = _ramp(50)
    cfg = RangeBarConfig(instrument="EUR_USD", threshold_pips=10)
    assert build_range_bars(rows, cfg) == build_range_bars(rows, cfg)


def test_unsorted_input_rejected_by_default():
    rows = [mk(0, "1.0000", "1.0001", "0.9999", "1.0000"), mk(0, "1.0000", "1.0001", "0.9999", "1.0000", minute=-1)]
    with pytest.raises(ValueError, match="not sorted"):
        build_range_bars(rows, RangeBarConfig(instrument="EUR_USD", threshold_pips=10))


def test_unsorted_input_sorted_when_allowed():
    a = mk(0, "1.0000", "1.0001", "0.9999", "1.0000")
    b = mk(1, "1.0000", "1.0012", "1.0000", "1.0011", minute=1)
    # Provide reversed; allow unsorted -> should sort and complete a bar.
    bars = build_range_bars(
        [b, a], RangeBarConfig(instrument="EUR_USD", threshold_pips=10, require_sorted=False)
    )
    assert len(bars) == 1
    assert bars[0].open_time == T0


def test_duplicate_timestamps_rejected_by_default():
    rows = [mk(0, "1.0000", "1.0001", "0.9999", "1.0000"), mk(0, "1.0000", "1.0001", "0.9999", "1.0000")]
    with pytest.raises(ValueError, match="duplicate"):
        build_range_bars(rows, RangeBarConfig(instrument="EUR_USD", threshold_pips=10))


def test_duplicate_timestamps_keep_last():
    a = mk(0, "1.0000", "1.0001", "0.9999", "1.0000")
    dup = mk(0, "1.0000", "1.0012", "1.0000", "1.0011")  # same ts, bigger range
    bars = build_range_bars(
        [a, dup],
        RangeBarConfig(instrument="EUR_USD", threshold_pips=10, duplicate_policy="keep_last"),
    )
    assert len(bars) == 1
    assert bars[0].high == pytest.approx(1.0012)


def test_mixed_instruments_rejected():
    rows = [mk(0, "1.0000", "1.0001", "0.9999", "1.0000"), mk(1, "1.0000", "1.0012", "1.0000", "1.0011", instrument="GBP_USD")]
    with pytest.raises(ValueError, match="do not match"):
        build_range_bars(rows, RangeBarConfig(instrument="EUR_USD", threshold_pips=10))


def test_empty_input_returns_empty():
    assert build_range_bars([], RangeBarConfig(instrument="EUR_USD", threshold_pips=10)) == []
    assert build_volatility_bars([], VolatilityBarConfig(instrument="EUR_USD", threshold_pips=10)) == []


# --------------------------------------------------------------------------- #
# No-lookahead: causal prefix property
# --------------------------------------------------------------------------- #


def test_range_bars_causal_prefix_no_future_leak():
    rows = _ramp(80)
    cfg = RangeBarConfig(instrument="EUR_USD", threshold_pips=10)
    full = build_range_bars(rows, cfg)
    for k in range(1, len(rows) + 1):
        partial = build_range_bars(rows[:k], cfg)
        # Every completed bar from the prefix must equal the corresponding full bar
        # (a completed bar never changes when future rows arrive).
        assert partial == full[: len(partial)]


def test_volatility_bars_causal_prefix_no_future_leak():
    rows = _ramp(80)
    cfg = VolatilityBarConfig(instrument="EUR_USD", method="abs_close", threshold_pips=15)
    full = build_volatility_bars(rows, cfg)
    for k in range(1, len(rows) + 1):
        partial = build_volatility_bars(rows[:k], cfg)
        assert partial == full[: len(partial)]


# --------------------------------------------------------------------------- #
# Price basis behaviour
# --------------------------------------------------------------------------- #


def test_price_basis_bid_ask_mid():
    rows = [
        mk(
            0,
            "1.0000",
            "1.0011",
            "1.0000",
            "1.0010",
            bid=("0.9999", "1.0010", "0.9999", "1.0009"),
            ask=("1.0001", "1.0012", "1.0001", "1.0011"),
        )
    ]
    for basis, expected_open, expected_high in (
        ("bid", 0.9999, 1.0010),
        ("ask", 1.0001, 1.0012),
        ("mid", 1.0000, 1.0011),
    ):
        bars = build_range_bars(
            rows, RangeBarConfig(instrument="EUR_USD", threshold_pips=10, price_basis=basis)
        )
        assert len(bars) == 1
        assert bars[0].open == pytest.approx(expected_open)
        assert bars[0].high == pytest.approx(expected_high)


def test_mid_falls_back_to_bid_ask_average():
    c = Candle(
        instrument="EUR_USD",
        granularity="M1",
        time=T0,
        complete=True,
        volume=1,
        bid_o=Decimal("1.0000"),
        bid_h=Decimal("1.0010"),
        bid_l=Decimal("1.0000"),
        bid_c=Decimal("1.0009"),
        ask_o=Decimal("1.0002"),
        ask_h=Decimal("1.0014"),
        ask_l=Decimal("1.0002"),
        ask_c=Decimal("1.0013"),
    )
    bars = build_range_bars([c], RangeBarConfig(instrument="EUR_USD", threshold_pips=10))
    assert len(bars) == 1
    assert bars[0].open == pytest.approx(1.0001)  # (1.0000 + 1.0002) / 2
    assert bars[0].high == pytest.approx(1.0012)  # (1.0010 + 1.0014) / 2


def test_missing_basis_price_raises():
    c = Candle(instrument="EUR_USD", granularity="M1", time=T0, complete=True, volume=1)
    with pytest.raises(ValueError, match="missing"):
        build_range_bars([c], RangeBarConfig(instrument="EUR_USD", threshold_pips=10, price_basis="bid"))


# --------------------------------------------------------------------------- #
# Volatility bars — proxies
# --------------------------------------------------------------------------- #


def test_volatility_abs_close_cumulative_movement():
    # Increments: |1.0002-1.0000|=2, |1.0006-1.0002|=4, |1.0010-1.0006|=4 -> 10 at row 2.
    rows = [
        mk(0, "1.0000", "1.0003", "0.9999", "1.0002"),
        mk(1, "1.0002", "1.0007", "1.0001", "1.0006"),
        mk(2, "1.0006", "1.0011", "1.0005", "1.0010"),
    ]
    bars = build_volatility_bars(
        rows, VolatilityBarConfig(instrument="EUR_USD", method="abs_close", threshold_pips=10)
    )
    assert len(bars) == 1
    bar = bars[0]
    assert bar.method == "abs_close"
    assert bar.movement_pips == pytest.approx(10.0)
    assert bar.source_count == 3
    assert bar.completion_reason == "volatility"
    assert bar.thresholds_crossed == 1
    assert bar.overshoot_pips == pytest.approx(0.0)


def test_volatility_true_range_mode():
    # TR row0 = 1.0003-0.9999 = 4 pips; TR row1 = max(1.0007-1.0001, |1.0007-1.0002|,
    # |1.0001-1.0002|) = 6 pips -> 10 at row1.
    rows = [
        mk(0, "1.0000", "1.0003", "0.9999", "1.0002"),
        mk(1, "1.0002", "1.0007", "1.0001", "1.0006"),
    ]
    bars = build_volatility_bars(
        rows, VolatilityBarConfig(instrument="EUR_USD", method="true_range", threshold_pips=10)
    )
    assert len(bars) == 1
    assert bars[0].movement_pips == pytest.approx(10.0)
    assert bars[0].source_count == 2


def test_volatility_jpy_pip_conversion():
    rows = [
        mk(0, "150.00", "150.05", "149.97", "150.04", instrument="USD_JPY"),  # TR = 8 pips
        mk(1, "150.04", "150.09", "150.03", "150.08", instrument="USD_JPY"),  # TR ~ 5 pips
    ]
    bars = build_volatility_bars(
        rows, VolatilityBarConfig(instrument="USD_JPY", method="true_range", threshold_pips=10)
    )
    assert len(bars) == 1
    assert bars[0].movement_pips >= 10.0


def test_volatility_incomplete_final_emitted_when_configured():
    rows = [mk(0, "1.0000", "1.0002", "1.0000", "1.0001")]  # only ~2 pips
    dropped = build_volatility_bars(
        rows, VolatilityBarConfig(instrument="EUR_USD", method="abs_close", threshold_pips=10)
    )
    assert dropped == []
    emitted = build_volatility_bars(
        rows,
        VolatilityBarConfig(
            instrument="EUR_USD", method="abs_close", threshold_pips=10, emit_incomplete_final=True
        ),
    )
    assert len(emitted) == 1
    assert emitted[0].incomplete is True
    assert emitted[0].completion_reason == "incomplete"


# --------------------------------------------------------------------------- #
# Volatility bars — ATR-scaled threshold uses prior completed data only
# --------------------------------------------------------------------------- #


def test_atr_scaled_uses_prior_completed_window_only():
    # Two warm-up rows with TR = 4 pips each -> ATR = 4; multiple 2 -> threshold 8.
    warm = [
        mk(0, "1.0000", "1.0002", "0.9998", "1.0001"),
        mk(1, "1.0001", "1.0003", "0.9999", "1.0002"),
    ]
    # Row 2 TR: max(1.0009-1.0001, |1.0009-1.0002|, |1.0001-1.0002|) = 8 pips -> completes.
    active = [mk(2, "1.0002", "1.0010", "1.0002", "1.0009")]
    bars = build_volatility_bars(
        warm + active,
        VolatilityBarConfig(
            instrument="EUR_USD",
            method="true_range",
            threshold_mode="atr_scaled",
            atr_multiple=2,
            atr_window=2,
        ),
    )
    assert len(bars) == 1
    assert bars[0].threshold_mode == "atr_scaled"
    assert bars[0].threshold_pips == pytest.approx(8.0)  # 2 * ATR(4) — from prior rows only
    assert bars[0].source_count == 1


def test_atr_scaled_threshold_independent_of_current_bar_rows():
    # The forming bar's own (large) TR must NOT raise its own threshold. Build a
    # version where the active bar is far more volatile than warm-up; threshold
    # must still equal multiple * warm-up ATR.
    warm = [mk(i, "1.0000", "1.0002", "0.9998", "1.0001") for i in range(3)]  # TR 4 each
    active = [mk(3, "1.0001", "1.0050", "1.0001", "1.0049")]  # TR ~ 48 pips
    bars = build_volatility_bars(
        warm + active,
        VolatilityBarConfig(
            instrument="EUR_USD",
            method="true_range",
            threshold_mode="atr_scaled",
            atr_multiple=2,
            atr_window=3,
        ),
    )
    assert len(bars) == 1
    assert bars[0].threshold_pips == pytest.approx(8.0)  # 2 * 4, NOT influenced by 48-pip row


def test_atr_scaled_warmup_emits_no_bars():
    warm = [mk(i, "1.0000", "1.0002", "0.9998", "1.0001") for i in range(2)]
    bars = build_volatility_bars(
        warm,
        VolatilityBarConfig(
            instrument="EUR_USD",
            method="true_range",
            threshold_mode="atr_scaled",
            atr_multiple=2,
            atr_window=5,  # never satisfied
        ),
    )
    assert bars == []


# --------------------------------------------------------------------------- #
# Config validation
# --------------------------------------------------------------------------- #


def test_config_validation_errors():
    with pytest.raises(ValueError):
        RangeBarConfig(instrument="EUR_USD", threshold_pips=0)
    with pytest.raises(ValueError):
        VolatilityBarConfig(instrument="EUR_USD", threshold_mode="fixed", threshold_pips=None)
    with pytest.raises(ValueError):
        VolatilityBarConfig(instrument="EUR_USD", threshold_mode="atr_scaled", atr_multiple=2)  # no window

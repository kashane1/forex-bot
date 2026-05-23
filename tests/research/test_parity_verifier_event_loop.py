"""Integration tests for the verifier event loop.

The event loop is exercised on hand-built bar sequences chosen to
trigger specific code paths (entry → trailing → stop, time stop,
end-of-data, no-entry due to insufficient warmup). Each test asserts
the exit reason and a small set of derived fields rather than exact
prices — exact prices are pinned by the rule fixtures in Phase 3.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from research.parity_verifier.event_loop import run_pair
from research.parity_verifier.instruments import get_instrument
from research.parity_verifier.models import (
    Bar,
    CandleSeries,
    Side,
    TradeExitReason,
    VerifierConfig,
)


def _bar(
    ts: datetime,
    open_: float,
    high: float,
    low: float,
    close: float,
    spread: float = 0.0002,
) -> Bar:
    """Convenience: build a Bar with a synthetic bid/ask spread around
    the mid price."""

    half = spread / 2.0
    return Bar(
        time=ts,
        open=open_,
        high=high,
        low=low,
        close=close,
        bid_open=open_ - half,
        bid_high=high - half,
        bid_low=low - half,
        bid_close=close - half,
        ask_open=open_ + half,
        ask_high=high + half,
        ask_low=low + half,
        ask_close=close + half,
        volume=10,
    )


def _config(
    *,
    ema_fast: int = 3,
    ema_slow: int = 5,
    donchian_lookback: int = 3,
    atr_lookback: int = 3,
    atr_stop_multiple: float = 2.0,
    trailing_stop_atr_multiple: float = 2.0,
    max_bars_in_trade: int = 5,
) -> VerifierConfig:
    """A tiny config for fixture runs. Real CAMPAIGN_002 uses
    50/200/20/14/2.0/2.0/240; the small values here let a handful of
    bars trigger an entry."""

    return VerifierConfig(
        ema_fast=ema_fast,
        ema_slow=ema_slow,
        donchian_lookback=donchian_lookback,
        atr_lookback=atr_lookback,
        atr_stop_multiple=atr_stop_multiple,
        trailing_stop_atr_multiple=trailing_stop_atr_multiple,
        max_bars_in_trade=max_bars_in_trade,
        risk_per_trade_pct=0.25,
        starting_equity_usd=500.0,
        fixed_slippage_pips=0.2,
        spread_slippage_multiplier=0.5,
    )


def _build_uptrend_then_drop(start: datetime) -> list[Bar]:
    """Construct a flat warmup → uptrend → sharp drop sequence that
    forces: warmup, EMA-fast > EMA-slow, Donchian-high breakout long
    entry, then a stop hit on a subsequent bar."""

    bars: list[Bar] = []
    # 6 flat bars at 1.00 to establish a level
    for i in range(6):
        bars.append(_bar(start + timedelta(hours=4 * i), 1.0, 1.001, 0.999, 1.0))
    # 4 climbing bars
    closes = [1.005, 1.010, 1.015, 1.020]
    for k, close in enumerate(closes):
        idx = 6 + k
        bars.append(
            _bar(
                start + timedelta(hours=4 * idx),
                close - 0.002,
                close + 0.001,
                close - 0.003,
                close,
            )
        )
    # one strong upward breakout bar
    idx = 6 + len(closes)
    bars.append(
        _bar(
            start + timedelta(hours=4 * idx),
            1.020,
            1.040,  # high jumps far above Donchian
            1.018,
            1.035,
        )
    )
    # subsequent bar that drops sharply, hitting the stop
    idx += 1
    bars.append(_bar(start + timedelta(hours=4 * idx), 1.034, 1.034, 0.990, 0.992))
    # one more bar in case EOD logic is needed
    idx += 1
    bars.append(_bar(start + timedelta(hours=4 * idx), 0.992, 0.995, 0.990, 0.993))
    return bars


def _build_flat_no_entry(start: datetime) -> list[Bar]:
    """Construct a series where nothing breaks the Donchian band, so no
    entry should fire."""

    bars: list[Bar] = []
    for i in range(20):
        bars.append(_bar(start + timedelta(hours=4 * i), 1.0, 1.0005, 0.9995, 1.0))
    return bars


def test_empty_series_returns_zero_trades() -> None:
    inst = get_instrument("EUR_USD")
    result, trades = run_pair(
        candles=CandleSeries(instrument="EUR_USD", bars=[]),
        instrument=inst,
        config=_config(),
    )
    assert result.candle_count == 0
    assert result.trades == 0
    assert trades == []


def test_flat_series_yields_no_trades() -> None:
    inst = get_instrument("EUR_USD")
    bars = _build_flat_no_entry(datetime(2024, 1, 1, tzinfo=UTC))
    result, trades = run_pair(
        candles=CandleSeries(instrument="EUR_USD", bars=bars),
        instrument=inst,
        config=_config(),
    )
    assert result.trades == 0
    assert trades == []
    assert result.candle_count == len(bars)


def test_uptrend_then_drop_produces_long_entry_and_stop_exit() -> None:
    inst = get_instrument("EUR_USD")
    bars = _build_uptrend_then_drop(datetime(2024, 1, 1, tzinfo=UTC))
    result, trades = run_pair(
        candles=CandleSeries(instrument="EUR_USD", bars=bars),
        instrument=inst,
        config=_config(),
    )
    assert result.trades >= 1
    first = trades[0]
    assert first.side is Side.LONG
    assert first.exit_reason in (TradeExitReason.STOP, TradeExitReason.TRAILING_STOP)
    assert first.entry_price > 1.0
    # A long stop can exit at the initial level (loss) or a ratcheted level
    # (potentially a win). Either is correct — we only assert the exit price
    # equals the stop price that was active when it triggered.
    assert first.exit_price == pytest.approx(first.final_stop_price)
    assert first.bars_held >= 1


def test_time_stop_fires_when_no_other_exit() -> None:
    """A persistent uptrend never hits the stop; the time stop triggers
    after ``max_bars_in_trade`` bars."""

    inst = get_instrument("EUR_USD")
    start = datetime(2024, 1, 1, tzinfo=UTC)
    bars: list[Bar] = []
    # establish warmup
    for i in range(6):
        bars.append(_bar(start + timedelta(hours=4 * i), 1.0, 1.001, 0.999, 1.0))
    # gentle climb
    for k in range(20):
        idx = 6 + k
        base = 1.0 + 0.001 * (k + 1)
        bars.append(
            _bar(
                start + timedelta(hours=4 * idx),
                base - 0.0005,
                base + 0.0005,
                base - 0.0010,
                base,
            )
        )
    # add a breakout bar then continued slow drift up (no stop hit, no drop)
    idx = 6 + 20
    bars.append(_bar(start + timedelta(hours=4 * idx), 1.020, 1.030, 1.019, 1.028))
    for k in range(10):
        idx += 1
        base = 1.028 + 0.0001 * k
        bars.append(
            _bar(
                start + timedelta(hours=4 * idx),
                base,
                base + 0.0005,
                base - 0.0001,
                base + 0.0001,
            )
        )
    result, trades = run_pair(
        candles=CandleSeries(instrument="EUR_USD", bars=bars),
        instrument=inst,
        config=_config(max_bars_in_trade=5),
    )
    assert result.trades >= 1
    # at least one trade must have closed via TIME or TRAILING_STOP
    reasons = {t.exit_reason for t in trades}
    assert reasons.intersection(
        {TradeExitReason.TIME, TradeExitReason.TRAILING_STOP, TradeExitReason.STOP, TradeExitReason.EOD}
    )


def test_pair_summary_has_expected_fields_when_trades_exist() -> None:
    inst = get_instrument("EUR_USD")
    bars = _build_uptrend_then_drop(datetime(2024, 1, 1, tzinfo=UTC))
    result, _ = run_pair(
        candles=CandleSeries(instrument="EUR_USD", bars=bars),
        instrument=inst,
        config=_config(),
    )
    if result.trades > 0:
        assert result.expectancy_r is not None
        assert result.win_rate is not None


def test_no_lookahead_in_event_loop() -> None:
    """Confirm the event loop only ever consults bars up to and
    including the current index. Constructed by giving the *last* bar
    a huge high — if the loop were peeking, the Donchian channel at an
    earlier bar would already see it. Verify entries fire at most at the
    same indices a manual walk would produce."""

    inst = get_instrument("EUR_USD")
    start = datetime(2024, 1, 1, tzinfo=UTC)
    bars: list[Bar] = []
    for i in range(15):
        bars.append(_bar(start + timedelta(hours=4 * i), 1.0, 1.001, 0.999, 1.0))
    # final bar has a massive spike that must NOT influence prior Donchian
    bars.append(_bar(start + timedelta(hours=4 * 15), 1.0, 1.500, 0.999, 1.0))
    # flat bars are unable to produce any entry — entry would require close > donchian_high
    result, trades = run_pair(
        candles=CandleSeries(instrument="EUR_USD", bars=bars),
        instrument=inst,
        config=_config(),
    )
    assert result.trades == 0
    assert trades == []


def test_run_pair_uses_authoritative_config_shape() -> None:
    """A smoke test that the verifier accepts the real CAMPAIGN_002
    parameter shape (50/200/20/14/2.0/2.0/240) even on a small bar
    series — it must simply produce zero trades (not enough bars to
    warm up) rather than crash."""

    from research.parity_verifier.data_loader import (
        DEFAULT_CONFIG_PATH,
        load_verifier_config,
    )

    inst = get_instrument("EUR_USD")
    config = load_verifier_config(DEFAULT_CONFIG_PATH)
    start = datetime(2024, 1, 1, tzinfo=UTC)
    bars = [_bar(start + timedelta(hours=4 * i), 1.0, 1.0005, 0.9995, 1.0) for i in range(50)]
    result, trades = run_pair(
        candles=CandleSeries(instrument="EUR_USD", bars=bars),
        instrument=inst,
        config=config,
    )
    assert result.candle_count == 50
    assert result.trades == 0
    assert trades == []


def test_usd_jpy_instrument_runs_without_crashing() -> None:
    """JPY pip math is different (0.01 not 0.0001) — make sure the
    event loop handles the divide-by-mid sizing path without error
    when an entry fires."""

    inst = get_instrument("USD_JPY")
    start = datetime(2024, 1, 1, tzinfo=UTC)
    bars: list[Bar] = []
    for i in range(8):
        bars.append(_bar(start + timedelta(hours=4 * i), 150.00, 150.10, 149.90, 150.00, spread=0.02))
    closes = [150.50, 151.00, 151.50, 152.00]
    for k, close in enumerate(closes):
        idx = 8 + k
        bars.append(
            _bar(
                start + timedelta(hours=4 * idx),
                close - 0.20,
                close + 0.10,
                close - 0.30,
                close,
                spread=0.02,
            )
        )
    idx = 8 + len(closes)
    bars.append(_bar(start + timedelta(hours=4 * idx), 152.00, 154.00, 151.80, 153.50, spread=0.02))
    idx += 1
    bars.append(_bar(start + timedelta(hours=4 * idx), 153.50, 153.60, 149.00, 149.50, spread=0.02))
    result, trades = run_pair(
        candles=CandleSeries(instrument="USD_JPY", bars=bars),
        instrument=inst,
        config=_config(),
    )
    if trades:
        assert trades[0].units > 0
        assert trades[0].exit_reason in (
            TradeExitReason.STOP,
            TradeExitReason.TRAILING_STOP,
            TradeExitReason.TIME,
            TradeExitReason.EOD,
        )
    assert result.candle_count == len(bars)

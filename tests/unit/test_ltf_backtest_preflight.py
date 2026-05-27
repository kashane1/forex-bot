from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from forex_bot.backtesting import ltf_preflight
from forex_bot.backtesting.ltf_preflight import (
    next_bar_open_time,
    run_ltf_backtest_preflight,
    time_stop_exit_index,
)
from forex_bot.domain.candles import Candle, CandleFrame


def _frame(granularity: str = "M15", count: int = 4) -> CandleFrame:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    minutes = 15 if granularity == "M15" else 5
    candles = []
    for i in range(count):
        candles.append(
            Candle(
                instrument="EUR_USD",
                granularity=granularity,
                time=start + timedelta(minutes=minutes * i),
                complete=True,
                volume=1,
                bid_o=Decimal("1.1"),
                bid_h=Decimal("1.2"),
                bid_l=Decimal("1.0"),
                bid_c=Decimal("1.15"),
                ask_o=Decimal("1.1002"),
                ask_h=Decimal("1.2002"),
                ask_l=Decimal("1.0002"),
                ask_c=Decimal("1.1502"),
            )
        )
    return CandleFrame.from_candles("EUR_USD", granularity, candles)


def test_next_bar_open_on_m15_uses_next_m15_open() -> None:
    frame = _frame("M15", 3)
    assert next_bar_open_time(frame, datetime(2024, 1, 1, 0, tzinfo=UTC)) == datetime(2024, 1, 1, 0, 15, tzinfo=UTC)


def test_final_bar_signal_unavailable() -> None:
    frame = _frame("M15", 1)
    result = run_ltf_backtest_preflight(frame, signal_time=datetime(2024, 1, 1, tzinfo=UTC))
    assert result.ok is False
    assert "NEXT_BAR_OPEN_UNAVAILABLE" in result.errors


def test_time_stop_uses_execution_bars() -> None:
    assert time_stop_exit_index(1, time_stop_bars=2, frame_length=5) == 3


def test_time_stop_of_n_bars_not_h4_bars() -> None:
    frame = _frame("M15", 10)
    result = run_ltf_backtest_preflight(frame, time_stop_bars=4)
    assert result.time_stop_bars == 4
    assert result.execution_timeframe == "M15"


def test_risk_sizing_unchanged_no_errors_for_valid_ltf() -> None:
    frame = _frame("M15", 3)
    result = run_ltf_backtest_preflight(frame, signal_time=datetime(2024, 1, 1, tzinfo=UTC))
    assert result.ok is True


def test_module_has_no_broker_executor_imports() -> None:
    source = Path(ltf_preflight.__file__).read_text(encoding="utf-8")
    assert "forex_bot.broker" not in source
    assert "forex_bot.execution" not in source

"""Entry-bar stop policy tests for CAMPAIGN_015 BT adapter."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("backtrader")

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.backtrader_lane.data_adapter import (  # noqa: E402
    CandleAdapterResult,
)
from research.backtrader_lane.strategies.campaign_015_failed_breakout_reversal import (  # noqa: E402
    run_campaign_015_pair,
)

from tests.unit.backtrader_lane.test_campaign_015_failed_breakout_reversal import (  # noqa: E402
    _make_candles_from_ohlc,
    _quiet_range_rows,
)


def _entry_bar_adverse_long_fixture() -> CandleAdapterResult:
    """Signal long on bar 80; entry bar 81 low pierces stop."""
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    # Failed downside sweep — signal bar.
    rows.append((1.1000, 1.1010, 1.0925, 1.0990))
    # Entry bar: open near 1.10 but low pierces stop (~1.0924).
    rows.append((1.1000, 1.1010, 1.0910, 1.0995))
    # Later bar: would hit stop if position survived.
    rows.append((1.0995, 1.1000, 1.0880, 1.0890))
    for _ in range(5):
        rows.append((1.0890, 1.0900, 1.0880, 1.0890))
    return _make_candles_from_ohlc("EUR_USD", rows)


def test_backtrader_default_rejects_entry_bar_adverse_stop(monkeypatch):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    candles = _entry_bar_adverse_long_fixture()
    result = run_campaign_015_pair(
        candles,
        500.0,
        entry_bar_stop_policy="backtrader_default",
    )
    # Either no trade (rejected at entry) or immediate stop_same_bar exit.
    if result.trades:
        assert result.trades[0].exit_reason == "stop_same_bar"
    else:
        assert result.trades == []


def test_bespoke_current_accepts_entry_bar_adverse_stop(monkeypatch):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    candles = _entry_bar_adverse_long_fixture()
    result = run_campaign_015_pair(
        candles,
        500.0,
        entry_bar_stop_policy="bespoke_current_no_entry_bar_stop",
    )
    assert len(result.trades) >= 1
    first = result.trades[0]
    assert first.side == "long"
    assert first.exit_reason != "stop_same_bar"


def test_later_bar_stop_still_exits_under_bespoke_current_policy(monkeypatch):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))  # short signal
    rows.append((1.1000, 1.1020, 1.0990, 1.1010))  # entry bar — safe
    rows.append((1.1010, 1.1200, 1.1000, 1.1180))  # rally through stop
    candles = _make_candles_from_ohlc("EUR_USD", rows)
    result = run_campaign_015_pair(
        candles,
        500.0,
        entry_bar_stop_policy="bespoke_current_no_entry_bar_stop",
    )
    assert any(t.exit_reason == "stop" for t in result.trades)

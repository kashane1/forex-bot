"""Fixture tests for independent exit_logic parity."""

from __future__ import annotations

from decimal import Decimal

import pandas as pd
from research.backtrader_exit_parity.exit_logic import OpenTrade, process_bar_exit


def _row(
    *,
    bid_o, bid_h, bid_l, bid_c,
    ask_o, ask_h, ask_l, ask_c,
) -> pd.Series:
    return pd.Series(
        {
            "open": (bid_o + ask_o) / 2,
            "high": (bid_h + ask_h) / 2,
            "low": (bid_l + ask_l) / 2,
            "close": (bid_c + ask_c) / 2,
            "bid_open": bid_o,
            "bid_high": bid_h,
            "bid_low": bid_l,
            "bid_close": bid_c,
            "ask_open": ask_o,
            "ask_high": ask_h,
            "ask_low": ask_l,
            "ask_close": ask_c,
        }
    )


def _long_trade(**kwargs) -> OpenTrade:
    defaults = dict(
        side="long",
        units=100,
        entry_price=Decimal("1.1000"),
        entry_time=pd.Timestamp("2020-01-01T00:00:00Z"),
        stop_price=Decimal("1.0950"),
        initial_stop_price=Decimal("1.0950"),
        spread_pips_at_entry=Decimal("1.2"),
    )
    defaults.update(kwargs)
    return OpenTrade(**defaults)


def test_stop_exit_long():
    trade = _long_trade()
    row = _row(
        bid_o=1.101, bid_h=1.102, bid_l=1.094, bid_c=1.0955,
        ask_o=1.1012, ask_h=1.1022, ask_l=1.0942, ask_c=1.0957,
    )
    res = process_bar_exit(
        trade, row, pd.Timestamp("2020-01-02T00:00:00Z"),
        max_bars_in_trade=40, protective_stop_after_r=None, pip_size=Decimal("0.0001"),
    )
    assert res is not None
    assert res.exit_reason == "stop"
    assert res.exit_price == Decimal("1.0950")


def test_time_exit_long():
    trade = _long_trade(bars_held=39)
    row = _row(
        bid_o=1.101, bid_h=1.102, bid_l=1.100, bid_c=1.1015,
        ask_o=1.1012, ask_h=1.1022, ask_l=1.1002, ask_c=1.1017,
    )
    res = process_bar_exit(
        trade, row, pd.Timestamp("2020-01-02T00:00:00Z"),
        max_bars_in_trade=40, protective_stop_after_r=None, pip_size=Decimal("0.0001"),
    )
    assert res is not None
    assert res.exit_reason == "time"
    assert res.exit_price == Decimal("1.1015")


def test_target_exit_long():
    trade = _long_trade(take_profit_price=Decimal("1.1050"))
    row = _row(
        bid_o=1.101, bid_h=1.106, bid_l=1.100, bid_c=1.104,
        ask_o=1.1012, ask_h=1.1062, ask_l=1.1002, ask_c=1.1042,
    )
    res = process_bar_exit(
        trade, row, pd.Timestamp("2020-01-02T00:00:00Z"),
        max_bars_in_trade=40, protective_stop_after_r=None, pip_size=Decimal("0.0001"),
    )
    assert res is not None
    assert res.exit_reason == "target"
    assert res.exit_price == Decimal("1.1050")


def test_protective_stop_arms_and_exits():
    trade = _long_trade()
    # Bar 1: favorable move >= 1R; low stays above entry after BE arm
    row1 = _row(
        bid_o=1.100, bid_h=1.106, bid_l=1.1001, bid_c=1.105,
        ask_o=1.1002, ask_h=1.1062, ask_l=1.1003, ask_c=1.1052,
    )
    res1 = process_bar_exit(
        trade, row1, pd.Timestamp("2020-01-02T00:00:00Z"),
        max_bars_in_trade=40, protective_stop_after_r=1.0, pip_size=Decimal("0.0001"),
    )
    assert res1 is None
    assert trade.protective_armed is True
    assert trade.stop_price == trade.entry_price
    # Bar 2: retrace to break-even
    row2 = _row(
        bid_o=1.104, bid_h=1.1045, bid_l=1.0995, bid_c=1.100,
        ask_o=1.1042, ask_h=1.1047, ask_l=1.0997, ask_c=1.1002,
    )
    res2 = process_bar_exit(
        trade, row2, pd.Timestamp("2020-01-03T00:00:00Z"),
        max_bars_in_trade=40, protective_stop_after_r=1.0, pip_size=Decimal("0.0001"),
    )
    assert res2 is not None
    assert res2.exit_reason == "protective_stop"


def test_same_bar_stop_wins_over_target():
    trade = _long_trade(take_profit_price=Decimal("1.1050"))
    row = _row(
        bid_o=1.101, bid_h=1.106, bid_l=1.094, bid_c=1.095,
        ask_o=1.1012, ask_h=1.1062, ask_l=1.0942, ask_c=1.0952,
    )
    res = process_bar_exit(
        trade, row, pd.Timestamp("2020-01-02T00:00:00Z"),
        max_bars_in_trade=40, protective_stop_after_r=None, pip_size=Decimal("0.0001"),
    )
    assert res is not None
    assert res.exit_reason == "stop"
    assert res.ambiguous_exit is True


def test_c018_no_ratchet_after_protective_arm():
    trade = _long_trade()
    row1 = _row(
        bid_o=1.100, bid_h=1.106, bid_l=1.099, bid_c=1.105,
        ask_o=1.1002, ask_h=1.1062, ask_l=1.0992, ask_c=1.1052,
    )
    process_bar_exit(
        trade, row1, pd.Timestamp("2020-01-02T00:00:00Z"),
        max_bars_in_trade=40, protective_stop_after_r=1.0, pip_size=Decimal("0.0001"),
    )
    stop_after_arm = trade.stop_price
    # Further favorable move should NOT ratchet stop above entry (ratchet=false)
    row2 = _row(
        bid_o=1.105, bid_h=1.110, bid_l=1.104, bid_c=1.109,
        ask_o=1.1052, ask_h=1.1102, ask_l=1.1042, ask_c=1.1092,
    )
    process_bar_exit(
        trade, row2, pd.Timestamp("2020-01-03T00:00:00Z"),
        max_bars_in_trade=40, protective_stop_after_r=1.0, pip_size=Decimal("0.0001"),
    )
    assert trade.stop_price == stop_after_arm == trade.entry_price

"""Tests for scripts/trace_campaign_015_cell_bar_decisions.py."""

from __future__ import annotations

from scripts.trace_campaign_015_cell_bar_decisions import (
    BarTraceRow,
    FirstDivergenceKind,
    classify_first_divergence,
    slice_trace_window,
)


def _row(**kwargs: object) -> BarTraceRow:
    base = dict(
        timestamp="2022-05-06T13:00:00+00:00",
        pair="AUD_USD",
        fold=1,
        in_test_window=True,
        csv_mid_open=0.71,
        csv_mid_high=0.72,
        csv_mid_low=0.70,
        csv_mid_close=0.715,
        csv_bid_close=0.714,
        csv_ask_close=0.716,
        sqlite_mid_close=0.715,
        sqlite_bid_close=0.714,
        sqlite_ask_close=0.716,
        ohlc_match="match",
        spread_close_csv_pips=2.0,
        spread_close_sqlite_pips=2.0,
        spread_match="match",
        bespoke_atr=0.01,
        bespoke_adx=15.0,
        bt_atr=0.01,
        bt_adx=15.0,
        prior_high=0.72,
        prior_low=0.70,
        range_width_atr=2.0,
        sweep_distance_atr=0.5,
        stop_distance_atr=1.0,
        bespoke_raw="none",
        bt_raw="long",
        side="long",
        planned_entry_timestamp="2022-05-06T17:00:00+00:00",
        planned_entry_price=0.7104,
        planned_stop=0.705,
        bespoke_risk_decision="n/a",
        bespoke_risk_rejection="",
        bt_risk_decision="approved",
        bt_risk_rejection="",
        session_gate_bespoke="pass",
        session_gate_bt="pass",
        spread_gate_bespoke="pass",
        spread_gate_bt="pass",
        margin_gate_bespoke="pass",
        margin_gate_bt="pass",
        open_position_before="flat",
        pending_entry_before="none",
        open_position_after="long",
        pending_entry_after="none",
        trade_accepted_bespoke="n/a",
        trade_accepted_bt="yes",
    )
    base.update(kwargs)
    return BarTraceRow(**base)  # type: ignore[arg-type]


def test_classify_bt_signal_bespoke_none() -> None:
    div = classify_first_divergence([_row()])
    assert div is not None
    assert div["kind"] == FirstDivergenceKind.BT_SIGNAL_BESPOKE_NONE.value


def test_classify_data_mismatch() -> None:
    div = classify_first_divergence([_row(ohlc_match="mismatch")])
    assert div is not None
    assert div["kind"] == FirstDivergenceKind.DATA_MISMATCH.value


def test_classify_riskengine_mismatch() -> None:
    div = classify_first_divergence(
        [
            _row(
                bespoke_raw="long",
                bt_raw="long",
                trade_accepted_bespoke="no",
                trade_accepted_bt="yes",
                bespoke_risk_decision="rejected",
                bespoke_risk_rejection="SPREAD_TO_ATR",
                bt_risk_decision="approved",
            )
        ]
    )
    assert div is not None
    assert div["kind"] == FirstDivergenceKind.BT_ACCEPTED_BESPOKE_REJECTED.value


def test_slice_trace_window() -> None:
    rows = [
        _row(timestamp=f"2022-05-0{i}T13:00:00+00:00") for i in range(1, 8)
    ]
    sliced = slice_trace_window(
        rows, center_ts="2022-05-04T13:00:00+00:00", window_bars=3
    )
    assert len(sliced) == 3
    assert sliced[1].timestamp == "2022-05-04T13:00:00+00:00"

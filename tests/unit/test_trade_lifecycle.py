"""Tests for the normalized trade-lifecycle schema and loaders."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from forex_bot.research.trade_lifecycle import (
    TradeLifecycleRecord,
    field_missingness,
    load_trades_csv,
    parse_lifecycle_row,
)

# A faithful subset of the real C022 trades.csv header.
C022_HEADER = (
    "instrument,side,units,entry_time,exit_time,entry_price,exit_price,stop_price,"
    "pnl,r_multiple,bars_held,spread_paid_pips,exit_reason,fill_timing,ambiguous_exit,"
    "gap_fill,gap_fill_distance_pips,protective_stop_armed,protective_stop_arm_time,"
    "protective_stop_arm_mfe_r,protective_stop_exit,thesis_invalidation_exit,zscore_at_exit"
)


def _c022_row(**overrides: str) -> dict[str, str]:
    base = {
        "instrument": "USD_JPY",
        "side": "short",
        "units": "1109",
        "entry_time": "2021-07-09T10:00:00+00:00",
        "exit_time": "2021-07-09T13:45:00+00:00",
        "entry_price": "110.0100",
        "exit_price": "110.140",
        "stop_price": "110.140",
        "pnl": "-1.30",
        "r_multiple": "-0.9079",
        "bars_held": "16",
        "spread_paid_pips": "1.2",
        "exit_reason": "stop",
        "fill_timing": "next_bar_open",
        "ambiguous_exit": "False",
        "gap_fill": "False",
        "gap_fill_distance_pips": "",
        "protective_stop_armed": "False",
        "protective_stop_arm_time": "",
        "protective_stop_arm_mfe_r": "",
        "protective_stop_exit": "False",
        "thesis_invalidation_exit": "False",
        "zscore_at_exit": "",
    }
    base.update(overrides)
    return base


def test_record_construction_minimal():
    rec = TradeLifecycleRecord(campaign_id="CAMPAIGN_022")
    assert rec.campaign_id == "CAMPAIGN_022"
    # All optional fields default to None / explicit-missing.
    assert rec.entry_time is None
    assert rec.mfe_r is None
    assert rec.h4_adx_at_entry is None
    assert rec.extra == {}


def test_parse_c022_style_row():
    rec = parse_lifecycle_row(
        _c022_row(), campaign_id="CAMPAIGN_022", split="train",
        strategy_name="h4_h1_pullback_resolution_entry",
    )
    assert rec.instrument == "USD_JPY"
    assert rec.side == "short"
    assert rec.split == "train"
    assert rec.entry_time == datetime(2021, 7, 9, 10, 0, tzinfo=UTC)
    assert rec.exit_time == datetime(2021, 7, 9, 13, 45, tzinfo=UTC)
    assert rec.entry_price == 110.01
    assert rec.exit_price == 110.14
    assert rec.initial_stop_price == 110.14
    assert rec.result_r == -0.9079
    assert rec.exit_reason == "stop"
    assert rec.bars_held == 16
    assert rec.spread_pips == 1.2


def test_jpy_stop_distance_in_pips():
    # entry 110.01, stop 110.14 -> 0.13 price -> 13 pips (JPY pip = 0.01)
    rec = parse_lifecycle_row(_c022_row(), campaign_id="CAMPAIGN_022", split="train")
    assert rec.stop_distance_pips is not None
    assert abs(rec.stop_distance_pips - 13.0) < 1e-6


def test_non_jpy_stop_distance_in_pips():
    rec = parse_lifecycle_row(
        _c022_row(instrument="EUR_USD", entry_price="1.10000", stop_price="1.10200"),
        campaign_id="CAMPAIGN_022",
        split="train",
    )
    # 0.0020 price / 0.0001 pip = 20 pips
    assert rec.stop_distance_pips is not None
    assert abs(rec.stop_distance_pips - 20.0) < 1e-6


def test_missing_optional_columns_are_none_not_error():
    # A spartan row missing most columns must not raise.
    rec = parse_lifecycle_row(
        {"instrument": "GBP_USD", "side": "long"},
        campaign_id="CAMPAIGN_X",
        split=None,
    )
    assert rec.instrument == "GBP_USD"
    assert rec.entry_price is None
    assert rec.stop_distance_pips is None
    assert rec.result_r is None
    assert rec.mfe_r is None


def test_full_mfe_mae_absent_in_c022_row():
    rec = parse_lifecycle_row(_c022_row(), campaign_id="CAMPAIGN_022", split="train")
    # The conditional protective_stop_arm_mfe_r proxy is blank here and must NOT
    # be silently promoted into mfe_r.
    assert rec.mfe_r is None
    assert rec.mae_r is None


def test_blank_numeric_yields_none():
    rec = parse_lifecycle_row(
        _c022_row(r_multiple="", bars_held=""),
        campaign_id="CAMPAIGN_022",
        split="train",
    )
    assert rec.result_r is None
    assert rec.bars_held is None


def test_unrecognized_columns_preserved_in_extra():
    rec = parse_lifecycle_row(
        _c022_row(zscore_at_exit="1.5"),
        campaign_id="CAMPAIGN_022",
        split="train",
    )
    assert rec.extra.get("zscore_at_exit") == "1.5"
    # blank extras are dropped
    assert "gap_fill_distance_pips" not in rec.extra


def test_field_missingness_counts():
    recs = [
        parse_lifecycle_row(_c022_row(), campaign_id="CAMPAIGN_022", split="train")
        for _ in range(3)
    ]
    miss = field_missingness(recs)
    assert miss["_total_records"] == 3
    # mfe_r / signal features absent in all 3
    assert miss["mfe_r"] == 3
    assert miss["h4_adx_at_entry"] == 3
    # present fields should not appear as missing
    assert "instrument" not in miss
    assert "result_r" not in miss


def test_load_real_c022_csv_if_present():
    """If the committed C022 CSV exists, load it read-only and sanity-check."""
    repo_root = Path(__file__).resolve().parents[2]
    csv_path = (
        repo_root
        / "backtests"
        / "CAMPAIGN_022_h4_h1_pullback_resolution"
        / "train"
        / "base"
        / "c022_USD_JPY_train_base_trades.csv"
    )
    if not csv_path.exists():
        return  # committed artifact not in this checkout; skip silently
    before = csv_path.read_bytes()
    recs = load_trades_csv(csv_path, campaign_id="CAMPAIGN_022", split="train")
    assert len(recs) > 0
    assert all(r.instrument == "USD_JPY" for r in recs)
    assert all(r.exit_reason in {"stop", "time", "time_stop"} or r.exit_reason for r in recs)
    # read-only: source bytes unchanged
    assert csv_path.read_bytes() == before

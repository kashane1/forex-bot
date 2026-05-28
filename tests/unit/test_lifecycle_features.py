"""Tests for the forward-looking lifecycle feature-capture schema."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from forex_bot.research.lifecycle_features import (
    CSV_COLUMNS,
    LifecycleFeatureRecord,
    derive_stop_distance_pips,
    missing_field_counts,
    pip_size,
    price_based_r,
    record_from_trade_row,
    records_from_trade_rows,
    session_bucket_from_utc,
    weekday_from,
    write_lifecycle_features_csv,
)


def test_csv_columns_cover_all_required_fields():
    expected = {
        "campaign_id", "strategy_name", "split", "instrument", "side",
        "entry_time", "exit_time", "entry_price", "exit_price",
        "initial_stop_price", "stop_distance_pips", "stop_distance_atr",
        "atr_at_entry", "spread_pips", "spread_to_atr_pct", "bars_held",
        "result_r", "exit_reason", "mfe_r", "mae_r", "reached_plus_0_25r",
        "reached_plus_0_5r", "reached_plus_1_0r", "touched_minus_0_5r",
        "touched_minus_0_9r", "h4_adx_at_entry", "h4_bias_score", "h4_ema_slope",
        "h1_pullback_depth_atr", "h1_rsi_at_entry", "m15_reclaim_distance_atr",
        "m15_adx_at_entry", "session_bucket", "weekday", "volatility_regime",
        "h1_feature_time", "h4_feature_time",
    }
    assert expected.issubset(set(CSV_COLUMNS))
    assert CSV_COLUMNS[0] == "campaign_id"


def test_minimal_record_all_optional_none():
    rec = LifecycleFeatureRecord(campaign_id="CAMPAIGN_999")
    assert rec.campaign_id == "CAMPAIGN_999"
    assert rec.mfe_r is None and rec.h4_adx_at_entry is None
    assert rec.reached_plus_0_5r is None


def test_to_csv_row_serialization():
    rec = LifecycleFeatureRecord(
        campaign_id="CAMPAIGN_999",
        instrument="USD_JPY",
        side="short",
        entry_time=datetime(2024, 1, 2, 9, 0, tzinfo=UTC),
        entry_price=110.0,
        exit_price=110.2,
        initial_stop_price=110.2,
        result_r=-1.0,
        reached_plus_0_5r=False,
        bars_held=12,
    )
    row = rec.to_csv_row()
    assert row["campaign_id"] == "CAMPAIGN_999"
    assert row["entry_time"] == "2024-01-02T09:00:00+00:00"
    assert row["reached_plus_0_5r"] == "False"
    assert row["bars_held"] == "12"
    assert row["mfe_r"] == ""  # None -> empty
    # every column present
    assert set(row.keys()) == set(CSV_COLUMNS)


def test_from_mapping_roundtrip_and_blanks():
    original = LifecycleFeatureRecord(
        campaign_id="CAMPAIGN_999",
        instrument="EUR_USD",
        side="long",
        entry_time=datetime(2024, 3, 1, 12, 0, tzinfo=UTC),
        entry_price=1.1,
        exit_price=1.105,
        initial_stop_price=1.095,
        result_r=1.0,
        mfe_r=1.3,
        reached_plus_1_0r=True,
        bars_held=20,
    )
    row = original.to_csv_row()
    rebuilt = LifecycleFeatureRecord.from_mapping(row)
    assert rebuilt.instrument == "EUR_USD"
    assert rebuilt.entry_time == original.entry_time
    assert rebuilt.result_r == 1.0
    assert rebuilt.mfe_r == 1.3
    assert rebuilt.reached_plus_1_0r is True
    assert rebuilt.bars_held == 20
    # blank optional stays None
    assert rebuilt.h4_adx_at_entry is None


def test_from_mapping_ignores_unknown_keys():
    rec = LifecycleFeatureRecord.from_mapping(
        {"campaign_id": "C", "instrument": "GBP_USD", "totally_unknown": "x"}
    )
    assert rec.instrument == "GBP_USD"
    assert not hasattr(rec, "totally_unknown")


def test_price_based_r_is_pair_agnostic_minus_one_at_stop():
    # JPY-base, CAD-base, USD-quote all yield -1 at the stop.
    assert price_based_r("short", 110.0, 110.2, 110.2) == -1.0
    assert price_based_r("long", 1.2704, 1.26845, 1.26845) == -1.0
    assert price_based_r("short", 1.19067, 1.19198, 1.19198) == -1.0


def test_price_based_r_partial_and_favorable():
    # long: entry 100 stop 99 (risk 1). exit 100.5 -> +0.5R; exit 98.5 -> -1.5R
    assert price_based_r("long", 100.0, 100.5, 99.0) == 0.5
    assert price_based_r("long", 100.0, 98.5, 99.0) == -1.5


def test_price_based_r_zero_risk_and_bad_side():
    assert price_based_r("long", 100.0, 100.5, 100.0) is None
    assert price_based_r("flat", 100.0, 100.5, 99.0) is None


def test_pip_size_jpy_vs_non_jpy():
    assert pip_size("USD_JPY") == 0.01
    assert pip_size("EUR_USD") == 0.0001
    assert pip_size(None) == 0.0001


def test_derive_stop_distance_pips():
    assert derive_stop_distance_pips("EUR_USD", 1.10000, 1.10200) == pytest.approx(20.0)
    assert derive_stop_distance_pips("USD_JPY", 110.00, 110.13) == pytest.approx(13.0)
    assert derive_stop_distance_pips("EUR_USD", None, 1.1) is None


def test_session_bucket_and_weekday_derivation():
    assert session_bucket_from_utc(datetime(2024, 1, 2, 3, 0, tzinfo=UTC)) == "asia"
    assert session_bucket_from_utc(datetime(2024, 1, 2, 9, 0, tzinfo=UTC)) == "london"
    assert session_bucket_from_utc(datetime(2024, 1, 2, 14, 0, tzinfo=UTC)) == "london_ny_overlap"
    assert session_bucket_from_utc(datetime(2024, 1, 2, 18, 0, tzinfo=UTC)) == "new_york"
    assert session_bucket_from_utc(datetime(2024, 1, 2, 22, 0, tzinfo=UTC)) == "late"
    assert session_bucket_from_utc(None) is None
    # 2024-01-02 is a Tuesday
    assert weekday_from(datetime(2024, 1, 2, 0, 0, tzinfo=UTC)) == "Tue"
    assert weekday_from(None) is None


def test_record_from_trade_row_uses_corrected_r_for_jpy():
    # A USD_JPY full-stop row: source r_multiple is the buggy ~-0.009, but the
    # exporter must recompute the corrected price-based R = -1.0.
    row = {
        "instrument": "USD_JPY", "side": "short",
        "entry_time": "2021-07-09T10:00:00+00:00",
        "exit_time": "2021-07-09T13:45:00+00:00",
        "entry_price": "110.0100", "exit_price": "110.140", "stop_price": "110.140",
        "r_multiple": "-0.00908", "bars_held": "16", "spread_paid_pips": "1.2",
        "exit_reason": "stop",
    }
    rec = record_from_trade_row(row, campaign_id="CAMPAIGN_022",
                                strategy_name="h4_h1_pullback_resolution_entry", split="train")
    assert rec.result_r == pytest.approx(-1.0, abs=1e-6)  # corrected, not -0.009
    assert rec.instrument == "USD_JPY"
    assert rec.stop_distance_pips == pytest.approx(13.0)
    assert rec.session_bucket == "london"  # 10:00 UTC
    assert rec.weekday == "Fri"  # 2021-07-09 is a Friday
    # MFE/MAE + signal features not in source -> explicitly None
    assert rec.mfe_r is None and rec.h4_adx_at_entry is None


def test_records_export_roundtrip_csv(tmp_path):
    rows = [
        {"instrument": "EUR_USD", "side": "long", "entry_time": "2024-01-02T09:00:00+00:00",
         "exit_time": "2024-01-02T12:00:00+00:00", "entry_price": "1.1000",
         "exit_price": "1.1050", "stop_price": "1.0950", "bars_held": "12",
         "exit_reason": "time", "spread_paid_pips": "0.8"},
    ]
    recs = records_from_trade_rows(rows, campaign_id="CAMPAIGN_022", split="validation")
    out = write_lifecycle_features_csv(recs, tmp_path / "feat.csv")
    assert out.exists()
    text = out.read_text()
    assert text.splitlines()[0] == ",".join(CSV_COLUMNS)  # canonical header
    # result_r corrected: (1.1050-1.1000)/(1.1000-1.0950) = +1.0
    assert recs[0].result_r == pytest.approx(1.0)


def test_missing_field_counts():
    recs = [
        LifecycleFeatureRecord(campaign_id="C", instrument="EUR_USD", result_r=1.0),
        LifecycleFeatureRecord(campaign_id="C", instrument="EUR_USD", result_r=-1.0),
    ]
    miss = missing_field_counts(recs)
    assert miss["_total_records"] == 2
    assert miss["mfe_r"] == 2          # absent in both
    assert miss["h4_adx_at_entry"] == 2
    assert "campaign_id" not in miss   # always present
    assert "instrument" not in miss    # present in both
    assert "result_r" not in miss

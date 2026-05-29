"""Unit tests for the lookahead-safe macro/rates/calendar regime-context module.

Focus: the as-of join must never use a value published after (t - publication_lag),
NFP first-Friday computation is exact, and event-window flags behave correctly. These
guarantee the slow-context features are lookahead-safe and latency-independent.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from forex_bot.research.macro_regime_context import (
    MacroRegimeParams,
    asof_join,
    build_daily_regime_features,
    build_event_calendar,
    event_proximity_hours,
    event_window_flags,
    fomc_announcement_datetimes,
    load_fred_series,
    nfp_release_datetimes,
    stabilization_bucket,
)


def _write_fred(cache_dir, series_id, feature_id, dates, values):
    rows = [{"date": f"{d} 00:00:00+00:00", "value": v} for d, v in zip(dates, values, strict=True)]
    (cache_dir / f"{series_id}.json").write_text(json.dumps(
        {"series_id": series_id, "feature_id": feature_id, "rows": len(rows), "data": rows}
    ))


# --------------------------------------------------------------------------- #
# As-of join — the critical no-lookahead guarantee
# --------------------------------------------------------------------------- #
def test_asof_join_uses_only_lagged_past_values(tmp_path):
    daily = pd.DataFrame(
        {"x": [10.0, 20.0, 30.0]},
        index=pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"], utc=True),
    )
    # intraday bars across Jan 3-5; publication lag = 1 day
    target = pd.to_datetime(
        ["2023-01-03T12:00:00Z", "2023-01-04T12:00:00Z", "2023-01-05T12:00:00Z"], utc=True
    )
    out = asof_join(daily, target, MacroRegimeParams(publication_lag_days=1))
    # Jan-3 bar: only Jan-2's value is available (Jan-3 value needs Jan-4 avail) -> 10
    assert out["x"].iloc[0] == 10.0
    # Jan-4 bar: Jan-3 value available (avail Jan-4) -> 20
    assert out["x"].iloc[1] == 20.0
    # Jan-5 bar: Jan-4 value available (avail Jan-5) -> 30
    assert out["x"].iloc[2] == 30.0


def test_asof_join_larger_lag_is_more_conservative(tmp_path):
    daily = pd.DataFrame(
        {"x": [10.0, 20.0, 30.0]},
        index=pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"], utc=True),
    )
    target = pd.to_datetime(["2023-01-06T12:00:00Z"], utc=True)
    out1 = asof_join(daily, target, MacroRegimeParams(publication_lag_days=1))
    out3 = asof_join(daily, target, MacroRegimeParams(publication_lag_days=3))
    # lag1: Jan-4 value available (avail Jan-5) -> 30; lag3: only Jan-3 (avail Jan-6) -> 20
    assert out1["x"].iloc[0] == 30.0
    assert out3["x"].iloc[0] == 20.0   # larger lag -> older value (latency-independence knob)


# --------------------------------------------------------------------------- #
# NFP / FOMC calendar
# --------------------------------------------------------------------------- #
def test_nfp_is_first_friday_0830et():
    dts = nfp_release_datetimes("2024-01-01", "2024-04-01")
    days = [t.strftime("%Y-%m-%d") for t in dts]
    # First Fridays of Jan/Feb/Mar 2024: 2024-01-05, 2024-02-02, 2024-03-01
    assert days == ["2024-01-05", "2024-02-02", "2024-03-01"]
    assert all(t.weekday() == 4 for t in dts)          # Friday
    assert all((t.hour, t.minute) == (13, 30) for t in dts)  # 13:30 UTC


def test_fomc_dates_within_window_only():
    dts = fomc_announcement_datetimes("2024-01-01", "2024-12-31")
    assert all(pd.Timestamp("2024-01-01", tz="UTC") <= t < pd.Timestamp("2024-12-31", tz="UTC")
               for t in dts)
    assert len(dts) == 8  # 8 FOMC meetings in 2024


def test_build_event_calendar_has_nfp_and_fomc():
    cal = build_event_calendar("2023-01-01", "2023-07-01")
    assert set(cal["event"]) == {"NFP", "FOMC"}
    assert (cal["time_utc"].dt.tz is not None) or str(cal["time_utc"].dtype).endswith("UTC]")


# --------------------------------------------------------------------------- #
# Event proximity & windows
# --------------------------------------------------------------------------- #
def test_event_proximity_sign_convention():
    ev = [pd.Timestamp("2023-06-14T18:00:00Z")]
    idx = pd.to_datetime(
        ["2023-06-14T12:00:00Z", "2023-06-14T18:00:00Z", "2023-06-15T06:00:00Z"], utc=True
    )
    hse = event_proximity_hours(idx, ev)
    assert hse.iloc[0] == -6.0   # 6h before event
    assert hse.iloc[1] == 0.0    # at event
    assert hse.iloc[2] == 12.0   # 12h after event


def test_event_window_and_stabilization_buckets():
    ev = [pd.Timestamp("2023-06-14T18:00:00Z")]
    idx = pd.to_datetime(
        ["2023-06-14T00:00:00Z", "2023-06-14T20:00:00Z", "2023-06-20T00:00:00Z"], utc=True
    )
    flags = event_window_flags(idx, ev, MacroRegimeParams())
    assert bool(flags["pre_event"].iloc[0])    # 18h before
    assert bool(flags["post_event"].iloc[1])   # 2h after
    assert not bool(flags["event_window"].iloc[2])  # ~6 days after -> normal
    buck = stabilization_bucket(flags["hours_since_event"], MacroRegimeParams())
    assert buck.iloc[0] == "pre_event"
    assert buck.iloc[1] == "post_4h"
    assert buck.iloc[2] == "normal"


# --------------------------------------------------------------------------- #
# FRED loading + daily regime features
# --------------------------------------------------------------------------- #
def test_load_fred_series_and_regime_features(tmp_path):
    dates = pd.date_range("2022-01-01", periods=400, freq="D").strftime("%Y-%m-%d").tolist()
    rng = np.random.default_rng(1)
    _write_fred(tmp_path, "DGS2", "us_2y_yield", dates, np.linspace(0.5, 4.5, 400))
    _write_fred(tmp_path, "DGS10", "us_10y_yield", dates, np.linspace(1.5, 4.0, 400))
    _write_fred(tmp_path, "VIXCLS", "vix", dates, 15 + 5 * rng.standard_normal(400))
    _write_fred(tmp_path, "SP500", "sp500", dates, np.linspace(3800, 4800, 400))
    _write_fred(tmp_path, "DTWEXBGS", "broad_usd_index", dates, np.linspace(100, 110, 400))

    s = load_fred_series(tmp_path, "DGS2")
    assert s.index.tz is not None and len(s) == 400

    feats = build_daily_regime_features(tmp_path, MacroRegimeParams())
    for col in ("us_2s10s", "us_2y_trend", "us_2y_regime", "vix_regime", "risk_off"):
        assert col in feats.columns
    # rising-rate ramp -> trend should be +1 once warmed up
    assert feats["us_2y_trend"].dropna().iloc[-1] == 1.0

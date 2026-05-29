"""Tests for the M1/HTF confluence response matrix (research-only framework).

These pin the analysis core on synthetic data: lookahead-safe alignment,
rising-edge + cooldown event sampling, forward return/MFE/MAE arithmetic, gap
handling, aggregation, and deterministic null sampling. No DB, no network.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from forex_bot.research import m1_response_matrix as mrm


def _m1_index(n: int, start: str = "2022-01-03 00:00") -> pd.DatetimeIndex:
    return pd.date_range(start=start, periods=n, freq="1min", tz="UTC")


# --------------------------------------------------------------------------- #
# pip / sessions
# --------------------------------------------------------------------------- #


def test_pip_size():
    assert mrm.pip_size("USD_JPY") == 0.01
    assert mrm.pip_size("EUR_USD") == 0.0001
    assert mrm.pip_size("GBP_JPY") == 0.01  # unknown JPY-quoted -> 0.01
    assert mrm.pip_size("XAG_USD") == 0.0001


def test_sessions_of():
    idx = pd.to_datetime(
        ["2022-01-03 03:00", "2022-01-03 09:00", "2022-01-03 15:00", "2022-01-03 22:00"]
    ).tz_localize("UTC")
    s = mrm.sessions_of(idx)
    assert list(s) == ["tokyo", "london", "ny", "offhours"]


# --------------------------------------------------------------------------- #
# htf_features
# --------------------------------------------------------------------------- #


def test_htf_features_uptrend_primitives():
    n = 150
    idx = pd.date_range("2022-01-01", periods=n, freq="15min", tz="UTC")
    close = 100.0 + np.arange(n) * 0.1
    df = pd.DataFrame(
        {"open": close, "high": close + 0.05, "low": close - 0.05, "close": close},
        index=idx,
    )
    feats = mrm.htf_features(df)
    # Monotone uptrend: tail bar is trend_up, never trend_down, and breaking out.
    assert bool(feats["trend_up"].iloc[-1])
    assert not bool(feats["trend_down"].iloc[-1])
    assert bool(feats["aligned_up"].iloc[-1])
    assert bool(feats["breakout_up"].iloc[-1])
    # Boolean columns are real booleans, atr is numeric and non-negative.
    assert feats["trend_up"].dtype == bool
    assert feats["atr"].iloc[-1] >= 0


# --------------------------------------------------------------------------- #
# align_asof — lookahead safety
# --------------------------------------------------------------------------- #


def test_align_asof_is_lookahead_safe():
    # Two M5 bars; bar @00:00 completes @00:05, bar @00:05 completes @00:10.
    htf = pd.DataFrame(
        {"val": [10.0, 20.0]},
        index=pd.to_datetime(["2022-01-03 00:00", "2022-01-03 00:05"]).tz_localize("UTC"),
    )
    m1 = _m1_index(13)  # 00:00 .. 00:12
    aligned = mrm.align_asof(m1, htf, tf_minutes=5, prefix="M5")
    v = aligned["M5_val"]
    # Before any HTF bar has completed -> NaN (no future leak).
    assert v.loc["2022-01-03 00:00"] != v.loc["2022-01-03 00:00"]  # NaN
    assert v.loc["2022-01-03 00:04"] != v.loc["2022-01-03 00:04"]  # NaN
    # First bar usable only at/after its 00:05 completion.
    assert v.loc["2022-01-03 00:05"] == 10.0
    assert v.loc["2022-01-03 00:09"] == 10.0
    # Second bar usable only at/after its 00:10 completion.
    assert v.loc["2022-01-03 00:10"] == 20.0
    assert v.loc["2022-01-03 00:12"] == 20.0


# --------------------------------------------------------------------------- #
# confluence_states
# --------------------------------------------------------------------------- #


def test_confluence_states_signed_and_named():
    idx = _m1_index(3)
    frame = pd.DataFrame(index=idx)
    # Minimal columns for A1 archetype.
    frame["M15_trend_up"] = [True, False, False]
    frame["M5_aligned_up"] = [True, False, False]
    frame["M15_trend_down"] = [False, False, True]
    frame["M5_aligned_down"] = [False, False, True]
    # Other archetypes need their columns too; add as all-False.
    for c in (
        "M5_pullback_up", "M5_pullback_down", "M5_breakout_up", "M5_breakout_down",
        "M5_compression", "M15_pullback_up", "M15_pullback_down", "M15_aligned_up",
        "M15_aligned_down", "M15_breakout_up", "M15_breakout_down", "H1_trend_up",
        "H1_trend_down", "H4_trend_up", "H4_trend_down",
    ):
        frame[c] = False
    states = mrm.confluence_states(frame)
    assert "A1_trend_cont_long" in states
    assert "A1_trend_cont_short" in states
    assert list(states["A1_trend_cont_long"]) == [1, 0, 0]
    assert list(states["A1_trend_cont_short"]) == [0, 0, -1]


# --------------------------------------------------------------------------- #
# extract_events — rising edge + cooldown
# --------------------------------------------------------------------------- #


def test_extract_events_rising_edge_and_cooldown():
    idx = _m1_index(200)
    frame = pd.DataFrame(index=idx)
    frame["spread_close"] = 0.0002  # 2 pips for EUR_USD
    frame["M15_atr"] = 0.0010  # 10 pips
    signed = pd.Series(0, index=idx)
    signed.iloc[10:41] = 1   # rising edge @ minute 10
    signed.iloc[50:61] = 1   # rising edge @ minute 50 (within 60min cooldown -> dropped)
    signed.iloc[130:141] = 1  # rising edge @ minute 130 (>=60min after 10 -> kept)
    ev = mrm.extract_events(
        signed, frame, pair="EUR_USD", state="A1_trend_cont_long", vol_col="M15_atr"
    )
    assert len(ev) == 2
    assert list(ev["timestamp"].dt.minute) == [10, 10]  # minutes 10 and 130 (both :10)
    assert ev["timestamp"].iloc[0] == idx[10]
    assert ev["timestamp"].iloc[1] == idx[130]
    assert (ev["direction"] == 1).all()
    assert ev["spread"].iloc[0] == pytest.approx(2.0)
    assert ev["volatility"].iloc[0] == pytest.approx(10.0)


def test_extract_events_empty_when_never_active():
    idx = _m1_index(10)
    frame = pd.DataFrame({"spread_close": 0.0002}, index=idx)
    signed = pd.Series(0, index=idx)
    ev = mrm.extract_events(signed, frame, pair="EUR_USD", state="x")
    assert ev.empty


# --------------------------------------------------------------------------- #
# forward_response — arithmetic + gaps
# --------------------------------------------------------------------------- #


def test_forward_response_arithmetic_and_gap():
    # 11 one-minute bars; pip moves relative to entry.
    p = np.array([0, 1, 2, -3, 4, 2, 5, 1, 0, 7, 6], dtype=float)
    idx = _m1_index(11)
    m1 = pd.DataFrame({"mid_c": 100.0 + p * 0.0001}, index=idx)
    events = pd.DataFrame(
        {
            "timestamp": [idx[0]],
            "pair": ["EUR_USD"],
            "state": ["s"],
            "direction": [1],
            "session": ["tokyo"],
            "spread": [np.nan],
            "volatility": [np.nan],
        }
    )
    resp = mrm.forward_response(m1, events, pair="EUR_USD", horizons_min=(5, 10, 15))
    # Horizon 5: endpoint index 5, window bars 1..5 = [1,2,-3,4,2].
    assert resp["ret_5"].iloc[0] == pytest.approx(2.0)
    assert resp["mfe_5"].iloc[0] == pytest.approx(4.0)
    assert resp["mae_5"].iloc[0] == pytest.approx(3.0)
    # Horizon 10: endpoint index 10 -> ret = p[10] = 6; mfe over 1..10 = 7.
    assert resp["ret_10"].iloc[0] == pytest.approx(6.0)
    assert resp["mfe_10"].iloc[0] == pytest.approx(7.0)
    # Horizon 15: beyond available bars -> NaN (gap handling).
    assert np.isnan(resp["ret_15"].iloc[0])


def test_forward_response_direction_short_flips_sign():
    p = np.array([0, -2, -5, -3, -8, -10], dtype=float)
    idx = _m1_index(6)
    m1 = pd.DataFrame({"mid_c": 100.0 + p * 0.0001}, index=idx)
    events = pd.DataFrame(
        {
            "timestamp": [idx[0]],
            "pair": ["EUR_USD"],
            "state": ["s"],
            "direction": [-1],
            "session": ["tokyo"],
            "spread": [np.nan],
            "volatility": [np.nan],
        }
    )
    resp = mrm.forward_response(m1, events, pair="EUR_USD", horizons_min=(5,))
    # Short: signed ret = -1 * (p[5]-p[0]) = -(-10) = 10 pips favorable.
    assert resp["ret_5"].iloc[0] == pytest.approx(10.0)
    assert resp["mfe_5"].iloc[0] == pytest.approx(10.0)
    assert resp["mae_5"].iloc[0] == pytest.approx(0.0)


# --------------------------------------------------------------------------- #
# summarize
# --------------------------------------------------------------------------- #


def test_summarize_stats():
    resp = pd.DataFrame(
        {
            "state": ["s", "s", "s", "s"],
            "spread": [1.0, 1.0, 1.0, 1.0],
            "volatility": [5.0, 5.0, 5.0, 5.0],
            "ret_5": [2.0, -1.0, 3.0, np.nan],
            "mfe_5": [3.0, 1.0, 4.0, np.nan],
            "mae_5": [1.0, 2.0, 0.5, np.nan],
        }
    )
    out = mrm.summarize(resp, horizons_min=(5,))
    row = out.iloc[0]
    assert row["state"] == "s"
    assert row["n"] == 3  # NaN dropped
    assert row["mean_ret"] == pytest.approx((2 - 1 + 3) / 3)
    assert row["hit_rate"] == pytest.approx(2 / 3)
    assert row["p_neg"] == pytest.approx(1 / 3)
    assert row["mean_spread"] == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# null sampling
# --------------------------------------------------------------------------- #


def test_sample_random_events_deterministic_and_session_restricted():
    idx = _m1_index(600)  # spans tokyo into london
    m1 = pd.DataFrame({"mid_c": 100.0}, index=idx)
    a = mrm.sample_random_events(m1, pair="EUR_USD", n=20, direction=1, seed=7)
    b = mrm.sample_random_events(m1, pair="EUR_USD", n=20, direction=1, seed=7)
    assert list(a["timestamp"]) == list(b["timestamp"])  # deterministic
    assert (a["direction"] == 1).all()
    only_tokyo = mrm.sample_random_events(
        m1, pair="EUR_USD", n=20, direction=1, seed=1, allowed_sessions=["tokyo"]
    )
    assert (only_tokyo["session"] == "tokyo").all()


def test_sample_matched_null_matches_session_and_count():
    idx = _m1_index(600)
    m1 = pd.DataFrame({"mid_c": 100.0}, index=idx)
    ref = pd.DataFrame(
        {
            "timestamp": [idx[30], idx[100]],
            "pair": ["EUR_USD", "EUR_USD"],
            "state": ["s", "s"],
            "direction": [1, -1],
            "session": ["tokyo", "tokyo"],
            "spread": [np.nan, np.nan],
            "volatility": [np.nan, np.nan],
        }
    )
    null = mrm.sample_matched_null(m1, ref, pair="EUR_USD", seed=3)
    assert len(null) == 2
    assert (null["session"] == "tokyo").all()
    assert sorted(null["direction"]) == [-1, 1]

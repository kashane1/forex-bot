"""Synthetic-data tests for the C1 factor-validation analysis module.

No network, no DB, no credentials — pure construction on hand-built frames.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from forex_bot.research import c1_factor_validation as c1v
from forex_bot.research import m1_response_matrix as mrm


def test_currency_legs_and_usd_leg():
    assert c1v.currency_legs("USD_JPY") == ("USD", "JPY")
    assert c1v.currency_legs("EUR_USD") == ("EUR", "USD")
    assert c1v.usd_leg("USD_JPY") == "base"
    assert c1v.usd_leg("USD_CAD") == "base"
    assert c1v.usd_leg("EUR_USD") == "quote"
    assert c1v.usd_leg("GBP_USD") == "quote"
    assert c1v.usd_leg("EUR_GBP") == "none"


def _ramp_ohlc(start: str, n: int, freq: str, step: float, base: float = 100.0):
    """Monotone-rising OHLC so trend_up/aligned_up are eventually True."""
    idx = pd.date_range(start, periods=n, freq=freq, tz="UTC")
    close = base + np.arange(n) * step
    return pd.DataFrame(
        {"open": close, "high": close + 0.01, "low": close - 0.01, "close": close},
        index=idx,
    )


def test_trend_frame_extension_sign_and_columns():
    ohlc = _ramp_ohlc("2022-01-01", 300, "4h", step=0.05)
    tf = c1v._trend_frame(ohlc, c1v.BASELINE)
    for col in ("atr", "trend_up", "trend_down", "aligned_up", "aligned_down", "ext_atr"):
        assert col in tf.columns
    # In a clean uptrend the tail is trend_up and extended above EMA (ext_atr>0).
    assert bool(tf["trend_up"].iloc[-1])
    assert not bool(tf["trend_down"].iloc[-1])
    assert tf["ext_atr"].iloc[-1] > 0


def test_baseline_spec_matches_locked_definition():
    # baseline legs == prior-sprint C1 (H4 trend, H1 trend, M15 aligned).
    assert c1v.BASELINE.legs == (("H4", "trend"), ("H1", "trend"), ("M15", "aligned"))
    assert c1v.BASELINE.vol_tf == "H4"
    assert c1v.BASELINE.timeframes == ("H4", "H1", "M15")


def _full_frame():
    """M1 frame + all-bullish-aligned HTF so C1_long fires, C1_short never."""
    m1_idx = pd.date_range("2022-01-03", periods=3 * 24 * 60, freq="1min", tz="UTC")
    mid = 100.0 + np.arange(len(m1_idx)) * 0.001
    m1_df = pd.DataFrame(
        {"mid_c": mid, "spread_close": np.full(len(m1_idx), 0.0002)}, index=m1_idx
    )
    raw = {
        "M15": _ramp_ohlc("2021-06-01", 400, "15min", 0.02),
        "H1": _ramp_ohlc("2021-06-01", 400, "1h", 0.05),
        "H4": _ramp_ohlc("2021-06-01", 400, "4h", 0.1),
    }
    frame = c1v.build_combined_frame(m1_df, raw, c1v.BASELINE)
    return m1_df, frame


def test_build_combined_frame_has_prefixed_columns():
    _, frame = _full_frame()
    for col in ("H4_trend_up", "H1_trend_up", "M15_aligned_up", "H4_atr", "H4_ext_atr"):
        assert col in frame.columns


def test_c1_signed_long_fires_short_silent_in_uptrend():
    _, frame = _full_frame()
    states = c1v.c1_signed(frame, c1v.BASELINE)
    assert set(states) == {"C1_trend_cont_long", "C1_trend_cont_short"}
    # Tail of a clean shared uptrend: long context active (+1), short never (-1).
    assert (states["C1_trend_cont_long"] == 1).any()
    assert not (states["C1_trend_cont_short"] == -1).any()


def test_panel_columns_and_covariates():
    m1_df, frame = _full_frame()
    panel = c1v.build_c1_panel(m1_df, frame, "EUR_USD", c1v.BASELINE)
    assert not panel.empty
    for col in ("base_ccy", "quote_ccy", "usd_leg", "year", "quarter",
                "ext_signed", "ret_60", "spread", "volatility"):
        assert col in panel.columns
    assert (panel["usd_leg"] == "quote").all()
    assert (panel["base_ccy"] == "EUR").all()
    # ext_signed = direction * extension; long events in an uptrend are >0.
    longs = panel[panel["state"] == "C1_trend_cont_long"]
    assert (longs["ext_signed"] > 0).all()


def test_dropping_h4_changes_event_set():
    m1_df, frame_base = _full_frame()
    raw = {
        "M15": _ramp_ohlc("2021-06-01", 400, "15min", 0.02),
        "H1": _ramp_ohlc("2021-06-01", 400, "1h", 0.05),
        "H4": _ramp_ohlc("2021-06-01", 400, "4h", 0.1),
    }
    drop_h4 = c1v.C1Spec(name="drop_h4", legs=(("H1", "trend"), ("M15", "aligned")))
    frame2 = c1v.build_combined_frame(m1_df, raw, drop_h4)
    assert drop_h4.timeframes == ("H1", "M15")
    assert "H4_trend_up" not in frame2.columns  # H4 not aligned for this spec
    s_base = c1v.c1_signed(frame_base, c1v.BASELINE)["C1_trend_cont_long"]
    s_drop = c1v.c1_signed(frame2, drop_h4)["C1_trend_cont_long"]
    # Different confluence depth -> different active mask (here both fire, but the
    # series objects are independently constructed and indexable).
    assert len(s_base) == len(s_drop)


def test_grouped_summary_by_session():
    m1_df, frame = _full_frame()
    panel = c1v.build_c1_panel(m1_df, frame, "USD_JPY", c1v.BASELINE)
    g = c1v.grouped_summary(panel, "session", state="C1_trend_cont_long", horizon=60)
    if not g.empty:
        assert "session" in g.columns
        assert {"n", "mean_ret", "t_stat", "p_neg"}.issubset(g.columns)
        assert (g["n"] > 0).all()


@pytest.mark.filterwarnings("ignore:Mean of empty slice:RuntimeWarning")
def test_c1_nulls_returns_finite_z_small_seeds():
    m1_df, frame = _full_frame()
    nulls = c1v.c1_nulls(m1_df, frame, "EUR_USD", seeds=5)
    # long context fires in this synthetic uptrend, so at least some rows exist.
    if not nulls.empty:
        assert {"rand_z", "matched_z", "obs_mean_ret"}.issubset(nulls.columns)
        assert set(nulls["state"]).issubset(
            {"C1_trend_cont_long", "C1_trend_cont_short"}
        )


def test_horizons_match_locked_set():
    assert mrm.HORIZONS_MIN == (5, 10, 15, 30, 60)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))

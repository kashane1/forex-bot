"""Phase 2 audit: backward-looking HTF join must not use forming HTF bars."""

from __future__ import annotations

import pandas as pd


def _last_completed_htf_value(
    decision_time: pd.Timestamp,
    htf_index: pd.DatetimeIndex,
    htf_values: pd.Series,
) -> float | None:
    """Documented join contract: last HTF row with index <= decision_time."""
    prior = htf_values.loc[htf_index <= decision_time]
    if prior.empty:
        return None
    return float(prior.iloc[-1])


def test_h4_decision_uses_prior_closed_d1_only():
    """At Wed 10:00 H4, Wed D1 close (18:00) must not be visible."""
    d1_times = pd.to_datetime(
        [
            "2024-01-08 18:00",  # Tue D1AGG close (example)
            "2024-01-09 18:00",  # Wed D1AGG close — still forming at 10:00
        ],
        utc=True,
    )
    d1_vals = pd.Series([1.0, 2.0], index=d1_times)
    h4_decision = pd.Timestamp("2024-01-09 10:00", tz="UTC")
    assert _last_completed_htf_value(h4_decision, d1_times, d1_vals) == 1.0


def test_h4_after_d1_close_sees_that_d1():
    h4_after = pd.Timestamp("2024-01-09 20:00", tz="UTC")
    d1_times = pd.to_datetime(["2024-01-09 18:00"], utc=True)
    d1_vals = pd.Series([2.0], index=d1_times)
    assert _last_completed_htf_value(h4_after, d1_times, d1_vals) == 2.0


def test_cross_asset_availability_blocks_same_day_close(tmp_path=None):
    """Mirror research/cross_asset_features/alignment: daily obs not available until next day."""
    from research.cross_asset_features.alignment import align_wide_frame_to_h4

    wide = pd.DataFrame({"vix": [18.0]}, index=pd.to_datetime(["2022-01-07"], utc=True))
    h4 = pd.date_range("2022-01-07 20:00", periods=2, freq="4h", tz="UTC")
    aligned = align_wide_frame_to_h4(h4, wide)
    assert pd.isna(aligned.iloc[0]["vix"])
    assert aligned.iloc[-1]["vix"] == 18.0

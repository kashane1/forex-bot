from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import pytest

from forex_bot.features.htf_align import HTF_STALE, HTF_UNAVAILABLE
from forex_bot.features.ltf_htf_alignment import align_ltf_execution_context


def _frame(times: list[datetime], *, complete: list[bool] | None = None) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": times,
            "complete": complete if complete is not None else [True] * len(times),
            "value": list(range(len(times))),
        }
    )


def test_m15_1015_cannot_use_h1_closing_1100() -> None:
    h1 = _frame(
        [
            datetime(2024, 1, 1, 10, tzinfo=UTC),
            datetime(2024, 1, 1, 11, tzinfo=UTC),
        ]
    )
    out = align_ltf_execution_context(
        pd.DatetimeIndex([datetime(2024, 1, 1, 10, 15, tzinfo=UTC)]),
        h1_frame=h1,
    )
    assert out["h1_feature_time"].iloc[0] == pd.Timestamp("2024-01-01T10:00:00Z")


def test_m15_1200_uses_completed_h1_and_h4() -> None:
    decision = pd.DatetimeIndex([datetime(2024, 1, 1, 12, tzinfo=UTC)])
    h1 = _frame([datetime(2024, 1, 1, 12, tzinfo=UTC)])
    h4 = _frame([datetime(2024, 1, 1, 8, tzinfo=UTC), datetime(2024, 1, 1, 12, tzinfo=UTC)])
    out = align_ltf_execution_context(decision, h1_frame=h1, h4_frame=h4)
    assert out["h1_feature_time"].iloc[0] == pd.Timestamp("2024-01-01T12:00:00Z")
    assert out["h4_feature_time"].iloc[0] == pd.Timestamp("2024-01-01T12:00:00Z")


def test_m5_m15_cannot_use_incomplete_h4_d1agg() -> None:
    decision = pd.DatetimeIndex([datetime(2024, 1, 1, 12, tzinfo=UTC)])
    h4 = _frame([datetime(2024, 1, 1, 12, tzinfo=UTC)], complete=[False])
    d1 = _frame([datetime(2024, 1, 1, 12, tzinfo=UTC)], complete=[False])
    out = align_ltf_execution_context(decision, execution_timeframe="M5", h4_frame=h4, d1agg_frame=d1)
    assert out["h4_blocked_reason"].iloc[0] == HTF_UNAVAILABLE
    assert out["d1agg_blocked_reason"].iloc[0] == HTF_UNAVAILABLE


def test_stale_context_returns_htf_stale() -> None:
    decision = pd.DatetimeIndex([datetime(2024, 1, 1, 12, tzinfo=UTC)])
    h1 = _frame([datetime(2024, 1, 1, 8, tzinfo=UTC)])
    out = align_ltf_execution_context(decision, h1_frame=h1, max_staleness=pd.Timedelta(hours=1))
    assert out["h1_blocked_reason"].iloc[0] == HTF_STALE


def test_unavailable_context_returns_htf_unavailable() -> None:
    decision = pd.DatetimeIndex([datetime(2024, 1, 1, 12, tzinfo=UTC)])
    h1 = _frame([datetime(2024, 1, 1, 13, tzinfo=UTC)])
    out = align_ltf_execution_context(decision, h1_frame=h1)
    assert out["h1_blocked_reason"].iloc[0] == HTF_UNAVAILABLE


def test_unsupported_execution_timeframe_refused() -> None:
    with pytest.raises(ValueError):
        align_ltf_execution_context(
            pd.DatetimeIndex([datetime(2024, 1, 1, tzinfo=UTC)]),
            execution_timeframe="H4",
        )

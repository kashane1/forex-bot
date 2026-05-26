"""Backtrader lane registration tests for CAMPAIGN_017."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from research.backtrader_lane.strategies import (
    campaign_017_weekly_volatility_contraction_breakout as bt017,
)

from forex_bot.features.weekly_momentum import week_start_monday_utc
from forex_bot.features.weekly_volatility import label_weekly_compression


def test_weekly_boundary_parity_with_bespoke():
    ts = pd.Timestamp(datetime(2024, 3, 13, 12, tzinfo=UTC))
    assert week_start_monday_utc(ts) == pd.Timestamp("2024-03-11", tz="UTC")


def test_compression_flag_parity():
    idx = pd.date_range("2024-01-01", periods=13, freq="7D", tz="UTC")
    tr = [5.0] * 12 + [0.1]
    weekly = pd.DataFrame(
        {"open": tr, "high": tr, "low": [0.0] * 13, "close": tr, "true_range": tr},
        index=idx,
    )
    labeled = label_weekly_compression(
        weekly, compression_lookback_weeks=12, compression_percentile_threshold=25,
    )
    assert bool(labeled.iloc[-2]["is_compressed"])


def test_no_broker_imports_in_bt_module():
    text = Path(bt017.__file__).read_text(encoding="utf-8")
    assert "forex_bot.broker" not in text
    assert "oandapyV20" not in text


def test_frozen_parameters_match_runner():
    assert bt017.FROZEN_PARAMETERS["compression_lookback_weeks"] == 12
    assert bt017.FROZEN_PARAMETERS["breakout_buffer_atr_multiple"] == 0.25


def test_adapter_registered():
    assert bt017.CAMPAIGN_017_ADAPTER.campaign_id == "CAMPAIGN_017"

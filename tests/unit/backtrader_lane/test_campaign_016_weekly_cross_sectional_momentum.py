"""Backtrader lane registration tests for CAMPAIGN_016."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
from research.backtrader_lane.strategies import (
    campaign_016_weekly_cross_sectional_momentum as bt016,
)

from forex_bot.features.weekly_momentum import is_rebalance_bar, week_start_monday_utc


def test_frozen_parameters_match_runner():
    import importlib.util
    import sys

    root = Path(__file__).resolve().parents[3]
    mod_name = "run_campaign_016_bt_test"
    spec = importlib.util.spec_from_file_location(
        mod_name, root / "scripts" / "run_campaign_016.py",
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    assert mod.FROZEN_PARAMETERS == bt016.FROZEN_PARAMETERS


def test_weekly_boundary_parity_with_bespoke_module():
    t0 = datetime(2024, 3, 11, 0, tzinfo=UTC)
    t1 = t0 + timedelta(hours=4)
    t2 = t0 + timedelta(days=7)
    assert week_start_monday_utc(pd.Timestamp(t0)) == pd.Timestamp(t0)
    assert not is_rebalance_bar(pd.Timestamp(t1), pd.Timestamp(t0))
    assert is_rebalance_bar(pd.Timestamp(t2), pd.Timestamp(t1))


def test_no_broker_imports_in_bt_adapter():
    root = Path(__file__).resolve().parents[3]
    text = (
        root
        / "research/backtrader_lane/strategies/campaign_016_weekly_cross_sectional_momentum.py"
    ).read_text(encoding="utf-8")
    assert "oandapyV20" not in text
    assert "forex_bot.broker" not in text

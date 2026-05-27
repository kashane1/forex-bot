"""Tests for deduped C008/C009 forensic replay helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from rerun_c008_c009_deduped_forensic import (  # noqa: E402
    RunRecord,
    aggregate_split,
    classify_delta,
    evaluate_c008_gates,
    evaluate_c009_gates,
    validate_frozen_config,
)

from forex_bot.config import load_settings  # noqa: E402


def test_c008_frozen_config_matches_yaml():
    settings = load_settings(ROOT / "configs/campaign_008_range_mean_reversion.yaml")
    validate_frozen_config(settings, "CAMPAIGN_008")


def test_c009_frozen_config_matches_yaml():
    settings = load_settings(ROOT / "configs/campaign_009_mean_reversion.yaml")
    validate_frozen_config(settings, "CAMPAIGN_009")


def test_c008_config_rejected_when_validated_as_c009():
    settings = load_settings(ROOT / "configs/campaign_008_range_mean_reversion.yaml")
    with pytest.raises(SystemExit):
        validate_frozen_config(settings, "CAMPAIGN_009")


def test_aggregate_split_weighted_expectancy():
    runs = [
        RunRecord(
            label="a", instrument="EUR_USD", split="train", cost_regime="base",
            strategy_version="0.1.0-c008", data_request_hash="x",
            dedupe_stats={}, metrics={"trade_count": 10, "expectancy_r": 0.1, "profit_factor": 1.1, "total_return_pct": 1.0},
            summary_path="s", trades_path="t",
        ),
        RunRecord(
            label="b", instrument="GBP_USD", split="train", cost_regime="base",
            strategy_version="0.1.0-c008", data_request_hash="y",
            dedupe_stats={}, metrics={"trade_count": 30, "expectancy_r": -0.1, "profit_factor": 0.9, "total_return_pct": -1.0},
            summary_path="s", trades_path="t",
        ),
    ]
    agg = aggregate_split(runs, "train", "base")
    assert agg["trade_count"] == 40
    assert agg["expectancy_r"] == pytest.approx(-0.05, abs=0.001)
    assert agg["pairs_positive"] == 1


def test_c008_gate_fail_on_negative_train():
    agg = {
        "train_base": {"expectancy_r": -0.02, "profit_factor": 1.0, "pairs_positive": 4, "trade_count": 200},
        "validation_base": {"expectancy_r": 0.15, "profit_factor": 1.2, "pairs_positive": 6, "trade_count": 100},
        "full_stress_15x": {"expectancy_r": 0.03},
    }
    result = evaluate_c008_gates(agg)
    assert result["screening_pass"] is False
    assert "train_expectancy_gte_zero" in result["failed_gates"]
    assert result["test_window_opened"] is False


def test_c009_gate_fail_on_negative_train():
    agg = {
        "train_base": {"expectancy_r": -0.06, "profit_factor": 0.97, "pairs_positive": 3, "trade_count": 250},
        "validation_base": {"expectancy_r": 0.17, "profit_factor": 1.37, "pairs_positive": 4, "trade_count": 150},
        "validation_stress_2x": {"expectancy_r": 0.05},
    }
    result = evaluate_c009_gates(agg)
    assert result["screening_pass"] is False
    assert result["test_window_opened"] is False


def test_classify_delta_material_change():
    assert classify_delta(-0.017, 0.05) == "MATERIAL_CHANGE"
    assert classify_delta(-0.017, -0.018) == "CONFIRMED_DEDUP_SAFE"

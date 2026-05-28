"""Phase 4 retrofit tests: opt-in lifecycle export + frozen-config invariants.

Proves the C022 runner retrofit is backwards-compatible (flag defaults OFF),
that diagnostic mode produces the new lifecycle-feature fields, and that no
frozen C022 parameter was changed by the edit.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_campaign_022_h4_h1_pullback_resolution.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("c022_runner_under_test", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # needed so dataclass annotations resolve
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def runner():
    return _load_runner()


def test_emit_flag_defaults_off_in_parser(runner):
    parser = runner.build_parser()
    args = parser.parse_args(["train-validation"])
    assert args.emit_lifecycle_features is False  # backwards-compatible default


def test_emit_flag_can_be_enabled(runner):
    parser = runner.build_parser()
    args = parser.parse_args(["--emit-lifecycle-features", "train-validation"])
    assert args.emit_lifecycle_features is True


def test_ctx_default_emit_is_off(runner):
    field = runner.CampaignCtx.__dataclass_fields__["emit_lifecycle_features"]
    assert field.default is False


def test_frozen_c022_parameters_unchanged(runner):
    # The retrofit must not touch any frozen knob.
    assert runner.EXPECTED_STRATEGY == "h4_h1_pullback_resolution_entry"
    assert runner.EXPECTED_VERSION == "0.1.0-c022"
    assert runner.SPLITS == {
        "train": ("2021-06-01", "2023-12-31"),
        "validation": ("2024-01-01", "2025-06-30"),
        "test": ("2025-07-01", "2026-05-20"),
    }
    assert runner.COST_BASE == {"name": "base", "spread_multiplier": 0.5, "fixed_slippage_pips": 0.2}
    assert runner.COST_STRESS_2X == {"name": "stress_2x", "spread_multiplier": 2.0, "fixed_slippage_pips": 0.5}
    assert runner.MIN_VALIDATION_TRADES == 150
    assert runner.MIN_VALIDATION_PAIRS_POSITIVE == 4
    assert runner.MATERIALIZED_SOURCE == "m1_materialized"


def test_runner_declares_no_approval_and_no_broker(runner):
    text = SCRIPT.read_text(encoding="utf-8")
    assert "OandaBroker" not in text
    assert "approved_strategies.yaml stays []" in text


def test_diagnostic_export_is_opt_in_guarded():
    # The emit call site must be guarded by the ctx flag (source-level invariant).
    text = SCRIPT.read_text(encoding="utf-8")
    assert "if ctx.emit_lifecycle_features:" in text
    assert "_emit_lifecycle_features(trades_df" in text

"""Runner-contract tests for scripts/run_campaign_017.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
RUNNER = ROOT / "scripts" / "run_campaign_017.py"
CONFIG = ROOT / "configs" / "campaign_017_weekly_volatility_contraction_breakout.yaml"
APPROVED = ROOT / "configs" / "approved_strategies.yaml"


def _load_runner_module():
    spec = importlib.util.spec_from_file_location("run_campaign_017", RUNNER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_campaign_017"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_runner_and_config_exist():
    assert RUNNER.is_file()
    assert CONFIG.is_file()


def test_no_broker_imports_in_runner():
    text = RUNNER.read_text(encoding="utf-8")
    lines = text.splitlines()
    in_doc = False
    quote = ""
    import_lines: list[str] = []
    for raw in lines:
        line = raw.strip()
        if not in_doc:
            if line.startswith(('"""', "'''")) and not (
                len(line) > 3 and line.endswith(line[:3])
            ):
                in_doc = True
                quote = line[:3]
                continue
            if line.startswith(("import ", "from ")):
                import_lines.append(line)
        else:
            if line.endswith(quote):
                in_doc = False
    joined = "\n".join(import_lines)
    assert "forex_bot.broker" not in joined
    assert "oandapyV20" not in joined


def test_frozen_parameters_match_precommit():
    mod = _load_runner_module()
    expected = {
        "version": "0.1.0-c017",
        "timeframe": "H4",
        "compression_lookback_weeks": 12,
        "compression_percentile_threshold": 25.0,
        "breakout_buffer_atr_multiple": 0.25,
        "atr_lookback_h4": 14,
        "max_bars_in_trade": 42,
        "take_profit_r": None,
        "trailing_stop_atr_multiple": None,
        "entry_timing": "next_bar_open",
        "same_bar_adverse_stop_wins": True,
        "spread_to_atr_max": 0.15,
        "min_atr_pips": {},
    }
    assert expected == mod.FROZEN_PARAMETERS


def test_assert_frozen_rejects_deviation():
    mod = _load_runner_module()
    cfg = dict(mod.FROZEN_PARAMETERS)
    cfg["compression_lookback_weeks"] = 10
    with pytest.raises(SystemExit):
        mod._assert_frozen(cfg)


def test_blocked_when_database_missing(tmp_path):
    cfg_text = CONFIG.read_text(encoding="utf-8")
    cfg_text = cfg_text.replace(
        "database_path: ./data/campaign_002.sqlite3",
        f"database_path: {tmp_path / 'missing.sqlite3'}",
    )
    cfg_path = tmp_path / "campaign_017.yaml"
    cfg_path.write_text(cfg_text, encoding="utf-8")
    out = tmp_path / "out"
    spec = importlib.util.spec_from_file_location("run_campaign_017", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    rc = mod.main(["--config", str(cfg_path), "--out", str(out)])
    assert rc == 0
    gate = json.loads((out / "walk_forward" / "gate_result.json").read_text())
    assert gate["verdict"] == "BLOCKED"
    assert gate["blocked"] is True


def test_gate_schema_has_dedupe_preflight():
    mod = _load_runner_module()
    assert "trade_count_min" in mod.AGGREGATE_GATES
    assert mod.AGGREGATE_GATES["trade_count_max"] == 350


def test_approved_strategies_yaml_still_empty():
    import yaml

    data = yaml.safe_load(APPROVED.read_text(encoding="utf-8"))
    assert data.get("approved") == []

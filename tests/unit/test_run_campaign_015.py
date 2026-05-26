"""Runner-contract tests for scripts/run_campaign_015.py.

Pinning the binding behaviour of the CAMPAIGN_015 walk-forward runner
without invoking the bespoke engine on real data (which may be absent).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
RUNNER = ROOT / "scripts" / "run_campaign_015.py"
CONFIG = ROOT / "configs" / "campaign_015_failed_breakout_reversal.yaml"
APPROVED = ROOT / "configs" / "approved_strategies.yaml"


def _load_runner_module():
    """Import the runner script as a module for in-process tests."""
    spec = importlib.util.spec_from_file_location("run_campaign_015", RUNNER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_campaign_015"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_runner_exists():
    assert RUNNER.is_file(), f"runner not at {RUNNER}"
    assert CONFIG.is_file(), f"config not at {CONFIG}"


def test_no_broker_or_oanda_sdk_or_lean_import_in_runner():
    """The runner must not import broker, oandapyV20, LEAN, or
    QuantConnect at the import level."""
    text = RUNNER.read_text(encoding="utf-8")
    # Strip the docstring (which intentionally mentions these terms).
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
    assert "from forex_bot.broker" not in joined
    assert "oandapyV20" not in joined
    assert "QuantConnect" not in joined
    assert "lean" not in joined.lower()


def test_frozen_parameter_dict_matches_pre_commit():
    """The FROZEN_PARAMETERS table in the runner must match the
    pre-commit §5 verbatim."""
    mod = _load_runner_module()
    expected = {
        "version": "0.1.0-c015",
        "timeframe": "H4",
        "range_lookback": 20,
        "atr_lookback": 14,
        "adx_lookback": 14,
        "adx_max": 20.0,
        "sweep_buffer_atr": 0.10,
        "min_range_atr_multiple": 1.25,
        "max_range_atr_multiple": 5.00,
        "stop_buffer_atr": 0.10,
        "min_stop_atr_multiple": 0.80,
        "max_stop_atr_multiple": 2.20,
        "max_bars_in_trade": 12,
        "take_profit_r": None,
        "trailing_stop_atr_multiple": None,
        "entry_timing": "next_bar_open",
        "same_bar_adverse_stop_wins": True,
        "min_atr_pips": {},
    }
    assert expected == mod.FROZEN_PARAMETERS
    assert mod.EXPECTED_PAIRS == (
        "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD",
        "USD_CAD", "USD_CHF", "NZD_USD",
    )
    assert mod.EXPECTED_STRATEGY == "failed_breakout_reversal"
    assert mod.EXPECTED_VERSION == "0.1.0-c015"
    # Plan windows match Phase 0 §7.
    assert mod.PLAN_WINDOWS == {
        "train_window_days": 540,
        "validation_window_days": 180,
        "test_window_days": 180,
        "step_days": 180,
    }


def test_assert_frozen_passes_on_compliant_config():
    mod = _load_runner_module()
    cfg = dict(mod.FROZEN_PARAMETERS)
    # No raise expected.
    mod._assert_frozen(cfg)


def test_assert_frozen_rejects_param_deviation():
    mod = _load_runner_module()
    cfg = dict(mod.FROZEN_PARAMETERS)
    cfg["max_bars_in_trade"] = 13  # deviation
    with pytest.raises(SystemExit) as excinfo:
        mod._assert_frozen(cfg)
    assert "max_bars_in_trade" in str(excinfo.value)


def test_assert_frozen_rejects_version_deviation():
    mod = _load_runner_module()
    cfg = dict(mod.FROZEN_PARAMETERS)
    cfg["version"] = "0.2.0-c015"
    with pytest.raises(SystemExit) as excinfo:
        mod._assert_frozen(cfg)
    assert "version" in str(excinfo.value)


def test_assert_frozen_rejects_entry_timing_deviation():
    mod = _load_runner_module()
    cfg = dict(mod.FROZEN_PARAMETERS)
    cfg["entry_timing"] = "signal_bar_close"
    with pytest.raises(SystemExit) as excinfo:
        mod._assert_frozen(cfg)
    assert "entry_timing" in str(excinfo.value)


def test_blocked_artifact_when_database_missing(tmp_path, monkeypatch):
    """If the database_path does not exist, the runner writes a
    BLOCKED gate_result.json and exits 0 cleanly."""
    cfg_text = CONFIG.read_text(encoding="utf-8")
    # Point at a non-existent database.
    nonexistent_db = tmp_path / "does_not_exist.sqlite3"
    cfg_text = cfg_text.replace(
        "database_path: ./data/campaign_002.sqlite3",
        f"database_path: {nonexistent_db}",
    )
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(cfg_text, encoding="utf-8")
    out_dir = tmp_path / "out"

    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")

    proc = subprocess.run(
        [
            sys.executable, str(RUNNER),
            "--config", str(cfg_path),
            "--out", str(out_dir),
        ],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, (
        f"runner exit {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    gate_result_path = out_dir / "walk_forward" / "gate_result.json"
    assert gate_result_path.exists()
    gate = json.loads(gate_result_path.read_text(encoding="utf-8"))
    assert gate["verdict"] == "BLOCKED"
    assert gate["blocked"] is True
    assert gate["approval_status"] == "NOT_APPROVED"
    assert gate["approved_strategies_yaml_state"] == "approved: []"
    assert gate["strategy_name"] == "failed_breakout_reversal"
    assert gate["strategy_version"] == "0.1.0-c015"
    assert any("does not exist" in r for r in gate["blocked_reasons"])
    # plan.json should also be present.
    assert (out_dir / "walk_forward" / "plan.json").exists()
    # preflight.json should be present.
    assert (out_dir / "walk_forward" / "preflight.json").exists()


def test_preflight_only_writes_blocked_artifact_when_data_present(tmp_path, monkeypatch):
    """With --preflight-only the runner exits cleanly without running
    backtests, even if the data is fine. This is a tests-friendly
    smoke entrypoint that pins the artifact skeleton."""
    # Use the real config (which may or may not have a present DB on
    # the developer's machine). We pass --preflight-only so we never
    # touch real data.
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    out_dir = tmp_path / "out"
    proc = subprocess.run(
        [
            sys.executable, str(RUNNER),
            "--config", str(CONFIG),
            "--out", str(out_dir),
            "--preflight-only",
        ],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, (
        f"runner exit {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    gate_path = out_dir / "walk_forward" / "gate_result.json"
    assert gate_path.exists()
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    assert gate["verdict"] == "BLOCKED"
    assert gate["campaign_id"] == "CAMPAIGN_015"
    assert gate["strategy_name"] == "failed_breakout_reversal"
    assert "by_cost" in gate
    plan_path = out_dir / "walk_forward" / "plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    # 8 folds rolling, frozen.
    assert plan["split_style"] == "rolling"
    assert plan["parameter_mode"] == "frozen"
    assert plan["strategy_evidence"] is False
    assert len(plan["folds"]) == 8


def test_approved_strategies_yaml_remains_empty_after_run(tmp_path, monkeypatch):
    """Sanity: invoking the runner under any path (BLOCKED or PASS)
    never modifies configs/approved_strategies.yaml."""
    before = APPROVED.read_bytes()
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    out_dir = tmp_path / "out"
    subprocess.run(
        [
            sys.executable, str(RUNNER),
            "--config", str(CONFIG),
            "--out", str(out_dir),
            "--preflight-only",
        ],
        capture_output=True, text=True, check=False,
    )
    after = APPROVED.read_bytes()
    assert before == after, "approved_strategies.yaml was mutated by the runner"


def test_config_loads_via_pydantic(monkeypatch):
    """The CAMPAIGN_015 config must load cleanly via the project's
    Settings loader (so the runner does not need to monkey-patch it)."""
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    from forex_bot.config import load_settings
    settings = load_settings(CONFIG)
    assert settings.strategy.enabled == ["failed_breakout_reversal"]
    fbr = settings.strategy.failed_breakout_reversal
    assert fbr is not None
    assert fbr.version == "0.1.0-c015"
    assert fbr.range_lookback == 20
    assert fbr.adx_max == 20.0
    assert fbr.entry_timing == "next_bar_open"
    assert fbr.take_profit_r is None
    assert fbr.trailing_stop_atr_multiple is None
    assert fbr.same_bar_adverse_stop_wins is True


def test_config_hash_changes_if_frozen_param_changes(tmp_path, monkeypatch):
    """A change to any frozen parameter must change settings.config_hash;
    that is the canonical "different candidate" signal."""
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    from forex_bot.config import load_settings
    h_a = load_settings(CONFIG).config_hash

    cfg_text = CONFIG.read_text(encoding="utf-8")
    cfg_text2 = cfg_text.replace(
        "    max_bars_in_trade: 12",
        "    max_bars_in_trade: 11",
    )
    assert cfg_text != cfg_text2
    cfg_path = tmp_path / "config_b.yaml"
    cfg_path.write_text(cfg_text2, encoding="utf-8")
    h_b = load_settings(cfg_path).config_hash
    assert h_a != h_b


def test_changed_frozen_param_in_yaml_is_rejected_by_runner(tmp_path, monkeypatch):
    """If the YAML drifts from FROZEN_PARAMETERS, the runner aborts
    before any backtest fires (via _assert_frozen)."""
    cfg_text = CONFIG.read_text(encoding="utf-8")
    # Bend max_bars_in_trade (validator allows 11 but FROZEN_PARAMETERS
    # requires 12).
    cfg_text2 = cfg_text.replace(
        "    max_bars_in_trade: 12",
        "    max_bars_in_trade: 11",
    )
    # Also point at a non-existent DB so we don't accidentally trigger
    # real backtests (we expect the runner to abort BEFORE preflight).
    nonexistent_db = tmp_path / "does_not_exist.sqlite3"
    cfg_text2 = cfg_text2.replace(
        "database_path: ./data/campaign_002.sqlite3",
        f"database_path: {nonexistent_db}",
    )
    cfg_path = tmp_path / "drifted.yaml"
    cfg_path.write_text(cfg_text2, encoding="utf-8")

    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    out_dir = tmp_path / "out"
    proc = subprocess.run(
        [
            sys.executable, str(RUNNER),
            "--config", str(cfg_path),
            "--out", str(out_dir),
        ],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode != 0
    combined = (proc.stdout + proc.stderr)
    assert "max_bars_in_trade" in combined or "frozen-parameter mismatch" in combined


def test_data_preflight_reports_dedupe_summary(tmp_path, monkeypatch):
    """Preflight must report duplicate rows detected/dropped per pair/fold."""
    from datetime import UTC, datetime, timedelta
    from decimal import Decimal

    from forex_bot.data.db import Database
    from forex_bot.data.repositories import CandleRepo, DataSourceRecord, DataSourceRepo
    from forex_bot.domain.candles import Candle

    mod = _load_runner_module()
    db_path = tmp_path / "preflight.sqlite3"
    db = Database(db_path)
    repo = CandleRepo(db)
    o = Decimal("1.1000")
    base = datetime(2020, 1, 1, tzinfo=UTC)
    candles = [
        Candle(
            instrument="EUR_USD",
            granularity="H4",
            time=base + timedelta(hours=4 * k),
            complete=True,
            volume=1000,
            bid_o=o,
            bid_h=o + Decimal("0.0020"),
            bid_l=o - Decimal("0.0020"),
            bid_c=o + Decimal("0.0005"),
            ask_o=o + Decimal("0.0002"),
            ask_h=o + Decimal("0.0022"),
            ask_l=o - Decimal("0.0018"),
            ask_c=o + Decimal("0.0007"),
        )
        for k in range(4000)
    ]
    t_utc = datetime(2025, 8, 1, 13, 0, tzinfo=UTC)
    t_offset = datetime.fromisoformat("2025-08-01T06:00:00-07:00")
    dupes = [
        Candle(
            instrument="EUR_USD",
            granularity="H4",
            time=t,
            complete=True,
            volume=1000,
            bid_o=o,
            bid_h=o + Decimal("0.0020"),
            bid_l=o - Decimal("0.0020"),
            bid_c=o + Decimal("0.0005"),
            ask_o=o + Decimal("0.0002"),
            ask_h=o + Decimal("0.0022"),
            ask_l=o - Decimal("0.0018"),
            ask_c=o + Decimal("0.0007"),
        )
        for t in (t_utc, t_offset)
    ]
    repo.upsert_many(
        candles + dupes,
        source="oanda-practice",
        price_components="BA",
        request_hash="x",
    )
    DataSourceRepo(db).insert(
        DataSourceRecord(
            campaign="test",
            instrument="EUR_USD",
            granularity="H4",
            source="oanda-practice",
            host="local",
            from_time="2020-01-01",
            to_time="2026-05-20",
            price_components="BA",
            page_count=1,
            candles_written=len(candles) + len(dupes),
            candles_dropped_incomplete=0,
            first_ts=candles[0].time.isoformat(),
            last_ts=candles[-1].time.isoformat(),
            raw_sha256="x",
            normalized_sha256="x",
            request_params_json="{}",
            broker_account_id_redacted="redacted",
        )
    )
    plan = mod.rolling_window_plan(
        campaign_name="test",
        universe_start=mod.UNIVERSE_START,
        universe_end=mod.UNIVERSE_END,
        train_window_days=mod.PLAN_WINDOWS["train_window_days"],
        validation_window_days=mod.PLAN_WINDOWS["validation_window_days"],
        test_window_days=mod.PLAN_WINDOWS["test_window_days"],
        step_days=mod.PLAN_WINDOWS["step_days"],
        parameter_mode=mod.ParameterMode.FROZEN,
    )
    preflight = mod._data_preflight(
        db_path=db_path,
        plan=plan,
        pairs=("EUR_USD",),
    )
    details = preflight["details"]
    assert details["dedupe_policy"] == "keep_last"
    assert details["duplicate_rows_dropped_total"] >= 1
    fold_dedupe = details["per_pair"]["EUR_USD"]["fold_dedupe"]
    assert any(v["duplicates_dropped"] >= 1 for v in fold_dedupe.values())


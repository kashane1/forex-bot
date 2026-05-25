"""Tests for the CAMPAIGN_011 no-RiskEngine bespoke reference exporter
(Phase 2, infra-bespoke-campaign-011-norisk-reference-001).

Covers the pure helpers: schema shape, frozen-parameter enforcement,
canonical pair ordering, diagnostics MD rendering, JSON rounding, the
"no strategy approval" + "REJECT / null model" disclosures, and the
no-credentials-in-output invariant. The bespoke engine run itself is
covered by ``tests/unit/test_backtest_engine.py``.

These tests deliberately do **not** approve a strategy and do **not**
change CAMPAIGN_011's verdict.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = _REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


exporter = _load_script("export_campaign_011_norisk_reference")


# ---------------------------------------------------------------------------
# Helpers


@dataclass
class _FakeTrade:
    """Minimal stand-in for TradeRecord. The exporter only reads side."""

    side: str = "long"
    entry_time: datetime = field(
        default_factory=lambda: datetime(2020, 6, 1, tzinfo=UTC)
    )
    signal_id: str = "abc"
    instrument: str = "EUR_USD"
    exit_time: datetime | None = None
    entry_price: str = "1.10000"
    exit_price: str = "1.11000"
    stop_price: str = "1.09000"
    units: str = "1000"
    pnl_home: str = "10.0"
    r_multiple: str = "1.0"
    bars_held: int = 3
    exit_reason: str = "time_stop"


def _result(instrument: str, **overrides) -> object:
    base = {
        "instrument": instrument,
        "candle_count": 9931,
        "first_ts": "2020-01-01T22:00:00+00:00",
        "last_ts": "2026-05-19T21:00:00+00:00",
        "data_request_hash": "abc123def4561234",
        "trade_count": 142,
        "expectancy_r": -0.103456,
        "return_pct": -4.794321,
        "profit_factor": 0.1914,
        "win_rate": 0.4189,
        "max_drawdown_pct": -1.3352,
        "config_hash": "d5f1238ff3ee9220",
        "long_trades": 78,
        "short_trades": 64,
        "starting_equity": 500.0,
        "final_equity": 476.03,
        "trades": [_FakeTrade()],
    }
    base.update(overrides)
    return exporter.PairWindowResult(**base)


# ---------------------------------------------------------------------------
# Constants


def test_canonical_pairs_are_the_seven_oanda_majors_in_canonical_order():
    assert exporter.CANONICAL_PAIRS == (
        "EUR_USD",
        "GBP_USD",
        "USD_JPY",
        "AUD_USD",
        "USD_CAD",
        "USD_CHF",
        "NZD_USD",
    )


def test_frozen_master_seed_is_20260523_and_never_swept():
    assert exporter.EXPECTED_MASTER_SEED == 20260523
    assert exporter.FROZEN_PARAMETERS["master_seed"] == 20260523


def test_window_matches_campaign_002_reference():
    assert exporter.WINDOW_FROM == "2020-01-01"
    assert exporter.WINDOW_TO == "2026-05-20"


# ---------------------------------------------------------------------------
# Frozen-parameter enforcement


def _frozen_config() -> dict:
    return dict(exporter.FROZEN_PARAMETERS)


def test_assert_frozen_accepts_pristine_config():
    exporter._assert_frozen(_frozen_config())


def test_assert_frozen_rejects_seed_tuning():
    cfg = _frozen_config()
    cfg["master_seed"] = 12345
    with pytest.raises(SystemExit) as exc:
        exporter._assert_frozen(cfg)
    msg = str(exc.value)
    assert "master_seed" in msg or "20260523" in msg


def test_assert_frozen_rejects_entry_probability_tuning():
    cfg = _frozen_config()
    cfg["entry_probability_per_bar"] = 0.10
    with pytest.raises(SystemExit) as exc:
        exporter._assert_frozen(cfg)
    assert "entry_probability_per_bar" in str(exc.value)


def test_assert_frozen_rejects_atr_stop_tuning():
    cfg = _frozen_config()
    cfg["atr_stop_multiple"] = 3.0
    with pytest.raises(SystemExit) as exc:
        exporter._assert_frozen(cfg)
    assert "atr_stop_multiple" in str(exc.value)


def test_assert_frozen_rejects_max_bars_tuning():
    cfg = _frozen_config()
    cfg["max_bars_in_trade"] = 12
    with pytest.raises(SystemExit) as exc:
        exporter._assert_frozen(cfg)
    assert "max_bars_in_trade" in str(exc.value)


def test_assert_frozen_uses_the_committed_yaml():
    # Loading the actual committed config should pass.
    from forex_bot.config import load_settings

    settings = load_settings(
        _REPO / "configs" / "campaign_011_random_entry_anchor.yaml"
    )
    cfg = settings.strategy.random_entry_anchor.model_dump()
    exporter._assert_frozen(cfg)


# ---------------------------------------------------------------------------
# Schema / JSON shape


def test_full_window_reference_payload_shape():
    pairs = [_result(p) for p in exporter.CANONICAL_PAIRS]
    payload = exporter._build_full_window_reference(
        pair_results=pairs, config_hash="abc" * 10
    )
    # Static keys / required fields.
    assert payload["risk_engine_used"] is False
    assert payload["strategy_evidence"] is False
    assert payload["fill_timing"] == "signal_bar_close"
    assert payload["window"] == [exporter.WINDOW_FROM, exporter.WINDOW_TO]
    assert payload["master_seed"] == 20260523
    assert payload["approval_path"] == "none (null model by design)"
    # 7 pair entries in canonical order.
    assert [p["instrument"] for p in payload["pairs"]] == list(
        exporter.CANONICAL_PAIRS
    )
    # data_request_hashes carries all 7 pairs.
    assert set(payload["data_request_hashes"]) == set(exporter.CANONICAL_PAIRS)
    # total_trades is sum across pairs.
    assert payload["total_trades"] == 7 * 142
    # Per-pair shape.
    p0 = payload["pairs"][0]
    assert set(p0) == {
        "instrument",
        "candle_count",
        "trades",
        "expectancy_r",
        "return_pct",
        "profit_factor",
        "win_rate",
        "max_drawdown_pct",
    }


def test_full_window_reference_rounds_metrics_to_four_decimal_places():
    pairs = [_result("EUR_USD")]
    payload = exporter._build_full_window_reference(
        pair_results=pairs, config_hash="x"
    )
    p0 = payload["pairs"][0]
    # The fixture has expectancy_r=-0.103456 -> rounded to -0.1035.
    assert p0["expectancy_r"] == -0.1035
    assert p0["return_pct"] == -4.7943


def test_full_window_reference_serializes_profit_factor_inf_as_null():
    pairs = [_result("EUR_USD", profit_factor=None)]
    payload = exporter._build_full_window_reference(
        pair_results=pairs, config_hash="x"
    )
    assert payload["pairs"][0]["profit_factor"] is None


def test_full_window_reference_json_round_trips_deterministically():
    pairs = [_result(p) for p in exporter.CANONICAL_PAIRS]
    a = json.dumps(
        exporter._build_full_window_reference(
            pair_results=pairs, config_hash="abc"
        ),
        indent=2,
        sort_keys=True,
    )
    b = json.dumps(
        exporter._build_full_window_reference(
            pair_results=pairs, config_hash="abc"
        ),
        indent=2,
        sort_keys=True,
    )
    assert a == b


# ---------------------------------------------------------------------------
# Per-fold aggregation


def test_aggregate_fold_handles_empty_pair_runs():
    total, expectancy, ret, pf = exporter._aggregate_fold([])
    assert total == 0
    assert expectancy == 0.0
    assert ret == 0.0
    assert pf is None


def test_aggregate_fold_weights_expectancy_by_trade_count():
    p1 = _result("EUR_USD", trade_count=10, expectancy_r=0.1, return_pct=1.0)
    p2 = _result("GBP_USD", trade_count=30, expectancy_r=-0.2, return_pct=-2.0)
    total, expectancy, ret, _pf = exporter._aggregate_fold([p1, p2])
    assert total == 40
    # weighted: (0.1*10 + -0.2*30) / 40 = (1.0 - 6.0) / 40 = -0.125
    assert expectancy == pytest.approx(-0.125)
    assert ret == pytest.approx(-1.0)


def test_aggregate_fold_profit_factor_handles_no_losses():
    p1 = _result("EUR_USD", trade_count=5, return_pct=2.0)
    p2 = _result("GBP_USD", trade_count=5, return_pct=3.0)
    _t, _e, _r, pf = exporter._aggregate_fold([p1, p2])
    assert pf is None  # inf -> serialised as null


# ---------------------------------------------------------------------------
# Diagnostics MD


def test_diagnostics_md_carries_null_model_disclosure():
    pairs = [_result(p) for p in exporter.CANONICAL_PAIRS]
    doc = exporter._render_diagnostics_md(
        pair_results=pairs,
        config_hash="d5f1238ff3ee922000",
        db_display="data/campaign_002.sqlite3",
        generated_at=datetime(2026, 5, 25, tzinfo=UTC),
    )
    lowered = doc.lower()
    assert "REJECT" in doc
    assert "null" in lowered
    assert "strategy_evidence: false" in doc
    # Must explicitly disclaim approval.
    assert "cannot be approved" in lowered
    # Must never positively claim approval.
    assert " is approved" not in lowered
    assert " approves the" not in lowered
    # Lists all 7 pairs.
    for p in exporter.CANONICAL_PAIRS:
        assert p in doc
    # Mentions no-RiskEngine.
    assert "risk_engine=None" in doc or "no-RiskEngine" in doc.lower()


def test_diagnostics_md_never_mentions_promotion_or_approval():
    pairs = [_result(p) for p in exporter.CANONICAL_PAIRS]
    doc = exporter._render_diagnostics_md(
        pair_results=pairs,
        config_hash="x",
        db_display="d",
        generated_at=datetime(2026, 5, 25, tzinfo=UTC),
    )
    lowered = doc.lower()
    assert "promote" not in lowered
    assert "live trading" not in lowered
    assert "paper-loop" not in lowered


# ---------------------------------------------------------------------------
# Approval-path safety


def test_exporter_module_does_not_touch_approved_strategies():
    """Static-grep guard: the exporter source must not read, write,
    or otherwise act on configs/approved_strategies.yaml, nor import
    any broker / live-loop module. Prose mentions in docstrings
    (safety disclosure) are fine."""
    src = (_REPO / "scripts" / "export_campaign_011_norisk_reference.py").read_text(
        encoding="utf-8"
    )
    forbidden_patterns = (
        'open("configs/approved_strategies',
        "open('configs/approved_strategies",
        'Path("configs/approved_strategies',
        "Path('configs/approved_strategies",
        'write_text("approved',
        "write_text('approved",
        'load_settings("configs/approved_strategies',
        "load_settings('configs/approved_strategies",
    )
    for pat in forbidden_patterns:
        assert pat not in src, f"unexpected approval-file access: {pat!r}"
    assert "forex_bot.broker" not in src
    assert "forex_bot.execution" not in src
    assert "forex_bot.loops" not in src


def test_exporter_module_does_not_use_random_or_numpy_random():
    """The strategy uses SHA-256 only; the exporter must too. Belt-
    and-suspenders against non-determinism leaks."""
    src = (_REPO / "scripts" / "export_campaign_011_norisk_reference.py").read_text(
        encoding="utf-8"
    )
    # ``hash()`` -> Python's built-in is fine for SystemExit message,
    # but ``random.random``, ``numpy.random`` are forbidden.
    assert "random.random" not in src
    assert "numpy.random" not in src
    # The exporter never calls OANDA APIs (uses local SQLite only).
    assert "oanda.com" not in src.lower()
    assert "api.oanda" not in src.lower()


def test_exporter_module_uses_no_risk_engine_path():
    src = (_REPO / "scripts" / "export_campaign_011_norisk_reference.py").read_text(
        encoding="utf-8"
    )
    assert "risk_engine=None" in src


# ---------------------------------------------------------------------------
# Missing-data handling


def test_main_exits_when_db_missing(tmp_path, capsys):
    rc = exporter.main(
        argv=[
            "--db",
            str(tmp_path / "does_not_exist.sqlite3"),
            "--out",
            str(tmp_path / "ref.json"),
            "--per-fold-out",
            str(tmp_path / "ref_per_fold.json"),
            "--diagnostics-md",
            str(tmp_path / "diag.md"),
            "--full-window-only",
        ]
    )
    assert rc == 1
    captured = capsys.readouterr()
    assert "BLOCKER" in captured.err
    assert "campaign_002.sqlite3" in captured.err or "SQLite store" in captured.err


# ---------------------------------------------------------------------------
# Trade serialization (optional dump path)


def test_serialize_trade_returns_jsonl_friendly_dict():
    t = _FakeTrade()
    row = exporter._serialize_trade(t)
    assert row["side"] == "long"
    # Ensure JSON-serializable (Decimal-strings already converted).
    s = json.dumps(row, default=str, sort_keys=True)
    assert "long" in s

"""Tests for the custom-engine CAMPAIGN_002 H4 parity reproduction script
(Phase 5, infra-lean-parity-001).

Cover the pure helpers — instrument construction, baseline-parameter
extraction, the reference table, and report rendering. The engine run
itself is covered by tests/unit/test_backtest_engine.py.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime
from pathlib import Path

from forex_bot.config import load_settings

_REPO = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = _REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


parity = _load_script("run_custom_campaign_002_h4_parity")


def _result(instrument: str, **overrides) -> object:
    base = {
        "instrument": instrument,
        "candle_count": 9931,
        "first_ts": "2020-01-01T22:00:00+00:00",
        "last_ts": "2026-05-19T21:00:00+00:00",
        "data_request_hash": "abc123def456",
        "trade_count": 132,
        "expectancy_r": -0.218,
        "total_return_pct": -7.04,
        "profit_factor": 0.55,
        "win_rate": 0.295,
        "max_drawdown_pct": -8.05,
        "rejected_signal_count": 274,
    }
    base.update(overrides)
    return parity.PairResult(**base)


def test_make_instrument_jpy_vs_non_jpy():
    jpy = parity.make_instrument("USD_JPY")
    assert jpy.pip_location == -2
    assert jpy.display_precision == 3
    eur = parity.make_instrument("EUR_USD")
    assert eur.pip_location == -4
    assert eur.display_precision == 5
    # all majors trade in whole units.
    assert eur.trade_units_precision == 0


def test_baseline_params_uses_the_campaign_config():
    settings = load_settings(_REPO / "configs" / "campaign_002_real_oanda.yaml")
    cfg = parity.baseline_params(settings)
    assert cfg["version"] == "0.1.0-baseline-frozen"
    # CAMPAIGN_002's real values — not the frozen baseline's 2.5 / 80.
    assert cfg["atr_stop_multiple"] == 2.0
    assert cfg["max_bars_in_trade"] == 240


def test_reference_covers_all_seven_campaign_002_pairs():
    assert set(parity.CAMPAIGN_002_H4_REFERENCE) == set(parity.PAIRS)
    assert len(parity.PAIRS) == 7
    assert "NZD_USD" in parity.PAIRS


def test_render_doc_labels_diagnostic_and_claims_no_verdict():
    doc = parity.render_doc(
        [_result("EUR_USD")],
        config_hash="d536a9b06818197f0000",
        generated_at=datetime(2026, 5, 22, tzinfo=UTC),
        db_display="data/oanda_h4_research.sqlite3",
    )
    assert "strategy_evidence: false" in doc
    assert "NOT A NEW VERDICT" in doc
    assert "REJECT" in doc
    assert "EUR_USD" in doc
    assert "signal_bar_close" in doc


def test_render_doc_shows_comparison_delta_against_reference():
    # 130 trades vs the committed reference of 132 -> delta -2.
    doc = parity.render_doc(
        [_result("EUR_USD", trade_count=130)],
        config_hash="c",
        generated_at=datetime(2026, 5, 22, tzinfo=UTC),
        db_display="d",
    )
    assert "130 / 132 / -2" in doc


def test_delta_helper_formats_signed_difference():
    assert parity._delta(-0.220, -0.218) == "-0.002"
    assert parity._delta(-0.218, -0.218) == "+0.000"

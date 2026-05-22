"""Tests for the Lean parity comparison harness
(Phase 3, infra-lean-parity-run-001).

Fixture Lean-output scenarios: exact match passes, small drift warns,
large drift fails, a missing instrument fails, malformed output fails.
"""

from __future__ import annotations

import importlib.util
import sys
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


cmp = _load_script("compare_lean_campaign_002_parity")


def _summary(pairs: list[dict]) -> dict:
    return {
        "parity_target": "CAMPAIGN_002 H4 trend_following baseline",
        "risk_engine_used": False,
        "total_trades": sum(p["trades"] for p in pairs),
        "pairs": pairs,
    }


# --------------------------------------------------------------------------
# compare — PASS / WARN / FAIL
# --------------------------------------------------------------------------


def test_exact_match_passes():
    pairs = [{"instrument": "EUR_USD", "trades": 233, "expectancy_r": -0.196,
              "return_pct": -10.83}]
    report = cmp.compare(_summary(pairs), _summary(pairs))
    assert report.status == "OK"


def test_small_drift_warns():
    ref = _summary([{"instrument": "EUR_USD", "trades": 233,
                     "expectancy_r": -0.196, "return_pct": -10.83}])
    # 233 -> 250 is +7.3% — inside the WARN band (5%-15%).
    lean = _summary([{"instrument": "EUR_USD", "trades": 250,
                      "expectancy_r": -0.196, "return_pct": -10.83}])
    report = cmp.compare(ref, lean)
    assert report.status == "WARN"


def test_large_drift_fails():
    ref = _summary([{"instrument": "EUR_USD", "trades": 233,
                     "expectancy_r": -0.196, "return_pct": -10.83}])
    lean = _summary([{"instrument": "EUR_USD", "trades": 500,
                      "expectancy_r": -0.196, "return_pct": -10.83}])
    report = cmp.compare(ref, lean)
    assert report.status == "FAIL"


def test_expectancy_drift_fails():
    ref = _summary([{"instrument": "EUR_USD", "trades": 233, "expectancy_r": -0.196}])
    lean = _summary([{"instrument": "EUR_USD", "trades": 233, "expectancy_r": 0.5}])
    report = cmp.compare(ref, lean)
    assert report.status == "FAIL"


def test_missing_instrument_fails():
    ref = _summary([{"instrument": "EUR_USD", "trades": 233},
                    {"instrument": "GBP_USD", "trades": 215}])
    lean = _summary([{"instrument": "EUR_USD", "trades": 233}])
    report = cmp.compare(ref, lean)
    assert report.status == "FAIL"
    gbp = next(p for p in report.pairs if p.instrument == "GBP_USD")
    assert gbp.found is False
    assert gbp.status == "FAIL"


# --------------------------------------------------------------------------
# load_lean_result — malformed output
# --------------------------------------------------------------------------


def test_malformed_json_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(cmp.MalformedLeanOutputError):
        cmp.load_lean_result(bad)


def test_missing_pairs_list_raises(tmp_path):
    bad = tmp_path / "x.json"
    bad.write_text('{"engine": "lean"}', encoding="utf-8")
    with pytest.raises(cmp.MalformedLeanOutputError):
        cmp.load_lean_result(bad)


def test_pair_without_required_keys_raises(tmp_path):
    bad = tmp_path / "x.json"
    bad.write_text('{"pairs": [{"instrument": "EUR_USD"}]}', encoding="utf-8")
    with pytest.raises(cmp.MalformedLeanOutputError):
        cmp.load_lean_result(bad)


def test_load_lean_result_accepts_a_directory(tmp_path):
    (tmp_path / "parity_summary.json").write_text(
        '{"pairs": [{"instrument": "EUR_USD", "trades": 1}]}', encoding="utf-8"
    )
    data = cmp.load_lean_result(tmp_path)
    assert data["pairs"][0]["instrument"] == "EUR_USD"


# --------------------------------------------------------------------------
# reference + no-Lean mode
# --------------------------------------------------------------------------


def test_committed_reference_is_no_risk_engine_and_seven_pairs():
    ref = cmp.load_reference(cmp.DEFAULT_REFERENCE)
    assert ref["risk_engine_used"] is False
    assert len(ref["pairs"]) == 7
    assert ref["total_trades"] == 1647


def test_render_no_lean_describes_expected_shape():
    ref = _summary([{"instrument": "EUR_USD", "trades": 233}])
    doc = cmp.render_no_lean(ref, generated_at=datetime(2026, 5, 22, tzinfo=UTC))
    assert "parity_summary.json" in doc
    assert "strategy_evidence: false" in doc

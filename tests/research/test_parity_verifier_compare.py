"""Tests for the comparison harness.

The comparison logic is exercised against synthesized verifier and
bespoke shapes — the real bespoke reference is also loaded once to
exercise the full-shape path. Tests cover the OK / WARN / FAIL ladder,
missing-pair detection, BLOCKED reports, and the divergence-
classification rails.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from research.parity_verifier.compare import blocked_report, compare
from research.parity_verifier.data_loader import (
    DEFAULT_BESPOKE_REFERENCE_PATH,
    load_bespoke_reference,
)
from research.parity_verifier.models import (
    ComparisonStatus,
    DivergenceClassification,
    PairResult,
    VerifierResult,
)


def _result(*, pairs: list[PairResult], total: int | None = None) -> VerifierResult:
    return VerifierResult(
        parity_target="x",
        risk_engine_used=False,
        fill_timing="signal_bar_close",
        window_start=datetime(2020, 1, 1, tzinfo=UTC),
        window_end=datetime(2026, 5, 20, tzinfo=UTC),
        config_hash="x",
        strategy_evidence=False,
        total_trades=total if total is not None else sum(p.trades for p in pairs),
        pairs=pairs,
    )


def _bespoke(pairs: list[dict], total: int | None = None) -> dict:
    if total is None:
        total = sum(p.get("trades", 0) for p in pairs)
    return {
        "parity_target": "x",
        "pairs": pairs,
        "total_trades": total,
    }


def test_perfect_match_is_ok() -> None:
    verifier = _result(pairs=[
        PairResult(instrument="EUR_USD", candle_count=10, trades=100,
                   expectancy_r=-0.196, return_pct=-10.83),
        PairResult(instrument="GBP_USD", candle_count=10, trades=200,
                   expectancy_r=-0.097, return_pct=-5.12),
    ])
    bespoke = _bespoke([
        {"instrument": "EUR_USD", "trades": 100,
         "expectancy_r": -0.196, "return_pct": -10.83},
        {"instrument": "GBP_USD", "trades": 200,
         "expectancy_r": -0.097, "return_pct": -5.12},
    ])
    report = compare(
        verifier=verifier,
        bespoke_reference=bespoke,
        bespoke_reference_path="bespoke.json",
    )
    assert report.overall_status is ComparisonStatus.OK
    assert report.overall_classification is DivergenceClassification.NONE
    assert all(p.status is ComparisonStatus.OK for p in report.pairs)
    assert report.total_trade_count_delta_pct == pytest.approx(0.0)


def test_trade_count_within_5_pct_is_ok() -> None:
    verifier = _result(pairs=[
        PairResult(instrument="EUR_USD", candle_count=10, trades=104,
                   expectancy_r=-0.196, return_pct=-10.83),
    ])
    bespoke = _bespoke([
        {"instrument": "EUR_USD", "trades": 100,
         "expectancy_r": -0.196, "return_pct": -10.83},
    ])
    report = compare(
        verifier=verifier,
        bespoke_reference=bespoke,
        bespoke_reference_path="bespoke.json",
    )
    # 4% delta -> still OK
    assert report.pairs[0].status is ComparisonStatus.OK


def test_trade_count_10_pct_is_warn() -> None:
    verifier = _result(pairs=[
        PairResult(instrument="EUR_USD", candle_count=10, trades=110,
                   expectancy_r=-0.196, return_pct=-10.83),
    ])
    bespoke = _bespoke([
        {"instrument": "EUR_USD", "trades": 100,
         "expectancy_r": -0.196, "return_pct": -10.83},
    ])
    report = compare(
        verifier=verifier,
        bespoke_reference=bespoke,
        bespoke_reference_path="bespoke.json",
    )
    assert report.pairs[0].status is ComparisonStatus.WARN
    assert report.overall_status is ComparisonStatus.WARN


def test_trade_count_50_pct_is_fail() -> None:
    verifier = _result(pairs=[
        PairResult(instrument="EUR_USD", candle_count=10, trades=150,
                   expectancy_r=-0.196, return_pct=-10.83),
    ])
    bespoke = _bespoke([
        {"instrument": "EUR_USD", "trades": 100,
         "expectancy_r": -0.196, "return_pct": -10.83},
    ])
    report = compare(
        verifier=verifier,
        bespoke_reference=bespoke,
        bespoke_reference_path="bespoke.json",
    )
    assert report.pairs[0].status is ComparisonStatus.FAIL
    assert report.overall_status is ComparisonStatus.FAIL


def test_expectancy_drift_classified_correctly() -> None:
    verifier = _result(pairs=[
        PairResult(instrument="EUR_USD", candle_count=10, trades=100,
                   expectancy_r=-0.100, return_pct=-10.83),  # 0.096 from bespoke -0.196
    ])
    bespoke = _bespoke([
        {"instrument": "EUR_USD", "trades": 100,
         "expectancy_r": -0.196, "return_pct": -10.83},
    ])
    report = compare(
        verifier=verifier,
        bespoke_reference=bespoke,
        bespoke_reference_path="bespoke.json",
    )
    assert report.pairs[0].status is ComparisonStatus.WARN  # 0.096 in WARN band


def test_return_pct_drift_is_fail_when_beyond_2pp() -> None:
    verifier = _result(pairs=[
        PairResult(instrument="EUR_USD", candle_count=10, trades=100,
                   expectancy_r=-0.196, return_pct=0.0),  # 10.83 pp from bespoke
    ])
    bespoke = _bespoke([
        {"instrument": "EUR_USD", "trades": 100,
         "expectancy_r": -0.196, "return_pct": -10.83},
    ])
    report = compare(
        verifier=verifier,
        bespoke_reference=bespoke,
        bespoke_reference_path="bespoke.json",
    )
    assert report.pairs[0].status is ComparisonStatus.FAIL


def test_missing_pair_is_fail_and_data_mismatch() -> None:
    verifier = _result(pairs=[])
    bespoke = _bespoke([
        {"instrument": "EUR_USD", "trades": 100,
         "expectancy_r": -0.196, "return_pct": -10.83},
    ])
    report = compare(
        verifier=verifier,
        bespoke_reference=bespoke,
        bespoke_reference_path="bespoke.json",
    )
    assert report.pairs[0].status is ComparisonStatus.FAIL
    assert report.pairs[0].classification is DivergenceClassification.DATA_MISMATCH
    assert report.overall_status is ComparisonStatus.FAIL
    assert any("missing" in note.lower() for note in report.notes)


def test_pair_status_is_worst_of_metrics() -> None:
    verifier = _result(pairs=[
        PairResult(instrument="EUR_USD", candle_count=10, trades=101,  # OK
                   expectancy_r=-0.196, return_pct=-10.83),
        PairResult(instrument="GBP_USD", candle_count=10, trades=150,  # FAIL on count
                   expectancy_r=-0.097, return_pct=-5.12),
    ])
    bespoke = _bespoke([
        {"instrument": "EUR_USD", "trades": 100,
         "expectancy_r": -0.196, "return_pct": -10.83},
        {"instrument": "GBP_USD", "trades": 100,
         "expectancy_r": -0.097, "return_pct": -5.12},
    ])
    report = compare(
        verifier=verifier,
        bespoke_reference=bespoke,
        bespoke_reference_path="bespoke.json",
    )
    assert report.overall_status is ComparisonStatus.FAIL


def test_blocked_report_carries_bespoke_side_and_reason() -> None:
    bespoke = _bespoke([
        {"instrument": "EUR_USD", "trades": 100,
         "expectancy_r": -0.196, "return_pct": -10.83},
        {"instrument": "GBP_USD", "trades": 200,
         "expectancy_r": -0.097, "return_pct": -5.12},
    ])
    report = blocked_report(
        bespoke_reference_path="bespoke.json",
        bespoke_reference=bespoke,
        reason="all seven CSVs are absent locally",
    )
    assert report.overall_status is ComparisonStatus.BLOCKED
    assert all(p.status is ComparisonStatus.BLOCKED for p in report.pairs)
    assert report.bespoke_total_trades == 300
    assert report.verifier_total_trades is None
    assert "all seven" in report.notes[0]


def test_full_shape_against_real_bespoke_reference() -> None:
    """Smoke: the comparison harness runs against the committed bespoke
    reference (1647 trades, 7 pairs) without crashing. The verifier
    side reports zero trades — predictably FAIL, but the harness must
    handle the seven-pair fan-out cleanly."""

    bespoke = load_bespoke_reference(DEFAULT_BESPOKE_REFERENCE_PATH)
    empty_verifier = _result(pairs=[
        PairResult(instrument=p["instrument"], candle_count=0, trades=0)
        for p in bespoke["pairs"]
    ])
    report = compare(
        verifier=empty_verifier,
        bespoke_reference=bespoke,
        bespoke_reference_path=str(DEFAULT_BESPOKE_REFERENCE_PATH),
    )
    assert len(report.pairs) == 7
    assert report.overall_status is ComparisonStatus.FAIL  # -100% on every pair
    assert report.bespoke_total_trades == 1647
    assert report.verifier_total_trades == 0


def test_compare_handles_none_expectancy_gracefully() -> None:
    """Some pairs may lack expectancy on the verifier side (no trades
    closed). The comparison should not crash and should not promote
    that into a FAIL purely because of the None."""

    verifier = _result(pairs=[
        PairResult(instrument="EUR_USD", candle_count=10, trades=0,
                   expectancy_r=None, return_pct=None),
    ])
    bespoke = _bespoke([
        {"instrument": "EUR_USD", "trades": 0,
         "expectancy_r": None, "return_pct": None},
    ])
    report = compare(
        verifier=verifier,
        bespoke_reference=bespoke,
        bespoke_reference_path="bespoke.json",
    )
    # trade_count delta is None (divide by zero), so FAIL on count;
    # expectancy/return both None -> neutral OK.
    assert report.pairs[0].status is ComparisonStatus.FAIL
    assert report.pairs[0].trade_count_delta_pct is None

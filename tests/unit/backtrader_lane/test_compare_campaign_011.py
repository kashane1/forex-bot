"""Phase 2 CAMPAIGN_011 comparison-harness fixture tests.

The existing `research/backtrader_lane/compare.py` is campaign-agnostic
and handles the CAMPAIGN_011 reference shape unchanged (the JSON is a
top-level `pairs[]` array with `instrument / trades / expectancy_r /
return_pct / profit_factor / win_rate / max_drawdown_pct` per entry).
These tests prove that with **synthetic dicts that match the committed
schema** — no real run is performed here.

Fixture tests cover the divergence labels the sprint-004 plan requires:

- exact-match PASS
- trade-count drift → SIGNAL_RULE_MISMATCH (seed mismatch / timestamp
  mismatch surface this way because they perturb which bars enter)
- expectancy-R drift → SIZING_OR_PNL_MISMATCH
- missing reference → FileNotFoundError
- unsupported field handling (BT summary missing a metric)

`strategy_evidence: false`. CAMPAIGN_011 remains REJECT.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.backtrader_lane.compare import (  # noqa: E402
    DivergenceLabel,
    Tolerances,
    compare,
)

# CAMPAIGN_011-specific tight tolerances (from
# docs/research/CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md §9).
CAMPAIGN_011_TIGHT_TOLERANCES = Tolerances(
    trade_count_pct=0.0,    # exact trade-count match
    expectancy_r=0.0050,
    return_pct=0.10,
    win_rate=0.0010,
)

CANONICAL_PAIRS = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)


# ---------------------------------------------------------------------------
# Synthetic reference / BT-summary builders


def _bespoke_pair(instrument: str, **overrides: Any) -> dict[str, Any]:
    base = {
        "instrument": instrument,
        "candle_count": 9931,
        "trades": 400,
        "expectancy_r": 0.0,
        "return_pct": 0.0,
        "profit_factor": 1.0,
        "win_rate": 0.5,
        "max_drawdown_pct": -1.0,
    }
    base.update(overrides)
    return base


def _bt_pair_summary(instrument: str, **overrides: Any) -> dict[str, Any]:
    """Mirror the runner.py `_build_summary` per-pair shape."""

    base = {
        "instrument": instrument,
        "candle_count": 9931,
        "trades": 400,
        "wins": 200,
        "losses": 200,
        "win_rate": 0.5,
        "pnl_account_total": 0.0,
        "final_cash": 500.0,
        "starting_cash": 500.0,
        "analyzer": {"closed_trades": 400},
        # Optional fields the campaign-011 comparison reads directly.
        "expectancy_r": 0.0,
        "return_pct": 0.0,
    }
    base.update(overrides)
    return base


def _write_campaign_011_reference(
    path: Path, pair_overrides: dict[str, dict[str, Any]] | None = None
) -> None:
    """Write a CAMPAIGN_011-shaped reference JSON."""

    pair_overrides = pair_overrides or {}
    pairs = []
    for name in CANONICAL_PAIRS:
        overrides = pair_overrides.get(name, {})
        pairs.append(_bespoke_pair(name, **overrides))
    payload = {
        "parity_target": "CAMPAIGN_011 H4 random_entry_anchor null-model baseline",
        "risk_engine_used": False,
        "fill_timing": "signal_bar_close",
        "window": ["2020-01-01", "2026-05-20"],
        "master_seed": 20260523,
        "config_hash": "abcdef0123456789",
        "data_request_hashes": {p: "00" * 8 for p in CANONICAL_PAIRS},
        "strategy_evidence": False,
        "approval_path": "none (null model by design)",
        "total_trades": sum(p["trades"] for p in pairs),
        "pairs": pairs,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_bt_summary(
    path: Path, pair_overrides: dict[str, dict[str, Any]] | None = None
) -> None:
    """Write a runner-shaped backtrader_summary.json."""

    pair_overrides = pair_overrides or {}
    pairs = []
    for name in CANONICAL_PAIRS:
        overrides = pair_overrides.get(name, {})
        pairs.append(_bt_pair_summary(name, **overrides))
    payload = {
        "campaign_id": "CAMPAIGN_011",
        "strategy_id": "random_entry_anchor",
        "strategy_version": "0.1.0-c011",
        "starting_equity_usd": 500.0,
        "total_trades": sum(p["trades"] for p in pairs),
        "total_pnl_account": sum(p["pnl_account_total"] for p in pairs),
        "pairs": pairs,
        "blocked_instruments": [],
        "strategy_evidence": False,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


# ---------------------------------------------------------------------------
# Tests


def test_exact_match_summary_classifies_pass(tmp_path: Path) -> None:
    """A BT summary exactly equal (per pair) to the bespoke reference
    must classify as PASS under tight CAMPAIGN_011 tolerances."""

    ref_path = tmp_path / "ref.json"
    bt_path = tmp_path / "bt.json"
    _write_campaign_011_reference(ref_path)
    _write_bt_summary(bt_path)
    report = compare(
        backtrader_summary_path=bt_path,
        bespoke_reference_path=ref_path,
        tolerances=CAMPAIGN_011_TIGHT_TOLERANCES,
    )
    assert report.campaign_id == "CAMPAIGN_011"
    assert report.bt_total_trades == report.bespoke_total_trades == 7 * 400
    assert report.overall_classification == DivergenceLabel.PASS
    for p in report.pair_results:
        assert p.classification == DivergenceLabel.PASS, (
            f"{p.instrument}: {p.classification}"
        )


def test_trade_count_drift_raises_signal_rule_mismatch(tmp_path: Path) -> None:
    """A 30%+ trade-count drift on one pair classifies as
    SIGNAL_RULE_MISMATCH at the per-pair level and propagates to overall."""

    ref_path = tmp_path / "ref.json"
    bt_path = tmp_path / "bt.json"
    _write_campaign_011_reference(ref_path)
    _write_bt_summary(bt_path, pair_overrides={"EUR_USD": {"trades": 600}})  # +50%
    report = compare(
        backtrader_summary_path=bt_path,
        bespoke_reference_path=ref_path,
        tolerances=CAMPAIGN_011_TIGHT_TOLERANCES,
    )
    eur = next(p for p in report.pair_results if p.instrument == "EUR_USD")
    assert eur.classification == DivergenceLabel.SIGNAL_RULE_MISMATCH
    assert report.overall_classification == DivergenceLabel.SIGNAL_RULE_MISMATCH


def test_seed_perturbation_surfaces_as_trade_count_mismatch(tmp_path: Path) -> None:
    """A wrong seed in the BT adapter would yield a different set of
    bars selected by the entry gate, so trade counts diverge. Simulate
    this with a Δ in trades and verify the harness flags it."""

    ref_path = tmp_path / "ref.json"
    bt_path = tmp_path / "bt.json"
    _write_campaign_011_reference(ref_path)
    # Different seed → different bars selected. Even a small Δ violates
    # exact-trade-count requirement.
    _write_bt_summary(bt_path, pair_overrides={"GBP_USD": {"trades": 410}})  # +2.5%
    report = compare(
        backtrader_summary_path=bt_path,
        bespoke_reference_path=ref_path,
        tolerances=CAMPAIGN_011_TIGHT_TOLERANCES,
    )
    gbp = next(p for p in report.pair_results if p.instrument == "GBP_USD")
    # 2.5% > 0% tight band; under the wider 10% band metric drift is
    # checked. Trades-only drift maps to TOLERABLE_DRIFT (wider band).
    assert gbp.classification in (
        DivergenceLabel.TOLERABLE_DRIFT,
        DivergenceLabel.SIGNAL_RULE_MISMATCH,
    )
    # Whatever the per-pair label, overall must not be PASS.
    assert report.overall_classification != DivergenceLabel.PASS


def test_expectancy_r_drift_raises_sizing_or_pnl_mismatch(tmp_path: Path) -> None:
    """Trade count matches exactly but R drifts → SIZING_OR_PNL_MISMATCH.
    This is the failure mode sprint 003 caught for CAMPAIGN_002 USD-base
    pairs; the BT-lane R formula now matches bespoke and the new adapter
    inherits that fix, so we use a fabricated R drift to exercise the
    classifier."""

    ref_path = tmp_path / "ref.json"
    bt_path = tmp_path / "bt.json"
    _write_campaign_011_reference(ref_path)
    _write_bt_summary(bt_path, pair_overrides={"USD_JPY": {"expectancy_r": 0.10}})
    report = compare(
        backtrader_summary_path=bt_path,
        bespoke_reference_path=ref_path,
        tolerances=CAMPAIGN_011_TIGHT_TOLERANCES,
    )
    jpy = next(p for p in report.pair_results if p.instrument == "USD_JPY")
    # Expectancy R Δ = 0.10 > 0.0050 (tight) and > 0.06 (wider) →
    # SIZING_OR_PNL_MISMATCH.
    assert jpy.classification == DivergenceLabel.SIZING_OR_PNL_MISMATCH


def test_missing_reference_raises(tmp_path: Path) -> None:
    bt_path = tmp_path / "bt.json"
    _write_bt_summary(bt_path)
    with pytest.raises(FileNotFoundError):
        compare(
            backtrader_summary_path=bt_path,
            bespoke_reference_path=tmp_path / "does_not_exist.json",
            tolerances=CAMPAIGN_011_TIGHT_TOLERANCES,
        )


def test_missing_bt_summary_raises(tmp_path: Path) -> None:
    ref_path = tmp_path / "ref.json"
    _write_campaign_011_reference(ref_path)
    with pytest.raises(FileNotFoundError):
        compare(
            backtrader_summary_path=tmp_path / "does_not_exist.json",
            bespoke_reference_path=ref_path,
            tolerances=CAMPAIGN_011_TIGHT_TOLERANCES,
        )


def test_bt_summary_missing_expectancy_r_falls_back_gracefully(
    tmp_path: Path,
) -> None:
    """If the BT summary's pair entry omits `expectancy_r` (which the
    current runner emits as an optional field), the harness should still
    classify on trade-count + return %."""

    ref_path = tmp_path / "ref.json"
    bt_path = tmp_path / "bt.json"
    _write_campaign_011_reference(ref_path)
    pairs = []
    for name in CANONICAL_PAIRS:
        # Strip expectancy_r from each pair.
        entry = _bt_pair_summary(name)
        entry.pop("expectancy_r", None)
        entry.pop("return_pct", None)
        pairs.append(entry)
    payload = {
        "campaign_id": "CAMPAIGN_011",
        "strategy_id": "random_entry_anchor",
        "strategy_version": "0.1.0-c011",
        "starting_equity_usd": 500.0,
        "total_trades": sum(p["trades"] for p in pairs),
        "total_pnl_account": 0.0,
        "pairs": pairs,
        "blocked_instruments": [],
        "strategy_evidence": False,
    }
    bt_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    report = compare(
        backtrader_summary_path=bt_path,
        bespoke_reference_path=ref_path,
        tolerances=CAMPAIGN_011_TIGHT_TOLERANCES,
    )
    # No crash; per-pair classification = PASS because trade counts +
    # win rates match and the optional fields are absent.
    assert report.overall_classification == DivergenceLabel.PASS


def test_campaign_011_reference_loads_via_committed_file(tmp_path: Path) -> None:
    """The actually-committed campaign_011_h4_bespoke_reference.json
    loads cleanly into the compare harness. Use a synthetic BT summary
    that matches it exactly per pair so the classification is PASS."""

    ref_path = (
        ROOT
        / "research"
        / "lean_parity"
        / "campaign_011_h4_bespoke_reference.json"
    )
    assert ref_path.exists(), "committed bespoke reference must exist"

    ref = json.loads(ref_path.read_text(encoding="utf-8"))
    pairs_bt = []
    for entry in ref["pairs"]:
        pairs_bt.append(
            {
                "instrument": entry["instrument"],
                "candle_count": entry["candle_count"],
                "trades": entry["trades"],
                "wins": int(entry["trades"] * entry["win_rate"]),
                "losses": entry["trades"] - int(entry["trades"] * entry["win_rate"]),
                "win_rate": entry["win_rate"],
                "pnl_account_total": 0.0,
                "final_cash": 500.0,
                "starting_cash": 500.0,
                "analyzer": {"closed_trades": entry["trades"]},
                "expectancy_r": entry["expectancy_r"],
                "return_pct": entry["return_pct"],
            }
        )
    bt_summary = {
        "campaign_id": "CAMPAIGN_011",
        "strategy_id": "random_entry_anchor",
        "strategy_version": "0.1.0-c011",
        "starting_equity_usd": 500.0,
        "total_trades": sum(p["trades"] for p in pairs_bt),
        "total_pnl_account": 0.0,
        "pairs": pairs_bt,
        "blocked_instruments": [],
        "strategy_evidence": False,
    }
    bt_path = tmp_path / "bt.json"
    bt_path.write_text(json.dumps(bt_summary, indent=2, sort_keys=True), encoding="utf-8")

    report = compare(
        backtrader_summary_path=bt_path,
        bespoke_reference_path=ref_path,
        tolerances=CAMPAIGN_011_TIGHT_TOLERANCES,
    )
    assert report.bt_total_trades == ref["total_trades"] == 2800
    assert report.overall_classification == DivergenceLabel.PASS


def test_one_pair_blocked_propagates_to_overall(tmp_path: Path) -> None:
    """If the BT side reports a blocked instrument, the harness lifts
    the overall classification to BLOCKED unless something worse is
    happening on the other pairs."""

    ref_path = tmp_path / "ref.json"
    bt_path = tmp_path / "bt.json"
    _write_campaign_011_reference(ref_path)
    # Build a BT summary with only 6 pairs (EUR_USD missing) + a blocked list.
    pairs_bt = [_bt_pair_summary(n) for n in CANONICAL_PAIRS if n != "EUR_USD"]
    payload = {
        "campaign_id": "CAMPAIGN_011",
        "strategy_id": "random_entry_anchor",
        "strategy_version": "0.1.0-c011",
        "starting_equity_usd": 500.0,
        "total_trades": sum(p["trades"] for p in pairs_bt),
        "total_pnl_account": 0.0,
        "pairs": pairs_bt,
        "blocked_instruments": ["EUR_USD"],
        "strategy_evidence": False,
    }
    bt_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    report = compare(
        backtrader_summary_path=bt_path,
        bespoke_reference_path=ref_path,
        tolerances=CAMPAIGN_011_TIGHT_TOLERANCES,
    )
    eur = next(p for p in report.pair_results if p.instrument == "EUR_USD")
    assert eur.classification == DivergenceLabel.BLOCKED
    assert report.overall_classification == DivergenceLabel.BLOCKED

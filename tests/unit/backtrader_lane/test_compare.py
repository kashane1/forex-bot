"""Phase 5 comparison-harness tests.

Synthetic fixtures (tiny dicts) exercise every documented divergence
label. The harness is pure (no I/O beyond reading the two JSON inputs)
so the tests don't require Backtrader.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.backtrader_lane.compare import (  # noqa: E402
    DivergenceLabel,
    Tolerances,
    classify_pair,
    compare,
    render_markdown,
    to_json_dict,
)


def test_classify_pair_pass() -> None:
    label, notes, deltas = classify_pair(
        bt_trades=100,
        bespoke_trades=100,
        bt_expectancy_r=-0.10,
        bespoke_expectancy_r=-0.10,
        bt_return_pct=-1.0,
        bespoke_return_pct=-1.0,
        bt_win_rate=0.30,
        bespoke_win_rate=0.30,
    )
    assert label == DivergenceLabel.PASS
    assert deltas["trades_delta_pct"] == 0.0
    assert deltas["expectancy_r_delta"] == 0.0


def test_classify_pair_tolerable_drift_trade_count() -> None:
    # 8% trade-count drift is outside the tight band but inside the wider band.
    label, notes, _ = classify_pair(
        bt_trades=108,
        bespoke_trades=100,
        bt_expectancy_r=-0.10,
        bespoke_expectancy_r=-0.10,
        bt_return_pct=-1.0,
        bespoke_return_pct=-1.0,
        bt_win_rate=0.30,
        bespoke_win_rate=0.30,
    )
    assert label == DivergenceLabel.TOLERABLE_DRIFT


def test_classify_pair_signal_rule_mismatch() -> None:
    # 30% trade-count drift is beyond the wider band.
    label, _, _ = classify_pair(
        bt_trades=130,
        bespoke_trades=100,
        bt_expectancy_r=-0.10,
        bespoke_expectancy_r=-0.10,
        bt_return_pct=-1.0,
        bespoke_return_pct=-1.0,
        bt_win_rate=0.30,
        bespoke_win_rate=0.30,
    )
    assert label == DivergenceLabel.SIGNAL_RULE_MISMATCH


def test_classify_pair_sizing_or_pnl_mismatch() -> None:
    # Trade count matches; expectancy R differs significantly.
    label, _, _ = classify_pair(
        bt_trades=100,
        bespoke_trades=100,
        bt_expectancy_r=-0.05,
        bespoke_expectancy_r=-0.20,
        bt_return_pct=-1.0,
        bespoke_return_pct=-1.0,
        bt_win_rate=0.30,
        bespoke_win_rate=0.30,
    )
    assert label == DivergenceLabel.SIZING_OR_PNL_MISMATCH


def test_classify_pair_blocked_on_missing_data() -> None:
    label, _, _ = classify_pair(
        bt_trades=None,
        bespoke_trades=100,
        bt_expectancy_r=None,
        bespoke_expectancy_r=-0.10,
        bt_return_pct=None,
        bespoke_return_pct=-1.0,
        bt_win_rate=None,
        bespoke_win_rate=0.30,
    )
    assert label == DivergenceLabel.BLOCKED


def test_classify_pair_tight_band_holds_with_some_metrics_missing() -> None:
    # When some metrics are None on either side, the harness must not
    # raise; it should still classify based on the available metrics.
    label, _, _ = classify_pair(
        bt_trades=100,
        bespoke_trades=100,
        bt_expectancy_r=None,
        bespoke_expectancy_r=None,
        bt_return_pct=None,
        bespoke_return_pct=None,
        bt_win_rate=None,
        bespoke_win_rate=None,
    )
    assert label == DivergenceLabel.PASS


def _write_bt_summary(path: Path, pairs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "campaign_id": "CAMPAIGN_002",
                "strategy_id": "trend_following",
                "strategy_version": "0.1.0-baseline-frozen",
                "starting_equity_usd": 500.0,
                "total_trades": sum(p.get("trades", 0) for p in pairs),
                "total_pnl_account": 0.0,
                "pairs": pairs,
                "blocked_instruments": [],
                "strategy_evidence": False,
                "dry_run": False,
            }
        ),
        encoding="utf-8",
    )


def _write_bespoke_ref(path: Path, pairs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "parity_target": "CAMPAIGN_002 H4 trend_following baseline",
                "risk_engine_used": False,
                "total_trades": sum(p["trades"] for p in pairs),
                "pairs": pairs,
                "strategy_evidence": False,
            }
        ),
        encoding="utf-8",
    )


def test_compare_overall_pass_on_matching_fixtures(tmp_path: Path) -> None:
    bt_path = tmp_path / "bt" / "backtrader_summary.json"
    ref_path = tmp_path / "bespoke_reference.json"
    pairs = [{"instrument": "EUR_USD", "trades": 233, "expectancy_r": -0.196}]
    _write_bt_summary(bt_path, pairs)
    _write_bespoke_ref(ref_path, pairs)
    report = compare(backtrader_summary_path=bt_path, bespoke_reference_path=ref_path)
    assert report.overall_classification == DivergenceLabel.PASS
    assert report.bt_total_trades == 233
    assert report.bespoke_total_trades == 233


def test_compare_overall_signal_rule_mismatch(tmp_path: Path) -> None:
    bt_path = tmp_path / "bt" / "backtrader_summary.json"
    ref_path = tmp_path / "bespoke_reference.json"
    _write_bt_summary(
        bt_path,
        [{"instrument": "EUR_USD", "trades": 500, "expectancy_r": -0.196}],
    )
    _write_bespoke_ref(
        ref_path,
        [{"instrument": "EUR_USD", "trades": 233, "expectancy_r": -0.196}],
    )
    report = compare(backtrader_summary_path=bt_path, bespoke_reference_path=ref_path)
    assert report.overall_classification == DivergenceLabel.SIGNAL_RULE_MISMATCH


def test_compare_blocked_when_pair_only_in_one_side(tmp_path: Path) -> None:
    bt_path = tmp_path / "bt" / "backtrader_summary.json"
    ref_path = tmp_path / "bespoke_reference.json"
    _write_bt_summary(bt_path, [])
    _write_bespoke_ref(
        ref_path,
        [{"instrument": "EUR_USD", "trades": 233, "expectancy_r": -0.196}],
    )
    report = compare(backtrader_summary_path=bt_path, bespoke_reference_path=ref_path)
    assert report.overall_classification == DivergenceLabel.BLOCKED
    pair_eur = next(p for p in report.pair_results if p.instrument == "EUR_USD")
    assert pair_eur.classification == DivergenceLabel.BLOCKED


def test_compare_raises_when_inputs_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        compare(
            backtrader_summary_path=tmp_path / "missing.json",
            bespoke_reference_path=tmp_path / "also_missing.json",
        )


def test_render_markdown_contains_divergence_label_and_strategy_evidence_false(
    tmp_path: Path,
) -> None:
    bt_path = tmp_path / "bt" / "backtrader_summary.json"
    ref_path = tmp_path / "bespoke_reference.json"
    pairs = [{"instrument": "EUR_USD", "trades": 233, "expectancy_r": -0.196}]
    _write_bt_summary(bt_path, pairs)
    _write_bespoke_ref(ref_path, pairs)
    report = compare(backtrader_summary_path=bt_path, bespoke_reference_path=ref_path)
    md = render_markdown(report)
    assert "PASS" in md
    assert "strategy_evidence: false" in md
    assert "EUR_USD" in md


def test_to_json_dict_contains_strategy_evidence_false(tmp_path: Path) -> None:
    bt_path = tmp_path / "bt" / "backtrader_summary.json"
    ref_path = tmp_path / "bespoke_reference.json"
    _write_bt_summary(
        bt_path,
        [{"instrument": "EUR_USD", "trades": 233, "expectancy_r": -0.196}],
    )
    _write_bespoke_ref(
        ref_path,
        [{"instrument": "EUR_USD", "trades": 233, "expectancy_r": -0.196}],
    )
    report = compare(backtrader_summary_path=bt_path, bespoke_reference_path=ref_path)
    payload = to_json_dict(report)
    assert payload["strategy_evidence"] is False
    assert payload["overall_classification"] in {label.value for label in DivergenceLabel}


def test_tolerances_dataclass_defaults() -> None:
    t = Tolerances()
    assert t.trade_count_pct == 5.0
    assert t.expectancy_r == 0.03
    assert t.return_pct == 0.5
    assert t.win_rate == 0.05


def test_compare_does_not_mutate_inputs(tmp_path: Path) -> None:
    bt_path = tmp_path / "bt" / "backtrader_summary.json"
    ref_path = tmp_path / "bespoke_reference.json"
    pairs = [{"instrument": "EUR_USD", "trades": 233, "expectancy_r": -0.196}]
    _write_bt_summary(bt_path, pairs)
    _write_bespoke_ref(ref_path, pairs)
    before_bt = bt_path.read_text(encoding="utf-8")
    before_ref = ref_path.read_text(encoding="utf-8")
    compare(backtrader_summary_path=bt_path, bespoke_reference_path=ref_path)
    assert bt_path.read_text(encoding="utf-8") == before_bt
    assert ref_path.read_text(encoding="utf-8") == before_ref


def test_compare_imports_no_forex_bot_or_broker() -> None:
    import research.backtrader_lane.compare as mod

    src = Path(mod.__file__).read_text(encoding="utf-8")
    for line in src.splitlines():
        clean = line.split("#", 1)[0].strip()
        if clean.startswith("import ") or clean.startswith("from "):
            assert "forex_bot" not in clean
            forbidden = (
                "backtrader.brokers.oandabroker",
                "backtrader.stores.oandastore",
                "backtrader.feeds.oanda",
                "import quantconnect",
                "from quantconnect",
                "import lean",
                "from lean ",
            )
            for needle in forbidden:
                assert needle not in clean


def test_compare_script_runs_end_to_end(tmp_path: Path) -> None:
    bt_path = tmp_path / "bt" / "backtrader_summary.json"
    ref_path = tmp_path / "bespoke_reference.json"
    out_dir = tmp_path / "compare_out"
    pairs = [{"instrument": "EUR_USD", "trades": 233, "expectancy_r": -0.196}]
    _write_bt_summary(bt_path, pairs)
    _write_bespoke_ref(ref_path, pairs)

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "scripts._compare_backtrader_parity",
        ROOT / "scripts" / "compare_backtrader_parity.py",
    )
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    rc = mod.main(
        [
            "--campaign",
            "CAMPAIGN_002",
            "--backtrader-results",
            str(bt_path),
            "--bespoke-reference",
            str(ref_path),
            "--output",
            str(out_dir),
        ]
    )
    assert rc == 0
    assert (out_dir / "comparison_summary.json").exists()
    assert (out_dir / "comparison_summary.md").exists()
    payload = json.loads((out_dir / "comparison_summary.json").read_text(encoding="utf-8"))
    assert payload["overall_classification"] == "PASS"

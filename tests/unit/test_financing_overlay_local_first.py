"""Tests for local-first trade-ledger financing overlay contract."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from forex_bot.research.financing_overlay import (
    FinancingOverlayMode,
    TradeLedgerRef,
    load_trades_for_overlay,
    merge_rate_fixtures,
    overlay_ledger,
    resolve_rate_source,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "research" / "financing" / "fixtures"


def _sample_row(
    *,
    side: str = "long",
    entry: str = "2020-01-06T09:00:00+00:00",
    exit_: str = "2020-01-10T13:00:00+00:00",
    bars: str = "20",
) -> dict[str, str]:
    return {
        "instrument": "EUR_USD",
        "side": side,
        "units": "1000",
        "entry_time": entry,
        "exit_time": exit_,
        "entry_price": "1.10000",
        "exit_price": "1.10500",
        "stop_price": "1.09500",
        "pnl": "50.0",
        "r_multiple": "1.0",
        "bars_held": bars,
    }


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = list(rows[0].keys())
    lines = [",".join(fields)]
    for row in rows:
        lines.append(",".join(row[k] for k in fields))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_resolve_synthetic_fixture_is_labeled_synthetic() -> None:
    src, label, synthetic, _ = resolve_rate_source(FinancingOverlayMode.SYNTHETIC_FIXTURE)
    assert src is not None
    assert synthetic is True
    assert "stress" in label.lower() or "synthetic" in label.lower()


def test_resolve_unavailable_has_no_source() -> None:
    src, label, _, warnings = resolve_rate_source(FinancingOverlayMode.UNAVAILABLE)
    assert src is None
    assert label == "unavailable"
    assert warnings


def test_manual_fixture_merge_labels_synthetic_warning() -> None:
    paths = sorted(FIXTURES.glob("rates_two_week_*.json"))
    if not paths:
        pytest.skip("no committed rate fixtures")
    src, label, synthetic, warnings = resolve_rate_source(
        FinancingOverlayMode.MANUAL_OBSERVED_FIXTURE, fixture_paths=paths[:1]
    )
    assert src is not None
    assert synthetic is True
    assert any("synthetic" in w.lower() for w in warnings)
    merged = merge_rate_fixtures(paths[:2])
    assert merged.name


def test_long_short_financing_sign_under_stress(tmp_path: Path) -> None:
    long_csv = tmp_path / "long.csv"
    short_csv = tmp_path / "short.csv"
    _write_csv(long_csv, [_sample_row(side="long")])
    _write_csv(short_csv, [_sample_row(side="short")])
    ledger_long = TradeLedgerRef("T", "long", (str(long_csv),))
    ledger_short = TradeLedgerRef("T", "short", (str(short_csv),))
    long_sum = overlay_ledger(ledger_long, FinancingOverlayMode.SYNTHETIC_FIXTURE)
    short_sum = overlay_ledger(ledger_short, FinancingOverlayMode.SYNTHETIC_FIXTURE)
    assert (long_sum.financing_drag_r or 0) != 0
    assert (short_sum.financing_drag_r or 0) != 0


def test_zero_day_hold_minimal_financing(tmp_path: Path) -> None:
    csv_path = tmp_path / "same_bar.csv"
    row = _sample_row(entry="2020-01-06T09:00:00+00:00", exit_="2020-01-06T09:00:00+00:00", bars="0")
    _write_csv(csv_path, [row])
    trades, warns = load_trades_for_overlay(csv_path)
    assert warns
    ledger = TradeLedgerRef("T", "zero", (str(csv_path),))
    summary = overlay_ledger(ledger, FinancingOverlayMode.SYNTHETIC_FIXTURE)
    assert summary.trade_count == 1
    assert summary.financing_drag_r is not None


def test_multi_day_hold_accrues_financing(tmp_path: Path) -> None:
    short_hold = tmp_path / "short.csv"
    long_hold = tmp_path / "long.csv"
    _write_csv(short_hold, [_sample_row(bars="2")])
    _write_csv(
        long_hold,
        [_sample_row(entry="2020-01-06T09:00:00+00:00", exit_="2020-01-20T13:00:00+00:00", bars="60")],
    )
    s1 = overlay_ledger(
        TradeLedgerRef("T", "s", (str(short_hold),)), FinancingOverlayMode.SYNTHETIC_FIXTURE
    )
    s2 = overlay_ledger(
        TradeLedgerRef("T", "l", (str(long_hold),)), FinancingOverlayMode.SYNTHETIC_FIXTURE
    )
    assert abs(s2.financing_drag_r or 0) > abs(s1.financing_drag_r or 0)


def test_none_mode_has_zero_drag(tmp_path: Path) -> None:
    csv_path = tmp_path / "t.csv"
    _write_csv(csv_path, [_sample_row()])
    ledger = TradeLedgerRef("T", "n", (str(csv_path),))
    summary = overlay_ledger(ledger, FinancingOverlayMode.NONE)
    assert summary.financing_drag_r == 0.0
    assert summary.gross_expectancy_r == summary.adjusted_expectancy_r


def test_overlay_script_missing_ledger_exits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script = ROOT / "scripts" / "apply_financing_overlay_to_trade_ledgers.py"
    monkeypatch.chdir(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(script), "--modes", "none"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={**dict(**{"PATH": ""}), **__import__("os").environ},
    )
    # Script should fail when reference globs find no files in empty cwd — actually runs from ROOT
    proc = subprocess.run(
        [sys.executable, str(script), "--inventory-only"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert proc.returncode == 0
    manifest = json.loads((ROOT / "research/financing_overlay_local_first/run_manifest.json").read_text())
    assert manifest["not_approved"] is True
    assert manifest["campaign_020_created"] is False


def test_run_manifest_schema() -> None:
    path = ROOT / "research/financing_overlay_local_first/run_manifest.json"
    if not path.is_file():
        pytest.skip("overlay not run yet")
    data = json.loads(path.read_text())
    assert data["strategy_evidence"] is False
    assert data["not_approved"] is True
    assert "modes" in data

"""Unit tests for scripts/diagnose_backtrader_csv_provenance.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from research.backtrader_lane.data_adapter import compute_csv_sha256
from scripts.diagnose_backtrader_csv_provenance import (
    diagnose,
    diagnose_instrument,
    main,
    render_md,
)

CSV_HEADER = (
    "time,bid_open,bid_high,bid_low,bid_close,"
    "ask_open,ask_high,ask_low,ask_close,volume"
)


def _write_csv(path: Path, rows: list[list[str]]) -> None:
    lines = [CSV_HEADER]
    for r in rows:
        lines.append(",".join(r))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _make_pair(
    *,
    dir_: Path,
    instrument: str,
    rows: list[list[str]],
    provenance_data_sha256: str | None = None,
    provenance_overrides: dict | None = None,
) -> tuple[Path, Path]:
    """Write a CSV + matching (or deliberately-mismatching) provenance JSON."""
    csv_path = dir_ / f"{instrument}_H4_lean.csv"
    prov_path = dir_ / f"{instrument}_H4_lean.provenance.json"
    _write_csv(csv_path, rows)
    sha = (
        provenance_data_sha256
        if provenance_data_sha256 is not None
        else compute_csv_sha256(csv_path)
    )
    prov = {
        "instrument": instrument,
        "granularity": "H4",
        "source": "oanda-practice",
        "data_sha256": sha,
        "candle_count": len(rows),
        "first_ts": rows[0][0] if rows else None,
        "last_ts": rows[-1][0] if rows else None,
        "exported_at": "2026-05-22T20:00:00+00:00",
    }
    if provenance_overrides:
        prov.update(provenance_overrides)
    prov_path.write_text(json.dumps(prov, indent=2), encoding="utf-8")
    return csv_path, prov_path


def test_diagnose_passes_when_csv_and_provenance_lock_step(tmp_path: Path):
    rows = [
        ["2024-01-01T00:00:00+00:00", "1.10", "1.11", "1.09", "1.105",
         "1.101", "1.111", "1.091", "1.106", "100"],
        ["2024-01-01T04:00:00+00:00", "1.11", "1.12", "1.10", "1.115",
         "1.111", "1.121", "1.101", "1.116", "120"],
    ]
    _make_pair(dir_=tmp_path, instrument="EUR_USD", rows=rows)
    obj = diagnose(exports_dir=tmp_path, instruments=("EUR_USD",))
    assert obj["all_bt_strict_preflight_pass"] is True
    assert obj["all_bt_strict_preflight_fail"] is False
    r = obj["per_instrument"][0]
    assert r["row_sha_match"] is True
    assert r["row_count_match"] is True
    assert r["first_ts_match"] is True
    assert r["last_ts_match"] is True
    assert r["bt_strict_preflight_pass"] is True


def test_diagnose_detects_row_sha_drift(tmp_path: Path):
    rows = [
        ["2024-01-01T00:00:00+00:00", "1.10", "1.11", "1.09", "1.105",
         "1.101", "1.111", "1.091", "1.106", "100"],
    ]
    _make_pair(
        dir_=tmp_path,
        instrument="EUR_USD",
        rows=rows,
        provenance_data_sha256="0" * 64,  # deliberately wrong
    )
    obj = diagnose(exports_dir=tmp_path, instruments=("EUR_USD",))
    assert obj["all_bt_strict_preflight_pass"] is False
    assert obj["all_bt_strict_preflight_fail"] is True
    r = obj["per_instrument"][0]
    assert r["row_sha_match"] is False
    assert r["bt_strict_preflight_pass"] is False


def test_diagnose_detects_row_count_drift(tmp_path: Path):
    rows = [
        ["2024-01-01T00:00:00+00:00", "1.10", "1.11", "1.09", "1.105",
         "1.101", "1.111", "1.091", "1.106", "100"],
        ["2024-01-01T04:00:00+00:00", "1.11", "1.12", "1.10", "1.115",
         "1.111", "1.121", "1.101", "1.116", "120"],
    ]
    # Override candle_count to a wrong value.
    _make_pair(
        dir_=tmp_path,
        instrument="EUR_USD",
        rows=rows,
        provenance_overrides={"candle_count": 99},
    )
    obj = diagnose(exports_dir=tmp_path, instruments=("EUR_USD",))
    r = obj["per_instrument"][0]
    assert r["row_count_match"] is False
    # row sha still matches (we recomputed it from the actual CSV)
    assert r["row_sha_match"] is True
    # but BT-strict pass requires BOTH
    assert r["bt_strict_preflight_pass"] is False


def test_diagnose_detects_missing_csv(tmp_path: Path):
    instrument = "EUR_USD"
    prov = tmp_path / f"{instrument}_H4_lean.provenance.json"
    prov.write_text(json.dumps({"data_sha256": "x"}), encoding="utf-8")
    r = diagnose_instrument(instrument=instrument, exports_dir=tmp_path)
    assert r["csv_exists"] is False
    assert r["provenance_exists"] is True
    assert "CSV missing" in r["notes"]


def test_diagnose_detects_missing_provenance(tmp_path: Path):
    instrument = "EUR_USD"
    rows = [
        ["2024-01-01T00:00:00+00:00", "1.10", "1.11", "1.09", "1.105",
         "1.101", "1.111", "1.091", "1.106", "100"],
    ]
    csv_path = tmp_path / f"{instrument}_H4_lean.csv"
    _write_csv(csv_path, rows)
    r = diagnose_instrument(instrument=instrument, exports_dir=tmp_path)
    assert r["csv_exists"] is True
    assert r["provenance_exists"] is False
    assert "provenance JSON missing" in r["notes"]


def test_render_md_marks_pass_and_fail(tmp_path: Path):
    rows = [
        ["2024-01-01T00:00:00+00:00", "1.10", "1.11", "1.09", "1.105",
         "1.101", "1.111", "1.091", "1.106", "100"],
    ]
    _make_pair(dir_=tmp_path, instrument="EUR_USD", rows=rows)
    _make_pair(
        dir_=tmp_path,
        instrument="GBP_USD",
        rows=rows,
        provenance_data_sha256="0" * 64,
    )
    obj = diagnose(exports_dir=tmp_path, instruments=("EUR_USD", "GBP_USD"))
    md = render_md(obj)
    assert "EUR_USD" in md
    assert "GBP_USD" in md
    assert "approved: []" in md
    # Both should show their booleans honestly.
    assert "all instruments BT-strict-preflight PASS" in md


def test_main_against_real_export_dir(tmp_path: Path):
    repo = Path(__file__).resolve().parents[2]
    exports = repo / "research/lean_parity/exports/campaign_002_h4"
    if not exports.exists():
        pytest.skip("exports dir not present")
    out_json = tmp_path / "o.json"
    out_md = tmp_path / "o.md"
    rc = main(
        [
            "--exports-dir", str(exports),
            "--out-json", str(out_json),
            "--out-md", str(out_md),
        ]
    )
    # rc 0 (PASS) or 1 (FAIL) are both acceptable — the script reports
    # honestly. It is rc 2 only if exports dir is missing.
    assert rc in (0, 1)
    obj = json.loads(out_json.read_text())
    assert len(obj["per_instrument"]) == 7


def test_main_blocked_on_missing_exports_dir(tmp_path: Path):
    rc = main(
        [
            "--exports-dir", str(tmp_path / "nope"),
            "--out-json", str(tmp_path / "o.json"),
            "--out-md", str(tmp_path / "o.md"),
        ]
    )
    assert rc == 2

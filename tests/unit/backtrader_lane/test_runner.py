"""Phase 3 runner-contract tests.

Exercises the Backtrader-lane runner end-to-end against the tiny
deterministic fixture in `tests/unit/backtrader_lane/fixtures/`.

These tests prove the runner:

- emits exactly the documented artefacts,
- writes a deterministic JSONL trade list on the fixture,
- handles missing data cleanly (BLOCKED, no fake trade),
- raises `KeyError` on unknown campaign id,
- does not leak any OANDA env-var name or value into the manifest,
- imports no broker / LEAN module.

`strategy_evidence: false`.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("backtrader")

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.backtrader_lane import runner  # noqa: E402

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
EXPECTED_ARTIFACTS = (
    "run_manifest.json",
    "backtrader_summary.json",
    "backtrader_trades.jsonl",
    "backtrader_metrics.json",
    "run_log_summary.md",
)


def _smoke_options(tmp_path: Path, **overrides) -> runner.RunOptions:
    base = {
        "campaign_id": "SMOKE_FIXTURE",
        "output_dir": tmp_path,
        "instruments": None,
        "data_export_dir": FIXTURE_DIR,
        "starting_equity_usd": None,
        "dry_run": False,
        "strict_data": True,
    }
    base.update(overrides)
    return runner.RunOptions(**base)


def test_smoke_campaign_is_registered() -> None:
    assert "SMOKE_FIXTURE" in runner.list_campaigns()


def test_unknown_campaign_raises_key_error() -> None:
    with pytest.raises(KeyError):
        runner.get_campaign("NOT_A_REAL_CAMPAIGN")


def test_preflight_lists_runnable_and_blocked(tmp_path: Path) -> None:
    pf = runner.preflight(_smoke_options(tmp_path))
    assert pf["campaign_id"] == "SMOKE_FIXTURE"
    assert "TEST_PAIR" in pf["instruments_runnable"]
    assert pf["instruments_blocked"] == []


def test_preflight_reports_missing_data_as_blocked(tmp_path: Path) -> None:
    """When the export dir contains no usable instruments, every requested
    instrument is reported as blocked."""

    pf = runner.preflight(
        _smoke_options(tmp_path, data_export_dir=tmp_path / "empty_dir")
    )
    assert pf["instruments_runnable"] == []
    assert pf["instruments_blocked"] == ["TEST_PAIR"]


def test_run_writes_expected_artifacts(tmp_path: Path) -> None:
    runner.run(_smoke_options(tmp_path))
    for name in EXPECTED_ARTIFACTS:
        path = tmp_path / name
        assert path.exists(), f"missing artefact: {name}"
        assert path.stat().st_size > 0, f"empty artefact: {name}"


def test_run_summary_has_strategy_evidence_false_and_one_trade(tmp_path: Path) -> None:
    summary = runner.run(_smoke_options(tmp_path))
    assert summary["strategy_evidence"] is False
    assert summary["campaign_id"] == "SMOKE_FIXTURE"
    assert summary["total_trades"] == 1
    assert summary["pairs"][0]["instrument"] == "TEST_PAIR"
    assert summary["pairs"][0]["trades"] == 1
    assert summary["pairs"][0]["wins"] == 1


def test_run_trades_jsonl_is_deterministic_on_fixture(tmp_path: Path) -> None:
    """Re-running the smoke campaign on the same fixture must produce
    bit-identical trade JSONL output (the runner is the determinism
    contract; the adapter is deterministic by construction)."""

    out_a = tmp_path / "run_a"
    out_b = tmp_path / "run_b"
    runner.run(_smoke_options(out_a))
    runner.run(_smoke_options(out_b))
    a = (out_a / "backtrader_trades.jsonl").read_text(encoding="utf-8")
    b = (out_b / "backtrader_trades.jsonl").read_text(encoding="utf-8")
    assert a == b
    # And the summary is the same up to the trade fields (manifest has
    # timestamps and may differ).
    sa = json.loads((out_a / "backtrader_summary.json").read_text(encoding="utf-8"))
    sb = json.loads((out_b / "backtrader_summary.json").read_text(encoding="utf-8"))
    sa.pop("dry_run", None)
    sb.pop("dry_run", None)
    assert sa == sb


def test_run_dry_run_writes_artifacts_but_skips_trades(tmp_path: Path) -> None:
    summary = runner.run(_smoke_options(tmp_path, dry_run=True))
    assert summary["total_trades"] == 0
    assert summary["pairs"] == []
    # The manifest must record this was a dry run via the `instruments.run`
    # being empty even though the instrument was "loadable" — the runner
    # loaded the data manifest entry but did not call the campaign runner.
    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["instruments"]["blocked"] == []
    assert manifest["instruments"]["run"] == []
    assert manifest["data"]["per_instrument"][0]["instrument"] == "TEST_PAIR"


def test_run_blocked_when_csv_missing(tmp_path: Path) -> None:
    """Pointing at a directory with no CSVs results in a clean BLOCKED
    report — no fake trades, no fake metrics."""

    empty = tmp_path / "empty"
    empty.mkdir()
    summary = runner.run(_smoke_options(tmp_path / "out", data_export_dir=empty))
    assert summary["total_trades"] == 0
    assert summary["blocked_instruments"] == ["TEST_PAIR"]
    # The manifest still gets written, with blocked instruments populated.
    manifest = json.loads(
        (tmp_path / "out" / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["instruments"]["blocked"] == ["TEST_PAIR"]
    assert manifest["instruments"]["run"] == []


def test_run_manifest_contains_data_provenance_hash(tmp_path: Path) -> None:
    runner.run(_smoke_options(tmp_path))
    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    per = manifest["data"]["per_instrument"][0]
    assert per["csv_sha256"] == per["provenance_data_sha256"]
    assert (
        per["provenance_campaign_002_data_request_hash"]
        == "deadbeefcafef00d"
    )
    # Every adapter-attached approximation flag is preserved.
    assert any("MID_OHLC_DERIVED" in f for f in per["approximation_flags"])


def test_run_manifest_does_not_leak_oanda_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Even if the environment carries an OANDA token, it must not appear
    in the manifest. The runner raises if it ever does."""

    monkeypatch.setenv("OANDA_TOKEN", "ABCDEF-NOT-A-REAL-TOKEN-1234567890")
    runner.run(_smoke_options(tmp_path))
    manifest_text = (tmp_path / "run_manifest.json").read_text(encoding="utf-8")
    assert "ABCDEF-NOT-A-REAL-TOKEN-1234567890" not in manifest_text
    # And the env key name itself is not in the manifest either (the
    # runner does not log env keys at all).
    assert "OANDA_TOKEN" not in manifest_text


def test_run_strict_data_off_does_not_silently_pass_drift(
    tmp_path: Path,
) -> None:
    """Even with --no-strict-data, sha drift on the fixture (which would
    require tampering anyway) does not throw — but we exercise the path."""

    # Copy the fixture and tamper a price so the sha drifts.
    src_csv = (FIXTURE_DIR / "TEST_PAIR_H4_lean.csv").read_text(encoding="utf-8")
    tampered_dir = tmp_path / "tampered"
    tampered_dir.mkdir()
    (tampered_dir / "TEST_PAIR_H4_lean.csv").write_text(
        src_csv.replace("1.10002", "1.10003", 1), encoding="utf-8"
    )
    (tampered_dir / "TEST_PAIR_H4_lean.provenance.json").write_text(
        (FIXTURE_DIR / "TEST_PAIR_H4_lean.provenance.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    # strict=True (default): blocks loudly.
    with pytest.raises(Exception):
        runner.run(_smoke_options(tmp_path / "strict_out", data_export_dir=tampered_dir))

    # strict=False: still runs, manifest still records the data; this is
    # the documented escape hatch, not a recommended path.
    summary = runner.run(
        _smoke_options(
            tmp_path / "loose_out",
            data_export_dir=tampered_dir,
            strict_data=False,
        )
    )
    assert summary["total_trades"] == 1
    manifest = json.loads(
        (tmp_path / "loose_out" / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["data"]["strict_mode"] is False


def test_runner_imports_no_forex_bot_or_broker() -> None:
    src = Path(runner.__file__).read_text(encoding="utf-8")
    for line in src.splitlines():
        clean = line.split("#", 1)[0].strip()
        if clean.startswith("import ") or clean.startswith("from "):
            assert "forex_bot" not in clean, f"forex_bot import in runner.py: {line}"
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
                assert needle not in clean, f"forbidden import: {line}"


def test_script_entry_point_imports_clean() -> None:
    """The CLI script must import cleanly under no special env."""

    spec = importlib.util.spec_from_file_location(
        "scripts._run_backtrader_parity",
        ROOT / "scripts" / "run_backtrader_parity.py",
    )
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    assert hasattr(mod, "main")


def test_script_list_campaigns(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`run_backtrader_parity.py --list-campaigns` prints the registered
    ids and exits 0."""

    spec = importlib.util.spec_from_file_location(
        "scripts._run_backtrader_parity",
        ROOT / "scripts" / "run_backtrader_parity.py",
    )
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    monkeypatch.setattr(sys, "argv", ["run_backtrader_parity.py", "--list-campaigns"])
    rc = mod.main(["--list-campaigns"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "SMOKE_FIXTURE" in out


def test_script_missing_required_args_returns_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    spec = importlib.util.spec_from_file_location(
        "scripts._run_backtrader_parity",
        ROOT / "scripts" / "run_backtrader_parity.py",
    )
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    rc = mod.main([])
    capsys.readouterr()
    assert rc == 2


def test_script_unknown_campaign_returns_two(
    tmp_path: Path,
) -> None:
    spec = importlib.util.spec_from_file_location(
        "scripts._run_backtrader_parity",
        ROOT / "scripts" / "run_backtrader_parity.py",
    )
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    rc = mod.main(
        [
            "--campaign",
            "NOT_REGISTERED_CAMPAIGN",
            "--output",
            str(tmp_path / "out"),
            "--data-export-dir",
            str(FIXTURE_DIR),
        ]
    )
    assert rc == 2

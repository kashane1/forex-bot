"""Edge-discovery CLI guardrail + smoke tests.

Each script must: declare diagnostic/not-approved/test-lockbox-closed flags,
never import the broker, BLOCK (exit 2) on missing inputs, honor --dry-run, and
produce a compact JSON artifact on a real run. Functional runs write to a
tmp_path via --out so the repo is never polluted.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = {
    "matrix_sanity": ROOT / "scripts/run_edge_discovery_matrix_sanity.py",
    "filter_ablation": ROOT / "scripts/run_edge_discovery_filter_ablation.py",
    "cost_feasibility": ROOT / "scripts/run_edge_discovery_cost_feasibility.py",
    "matched_null": ROOT / "scripts/run_edge_discovery_matched_null.py",
}


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"edge_cli_{name}", SCRIPTS[name])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("name", list(SCRIPTS))
def test_script_declares_infrastructure_only_flags(name: str) -> None:
    text = SCRIPTS[name].read_text(encoding="utf-8")
    assert "diagnostic_only" in text
    assert "not_approved" in text
    assert "test_lockbox_opened" in text
    assert "strategy_evidence" in text
    # No broker / order / live wiring.
    assert "OandaBroker" not in text
    assert "forex_bot.broker" not in text


@pytest.mark.parametrize("name", list(SCRIPTS))
def test_build_parser_smoke(name: str) -> None:
    mod = _load(name)
    parser = mod.build_parser()
    assert parser is not None


def test_matrix_sanity_blocks_on_missing_file(tmp_path: Path) -> None:
    mod = _load("matrix_sanity")
    rc = mod.main(["--matrix-csv", str(tmp_path / "nope.csv")])
    assert rc == 2


def test_matrix_sanity_dry_run(tmp_path: Path) -> None:
    mod = _load("matrix_sanity")
    csv = tmp_path / "m.csv"
    pd.DataFrame({"candidate_id": ["a", "b"], "expectancy_r": [-0.1, -0.2]}).to_csv(csv, index=False)
    assert mod.main(["--matrix-csv", str(csv), "--dry-run"]) == 0


def test_matrix_sanity_runs_and_writes(tmp_path: Path) -> None:
    mod = _load("matrix_sanity")
    csv = tmp_path / "m.csv"
    vals = list(np.random.default_rng(0).normal(-0.14, 0.02, 16))
    pd.DataFrame({"candidate_id": [f"c{i}" for i in range(16)], "expectancy_r": vals}).to_csv(csv, index=False)
    out = tmp_path / "out.json"
    rc = mod.main([
        "--matrix-csv", str(csv), "--null-reference", "-0.0029", "--null-std", "0.02",
        "--out", str(out),
    ])
    assert rc == 0
    payload = json.loads(out.read_text())
    assert payload["_meta"]["not_approved"] is True
    assert payload["_meta"]["test_lockbox_opened"] is False
    assert "flags" in payload["result"]


def test_filter_ablation_runs_and_writes(tmp_path: Path) -> None:
    mod = _load("filter_ablation")
    rng = np.random.default_rng(1)
    n = 300
    base = rng.normal(0, 1, n)
    df = pd.DataFrame({
        "instrument": rng.choice(["EUR_USD", "USD_JPY"], n),
        "side": "long",
        "log_return": base,
        "A": base > np.median(base),
    })
    csv = tmp_path / "s.csv"
    df.to_csv(csv, index=False)
    out = tmp_path / "fa.json"
    rc = mod.main(["--signals-csv", str(csv), "--filter-cols", "A", "--out", str(out)])
    assert rc == 0
    payload = json.loads(out.read_text())
    assert payload["result"]["contributions"][0]["filter"] == "A"


def test_filter_ablation_blocks_on_missing_column(tmp_path: Path) -> None:
    mod = _load("filter_ablation")
    csv = tmp_path / "s.csv"
    pd.DataFrame({"instrument": ["EUR_USD"], "log_return": [0.1]}).to_csv(csv, index=False)
    rc = mod.main(["--signals-csv", str(csv), "--filter-cols", "ZZZ"])
    assert rc == 2


def test_cost_feasibility_inline_json(tmp_path: Path, monkeypatch) -> None:
    mod = _load("cost_feasibility")
    # Redirect the default output dir into tmp.
    monkeypatch.setattr(mod, "DEFAULT_OUTPUT_DIR", tmp_path)
    rc = mod.main(["--ratios-json", '{"M3":0.59,"M5":0.45,"M15":0.23,"M30":0.15}',
                   "--kind", "timeframe", "--out-prefix", "cf"])
    assert rc == 0
    payload = json.loads((tmp_path / "cf.json").read_text())
    cells = {c["label"]: c["flags"] for c in payload["cells"]}
    assert "TIMEFRAME_TOO_FAST" in cells["M5"]
    assert cells["M30"] == "COST_FEASIBLE"


def test_matched_null_blocks_without_frames(tmp_path: Path) -> None:
    mod = _load("matched_null")
    ledger = tmp_path / "led.csv"
    pd.DataFrame({"instrument": ["EUR_USD"], "side": ["long"],
                  "entry_time": ["2021-01-04T00:00:00Z"], "bars_held": [6]}).to_csv(ledger, index=False)
    rc = mod.main(["--ledger-csv", str(ledger), "--frames-dir", str(tmp_path / "no_frames")])
    assert rc == 2  # frames dir absent → clean block, no fabrication

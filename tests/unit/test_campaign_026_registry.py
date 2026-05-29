"""CAMPAIGN_026 — frozen candidate registry + runner safety-guard tests."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_REGISTRY = _REPO / "research/campaign_026/timeframe_ladder/candidate_registry.json"

_REQUIRED_FIELDS = {
    "candidate_id", "campaign_id", "strategy_family", "version", "execution_timeframe",
    "local_setup_timeframe", "trend_timeframes", "regime_timeframe", "donchian_length",
    "initial_stop_model", "atr_stop_multiple", "exit_model", "target_r_multiple",
    "breakeven_trigger_r", "trail_activation_r", "trail_atr_multiple", "channel_exit_length",
    "time_stop_bars", "context_mode", "execution_fill", "not_approved",
}
_VALID_TFS = {"M3", "M15", "M30"}
_VALID_EXITS = {"time_stop_only", "fixed_2r_target", "fixed_3r_target", "breakeven_then_atr_trail", "donchian_channel_exit"}


def _registry() -> dict:
    return json.loads(_REGISTRY.read_text(encoding="utf-8"))


def test_registry_has_11_candidates_max_15() -> None:
    cands = _registry()["candidates"]
    assert 1 <= len(cands) <= 15
    assert len(cands) == 11  # preferred count


def test_candidate_ids_unique_and_well_formed() -> None:
    cands = _registry()["candidates"]
    ids = [c["candidate_id"] for c in cands]
    assert len(set(ids)) == len(ids)
    assert all(cid.startswith("C026_TF_") for cid in ids)


def test_no_duplicate_candidate_parameter_sets() -> None:
    cands = _registry()["candidates"]
    keys = [
        (c["execution_timeframe"], c["donchian_length"], c["atr_stop_multiple"], c["exit_model"],
         c["time_stop_bars"], c["context_mode"], c.get("local_setup_mode"))
        for c in cands
    ]
    assert len(set(keys)) == len(keys), "duplicate candidate parameter set found"


def test_required_fields_and_valid_enums() -> None:
    for c in _registry()["candidates"]:
        assert set(c) >= _REQUIRED_FIELDS, f"missing fields in {c['candidate_id']}"
        assert c["execution_timeframe"] in _VALID_TFS
        assert c["exit_model"] in _VALID_EXITS
        assert c["campaign_id"] == "CAMPAIGN_026"
        assert c["not_approved"] is True
        assert c["execution_fill"] == "next_bar_open"
        assert c["regime_timeframe"] == "D1AGG"


def test_exit_model_parameters_consistent() -> None:
    for c in _registry()["candidates"]:
        em = c["exit_model"]
        if em == "fixed_2r_target":
            assert c["target_r_multiple"] == 2.0
        elif em == "fixed_3r_target":
            assert c["target_r_multiple"] == 3.0
        elif em == "breakeven_then_atr_trail":
            assert c["breakeven_trigger_r"] is not None and c["trail_atr_multiple"] is not None
        elif em == "donchian_channel_exit":
            assert c["channel_exit_length"] is not None


def test_context_ladder_matches_loader() -> None:
    from forex_bot.research.campaign_026_loader import CONTEXT_LADDER

    for c in _registry()["candidates"]:
        tf = c["execution_timeframe"]
        # M15 stores "M15_internal" in the registry; loader uses "M15" as the local frame
        local = c["local_setup_timeframe"]
        expected_local = CONTEXT_LADDER[tf]["local"]
        if local == "M15_internal":
            assert tf == "M15" and expected_local == "M15"
        else:
            assert local == expected_local


# --------------------------------------------------------------------------- #
# runner safety guards
# --------------------------------------------------------------------------- #
def _load_runner():
    path = _REPO / "scripts/run_campaign_026_donchian_htf_timeframe_ladder.py"
    spec = importlib.util.spec_from_file_location("c026_runner", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_test_window_guard_rejects_overlap() -> None:
    runner = _load_runner()
    with pytest.raises(SystemExit, match="FAIL_IF_TEST_WINDOW"):
        runner.assert_not_test_window("2025-02-01", "2025-06-01", fail_if_test_window=True)
    # pre-test window allowed
    runner.assert_not_test_window("2021-07-01", "2023-06-30", fail_if_test_window=True)
    # guard can be disabled but defaults on everywhere it is called
    runner.assert_not_test_window("2025-02-01", "2025-06-01", fail_if_test_window=False)


def test_validation_requires_champion(tmp_path, monkeypatch) -> None:
    runner = _load_runner()
    # point the runner's ladder dir at a temp dir with a no-champion selection
    monkeypatch.setattr(runner, "LADDER_DIR", tmp_path)
    monkeypatch.setattr(runner, "APPROVED_PATH", _REPO / "configs/approved_strategies.yaml")
    (tmp_path / "train_matrix_candidate_selection.json").write_text(
        json.dumps({"champion_candidate_id": None, "classification": "REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE"}),
        encoding="utf-8",
    )
    out = runner.run_champion_validation(valid_start="2023-07-01", valid_end="2024-12-31", fail_if_test_window=True)
    assert out["validation_run"] is False
    assert "no champion" in out["reason"]


def test_validation_errors_without_train_selection(tmp_path, monkeypatch) -> None:
    runner = _load_runner()
    monkeypatch.setattr(runner, "LADDER_DIR", tmp_path)  # empty -> no selection file
    with pytest.raises(SystemExit, match="run --train-matrix first"):
        runner.run_champion_validation(valid_start="2023-07-01", valid_end="2024-12-31", fail_if_test_window=True)

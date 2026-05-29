"""CAMPAIGN_025 train-matrix candidate registry — frozen-before-evidence checks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_REGISTRY = _REPO / "research/campaign_025/train_matrix/candidate_registry.json"

_ALLOWED_DONCHIAN = {12, 20, 30}
_ALLOWED_STOP = {
    "atr_1_5_channel_farther": 1.5,
    "atr_2_0_channel_farther": 2.0,
    "atr_2_5_channel_farther": 2.5,
}
_ALLOWED_EXIT = {
    "time_stop_only",
    "fixed_2r_target",
    "fixed_3r_target",
    "breakeven_then_atr_trail",
    "donchian_channel_exit",
}
_ALLOWED_TIMESTOP = {36, 48, 72}
_ALLOWED_H1 = {"standard", "strict"}
_ALLOWED_M15 = {"pullback_or_compression", "pullback_only", "compression_only"}


@pytest.fixture(scope="module")
def registry() -> dict:
    return json.loads(_REGISTRY.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def candidates(registry: dict) -> list[dict]:
    return registry["candidates"]


def _sig(c: dict) -> tuple:
    return (
        c["m5_donchian_length"],
        c["initial_stop_model"],
        c["exit_model"],
        c["time_stop_m5_bars"],
        c["h1_trend_mode"],
        c["m15_setup_mode"],
    )


def test_registry_marks_frozen_and_not_validation_selected(registry: dict) -> None:
    assert registry["campaign_id"] == "CAMPAIGN_025"
    assert registry["frozen"] is True
    assert registry["not_approved"] is True
    assert registry["selection_uses_validation"] is False


def test_no_duplicate_signatures(candidates: list[dict]) -> None:
    sigs = [_sig(c) for c in candidates]
    assert len(sigs) == len(set(sigs)), "duplicate candidate parameter signatures"


def test_candidate_count_within_limits(candidates: list[dict]) -> None:
    assert len(candidates) <= 36, "hard maximum 36 candidates"
    # preferred <= 24 (no documented exception in this matrix)
    assert len(candidates) <= 24
    assert len(candidates) >= 1


def test_registry_count_field_matches(registry: dict, candidates: list[dict]) -> None:
    assert registry["candidate_count"] == len(candidates)


def test_stable_sequential_ids(candidates: list[dict]) -> None:
    ids = [c["candidate_id"] for c in candidates]
    assert ids == [f"C025_MTX_{i + 1:03d}" for i in range(len(candidates))]
    assert len(set(ids)) == len(ids)


def test_base_candidate_exists(candidates: list[dict]) -> None:
    base = [
        c
        for c in candidates
        if c["m5_donchian_length"] == 20
        and c["initial_stop_model"] == "atr_2_0_channel_farther"
        and c["exit_model"] == "time_stop_only"
        and c["time_stop_m5_bars"] == 48
        and c["h1_trend_mode"] == "standard"
        and c["m15_setup_mode"] == "pullback_or_compression"
    ]
    assert len(base) == 1, "the frozen baseline_continuation candidate must exist"


def test_all_exit_archetypes_represented(candidates: list[dict]) -> None:
    present = {c["exit_model"] for c in candidates}
    assert present == _ALLOWED_EXIT, f"missing exit archetypes: {_ALLOWED_EXIT - present}"


def test_parameters_within_allowed_sets(candidates: list[dict]) -> None:
    for c in candidates:
        assert c["campaign_id"] == "CAMPAIGN_025"
        assert c["strategy_family"] == "m5_donchian_htf_confluence_breakout"
        assert c["version"] == "0.1.0-c025"
        assert c["m5_donchian_length"] in _ALLOWED_DONCHIAN
        assert c["initial_stop_model"] in _ALLOWED_STOP
        assert c["atr_stop_multiple"] == _ALLOWED_STOP[c["initial_stop_model"]]
        assert c["exit_model"] in _ALLOWED_EXIT
        assert c["time_stop_m5_bars"] in _ALLOWED_TIMESTOP
        assert c["h1_trend_mode"] in _ALLOWED_H1
        assert c["m15_setup_mode"] in _ALLOWED_M15
        assert c["execution_fill"] == "next_bar_open"
        assert c["not_approved"] is True


def test_fixed_target_candidates_have_target_r(candidates: list[dict]) -> None:
    for c in candidates:
        if c["exit_model"] == "fixed_2r_target":
            assert c["target_r_multiple"] == 2.0
        elif c["exit_model"] == "fixed_3r_target":
            assert c["target_r_multiple"] == 3.0
        else:
            # non-fixed-target candidates must not carry a target
            assert c["target_r_multiple"] is None


def test_trailing_candidates_have_be_and_trail_fields(candidates: list[dict]) -> None:
    for c in candidates:
        if c["exit_model"] == "breakeven_then_atr_trail":
            assert c["breakeven_trigger_r"] == 1.0
            assert c["trail_activation_r"] == 1.5
            assert c["trail_atr_multiple"] == 1.5
        else:
            assert c["breakeven_trigger_r"] is None
            assert c["trail_activation_r"] is None
            assert c["trail_atr_multiple"] is None


def test_channel_exit_candidates_have_channel_length(candidates: list[dict]) -> None:
    for c in candidates:
        if c["exit_model"] == "donchian_channel_exit":
            assert c["channel_exit_length"] == c["m5_donchian_length"]
        else:
            assert c["channel_exit_length"] is None

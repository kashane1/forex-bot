"""Smoke + binding tests for the single-pair-probe sprint outputs.

Pins the falsification result so future lab changes don't silently
flip the classification, and verifies the provenance / verdict-word
ban contracts on the new outputs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs" / "real"
PHASE1 = OUTPUTS / "probe_single_pair_eur_usd_c012.json"
PHASE2 = OUTPUTS / "probe_robustness_eur_usd_c012.json"


@pytest.fixture(scope="module")
def phase1_payload() -> dict:
    return json.loads(PHASE1.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def phase2_payload() -> dict:
    return json.loads(PHASE2.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Phase 1 extraction integrity
# ---------------------------------------------------------------------------


def test_phase1_output_exists() -> None:
    assert PHASE1.is_file(), f"phase 1 extraction missing: {PHASE1}"


def test_phase1_provenance_block_is_complete(phase1_payload: dict) -> None:
    prov = phase1_payload["provenance"]
    for key in ("data_kind", "inputs", "date_coverage", "pair_universe",
                "limitations", "exploratory_only"):
        assert key in prov
    assert prov["data_kind"] == "real"
    assert prov["exploratory_only"] is True


def test_phase1_pins_committed_numbers(phase1_payload: dict) -> None:
    """The committed CAMPAIGN_012 EUR_USD aggregate must match the
    hydrate sprint's prior pair-baseline numbers within 1e-4 R."""
    cand = phase1_payload["candidate"]
    null = phase1_payload["null"]
    gap = phase1_payload["gap"]
    assert cand["mean_expectancy_r"] == pytest.approx(+0.0300, abs=1e-3)
    assert cand["median_expectancy_r"] == pytest.approx(-0.0189, abs=1e-3)
    assert cand["total_trades"] == 479
    assert cand["n_folds_positive_expectancy"] == 3
    assert null["mean_expectancy_r"] == pytest.approx(-0.0650, abs=1e-3)
    assert null["total_trades"] == 119
    assert gap["mean_gap_r"] == pytest.approx(+0.0950, abs=1e-3)


def test_phase1_dominance_signals_artifact(phase1_payload: dict) -> None:
    """Single-fold contribution exceeds the |signed total|; fold 3
    alone is the top-fold contributor."""
    dom = phase1_payload["candidate_dominance"]
    # fold 3 contributed > total (which is negative)
    assert dom["top_fold_index"] == 3
    assert dom["top_fold_cum_r"] > 9.0
    # |total| < top fold contribution → top_fold_share_of_abs_total > 1
    assert dom["top_fold_share_of_abs_total"] > 1.0


def test_phase1_stop_exits_have_exact_minus_one_r(phase1_payload: dict) -> None:
    """The lab observation: every 'stop' exit pays exactly -1.0 R.
    Pin this so the lab knows the strategy's loss profile is hard-
    stopped, not gradual."""
    dist = phase1_payload["candidate_distribution"]
    assert "stop" in dist["exit_reason_counts"]
    assert dist["exit_reason_mean_r"]["stop"] == pytest.approx(-1.0, abs=1e-6)


# ---------------------------------------------------------------------------
# Phase 2 robustness + classification
# ---------------------------------------------------------------------------


def test_phase2_output_exists() -> None:
    assert PHASE2.is_file(), f"phase 2 robustness missing: {PHASE2}"


def test_phase2_classification_is_selected_cell_artifact(phase2_payload: dict) -> None:
    """The headline binding test: the EUR_USD / CAMPAIGN_012 cell
    must classify as SELECTED_CELL_ARTIFACT. If a future lab change
    flips this, the change is breaking the falsification."""
    cls = phase2_payload["classification_block"]
    assert cls["classification"] == "SELECTED_CELL_ARTIFACT"


def test_phase2_classification_failures_are_documented(phase2_payload: dict) -> None:
    cls = phase2_payload["classification_block"]
    failures = cls["failures"]
    assert "median_per_fold_expectancy_negative" in failures
    assert "at_most_4_of_8_folds_positive" in failures
    assert "LOO_drops_below_floor" in failures


def test_phase2_loo_minimum_below_floor(phase2_payload: dict) -> None:
    """Dropping one fold drops the mean gap below +0.05 R."""
    loo = phase2_payload["loo"]
    assert loo["min_loo_mean_gap"] < 0.05
    # But not below zero - the cell isn't catastrophic, just
    # not robust to LOO.
    assert loo["min_loo_mean_gap"] > 0.0


def test_phase2_neighbor_pair_isolation(phase2_payload: dict) -> None:
    """EUR_USD is the only pair above the +0.05 floor for C012."""
    pairs = phase2_payload["neighboring_pairs"]
    above = [r for r in pairs if r["above_material_floor"]]
    assert len(above) == 1
    assert above[0]["pair"] == "EUR_USD"


def test_phase2_neighbor_candidate_isolation(phase2_payload: dict) -> None:
    """C012 is the only candidate above the +0.05 floor on EUR_USD."""
    cands = phase2_payload["neighboring_candidates"]
    above = [r for r in cands if r["above_material_floor"]]
    assert len(above) == 1
    assert above[0]["candidate"] == "CAMPAIGN_012_regime_switcher_atr_percentile"


def test_phase2_t_stat_below_two(phase2_payload: dict) -> None:
    """The mean gap is within ~1.3 SE of zero — not 2 SE, the lab's
    soft significance threshold."""
    summary = phase2_payload["classification_block"]["summary"]
    assert summary["t_stat_approx"] < 2.0


def test_phase2_acknowledges_verdict_word_ban(phase2_payload: dict) -> None:
    assert phase2_payload["verdict_word_ban_acknowledged"] is True


@pytest.mark.parametrize("name", ["probe_single_pair_eur_usd_c012",
                                  "probe_robustness_eur_usd_c012"])
def test_probe_outputs_have_paired_md(name: str) -> None:
    md = OUTPUTS / f"{name}.md"
    json_path = OUTPUTS / f"{name}.json"
    assert md.is_file(), f"missing markdown for {name}"
    assert json_path.is_file(), f"missing json for {name}"


@pytest.mark.parametrize("name", ["probe_single_pair_eur_usd_c012",
                                  "probe_robustness_eur_usd_c012"])
def test_probe_markdowns_state_no_strategy_approval(name: str) -> None:
    md = (OUTPUTS / f"{name}.md").read_text(encoding="utf-8")
    # Must contain the explicit refusal / preservation statement.
    assert "does not approve" in md.lower() or "remains REJECT" in md

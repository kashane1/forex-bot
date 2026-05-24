"""Binding tests for the cross-campaign exit-asymmetry sprint outputs.

Sprint: ``research-exit-asymmetry-cross-campaign-001``.

These tests pin the headline structural-pattern observations and the
robustness classification so future lab changes don't silently
invalidate them. They also re-verify the verdict-word ban and
provenance contracts on the two new outputs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs" / "real"
PHASE12 = OUTPUTS / "exit_asymmetry_cross_campaign.json"
PHASE3 = OUTPUTS / "exit_asymmetry_robustness.json"


@pytest.fixture(scope="module")
def phase12_payload() -> dict:
    return json.loads(PHASE12.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def phase3_payload() -> dict:
    return json.loads(PHASE3.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Output integrity
# ---------------------------------------------------------------------------


def test_phase12_output_exists() -> None:
    assert PHASE12.is_file(), f"phase 1+2 extraction missing: {PHASE12}"


def test_phase3_output_exists() -> None:
    assert PHASE3.is_file(), f"phase 3 robustness missing: {PHASE3}"


@pytest.mark.parametrize("name", ["exit_asymmetry_cross_campaign",
                                  "exit_asymmetry_robustness"])
def test_paired_markdown_exists(name: str) -> None:
    md = OUTPUTS / f"{name}.md"
    assert md.is_file(), f"missing markdown for {name}"


# ---------------------------------------------------------------------------
# Provenance + refusals
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("payload_fixture", ["phase12_payload", "phase3_payload"])
def test_verdict_word_ban_acknowledged(payload_fixture: str, request: pytest.FixtureRequest) -> None:
    payload = request.getfixturevalue(payload_fixture)
    assert payload["verdict_word_ban_acknowledged"] is True


@pytest.mark.parametrize("payload_fixture", ["phase12_payload", "phase3_payload"])
def test_provenance_marks_real_and_exploratory(payload_fixture: str, request: pytest.FixtureRequest) -> None:
    payload = request.getfixturevalue(payload_fixture)
    prov = payload["provenance"]
    assert prov["data_kind"] == "real"
    assert prov["exploratory_only"] is True
    assert isinstance(prov["inputs"], list) and len(prov["inputs"]) >= 5


@pytest.mark.parametrize("payload_fixture", ["phase12_payload", "phase3_payload"])
def test_refusal_block_is_intact(payload_fixture: str, request: pytest.FixtureRequest) -> None:
    payload = request.getfixturevalue(payload_fixture)
    ref = payload["refusals"]
    assert ref["approves_strategy"] is False
    assert ref["changes_campaign_verdict"] is False
    assert ref["proposes_parameter_tune"] is False
    assert ref["writes_to_approved_strategies_yaml"] is False


@pytest.mark.parametrize("name", ["exit_asymmetry_cross_campaign",
                                  "exit_asymmetry_robustness"])
def test_markdown_states_no_approval(name: str) -> None:
    md = (OUTPUTS / f"{name}.md").read_text(encoding="utf-8").lower()
    # Either explicit refusal language or the "remains REJECT-anchored" line.
    assert (
        "no strategy approved" in md
        or "does not approve" in md
        or "remain reject" in md
    )


# ---------------------------------------------------------------------------
# Phase 1+2 headline pins
# ---------------------------------------------------------------------------


def test_phase12_total_trades_pinned(phase12_payload: dict) -> None:
    """Pin the cross-campaign trade count. A change here means the
    underlying ledgers changed - the test must be re-evaluated."""
    assert phase12_payload["headline"]["n_trades_total"] == 16354
    assert phase12_payload["headline"]["n_campaigns"] == 5
    assert phase12_payload["headline"]["n_pairs"] == 7
    assert phase12_payload["headline"]["n_folds_per_campaign"] == 8


def test_phase12_exit_reasons_are_three_known_classes(phase12_payload: dict) -> None:
    assert phase12_payload["headline"]["exit_reason_vocabulary"] == ["eod", "stop", "time"]


def test_phase12_every_campaign_has_positive_mean_r_given_time(phase12_payload: dict) -> None:
    """The headline structural finding: every campaign INCLUDING the
    random-entry null has positive mean_r_given_time. This is the
    proof that the time-exit positivity is an exit-engine artifact,
    not a strategy edge."""
    rows = {r["campaign_name"]: r for r in phase12_payload["per_campaign"]}
    for campaign, row in rows.items():
        assert row["mean_r_given_time"] > 0, f"{campaign} mean_r_given_time={row['mean_r_given_time']}"


def test_phase12_every_campaign_loses_overall(phase12_payload: dict) -> None:
    """Every CAMPAIGN_010-014 has non-positive mean_r_overall. Pins
    that the structural exit shape cannot save any of them."""
    for row in phase12_payload["per_campaign"]:
        assert row["mean_r_overall"] <= 0


def test_phase12_stops_dominate_gross_losses(phase12_payload: dict) -> None:
    """≥ 60% of every campaign's gross losses come from stops."""
    for row in phase12_payload["per_campaign"]:
        assert row["share_gross_loss_from_stops"] >= 0.60, row


def test_phase12_time_exits_dominate_gross_gains(phase12_payload: dict) -> None:
    """≥ 98% of every campaign's gross gains come from time exits."""
    for row in phase12_payload["per_campaign"]:
        assert row["share_gross_gain_from_time_exits"] >= 0.98, row


def test_phase12_structural_pattern_check_is_at_least_partial(phase12_payload: dict) -> None:
    cls = phase12_payload["structural_pattern_check"]["classification"]
    assert cls in {
        "STRUCTURAL_FAILURE_PATTERN_CONFIRMED",
        "STRUCTURAL_FAILURE_PATTERN_PARTIAL",
    }


def test_phase12_null_and_fold_noise_conditions_pass(phase12_payload: dict) -> None:
    """Pin the two conditions that pass at strict thresholds:
    - Condition 3: null shares the shape with the cross-campaign median.
    - Condition 4: per-pair stop_rate std across folds ≥ 0.05.
    """
    sp = phase12_payload["structural_pattern_check"]
    assert sp["condition_3_null_shares_shape"]["pass"] is True
    assert sp["condition_4_fold_noise_driver"]["pass"] is True


def test_phase12_at_least_one_above_floor_cell_on_time_only(phase12_payload: dict) -> None:
    """At least one cell clears the +0.05 R floor on mean_r_given_time
    (this is the CAMPAIGN_013 × EUR_USD cell that Phase 3 screens).
    Pinning the existence so Phase 3's screening artifact stays in
    play; the screening downgrades the cell to INSUFFICIENT_DATA."""
    cells = phase12_payload["above_floor_cells_vs_null"]
    time_only = [c for c in cells if c["above_floor_on_time_only"]]
    assert len(time_only) >= 1


# ---------------------------------------------------------------------------
# Phase 3 robustness pins
# ---------------------------------------------------------------------------


def test_phase3_r9_fires_exactly_once_on_eur_usd_c012(phase3_payload: dict) -> None:
    """R-9 (mean-of-fold-means positive while cumulative R negative)
    should fire on exactly the EUR_USD / CAMPAIGN_012 cell the
    single-pair-probe sprint identified - and on no other cell.
    This is the headline structural finding: R-9 is selective."""
    fires = [r for r in phase3_payload["r9_sweep"] if r["r9_fires"]]
    assert len(fires) == 1
    assert fires[0]["campaign"] == "CAMPAIGN_012_regime_switcher_atr_percentile"
    assert fires[0]["instrument"] == "EUR_USD"


def test_phase3_majority_cells_lose_overall(phase3_payload: dict) -> None:
    """At least 28 of 35 (campaign, pair) cells have negative
    cumulative R. Pins the universal-loss observation."""
    bc = phase3_payload["bucket_counters"]
    assert bc["total_cells"] == 35
    assert bc["cumulative_negative"] >= 28
    assert bc["median_per_fold_mean_r_overall_negative"] >= 28


def test_phase3_screened_cells_classification(phase3_payload: dict) -> None:
    """The CAMPAIGN_013 × EUR_USD time-only cell should not classify
    as PROMISING_BUT_INSUFFICIENT_LAB_SIGNAL or stronger. Allowed
    classifications: INSUFFICIENT_DATA or ISOLATED_SELECTED_CELL_ARTIFACT."""
    for cell in phase3_payload["screened_cells"]:
        assert cell["classification"] in {
            "INSUFFICIENT_DATA",
            "ISOLATED_SELECTED_CELL_ARTIFACT",
        }, cell


def test_phase3_no_cell_classifies_as_promising(phase3_payload: dict) -> None:
    """No (campaign, pair) cell across the cross-campaign exit
    asymmetry sweep should classify as PROMISING_BUT_INSUFFICIENT_LAB_SIGNAL
    or stronger. The structural finding is that the exit shape is a
    null artifact; no candidate is signalling above the lab's screens."""
    for cell in phase3_payload["screened_cells"]:
        assert cell["classification"] not in {
            "PROMISING_BUT_INSUFFICIENT_LAB_SIGNAL",
            "STRUCTURAL_FAILURE_PATTERN_CONFIRMED",
        }, cell


# ---------------------------------------------------------------------------
# Configs / freeze invariants
# ---------------------------------------------------------------------------


def test_approved_strategies_yaml_remains_empty() -> None:
    """Re-assert that no approval was added by this sprint."""
    cfg = (REPO_ROOT / "configs" / "approved_strategies.yaml").read_text(encoding="utf-8")
    # Find the 'approved:' line and assert empty list.
    found = False
    for line in cfg.splitlines():
        stripped = line.strip()
        if stripped.startswith("approved:"):
            found = True
            # Either approved: [] inline or approved: followed by empty / no list items
            assert stripped in {"approved: []"} or stripped == "approved:", (
                f"approved_strategies.yaml line was {stripped!r}, expected empty list"
            )
    assert found, "approved_strategies.yaml missing 'approved:' top-level key"

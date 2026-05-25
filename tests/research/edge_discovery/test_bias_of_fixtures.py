"""Binding tests for the bias-of-fixtures audit sprint outputs.

Sprint: ``research-bias-of-fixtures-audit-001``.

These tests pin the audit's headline findings:

  - the CAMPAIGN_011 null coverage and shape findings
  - the cross-campaign comparability invariants (5 of 5 pass)
  - the test-only headline survival
  - the synthetic-vs-real corpus boundary

so that a future lab change cannot silently invalidate the audit's
conclusions, and re-verify the verdict-word ban and refusal block on
both new outputs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs" / "real"
LEGACY_OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs"
NULL_BASELINE = OUTPUTS / "bias_null_baseline.json"
COMPARABILITY = OUTPUTS / "bias_cross_campaign_comparability.json"


@pytest.fixture(scope="module")
def null_payload() -> dict:
    return json.loads(NULL_BASELINE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def comparability_payload() -> dict:
    return json.loads(COMPARABILITY.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Output integrity
# ---------------------------------------------------------------------------


def test_null_baseline_output_exists() -> None:
    assert NULL_BASELINE.is_file(), f"phase 2 output missing: {NULL_BASELINE}"


def test_comparability_output_exists() -> None:
    assert COMPARABILITY.is_file(), f"phase 3 output missing: {COMPARABILITY}"


@pytest.mark.parametrize(
    "name", ["bias_null_baseline", "bias_cross_campaign_comparability"]
)
def test_paired_markdown_exists(name: str) -> None:
    md = OUTPUTS / f"{name}.md"
    assert md.is_file(), f"missing markdown for {name}"


# ---------------------------------------------------------------------------
# Provenance + refusals
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("payload_fixture", ["null_payload", "comparability_payload"])
def test_verdict_word_ban_acknowledged(
    payload_fixture: str, request: pytest.FixtureRequest
) -> None:
    payload = request.getfixturevalue(payload_fixture)
    assert payload["verdict_word_ban_acknowledged"] is True


@pytest.mark.parametrize("payload_fixture", ["null_payload", "comparability_payload"])
def test_provenance_marks_real_and_exploratory(
    payload_fixture: str, request: pytest.FixtureRequest
) -> None:
    payload = request.getfixturevalue(payload_fixture)
    prov = payload["provenance"]
    assert prov["data_kind"] == "real"
    assert prov["exploratory_only"] is True
    assert isinstance(prov["inputs"], list) and len(prov["inputs"]) >= 5


@pytest.mark.parametrize("payload_fixture", ["null_payload", "comparability_payload"])
def test_refusal_block_intact(
    payload_fixture: str, request: pytest.FixtureRequest
) -> None:
    payload = request.getfixturevalue(payload_fixture)
    r = payload["refusals"]
    assert r["approves_strategy"] is False
    assert r["changes_campaign_verdict"] is False
    assert r["proposes_parameter_tune"] is False
    assert r["writes_to_approved_strategies_yaml"] is False


# ---------------------------------------------------------------------------
# Phase 2 null-baseline headline pins
# ---------------------------------------------------------------------------


def test_null_has_full_8x7_coverage(null_payload: dict) -> None:
    """CAMPAIGN_011 has trades in every (fold, pair) cell — 0 empty
    out of 56. If this regresses, the null itself has degraded."""
    head = null_payload["headline"]
    assert head["null_coverage_complete"] is True
    null_row = next(
        r for r in null_payload["coverage"]
        if r["campaign"] == "CAMPAIGN_011_random_entry_anchor"
    )
    assert null_row["n_folds_with_trades"] == 8
    assert null_row["n_pairs_with_trades"] == 7
    assert null_row["n_empty_cells"] == 0


def test_null_trade_count_pinned(null_payload: dict) -> None:
    """Pin the C011 total trade count at the audit-time value."""
    assert null_payload["headline"]["null_trade_count"] == 1177


def test_null_direction_balance_within_range(null_payload: dict) -> None:
    """C011 is within 5pp of 50/50 long/short — the random-entry
    direction balance is structurally expected to be near-equal."""
    null_row = next(
        r for r in null_payload["direction_balance"]
        if r["campaign"] == "CAMPAIGN_011_random_entry_anchor"
    )
    assert null_row["classification"] == "within_expected_range"
    assert abs(null_row["long_share"] - 0.5) < 0.05


def test_null_inside_others_range_on_conditional_shape(null_payload: dict) -> None:
    """The null's stop_rate, time_rate, mean_R_given_stop, and
    mean_R_given_time all sit INSIDE the cross-campaign range of
    CAMPAIGN_010, 012, 013, 014. This is the proof that the null
    shares the engine's exit shape with the candidates — a
    necessary property for it to be a legitimate baseline."""
    cmp = null_payload["null_vs_others"]["null_compare"]
    for metric in ("stop_rate", "time_rate", "mean_r_given_stop", "mean_r_given_time"):
        assert cmp[metric]["null_is_outside_others_range"] is False, (
            f"null is outside others range on {metric}: {cmp[metric]}"
        )


def test_null_outside_others_range_on_mean_r_overall(null_payload: dict) -> None:
    """The null SHOULD sit outside the others range on
    mean_R_overall — it is less negative than every candidate
    because random entry beats every rule-based candidate the
    lab has tried. This is the structurally desired property of
    a binding null floor."""
    assert (
        null_payload["null_vs_others"]["null_compare"]["mean_r_overall"][
            "null_is_outside_others_range"
        ]
        is True
    )


# ---------------------------------------------------------------------------
# Phase 3 cross-campaign comparability headline pins
# ---------------------------------------------------------------------------


def test_all_5_invariant_axes_pass(comparability_payload: dict) -> None:
    """Pin: all 5 invariant axes (fold layout, pair universe, cost
    assumptions, schema, exit-reason vocab) are identical across
    the 5 campaigns. If any one of these regresses, the cross-
    campaign comparisons must be re-evaluated."""
    head = comparability_payload["headline"]
    assert head["n_invariant_axes_pass"] == 5
    assert head["n_invariant_axes_total"] == 5


def test_fold_layout_invariant_holds(comparability_payload: dict) -> None:
    inv = comparability_payload["invariants"]["fold_layout"]
    assert inv["all_campaigns_share_fold_layout"] is True
    assert inv["n_folds"] == 8
    assert inv["deviating_campaigns"] == []


def test_pair_universe_invariant_holds(comparability_payload: dict) -> None:
    inv = comparability_payload["invariants"]["pair_universe"]
    assert inv["all_campaigns_share_pair_universe"] is True
    assert set(inv["pair_universe_reference"]) == {
        "AUD_USD",
        "EUR_USD",
        "GBP_USD",
        "NZD_USD",
        "USD_CAD",
        "USD_CHF",
        "USD_JPY",
    }


def test_schema_invariant_holds(comparability_payload: dict) -> None:
    inv = comparability_payload["invariants"]["schema"]
    assert inv["single_column_set_across_all_campaigns"] is True
    assert inv["column_count"] == 14


def test_exit_reason_vocab_invariant_holds(comparability_payload: dict) -> None:
    inv = comparability_payload["invariants"]["exit_reason_vocab"]
    assert inv["all_share_exit_vocab"] is True
    assert inv["reference_vocab"] == ["eod", "stop", "time"]


def test_trade_window_asymmetry_is_present(comparability_payload: dict) -> None:
    """Pin F0-2: C010 and C011 are test-only; C012-014 are partial."""
    head = comparability_payload["headline"]
    assert head["trade_window_asymmetry_present"] is True


def test_exit_asymmetry_headline_survives_test_only(comparability_payload: dict) -> None:
    """The audit's most important finding: every campaign still
    has positive mean_R_given_time AND negative mean_R_overall
    when restricted to test-window trades. The earlier sprint's
    exit-asymmetry conclusions therefore stand."""
    s = comparability_payload["headline_survival"]
    assert s["all_campaigns_positive_mean_r_given_time_test_only"] is True
    assert s["all_campaigns_negative_mean_r_overall_test_only"] is True
    assert s["exit_asymmetry_headline_survives_test_only_restriction"] is True


def test_max_classification_severity_is_no_worse_than_weakens(
    comparability_payload: dict,
) -> None:
    """No axis classified as invalidates_comparison or
    requires_repair_sprint. If this regresses, the audit must be
    re-run before any cross-campaign screen runs."""
    sev = comparability_payload["headline"]["max_classification_severity"]
    allowed = {"harmless", "needs_documentation", "weakens_comparison"}
    assert sev in allowed, f"max severity {sev!r} is stronger than allowed"


def test_trade_window_classification_is_documentation_grade(
    comparability_payload: dict,
) -> None:
    """The trade-window asymmetry's classification must remain
    documentation-grade as long as the test-only restriction still
    keeps the headline alive. If the headline ever stops surviving,
    this test starts failing and the audit must be re-opened."""
    tw = next(
        f for f in comparability_payload["classification"]
        if f["axis"] == "trade_window_population"
    )
    s = comparability_payload["headline_survival"]
    if s["exit_asymmetry_headline_survives_test_only_restriction"]:
        assert tw["classification"] == "needs_documentation"
    else:
        # If the headline ever stops surviving, we expect the
        # classification to escalate (and this test forces an
        # explicit re-evaluation).
        assert tw["classification"] in {
            "weakens_comparison",
            "invalidates_comparison",
            "requires_repair_sprint",
        }


# ---------------------------------------------------------------------------
# Synthetic-vs-real corpus boundary
# ---------------------------------------------------------------------------


def test_legacy_outputs_readme_exists() -> None:
    """The synthetic-vs-real distinction README must be present in
    research/edge_discovery/studies/outputs/. Phase 4 of the audit
    added it to close the machine-readable-label gap."""
    assert (LEGACY_OUTPUTS / "README.md").is_file()


def test_every_real_output_has_data_kind_real() -> None:
    """Every JSON under outputs/real/ must carry
    provenance.data_kind == "real" (or "synthetic-fallback" — both
    are valid per the lab contract). Files in this directory must
    NEVER be silently produced from synthetic data."""
    real_dir = OUTPUTS
    for p in real_dir.glob("*.json"):
        j = json.loads(p.read_text(encoding="utf-8"))
        prov = j.get("provenance", {})
        assert prov.get("data_kind") in {"real", "synthetic-fallback"}, (
            f"{p.name}: provenance.data_kind = "
            f"{prov.get('data_kind')!r} (must be real or synthetic-fallback)"
        )
        assert prov.get("exploratory_only") is True, (
            f"{p.name}: provenance.exploratory_only is not True"
        )


def test_legacy_synthetic_outputs_are_static() -> None:
    """No active script may read from the legacy outputs/study_*.json
    files. If a future script needs them, it must move to outputs/real
    or be explicitly synthetic-labelled. This is a grep-style guard.

    The check scans research/, tests/, src/ for the four legacy
    output filenames; finds zero hits today. Any new reference would
    need to be reviewed for the synthetic-vs-real boundary.
    """
    needle_files = (
        "study_session",
        "study_event_window",
        "study_pair_baseline",
        "study_turnover_cost",
    )
    hits: list[str] = []
    for root in (REPO_ROOT / "research", REPO_ROOT / "tests", REPO_ROOT / "src"):
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            # We tolerate the script files themselves (they reference
            # their OWN outputs by name).
            if path.name in {
                "study_session.py",
                "study_event_window.py",
                "study_pair_baseline.py",
                "study_turnover_cost.py",
                "test_bias_of_fixtures.py",  # this file
            }:
                continue
            for needle in needle_files:
                # We tolerate "study_real_..." which is a different prefix
                if f"outputs/{needle}" in content:
                    hits.append(f"{path.relative_to(REPO_ROOT)}: cites outputs/{needle}")
    assert hits == [], (
        "active code references the legacy synthetic outputs by path. "
        "Either move to outputs/real or annotate synthetic origin "
        "explicitly. Hits:\n" + "\n".join(hits)
    )


# ---------------------------------------------------------------------------
# Freeze invariants
# ---------------------------------------------------------------------------


def test_approved_strategies_yaml_remains_empty() -> None:
    """Re-assert that this audit sprint did not add any approval."""
    cfg = (REPO_ROOT / "configs" / "approved_strategies.yaml").read_text(
        encoding="utf-8"
    )
    found = False
    for line in cfg.splitlines():
        stripped = line.strip()
        if stripped.startswith("approved:"):
            found = True
            assert stripped in {"approved: []"} or stripped == "approved:", (
                f"approved_strategies.yaml line was {stripped!r}, "
                "expected empty list"
            )
    assert found, "approved_strategies.yaml missing 'approved:' top-level key"

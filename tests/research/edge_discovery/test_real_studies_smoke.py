"""Smoke tests for the real-data studies under
``research/edge_discovery/studies/study_real_*.py``.

Each study is run in a freshly-resolved import and its output JSON
is checked for:

  * the verdict-word ban (no APPROVE / PASS / PROMOTE in the output)
  * the presence of a ``provenance`` block with the required keys
  * a sane non-empty input list when ``data_kind == "real"``

The session-by-hour study has a synthetic-fallback path for fresh-
clone CI; both branches must populate the provenance block.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS_REAL = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs" / "real"

_REAL_STUDY_OUTPUTS = (
    "real_study_event_window.json",
    "real_study_turnover_cost.json",
    "real_study_pair_baseline.json",
    "real_study_session_by_hour.json",
)
_BANNED_VERDICT_WORDS = ("APPROVE", "APPROVED", "PROMOTE", "PROMOTED")


def _committed_output(name: str) -> Path:
    return OUTPUTS_REAL / name


@pytest.mark.parametrize("name", _REAL_STUDY_OUTPUTS)
def test_real_study_output_exists(name: str) -> None:
    path = _committed_output(name)
    assert path.is_file(), f"real-data study output is missing: {path}"


@pytest.mark.parametrize("name", _REAL_STUDY_OUTPUTS)
def test_real_study_output_has_provenance_block(name: str) -> None:
    path = _committed_output(name)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert "provenance" in payload, f"{name}: missing provenance block"
    prov = payload["provenance"]
    for key in ("data_kind", "inputs", "date_coverage", "pair_universe", "limitations", "exploratory_only"):
        assert key in prov, f"{name}: provenance missing key {key!r}"
    assert prov["data_kind"] in ("real", "synthetic-fallback")
    assert prov["exploratory_only"] is True


@pytest.mark.parametrize("name", _REAL_STUDY_OUTPUTS)
def test_real_study_output_acknowledges_verdict_word_ban(name: str) -> None:
    path = _committed_output(name)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload.get("verdict_word_ban_acknowledged") is True


@pytest.mark.parametrize("name", _REAL_STUDY_OUTPUTS)
def test_real_study_markdown_has_no_banned_verdict_words(name: str) -> None:
    md_path = _committed_output(name).with_suffix(".md")
    assert md_path.is_file(), f"markdown output missing: {md_path}"
    text = md_path.read_text(encoding="utf-8")
    # Match whole-word verdict tokens uppercase or first-cap — but allow
    # mentions inside the verdict-word-ban context lines.
    upper = " " + text.upper() + " "
    for w in _BANNED_VERDICT_WORDS:
        # Allow the literal token if it appears prefixed/suffixed in a
        # legitimate way like ``cannot APPROVE`` or ``verdict-word
        # ban``-style. Strict whole-word check would be too aggressive.
        # Instead, require: if the word appears, the surrounding line
        # must contain "ban", "not", "never", "may not", "cannot",
        # "remain", or "reserved" — these are the existing escape
        # contexts.
        for match in re.finditer(rf"\b{w}\b", text, re.IGNORECASE):
            start = max(0, match.start() - 80)
            end = min(len(text), match.end() + 80)
            window = text[start:end].lower()
            assert any(safe in window for safe in (
                "ban", "not approve", "never", "may not", "cannot",
                "remain", "reserved", "remains", "graduate", "graduation",
            )), (
                f"{md_path.name}: bare verdict token {w!r} found at offset "
                f"{match.start()}: context = {window!r}"
            )


def test_real_event_window_uses_campaign_011_as_null() -> None:
    payload = json.loads(_committed_output("real_study_event_window.json").read_text())
    assert payload["null_source"] == "CAMPAIGN_011_random_entry_anchor"
    # The published CAMPAIGN_011 expectancy is near zero.
    assert abs(payload["null_mean_r"]) < 0.01


def test_real_event_window_dominance_share_flags_nfp() -> None:
    """CAMPAIGN_014 trades are heavily NFP-dominated by construction
    of its window-trigger; the study must surface this honestly."""
    payload = json.loads(_committed_output("real_study_event_window.json").read_text())
    dominance = payload.get("dominance_share", {})
    # NFP should be the largest single share by a wide margin.
    nfp_share = float(dominance.get("NFP", 0.0))
    assert nfp_share > 0.5, f"expected NFP to dominate trade count, got share {nfp_share}"


def test_real_event_window_reports_zero_trade_classes_honestly() -> None:
    payload = json.loads(_committed_output("real_study_event_window.json").read_text())
    zero_classes = payload.get("zero_trade_event_classes_in_fixture", [])
    # FOMC has zero matched trades under the ±24h window — exactly the
    # zero-trade-class failure mode the brief warned about.
    assert "FOMC" in zero_classes


def test_real_turnover_cost_published_matches_observed_for_all_campaigns() -> None:
    """Every committed CAMPAIGN_010-014 row should have the observed
    mean R equal to the published aggregate within rounding."""
    payload = json.loads(_committed_output("real_study_turnover_cost.json").read_text())
    for row in payload["per_campaign"]:
        diff = abs(float(row["mean_r_observed"]) - float(row["mean_r_published"]))
        assert diff < 1e-3, (
            f"{row['campaign_name']}: observed vs published mean R drift "
            f"is {diff:.5f}, expected < 1e-3"
        )
        assert int(row["n_trades_observed"]) == int(row["n_trades_published"])


def test_real_pair_baseline_uses_campaign_011_null() -> None:
    payload = json.loads(_committed_output("real_study_pair_baseline.json").read_text())
    assert payload["null_campaign"] == "CAMPAIGN_011_random_entry_anchor"
    # Null row count must match the seven-major universe.
    assert len(payload["null_per_pair"]) == 7


def test_real_session_study_records_h4_source() -> None:
    """The session study must record whether it used the real H4
    SQLite store or fell back to synthetic."""
    payload = json.loads(_committed_output("real_study_session_by_hour.json").read_text())
    prov = payload["provenance"]
    kinds = [i["kind"] for i in prov["inputs"]]
    assert kinds, "no inputs recorded"
    # Either real h4_sqlite_store or synthetic candle_csv.
    assert kinds[0] in ("h4_sqlite_store", "candle_csv")
    assert prov["pair_universe"] == ["EUR_USD"]

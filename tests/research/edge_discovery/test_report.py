"""Reporter tests — summarize_study + write_study_report.

Pin the verdict-word ban (refusing to write a Markdown body that
contains APPROVE / GO / PROMOTE), the JSON / Markdown round-trip, and
the per-group breakdown when ``labels`` is set on the forward returns.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from research.edge_discovery.costs import apply_cost_overlay
from research.edge_discovery.loaders import load_candles_csv
from research.edge_discovery.null import random_null_baseline
from research.edge_discovery.report import (
    StudySummary,
    summarize_study,
    write_study_report,
)
from research.edge_discovery.windows import Side, compute_forward_returns

REPO_ROOT = Path(__file__).resolve().parents[3]
H4_FIXTURE = REPO_ROOT / "research" / "edge_discovery" / "sample_fixtures" / "synthetic_EUR_USD_H4.csv"


def _summary_with_group() -> StudySummary:
    sample = load_candles_csv(H4_FIXTURE)
    sigs = [sample.frame.index[i] for i in (10, 30, 50, 80, 110, 140)]
    labels = ["NFP", "FOMC", "CPI", "NFP", "FOMC", "CPI"]
    fr = compute_forward_returns(sample.frame, sigs, window_bars=4, side=Side.LONG, labels=labels)
    with_costs = apply_cost_overlay(fr.per_signal, sample.instrument)
    null = random_null_baseline(
        sample.frame,
        n_trades=len(with_costs),
        window_bars=4,
        seeds=range(5),
        apply_cost_overlay_fn=apply_cost_overlay,
        instrument=sample.instrument,
    )
    return summarize_study(
        "event_window_smoke",
        with_costs,
        instrument=sample.instrument,
        granularity=sample.granularity,
        window_bars=4,
        null=null,
        dropped_trailing=fr.dropped_trailing,
        dropped_missing=fr.dropped_missing,
        inputs={"candles_path": sample.source_path, "candles_sha256": sample.source_sha256},
        notes=["synthetic-fixture run — not strategy evidence"],
    )


def test_summary_has_pre_and_post_cost_blocks() -> None:
    s = _summary_with_group()
    assert s.pre_cost["n"] == s.n_signals
    assert s.post_cost is not None
    assert s.post_cost["n"] == s.n_signals
    # Post-cost mean should be <= pre-cost mean (costs only subtract).
    assert s.post_cost["mean"] <= s.pre_cost["mean"]


def test_summary_by_group_keys_match_labels() -> None:
    s = _summary_with_group()
    assert set(s.by_group.keys()) == {"NFP", "FOMC", "CPI"}


def test_summary_null_compare_is_descriptive_band() -> None:
    s = _summary_with_group()
    assert s.null_compare is not None
    assert s.null_compare["band"] in {
        "within_null",
        "slightly_above_null",
        "materially_above_null",
        "slightly_below_null",
        "materially_below_null",
        "null_collapsed",
    }


def test_summary_empty_returns_yields_zero_n_summary() -> None:
    s = summarize_study(
        "empty",
        pd.DataFrame(),
        instrument="EUR_USD",
        granularity="H4",
        window_bars=5,
    )
    assert s.n_signals == 0
    assert s.pre_cost["n"] == 0


def test_write_study_report_writes_json_and_md(tmp_path: Path) -> None:
    s = _summary_with_group()
    j = tmp_path / "out.json"
    m = tmp_path / "out.md"
    write_study_report(s, json_path=j, md_path=m)
    assert j.is_file() and m.is_file()
    payload = json.loads(j.read_text(encoding="utf-8"))
    assert payload["label"] == "event_window_smoke"
    assert "pre_cost" in payload and "post_cost" in payload
    md = m.read_text(encoding="utf-8")
    assert "# Edge-discovery study — event_window_smoke" in md
    assert "Pre-cost" in md
    assert "Post-cost" in md


def test_write_study_report_rejects_verdict_words(tmp_path: Path) -> None:
    s = _summary_with_group()
    # Inject a banned word into a note — the writer must refuse.
    tainted = StudySummary(
        label=s.label,
        instrument=s.instrument,
        granularity=s.granularity,
        window_bars=s.window_bars,
        n_signals=s.n_signals,
        dropped_trailing=s.dropped_trailing,
        dropped_missing=s.dropped_missing,
        pre_cost=s.pre_cost,
        post_cost=s.post_cost,
        null_compare=s.null_compare,
        by_group=s.by_group,
        notes=["this finding says APPROVE the candidate"],
        inputs=s.inputs,
    )
    with pytest.raises(ValueError, match="banned verdict word"):
        write_study_report(tainted, json_path=tmp_path / "x.json", md_path=tmp_path / "x.md")

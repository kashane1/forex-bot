"""Compare synthetic stress financing assumptions vs observed practice fixtures."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from forex_bot.research.observed_financing_fixture import (
    ObservedFinancingFixture,
    validate_observed_fixture,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OBSERVED = ROOT / "research/observed_financing_capture_readonly/observed_practice_financing.json"
DEFAULT_SYNTHETIC_DELTA = ROOT / "research/financing_overlay_local_first/adjusted_metric_delta.json"


def load_observed_fixture(path: Path | None = None) -> ObservedFinancingFixture | None:
    p = path or DEFAULT_OBSERVED
    if not p.is_file():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    return validate_observed_fixture(data)


def summarize_observed(fixture: ObservedFinancingFixture) -> dict[str, Any]:
    by_instrument: dict[str, float] = defaultdict(float)
    for entry in fixture.entries:
        if entry.instrument:
            by_instrument[entry.instrument] += float(entry.financing_home)
    return {
        "entry_count": len(fixture.entries),
        "financing_transaction_count": fixture.transaction_counts.get("financing", 0),
        "unknown_transaction_count": fixture.transaction_counts.get("unknown", 0),
        "financing_total_by_instrument": dict(by_instrument),
        "capture_window": fixture.capture_window,
        "sufficient_for_rate_inference": len(fixture.entries) >= 10,
    }


def compare_to_synthetic_overlay(
    observed: ObservedFinancingFixture | None,
    *,
    synthetic_delta_path: Path | None = None,
) -> dict[str, Any]:
    syn_path = synthetic_delta_path or DEFAULT_SYNTHETIC_DELTA
    synthetic_drag: dict[str, float] = {}
    if syn_path.is_file():
        synthetic_drag = json.loads(syn_path.read_text(encoding="utf-8"))

    obs_summary = summarize_observed(observed) if observed else {"entry_count": 0}
    sufficient = bool(obs_summary.get("sufficient_for_rate_inference"))
    conclusion = "inconclusive"
    if observed and observed.entries:
        conclusion = "observed_sample_sparse"
    if sufficient:
        conclusion = "needs_deeper_reconciliation"
    if not observed or not observed.entries:
        conclusion = "synthetic_only_no_observed_data"

    return {
        "strategy_evidence": False,
        "not_approved": True,
        "observed": obs_summary,
        "synthetic_ledger_drag_r": synthetic_drag,
        "conclusion": conclusion,
        "synthetic_vs_observed": (
            "Synthetic stress drag on reference ledgers is material (~0.04–0.08R). "
            "Without sufficient observed entries, treat stress as conservative directional "
            "bound, not calibrated truth."
        ),
    }

"""Edge-discovery lab — lightweight pre-campaign exploratory workbench.

A small reusable module for testing many signal ideas cheaply before
turning any one of them into a full formal campaign. Reads only
committed local research artifacts, never touches the broker, never
approves a strategy. See ``docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md``
for the lab contract and graduation criteria.

The lab cannot, by construction, produce a verdict word — APPROVE /
PASS / GO / PROMOTE are reserved for the formal campaign machinery. A
lab finding is at best a candidate hypothesis with cheap supporting
evidence.

Public API:

    load_candles_csv(path)
    load_event_fixture(path)
    compute_forward_returns(frame, signal_times, *, window_bars, side)
    apply_cost_overlay(returns_df, instrument, *, spread_pips, slip_pips)
    random_null_baseline(frame, *, n_trades, window_bars, seeds)
    summarize_study(label, returns_df, *, null=None, group_by=None)
    write_study_report(summary, *, json_path, md_path)
"""

from __future__ import annotations

from research.edge_discovery.costs import apply_cost_overlay
from research.edge_discovery.loaders import (
    CandleSample,
    EventFixture,
    load_candles_csv,
    load_event_fixture,
)
from research.edge_discovery.null import NullBaseline, random_null_baseline
from research.edge_discovery.report import StudySummary, summarize_study, write_study_report
from research.edge_discovery.windows import ForwardReturns, Side, compute_forward_returns

__all__ = [
    "CandleSample",
    "EventFixture",
    "ForwardReturns",
    "NullBaseline",
    "Side",
    "StudySummary",
    "apply_cost_overlay",
    "compute_forward_returns",
    "load_candles_csv",
    "load_event_fixture",
    "random_null_baseline",
    "summarize_study",
    "write_study_report",
]

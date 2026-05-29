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

Public API (synthetic-fixture path — unchanged):

    load_candles_csv(path)
    load_event_fixture(path)
    compute_forward_returns(frame, signal_times, *, window_bars, side)
    apply_cost_overlay(returns_df, instrument, *, spread_pips, slip_pips)
    random_null_baseline(frame, *, n_trades, window_bars, seeds)
    summarize_study(label, returns_df, *, null=None, group_by=None)
    write_study_report(summary, *, json_path, md_path)

Public API (real-data hydration — added by
research-edge-discovery-lab-hydrate-001):

    resolve_h4_store_path(repo_root)
    load_h4_candles_from_sqlite(db_path, instrument, *, from_time, to_time)
    load_campaign_walk_forward_result(campaign_dir)
    load_campaign_fold_pair_summaries(campaign_dir)
    fold_pair_summaries_to_frame(summaries)
    load_campaign_trades(campaign_dir, *, instruments)
    load_event_fixture_json(path)
    StudyProvenance / StudyInput dataclasses

Public API (matched-null / gap diagnostics — added by
research-edge-discovery-null-benchmark-lab-001):

    matched_null_baseline(ledger, frames_by_pair, *, mode, window_bars, seeds)
    interpret_matched_null(result)
    MatchedNullResult / MATCHED_NULL_MODES
    (see also research.edge_discovery.filter_ablation and
     research.edge_discovery.multiple_comparison)
"""

from __future__ import annotations

from research.edge_discovery.costs import apply_cost_overlay
from research.edge_discovery.loaders import (
    CandleSample,
    EventFixture,
    load_candles_csv,
    load_event_fixture,
)
from research.edge_discovery.matched_nulls import (
    MATCHED_NULL_MODES,
    MatchedNullResult,
    interpret_matched_null,
    matched_null_baseline,
)
from research.edge_discovery.null import NullBaseline, random_null_baseline
from research.edge_discovery.real_data import (
    CampaignWalkForwardResult,
    FoldPairSummary,
    StudyInput,
    StudyProvenance,
    assert_real_data_kind,
    fold_pair_summaries_to_frame,
    load_campaign_fold_pair_summaries,
    load_campaign_trades,
    load_campaign_walk_forward_result,
    load_event_fixture_json,
    load_h4_candles_from_sqlite,
    resolve_h4_store_path,
)
from research.edge_discovery.report import StudySummary, summarize_study, write_study_report
from research.edge_discovery.windows import ForwardReturns, Side, compute_forward_returns

__all__ = [
    "MATCHED_NULL_MODES",
    "CampaignWalkForwardResult",
    "CandleSample",
    "EventFixture",
    "FoldPairSummary",
    "ForwardReturns",
    "MatchedNullResult",
    "NullBaseline",
    "Side",
    "StudyInput",
    "StudyProvenance",
    "StudySummary",
    "apply_cost_overlay",
    "assert_real_data_kind",
    "compute_forward_returns",
    "fold_pair_summaries_to_frame",
    "interpret_matched_null",
    "load_campaign_fold_pair_summaries",
    "load_campaign_trades",
    "load_campaign_walk_forward_result",
    "load_candles_csv",
    "load_event_fixture",
    "load_event_fixture_json",
    "load_h4_candles_from_sqlite",
    "matched_null_baseline",
    "random_null_baseline",
    "resolve_h4_store_path",
    "summarize_study",
    "write_study_report",
]

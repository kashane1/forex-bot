"""Infer H4 research window and external-feature observation range."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from research.cost_atlas.loader import SEVEN_PAIR_UNIVERSE, load_deduped_h4_frame
from research.edge_discovery.real_data import resolve_h4_store_path


@dataclass(frozen=True)
class ResearchWindow:
    h4_first: pd.Timestamp
    h4_last: pd.Timestamp
    h4_bar_count: int
    observation_start: str
    observation_end: str
    warmup_start: str = "2018-01-01"


def resolve_h4_research_window(
    repo_root: Path,
    *,
    db_path: Path | None = None,
    warmup_start: str = "2018-01-01",
) -> ResearchWindow:
    db_path = db_path or resolve_h4_store_path(repo_root)
    if db_path is None:
        raise FileNotFoundError("H4 SQLite store not found")
    mins: list[pd.Timestamp] = []
    maxs: list[pd.Timestamp] = []
    total_bars = 0
    for instrument in SEVEN_PAIR_UNIVERSE:
        frame, _ = load_deduped_h4_frame(repo_root, instrument, db_path=db_path)
        if len(frame) == 0:
            continue
        mins.append(frame.index.min())
        maxs.append(frame.index.max())
        total_bars = max(total_bars, len(frame))
    if not mins:
        raise ValueError("no H4 bars loaded from store")
    h4_first = min(mins)
    h4_last = max(maxs)
    obs_end = h4_last.tz_convert("UTC").strftime("%Y-%m-%d")
    return ResearchWindow(
        h4_first=h4_first,
        h4_last=h4_last,
        h4_bar_count=total_bars,
        observation_start=warmup_start,
        observation_end=obs_end,
    )


def research_window_report(repo_root: Path, *, db_path: Path | None = None) -> dict[str, object]:
    window = resolve_h4_research_window(repo_root, db_path=db_path)
    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "h4_first_bar": str(window.h4_first),
        "h4_last_bar": str(window.h4_last),
        "h4_bar_count_max_per_pair": window.h4_bar_count,
        "observation_start": window.observation_start,
        "observation_end": window.observation_end,
        "warmup_rationale": (
            f"Observation start {window.observation_start} provides warmup before "
            f"H4 research start {window.h4_first} for derived 1d features."
        ),
    }

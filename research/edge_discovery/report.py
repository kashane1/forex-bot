"""Summarize and emit lab-study results.

A study produces:

  * a ``StudySummary`` dataclass with descriptive statistics,
    optional per-group breakdown, and an optional null comparison,
  * a JSON file with the same content (for programmatic consumption),
  * a Markdown file (for human review).

The Markdown writer deliberately uses descriptive language only — it
never emits ``APPROVE``, ``PASS``, ``GO``, or ``PROMOTE``. The
verdict-word ban from the lab plan is enforced by ``write_study_report``
at write time.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path

import pandas as pd

from research.edge_discovery.null import NullBaseline, compare_to_null

_BANNED_VERDICT_WORDS = ("APPROVE", "APPROVED", "GO", "PROMOTE", "PROMOTED")


def _summary_stats(returns: pd.Series) -> dict[str, float]:
    if len(returns) == 0:
        return {
            "n": 0,
            "mean": 0.0,
            "std": 0.0,
            "median": 0.0,
            "win_rate": 0.0,
            "p10": 0.0,
            "p90": 0.0,
        }
    arr = returns.dropna()
    return {
        "n": len(arr),
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        "median": float(arr.median()),
        "win_rate": float((arr > 0).mean()),
        "p10": float(arr.quantile(0.10)),
        "p90": float(arr.quantile(0.90)),
    }


@dataclass(frozen=True)
class StudySummary:
    label: str
    instrument: str
    granularity: str
    window_bars: int
    n_signals: int
    dropped_trailing: int
    dropped_missing: int
    pre_cost: dict[str, float]
    post_cost: dict[str, float] | None
    null_compare: dict[str, object] | None
    by_group: dict[str, dict[str, float]] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    inputs: dict[str, object] = field(default_factory=dict)


def summarize_study(
    label: str,
    returns_df: pd.DataFrame,
    *,
    instrument: str,
    granularity: str,
    window_bars: int,
    null: NullBaseline | None = None,
    group_by: str | None = "label",
    dropped_trailing: int = 0,
    dropped_missing: int = 0,
    notes: list[str] | None = None,
    inputs: Mapping[str, object] | None = None,
) -> StudySummary:
    """Summarize a forward-returns DataFrame into a StudySummary.

    If ``returns_df`` contains ``log_return_post_cost`` the post-cost
    stats are filled in; otherwise only pre-cost.

    ``group_by`` defaults to ``"label"`` so studies that pass per-signal
    labels (event class, pair, session) get a free per-group breakdown.
    """
    if returns_df is None or returns_df.empty:
        return StudySummary(
            label=label,
            instrument=instrument,
            granularity=granularity,
            window_bars=window_bars,
            n_signals=0,
            dropped_trailing=int(dropped_trailing),
            dropped_missing=int(dropped_missing),
            pre_cost=_summary_stats(pd.Series(dtype=float)),
            post_cost=None,
            null_compare=None,
            notes=list(notes or []),
            inputs=dict(inputs or {}),
        )

    pre = _summary_stats(returns_df["log_return"])
    post = None
    if "log_return_post_cost" in returns_df.columns:
        post = _summary_stats(returns_df["log_return_post_cost"])

    null_compare = None
    if null is not None:
        study_mean = post["mean"] if post is not None else pre["mean"]
        null_compare = compare_to_null(study_mean, null)
        null_compare["null_mean"] = null.mean_of_means
        null_compare["null_std"] = null.std_of_means
        null_compare["null_seeds"] = list(null.seeds_used)
        null_compare["null_n_per_seed"] = null.n_trades_per_seed

    by_group: dict[str, dict[str, float]] = {}
    if group_by is not None and group_by in returns_df.columns:
        target_col = "log_return_post_cost" if "log_return_post_cost" in returns_df.columns else "log_return"
        for key, sub in returns_df.groupby(group_by):
            stats = _summary_stats(sub[target_col])
            stats["sub_pre_mean"] = float(sub["log_return"].mean())
            if "log_return_post_cost" in sub.columns:
                stats["sub_post_mean"] = float(sub["log_return_post_cost"].mean())
            by_group[str(key)] = stats

    return StudySummary(
        label=label,
        instrument=instrument,
        granularity=granularity,
        window_bars=window_bars,
        n_signals=len(returns_df),
        dropped_trailing=int(dropped_trailing),
        dropped_missing=int(dropped_missing),
        pre_cost=pre,
        post_cost=post,
        null_compare=null_compare,
        by_group=by_group,
        notes=list(notes or []),
        inputs=dict(inputs or {}),
    )


def _check_no_verdict_words(text: str) -> None:
    upper = text.upper()
    for w in _BANNED_VERDICT_WORDS:
        if f" {w} " in f" {upper} " or upper.startswith(w + " ") or upper.endswith(" " + w):
            raise ValueError(
                f"refusing to write study report: contains banned verdict word {w!r}. "
                "Lab outputs may not approve, promote, or pass a strategy — that is reserved "
                "for the formal campaign machinery."
            )


def _md_summary(s: StudySummary) -> str:
    lines: list[str] = []
    lines.append(f"# Edge-discovery study — {s.label}")
    lines.append("")
    lines.append("> Exploratory lab output. Not a strategy verdict; does not approve, ")
    lines.append("> promote, or change any campaign status. See ")
    lines.append("> `docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md`.")
    lines.append("")
    lines.append("## Setup")
    lines.append("")
    lines.append(f"- Instrument: `{s.instrument}`")
    lines.append(f"- Granularity: `{s.granularity}`")
    lines.append(f"- Forward window (bars): `{s.window_bars}`")
    lines.append(f"- Signals used: `{s.n_signals}` (dropped trailing: `{s.dropped_trailing}`, dropped missing: `{s.dropped_missing}`)")
    if s.inputs:
        lines.append("")
        lines.append("### Inputs")
        for k, v in s.inputs.items():
            lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Pre-cost")
    lines.append("")
    lines.append(_stats_table(s.pre_cost))
    if s.post_cost is not None:
        lines.append("")
        lines.append("## Post-cost")
        lines.append("")
        lines.append(_stats_table(s.post_cost))
    if s.null_compare is not None:
        lines.append("")
        lines.append("## Null comparison (descriptive — not a significance test)")
        lines.append("")
        nc = s.null_compare
        lines.append(f"- Null mean (random-entry, sample-matched): `{nc.get('null_mean'):+.6f}`")
        std_val = nc.get('null_std') or 0.0
        lines.append(f"- Null std across seeds: `{std_val:.6f}`")
        gap_val = nc.get('gap') or 0.0
        lines.append(f"- Study mean − null mean: `{gap_val:+.6f}`")
        gns = nc.get('gap_in_null_stds')
        if gns is not None:
            lines.append(f"- Gap in null stds: `{gns:+.2f}`")
        lines.append(f"- Band: `{nc.get('band')}`")
    if s.by_group:
        lines.append("")
        lines.append("## By group")
        lines.append("")
        lines.append("| group | n | mean | std | win_rate | sub_pre_mean | sub_post_mean |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for k, st in s.by_group.items():
            sub_post = st.get('sub_post_mean')
            sub_post_s = f"{sub_post:+.6f}" if sub_post is not None else "—"
            lines.append(
                f"| {k} | {int(st['n'])} | {st['mean']:+.6f} | "
                f"{st['std']:.6f} | {st['win_rate']:.2%} | "
                f"{st.get('sub_pre_mean', 0.0):+.6f} | {sub_post_s} |"
            )
    if s.notes:
        lines.append("")
        lines.append("## Notes")
        lines.append("")
        for n in s.notes:
            lines.append(f"- {n}")
    lines.append("")
    return "\n".join(lines)


def _stats_table(stats: dict[str, float]) -> str:
    return (
        "| n | mean | std | median | win_rate | p10 | p90 |\n"
        "|---:|---:|---:|---:|---:|---:|---:|\n"
        f"| {int(stats['n'])} | {stats['mean']:+.6f} | {stats['std']:.6f} | "
        f"{stats['median']:+.6f} | {stats['win_rate']:.2%} | "
        f"{stats['p10']:+.6f} | {stats['p90']:+.6f} |"
    )


def write_study_report(
    summary: StudySummary,
    *,
    json_path: str | Path,
    md_path: str | Path,
) -> None:
    """Write the JSON + Markdown artifacts for a lab study.

    Refuses to write if the Markdown body would contain any banned
    verdict word (APPROVE / GO / PROMOTE etc.) — see the lab plan
    Safety Constraints section.
    """
    md = _md_summary(summary)
    _check_no_verdict_words(md)
    json_path = Path(json_path)
    md_path = Path(md_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(summary)
    json_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    md_path.write_text(md + "\n", encoding="utf-8")

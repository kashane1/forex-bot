"""Markdown rendering for walk-forward plans and results.

Pure formatting; no I/O side effects beyond the string return. The
dry-run script chooses where to write the rendered output.
"""

from __future__ import annotations

from research.walk_forward.models import WalkForwardPlan, WalkForwardResults


def render_plan_md(plan: WalkForwardPlan) -> str:
    lines: list[str] = []
    lines.append(f"# Walk-Forward Plan — {plan.campaign_name}")
    lines.append("")
    lines.append(
        "> `strategy_evidence: false`. The harness produces fold plans, "
        "not strategy verdicts. A clean plan does not approve a strategy."
    )
    lines.append("")
    lines.append(f"- Universe: `{plan.universe_start}` → `{plan.universe_end}`")
    lines.append(f"- Split style: `{plan.split_style.value}`")
    lines.append(f"- Parameter mode: `{plan.parameter_mode.value}`")
    lines.append(f"- Fold count: **{len(plan.folds)}**")
    lines.append("")
    if plan.notes:
        lines.append("## Notes")
        lines.append("")
        for note in plan.notes:
            lines.append(f"- {note}")
        lines.append("")
    lines.append("## Folds")
    lines.append("")
    lines.append(
        "| # | train | validation | test |\n"
        "|---|---|---|---|"
    )
    for fold in plan.folds:
        lines.append(
            f"| {fold.fold_index} | "
            f"`{fold.train_start}` → `{fold.train_end}` | "
            f"`{fold.validation_start}` → `{fold.validation_end}` | "
            f"`{fold.test_start}` → `{fold.test_end}` |"
        )
    lines.append("")
    return "\n".join(lines)


def render_results_md(results: WalkForwardResults) -> str:
    plan = results.plan
    agg = results.aggregate
    lines: list[str] = []
    lines.append(f"# Walk-Forward Results — {plan.campaign_name}")
    lines.append("")
    lines.append(
        "> `strategy_evidence: false`. A PASS / REJECT verdict here is one "
        "of several gates required before paper / demo. It does not "
        "approve a strategy."
    )
    lines.append("")
    lines.append(f"- Universe: `{plan.universe_start}` → `{plan.universe_end}`")
    lines.append(f"- Split style: `{plan.split_style.value}`")
    lines.append(f"- Parameter mode: `{plan.parameter_mode.value}`")
    lines.append(
        f"- Folds: **{agg.fold_count}** — passing gates: "
        f"**{agg.folds_passing_gates}** "
        f"(rate {agg.fold_pass_rate:.2%})"
    )
    lines.append(f"- Total trades across folds: **{agg.total_trades_across_folds}**")
    if agg.aggregate_expectancy_r is not None:
        lines.append(
            f"- Aggregate expectancy R: **{agg.aggregate_expectancy_r:+.4f}**"
        )
    if agg.aggregate_return_pct is not None:
        lines.append(
            f"- Aggregate return %: **{agg.aggregate_return_pct:+.4f}**"
        )
    if agg.single_fold_max_return_share is not None:
        lines.append(
            f"- Single-fold max return share: "
            f"**{agg.single_fold_max_return_share:.2%}**"
        )
    lines.append(f"- **Overall verdict: {results.overall_verdict}**")
    lines.append("")
    lines.append("## Per-fold metrics")
    lines.append("")
    lines.append(
        "| # | trades | exp R | return % | PF | DD % | win % | gates |\n"
        "|---|---|---|---|---|---|---|---|"
    )
    for fold_metrics in results.fold_metrics:
        gates = "PASS" if fold_metrics.pass_pre_commit_gates else "REJECT"
        lines.append(
            f"| {fold_metrics.fold_index} | "
            f"{fold_metrics.total_trades} | "
            f"{_fmt(fold_metrics.expectancy_r)} | "
            f"{_fmt(fold_metrics.return_pct)} | "
            f"{_fmt(fold_metrics.profit_factor)} | "
            f"{_fmt(fold_metrics.max_drawdown_pct)} | "
            f"{_fmt(fold_metrics.win_rate)} | "
            f"**{gates}** |"
        )
    lines.append("")
    return "\n".join(lines)


def _fmt(value: float | None) -> str:
    if value is None:
        return "—"
    if value != value:  # NaN
        return "—"
    return f"{value:.4f}"

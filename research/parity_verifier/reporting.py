"""Markdown report rendering for the verifier and comparison output.

Pure formatting; no I/O side effects beyond the string return. The
script entry point chooses where to write the result.
"""

from __future__ import annotations

from research.parity_verifier.models import ComparisonReport, ComparisonStatus, VerifierResult


def render_verifier_result_md(result: VerifierResult) -> str:
    lines: list[str] = []
    lines.append(f"# Free / Local Parity Verifier — {result.parity_target}")
    lines.append("")
    lines.append(
        "> `strategy_evidence: false`. This output measures the bespoke "
        "engine's behavior against an independent re-implementation. It "
        "approves no strategy. CAMPAIGN_002 remains REJECT."
    )
    lines.append("")
    lines.append(f"- Window: `{result.window_start.isoformat()}` → `{result.window_end.isoformat()}`")
    lines.append(f"- Fill timing: `{result.fill_timing}`")
    lines.append(f"- Config hash: `{result.config_hash}`")
    lines.append(f"- Risk engine used: `{result.risk_engine_used}`")
    lines.append(f"- Total trades: **{result.total_trades}**")
    lines.append("")
    lines.append("| instrument | candles | trades | expectancy R | return % | profit factor | win rate |")
    lines.append("|---|---|---|---|---|---|---|")
    for pair in result.pairs:
        lines.append(
            f"| {pair.instrument} | {pair.candle_count} | {pair.trades} | "
            f"{_fmt(pair.expectancy_r)} | {_fmt(pair.return_pct)} | "
            f"{_fmt(pair.profit_factor)} | {_fmt(pair.win_rate)} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_comparison_md(report: ComparisonReport) -> str:
    lines: list[str] = []
    lines.append("# Free / Local Parity Verifier — Comparison vs Bespoke Reference")
    lines.append("")
    lines.append(
        "> `strategy_evidence: false`. A PASS or FAIL here describes "
        "agreement between two engines on a rejected strategy. It does "
        "**not** approve a strategy and does not lift the freeze."
    )
    lines.append("")
    lines.append(f"- Bespoke reference: `{report.bespoke_reference_path}`")
    lines.append(
        f"- Verifier result: `{report.verifier_result_path or '— not produced (BLOCKED)'}`"
    )
    lines.append(f"- Overall status: **{report.overall_status.value.upper()}**")
    lines.append(f"- Overall classification: `{report.overall_classification.value}`")
    lines.append(
        f"- Bespoke total trades: **{report.bespoke_total_trades}** · "
        f"Verifier total trades: **{_fmt(report.verifier_total_trades)}** · "
        f"Δ: {_fmt_pct(report.total_trade_count_delta_pct)}"
    )
    lines.append("")
    lines.append(
        "| instrument | bespoke trades | verifier trades | Δ % | bespoke exp R | verifier exp R | Δ R | bespoke ret % | verifier ret % | Δ pp | status | classification |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for pair in report.pairs:
        lines.append(
            f"| {pair.instrument} | {pair.bespoke_trades} | "
            f"{_fmt(pair.verifier_trades)} | {_fmt_pct(pair.trade_count_delta_pct)} | "
            f"{_fmt(pair.bespoke_expectancy_r)} | {_fmt(pair.verifier_expectancy_r)} | "
            f"{_fmt(pair.expectancy_r_delta)} | "
            f"{_fmt(pair.bespoke_return_pct)} | {_fmt(pair.verifier_return_pct)} | "
            f"{_fmt(pair.return_pct_delta)} | "
            f"{pair.status.value.upper()} | {pair.classification.value} |"
        )
    lines.append("")
    if report.notes:
        lines.append("## Notes")
        lines.append("")
        for note in report.notes:
            lines.append(f"- {note}")
        lines.append("")
    if report.overall_status is ComparisonStatus.BLOCKED:
        lines.append(
            "**BLOCKED.** The verifier could not produce a result for this "
            "comparison. See the notes above for the precise reason."
        )
        lines.append("")
    return "\n".join(lines)


def _fmt(value: float | int | None) -> str:
    if value is None:
        return "—"
    if isinstance(value, int):
        return str(value)
    if value != value:  # NaN
        return "—"
    return f"{value:.4f}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:+.2f}%"

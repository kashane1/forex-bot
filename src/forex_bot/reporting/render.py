"""Markdown and minimal HTML rendering for WeeklyReport."""

from __future__ import annotations

import html

from forex_bot.reporting.weekly import WeeklyReport


def render_markdown(report: WeeklyReport) -> str:
    lines: list[str] = []
    lines.append("# Weekly Bot Report")
    lines.append("")
    lines.append(f"- Generated at: `{report.generated_at.isoformat()}`")
    lines.append(f"- Window: `{report.window_start.isoformat()}` → `{report.window_end.isoformat()}`")
    lines.append(f"- Config hash: `{report.config_hash}`")
    if report.code_commit_hash:
        lines.append(f"- Code commit: `{report.code_commit_hash}`")
    lines.append("")
    lines.append("## Account")
    lines.append(f"- NAV: `{report.account_nav}`")
    lines.append(f"- Realized P/L (7d): `{report.realized_pl}`")
    lines.append(f"- Unrealized P/L: `{report.unrealized_pl}`")
    lines.append("")
    lines.append("## Trading")
    lines.append(f"- Closed trades: `{report.closed_trade_count}`")
    lines.append(f"- Win rate: `{report.win_rate:.2%}`")
    lines.append(f"- Profit factor: `{report.profit_factor:.2f}`")
    lines.append(f"- Average win: `{report.average_win}`")
    lines.append(f"- Average loss: `{report.average_loss}`")
    lines.append(f"- Largest single loss: `{report.largest_single_loss}`")
    lines.append("")
    lines.append("## Risk rejections (7d)")
    if not report.risk_rejections:
        lines.append("- _No rejections recorded._")
    else:
        for code, count in sorted(report.risk_rejections.items(), key=lambda kv: -kv[1]):
            lines.append(f"- `{code}`: {count}")
    lines.append("")
    lines.append("## Reconciliation mismatches")
    if not report.reconciliation_mismatches:
        lines.append("- _None this week._")
    else:
        for msg in report.reconciliation_mismatches:
            lines.append(f"- {msg}")
    lines.append("")
    return "\n".join(lines)


def render_html(report: WeeklyReport) -> str:
    body = (
        "<h1>Weekly Bot Report</h1>"
        f"<p><strong>Generated:</strong> {html.escape(report.generated_at.isoformat())}</p>"
        f"<p><strong>Window:</strong> {html.escape(report.window_start.isoformat())} → "
        f"{html.escape(report.window_end.isoformat())}</p>"
        f"<p><strong>Config hash:</strong> {html.escape(report.config_hash)}</p>"
        "<h2>Account</h2><ul>"
        f"<li>NAV: {html.escape(str(report.account_nav))}</li>"
        f"<li>Realized P/L (7d): {html.escape(str(report.realized_pl))}</li>"
        f"<li>Unrealized P/L: {html.escape(str(report.unrealized_pl))}</li>"
        "</ul>"
        "<h2>Trading</h2><ul>"
        f"<li>Closed trades: {report.closed_trade_count}</li>"
        f"<li>Win rate: {report.win_rate:.2%}</li>"
        f"<li>Profit factor: {report.profit_factor:.2f}</li>"
        "</ul>"
    )
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Weekly Report</title></head><body>{body}</body></html>"

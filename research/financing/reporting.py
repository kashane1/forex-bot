"""Markdown + JSON reporting helpers.

Pure formatting. No I/O — callers write the strings wherever they
need to. Determinism: same input ⇒ bit-identical output.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from research.financing.models import (
    DailyFinancingEvent,
    FinancingRunReport,
    PositionFinancingSummary,
)


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        # Force consistent timezone-suffix form.
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"unserializable: {type(value).__name__}: {value!r}")


def dump_events_json(report: FinancingRunReport) -> str:
    """Serialize the entire run report to a UTF-8 JSON string with
    sorted keys, ISO-8601 dates, and 2-space indent."""
    payload = report.model_dump(mode="python")
    return json.dumps(
        payload,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
        default=_json_default,
    )


def _fmt(value: float, decimals: int = 6) -> str:
    """Stable float-to-string with fixed decimals. Avoids locale
    or scientific-notation drift between platforms."""
    return f"{value:.{decimals}f}"


def _event_line(e: DailyFinancingEvent) -> str:
    long = "n/a" if e.rate_long_annual_bp is None else _fmt(e.rate_long_annual_bp, 4)
    short = "n/a" if e.rate_short_annual_bp is None else _fmt(e.rate_short_annual_bp, 4)
    parts = [
        f"`{e.date_utc.isoformat()}`",
        f"weekday={e.weekday}",
        f"x{e.rollover_multiplier}",
        f"long_bp={long}",
        f"short_bp={short}",
        f"applied={e.applied_side}",
        f"bp/day={_fmt(e.applied_rate_bp_per_day, 4)}",
        f"notional={_fmt(e.notional_home, 2)}",
        f"cashflow={_fmt(e.cashflow_home, 6)}",
        f"stress={_fmt(e.cashflow_home_stress, 6)}",
    ]
    if e.rate_was_missing:
        parts.append("**MISSING**")
    line = " · ".join(parts)
    if e.notes:
        note_str = "; ".join(e.notes)
        line += f" — {note_str}"
    return line


def _summary_section(s: PositionFinancingSummary) -> list[str]:
    out: list[str] = []
    miss_tag = " · **missing rates**" if s.rate_was_missing_any else ""
    out.append(
        f"### {s.position_id} — {s.instrument} {s.side}"
        f" · rollovers={s.rollovers}"
        f" · cashflow={_fmt(s.cashflow_home_total, 6)}"
        f" · stress={_fmt(s.cashflow_home_stress_total, 6)}"
        f"{miss_tag}"
    )
    if not s.events:
        out.append("")
        out.append("_no rollover events_")
        return out
    out.append("")
    for e in s.events:
        out.append(f"- {_event_line(e)}")
    return out


def render_summary_md(report: FinancingRunReport) -> str:
    """Render a full markdown summary of the run report.

    Deterministic — same input ⇒ bit-identical output (besides
    the embedded ``generated_at_utc``, which the caller controls
    via ``calculate_run(now=...)``).
    """
    lines: list[str] = []
    lines.append("# Financing Run Report")
    lines.append("")
    lines.append(
        f"`strategy_evidence: false` · "
        f"`financing_treatment: {report.financing_treatment.value}` · "
        f"`financing_in_engine_pnl: false` · "
        f"`financing_is_live_blocker: true`"
    )
    lines.append("")
    lines.append("## Run metadata")
    lines.append("")
    lines.append(f"- generated_at_utc: `{report.generated_at_utc.isoformat()}`")
    lines.append(f"- rate_source: `{report.rate_source_name}`")
    lines.append(f"- home_currency: `{report.home_currency}`")
    lines.append(f"- rollover_hour_utc: {report.config.rollover_hour_utc}")
    triple = (
        "disabled"
        if report.config.triple_swap_weekday is None
        else str(report.config.triple_swap_weekday)
    )
    lines.append(f"- triple_swap_weekday: {triple}")
    lines.append(f"- skip_weekends: {report.config.skip_weekends}")
    lines.append(
        f"- missing_rate_policy: {report.config.missing_rate_policy.value}"
    )
    lines.append(
        f"- conservative_fallback_bp_per_day: "
        f"{report.config.conservative_fallback_bp_per_day}"
    )
    lines.append("")
    lines.append("## Aggregate")
    lines.append("")
    lines.append(f"- positions: {len(report.positions)}")
    lines.append(f"- event_count: {report.event_count}")
    lines.append(f"- missing_rate_event_count: {report.missing_rate_event_count}")
    lines.append(
        f"- cashflow_home_total: {_fmt(report.cashflow_home_total, 6)}"
    )
    lines.append(
        f"- cashflow_home_stress_total: "
        f"{_fmt(report.cashflow_home_stress_total, 6)}"
    )
    lines.append("")
    if not report.positions:
        lines.append("## Positions")
        lines.append("")
        lines.append("_no positions_")
        lines.append("")
    else:
        lines.append("## Positions")
        lines.append("")
        for s in report.positions:
            lines.extend(_summary_section(s))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"

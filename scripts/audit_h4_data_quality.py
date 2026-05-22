#!/usr/bin/env python3
"""Audit the local OANDA H4 research store for data quality.

Read-only. Reads `data/oanda_h4_research.sqlite3` and reports, per pair,
the completeness and quality signals that matter before the data is used
in a diagnostic or a Lean parity export. **No OANDA call, no
credentials** — it operates purely on the local store.

Gaps are explicitly classified into expected closures (weekend,
year-end holiday) and concerning gaps (outage-like, suspicious-short).
Abnormal spreads are bucketed by whether they fall on the post-rollover
H4 bar (expected microstructure) or elsewhere.

Exit codes:
  0  every pair acceptable for diagnostics / parity
  1  the store is missing, or a pair is not acceptable

Usage:
    python scripts/audit_h4_data_quality.py \\
        [--db data/oanda_h4_research.sqlite3] \\
        [--out docs/research/OANDA_H4_DATA_QUALITY_AUDIT.md]

See docs/research/OANDA_PRACTICE_READONLY_001_PLAN.md.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.backtesting.audit import (
    AuditReport,
    GapClassification,
    audit_instrument,
    classify_gaps,
)
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo

PAIRS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF"]
DEFAULT_DB = ROOT / "data" / "oanda_h4_research.sqlite3"
DEFAULT_OUT = ROOT / "docs" / "research" / "OANDA_H4_DATA_QUALITY_AUDIT.md"

# H4 bars whose CLOSE coincides with the 17:00 New York daily rollover.
# audit_instrument measures the close spread (ask_c - bid_c); the bar that
# closes at the rollover starts at 17:00 UTC under EDT / 18:00 UTC under EST.
ROLLOVER_BAR_HOURS = {17, 18}
# A six-year H4 series of a major pair is ~9,900+ completed candles.
MIN_EXPECTED_CANDLES = 9000


def pip_size_for(pair: str) -> Decimal:
    """Pip size from the Phase 3 verified metadata: JPY majors -2, others -4."""
    return Decimal("0.01") if "JPY" in pair.split("_") else Decimal("0.0001")


@dataclass
class PairAudit:
    pair: str
    report: AuditReport
    gaps: GapClassification
    abnormal_rollover: int
    abnormal_other: int
    blockers: list[str]

    @property
    def acceptable(self) -> bool:
        return not self.blockers


def audit_pair(
    repo: CandleRepo, pair: str, *, min_candles: int = MIN_EXPECTED_CANDLES
) -> PairAudit:
    """Audit one pair's H4 data and judge it for diagnostic/parity use."""
    report = audit_instrument(repo, pair, "H4", pip_size=pip_size_for(pair))
    gaps = classify_gaps(report)

    abnormal_rollover = sum(
        1 for ts, _ in report.abnormal_spreads if ts.hour in ROLLOVER_BAR_HOURS
    )
    abnormal_other = len(report.abnormal_spreads) - abnormal_rollover

    # Blockers disqualify the pair for diagnostics. Weekend / holiday
    # gaps are expected and never block; outage-like / suspicious-short
    # gaps are reported as caveats, not blockers, for a *diagnostic*.
    blockers: list[str] = []
    if report.candle_count < min_candles:
        blockers.append(
            f"only {report.candle_count} candles (< {min_candles})"
        )
    if report.incomplete_count > 0:
        blockers.append(f"{report.incomplete_count} incomplete candles")
    if report.bid_available_count != report.candle_count:
        blockers.append("bid not available on every candle")
    if report.ask_available_count != report.candle_count:
        blockers.append("ask not available on every candle")
    if report.duplicate_timestamps:
        blockers.append(f"{len(report.duplicate_timestamps)} duplicate timestamps")

    return PairAudit(
        pair=pair,
        report=report,
        gaps=gaps,
        abnormal_rollover=abnormal_rollover,
        abnormal_other=abnormal_other,
        blockers=blockers,
    )


def audit_store(
    db: Database, pairs: list[str], *, min_candles: int = MIN_EXPECTED_CANDLES
) -> list[PairAudit]:
    repo = CandleRepo(db)
    return [audit_pair(repo, pair, min_candles=min_candles) for pair in pairs]


# --------------------------------------------------------------------------
# Report rendering
# --------------------------------------------------------------------------


def _spread(value: float | None) -> str:
    return f"{value:.2f}" if value is not None else "n/a"


def render_doc(
    audits: list[PairAudit], *, generated_at: datetime, db_display: str
) -> str:
    all_ok = all(a.acceptable for a in audits)
    lines: list[str] = [
        "# OANDA H4 Data Quality Audit — `oanda-practice-readonly-001` Phase 5",
        "",
        f"**Generated:** {generated_at.isoformat()} · "
        f"**Branch:** `oanda-practice-readonly-001`",
        f"**Store:** `{db_display}` · "
        f"**Overall:** **{'PASS' if all_ok else 'REVIEW'}**",
        "",
        "> Read-only audit of the local H4 research store. **No OANDA call, "
        "no credentials.** Diagnostic only — `strategy_evidence: false`; "
        "approves no strategy and produces no trading verdict.",
        "",
        "## Summary",
        "",
        "| instrument | candles | incomplete | dups | weekend | holiday | "
        "outage | suspicious | median spr | p95 spr | abnormal | acceptable |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for a in audits:
        r, g = a.report, a.gaps
        lines.append(
            f"| {a.pair} | {r.candle_count} | {r.incomplete_count} | "
            f"{len(r.duplicate_timestamps)} | {len(g.weekend)} | "
            f"{len(g.year_end_holiday)} | {len(g.outage_like)} | "
            f"{len(g.suspicious_short)} | {_spread(r.median_spread_pips)} | "
            f"{_spread(r.p95_spread_pips)} | {len(r.abnormal_spreads)} | "
            f"{'yes' if a.acceptable else 'NO'} |"
        )

    lines += [
        "",
        "## Gap & anomaly classification",
        "",
        "Every gap and spread anomaly is sorted into one of five "
        "categories — the first two are expected market behaviour, the "
        "last three warrant a look:",
        "",
        "1. **Expected weekend gaps** — the Friday-close → Sunday-open "
        "closure (a gap spanning Saturday, ≥ 24h). Normal; not a defect.",
        "2. **Expected holiday closures** — gaps overlapping the "
        "Dec 24 – Jan 2 thin-liquidity window. Normal for FX.",
        "3. **Broker / data outage-like gaps** — a multi-bar (> 2 H4 "
        "bars) non-weekend, non-holiday gap. Concerning — review.",
        "4. **Suspicious short missing bars** — a 1-2 bar non-weekend, "
        "non-holiday gap. Usually thin mid-week liquidity; noted.",
        "5. **Spread spikes / rollover events** — abnormal spreads "
        "(> 5× median close spread). FX spreads widen at the daily "
        "rollover, the Sunday open, and around news; the per-pair "
        "breakdown buckets them by whether they fall on the H4 bar that "
        f"closes at the 17:00 NY rollover (start hour "
        f"{sorted(ROLLOVER_BAR_HOURS)} UTC). These are expected "
        "microstructure, not data corruption.",
        "",
    ]

    for a in audits:
        r, g = a.report, a.gaps
        lines += [
            f"## {a.pair}",
            "",
            f"- First / last timestamp: `{r.first_ts}` → `{r.last_ts}`",
            f"- Candle count: **{r.candle_count}** "
            f"(complete {r.completed_count}, incomplete {r.incomplete_count})",
            f"- Duplicate timestamps: **{len(r.duplicate_timestamps)}**",
            f"- Bid / ask availability: "
            f"**{r.bid_available_count} / {r.ask_available_count}** "
            f"of {r.candle_count}",
            f"- Missing intervals (non-weekend, raw): "
            f"**{len(r.missing_intervals)}**",
            "- Gap classification:",
            f"    - expected weekend gaps: **{len(g.weekend)}**",
            f"    - expected holiday closures: **{len(g.year_end_holiday)}**",
            f"    - broker/data outage-like gaps: **{len(g.outage_like)}**",
            f"    - suspicious short missing bars: **{len(g.suspicious_short)}**",
            f"- Median spread: **{_spread(r.median_spread_pips)}** pips · "
            f"p95 spread: **{_spread(r.p95_spread_pips)}** pips",
            f"- Abnormal spreads (> 5× median): **{len(r.abnormal_spreads)}** "
            f"({a.abnormal_rollover} on the rollover-close H4 bar, "
            f"{a.abnormal_other} elsewhere)",
        ]
        if g.outage_like:
            lines.append("- Outage-like gaps (sample):")
            for start, end, bars in g.outage_like[:8]:
                lines.append(
                    f"    - `{start.isoformat()}` → `{end.isoformat()}` "
                    f"({bars} bars)"
                )
        if g.suspicious_short:
            lines.append("- Suspicious short gaps (sample):")
            for start, end, bars in g.suspicious_short[:8]:
                lines.append(
                    f"    - `{start.isoformat()}` → `{end.isoformat()}` "
                    f"({bars} bars)"
                )
        verdict = (
            "acceptable for diagnostics / parity"
            if a.acceptable
            else "**NOT acceptable** — " + "; ".join(a.blockers)
        )
        lines += [
            f"- **Acceptable for diagnostics / parity:** {verdict}",
            "",
        ]

    concerning = sum(a.gaps.concerning_count for a in audits)
    lines += [
        "## Verdict",
        "",
        f"- {'All' if all_ok else 'Not all'} {len(audits)} pairs are "
        "structurally acceptable for diagnostics / parity: completed "
        "candles only, full bid/ask coverage, no duplicate timestamps, "
        "and a full ~6-year H4 history.",
        f"- {concerning} concerning gap(s) (outage-like + suspicious-short) "
        "across all pairs are classified above. For a **diagnostic**, "
        "classified gaps are handled by D1 aggregation and do not block "
        "the run; they would warrant scrutiny before any strategy verdict "
        "(which this sprint does not produce).",
        "- Weekend and year-end-holiday gaps are expected market closures "
        "and are not defects.",
        "",
        "## Safety statement",
        "",
        "- Read-only audit of the local store; no OANDA call, no "
        "credentials read or written.",
        "- Diagnostic only — `strategy_evidence: false`. Approves no "
        "strategy and produces no trading recommendation.",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Audit the local OANDA H4 research store for data quality."
    )
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args(argv)

    db_path = Path(args.db)
    try:
        db_display = str(db_path.resolve().relative_to(ROOT))
    except ValueError:
        db_display = str(db_path)
    if not db_path.exists():
        print(
            f"BLOCKER: no H4 store at {db_display}. Run "
            "scripts/rehydrate_oanda_h4_store.py first (Phase 4).",
            file=sys.stderr,
        )
        return 1

    audits = audit_store(Database(db_path), PAIRS)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        render_doc(audits, generated_at=datetime.now(UTC), db_display=db_display),
        encoding="utf-8",
    )
    try:
        out_display = str(out_path.resolve().relative_to(ROOT))
    except ValueError:
        out_display = str(out_path)
    ok = sum(1 for a in audits if a.acceptable)
    print(
        f"H4 data quality audit: {ok}/{len(audits)} pairs acceptable "
        f"— report written to {out_display}"
    )
    return 0 if ok == len(audits) else 1


if __name__ == "__main__":
    raise SystemExit(main())

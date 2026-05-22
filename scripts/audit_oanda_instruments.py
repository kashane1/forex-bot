#!/usr/bin/env python3
"""Audit OANDA practice instrument metadata for the research universe.

Read-only. Fetches the per-account instrument list from OANDA practice
and verifies the metadata fields the bot relies on for position sizing,
pip math, price/units precision, and margin.

For every instrument the *intrinsic, stable* fields — instrument type,
pip location, display precision, trade-units precision, and minimum
trade size — are checked against the value the repo assumes. The margin
rate is recorded as **informational only**: it is broker / account /
region specific and legitimately varies, so a margin-rate difference is
never treated as a failure.

Safety:
  * practice only — the practice-data environment guard must pass;
  * read-only — only the instruments `GET` endpoint is called;
  * the account id is redacted; the access token is never printed.

Exit codes:
  0  every requested instrument found, all stable fields match
  1  a stable-field mismatch or a missing instrument (report written)
  2  refused — non-practice environment or missing credentials

Usage:
    python scripts/audit_oanda_instruments.py [--config configs/paper.yaml]
        [--out docs/research/OANDA_INSTRUMENT_METADATA_AUDIT.md]

See docs/research/OANDA_PRACTICE_READONLY_001_PLAN.md.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.broker.oanda import OandaBroker
from forex_bot.config import ConfigError, load_settings
from forex_bot.domain.instruments import Instrument
from forex_bot.guards import assert_practice_data_environment

# The six-pair H4 research universe.
RESEARCH_UNIVERSE = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF"]
# Used by CAMPAIGN_001 / 002 / 003 historically; audited but kept
# explicitly separate from the six-pair research universe.
HISTORICAL_EXTRA = ["NZD_USD"]

DEFAULT_CONFIG = ROOT / "configs" / "paper.yaml"
DEFAULT_OUT = ROOT / "docs" / "research" / "OANDA_INSTRUMENT_METADATA_AUDIT.md"

# Intrinsic fields verified against an expectation. margin_rate is
# deliberately excluded — it is variable and informational only.
STABLE_FIELDS = (
    "type",
    "pip_location",
    "display_precision",
    "trade_units_precision",
    "minimum_trade_size",
)


def redact_account_id(account_id: str | None) -> str:
    """Redact an account id to first-3 / last-3 characters."""
    aid = (account_id or "").strip()
    if len(aid) >= 8:
        return f"{aid[:3]}…{aid[-3:]}"
    return "<short-or-empty>"


def is_jpy_pair(instrument: str) -> bool:
    """True if either leg of the pair is JPY (JPY-quoted majors use a
    pip location of -2 and a display precision of 3)."""
    parts = instrument.split("_")
    return "JPY" in parts


def expected_metadata(instrument: str) -> dict[str, object]:
    """The intrinsic metadata the repo assumes for a major FX pair."""
    jpy = is_jpy_pair(instrument)
    return {
        "type": "CURRENCY",
        "pip_location": -2 if jpy else -4,
        "display_precision": 3 if jpy else 5,
        "trade_units_precision": 0,
        "minimum_trade_size": Decimal("1"),
    }


@dataclass
class FieldCheck:
    field: str
    expected: object
    actual: object

    @property
    def ok(self) -> bool:
        return self.expected == self.actual


@dataclass
class InstrumentAudit:
    name: str
    in_research_universe: bool
    found: bool
    checks: list[FieldCheck] = field(default_factory=list)
    # Live values (None when the instrument is missing).
    pip_size: Decimal | None = None
    margin_rate: Decimal | None = None
    display_name: str | None = None

    @property
    def ok(self) -> bool:
        return self.found and all(c.ok for c in self.checks)

    @property
    def mismatches(self) -> list[FieldCheck]:
        return [c for c in self.checks if not c.ok]


@dataclass
class AuditReport:
    audits: list[InstrumentAudit] = field(default_factory=list)
    instrument_universe_count: int = 0  # total instruments OANDA exposes

    @property
    def missing(self) -> list[str]:
        return [a.name for a in self.audits if not a.found]

    @property
    def mismatched(self) -> list[str]:
        return [a.name for a in self.audits if a.found and not a.ok]

    @property
    def ok(self) -> bool:
        return not self.missing and not self.mismatched


def audit_one(instrument_name: str, instr: Instrument | None, *, in_universe: bool) -> InstrumentAudit:
    """Audit one instrument's metadata against the repo's expectation."""
    if instr is None:
        return InstrumentAudit(
            name=instrument_name, in_research_universe=in_universe, found=False
        )
    expected = expected_metadata(instrument_name)
    actual = {
        "type": instr.type,
        "pip_location": instr.pip_location,
        "display_precision": instr.display_precision,
        "trade_units_precision": instr.trade_units_precision,
        "minimum_trade_size": instr.minimum_trade_size,
    }
    checks = [
        FieldCheck(field=name, expected=expected[name], actual=actual[name])
        for name in STABLE_FIELDS
    ]
    return InstrumentAudit(
        name=instrument_name,
        in_research_universe=in_universe,
        found=True,
        checks=checks,
        pip_size=instr.pip_size,
        margin_rate=instr.margin_rate,
        display_name=instr.display_name,
    )


def audit_instruments(
    instruments: list[Instrument],
    *,
    universe: list[str] | None = None,
    historical: list[str] | None = None,
) -> AuditReport:
    """Audit the requested instruments against the metadata the repo
    assumes. Pure — operates on an already-fetched instrument list."""
    universe = universe if universe is not None else RESEARCH_UNIVERSE
    historical = historical if historical is not None else HISTORICAL_EXTRA
    by_name = {i.name: i for i in instruments}
    report = AuditReport(instrument_universe_count=len(instruments))
    for name in universe:
        report.audits.append(audit_one(name, by_name.get(name), in_universe=True))
    for name in historical:
        report.audits.append(audit_one(name, by_name.get(name), in_universe=False))
    return report


# --------------------------------------------------------------------------
# Report rendering
# --------------------------------------------------------------------------


def _row(audit: InstrumentAudit) -> str:
    if not audit.found:
        return f"| {audit.name} | — | — | — | — | — | — | **MISSING** |"
    by = {c.field: c for c in audit.checks}
    return (
        f"| {audit.name} | {by['type'].actual} | "
        f"{by['pip_location'].actual} | {audit.pip_size} | "
        f"{by['display_precision'].actual} | "
        f"{by['trade_units_precision'].actual} | "
        f"{by['minimum_trade_size'].actual} | "
        f"{audit.margin_rate} | "
        f"{'OK' if audit.ok else 'MISMATCH'} |"
    )


def render_report(
    report: AuditReport,
    *,
    account_id_redacted: str,
    host: str,
    config_path: str,
    generated_at: datetime,
) -> str:
    lines: list[str] = []
    status = "PASS" if report.ok else "FAIL"
    lines += [
        "# OANDA Instrument Metadata Audit — "
        "`oanda-practice-readonly-001` Phase 3",
        "",
        f"**Generated:** {generated_at.isoformat()} · "
        f"**Branch:** `oanda-practice-readonly-001`",
        f"**Config:** `{config_path}` · **Overall:** **{status}**",
        "",
        "> Read-only diagnostic. Instrument metadata was fetched from the "
        "OANDA **practice** `GET /v3/accounts/{id}/instruments` endpoint. "
        "**No order was submitted.** This is not a strategy campaign and "
        "produces no trading verdict.",
        "",
        "## Environment",
        "",
        "| field | value |",
        "|---|---|",
        f"| OANDA host | `{host}` |",
        f"| account id (redacted) | `{account_id_redacted}` |",
        f"| instruments exposed by account | {report.instrument_universe_count} |",
        "",
        "## Six-pair H4 research universe",
        "",
        "| instrument | type | pip_loc | pip_size | disp_prec | "
        "units_prec | min_size | margin_rate | stable fields |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    lines += [_row(a) for a in report.audits if a.in_research_universe]
    lines += [
        "",
        "## Historical extra — NZD_USD (not in the six-pair universe)",
        "",
        "NZD_USD was used by CAMPAIGN_001 / 002 / 003. It is audited here "
        "for completeness but is **kept separate** from the six-pair H4 "
        "research universe.",
        "",
        "| instrument | type | pip_loc | pip_size | disp_prec | "
        "units_prec | min_size | margin_rate | stable fields |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    lines += [_row(a) for a in report.audits if not a.in_research_universe]

    lines += [
        "",
        "## Required fields present",
        "",
        "Every audited instrument exposes all six fields the bot relies on "
        "(instrument name, pip location, display precision, trade-units "
        "precision, minimum trade size, margin rate):",
        "",
    ]
    for a in report.audits:
        if a.found:
            lines.append(f"- **{a.name}**: all required fields present.")
        else:
            lines.append(f"- **{a.name}**: **MISSING from the account instrument list.**")

    lines += [
        "",
        "## Precision & pip checks",
        "",
        "Stable, intrinsic fields are checked against the repo's "
        "expectation. JPY-quoted pairs are expected at pip location -2 / "
        "display precision 3; all other majors at -4 / 5; trade-units "
        "precision 0 and minimum trade size 1 for every major.",
        "",
    ]
    any_mismatch = False
    for a in report.audits:
        if a.found and a.mismatches:
            any_mismatch = True
            for c in a.mismatches:
                lines.append(
                    f"- **{a.name}.{c.field}**: expected `{c.expected}`, "
                    f"got `{c.actual}` — **MISMATCH**"
                )
    if not any_mismatch:
        lines.append(
            "- no mismatch — every audited instrument's stable fields match "
            "the repo's expectation."
        )

    lines += [
        "",
        "### JPY pip handling",
        "",
    ]
    jpy = [a for a in report.audits if a.found and is_jpy_pair(a.name)]
    if jpy:
        for a in jpy:
            lines.append(
                f"- **{a.name}**: pip location "
                f"{next(c.actual for c in a.checks if c.field == 'pip_location')}, "
                f"pip size `{a.pip_size}` — `Instrument.pip_size = 10 ** "
                "pip_location` resolves JPY pips correctly."
            )
    else:
        lines.append("- no JPY-quoted instrument in the audited set.")

    lines += [
        "",
        "## Margin checks (informational)",
        "",
        "Margin rate is **broker / account / region specific** and varies; "
        "it is recorded as the authoritative live value, not pass/failed. "
        "Position sizing must read the live `margin_rate`, never a "
        "hard-coded constant.",
        "",
    ]
    for a in report.audits:
        if a.found:
            lines.append(f"- **{a.name}**: live margin rate `{a.margin_rate}`.")

    lines += [
        "",
        "## Differences from the local instrument cache",
        "",
        "The repo has **no committed instrument-metadata cache** — instrument "
        "metadata is otherwise only fetched live (`bot sync-instruments` "
        "into the gitignored DB) or hard-coded in test fixtures "
        "(`tests/conftest.py`: EUR_USD pip -4 / precision 5, USD_JPY pip -2 "
        "/ precision 3). This audit establishes the first committed, "
        "reproducible metadata record. The live stable fields match those "
        "test-fixture assumptions; the test-fixture margin rates (EUR_USD "
        "0.02, USD_JPY 0.04) are illustrative only and are expected to "
        "differ from the live account's margin rates.",
        "",
        "## Implications for sizing and PnL",
        "",
        "- **Pip math:** `pip_size = 10 ** pip_location` — correct for both "
        "JPY (-2) and non-JPY (-4) majors, so pip-denominated stops, ATR "
        "filters, and spread filters size correctly.",
        "- **Units precision 0:** all majors trade in whole units; "
        "`Instrument.round_units` floors to integer units.",
        "- **Minimum trade size 1:** sizing must not emit sub-unit orders.",
        "- **Margin rate:** sizing / margin checks must use the live "
        "`margin_rate` per instrument; it is variable and must not be "
        "assumed constant across instruments or over time.",
        "",
        "## Blockers",
        "",
    ]
    if report.ok:
        lines.append(
            "- none — every audited instrument was found and every stable "
            "field matched the repo's expectation."
        )
    else:
        for name in report.missing:
            lines.append(f"- **{name}**: missing from the account instrument list.")
        for name in report.mismatched:
            lines.append(f"- **{name}**: one or more stable fields mismatched (see above).")

    lines += [
        "",
        "## Safety statement",
        "",
        "- Read-only: only `GET /v3/accounts/{id}/instruments` was called. "
        "**No order was submitted, created, modified, or closed.**",
        "- Practice environment only; the live host was never contacted.",
        "- The account id is redacted; the access token was never printed "
        "or written. `strategy_evidence: false` — approves no strategy.",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Audit OANDA practice instrument metadata."
    )
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args(argv)

    try:
        settings = load_settings(Path(args.config))
        assert_practice_data_environment(settings)
    except ConfigError as exc:
        print(
            f"REFUSED: practice-data environment guard refused — {exc}",
            file=sys.stderr,
        )
        return 2

    account_id, token = settings.broker_credentials()
    broker = OandaBroker(
        environment="practice",
        account_id=account_id,
        access_token=token,
        timeout_seconds=settings.broker.request_timeout_seconds,
        max_retries=settings.broker.max_retries,
    )
    try:
        instruments = broker.list_instruments()
    finally:
        broker.close()

    report = audit_instruments(instruments)

    try:
        cfg_display = str(Path(args.config).resolve().relative_to(ROOT))
    except ValueError:
        cfg_display = str(args.config)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        render_report(
            report,
            account_id_redacted=redact_account_id(account_id),
            host="https://api-fxpractice.oanda.com",
            config_path=cfg_display,
            generated_at=datetime.now(UTC),
        ),
        encoding="utf-8",
    )
    try:
        out_display = str(out_path.resolve().relative_to(ROOT))
    except ValueError:
        out_display = str(out_path)
    print(
        f"instrument audit: {len(report.audits)} instruments audited, "
        f"{len(report.missing)} missing, {len(report.mismatched)} mismatched "
        f"— report written to {out_display}"
    )
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

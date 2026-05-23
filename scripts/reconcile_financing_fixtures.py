#!/usr/bin/env python3
"""Reconcile an observed-financing fixture against the financing
calculator's prediction for the same window.

Inputs are two local JSON fixtures: an ``observed_financing_events``
file and a ``financing_rates`` file (schemas in
docs/research/FINANCING_OBSERVED_FIXTURE_SCHEMA.md). The script
loads both via research/financing/fixtures, runs
research/financing/calculator.calculate_run for the implied
window, and writes a deterministic per-row diff report
(reconciliation.json + reconciliation.md) under --output.

The script is intentionally self-contained:

- no imports from ``forex_bot``;
- no network / broker / OANDA calls;
- no ``.env`` reads;
- no credential value printed;
- no SQLite write;
- writes exactly two small files under the explicit --output dir.

A run exits with 0 only when every shared (date_utc, instrument)
row is a ``match`` within tolerance and no schema violation
occurred. Mismatches exit non-zero (see §12 of the protocol).

The CLI's outputs carry ``strategy_evidence: false``,
``financing_in_engine_pnl: false``, and
``financing_is_live_blocker: true``. ``financing_treatment``
mirrors the rate source's treatment (``ESTIMATED`` for both
v1 sources); ``MODELED`` is refused — defense-in-depth at
several layers.

See docs/research/FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# isort: off
from research.financing.calculator import (
    MissingFinancingRateError,
    calculate_run,
)
from research.financing.fixtures import (
    FixtureValidationError,
    ObservedEventDict,
    load_observed_event_fixture,
    load_rate_fixture,
)
from research.financing.models import (
    FinancingCalculatorConfig,
    FinancingTreatment,
    MissingRatePolicy,
    PositionInterval,
)
# isort: on

TOOL_NAME = "reconcile_financing_fixtures"
TOOL_VERSION = "1"

EXIT_OK = 0
EXIT_MISMATCH = 2
EXIT_SCHEMA = 3
EXIT_IO = 4
EXIT_MISSING_RATE_ERROR = 5
EXIT_RUNTIME = 6


def _default_output_dir() -> str:
    """A /tmp path — gitignored by the OS — chosen so a default
    invocation can never write bulky files into the repo."""
    return "/tmp/financing_reconcile_default"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reconcile an observed-financing fixture against the "
            "financing calculator. Diagnostic only — never produces "
            "MODELED financing, never reads broker data."
        )
    )
    parser.add_argument(
        "--observed",
        required=True,
        type=Path,
        help="Path to an observed_financing_events fixture file.",
    )
    parser.add_argument(
        "--rates",
        required=True,
        type=Path,
        help="Path to a financing_rates fixture file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(_default_output_dir()),
        help=(
            "Output directory. Defaults to a /tmp path so a default-arg "
            "run cannot write bulky files into the repo."
        ),
    )
    parser.add_argument(
        "--units",
        default="10000",
        help="Position units (stringified Decimal). Default 10000.",
    )
    parser.add_argument(
        "--entry-price",
        default="1.0800",
        help="Position entry price (stringified Decimal). Default 1.0800.",
    )
    parser.add_argument(
        "--side",
        choices=("long", "short"),
        default="long",
        help="Position side. Default long.",
    )
    parser.add_argument(
        "--missing-rate-policy",
        choices=tuple(p.value for p in MissingRatePolicy),
        default=MissingRatePolicy.CONSERVATIVE.value,
        help="Calculator missing-rate policy. Default conservative.",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-9,
        help=(
            "Absolute per-row tolerance in home-currency units. "
            "Default 1e-9 (synthetic-fixture grade)."
        ),
    )
    parser.add_argument(
        "--generated-at-utc",
        default=None,
        help=(
            "Injectable clock value for deterministic tests "
            "(ISO-8601). Defaults to datetime.now(UTC)."
        ),
    )
    return parser.parse_args(argv)


def _parse_now(value: str | None) -> datetime:
    if value is None:
        return datetime.now(UTC).replace(microsecond=0)
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise FixtureValidationError(
            "--generated-at-utc must be a timezone-aware ISO-8601 string"
        )
    return dt


def _infer_window(events: list[ObservedEventDict]) -> tuple[datetime, datetime]:
    """Open = earliest event - 13 hours (so the rollover at
    21:00 UTC is strictly inside the window); close = latest
    event + 1 hour (same logic, on the other side).

    Strict-inequality calculator semantics require the rollover
    moment to fall *strictly inside* (open_time, close_time);
    the offsets ensure that without making the caller deal with
    the inclusion math."""
    open_t = min(e["time"] for e in events) - timedelta(hours=13)
    close_t = max(e["time"] for e in events) + timedelta(hours=1)
    return open_t, close_t


def _instruments(events: list[ObservedEventDict]) -> list[str]:
    """Unique instrument names in the observed file, sorted."""
    return sorted({e["instrument"] for e in events if e["instrument"]})


def _classification_for(
    observed: Decimal | None,
    calculated: float | None,
    tolerance: float,
) -> tuple[str, float | None]:
    """Returns (classification, diff) for one (date, instrument) row."""
    if observed is not None and calculated is not None:
        diff = float(observed) - calculated
        return ("match" if abs(diff) <= tolerance else "mismatch", diff)
    if observed is None and calculated is not None:
        return ("missing_in_observed", None)
    if observed is not None and calculated is None:
        return ("missing_in_calculated", None)
    # Both None — impossible by construction (we only iterate rows
    # that exist somewhere). Treated as a runtime error.
    raise RuntimeError(
        "_classification_for called with both sides None — bug"
    )


def _fmt_decimal_or_none(value: Decimal | None) -> str | None:
    return None if value is None else str(value)


def _build_report(
    *,
    observed: list[ObservedEventDict],
    rate_source_name: str,
    rate_source_treatment: FinancingTreatment,
    inputs_block: dict,
    window_open: datetime,
    window_close: datetime,
    home_currency: str,
    calc_events_by_key: dict[tuple[date, str], dict],
    tolerance: float,
    generated_at_utc: datetime,
) -> dict:
    """Build the report dict from observed events + calculator
    output. Pure construction; no I/O."""

    if rate_source_treatment == FinancingTreatment.MODELED:
        # Defense-in-depth — the calculator already refuses this.
        raise RuntimeError(
            "rate_source_treatment is MODELED — refused by the "
            "reconciliation tool"
        )

    observed_by_key: dict[tuple[date, str], list[ObservedEventDict]] = {}
    for ev in observed:
        if ev["instrument"] is None:
            # Account-level events have no instrument; the reconciliation
            # tool requires a per-instrument breakdown to be useful.
            # Surface them as missing_in_calculated rows under a synthetic
            # ("", date) key so they appear in the output.
            key = (ev["time"].astimezone(UTC).date(), "")
        else:
            key = (ev["time"].astimezone(UTC).date(), ev["instrument"])
        observed_by_key.setdefault(key, []).append(ev)

    all_keys = sorted(set(observed_by_key) | set(calc_events_by_key))

    rows = []
    counts = {
        "match": 0,
        "mismatch": 0,
        "missing_in_observed": 0,
        "missing_in_calculated": 0,
    }
    rate_was_missing_count = 0

    for key in all_keys:
        d, instrument = key
        obs_rows = observed_by_key.get(key, [])
        # Sum financing across all observed rows for this (date,
        # instrument) — broker DAILY_FINANCING may break down by
        # trade.
        observed_financing: Decimal | None = (
            sum((r["financing"] for r in obs_rows), start=Decimal("0"))
            if obs_rows
            else None
        )

        calc = calc_events_by_key.get(key)
        calculated_cashflow_home: float | None = (
            calc["cashflow_home"] if calc is not None else None
        )

        classification, diff = _classification_for(
            observed_financing, calculated_cashflow_home, tolerance,
        )
        counts[classification] += 1
        if calc is not None and calc.get("rate_was_missing"):
            rate_was_missing_count += 1

        rows.append({
            "date_utc": d.isoformat(),
            "instrument": instrument,
            "weekday": d.weekday() if d is not None else None,
            "classification": classification,
            "observed_financing": _fmt_decimal_or_none(observed_financing),
            "calculated_cashflow_home": calculated_cashflow_home,
            "diff": diff,
            "tolerance": tolerance,
            "rate_was_missing": bool(calc and calc.get("rate_was_missing")),
            "notes": list(calc["notes"]) if calc is not None else [],
        })

    summary = {
        "row_count": len(rows),
        **counts,
        "rate_was_missing_count": rate_was_missing_count,
    }

    report = {
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "strategy_evidence": False,
        "financing_in_engine_pnl": False,
        "financing_is_live_blocker": True,
        "financing_treatment": rate_source_treatment.value,
        "inputs": inputs_block,
        "window": {
            "open_time": window_open.isoformat(),
            "close_time": window_close.isoformat(),
            "home_currency": home_currency,
        },
        "summary": summary,
        "rows": rows,
        "generated_at_utc": generated_at_utc.isoformat(),
    }

    # Defense-in-depth — never let MODELED escape.
    if report["financing_treatment"] == FinancingTreatment.MODELED.value:
        raise RuntimeError("financing_treatment must not be modeled")
    if report["strategy_evidence"] is not False:
        raise RuntimeError("strategy_evidence must be False")
    if report["financing_in_engine_pnl"] is not False:
        raise RuntimeError("financing_in_engine_pnl must be False")
    if report["financing_is_live_blocker"] is not True:
        raise RuntimeError("financing_is_live_blocker must be True")

    return report


def _dump_json(report: dict) -> str:
    return json.dumps(
        report,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    )


def _fmt(value: float | None, decimals: int = 6) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{decimals}f}"


def _fmt_tol(value: float) -> str:
    return f"{value:.1e}"


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append("# Financing Reconciliation")
    lines.append("")
    lines.append(
        f"`strategy_evidence: {str(report['strategy_evidence']).lower()}` · "
        f"`financing_treatment: {report['financing_treatment']}` · "
        f"`financing_in_engine_pnl: "
        f"{str(report['financing_in_engine_pnl']).lower()}` · "
        f"`financing_is_live_blocker: "
        f"{str(report['financing_is_live_blocker']).lower()}`"
    )
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    inputs = report["inputs"]
    for key in (
        "observed_path",
        "rates_path",
        "rate_source_name",
        "units",
        "entry_price",
        "side",
        "missing_rate_policy",
        "tolerance",
    ):
        value = inputs.get(key)
        if isinstance(value, float):
            value = _fmt_tol(value) if key == "tolerance" else str(value)
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Window")
    lines.append("")
    for key in ("open_time", "close_time", "home_currency"):
        lines.append(f"- {key}: `{report['window'][key]}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    summary = report["summary"]
    for key in (
        "row_count",
        "match",
        "mismatch",
        "missing_in_observed",
        "missing_in_calculated",
        "rate_was_missing_count",
    ):
        lines.append(f"- {key}: {summary[key]}")
    lines.append("")
    lines.append("## Rows")
    lines.append("")
    if not report["rows"]:
        lines.append("_no rows_")
        lines.append("")
    else:
        lines.append(
            "| date_utc | instrument | weekday | classification "
            "| observed | calculated | diff | tol |"
        )
        lines.append("|---|---|---:|---|---:|---:|---:|---:|")
        for row in report["rows"]:
            observed_display = (
                "n/a" if row["observed_financing"] is None
                else _fmt(float(row["observed_financing"]), 6)
            )
            calculated_display = _fmt(row["calculated_cashflow_home"], 6)
            diff_display = _fmt(row["diff"], 6) if row["diff"] is not None else "n/a"
            lines.append(
                f"| {row['date_utc']} "
                f"| {row['instrument'] or 'n/a'} "
                f"| {row['weekday']} "
                f"| {row['classification']} "
                f"| {observed_display} "
                f"| {calculated_display} "
                f"| {diff_display} "
                f"| {_fmt_tol(row['tolerance'])} |"
            )
    lines.append("")
    lines.append(f"_generated_at_utc: `{report['generated_at_utc']}`_")
    return "\n".join(lines).rstrip() + "\n"


def _calc_events_by_key(report) -> dict[tuple[date, str], dict]:
    out: dict[tuple[date, str], dict] = {}
    for pos in report.positions:
        for ev in pos.events:
            key = (ev.date_utc, ev.instrument)
            # Multiple positions on the same (date, instrument) is
            # nonsensical for this CLI's one-synthetic-position
            # mode, but guard against it: aggregate cashflows.
            existing = out.get(key)
            if existing is None:
                out[key] = {
                    "cashflow_home": ev.cashflow_home,
                    "rate_was_missing": ev.rate_was_missing,
                    "notes": list(ev.notes),
                }
            else:
                existing["cashflow_home"] += ev.cashflow_home
                existing["rate_was_missing"] = (
                    existing["rate_was_missing"] or ev.rate_was_missing
                )
                existing["notes"].extend(ev.notes)
    return out


def run(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        events = load_observed_event_fixture(args.observed)
        rate_source, missing_dates = load_rate_fixture(args.rates)
    except FixtureValidationError as exc:
        print(f"[reconcile_financing_fixtures] schema error: {exc}", file=sys.stderr)
        return EXIT_SCHEMA

    if rate_source.treatment == FinancingTreatment.MODELED:
        print(
            "[reconcile_financing_fixtures] rate source declared MODELED — refused",
            file=sys.stderr,
        )
        return EXIT_RUNTIME

    if not events:
        # Zero-event observation. The script still emits an output;
        # the calculator runs against an empty position set so it
        # produces zero events too. The result: empty rows, summary
        # all zero, exit OK.
        instruments_present: list[str] = []
        window_open = datetime.now(UTC).replace(microsecond=0)
        window_close = window_open
        positions: list[PositionInterval] = []
    else:
        instruments_present = _instruments(events)
        window_open, window_close = _infer_window(events)
        try:
            positions = [
                PositionInterval(
                    position_id=f"reconcile-{instrument}",
                    instrument=instrument,
                    side=args.side,
                    units=Decimal(args.units),
                    entry_price=Decimal(args.entry_price),
                    open_time=window_open,
                    close_time=window_close,
                )
                for instrument in instruments_present
            ]
        except Exception as exc:
            print(
                f"[reconcile_financing_fixtures] could not build "
                f"PositionInterval: {exc}",
                file=sys.stderr,
            )
            return EXIT_RUNTIME

    try:
        now = _parse_now(args.generated_at_utc)
    except FixtureValidationError as exc:
        print(f"[reconcile_financing_fixtures] {exc}", file=sys.stderr)
        return EXIT_SCHEMA

    cfg = FinancingCalculatorConfig(
        missing_rate_policy=MissingRatePolicy(args.missing_rate_policy),
    )
    try:
        calc_report = calculate_run(positions, rate_source, cfg, now=now)
    except MissingFinancingRateError as exc:
        print(
            f"[reconcile_financing_fixtures] missing-rate ERROR policy: {exc}",
            file=sys.stderr,
        )
        return EXIT_MISSING_RATE_ERROR
    except ValueError as exc:
        # calculate_run refuses a MODELED source — surface as RUNTIME
        # since the loader already refused, but keep defense-in-depth.
        print(f"[reconcile_financing_fixtures] {exc}", file=sys.stderr)
        return EXIT_RUNTIME

    inputs_block = {
        "observed_path": str(args.observed),
        "rates_path": str(args.rates),
        "units": args.units,
        "entry_price": args.entry_price,
        "side": args.side,
        "missing_rate_policy": args.missing_rate_policy,
        "tolerance": args.tolerance,
        "rate_source_name": rate_source.name,
        "rate_missing_dates": [d.isoformat() for d in missing_dates],
    }

    try:
        report = _build_report(
            observed=events,
            rate_source_name=rate_source.name,
            rate_source_treatment=rate_source.treatment,
            inputs_block=inputs_block,
            window_open=window_open,
            window_close=window_close,
            home_currency=calc_report.home_currency if events else "USD",
            calc_events_by_key=_calc_events_by_key(calc_report),
            tolerance=args.tolerance,
            generated_at_utc=now,
        )
    except RuntimeError as exc:
        print(f"[reconcile_financing_fixtures] {exc}", file=sys.stderr)
        return EXIT_RUNTIME

    try:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "reconciliation.json").write_text(
            _dump_json(report), encoding="utf-8",
        )
        (args.output / "reconciliation.md").write_text(
            _render_md(report), encoding="utf-8",
        )
    except OSError as exc:
        print(f"[reconcile_financing_fixtures] output I/O error: {exc}", file=sys.stderr)
        return EXIT_IO

    if report["summary"]["mismatch"] > 0:
        print(
            f"[reconcile_financing_fixtures] {report['summary']['mismatch']} "
            "mismatch row(s)",
            file=sys.stderr,
        )
        return EXIT_MISMATCH
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    return run(argv)


if __name__ == "__main__":  # pragma: no cover — exercised via tests via main()
    sys.exit(main())

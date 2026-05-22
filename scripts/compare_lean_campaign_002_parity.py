#!/usr/bin/env python3
"""Compare a Lean CAMPAIGN_002 H4 parity run against the bespoke reference.

Reads the no-RiskEngine bespoke reference
(`research/lean_parity/campaign_002_h4_bespoke_reference.json`) and a
Lean parity result, compares them per pair within documented tolerances,
and writes a Markdown comparison report.

Verification only — `strategy_evidence: false`. A parity FAIL localizes
a parity-implementation bug or an engine discrepancy; it never reflects
strategy quality. CAMPAIGN_002 stays REJECT regardless.

Modes:
  * with a Lean result — full per-pair comparison + PASS / WARN / FAIL;
  * `--no-lean` (or a missing Lean path) — validate the bespoke
    reference and describe the expected Lean-result shape.

Exit codes:
  0  comparison PASS (or reference-only validation OK)
  1  comparison WARN — drift inside the review band
  2  comparison FAIL — drift outside tolerance, missing pair, or
     malformed Lean output

Usage:
    python scripts/compare_lean_campaign_002_parity.py \\
        [--reference research/lean_parity/campaign_002_h4_bespoke_reference.json] \\
        [--lean PATH_TO_lean_summary.json | --no-lean] \\
        [--out docs/research/LEAN_PARITY_CAMPAIGN_002_RESULT.md]

See docs/research/LEAN_PARITY_COMPARISON_METHOD.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REFERENCE = ROOT / "research" / "lean_parity" / "campaign_002_h4_bespoke_reference.json"
DEFAULT_OUT = ROOT / "docs" / "research" / "LEAN_PARITY_CAMPAIGN_002_RESULT.md"

# Tolerance tiers — (OK threshold, WARN threshold). Beyond WARN → FAIL.
# trades: relative; expectancy_r and return_pct: absolute. From the
# mapping spec §8.
TOL = {
    "trades": (0.05, 0.15),        # ±5% OK, ±15% WARN (relative)
    "expectancy_r": (0.03, 0.10),  # ±0.03 R OK, ±0.10 WARN (absolute)
    "return_pct": (0.5, 2.0),      # ±0.5 pp OK, ±2.0 WARN (absolute)
}
_RANK = {"OK": 0, "WARN": 1, "FAIL": 2}


class MalformedLeanOutputError(ValueError):
    """Raised when a Lean parity result cannot be parsed / is incomplete."""


@dataclass
class MetricComparison:
    name: str
    reference: float
    lean: float
    status: str  # OK | WARN | FAIL

    @property
    def delta(self) -> float:
        return self.lean - self.reference


@dataclass
class PairComparison:
    instrument: str
    found: bool
    metrics: list[MetricComparison] = field(default_factory=list)

    @property
    def status(self) -> str:
        if not self.found:
            return "FAIL"
        if not self.metrics:
            return "OK"
        return max((m.status for m in self.metrics), key=lambda s: _RANK[s])


@dataclass
class ComparisonReport:
    pairs: list[PairComparison]
    total_reference: int
    total_lean: int
    total_status: str

    @property
    def status(self) -> str:
        worst = self.total_status
        for p in self.pairs:
            if _RANK[p.status] > _RANK[worst]:
                worst = p.status
        return worst


def _classify_abs(delta: float, ok: float, warn: float) -> str:
    d = abs(delta)
    if d <= ok:
        return "OK"
    if d <= warn:
        return "WARN"
    return "FAIL"


def _classify_rel(reference: float, lean: float, ok: float, warn: float) -> str:
    if reference == 0:
        return "OK" if lean == 0 else "FAIL"
    rel = abs(lean - reference) / abs(reference)
    if rel <= ok:
        return "OK"
    if rel <= warn:
        return "WARN"
    return "FAIL"


def load_reference(path: Path) -> dict:
    """Load and validate the bespoke reference JSON."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if "pairs" not in data or not isinstance(data["pairs"], list):
        raise MalformedLeanOutputError(f"reference {path} has no 'pairs' list")
    return data


def load_lean_result(path: Path) -> dict:
    """Load a Lean parity result. `path` may be the summary JSON itself
    or a directory containing `parity_summary.json`. Raises
    MalformedLeanOutputError on anything unparseable / incomplete."""
    target = path / "parity_summary.json" if path.is_dir() else path
    if not target.is_file():
        raise MalformedLeanOutputError(f"no Lean result file at {target}")
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MalformedLeanOutputError(f"{target} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("pairs"), list):
        raise MalformedLeanOutputError(f"{target}: missing a 'pairs' list")
    for entry in data["pairs"]:
        if not isinstance(entry, dict) or "instrument" not in entry or "trades" not in entry:
            raise MalformedLeanOutputError(
                f"{target}: a pair entry lacks 'instrument' / 'trades'"
            )
    return data


def compare(reference: dict, lean: dict) -> ComparisonReport:
    """Compare a Lean result against the bespoke reference, per pair."""
    lean_by_inst = {p["instrument"]: p for p in lean["pairs"]}
    pairs: list[PairComparison] = []
    for ref_pair in reference["pairs"]:
        inst = ref_pair["instrument"]
        lean_pair = lean_by_inst.get(inst)
        if lean_pair is None:
            pairs.append(PairComparison(instrument=inst, found=False))
            continue
        metrics: list[MetricComparison] = []
        # trade count — relative tolerance.
        ref_t, lean_t = float(ref_pair["trades"]), float(lean_pair["trades"])
        metrics.append(
            MetricComparison(
                "trades", ref_t, lean_t,
                _classify_rel(ref_t, lean_t, *TOL["trades"]),
            )
        )
        # expectancy_r / return_pct — absolute tolerance, compared only
        # when the Lean result carries them.
        for name in ("expectancy_r", "return_pct"):
            if name in lean_pair and name in ref_pair:
                ref_v, lean_v = float(ref_pair[name]), float(lean_pair[name])
                metrics.append(
                    MetricComparison(
                        name, ref_v, lean_v,
                        _classify_abs(lean_v - ref_v, *TOL[name]),
                    )
                )
        pairs.append(PairComparison(instrument=inst, found=True, metrics=metrics))

    total_ref = int(reference.get("total_trades", sum(p["trades"] for p in reference["pairs"])))
    total_lean = int(lean.get("total_trades", sum(p["trades"] for p in lean["pairs"])))
    total_status = _classify_rel(total_ref, total_lean, *TOL["trades"])
    return ComparisonReport(
        pairs=pairs,
        total_reference=total_ref,
        total_lean=total_lean,
        total_status=total_status,
    )


# --------------------------------------------------------------------------
# Report rendering
# --------------------------------------------------------------------------


def _banner() -> list[str]:
    return [
        "> **DIAGNOSTIC / PARITY COMPARISON — NOT A VERDICT.** This compares "
        "an independent Lean re-implementation against the bespoke engine to "
        "verify the *engine*, not a strategy. `strategy_evidence: false`. "
        "CAMPAIGN_002 is REJECT and stays REJECT; a parity FAIL localizes an "
        "implementation discrepancy and never reflects strategy quality.",
        "",
    ]


def render_no_lean(reference: dict, *, generated_at: datetime) -> str:
    lines = [
        "# Lean Parity — CAMPAIGN_002 H4 (awaiting Lean result)",
        "",
        f"**Generated:** {generated_at.isoformat()} · "
        f"**Branch:** `infra-lean-parity-run-001`",
        "",
        *_banner(),
        "## Status",
        "",
        "No Lean parity result was supplied. The bespoke reference is "
        "validated and ready; this report describes the expected Lean "
        "input shape.",
        "",
        "## Bespoke reference (validated)",
        "",
        f"- target: {reference.get('parity_target', 'n/a')}",
        f"- risk engine used: {reference.get('risk_engine_used', 'n/a')} "
        "(no-RiskEngine parity-isolation reference)",
        f"- total trades: {reference.get('total_trades', 'n/a')}",
        f"- pairs: {len(reference['pairs'])}",
        "",
        "## Expected Lean result shape",
        "",
        "A JSON object (the algorithm's `parity_summary.json`) with a "
        "`pairs` list; each entry needs `instrument` and `trades`, and "
        "optionally `expectancy_r` and `return_pct`:",
        "",
        "```json",
        '{"engine": "lean", "total_trades": 0,',
        ' "pairs": [{"instrument": "EUR_USD", "trades": 0,',
        '            "expectancy_r": 0.0, "return_pct": 0.0}]}',
        "```",
        "",
        "Re-run with `--lean <parity_summary.json>` once a Lean backtest "
        "has produced one.",
        "",
    ]
    return "\n".join(lines)


def render_report(
    report: ComparisonReport,
    *,
    reference_path: str,
    lean_path: str,
    generated_at: datetime,
) -> str:
    lines = [
        "# Lean Parity — CAMPAIGN_002 H4 comparison",
        "",
        f"**Generated:** {generated_at.isoformat()} · "
        f"**Branch:** `infra-lean-parity-run-001`",
        f"**Overall:** **{report.status}**",
        "",
        *_banner(),
        "## Sources",
        "",
        f"- bespoke reference: `{reference_path}`",
        f"- Lean result: `{lean_path}`",
        "",
        "## Per-pair comparison",
        "",
        "| instrument | metric | reference | lean | Δ | status |",
        "|---|---|---|---|---|---|",
    ]
    for p in report.pairs:
        if not p.found:
            lines.append(
                f"| {p.instrument} | — | — | **missing** | — | **FAIL** |"
            )
            continue
        for m in p.metrics:
            lines.append(
                f"| {p.instrument} | {m.name} | {m.reference:.3f} | "
                f"{m.lean:.3f} | {m.delta:+.3f} | {m.status} |"
            )
    lines += [
        "",
        f"**Total trades:** reference {report.total_reference} · "
        f"lean {report.total_lean} · status **{report.total_status}**.",
        "",
        "## Verdict",
        "",
        f"- Overall parity status: **{report.status}**.",
        "  - **PASS** — the independent Lean engine corroborates the "
        "bespoke engine within tolerance.",
        "  - **WARN** — drift inside the review band; inspect before "
        "relying on the comparison.",
        "  - **FAIL** — drift outside tolerance, a missing pair, or "
        "malformed output: localize the cause (a Lean-side parity bug, "
        "or a real bespoke-engine discrepancy) — never tune it away.",
        "",
        "This compares engines. It does not measure, imply, or establish "
        "a strategy edge. CAMPAIGN_002 remains REJECT.",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Compare a Lean CAMPAIGN_002 H4 parity run vs the bespoke reference."
    )
    ap.add_argument("--reference", default=str(DEFAULT_REFERENCE))
    ap.add_argument("--lean", default=None, help="Lean parity result JSON or dir")
    ap.add_argument("--no-lean", action="store_true", help="reference-only validation")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args(argv)

    ref_path = Path(args.reference)
    if not ref_path.is_file():
        print(f"BLOCKER: no bespoke reference at {ref_path}", file=sys.stderr)
        return 2
    try:
        reference = load_reference(ref_path)
    except MalformedLeanOutputError as exc:
        print(f"BLOCKER: {exc}", file=sys.stderr)
        return 2

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC)

    if args.no_lean or not args.lean:
        out_path.write_text(render_no_lean(reference, generated_at=now), encoding="utf-8")
        print(f"reference validated; no Lean result — report → {args.out}")
        return 0

    try:
        lean = load_lean_result(Path(args.lean))
    except MalformedLeanOutputError as exc:
        print(f"FAIL: malformed Lean output — {exc}", file=sys.stderr)
        return 2

    report = compare(reference, lean)
    out_path.write_text(
        render_report(
            report,
            reference_path=args.reference,
            lean_path=args.lean,
            generated_at=now,
        ),
        encoding="utf-8",
    )
    print(f"parity comparison: {report.status} — report → {args.out}")
    return {"OK": 0, "WARN": 1, "FAIL": 2}[report.status]


if __name__ == "__main__":
    raise SystemExit(main())

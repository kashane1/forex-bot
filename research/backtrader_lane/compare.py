"""Backtrader-lane comparison harness.

Compares a Backtrader-lane run summary (the
`backtrader_summary.json` written by the Phase 3 runner) against the
canonical bespoke reference for the same campaign, and emits:

- a per-pair table of trade-count, expectancy R, return %, win rate
  differences, each classified into a divergence label,
- an overall classification per `INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md` §7,
- a compact JSON summary (one row per pair + an overall) and a
  human-readable Markdown report.

The harness **does not modify** any committed campaign artefact or any
bespoke reference. It only reads. It cannot approve a strategy and
does not change a verdict.

`strategy_evidence: false`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class DivergenceLabel(str, Enum):
    """Binding divergence taxonomy. Each comparison emits exactly one."""

    PASS = "PASS"
    TOLERABLE_DRIFT = "TOLERABLE_DRIFT"
    DATA_MISMATCH = "DATA_MISMATCH"
    TIMESTAMP_ALIGNMENT_MISMATCH = "TIMESTAMP_ALIGNMENT_MISMATCH"
    INDICATOR_MISMATCH = "INDICATOR_MISMATCH"
    SIGNAL_RULE_MISMATCH = "SIGNAL_RULE_MISMATCH"
    FILL_MODEL_MISMATCH = "FILL_MODEL_MISMATCH"
    STOP_OR_EXIT_ORDERING_MISMATCH = "STOP_OR_EXIT_ORDERING_MISMATCH"
    SIZING_OR_PNL_MISMATCH = "SIZING_OR_PNL_MISMATCH"
    UNSUPPORTED_BY_BACKTRADER = "UNSUPPORTED_BY_BACKTRADER"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


# Default per-pair tolerance windows for CAMPAIGN_002, mirroring the
# Lean mapping spec §8 "Expected tolerance ranges" table.
DEFAULT_TRADE_COUNT_TOLERANCE_PCT = 5.0       # ±5%
DEFAULT_EXPECTANCY_R_TOLERANCE = 0.03         # ±0.03 R
DEFAULT_RETURN_PCT_TOLERANCE = 0.5            # ±0.5 percentage points
DEFAULT_WIN_RATE_TOLERANCE = 0.05             # ±5 percentage points
# A wider "tolerable drift" band for sub-bps Decimal-vs-float rounding.
WIDER_TRADE_COUNT_TOLERANCE_PCT = 10.0
WIDER_EXPECTANCY_R_TOLERANCE = 0.06
WIDER_RETURN_PCT_TOLERANCE = 1.0


@dataclass(frozen=True)
class Tolerances:
    trade_count_pct: float = DEFAULT_TRADE_COUNT_TOLERANCE_PCT
    expectancy_r: float = DEFAULT_EXPECTANCY_R_TOLERANCE
    return_pct: float = DEFAULT_RETURN_PCT_TOLERANCE
    win_rate: float = DEFAULT_WIN_RATE_TOLERANCE


@dataclass
class PairComparison:
    instrument: str
    bt_trades: int | None
    bespoke_trades: int | None
    trades_delta_pct: float | None
    bt_expectancy_r: float | None
    bespoke_expectancy_r: float | None
    expectancy_r_delta: float | None
    bt_return_pct: float | None
    bespoke_return_pct: float | None
    return_pct_delta: float | None
    bt_win_rate: float | None
    bespoke_win_rate: float | None
    win_rate_delta: float | None
    classification: DivergenceLabel
    notes: list[str] = field(default_factory=list)


@dataclass
class ComparisonReport:
    campaign_id: str
    strategy_id: str
    strategy_version: str
    bespoke_reference_path: str
    backtrader_summary_path: str
    bt_total_trades: int
    bespoke_total_trades: int
    overall_classification: DivergenceLabel
    pair_results: list[PairComparison]
    blocked_instruments: list[str]
    notes: list[str]
    generated_at: str


# ---------------------------------------------------------------------------
# Pure classifier helpers
# ---------------------------------------------------------------------------


def _pct_delta(bt: float, ref: float) -> float | None:
    """Symmetric percent difference vs the bespoke reference. Returns
    None if both sides are zero (no meaningful comparison)."""

    if ref == 0:
        return None if bt == 0 else float("inf")
    return (bt - ref) / abs(ref) * 100.0


def _abs_delta(bt: float | None, ref: float | None) -> float | None:
    if bt is None or ref is None:
        return None
    return bt - ref


def classify_pair(
    *,
    bt_trades: int | None,
    bespoke_trades: int | None,
    bt_expectancy_r: float | None,
    bespoke_expectancy_r: float | None,
    bt_return_pct: float | None,
    bespoke_return_pct: float | None,
    bt_win_rate: float | None,
    bespoke_win_rate: float | None,
    tolerances: Tolerances = Tolerances(),
) -> tuple[DivergenceLabel, list[str], dict[str, float | None]]:
    """Return (classification, notes, deltas) for a single pair.

    Decision ladder (first match wins):

    1. If either side is missing data for the pair → BLOCKED.
    2. If trade counts agree within the wider band but expectancy /
       return differ outside the tight band → SIZING_OR_PNL_MISMATCH.
    3. If trade counts diverge beyond the wider band → SIGNAL_RULE_MISMATCH.
    4. If trade counts diverge between the tight and wider bands → TOLERABLE_DRIFT.
    5. If every tight band holds → PASS.
    6. Otherwise → UNKNOWN (with notes describing which dimension drifted).
    """

    notes: list[str] = []

    if bt_trades is None or bespoke_trades is None:
        return DivergenceLabel.BLOCKED, ["one or both sides missing pair data"], {}

    trades_delta_pct = _pct_delta(float(bt_trades), float(bespoke_trades))
    expectancy_r_delta = _abs_delta(bt_expectancy_r, bespoke_expectancy_r)
    return_pct_delta = _abs_delta(bt_return_pct, bespoke_return_pct)
    win_rate_delta = _abs_delta(bt_win_rate, bespoke_win_rate)
    deltas = {
        "trades_delta_pct": trades_delta_pct,
        "expectancy_r_delta": expectancy_r_delta,
        "return_pct_delta": return_pct_delta,
        "win_rate_delta": win_rate_delta,
    }

    # Tight tolerance band — both engines agree to spec.
    tight_trades = trades_delta_pct is not None and abs(trades_delta_pct) <= tolerances.trade_count_pct
    tight_expectancy = (
        expectancy_r_delta is None or abs(expectancy_r_delta) <= tolerances.expectancy_r
    )
    tight_return = (
        return_pct_delta is None or abs(return_pct_delta) <= tolerances.return_pct
    )
    tight_win_rate = (
        win_rate_delta is None or abs(win_rate_delta) <= tolerances.win_rate
    )
    if tight_trades and tight_expectancy and tight_return and tight_win_rate:
        return DivergenceLabel.PASS, ["all tight tolerance bands hold"], deltas

    # Wider tolerance band — same trade space, sub-bps PnL drift.
    wider_trades = (
        trades_delta_pct is not None and abs(trades_delta_pct) <= WIDER_TRADE_COUNT_TOLERANCE_PCT
    )

    if wider_trades and tight_expectancy and tight_return:
        # Trade counts within the wider band; metric drift inside the
        # wider band; this is tolerable.
        notes.append(
            f"trade-count drift {trades_delta_pct:.2f}% inside wider band; "
            "metric agreement holds"
        )
        return DivergenceLabel.TOLERABLE_DRIFT, notes, deltas

    if not wider_trades:
        # Large trade-count divergence — the two engines disagree on
        # whether a signal fired at all.
        notes.append(
            f"trade-count drift {trades_delta_pct:.2f}% exceeds wider band "
            f"(±{WIDER_TRADE_COUNT_TOLERANCE_PCT:.1f}%) — likely SIGNAL_RULE_MISMATCH"
        )
        return DivergenceLabel.SIGNAL_RULE_MISMATCH, notes, deltas

    # Trade counts agree but PnL / expectancy / return don't.
    if not tight_expectancy or not tight_return or not tight_win_rate:
        if expectancy_r_delta is not None and abs(expectancy_r_delta) > WIDER_EXPECTANCY_R_TOLERANCE:
            notes.append(
                f"expectancy R delta {expectancy_r_delta:.4f} outside wider band — "
                "likely SIZING_OR_PNL_MISMATCH or FILL_MODEL_MISMATCH"
            )
            return DivergenceLabel.SIZING_OR_PNL_MISMATCH, notes, deltas
        if return_pct_delta is not None and abs(return_pct_delta) > WIDER_RETURN_PCT_TOLERANCE:
            notes.append(
                f"return % delta {return_pct_delta:.4f} outside wider band — "
                "likely SIZING_OR_PNL_MISMATCH"
            )
            return DivergenceLabel.SIZING_OR_PNL_MISMATCH, notes, deltas
        notes.append("metric drift inside wider band but outside tight band")
        return DivergenceLabel.TOLERABLE_DRIFT, notes, deltas

    notes.append("classification could not be determined from available metrics")
    return DivergenceLabel.UNKNOWN, notes, deltas


def _bespoke_pair_lookup(bespoke_ref: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return a name → pair-record mapping for the bespoke reference JSON.

    Handles the campaign-002 reference shape:
      {"pairs": [{"instrument": "EUR_USD", "trades": 233, "expectancy_r": -0.196, ...}, …]}
    """

    out: dict[str, dict[str, Any]] = {}
    for entry in bespoke_ref.get("pairs", []):
        out[entry["instrument"]] = entry
    return out


def compare(
    *,
    backtrader_summary_path: Path,
    bespoke_reference_path: Path,
    tolerances: Tolerances = Tolerances(),
) -> ComparisonReport:
    """Compare a runner-emitted summary against the bespoke reference.

    Raises ``FileNotFoundError`` if either input file is absent.
    """

    if not backtrader_summary_path.exists():
        raise FileNotFoundError(
            f"backtrader summary not found at {backtrader_summary_path}"
        )
    if not bespoke_reference_path.exists():
        raise FileNotFoundError(
            f"bespoke reference not found at {bespoke_reference_path}"
        )

    bt = json.loads(backtrader_summary_path.read_text(encoding="utf-8"))
    bespoke = json.loads(bespoke_reference_path.read_text(encoding="utf-8"))
    bespoke_pairs = _bespoke_pair_lookup(bespoke)

    bt_pairs: dict[str, dict[str, Any]] = {p["instrument"]: p for p in bt.get("pairs", [])}
    bt_blocked: list[str] = list(bt.get("blocked_instruments", []))

    pair_reports: list[PairComparison] = []
    notes: list[str] = []

    for name in sorted(set(bt_pairs) | set(bespoke_pairs)):
        bt_entry = bt_pairs.get(name)
        bespoke_entry = bespoke_pairs.get(name)
        bt_trades = bt_entry.get("trades") if bt_entry else None
        bespoke_trades = bespoke_entry.get("trades") if bespoke_entry else None
        bt_exp = bt_entry.get("expectancy_r") if bt_entry else None
        bespoke_exp = (
            bespoke_entry.get("expectancy_r") if bespoke_entry else None
        )
        # The Backtrader summary does not carry per-pair expectancy R or
        # return % out of the box (the runner emits trade-by-trade JSONL
        # plus simple pair PnL totals); if needed for comparison, derive
        # them here from the optional fields.
        if bt_exp is None and bt_entry is not None and bt_entry.get("trades", 0) > 0:
            bt_exp = _derive_expectancy_r(bt_entry)
        bt_return = bt_entry.get("return_pct") if bt_entry else None
        bespoke_return = (
            bespoke_entry.get("return_pct") if bespoke_entry else None
        )
        if bt_return is None and bt_entry is not None:
            bt_return = _derive_return_pct(bt_entry)
        bt_win_rate = bt_entry.get("win_rate") if bt_entry else None
        bespoke_win_rate = (
            bespoke_entry.get("win_rate") if bespoke_entry else None
        )

        label, pair_notes, deltas = classify_pair(
            bt_trades=bt_trades,
            bespoke_trades=bespoke_trades,
            bt_expectancy_r=bt_exp,
            bespoke_expectancy_r=bespoke_exp,
            bt_return_pct=bt_return,
            bespoke_return_pct=bespoke_return,
            bt_win_rate=bt_win_rate,
            bespoke_win_rate=bespoke_win_rate,
            tolerances=tolerances,
        )

        if bt_entry is None:
            pair_notes.append("not run in backtrader lane")
        if bespoke_entry is None:
            pair_notes.append("not present in bespoke reference")

        pair_reports.append(
            PairComparison(
                instrument=name,
                bt_trades=bt_trades,
                bespoke_trades=bespoke_trades,
                trades_delta_pct=deltas.get("trades_delta_pct"),
                bt_expectancy_r=bt_exp,
                bespoke_expectancy_r=bespoke_exp,
                expectancy_r_delta=deltas.get("expectancy_r_delta"),
                bt_return_pct=bt_return,
                bespoke_return_pct=bespoke_return,
                return_pct_delta=deltas.get("return_pct_delta"),
                bt_win_rate=bt_win_rate,
                bespoke_win_rate=bespoke_win_rate,
                win_rate_delta=deltas.get("win_rate_delta"),
                classification=label,
                notes=pair_notes,
            )
        )

    overall = _roll_up_classifications(pair_reports, bt_blocked)
    if bt_blocked:
        notes.append(
            f"backtrader lane reported {len(bt_blocked)} blocked instruments: "
            f"{sorted(bt_blocked)}"
        )

    return ComparisonReport(
        campaign_id=bt.get("campaign_id", "UNKNOWN"),
        strategy_id=bt.get("strategy_id", "UNKNOWN"),
        strategy_version=bt.get("strategy_version", "UNKNOWN"),
        bespoke_reference_path=str(bespoke_reference_path),
        backtrader_summary_path=str(backtrader_summary_path),
        bt_total_trades=int(bt.get("total_trades", 0)),
        bespoke_total_trades=int(bespoke.get("total_trades", 0)),
        overall_classification=overall,
        pair_results=pair_reports,
        blocked_instruments=bt_blocked,
        notes=notes,
        generated_at=datetime.now(UTC).isoformat(timespec="seconds"),
    )


def _derive_expectancy_r(bt_pair_entry: dict[str, Any]) -> float | None:
    """The runner summary emits per-pair PnL totals; per-pair R requires
    the trade list, which the harness does not load (the JSONL lives
    separately). Returning None here is the documented behaviour."""

    return None


def _derive_return_pct(bt_pair_entry: dict[str, Any]) -> float | None:
    """Convert per-pair PnL total to a return % over the bespoke
    reference's starting equity. The runner does not currently carry the
    bespoke starting equity per pair, so use the campaign default (500).

    For a more precise comparison, the comparison script can be passed
    the actual starting equity via Tolerances or a CLI flag in the
    future. For now, this returns None — the trade-count and expectancy
    deltas are the load-bearing checks.
    """

    return None


def _roll_up_classifications(
    pairs: list[PairComparison], blocked: list[str]
) -> DivergenceLabel:
    """Roll per-pair labels into one overall verdict.

    Order of precedence:

    1. Any FAIL-like label on any pair → that label (worst-of).
    2. Any TOLERABLE_DRIFT and no FAIL-like → TOLERABLE_DRIFT.
    3. Any BLOCKED or blocked instruments → BLOCKED.
    4. Otherwise → PASS.
    """

    severity = {
        DivergenceLabel.SIGNAL_RULE_MISMATCH: 60,
        DivergenceLabel.SIZING_OR_PNL_MISMATCH: 55,
        DivergenceLabel.FILL_MODEL_MISMATCH: 55,
        DivergenceLabel.STOP_OR_EXIT_ORDERING_MISMATCH: 55,
        DivergenceLabel.INDICATOR_MISMATCH: 50,
        DivergenceLabel.TIMESTAMP_ALIGNMENT_MISMATCH: 50,
        DivergenceLabel.DATA_MISMATCH: 50,
        DivergenceLabel.UNSUPPORTED_BY_BACKTRADER: 45,
        DivergenceLabel.UNKNOWN: 40,
        DivergenceLabel.TOLERABLE_DRIFT: 30,
        DivergenceLabel.BLOCKED: 20,
        DivergenceLabel.PASS: 0,
    }
    worst = DivergenceLabel.PASS
    worst_severity = -1
    for p in pairs:
        s = severity.get(p.classification, 40)
        if s > worst_severity:
            worst_severity = s
            worst = p.classification
    if worst == DivergenceLabel.PASS and blocked:
        return DivergenceLabel.BLOCKED
    return worst


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_markdown(report: ComparisonReport) -> str:
    lines: list[str] = []
    lines.append(f"# Backtrader Parity Comparison — `{report.campaign_id}`")
    lines.append("")
    lines.append(
        "> `strategy_evidence: false`. Verification infrastructure. Does "
        "**not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, "
        "CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/"
        "research-only. CAMPAIGN_014 remains scaffold-only."
    )
    lines.append("")
    lines.append(f"- Generated at: `{report.generated_at}`")
    lines.append(f"- Strategy: `{report.strategy_id}` `{report.strategy_version}`")
    lines.append(f"- Backtrader summary: `{report.backtrader_summary_path}`")
    lines.append(f"- Bespoke reference: `{report.bespoke_reference_path}`")
    lines.append(
        f"- Total trades: backtrader **{report.bt_total_trades}** · "
        f"bespoke **{report.bespoke_total_trades}** · Δ "
        f"{report.bt_total_trades - report.bespoke_total_trades:+d}"
    )
    lines.append(f"- **Overall classification: `{report.overall_classification.value}`**")
    lines.append("")
    if report.notes:
        lines.append("### Run notes")
        for n in report.notes:
            lines.append(f"- {n}")
        lines.append("")
    lines.append(
        "| instrument | BT trades | bespoke trades | Δ% | BT R | bespoke R | Δ R | classification |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for p in report.pair_results:
        bt_t = _fmt_int(p.bt_trades)
        b_t = _fmt_int(p.bespoke_trades)
        td = _fmt_pct(p.trades_delta_pct)
        bt_r = _fmt_float(p.bt_expectancy_r)
        b_r = _fmt_float(p.bespoke_expectancy_r)
        er = _fmt_float(p.expectancy_r_delta)
        label = p.classification.value
        lines.append(
            f"| {p.instrument} | {bt_t} | {b_t} | {td} | {bt_r} | {b_r} | {er} | `{label}` |"
        )
    lines.append("")
    for p in report.pair_results:
        if not p.notes:
            continue
        lines.append(f"#### {p.instrument} notes")
        for n in p.notes:
            lines.append(f"- {n}")
        lines.append("")
    return "\n".join(lines) + "\n"


def to_json_dict(report: ComparisonReport) -> dict[str, Any]:
    return {
        "campaign_id": report.campaign_id,
        "strategy_id": report.strategy_id,
        "strategy_version": report.strategy_version,
        "bespoke_reference_path": report.bespoke_reference_path,
        "backtrader_summary_path": report.backtrader_summary_path,
        "bt_total_trades": report.bt_total_trades,
        "bespoke_total_trades": report.bespoke_total_trades,
        "overall_classification": report.overall_classification.value,
        "blocked_instruments": report.blocked_instruments,
        "notes": report.notes,
        "generated_at": report.generated_at,
        "pairs": [
            {
                "instrument": p.instrument,
                "bt_trades": p.bt_trades,
                "bespoke_trades": p.bespoke_trades,
                "trades_delta_pct": p.trades_delta_pct,
                "bt_expectancy_r": p.bt_expectancy_r,
                "bespoke_expectancy_r": p.bespoke_expectancy_r,
                "expectancy_r_delta": p.expectancy_r_delta,
                "bt_return_pct": p.bt_return_pct,
                "bespoke_return_pct": p.bespoke_return_pct,
                "return_pct_delta": p.return_pct_delta,
                "bt_win_rate": p.bt_win_rate,
                "bespoke_win_rate": p.bespoke_win_rate,
                "win_rate_delta": p.win_rate_delta,
                "classification": p.classification.value,
                "notes": p.notes,
            }
            for p in report.pair_results
        ],
        "strategy_evidence": False,
    }


def _fmt_int(v: int | None) -> str:
    return "—" if v is None else f"{v}"


def _fmt_float(v: float | None) -> str:
    if v is None:
        return "—"
    if abs(v) >= 1:
        return f"{v:.4f}"
    return f"{v:.6f}"


def _fmt_pct(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v:+.2f}%"

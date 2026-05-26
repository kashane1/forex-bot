#!/usr/bin/env python3
"""Diagnostic-only MTF confluence + cost atlas report.

No strategy campaign. No broker orders. strategy_evidence: false.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from research.confluence.grader import grade_confluence
from research.confluence.models import CrossAssetState, TimeframeState
from research.confluence.states import (
    aggregate_d1_from_h4,
    compute_h4_setup,
    compute_timeframe_state,
    resample_h4_to_d1,
)
from research.cost_atlas.atlas import build_cost_atlas
from research.cost_atlas.loader import SEVEN_PAIR_UNIVERSE, load_deduped_h4_frame
from research.cross_asset_features.loader import (
    align_features_to_h4,
    build_availability_report,
    load_features_from_directory,
)
from research.edge_discovery.real_data import resolve_h4_store_path


def _cross_asset_from_row(row, side: str) -> CrossAssetState:
    missing: list[str] = []
    usd = "unknown"
    risk = "unknown"
    if "dxy" in row and row["dxy"] == row["dxy"]:
        dxy = float(row["dxy"])
        usd = "strengthening" if dxy > 97 else "weakening" if dxy < 96 else "neutral"
    else:
        missing.append("dxy")
    if "vix" in row and row["vix"] == row["vix"]:
        vix = float(row["vix"])
        risk = "risk_off" if vix > 25 else "risk_on" if vix < 20 else "neutral"
    else:
        missing.append("vix")
    rates = "unknown"
    if "us10y" in row and row["us10y"] == row["us10y"]:
        rates = "higher" if float(row["us10y"]) > 1.66 else "flat"
    else:
        missing.append("us10y")
    return CrossAssetState(
        usd_regime=usd,  # type: ignore[arg-type]
        risk_regime=risk,  # type: ignore[arg-type]
        rates_bias=rates,  # type: ignore[arg-type]
        missing_features=tuple(missing),
    )


def run_diagnostics(
    repo_root: Path,
    *,
    instruments: tuple[str, ...] = SEVEN_PAIR_UNIVERSE,
    sample_every: int = 20,
    db_path: Path | None = None,
) -> dict[str, object]:
    db_path = db_path or resolve_h4_store_path(repo_root)
    if db_path is None:
        raise FileNotFoundError("H4 SQLite store not found")

    atlas = build_cost_atlas(repo_root, instruments=instruments, db_path=db_path)
    feature_dir = repo_root / "data" / "external_features"
    fixture_dir = repo_root / "tests" / "fixtures" / "cross_asset"
    features = load_features_from_directory(feature_dir)
    if not features:
        features = load_features_from_directory(fixture_dir)
    availability = build_availability_report(repo_root)

    grade_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    examples: list[dict[str, object]] = []
    contexts_evaluated = 0
    missing_data_notes: list[str] = []

    for instrument in instruments:
        frame, _ = load_deduped_h4_frame(repo_root, instrument, db_path=db_path)
        if len(frame) < 100:
            missing_data_notes.append(f"{instrument}: insufficient bars")
            continue
        d1 = resample_h4_to_d1(frame)
        w1 = aggregate_d1_from_h4(frame)
        w1_state = compute_timeframe_state(w1) if len(w1) >= 60 else "unknown"
        d1_state = compute_timeframe_state(d1) if len(d1) >= 60 else "unknown"
        h4_setup = compute_h4_setup(frame)
        aligned = align_features_to_h4(frame.index, features) if features else None

        for i in range(80, len(frame), sample_every):
            sub = frame.iloc[: i + 1]
            bar = frame.iloc[i]
            spread_to_atr = float(bar.get("spread_to_atr_pct", 0)) if "spread_to_atr_pct" in frame.columns else None
            if spread_to_atr is None:
                from research.cost_atlas.metrics import compute_bar_metrics

                metrics = compute_bar_metrics(instrument, sub)
                spread_to_atr = float(metrics["spread_to_atr_pct"].iloc[-1])

            cross = CrossAssetState()
            if aligned is not None:
                row = aligned.iloc[i]
                cross = _cross_asset_from_row(row, "long")

            tf = TimeframeState(
                w1=w1_state,
                d1=d1_state,
                h4_setup=h4_setup,
                h1_trigger="unknown",
            )
            for side in ("long", "short"):
                score = grade_confluence(
                    side=side,
                    timeframe=tf,
                    cross_asset=cross,
                    cost_spread_to_atr_pct=spread_to_atr,
                )
                contexts_evaluated += 1
                grade_counts[score.grade] += 1
                for rc in score.reason_codes:
                    reason_counts[rc] += 1
                if len(examples) < 8:
                    examples.append(
                        {
                            "instrument": instrument,
                            "bar_time": str(frame.index[i]),
                            "side": side,
                            **score.to_features_dict(),
                        }
                    )

    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "contexts_evaluated": contexts_evaluated,
        "instruments": list(instruments),
        "sample_every_bars": sample_every,
        "grade_distribution": dict(grade_counts),
        "top_reason_codes": reason_counts.most_common(15),
        "missing_data_notes": missing_data_notes,
        "cost_atlas_bar_count": atlas.summary["bar_count"],
        "cost_hostile_cell_count": atlas.summary["hostile_cell_count"],
        "cross_asset_status": availability["status"],
        "examples": examples,
        "explicit_disclaimer": (
            "Diagnostic infrastructure only. Not strategy evidence. "
            "No approval. No expectancy or win-rate claims."
        ),
    }


def write_outputs(summary: dict[str, object], output_dir: Path, doc_path: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "confluence_diagnostic_summary.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    with (output_dir / "confluence_reason_code_counts.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["reason_code", "count"])
        for code, count in summary.get("top_reason_codes", []):
            writer.writerow([code, count])

    doc_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# MTF Confluence and Cost Atlas Diagnostics 001",
        "",
        "**Diagnostic only** — `strategy_evidence: false`. No strategy approved.",
        "",
        f"- Contexts evaluated: {summary['contexts_evaluated']}",
        f"- Grade distribution: {summary['grade_distribution']}",
        f"- Cost atlas bars: {summary['cost_atlas_bar_count']}",
        f"- Hostile cells: {summary['cost_hostile_cell_count']}",
        f"- Cross-asset status: {summary['cross_asset_status']}",
        "",
        "## Top reason codes",
        "",
    ]
    for code, count in summary.get("top_reason_codes", []):
        lines.append(f"- `{code}`: {count}")
    lines.extend(["", "## Disclaimer", "", str(summary["explicit_disclaimer"]), ""])
    doc_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "research" / "confluence_diagnostics")
    parser.add_argument(
        "--doc",
        type=Path,
        default=ROOT / "docs" / "research" / "MTF_CONFLUENCE_AND_COST_ATLAS_DIAGNOSTICS_001.md",
    )
    args = parser.parse_args()
    try:
        summary = run_diagnostics(ROOT)
    except FileNotFoundError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    write_outputs(summary, args.output_dir, args.doc)
    print(f"Wrote diagnostics to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

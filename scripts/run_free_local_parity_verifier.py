#!/usr/bin/env python3
"""Run the free / local independent parity verifier.

Reads the authoritative CAMPAIGN_002 parameter set and, for each pair
in the universe, attempts to consume the exported H4 candle CSV from
``research/lean_parity/exports/campaign_002_h4/``. The CSVs are
gitignored regenerable bulk data; any pair whose CSV is absent is
reported as BLOCKED and excluded from the per-pair totals, never
silently treated as zero trades.

Outputs:

- ``<out_dir>/parity_summary.json`` — same shape as the bespoke
  reference and the LEAN ``parity_summary.json``.
- ``<out_dir>/trades.csv`` — flat trade list (one row per closed
  position). Gitignored.
- ``<out_dir>/parity_summary.md`` — human-readable summary rendered
  via ``reporting.render_verifier_result_md``.

The script does not call any broker, OANDA, QuantConnect, LEAN, or
external network service. It edits no committed config and writes
nothing under ``src/``. ``configs/approved_strategies.yaml`` is not
touched. No order is submitted. CAMPAIGN_002 remains REJECT regardless
of the script's output.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# isort: off
from research.parity_verifier.data_loader import (
    DEFAULT_BESPOKE_REFERENCE_PATH,
    DEFAULT_CONFIG_PATH,
    DEFAULT_EXPORT_DIR,
    config_hash,
    load_bespoke_reference,
    load_candle_csv,
    load_verifier_config,
)
from research.parity_verifier.event_loop import run_pair
from research.parity_verifier.instruments import CAMPAIGN_002_INSTRUMENTS
from research.parity_verifier.models import (
    PairResult,
    Trade,
    VerifierResult,
)
from research.parity_verifier.reporting import render_verifier_result_md
# isort: on


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the free / local independent parity verifier. "
            "Strictly local; no network, no broker, no QC/LEAN."
        )
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the authoritative CAMPAIGN_002 parameter JSON.",
    )
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=DEFAULT_EXPORT_DIR,
        help="Path to the seven-pair H4 candle CSV directory (gitignored bulk).",
    )
    parser.add_argument(
        "--bespoke-reference",
        type=Path,
        default=DEFAULT_BESPOKE_REFERENCE_PATH,
        help="Path to the bespoke no-RiskEngine reference JSON.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directory to write verifier outputs into.",
    )
    parser.add_argument(
        "--instruments",
        nargs="+",
        default=sorted(CAMPAIGN_002_INSTRUMENTS),
        help="Subset of instruments to run (defaults to the seven-pair universe).",
    )
    return parser.parse_args(argv)


def _write_trades_csv(path: Path, trades: list[Trade]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "instrument",
                "side",
                "entry_time",
                "entry_price",
                "exit_time",
                "exit_price",
                "exit_reason",
                "units",
                "initial_stop_price",
                "final_stop_price",
                "bars_held",
                "r_multiple",
                "return_pct",
            ]
        )
        for t in trades:
            writer.writerow(
                [
                    t.instrument,
                    t.side.value,
                    t.entry_time.isoformat(),
                    f"{t.entry_price:.6f}",
                    t.exit_time.isoformat(),
                    f"{t.exit_price:.6f}",
                    t.exit_reason.value,
                    t.units,
                    f"{t.initial_stop_price:.6f}",
                    f"{t.final_stop_price:.6f}",
                    t.bars_held,
                    f"{t.r_multiple:.6f}",
                    f"{t.return_pct:.6f}",
                ]
            )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    out_dir: Path = args.output
    out_dir.mkdir(parents=True, exist_ok=True)
    config = load_verifier_config(args.config)
    bespoke = load_bespoke_reference(args.bespoke_reference)
    # Echo the bespoke reference availability — it's part of the status
    # the verifier reports back to the human caller.
    print(
        f"Loaded bespoke reference: {args.bespoke_reference} "
        f"({bespoke.get('total_trades', '?')} trades, "
        f"{len(bespoke.get('pairs', []))} pairs).",
        flush=True,
    )

    pair_results: list[PairResult] = []
    all_trades: list[Trade] = []
    blocked: list[str] = []

    for name in args.instruments:
        if name not in CAMPAIGN_002_INSTRUMENTS:
            print(f"Skipping unknown instrument {name!r}.", file=sys.stderr)
            continue
        spec = CAMPAIGN_002_INSTRUMENTS[name]
        try:
            candles = load_candle_csv(name, args.export_dir)
        except FileNotFoundError as exc:
            print(f"BLOCKED — {name}: {exc}", flush=True)
            blocked.append(name)
            continue
        result, trades = run_pair(
            candles=candles, instrument=spec, config=config
        )
        pair_results.append(result)
        all_trades.extend(trades)
        print(
            f"{name}: {result.trades} trades · "
            f"expectancy_r={result.expectancy_r} · "
            f"return_pct={result.return_pct}",
            flush=True,
        )

    window_start = (
        all_trades[0].entry_time if all_trades else datetime(2020, 1, 1, tzinfo=UTC)
    )
    window_end = (
        all_trades[-1].exit_time if all_trades else datetime(2026, 5, 20, tzinfo=UTC)
    )
    summary = VerifierResult(
        parity_target="CAMPAIGN_002 H4 trend_following baseline",
        risk_engine_used=False,
        fill_timing="signal_bar_close",
        window_start=window_start,
        window_end=window_end,
        config_hash=config_hash(config),
        strategy_evidence=False,
        total_trades=sum(p.trades for p in pair_results),
        pairs=pair_results,
    )

    summary_json_path = out_dir / "parity_summary.json"
    summary_json_path.write_text(
        json.dumps(summary.model_dump(mode="json"), indent=2, default=str),
        encoding="utf-8",
    )
    _write_trades_csv(out_dir / "trades.csv", all_trades)
    md = render_verifier_result_md(summary)
    if blocked:
        md += (
            "\n## Pairs blocked (no CSV)\n\n"
            "The following instruments had no exported H4 CSV locally and "
            "were excluded from the totals. Regenerate them via "
            "`research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md` "
            "and re-run.\n\n"
        )
        for name in blocked:
            md += f"- {name}\n"
    (out_dir / "parity_summary.md").write_text(md, encoding="utf-8")

    print(
        f"\nWrote: {summary_json_path}\n"
        f"       {out_dir / 'trades.csv'}\n"
        f"       {out_dir / 'parity_summary.md'}\n"
        f"Verifier total trades: {summary.total_trades}\n"
        f"Blocked pairs: {blocked or '(none)'}",
        flush=True,
    )
    # Exit non-zero if every requested pair was blocked — communicates
    # to the caller that no usable result was produced.
    if pair_results == [] and blocked:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

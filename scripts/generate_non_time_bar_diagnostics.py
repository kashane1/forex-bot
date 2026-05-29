#!/usr/bin/env python3
"""Compact diagnostics for non-time bars (range / volatility) from local M1.

infra-range-and-volatility-bars-001 · Phases 4-6.

Streams local canonical M1 from the Postgres research store (NO broker/network
calls) through the deterministic builders in
``forex_bot.data.non_time_bars`` and writes **compact JSON summaries/manifests**
under ``research/non_time_bars/<run_label>/``. Full generated bars are NOT
written unless ``--save-full-bars`` is passed, and even then they land in a
gitignored ``full_bars/`` subdir (CSV) — never committed.

This is data-infrastructure diagnostics only: it measures bar geometry
(counts, compression, session/weekday spread, completion reasons). It produces
**no strategy evidence**, trades nothing, and approves nothing.

Examples
--------
Smoke (one pair, bounded window, one threshold each)::

    python scripts/generate_non_time_bar_diagnostics.py --bar-type range \
        --pairs USD_JPY --from 2023-01-01 --to 2023-03-01 --thresholds 10

Full corpus range grid::

    python scripts/generate_non_time_bar_diagnostics.py --bar-type range \
        --thresholds 5 10 15 20 --run-label full_corpus
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import Counter
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

from forex_bot.data.m1_corpus_validation import (
    MAJOR_PAIRS,
    _row_to_candle,
    iter_m1_chunks,
    pair_range,
)
from forex_bot.data.non_time_bars import (
    RangeBar,
    RangeBarConfig,
    VolatilityBar,
    VolatilityBarConfig,
    stream_range_bars,
    stream_volatility_bars,
)
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ

DEFAULT_OUTPUT_DIR = ROOT / "research" / "non_time_bars"
GAP_SECONDS = 24 * 3600  # a bar spanning > 1 day flags a weekend/holiday gap


# --------------------------------------------------------------------------- #
# Pure helpers (unit-tested in tests/unit/test_non_time_bar_diagnostics.py)
# --------------------------------------------------------------------------- #


def session_bucket(hour: int) -> str:
    """FX session bucket by UTC hour (Tokyo / London / overlap / NY / rollover).

    Same UTC-hour partition as forex_bot.research.microstructure_confirmations,
    duplicated here so the diagnostics script stays import-light and the helper
    is unit-testable without pulling research dependencies.
    """
    h = int(hour) % 24
    if h >= 21:
        return "rollover_late"
    if h < 7:
        return "tokyo"
    if h < 12:
        return "london"
    if h < 16:
        return "london_ny_overlap"
    return "new_york"  # 16..21


def _number_stats(values: list[float]) -> dict[str, float | None]:
    """Compact distribution summary (None-safe for empty input)."""
    if not values:
        return {"mean": None, "median": None, "min": None, "max": None, "p25": None, "p75": None}
    ordered = sorted(values)
    quantiles = statistics.quantiles(ordered, n=4) if len(ordered) >= 2 else [ordered[0], ordered[0], ordered[0]]
    return {
        "mean": round(statistics.fmean(ordered), 4),
        "median": round(statistics.median(ordered), 4),
        "min": round(ordered[0], 4),
        "max": round(ordered[-1], 4),
        "p25": round(quantiles[0], 4),
        "p75": round(quantiles[2], 4),
    }


def summarize_bars(
    bars: list[RangeBar | VolatilityBar],
    *,
    instrument: str,
    bar_type: str,
    threshold_label: str,
    m1_rows: int,
) -> dict[str, Any]:
    """Compute the compact per-(pair, threshold) diagnostic summary.

    Pure: depends only on the bar records + the M1 row count of the window.
    ``m1_rows`` is used for compression ratios (vs M1 and approx vs M15).
    """
    completed = [b for b in bars if not b.incomplete]
    incomplete = [b for b in bars if b.incomplete]
    source_counts = [float(b.source_count) for b in completed]
    elapsed_seconds = [(b.close_time - b.open_time).total_seconds() for b in completed]
    overshoot = [float(b.overshoot_pips) for b in completed]

    sessions: Counter[str] = Counter(session_bucket(b.close_time.hour) for b in completed)
    weekdays: Counter[str] = Counter(
        b.close_time.strftime("%A") for b in completed
    )
    reasons: Counter[str] = Counter(b.completion_reason for b in completed)
    thresholds_crossed: Counter[int] = Counter(b.thresholds_crossed for b in completed)
    multi_threshold = sum(1 for b in completed if b.thresholds_crossed > 1)
    gap_spanning = sum(1 for s in elapsed_seconds if s > GAP_SECONDS)

    n = len(completed)
    times = [b.close_time for b in completed]
    summary: dict[str, Any] = {
        "instrument": instrument,
        "bar_type": bar_type,
        "threshold": threshold_label,
        "bar_count": n,
        "incomplete_final_bars": len(incomplete),
        "m1_source_rows": m1_rows,
        "first_bar_close_utc": min(times).isoformat() if times else None,
        "last_bar_close_utc": max(times).isoformat() if times else None,
        "source_m1_rows_per_bar": _number_stats(source_counts),
        "elapsed_seconds_per_bar": _number_stats(elapsed_seconds),
        "elapsed_minutes_per_bar": _number_stats([s / 60 for s in elapsed_seconds]),
        "overshoot_pips_per_bar": _number_stats(overshoot),
        "session_distribution": dict(sorted(sessions.items())),
        "weekday_distribution": dict(sorted(weekdays.items())),
        "completion_reason_counts": dict(sorted(reasons.items())),
        "thresholds_crossed_distribution": {str(k): v for k, v in sorted(thresholds_crossed.items())},
        "multi_threshold_bars": multi_threshold,
        "compression_vs_m1": round(m1_rows / n, 2) if n else None,
        "compression_vs_m15_approx": round((m1_rows / 15) / n, 2) if n else None,
        "data_quality_warnings": _quality_warnings(n, gap_spanning, multi_threshold),
    }
    return summary


def _quality_warnings(bar_count: int, gap_spanning: int, multi_threshold: int) -> list[str]:
    warnings: list[str] = []
    if bar_count == 0:
        warnings.append("no completed bars in window (threshold too large or window too short)")
    if gap_spanning:
        warnings.append(f"{gap_spanning} bar(s) span >24h (weekend/holiday gaps — expected in FX)")
    if bar_count and multi_threshold / bar_count > 0.10:
        warnings.append(
            f"{multi_threshold}/{bar_count} bars crossed >1 threshold in a single M1 candle "
            "(threshold small relative to M1 volatility)"
        )
    return warnings


# --------------------------------------------------------------------------- #
# DB streaming + per-pair run (impure)
# --------------------------------------------------------------------------- #


class _CountingStream:
    """Wrap an M1 candle generator to count rows consumed (peak memory = 1 row)."""

    def __init__(self, inner: Iterator[Any]) -> None:
        self._inner = inner
        self.count = 0

    def __iter__(self) -> Iterator[Any]:
        for row in self._inner:
            self.count += 1
            yield row


def _m1_candles(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_utc: datetime,
    to_utc: datetime,
    chunk_days: int,
    max_rows: int | None,
) -> Iterator[Any]:
    emitted = 0
    for chunk in iter_m1_chunks(
        store, instrument=instrument, start_utc=from_utc, end_utc=to_utc, chunk_days=chunk_days
    ):
        for row in chunk:
            yield _row_to_candle(row, instrument=instrument)
            emitted += 1
            if max_rows is not None and emitted >= max_rows:
                return


def run_pair(
    store: PostgresCandleStore,
    instrument: str,
    *,
    bar_type: str,
    threshold: float,
    method: str,
    price_basis: str,
    from_utc: datetime,
    to_utc: datetime,
    chunk_days: int,
    max_rows: int | None,
    out_dir: Path,
    save_full_bars: bool,
) -> dict[str, Any]:
    counter = _CountingStream(
        _m1_candles(
            store,
            instrument,
            from_utc=from_utc,
            to_utc=to_utc,
            chunk_days=chunk_days,
            max_rows=max_rows,
        )
    )
    if bar_type == "range":
        cfg_r = RangeBarConfig(instrument=instrument, threshold_pips=threshold, price_basis=price_basis)
        bars: list[Any] = list(stream_range_bars(iter(counter), cfg_r))
        threshold_label = f"{threshold:g}pip"
    else:
        cfg_v = VolatilityBarConfig(
            instrument=instrument,
            method=method,
            threshold_mode="fixed",
            threshold_pips=threshold,
            price_basis=price_basis,
        )
        bars = list(stream_volatility_bars(iter(counter), cfg_v))
        threshold_label = f"{method}_{threshold:g}pip"

    summary = summarize_bars(
        bars,
        instrument=instrument,
        bar_type=bar_type,
        threshold_label=threshold_label,
        m1_rows=counter.count,
    )
    if save_full_bars:
        _write_full_bars(out_dir, instrument, threshold_label, bars)
    return summary


def _write_full_bars(out_dir: Path, instrument: str, threshold_label: str, bars: list[Any]) -> None:
    """Write the full generated bars to a GITIGNORED full_bars/ CSV (local only)."""
    full_dir = out_dir / "full_bars"
    full_dir.mkdir(parents=True, exist_ok=True)
    path = full_dir / f"{instrument}_{threshold_label}.csv"
    if not bars:
        path.write_text("", encoding="utf-8")
        return
    fields = list(vars(bars[0]).keys())
    lines = [",".join(fields)]
    for bar in bars:
        values = vars(bar)
        lines.append(",".join(str(values[f]) for f in fields))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=UTC)


def main(argv: list[str] | None = None) -> int:
    bootstrap_environ()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bar-type", choices=["range", "volatility"], required=True)
    parser.add_argument("--pairs", nargs="+", default=list(MAJOR_PAIRS))
    parser.add_argument("--thresholds", nargs="+", type=float, required=True)
    parser.add_argument(
        "--method",
        choices=["abs_close", "true_range"],
        default="abs_close",
        help="volatility movement proxy (ignored for range bars)",
    )
    parser.add_argument("--price-basis", choices=["bid", "ask", "mid"], default="mid")
    parser.add_argument("--from", dest="from_date", type=_parse_date, default=None)
    parser.add_argument("--to", dest="to_date", type=_parse_date, default=None)
    parser.add_argument("--chunk-days", type=int, default=30)
    parser.add_argument("--max-rows", type=int, default=None, help="cap M1 rows per pair (smoke)")
    parser.add_argument("--run-label", default=None, help="output subdir under research/non_time_bars/")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--save-full-bars",
        action="store_true",
        help="also write full generated bars to a gitignored full_bars/ CSV (local only)",
    )
    args = parser.parse_args(argv)

    unknown = [p for p in args.pairs if p not in MAJOR_PAIRS]
    if unknown:
        parser.error(f"unknown pair(s) {unknown}; valid: {list(MAJOR_PAIRS)}")

    run_label = args.run_label or f"{args.bar_type}_{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
    out_dir = args.output_dir / run_label
    out_dir.mkdir(parents=True, exist_ok=True)

    store = PostgresCandleStore(get_research_database_config())
    t0 = time.time()

    manifest: dict[str, Any] = {
        "sprint": "infra-range-and-volatility-bars-001",
        "bar_type": args.bar_type,
        "method": args.method if args.bar_type == "volatility" else None,
        "price_basis": args.price_basis,
        "thresholds": args.thresholds,
        "pairs": args.pairs,
        "chunk_days": args.chunk_days,
        "max_rows": args.max_rows,
        "started_at_utc": datetime.now(UTC).isoformat(),
        "source": "local Postgres M1 (granularity=M1); NO broker/network calls",
        "network_or_broker_calls": False,
        "strategy_evidence": False,
        "not_approved": True,
        "pair_results": {},
    }

    for instrument in args.pairs:
        pr = pair_range(store, instrument)
        from_utc = args.from_date or pr.start_utc
        to_utc = args.to_date or pr.end_utc
        manifest["pair_results"][instrument] = {
            "window": {"from_utc": from_utc.isoformat(), "to_utc": to_utc.isoformat()},
            "thresholds": {},
        }
        pair_summary: dict[str, Any] = {
            "instrument": instrument,
            "bar_type": args.bar_type,
            "window": {"from_utc": from_utc.isoformat(), "to_utc": to_utc.isoformat()},
            "thresholds": {},
        }
        for threshold in args.thresholds:
            summary = run_pair(
                store,
                instrument,
                bar_type=args.bar_type,
                threshold=threshold,
                method=args.method,
                price_basis=args.price_basis,
                from_utc=from_utc,
                to_utc=to_utc,
                chunk_days=args.chunk_days,
                max_rows=args.max_rows,
                out_dir=out_dir,
                save_full_bars=args.save_full_bars,
            )
            label = summary["threshold"]
            pair_summary["thresholds"][label] = summary
            manifest["pair_results"][instrument]["thresholds"][label] = {
                "bar_count": summary["bar_count"],
                "compression_vs_m1": summary["compression_vs_m1"],
                "compression_vs_m15_approx": summary["compression_vs_m15_approx"],
                "median_source_m1_rows_per_bar": summary["source_m1_rows_per_bar"]["median"],
                "warnings": summary["data_quality_warnings"],
            }
            print(
                f"{instrument} {args.bar_type} {label}: "
                f"{summary['bar_count']} bars, compression x{summary['compression_vs_m1']} vs M1"
            )
        (out_dir / f"{instrument}_{args.bar_type}_summary.json").write_text(
            json.dumps(pair_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    manifest["elapsed_seconds"] = round(time.time() - t0, 1)
    manifest["finished_at_utc"] = datetime.now(UTC).isoformat()
    (out_dir / f"{args.bar_type}_diagnostics_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"\nwrote compact summaries to {out_dir.relative_to(ROOT)} (elapsed {manifest['elapsed_seconds']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

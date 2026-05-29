"""CAMPAIGN_029 preflight — characterise USD_JPY 10-pip range bars (NO evidence).

Loads canonical USD_JPY M1 from the local Postgres research store, folds it into
10-pip range bars with the merged ``non_time_bars`` builder, and writes **compact
diagnostics only** (no signals, no trades, no P&L). This mirrors the already
committed non-time-bar full-corpus diagnostics: it characterises the *bar stream*
so the future execution sprint knows what it is trading on.

It NEVER:
  * approves anything / opens the test lockbox / produces a recommendation,
  * calls a broker / OANDA / network endpoint (local Postgres only),
  * commits full generated bars (those go to a GITIGNORED ``full_bars/`` and the
    script verifies they are git-ignored before exiting).

Compact outputs land under ``research/campaign_029/preflight/`` (whitelisted in
.gitignore): ``USD_JPY_range_10pip_diagnostics.json`` (+ ``.md``) and a manifest.

Usage (worktree needs ``PYTHONPATH=$PWD/src:$PWD``)::

    python scripts/preflight_campaign_029_usdjpy_range_bars.py
    python scripts/preflight_campaign_029_usdjpy_range_bars.py --max-rows 200000  # smoke
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

from forex_bot.data.m1_corpus_validation import _row_to_candle, iter_m1_chunks, pair_range
from forex_bot.data.non_time_bars import RangeBar, RangeBarConfig, stream_range_bars
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ

INSTRUMENT = "USD_JPY"
THRESHOLD_PIPS = 10.0
DEFAULT_OUTPUT_DIR = ROOT / "research" / "campaign_029" / "preflight"
GAP_SECONDS = 24 * 3600  # a bar spanning > 1 day flags a weekend/holiday gap

# Non-overlapping UTC session buckets (documented in the output). FX trades
# ~Sun 21:00 → Fri 21:00 UTC; weekend-gap-spanning bars surface in elapsed_time.
_SESSION_BUCKETS = (
    ("tokyo", 0, 7),
    ("london", 7, 12),
    ("london_ny_overlap", 12, 16),
    ("new_york", 16, 21),
    ("pacific", 21, 24),
)
_WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


# --------------------------------------------------------------------------- #
# Pure helpers (no I/O — safe to unit test)
# --------------------------------------------------------------------------- #
def session_bucket(dt: datetime) -> str:
    hour = dt.astimezone(UTC).hour
    for name, lo, hi in _SESSION_BUCKETS:
        if lo <= hour < hi:
            return name
    return "pacific"  # hour == 24 never occurs; defensive


def percentiles(values: list[float], points: tuple[float, ...]) -> dict[str, float]:
    """Inclusive linear-interpolation percentiles; ``{}`` for empty input."""
    if not values:
        return {}
    ordered = sorted(values)
    n = len(ordered)
    out: dict[str, float] = {}
    for p in points:
        if n == 1:
            out[f"p{p:g}"] = float(ordered[0])
            continue
        rank = (p / 100.0) * (n - 1)
        lo = int(rank)
        hi = min(lo + 1, n - 1)
        frac = rank - lo
        out[f"p{p:g}"] = float(ordered[lo] + (ordered[hi] - ordered[lo]) * frac)
    return out


def check_no_lookahead(bar: RangeBar, prev: RangeBar | None) -> list[str]:
    """Per-bar structural invariants that would break if a bar saw the future.

    Returns a list of violation strings (empty == clean).
    """
    errs: list[str] = []
    if bar.open_time != bar.source_start_time:
        errs.append(f"open_time {bar.open_time} != source_start_time {bar.source_start_time}")
    if bar.close_time != bar.source_end_time:
        errs.append(f"close_time {bar.close_time} != source_end_time {bar.source_end_time}")
    if bar.open_time > bar.close_time:
        errs.append(f"open_time {bar.open_time} after close_time {bar.close_time}")
    if not bar.incomplete:
        # a completed bar must actually have reached the threshold
        span_pips = max(
            (bar.high - bar.open), (bar.open - bar.low)
        ) / 0.01  # USD_JPY pip
        if span_pips + 1e-9 < bar.threshold_pips:
            errs.append(f"completed bar span {span_pips:.4f}pip < threshold {bar.threshold_pips}")
        if bar.thresholds_crossed < 1:
            errs.append(f"completed bar thresholds_crossed {bar.thresholds_crossed} < 1")
    if prev is not None:
        # the next bar opens strictly after the prior bar closed (row R+1)
        if bar.open_time <= prev.close_time:
            errs.append(f"open_time {bar.open_time} not after prior close_time {prev.close_time}")
    return errs


# --------------------------------------------------------------------------- #
# M1 streaming (dedupe chunk-boundary overlap, same as the diagnostics script)
# --------------------------------------------------------------------------- #
def _m1_candles(
    store: PostgresCandleStore,
    *,
    from_utc: datetime,
    to_utc: datetime,
    chunk_days: int,
    max_rows: int | None,
) -> Any:
    emitted = 0
    last_time: datetime | None = None
    for chunk in iter_m1_chunks(
        store, instrument=INSTRUMENT, start_utc=from_utc, end_utc=to_utc, chunk_days=chunk_days
    ):
        for row in chunk:
            candle = _row_to_candle(row, instrument=INSTRUMENT)
            if last_time is not None and candle.time == last_time:
                continue  # inclusive chunk-edge overlap
            last_time = candle.time
            yield candle
            emitted += 1
            if max_rows is not None and emitted >= max_rows:
                return


# --------------------------------------------------------------------------- #
# Diagnostics fold (streaming; holds per-bar scalars only)
# --------------------------------------------------------------------------- #
def build_diagnostics(
    store: PostgresCandleStore,
    *,
    from_utc: datetime,
    to_utc: datetime,
    chunk_days: int,
    max_rows: int | None,
    save_full_bars: bool,
    out_dir: Path,
) -> dict[str, Any]:
    cfg = RangeBarConfig(
        instrument=INSTRUMENT,
        threshold_pips=THRESHOLD_PIPS,
        price_basis="mid",
        emit_incomplete_final=True,  # so we can COUNT the trailing incomplete bar
        require_sorted=True,
        duplicate_policy="reject",
    )

    m1_count = 0
    bar_count = 0
    incomplete_final = 0
    multi_threshold = 0
    first_time: datetime | None = None
    last_time: datetime | None = None
    source_counts: list[int] = []
    elapsed_seconds: list[float] = []
    overshoots: list[float] = []
    gap_spanning = 0
    sessions: Counter[str] = Counter()
    weekdays: Counter[str] = Counter()
    completion_reasons: Counter[str] = Counter()
    lookahead_violations: list[str] = []

    full_rows: list[RangeBar] = []

    # We count M1 rows by tapping the generator.
    def _counting(gen: Any) -> Any:
        nonlocal m1_count
        for c in gen:
            m1_count += 1
            yield c

    prev: RangeBar | None = None
    src = _counting(
        _m1_candles(store, from_utc=from_utc, to_utc=to_utc, chunk_days=chunk_days, max_rows=max_rows)
    )
    for bar in stream_range_bars(src, cfg):
        bar_count += 1
        if first_time is None:
            first_time = bar.open_time
        last_time = bar.close_time
        if bar.incomplete:
            incomplete_final += 1
        else:
            if bar.thresholds_crossed > 1:
                multi_threshold += 1
            overshoots.append(float(bar.overshoot_pips))
        source_counts.append(int(bar.source_count))
        elapsed = (bar.close_time - bar.open_time).total_seconds()
        elapsed_seconds.append(elapsed)
        if elapsed > GAP_SECONDS:
            gap_spanning += 1
        sessions[session_bucket(bar.close_time)] += 1
        weekdays[_WEEKDAYS[bar.close_time.astimezone(UTC).weekday()]] += 1
        completion_reasons[bar.completion_reason] += 1
        if len(lookahead_violations) < 50:
            lookahead_violations.extend(check_no_lookahead(bar, prev))
        prev = bar
        if save_full_bars:
            full_rows.append(bar)

    if save_full_bars:
        _write_full_bars(out_dir, full_rows)

    completed = bar_count - incomplete_final
    diag: dict[str, Any] = {
        "campaign": "CAMPAIGN_029",
        "strategy_family": "usdjpy_range_bar_mtf_breakout",
        "purpose": "range-bar STREAM characterisation (NO signals/trades/PnL)",
        "instrument": INSTRUMENT,
        "bar_type": "range",
        "threshold_pips": THRESHOLD_PIPS,
        "price_basis": "mid",
        "source": "local Postgres M1 (granularity=M1); NO broker/network calls",
        "window": {"from": _iso(from_utc), "to": _iso(to_utc), "max_rows": max_rows},
        "m1_rows_consumed": m1_count,
        "bar_count_total": bar_count,
        "bar_count_completed": completed,
        "incomplete_final_bar_count": incomplete_final,
        "first_bar_open_time": _iso(first_time),
        "last_bar_close_time": _iso(last_time),
        "m1_rows_per_bar": {
            "mean": round(statistics.fmean(source_counts), 4) if source_counts else None,
            "median": statistics.median(source_counts) if source_counts else None,
            **percentiles([float(x) for x in source_counts], (10, 25, 50, 75, 90, 99)),
            "min": min(source_counts) if source_counts else None,
            "max": max(source_counts) if source_counts else None,
        },
        "elapsed_seconds_per_bar": {
            "mean": round(statistics.fmean(elapsed_seconds), 2) if elapsed_seconds else None,
            "median": statistics.median(elapsed_seconds) if elapsed_seconds else None,
            **percentiles(elapsed_seconds, (10, 25, 50, 75, 90, 99)),
            "max": max(elapsed_seconds) if elapsed_seconds else None,
            "gap_spanning_bars_gt_1d": gap_spanning,
        },
        "multi_threshold_crossing": {
            "count": multi_threshold,
            "rate_of_completed": round(multi_threshold / completed, 6) if completed else None,
            "note": "completed bars whose single closing M1 candle crossed >1 threshold",
        },
        "overshoot_pips": {
            "mean": round(statistics.fmean(overshoots), 4) if overshoots else None,
            "median": statistics.median(overshoots) if overshoots else None,
            **percentiles(overshoots, (50, 90, 99)),
            "max": max(overshoots) if overshoots else None,
        },
        "session_distribution_utc": dict(sessions),
        "session_bucket_definition_utc": {n: f"[{lo:02d}:00,{hi:02d}:00)" for n, lo, hi in _SESSION_BUCKETS},
        "weekday_distribution": {d: weekdays.get(d, 0) for d in _WEEKDAYS},
        "completion_reasons": dict(completion_reasons),
        "lookahead_check": {
            "violations_found": len(lookahead_violations),
            "examples": lookahead_violations[:10],
            "invariants": [
                "open_time == source_start_time",
                "close_time == source_end_time",
                "open_time <= close_time",
                "completed-bar span >= threshold and thresholds_crossed >= 1",
                "each bar opens strictly after the prior bar's close",
            ],
        },
        "full_bars_saved": save_full_bars,
    }
    return diag


def _write_full_bars(out_dir: Path, bars: list[RangeBar]) -> None:
    """Write full generated bars to a GITIGNORED full_bars/ CSV (local only)."""
    full_dir = out_dir / "full_bars"
    full_dir.mkdir(parents=True, exist_ok=True)
    path = full_dir / f"{INSTRUMENT}_range_10pip.csv"
    if not bars:
        path.write_text("", encoding="utf-8")
        return
    fields = list(vars(bars[0]).keys())
    lines = [",".join(fields)]
    for bar in bars:
        values = vars(bar)
        lines.append(",".join(str(values[f]) for f in fields))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_full_bars_gitignored(out_dir: Path) -> bool:
    """Assert the full_bars/ tree is git-ignored (so it can never be staged)."""
    full_dir = out_dir / "full_bars"
    if not full_dir.exists():
        return True
    probe = full_dir / f"{INSTRUMENT}_range_10pip.csv"
    result = subprocess.run(
        ["git", "check-ignore", "-q", str(probe)],
        cwd=ROOT,
        capture_output=True,
    )
    return result.returncode == 0  # 0 == path IS ignored


def _iso(value: datetime | None) -> str | None:
    return value.astimezone(UTC).isoformat() if value else None


def _render_markdown(diag: dict[str, Any]) -> str:
    lines = [
        "# CAMPAIGN_029 — USD_JPY 10-pip range-bar preflight diagnostics",
        "",
        "> Bar-stream characterisation only. **No signals, trades, or P&L.** "
        "Source: local Postgres M1. Full generated bars are local & gitignored.",
        "",
        f"- instrument: **{diag['instrument']}** · threshold: **{diag['threshold_pips']:g} pip** "
        f"· price basis: **{diag['price_basis']}**",
        f"- window: {diag['window']['from']} → {diag['window']['to']} "
        f"(max_rows={diag['window']['max_rows']})",
        f"- M1 rows consumed: **{diag['m1_rows_consumed']:,}**",
        f"- range bars: **{diag['bar_count_completed']:,} completed** "
        f"(+{diag['incomplete_final_bar_count']} incomplete final)",
        f"- first bar open: {diag['first_bar_open_time']}",
        f"- last bar close: {diag['last_bar_close_time']}",
        f"- M1 rows / bar: mean {diag['m1_rows_per_bar']['mean']}, "
        f"median {diag['m1_rows_per_bar']['median']}, max {diag['m1_rows_per_bar']['max']}",
        f"- elapsed sec / bar: median {diag['elapsed_seconds_per_bar']['median']}, "
        f"p99 {diag['elapsed_seconds_per_bar'].get('p99')}, "
        f"max {diag['elapsed_seconds_per_bar']['max']} "
        f"(gap-spanning >1d: {diag['elapsed_seconds_per_bar']['gap_spanning_bars_gt_1d']})",
        f"- multi-threshold crossing: {diag['multi_threshold_crossing']['count']} "
        f"(rate {diag['multi_threshold_crossing']['rate_of_completed']})",
        f"- overshoot pips: mean {diag['overshoot_pips']['mean']}, "
        f"p99 {diag['overshoot_pips'].get('p99')}, max {diag['overshoot_pips']['max']}",
        f"- session dist (UTC): {diag['session_distribution_utc']}",
        f"- weekday dist: {diag['weekday_distribution']}",
        f"- completion reasons: {diag['completion_reasons']}",
        f"- **lookahead violations: {diag['lookahead_check']['violations_found']}**",
        "",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from", dest="from_date", default=None, help="UTC ISO date (default: corpus start)")
    parser.add_argument("--to", dest="to_date", default=None, help="UTC ISO date (default: corpus end)")
    parser.add_argument("--chunk-days", type=int, default=14)
    parser.add_argument("--max-rows", type=int, default=None, help="cap M1 rows (smoke)")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--save-full-bars", action="store_true", help="write gitignored full bars locally")
    args = parser.parse_args(argv)

    bootstrap_environ()
    store = PostgresCandleStore(get_research_database_config())

    pr = pair_range(store, INSTRUMENT)
    from_utc = datetime.fromisoformat(args.from_date).replace(tzinfo=UTC) if args.from_date else pr.start_utc
    to_utc = datetime.fromisoformat(args.to_date).replace(tzinfo=UTC) if args.to_date else pr.end_utc

    args.out_dir.mkdir(parents=True, exist_ok=True)
    diag = build_diagnostics(
        store,
        from_utc=from_utc,
        to_utc=to_utc,
        chunk_days=args.chunk_days,
        max_rows=args.max_rows,
        save_full_bars=args.save_full_bars,
        out_dir=args.out_dir,
    )

    # Hard safety: full bars must be git-ignored; lookahead must be clean.
    ignored = verify_full_bars_gitignored(args.out_dir)
    diag["full_bars_gitignored_verified"] = ignored
    if not ignored:
        print("FATAL: full_bars/ is NOT git-ignored — refusing to leave it stageable", file=sys.stderr)
        return 2
    if diag["lookahead_check"]["violations_found"]:
        print(f"FATAL: {diag['lookahead_check']['violations_found']} lookahead violations", file=sys.stderr)
        return 3

    diag_path = args.out_dir / f"{INSTRUMENT}_range_10pip_diagnostics.json"
    md_path = args.out_dir / f"{INSTRUMENT}_range_10pip_diagnostics.md"
    manifest_path = args.out_dir / "preflight_manifest.json"
    diag_path.write_text(json.dumps(diag, indent=2, default=str) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(diag), encoding="utf-8")
    manifest_path.write_text(
        json.dumps(
            {
                "campaign": "CAMPAIGN_029",
                "kind": "range_bar_preflight",
                "instrument": INSTRUMENT,
                "threshold_pips": THRESHOLD_PIPS,
                "outputs": [diag_path.name, md_path.name],
                "evidence": False,
                "note": "characterisation only; no signals/trades/PnL; lockbox not opened",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {diag_path}")
    print(f"wrote {md_path}")
    print(f"wrote {manifest_path}")
    print(
        f"USD_JPY 10pip: {diag['bar_count_completed']:,} completed bars from "
        f"{diag['m1_rows_consumed']:,} M1 rows; lookahead violations="
        f"{diag['lookahead_check']['violations_found']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

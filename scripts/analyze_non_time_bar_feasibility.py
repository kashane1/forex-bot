"""Non-time-bar feasibility analyzer — driver script (diagnostic-only, research).

Streams the **local** M1 corpus (Postgres, no broker/network), folds range and
volatility bars across a fixed threshold grid using the existing, tested
``forex_bot.data.non_time_bars`` builders, estimates spread → round-trip cost from
the M1 bid/ask, and runs the pure economics/classification layer
(``forex_bot.research.non_time_bar_feasibility``) to label every
(pair, bar_type, threshold) cell.

It produces only **compact** diagnostics. It computes no strategy signals, no PnL,
no labelled returns — only market-microstructure geometry + cost — so the test
lockbox is untouched. Default window is the C029 train window
(2021-05-27 → 2023-12-31), entirely outside the lockbox.

Nothing here approves a strategy, tunes C029, creates a campaign, or touches
paper/demo/live. See docs/research/RANGE_VOLATILITY_BAR_FEASIBILITY_PROTOCOL.md.

Usage (full study, ~3 min on the local corpus):
    PYTHONPATH=$PWD/src:$PWD python scripts/analyze_non_time_bar_feasibility.py

Smoke (cap M1 rows per pair):
    ... python scripts/analyze_non_time_bar_feasibility.py --max-rows 50000 --pairs USD_JPY
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.m1_corpus_validation import (
    MAJOR_PAIRS,
    _row_to_candle,
    iter_m1_chunks,
    pair_range,
)
from forex_bot.data.non_time_bars import (
    RangeBarConfig,
    VolatilityBarConfig,
    build_range_bars,
    build_volatility_bars,
    pip_size,
)
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ
from forex_bot.research.non_time_bar_feasibility import (
    C029_AVG_RISK_PIPS,
    C029_COST_PIPS,
    C029_COST_TO_RISK,
    C029_GROSS_EDGE_R,
    C029_NET_EDGE_R,
    DEFAULT_SLIPPAGE_PIPS_PER_SIDE,
    LAB_ACHIEVABLE_GROSS_EDGE_R,
    FeasibilityCell,
    build_cell,
    cost_floor_row,
    summarize_feasibility,
)

DEFAULT_OUT_DIR = ROOT / "research" / "non_time_bar_feasibility"

# C029 train window — outside the test lockbox by construction.
DEFAULT_FROM = datetime(2021, 5, 27, tzinfo=UTC)
DEFAULT_TO = datetime(2023, 12, 31, 23, 59, tzinfo=UTC)

DEFAULT_RANGE_THRESHOLDS = (10.0, 15.0, 20.0, 25.0, 30.0)
DEFAULT_TR_THRESHOLDS = (20.0, 30.0, 40.0, 50.0)
DEFAULT_ABS_THRESHOLDS = (20.0, 30.0, 40.0, 50.0)


# --------------------------------------------------------------------------- #
# Pure helpers (unit-tested in tests/unit/test_non_time_bar_feasibility_driver.py)
# --------------------------------------------------------------------------- #


def session_bucket(hour: int) -> str:
    """FX session bucket by UTC hour (same partition as the diagnostics script)."""
    h = int(hour) % 24
    if h >= 21:
        return "rollover_late"
    if h < 7:
        return "tokyo"
    if h < 12:
        return "london"
    if h < 16:
        return "london_ny_overlap"
    return "new_york"


def spread_pips_from_candle(candle: Any, instrument: str) -> float | None:
    """Close-bar bid/ask spread in pips, or None when bid/ask is absent."""
    if candle.ask_c is None or candle.bid_c is None:
        return None
    spread_price = float(candle.ask_c) - float(candle.bid_c)
    if spread_price < 0:
        return None
    return spread_price / float(pip_size(instrument))


def window_days_from_span(first_utc: datetime, last_utc: datetime) -> float:
    """Calendar span of the data window in days (>= a tiny positive floor)."""
    seconds = (last_utc - first_utc).total_seconds()
    return max(seconds / 86_400.0, 1e-9)


def bar_geometry(bars: list[Any]) -> dict[str, Any]:
    """Compact geometry summary from a list of (completed-or-not) bars (pure)."""
    completed = [b for b in bars if not b.incomplete]
    n = len(completed)
    if n == 0:
        return {
            "bar_count": 0,
            "incomplete_final_bars": len(bars) - n,
            "median_minutes_per_bar": None,
            "avg_m1_rows_per_bar": None,
            "avg_overshoot_pips": None,
            "multi_threshold_rate": 0.0,
            "session_distribution": {},
            "weekday_distribution": {},
            "first_bar_close_utc": None,
            "last_bar_close_utc": None,
        }
    close_utc = [b.close_time.astimezone(UTC) for b in completed]
    minutes = [(b.close_time - b.open_time).total_seconds() / 60.0 for b in completed]
    source = [float(b.source_count) for b in completed]
    overshoot = [float(b.overshoot_pips) for b in completed]
    multi = sum(1 for b in completed if b.thresholds_crossed > 1)
    sessions: Counter[str] = Counter(session_bucket(ts.hour) for ts in close_utc)
    weekdays: Counter[str] = Counter(ts.strftime("%A") for ts in close_utc)
    return {
        "bar_count": n,
        "incomplete_final_bars": len(bars) - n,
        "median_minutes_per_bar": round(statistics.median(minutes), 3),
        "avg_m1_rows_per_bar": round(statistics.fmean(source), 3),
        "avg_overshoot_pips": round(statistics.fmean(overshoot), 4),
        "multi_threshold_rate": round(multi / n, 4),
        "session_distribution": dict(sorted(sessions.items())),
        "weekday_distribution": dict(sorted(weekdays.items())),
        "first_bar_close_utc": min(close_utc).isoformat(),
        "last_bar_close_utc": max(close_utc).isoformat(),
    }


# --------------------------------------------------------------------------- #
# Impure: stream one pair's M1 once, cache, accumulate spread.
# --------------------------------------------------------------------------- #


def load_pair_candles(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_utc: datetime,
    to_utc: datetime,
    chunk_days: int,
    max_rows: int | None,
) -> tuple[list[Any], dict[str, Any]]:
    """Stream M1 for one pair into a cached list; accumulate spread stats by session.

    Returns (candles, spread_stats). Peak memory holds one pair's M1 candles; the
    caller frees the list before the next pair.
    """
    candles: list[Any] = []
    spread_all: list[float] = []
    spread_by_session: dict[str, list[float]] = {}
    last_time: datetime | None = None
    for chunk in iter_m1_chunks(
        store, instrument=instrument, start_utc=from_utc, end_utc=to_utc, chunk_days=chunk_days
    ):
        for row in chunk:
            candle = _row_to_candle(row, instrument=instrument)
            if last_time is not None and candle.time == last_time:
                continue  # chunk-boundary overlap (corpus is duplicate-free)
            last_time = candle.time
            candles.append(candle)
            sp = spread_pips_from_candle(candle, instrument)
            if sp is not None:
                spread_all.append(sp)
                bucket = session_bucket(candle.time.astimezone(UTC).hour)
                spread_by_session.setdefault(bucket, []).append(sp)
            if max_rows is not None and len(candles) >= max_rows:
                break
        if max_rows is not None and len(candles) >= max_rows:
            break

    def _stats(values: list[float]) -> dict[str, float | None]:
        if not values:
            return {"mean": None, "median": None, "p25": None, "p75": None, "n": 0}
        ordered = sorted(values)
        q = statistics.quantiles(ordered, n=4) if len(ordered) >= 2 else [ordered[0]] * 3
        return {
            "mean": round(statistics.fmean(ordered), 4),
            "median": round(statistics.median(ordered), 4),
            "p25": round(q[0], 4),
            "p75": round(q[2], 4),
            "n": len(ordered),
        }

    spread_stats = {
        "overall": _stats(spread_all),
        "by_session": {k: _stats(v) for k, v in sorted(spread_by_session.items())},
    }
    return candles, spread_stats


def fold_cells_for_pair(
    instrument: str,
    candles: list[Any],
    *,
    range_thresholds: tuple[float, ...],
    tr_thresholds: tuple[float, ...],
    abs_thresholds: tuple[float, ...],
    price_basis: str,
    mean_spread_pips: float,
    slippage: float,
    window_days: float,
) -> tuple[list[FeasibilityCell], dict[str, Any]]:
    """Fold every grid cell for one pair; return analyzer cells + raw geometry."""
    cells: list[FeasibilityCell] = []
    geometry: dict[str, Any] = {}

    def _record(bar_type: str, method: str | None, threshold: float, bars: list[Any]) -> None:
        geo = bar_geometry(bars)
        label = (
            f"{threshold:g}pip" if bar_type == "range" else f"{method}_{threshold:g}pip"
        )
        geometry[label] = geo
        cell = build_cell(
            instrument=instrument,
            bar_type=bar_type,
            method=method,
            threshold_pips=threshold,
            bar_count=geo["bar_count"],
            window_days=window_days,
            spread_pips=mean_spread_pips,
            slippage_pips_per_side=slippage,
            multi_threshold_rate=geo["multi_threshold_rate"],
            median_minutes_per_bar=geo["median_minutes_per_bar"],
            avg_m1_rows_per_bar=geo["avg_m1_rows_per_bar"],
            avg_overshoot_pips=geo["avg_overshoot_pips"],
        )
        cells.append(cell)

    for thr in range_thresholds:
        bars = build_range_bars(
            candles, RangeBarConfig(instrument=instrument, threshold_pips=thr, price_basis=price_basis)
        )
        _record("range", None, thr, bars)
    for thr in tr_thresholds:
        bars = build_volatility_bars(
            candles,
            VolatilityBarConfig(
                instrument=instrument,
                method="true_range",
                threshold_mode="fixed",
                threshold_pips=thr,
                price_basis=price_basis,
            ),
        )
        _record("volatility", "true_range", thr, bars)
    for thr in abs_thresholds:
        bars = build_volatility_bars(
            candles,
            VolatilityBarConfig(
                instrument=instrument,
                method="abs_close",
                threshold_mode="fixed",
                threshold_pips=thr,
                price_basis=price_basis,
            ),
        )
        _record("volatility", "abs_close", thr, bars)

    return cells, geometry


# --------------------------------------------------------------------------- #
# Output writers
# --------------------------------------------------------------------------- #


def _matrix_rows(cells: list[FeasibilityCell]) -> list[dict[str, Any]]:
    rows = []
    for c in sorted(cells, key=lambda x: (x.instrument, x.bar_type, x.method or "", x.threshold_pips)):
        rows.append(
            {
                "instrument": c.instrument,
                "bar_type": c.bar_type,
                "method": c.method or "",
                "threshold_pips": c.threshold_pips,
                "bar_count": c.bar_count,
                "bars_per_year": c.per_year,
                "bars_per_day": c.per_day,
                "median_minutes_per_bar": c.median_minutes_per_bar,
                "avg_overshoot_pips": c.avg_overshoot_pips,
                "multi_threshold_rate": c.multi_threshold_rate,
                "spread_pips": c.spread_pips,
                "round_trip_cost_pips": c.round_trip_cost_pips,
                "cost_to_threshold": c.cost_to_threshold,
                "baseline_stop_pips": c.baseline_stop_pips,
                "cost_to_risk_baseline": c.cost_to_risk_baseline,
                "cost_to_risk_wide": c.cost_to_risk_wide,
                "min_gross_edge_baseline_r": c.min_gross_edge_baseline_r,
                "cadence_class": c.cadence_class,
                "label": c.label,
            }
        )
    return rows


def write_matrix_csv(path: Path, cells: list[FeasibilityCell]) -> None:
    rows = _matrix_rows(cells)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    header = list(rows[0].keys())
    lines = [",".join(header)]
    for r in rows:
        lines.append(",".join("" if r[h] is None else str(r[h]) for h in header))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(
    out_dir: Path,
    *,
    cells: list[FeasibilityCell],
    pair_detail: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = summarize_feasibility(cells)
    summary["window"] = manifest["window"]
    summary["c029_anchor"] = manifest["c029_anchor"]
    (out_dir / "feasibility_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    write_matrix_csv(out_dir / "feasibility_matrix.csv", cells)

    (out_dir / "pair_threshold_summary.json").write_text(
        json.dumps(pair_detail, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    cost_floor = {
        "c029_anchor": manifest["c029_anchor"],
        "rows": [
            cost_floor_row(c).as_dict()
            for c in sorted(
                cells, key=lambda x: (x.instrument, x.bar_type, x.method or "", x.threshold_pips)
            )
        ],
    }
    (out_dir / "cost_floor_summary.json").write_text(
        json.dumps(cost_floor, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    (out_dir / "feasibility_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    write_report(out_dir / "non_time_bar_feasibility_report.md", cells, manifest)


def write_report(path: Path, cells: list[FeasibilityCell], manifest: dict[str, Any]) -> None:
    from forex_bot.research.non_time_bar_feasibility import (
        compare_pair_vs_others,
        compare_range_vs_volatility,
        label_counts,
    )

    counts = label_counts(cells)
    rvv = compare_range_vs_volatility(cells)
    pvo = compare_pair_vs_others(cells, focus="USD_JPY") if any(
        c.instrument == "USD_JPY" for c in cells
    ) else {}

    lines = [
        "# Non-time-bar feasibility report (diagnostic-only)",
        "",
        f"**Sprint:** {manifest['sprint']}  ",
        f"**Window:** {manifest['window']['from_utc']} → {manifest['window']['to_utc']}  ",
        f"**Pairs:** {', '.join(manifest['pairs'])}  ",
        f"**Slippage:** {manifest['slippage_pips_per_side']} pip/side · "
        f"**price basis:** {manifest['price_basis']}  ",
        "",
        "> Diagnostic geometry + cost only. No signals, no PnL, no returns, no "
        "approval. Test lockbox untouched (window is the C029 train window). Labels "
        "are hypotheses about where it is worth looking, not gate passes.",
        "",
        "## C029 anchor",
        "",
        f"- 10-pip USD_JPY range: cost {C029_COST_PIPS} pips vs {C029_AVG_RISK_PIPS}-pip "
        f"risk → cost-to-risk {C029_COST_TO_RISK}; gross +{C029_GROSS_EDGE_R}R, net "
        f"{C029_NET_EDGE_R}R (cost-defeated).",
        f"- Lab achievable gross-edge benchmark: ~{LAB_ACHIEVABLE_GROSS_EDGE_R}R.",
        "",
        "## Label counts",
        "",
        "| label | n |",
        "|---|---:|",
    ]
    lines += [f"| {k} | {v} |" for k, v in counts.items()]
    lines += [
        "",
        "## Range vs volatility",
        "",
        "| bar_type | n | feasible | feasible_share | median cost/risk | min cost/risk |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for bt, d in rvv.items():
        if d.get("n_cells"):
            lines.append(
                f"| {bt} | {d['n_cells']} | {d['n_feasible']} | {d['feasible_share']} | "
                f"{d['median_cost_to_risk_baseline']} | {d['min_cost_to_risk_baseline']} |"
            )
    if pvo:
        lines += [
            "",
            "## USD_JPY vs other pairs (pooled)",
            "",
            "| group | n | median cost/risk | min cost/risk | feasible_share | mean spread |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for g, d in pvo.items():
            if d.get("n_cells"):
                lines.append(
                    f"| {g} | {d['n_cells']} | {d['median_cost_to_risk_baseline']} | "
                    f"{d['min_cost_to_risk_baseline']} | {d['feasible_share']} | "
                    f"{d['mean_spread_pips']} |"
                )

    lines += [
        "",
        "## Full matrix",
        "",
        "| pair | type | thr | bars/yr | med min | overshoot | cost p | cost/thr | "
        "stop p | cost/risk | label |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for c in sorted(cells, key=lambda x: (x.instrument, x.bar_type, x.method or "", x.threshold_pips)):
        thr = f"{c.threshold_pips:g}" + (f" {c.method}" if c.method else "")
        lines.append(
            f"| {c.instrument} | {c.bar_type} | {thr} | {c.per_year:g} | "
            f"{c.median_minutes_per_bar} | {c.avg_overshoot_pips} | "
            f"{c.round_trip_cost_pips} | {c.cost_to_threshold} | {c.baseline_stop_pips:g} | "
            f"{c.cost_to_risk_baseline} | {c.label} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=UTC)


def main(argv: list[str] | None = None) -> int:
    bootstrap_environ()
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--pairs", nargs="+", default=list(MAJOR_PAIRS))
    p.add_argument("--range-thresholds", nargs="+", type=float, default=list(DEFAULT_RANGE_THRESHOLDS))
    p.add_argument("--tr-thresholds", nargs="+", type=float, default=list(DEFAULT_TR_THRESHOLDS))
    p.add_argument("--abs-thresholds", nargs="+", type=float, default=list(DEFAULT_ABS_THRESHOLDS))
    p.add_argument("--from", dest="from_date", type=_parse_date, default=DEFAULT_FROM)
    p.add_argument("--to", dest="to_date", type=_parse_date, default=DEFAULT_TO)
    p.add_argument("--price-basis", choices=["bid", "ask", "mid"], default="mid")
    p.add_argument("--slippage", type=float, default=DEFAULT_SLIPPAGE_PIPS_PER_SIDE)
    p.add_argument("--chunk-days", type=int, default=30)
    p.add_argument("--max-rows", type=int, default=None, help="cap M1 rows per pair (smoke)")
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--run-label", default=None, help="subdir under out-dir (default: out-dir root)")
    args = p.parse_args(argv)

    unknown = [pair for pair in args.pairs if pair not in MAJOR_PAIRS]
    if unknown:
        p.error(f"unknown pair(s) {unknown}; valid: {list(MAJOR_PAIRS)}")

    out_dir = args.out_dir / args.run_label if args.run_label else args.out_dir
    store = PostgresCandleStore(get_research_database_config())
    t0 = time.time()

    all_cells: list[FeasibilityCell] = []
    pair_detail: dict[str, Any] = {}

    for instrument in args.pairs:
        pr = pair_range(store, instrument)
        from_utc = max(args.from_date, pr.start_utc)
        to_utc = min(args.to_date, pr.end_utc)
        candles, spread_stats = load_pair_candles(
            store,
            instrument,
            from_utc=from_utc,
            to_utc=to_utc,
            chunk_days=args.chunk_days,
            max_rows=args.max_rows,
        )
        if not candles:
            print(f"{instrument}: no M1 in window — skipped")
            continue
        win_days = window_days_from_span(candles[0].time, candles[-1].time)
        mean_spread = spread_stats["overall"]["mean"] or 0.0
        cells, geometry = fold_cells_for_pair(
            instrument,
            candles,
            range_thresholds=tuple(args.range_thresholds),
            tr_thresholds=tuple(args.tr_thresholds),
            abs_thresholds=tuple(args.abs_thresholds),
            price_basis=args.price_basis,
            mean_spread_pips=mean_spread,
            slippage=args.slippage,
            window_days=win_days,
        )
        all_cells.extend(cells)
        threshold_detail: dict[str, Any] = {}
        for c in cells:
            label = (
                f"{c.threshold_pips:g}pip"
                if c.method is None
                else f"{c.method}_{c.threshold_pips:g}pip"
            )
            threshold_detail[label] = {**geometry[label], "economics": c.as_dict()}
        pair_detail[instrument] = {
            "m1_rows": len(candles),
            "window_days": round(win_days, 2),
            "spread_pips": spread_stats,
            "thresholds": threshold_detail,
        }
        feasible = sum(1 for c in cells if c.label.startswith("FEASIBLE"))
        print(
            f"{instrument}: {len(candles)} M1 rows, spread~{mean_spread}p, "
            f"{len(cells)} cells, {feasible} feasible"
        )
        del candles  # free before next pair

    manifest: dict[str, Any] = {
        "sprint": "research-range-volatility-bar-feasibility-001",
        "kind": "diagnostic_feasibility",
        "window": {"from_utc": args.from_date.isoformat(), "to_utc": args.to_date.isoformat()},
        "pairs": args.pairs,
        "range_thresholds": args.range_thresholds,
        "tr_thresholds": args.tr_thresholds,
        "abs_thresholds": args.abs_thresholds,
        "price_basis": args.price_basis,
        "slippage_pips_per_side": args.slippage,
        "max_rows": args.max_rows,
        "source": "local Postgres M1 (granularity=M1); NO broker/network/OANDA calls",
        "network_or_broker_calls": False,
        "strategy_evidence": False,
        "computes_pnl_or_returns": False,
        "test_lockbox_touched": False,
        "not_approved": True,
        "c029_anchor": {
            "instrument": "USD_JPY",
            "threshold": "10pip range",
            "cost_pips": C029_COST_PIPS,
            "avg_risk_pips": C029_AVG_RISK_PIPS,
            "cost_to_risk": C029_COST_TO_RISK,
            "gross_edge_R": C029_GROSS_EDGE_R,
            "net_edge_R": C029_NET_EDGE_R,
            "lab_achievable_gross_edge_R": LAB_ACHIEVABLE_GROSS_EDGE_R,
        },
        "started_at_utc": datetime.now(UTC).isoformat(),
        "elapsed_seconds": round(time.time() - t0, 1),
    }

    write_outputs(out_dir, cells=all_cells, pair_detail=pair_detail, manifest=manifest)
    print(
        f"\nwrote compact feasibility diagnostics to {out_dir} "
        f"({len(all_cells)} cells, elapsed {manifest['elapsed_seconds']}s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

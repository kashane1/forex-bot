"""H16 overshoot-exhaustion fade — front-gate screen driver (diagnostic-only).

Streams the **local** M1 corpus (Postgres; no broker/network/OANDA), builds 30-pip
range bars via the existing ``forex_bot.data.non_time_bars`` builders, and **measures
conditional forward returns** after completions, bucketed by overshoot, on the C029
train window (lockbox untouched). It runs the pure
``forex_bot.research.overshoot_exhaustion_screen`` helpers and writes **compact**
diagnostics for Phases 2–5 of the screen.

This is a CONDITIONAL-DISTRIBUTION MEASUREMENT, not a strategy: no positions, stops,
sizing, PnL, equity, signals, train/val/test split, lockbox, or campaign. Nothing is
approved. See docs/research/H16_OVERSHOOT_EXHAUSTION_FRONTGATE_PLAN.md.

Usage:
    PYTHONPATH=$PWD/src:$PWD python scripts/screen_h16_overshoot_exhaustion.py
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.m1_corpus_validation import (
    _row_to_candle,
    iter_m1_chunks,
    pair_range,
)
from forex_bot.data.non_time_bars import RangeBarConfig, build_range_bars, pip_size
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ
from forex_bot.research.overshoot_exhaustion_screen import (
    BUCKET_NAMES,
    autocorr_lag1,
    bucket_label,
    bucket_stats,
    conditional_followon_rate,
    fade_returns,
    permutation_null_group_mean,
    quantile_edges,
    top_tail_threshold,
)

DEFAULT_OUT_DIR = ROOT / "research" / "h16_overshoot_frontgate"
DEFAULT_FROM = datetime(2021, 5, 27, tzinfo=UTC)
DEFAULT_TO = datetime(2023, 12, 31, 23, 59, tzinfo=UTC)
DEFAULT_PAIRS = ("USD_JPY", "EUR_USD", "GBP_USD")
THRESHOLD_PIPS = 30.0
HORIZONS = (1, 2, 3)
SLIPPAGE_PER_SIDE = 0.2
NULL_DRAWS = 2000
NULL_SEED = 20260529


def session_bucket(hour: int) -> str:
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


def _stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"mean": None, "median": None, "p25": None, "p75": None, "p95": None, "n": 0}
    ordered = sorted(values)
    q = statistics.quantiles(ordered, n=4) if len(ordered) >= 2 else [ordered[0]] * 3
    p95_idx = min(len(ordered) - 1, max(0, round(0.95 * len(ordered)) - 1))
    return {
        "mean": round(statistics.fmean(ordered), 4),
        "median": round(statistics.median(ordered), 4),
        "p25": round(q[0], 4),
        "p75": round(q[2], 4),
        "p95": round(ordered[p95_idx], 4),
        "n": len(ordered),
    }


def load_candles(store, instrument, *, from_utc, to_utc, chunk_days, max_rows):
    candles: list[Any] = []
    last_time = None
    for chunk in iter_m1_chunks(
        store, instrument=instrument, start_utc=from_utc, end_utc=to_utc, chunk_days=chunk_days
    ):
        for row in chunk:
            c = _row_to_candle(row, instrument=instrument)
            if last_time is not None and c.time == last_time:
                continue
            last_time = c.time
            candles.append(c)
            if max_rows is not None and len(candles) >= max_rows:
                return candles
    return candles


def spread_pips_at(candle: Any, psize: float) -> float | None:
    if candle.ask_c is None or candle.bid_c is None:
        return None
    sp = (float(candle.ask_c) - float(candle.bid_c)) / psize
    return sp if sp >= 0 else None


def build_events(candles: list[Any], instrument: str) -> dict[str, Any]:
    """Build the per-bar event arrays for one pair (overshoot, dir, mid-close, session,
    spread-at-completion). Pure-ish: depends only on the candle list + builders."""
    psize = float(pip_size(instrument))
    spread_by_time = {}
    for c in candles:
        sp = spread_pips_at(c, psize)
        if sp is not None:
            spread_by_time[c.time] = sp

    bars = build_range_bars(
        candles, RangeBarConfig(instrument=instrument, threshold_pips=THRESHOLD_PIPS, price_basis="mid")
    )
    completed = [b for b in bars if not b.incomplete]

    closes = [float(b.close) for b in completed]
    dirs = [1 if b.completion_reason == "range_up" else -1 for b in completed]
    overshoot = [float(b.overshoot_pips) for b in completed]
    sessions = [session_bucket(b.close_time.astimezone(UTC).hour) for b in completed]
    spreads = [spread_by_time.get(b.source_end_time) for b in completed]
    thresholds_crossed = [int(b.thresholds_crossed) for b in completed]
    return {
        "closes": closes,
        "dirs": dirs,
        "overshoot": overshoot,
        "sessions": sessions,
        "spreads": spreads,
        "thresholds_crossed": thresholds_crossed,
        "psize": psize,
        "n_bars": len(completed),
    }


def analyze_pair(instrument: str, ev: dict[str, Any]) -> dict[str, Any]:
    overshoot = ev["overshoot"]
    closes = ev["closes"]
    dirs = ev["dirs"]
    psize = ev["psize"]
    n = ev["n_bars"]

    edges = quantile_edges(overshoot)
    labels = [bucket_label(v, edges) for v in overshoot]
    tail_thr = top_tail_threshold(overshoot, frac=0.05)

    # Phase-2 distribution + clustering + session/spread association.
    by_session_overshoot: dict[str, list[float]] = defaultdict(list)
    by_session_spread: dict[str, list[float]] = defaultdict(list)
    for i in range(n):
        by_session_overshoot[ev["sessions"][i]].append(overshoot[i])
        if ev["spreads"][i] is not None:
            by_session_spread[ev["sessions"][i]].append(ev["spreads"][i])
    # spread by overshoot bucket (do big overshoots coincide with wide spread / news?)
    spread_by_bucket: dict[str, list[float]] = defaultdict(list)
    crossed_by_bucket: dict[str, list[int]] = defaultdict(list)
    for i in range(n):
        if ev["spreads"][i] is not None:
            spread_by_bucket[labels[i]].append(ev["spreads"][i])
        crossed_by_bucket[labels[i]].append(ev["thresholds_crossed"][i])

    distribution = {
        "instrument": instrument,
        "n_bars": n,
        "threshold_pips": THRESHOLD_PIPS,
        "overshoot_stats_pips": _stats(overshoot),
        "quartile_edges_pips": [round(e, 4) for e in edges],
        "top5pct_threshold_pips": round(tail_thr, 4),
        "overshoot_autocorr_lag1": autocorr_lag1(overshoot),
        "clustering_extreme": conditional_followon_rate(labels, ("extreme",)),
        "clustering_large_extreme": conditional_followon_rate(labels, ("large", "extreme")),
        "overshoot_by_session": {k: _stats(v) for k, v in sorted(by_session_overshoot.items())},
        "spread_by_session_pips": {k: _stats(v) for k, v in sorted(by_session_spread.items())},
        "spread_by_overshoot_bucket_pips": {
            k: _stats(spread_by_bucket.get(k, [])) for k in BUCKET_NAMES
        },
        "mean_thresholds_crossed_by_bucket": {
            k: (round(statistics.fmean(crossed_by_bucket[k]), 3) if crossed_by_bucket.get(k) else None)
            for k in BUCKET_NAMES
        },
        "session_distribution": dict(sorted(Counter(ev["sessions"]).items())),
    }

    # Phase-3 conditional behavior: fade stats by bucket × horizon (+ top-5% tail).
    behavior: dict[str, Any] = {"instrument": instrument, "horizons": {}}
    fades_by_h: dict[int, list[float | None]] = {}
    for k in HORIZONS:
        fades = fade_returns(closes, dirs, psize, k)
        fades_by_h[k] = fades
        per_bucket = {}
        for name in BUCKET_NAMES:
            vals = [fades[i] for i in range(n) if labels[i] == name and fades[i] is not None]
            per_bucket[name] = bucket_stats(vals).as_dict()
        tail_vals = [
            fades[i] for i in range(n) if overshoot[i] >= tail_thr and fades[i] is not None
        ]
        all_vals = [fades[i] for i in range(n) if fades[i] is not None]
        behavior["horizons"][str(k)] = {
            "by_bucket": per_bucket,
            "top5pct_tail": bucket_stats(tail_vals).as_dict(),
            "unconditional": bucket_stats(all_vals).as_dict(),
        }

    # Phase-4 cost: per-pair round-trip cost vs extreme/tail conditional move.
    pair_spreads = [s for s in ev["spreads"] if s is not None]
    mean_spread = statistics.fmean(pair_spreads) if pair_spreads else None
    rt_cost = (mean_spread + 2 * SLIPPAGE_PER_SIDE) if mean_spread is not None else None
    cost = {
        "instrument": instrument,
        "mean_spread_pips": round(mean_spread, 4) if mean_spread is not None else None,
        "round_trip_cost_pips": round(rt_cost, 4) if rt_cost is not None else None,
        "extreme_bucket_mean_fade_by_horizon": {
            str(k): behavior["horizons"][str(k)]["by_bucket"]["extreme"]["mean"] for k in HORIZONS
        },
        "top5pct_mean_fade_by_horizon": {
            str(k): behavior["horizons"][str(k)]["top5pct_tail"]["mean"] for k in HORIZONS
        },
        "extreme_exceeds_cost_by_horizon": {
            str(k): (
                behavior["horizons"][str(k)]["by_bucket"]["extreme"]["mean"] is not None
                and rt_cost is not None
                and behavior["horizons"][str(k)]["by_bucket"]["extreme"]["mean"] > rt_cost
            )
            for k in HORIZONS
        },
    }

    # Phase-5 null: permutation null for the extreme-bucket and large+extreme group means.
    null: dict[str, Any] = {"instrument": instrument, "horizons": {}}
    for k in HORIZONS:
        fades = fades_by_h[k]
        extreme_mask = [labels[i] == "extreme" for i in range(n)]
        large_mask = [labels[i] in ("large", "extreme") for i in range(n)]
        h_out = {}
        try:
            h_out["extreme"] = permutation_null_group_mean(
                fades, extreme_mask, draws=NULL_DRAWS, seed=NULL_SEED + k
            ).as_dict()
        except ValueError as exc:
            h_out["extreme"] = {"error": str(exc)}
        try:
            h_out["large_plus_extreme"] = permutation_null_group_mean(
                fades, large_mask, draws=NULL_DRAWS, seed=NULL_SEED + 100 + k
            ).as_dict()
        except ValueError as exc:
            h_out["large_plus_extreme"] = {"error": str(exc)}
        null["horizons"][str(k)] = h_out

    return {"distribution": distribution, "behavior": behavior, "cost": cost, "null": null}


def write_matrix_csv(path: Path, results: dict[str, Any]) -> None:
    header = [
        "instrument", "bucket", "horizon", "n", "mean_fade_pips", "median_fade_pips",
        "reversion_rate", "sem",
    ]
    lines = [",".join(header)]
    for instrument, res in results.items():
        for k in HORIZONS:
            hb = res["behavior"]["horizons"][str(k)]
            for name in (*BUCKET_NAMES, "top5pct_tail", "unconditional"):
                st = hb["by_bucket"][name] if name in BUCKET_NAMES else hb[name]
                lines.append(
                    ",".join(
                        str(x) if x is not None else ""
                        for x in [
                            instrument, name, k, st["n"], st["mean"], st["median"],
                            st["reversion_rate"], st["sem"],
                        ]
                    )
                )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    bootstrap_environ()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pairs", nargs="+", default=list(DEFAULT_PAIRS))
    p.add_argument("--from", dest="from_date", default=DEFAULT_FROM,
                   type=lambda s: datetime.fromisoformat(s).replace(tzinfo=UTC))
    p.add_argument("--to", dest="to_date", default=DEFAULT_TO,
                   type=lambda s: datetime.fromisoformat(s).replace(tzinfo=UTC))
    p.add_argument("--chunk-days", type=int, default=30)
    p.add_argument("--max-rows", type=int, default=None)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = p.parse_args(argv)

    store = PostgresCandleStore(get_research_database_config())
    t0 = time.time()
    results: dict[str, Any] = {}
    for instrument in args.pairs:
        pr = pair_range(store, instrument)
        from_utc = max(args.from_date, pr.start_utc)
        to_utc = min(args.to_date, pr.end_utc)
        candles = load_candles(
            store, instrument, from_utc=from_utc, to_utc=to_utc,
            chunk_days=args.chunk_days, max_rows=args.max_rows,
        )
        ev = build_events(candles, instrument)
        if ev["n_bars"] < 100:
            print(f"{instrument}: only {ev['n_bars']} bars — skipped")
            continue
        results[instrument] = analyze_pair(instrument, ev)
        extreme1 = results[instrument]["behavior"]["horizons"]["1"]["by_bucket"]["extreme"]
        print(
            f"{instrument}: {ev['n_bars']} bars, extreme-bucket h1 mean fade "
            f"{extreme1['mean']} pips (reversion rate {extreme1['reversion_rate']})"
        )
        del candles

    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "sprint": "research-non-time-bar-overshoot-frontgate-001",
        "kind": "front_gate_screen_conditional_distribution",
        "window": {"from_utc": args.from_date.isoformat(), "to_utc": args.to_date.isoformat()},
        "pairs": args.pairs,
        "threshold_pips": THRESHOLD_PIPS,
        "horizons": list(HORIZONS),
        "slippage_pips_per_side": SLIPPAGE_PER_SIDE,
        "null_draws": NULL_DRAWS,
        "null_seed": NULL_SEED,
        "source": "local Postgres M1; NO broker/network/OANDA",
        "computes_pnl_or_returns": "conditional forward returns only — NO positions/PnL/signals",
        "test_lockbox_touched": False,
        "is_campaign": False,
        "not_approved": True,
        "elapsed_seconds": round(time.time() - t0, 1),
    }
    out = args.out_dir
    (out / "distribution_study.json").write_text(
        json.dumps({k: v["distribution"] for k, v in results.items()}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    (out / "behavior_study.json").write_text(
        json.dumps({k: v["behavior"] for k, v in results.items()}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    (out / "cost_study.json").write_text(
        json.dumps({k: v["cost"] for k, v in results.items()}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    (out / "null_study.json").write_text(
        json.dumps({k: v["null"] for k, v in results.items()}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    (out / "h16_screen_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_matrix_csv(out / "h16_screen_matrix.csv", results)
    print(f"\nwrote compact H16 screen diagnostics to {out} (elapsed {manifest['elapsed_seconds']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

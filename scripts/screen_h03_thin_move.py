"""H03 thin-move fade — front-gate screen driver (diagnostic-only).

Streams the **local** M1 corpus (Postgres; no broker/network/OANDA), builds 30-pip
range bars via the existing ``forex_bot.data.non_time_bars`` builders, and **measures
conditional forward returns** after completions, bucketed by **participation
(tick-count volume)**, on the C029 train window (lockbox untouched). It runs the pure
``forex_bot.research.thin_move_screen`` helpers and writes **compact** diagnostics for
Phases 2–5 of the screen.

This is a CONDITIONAL-DISTRIBUTION MEASUREMENT, not a strategy: no positions, stops,
sizing, PnL, equity, signals, train/val/test split, lockbox, or campaign. Nothing is
approved. See docs/research/H03_THIN_MOVE_FRONTGATE_PLAN.md.

Usage:
    PYTHONPATH=$PWD/src:$PWD python scripts/screen_h03_thin_move.py
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
from forex_bot.research.thin_move_screen import (
    PARTICIPATION_BUCKETS,
    autocorr_lag1,
    bucket_stats,
    fade_returns,
    low_tail_threshold,
    participation_label,
    permutation_null_group_mean,
    tertile_edges,
)

DEFAULT_OUT_DIR = ROOT / "research" / "h03_thin_move_frontgate"
DEFAULT_FROM = datetime(2021, 5, 27, tzinfo=UTC)
DEFAULT_TO = datetime(2023, 12, 31, 23, 59, tzinfo=UTC)
DEFAULT_PAIRS = ("EUR_USD", "GBP_USD", "USD_JPY")
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
    """Per-bar event arrays for one pair: participation (volume), duration, dir,
    mid-close, overshoot, travel, session, spread-at-completion."""
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
    volume = [int(b.volume) for b in completed]
    duration = [int(b.source_count) for b in completed]  # M1 minutes to complete
    overshoot = [float(b.overshoot_pips) for b in completed]
    travel = [THRESHOLD_PIPS + float(b.overshoot_pips) for b in completed]
    sessions = [session_bucket(b.close_time.astimezone(UTC).hour) for b in completed]
    spreads = [spread_by_time.get(b.source_end_time) for b in completed]
    return {
        "closes": closes,
        "dirs": dirs,
        "volume": volume,
        "duration": duration,
        "overshoot": overshoot,
        "travel": travel,
        "sessions": sessions,
        "spreads": spreads,
        "psize": psize,
        "n_bars": len(completed),
    }


def analyze_pair(instrument: str, ev: dict[str, Any]) -> dict[str, Any]:
    volume = [float(v) for v in ev["volume"]]
    closes = ev["closes"]
    dirs = ev["dirs"]
    psize = ev["psize"]
    n = ev["n_bars"]

    edges = tertile_edges(volume)
    labels = [participation_label(v, edges) for v in volume]
    ultra_thr = low_tail_threshold(volume, frac=0.10)
    ultra_mask = [volume[i] <= ultra_thr for i in range(n)]

    # travel / volume ratio (thin-move metric); since travel ~fixed, monotone in 1/vol.
    tvr = [ev["travel"][i] / volume[i] if volume[i] > 0 else None for i in range(n)]

    # ---- Phase-2 distribution + confounds (overshoot/duration/spread/session vs vol) ----
    by_session_vol: dict[str, list[float]] = defaultdict(list)
    by_session_spread: dict[str, list[float]] = defaultdict(list)
    for i in range(n):
        by_session_vol[ev["sessions"][i]].append(volume[i])
        if ev["spreads"][i] is not None:
            by_session_spread[ev["sessions"][i]].append(ev["spreads"][i])

    overshoot_by_bucket: dict[str, list[float]] = defaultdict(list)
    duration_by_bucket: dict[str, list[float]] = defaultdict(list)
    spread_by_bucket: dict[str, list[float]] = defaultdict(list)
    vol_by_bucket: dict[str, list[float]] = defaultdict(list)
    session_by_bucket: dict[str, Counter] = defaultdict(Counter)
    for i in range(n):
        b = labels[i]
        overshoot_by_bucket[b].append(ev["overshoot"][i])
        duration_by_bucket[b].append(float(ev["duration"][i]))
        vol_by_bucket[b].append(volume[i])
        session_by_bucket[b][ev["sessions"][i]] += 1
        if ev["spreads"][i] is not None:
            spread_by_bucket[b].append(ev["spreads"][i])

    # ultra-thin confound snapshot
    ultra_overshoot = [ev["overshoot"][i] for i in range(n) if ultra_mask[i]]
    ultra_spread = [ev["spreads"][i] for i in range(n) if ultra_mask[i] and ev["spreads"][i] is not None]
    ultra_sessions = Counter(ev["sessions"][i] for i in range(n) if ultra_mask[i])

    distribution = {
        "instrument": instrument,
        "n_bars": n,
        "threshold_pips": THRESHOLD_PIPS,
        "volume_stats_ticks": _stats(volume),
        "tertile_edges_ticks": [round(e, 2) for e in edges],
        "ultra_thin_p10_threshold_ticks": round(ultra_thr, 2),
        "travel_per_volume_stats": _stats([x for x in tvr if x is not None]),
        "volume_autocorr_lag1": autocorr_lag1(volume),
        "duration_stats_minutes": _stats([float(d) for d in ev["duration"]]),
        "volume_by_session": {k: _stats(v) for k, v in sorted(by_session_vol.items())},
        "spread_by_session_pips": {k: _stats(v) for k, v in sorted(by_session_spread.items())},
        # confound: are thin (low-vol) bars systematically different?
        "volume_by_bucket_ticks": {k: _stats(vol_by_bucket.get(k, [])) for k in PARTICIPATION_BUCKETS},
        "overshoot_by_bucket_pips": {k: _stats(overshoot_by_bucket.get(k, [])) for k in PARTICIPATION_BUCKETS},
        "duration_by_bucket_minutes": {k: _stats(duration_by_bucket.get(k, [])) for k in PARTICIPATION_BUCKETS},
        "spread_by_bucket_pips": {k: _stats(spread_by_bucket.get(k, [])) for k in PARTICIPATION_BUCKETS},
        "session_distribution_by_bucket": {
            k: dict(sorted(session_by_bucket.get(k, Counter()).items())) for k in PARTICIPATION_BUCKETS
        },
        "ultra_thin_overshoot_pips": _stats(ultra_overshoot),
        "ultra_thin_spread_pips": _stats(ultra_spread),
        "ultra_thin_session_distribution": dict(sorted(ultra_sessions.items())),
        "session_distribution": dict(sorted(Counter(ev["sessions"]).items())),
    }

    # ---- Phase-3 conditional behavior: fade stats by participation bucket × horizon ----
    behavior: dict[str, Any] = {"instrument": instrument, "horizons": {}}
    fades_by_h: dict[int, list[float | None]] = {}
    for k in HORIZONS:
        fades = fade_returns(closes, dirs, psize, k)
        fades_by_h[k] = fades
        per_bucket = {}
        for name in PARTICIPATION_BUCKETS:
            vals = [fades[i] for i in range(n) if labels[i] == name and fades[i] is not None]
            per_bucket[name] = bucket_stats(vals).as_dict()
        ultra_vals = [fades[i] for i in range(n) if ultra_mask[i] and fades[i] is not None]
        all_vals = [fades[i] for i in range(n) if fades[i] is not None]
        low = per_bucket["low"]["mean"]
        high = per_bucket["high"]["mean"]
        behavior["horizons"][str(k)] = {
            "by_bucket": per_bucket,
            "ultra_thin_tail": bucket_stats(ultra_vals).as_dict(),
            "unconditional": bucket_stats(all_vals).as_dict(),
            # H03 gradient: thin should revert MORE than high participation (low - high > 0)
            "low_minus_high_mean": (round(low - high, 5) if (low is not None and high is not None) else None),
        }

    # ---- Phase-4 cost: per-pair round-trip cost vs low/ultra-thin conditional move ----
    pair_spreads = [s for s in ev["spreads"] if s is not None]
    mean_spread = statistics.fmean(pair_spreads) if pair_spreads else None
    rt_cost = (mean_spread + 2 * SLIPPAGE_PER_SIDE) if mean_spread is not None else None
    # thin-specific cost: thin bars may carry WIDER spreads -> use the low-bucket spread
    low_spreads = spread_by_bucket.get("low", [])
    low_mean_spread = statistics.fmean(low_spreads) if low_spreads else None
    low_rt_cost = (low_mean_spread + 2 * SLIPPAGE_PER_SIDE) if low_mean_spread is not None else None
    cost = {
        "instrument": instrument,
        "mean_spread_pips": round(mean_spread, 4) if mean_spread is not None else None,
        "round_trip_cost_pips": round(rt_cost, 4) if rt_cost is not None else None,
        "low_bucket_mean_spread_pips": round(low_mean_spread, 4) if low_mean_spread is not None else None,
        "low_bucket_round_trip_cost_pips": round(low_rt_cost, 4) if low_rt_cost is not None else None,
        "low_bucket_mean_fade_by_horizon": {
            str(k): behavior["horizons"][str(k)]["by_bucket"]["low"]["mean"] for k in HORIZONS
        },
        "ultra_thin_mean_fade_by_horizon": {
            str(k): behavior["horizons"][str(k)]["ultra_thin_tail"]["mean"] for k in HORIZONS
        },
        "low_exceeds_low_bucket_cost_by_horizon": {
            str(k): (
                behavior["horizons"][str(k)]["by_bucket"]["low"]["mean"] is not None
                and low_rt_cost is not None
                and behavior["horizons"][str(k)]["by_bucket"]["low"]["mean"] > low_rt_cost
            )
            for k in HORIZONS
        },
        "ultra_thin_exceeds_low_bucket_cost_by_horizon": {
            str(k): (
                behavior["horizons"][str(k)]["ultra_thin_tail"]["mean"] is not None
                and low_rt_cost is not None
                and behavior["horizons"][str(k)]["ultra_thin_tail"]["mean"] > low_rt_cost
            )
            for k in HORIZONS
        },
    }

    # ---- Phase-5 null: permutation null for the low-participation & ultra-thin group means ----
    null: dict[str, Any] = {"instrument": instrument, "horizons": {}}
    for k in HORIZONS:
        fades = fades_by_h[k]
        low_mask = [labels[i] == "low" for i in range(n)]
        h_out = {}
        try:
            h_out["low"] = permutation_null_group_mean(
                fades, low_mask, draws=NULL_DRAWS, seed=NULL_SEED + k
            ).as_dict()
        except ValueError as exc:
            h_out["low"] = {"error": str(exc)}
        try:
            h_out["ultra_thin"] = permutation_null_group_mean(
                fades, ultra_mask, draws=NULL_DRAWS, seed=NULL_SEED + 100 + k
            ).as_dict()
        except ValueError as exc:
            h_out["ultra_thin"] = {"error": str(exc)}
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
            for name in (*PARTICIPATION_BUCKETS, "ultra_thin_tail", "unconditional"):
                st = hb["by_bucket"][name] if name in PARTICIPATION_BUCKETS else hb[name]
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
        h1 = results[instrument]["behavior"]["horizons"]["1"]
        low1 = h1["by_bucket"]["low"]
        high1 = h1["by_bucket"]["high"]
        print(
            f"{instrument}: {ev['n_bars']} bars | low-part h1 mean fade {low1['mean']} "
            f"(rev {low1['reversion_rate']}) vs high {high1['mean']} | low−high {h1['low_minus_high_mean']}"
        )
        del candles

    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "sprint": "research-non-time-bar-thin-move-frontgate-001",
        "hypothesis": "H03 thin-move fade (low participation -> reversion)",
        "kind": "front_gate_screen_conditional_distribution",
        "window": {"from_utc": args.from_date.isoformat(), "to_utc": args.to_date.isoformat()},
        "pairs": args.pairs,
        "threshold_pips": THRESHOLD_PIPS,
        "participation_metric": "per-bar tick-count volume (sum of constituent M1 volume)",
        "buckets": "per-pair tertiles low/medium/high + bottom-decile ultra_thin tail",
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
    (out / "h03_screen_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_matrix_csv(out / "h03_screen_matrix.csv", results)
    print(f"\nwrote compact H03 screen diagnostics to {out} (elapsed {manifest['elapsed_seconds']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Phase 3 — cheap forward-return signal probes for the front gate.

Builds a small set of signal-prototype ledgers from the local H4/H1 store and
measures, per prototype, signed forward log-returns over several horizons
(pre- and post-cost) against a timestamp-random same-pair null that preserves
each prototype's per-pair signal count and side composition. Uses realized
per-bar bid/ask spreads for the cost overlay.

This produces *signal diagnostics only* (protocol level 2): forward-return
information and a cheap random-timestamp comparison. It builds no executable
strategy, claims no edge, opens no test lockbox, and creates no campaign. The
compact per-prototype ledgers it writes feed the Phase 4 matched-null CLI.

Run:
    PYTHONPATH=$PWD/src python -m \
        research.edge_discovery.front_gate_idea_selection.run_signal_probes
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.data.db import Database  # noqa: E402
from forex_bot.data.repositories import CandleRepo  # noqa: E402
from research.cost_atlas.loader import candles_to_frame  # noqa: E402
from research.edge_discovery.costs import pip_value_for  # noqa: E402
from research.edge_discovery.matched_nulls import session_bucket_utc  # noqa: E402
from research.edge_discovery.real_data import SEVEN_MAJORS, resolve_h4_store_path  # noqa: E402

OUT_DIR = REPO_ROOT / "research" / "edge_discovery" / "front_gate_idea_selection"
LEDGER_DIR = OUT_DIR / "ledgers"  # reproducible local artifacts (gitignored)
HORIZONS = (1, 3, 6, 12, 24)
SEEDS = tuple(range(20))
SLIP_PIPS = 0.2
MIN_SIGNALS = 40  # below this a probe is flagged SPARSE
REP_HORIZON = 6  # representative horizon for by-pair / by-session tables


@dataclass
class PairData:
    instrument: str
    timeframe: str
    times: np.ndarray  # datetime64 index values
    mid: np.ndarray
    high: np.ndarray
    low: np.ndarray
    spread_px: np.ndarray
    pip: float
    pos_by_time: dict = field(default_factory=dict)


def _load_pairs(db_path: Path, timeframe: str) -> dict[str, PairData]:
    out: dict[str, PairData] = {}
    for inst in SEVEN_MAJORS:
        db = Database(db_path)
        try:
            candles, _ = CandleRepo(db).list_with_dedupe_stats(
                inst, timeframe, completed_only=True
            )
        finally:
            db.close()
        frame = candles_to_frame(candles)
        if frame.empty:
            continue
        times = frame.index.values
        out[inst] = PairData(
            instrument=inst,
            timeframe=timeframe,
            times=times,
            mid=frame["close"].to_numpy(float),
            high=frame["high"].to_numpy(float),
            low=frame["low"].to_numpy(float),
            spread_px=(frame["ask_c"] - frame["bid_c"]).clip(lower=0).to_numpy(float),
            pip=pip_value_for(inst),
            pos_by_time={t: i for i, t in enumerate(times)},
        )
    return out


# --------------------------------------------------------------------------
# Prototype signal generators — each returns rows of
# (instrument, entry_time, side, session, extra fields). No lookahead: every
# rolling statistic is shifted so the signal at bar i uses only bars <= i-1.
# --------------------------------------------------------------------------

def _frame_for(pd_obj: PairData) -> pd.DataFrame:
    return pd.DataFrame(
        {"mid": pd_obj.mid, "high": pd_obj.high, "low": pd_obj.low},
        index=pd.DatetimeIndex(pd_obj.times),
    )


def proto_zscore_reversion(pairs: dict[str, PairData], *, length: int = 20, z_thresh: float = 2.0) -> pd.DataFrame:
    rows = []
    for inst, pdat in pairs.items():
        f = _frame_for(pdat)
        ma = f["mid"].rolling(length).mean().shift(1)
        sd = f["mid"].rolling(length).std().shift(1)
        z = (f["mid"] - ma) / sd
        hit = z.abs() >= z_thresh
        for ts, zv in z[hit].items():
            if np.isnan(zv):
                continue
            rows.append({
                "instrument": inst, "entry_time": ts, "side": int(-np.sign(zv)),
                "session": session_bucket_utc(ts), "zscore": round(float(zv), 3),
            })
    return pd.DataFrame(rows)


def proto_failed_breakout_fade(pairs: dict[str, PairData], *, lookback: int = 20) -> pd.DataFrame:
    rows = []
    for inst, pdat in pairs.items():
        f = _frame_for(pdat)
        prior_max = f["high"].rolling(lookback).max().shift(1)
        prior_min = f["low"].rolling(lookback).min().shift(1)
        up_fail = (f["high"] > prior_max) & (f["mid"] < prior_max)   # poked high, closed back below -> fade short
        dn_fail = (f["low"] < prior_min) & (f["mid"] > prior_min)    # poked low, closed back above -> fade long
        for ts in f.index[up_fail.fillna(False)]:
            rows.append({"instrument": inst, "entry_time": ts, "side": -1,
                         "session": session_bucket_utc(ts), "dir": "up_fail"})
        for ts in f.index[dn_fail.fillna(False)]:
            rows.append({"instrument": inst, "entry_time": ts, "side": 1,
                         "session": session_bucket_utc(ts), "dir": "dn_fail"})
    return pd.DataFrame(rows)


def proto_asia_range_breakout(pairs: dict[str, PairData], *, asia_end_hour: int = 6,
                              london_end_hour: int = 12) -> pd.DataFrame:
    """H1 only. Asia range approximated as 00:00-06:00 UTC; first London-window
    (06:00-12:00) H1 close beyond that range is a breakout (continuation side).
    Approximation noted in the doc: the true Asia session also spans 22:00-24:00."""
    rows = []
    for inst, pdat in pairs.items():
        f = _frame_for(pdat)
        df = f.copy()
        df["date"] = df.index.date
        df["hour"] = df.index.hour
        for _, day in df.groupby("date"):
            asia = day[day["hour"] < asia_end_hour]
            lon = day[(day["hour"] >= asia_end_hour) & (day["hour"] < london_end_hour)]
            if len(asia) < 3 or lon.empty:
                continue
            hi, lo = asia["high"].max(), asia["low"].min()
            broke = None
            for ts, r in lon.iterrows():
                if r["mid"] > hi:
                    broke = (ts, 1)
                    break
                if r["mid"] < lo:
                    broke = (ts, -1)
                    break
            if broke:
                ts, side = broke
                rows.append({"instrument": inst, "entry_time": ts, "side": side,
                             "session": session_bucket_utc(ts), "range_pips": round(float(hi - lo) / pdat.pip, 1)})
    return pd.DataFrame(rows)


def proto_ny_open_continuation(pairs: dict[str, PairData], *, london_start: int = 7,
                               ny_open: int = 13) -> pd.DataFrame:
    """H1 only. At the NY-open bar (13:00 UTC), continue the prior London move
    (close@12:00 - close@07:00). Continuation side = sign(London move)."""
    rows = []
    for inst, pdat in pairs.items():
        f = _frame_for(pdat)
        df = f.copy()
        df["date"] = df.index.date
        df["hour"] = df.index.hour
        for _, day in df.groupby("date"):
            lon_start = day[day["hour"] == london_start]
            lon_end = day[day["hour"] == ny_open - 1]
            ny = day[day["hour"] == ny_open]
            if lon_start.empty or lon_end.empty or ny.empty:
                continue
            move = float(lon_end["mid"].iloc[0] - lon_start["mid"].iloc[0])
            if move == 0:
                continue
            ts = ny.index[0]
            rows.append({"instrument": inst, "entry_time": ts, "side": int(np.sign(move)),
                         "session": session_bucket_utc(ts), "london_move_pips": round(move / pdat.pip, 1)})
    return pd.DataFrame(rows)


def proto_vol_compression_expansion(pairs: dict[str, PairData], *, atr_len: int = 14,
                                    rank_window: int = 250, comp_pct: float = 0.20,
                                    box: int = 10) -> pd.DataFrame:
    """H4. After a compressed-ATR regime (trailing-window ATR percentile <= 20%),
    a break of the prior `box`-bar high/low triggers an expansion breakout. Tests
    whether the *direction* of the expansion carries information."""
    rows = []
    for inst, pdat in pairs.items():
        f = _frame_for(pdat)
        tr = pd.concat([
            (f["high"] - f["low"]),
            (f["high"] - f["mid"].shift(1)).abs(),
            (f["low"] - f["mid"].shift(1)).abs(),
        ], axis=1).max(axis=1)
        atr = tr.rolling(atr_len).mean()
        pct = atr.rolling(rank_window).apply(lambda a: (a[-1] >= a).mean(), raw=True).shift(1)
        prior_max = f["high"].rolling(box).max().shift(1)
        prior_min = f["low"].rolling(box).min().shift(1)
        compressed = pct <= comp_pct
        up = compressed & (f["mid"] > prior_max)
        dn = compressed & (f["mid"] < prior_min)
        for ts in f.index[up.fillna(False)]:
            rows.append({"instrument": inst, "entry_time": ts, "side": 1,
                         "session": session_bucket_utc(ts), "dir": "up"})
        for ts in f.index[dn.fillna(False)]:
            rows.append({"instrument": inst, "entry_time": ts, "side": -1,
                         "session": session_bucket_utc(ts), "dir": "dn"})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Forward-return + timestamp-random null engine
# --------------------------------------------------------------------------

def _signed_returns(pairs: dict[str, PairData], ledger: pd.DataFrame, horizon: int):
    """Return arrays of signed pre-cost and post-cost forward log-returns for the
    ledger at one horizon, plus per-row instrument for grouping."""
    pre, post, insts, sess = [], [], [], []
    for inst, g in ledger.groupby("instrument"):
        pdat = pairs.get(inst)
        if pdat is None:
            continue
        n = len(pdat.mid)
        slip_px = SLIP_PIPS * pdat.pip
        for _, r in g.iterrows():
            pos = pdat.pos_by_time.get(np.datetime64(r["entry_time"]))
            if pos is None or pos + horizon >= n:
                continue
            entry, exit_ = pdat.mid[pos], pdat.mid[pos + horizon]
            if entry <= 0 or exit_ <= 0:
                continue
            raw = np.log(exit_ / entry)
            signed = r["side"] * raw
            cost = (pdat.spread_px[pos] + 2 * slip_px) / entry
            pre.append(signed)
            post.append(signed - cost)
            insts.append(inst)
            sess.append(r["session"])
    return np.array(pre), np.array(post), np.array(insts), np.array(sess)


def _null_distribution(pairs: dict[str, PairData], ledger: pd.DataFrame, horizon: int):
    """Timestamp-random same-pair null: preserve each pair's signal count and
    side composition, redraw entry timestamps at random. Returns per-seed pooled
    post-cost means."""
    per_pair = {
        inst: (len(g), g["side"].to_numpy(int))
        for inst, g in ledger.groupby("instrument") if inst in pairs
    }
    seed_means = []
    warmup = 250
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        pooled = []
        for inst, (count, sides) in per_pair.items():
            pdat = pairs[inst]
            n = len(pdat.mid)
            hi = n - horizon
            if hi <= warmup or count == 0:
                continue
            slip_px = SLIP_PIPS * pdat.pip
            pos = rng.integers(warmup, hi, size=count)
            draw_sides = rng.choice(sides, size=count) if len(sides) else np.ones(count, int)
            entry = pdat.mid[pos]
            exit_ = pdat.mid[pos + horizon]
            raw = np.log(exit_ / entry)
            cost = (pdat.spread_px[pos] + 2 * slip_px) / entry
            pooled.append(draw_sides * raw - cost)
        if pooled:
            seed_means.append(float(np.concatenate(pooled).mean()))
    return np.array(seed_means)


def _probe_result(name: str, timeframe: str, pairs: dict[str, PairData], ledger: pd.DataFrame) -> dict:
    n_total = len(ledger)
    sparse = n_total < MIN_SIGNALS
    by_horizon = {}
    for h in HORIZONS:
        pre, post, insts, sess = _signed_returns(pairs, ledger, h)
        if len(post) == 0:
            by_horizon[str(h)] = {"n": 0, "flag": "NO_SAMPLE"}
            continue
        null = _null_distribution(pairs, ledger, h)
        strat_post = float(post.mean())
        null_mean = float(null.mean()) if len(null) else float("nan")
        null_std = float(null.std(ddof=1)) if len(null) > 1 else float("nan")
        prob_null_ge = float((null >= strat_post).mean()) if len(null) else float("nan")
        pctile = float((null < strat_post).mean() * 100) if len(null) else float("nan")
        effect = (strat_post - null_mean) / null_std if null_std and null_std > 0 else float("nan")
        by_horizon[str(h)] = {
            "n": len(post),
            "mean_fwd_logret_pre_cost": round(float(pre.mean()), 6),
            "mean_fwd_logret_post_cost": round(strat_post, 6),
            "hit_rate_post_cost": round(float((post > 0).mean()), 4),
            "null_mean_post_cost": round(null_mean, 6),
            "null_std": round(null_std, 6),
            "prob_null_ge_strategy": round(prob_null_ge, 4),
            "strategy_percentile_vs_null": round(pctile, 2),
            "effect_size_vs_null": round(effect, 3) if effect == effect else None,
        }
    # representative-horizon breakdowns
    pre, post, insts, sess = _signed_returns(pairs, ledger, REP_HORIZON)
    by_pair, by_session = [], []
    if len(post):
        dfp = pd.DataFrame({"instrument": insts, "session": sess, "post": post})
        for inst, g in dfp.groupby("instrument"):
            by_pair.append({"prototype": name, "instrument": inst, "n": len(g),
                            "mean_post_cost": round(float(g["post"].mean()), 6),
                            "hit_rate": round(float((g["post"] > 0).mean()), 4)})
        for s, g in dfp.groupby("session"):
            by_session.append({"prototype": name, "session": s, "n": len(g),
                               "mean_post_cost": round(float(g["post"].mean()), 6),
                               "hit_rate": round(float((g["post"] > 0).mean()), 4)})
    side_counts = ledger["side"].value_counts().to_dict() if not ledger.empty else {}
    return {
        "prototype": name,
        "timeframe": timeframe,
        "n_signals": n_total,
        "n_pairs": int(ledger["instrument"].nunique()) if not ledger.empty else 0,
        "side_counts": {str(k): int(v) for k, v in side_counts.items()},
        "sessions": ledger["session"].value_counts().to_dict() if not ledger.empty else {},
        "sparse": bool(sparse),
        "rep_horizon": REP_HORIZON,
        "by_horizon": by_horizon,
        "_by_pair": by_pair,
        "_by_session": by_session,
    }


def main() -> int:
    db_path = resolve_h4_store_path(REPO_ROOT)
    if db_path is None:
        print("BLOCKED: store not found.", file=sys.stderr)
        return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)

    h4 = _load_pairs(db_path, "H4")
    h1 = _load_pairs(db_path, "H1")

    skipped = []
    specs = [
        ("zscore_reversion_h4", "H4", h4, proto_zscore_reversion),
        ("failed_breakout_fade_h4", "H4", h4, proto_failed_breakout_fade),
        ("asia_range_breakout_h1", "H1", h1, proto_asia_range_breakout),
        ("ny_open_continuation_h1", "H1", h1, proto_ny_open_continuation),
        ("vol_compression_expansion_h4", "H4", h4, proto_vol_compression_expansion),
    ]
    results = []
    for name, tf, pairs, gen in specs:
        ledger = gen(pairs)
        if ledger.empty:
            skipped.append({"prototype": name, "reason": "no signals generated"})
            continue
        ledger = ledger.sort_values(["instrument", "entry_time"]).reset_index(drop=True)
        out = ledger.copy()
        out["entry_time"] = pd.DatetimeIndex(out["entry_time"]).strftime("%Y-%m-%dT%H:%M:%SZ")
        out.to_csv(LEDGER_DIR / f"{name}.csv", index=False)
        results.append(_probe_result(name, tf, pairs, ledger))

    # USD_JPY overlay on the cleanest reversion prototype
    jpy_ledger = proto_zscore_reversion({"USD_JPY": h4["USD_JPY"]})
    if not jpy_ledger.empty:
        jpy_ledger = jpy_ledger.sort_values("entry_time").reset_index(drop=True)
        out = jpy_ledger.copy()
        out["entry_time"] = pd.DatetimeIndex(out["entry_time"]).strftime("%Y-%m-%dT%H:%M:%SZ")
        out.to_csv(LEDGER_DIR / "zscore_reversion_h4_usdjpy.csv", index=False)
        results.append(_probe_result("zscore_reversion_h4_usdjpy", "H4",
                                     {"USD_JPY": h4["USD_JPY"]}, jpy_ledger))

    # assemble artifacts
    summary_rows, by_pair_rows, by_session_rows, fwd_json = [], [], [], {}
    for r in results:
        by_pair_rows.extend(r.pop("_by_pair"))
        by_session_rows.extend(r.pop("_by_session"))
        fwd_json[r["prototype"]] = r["by_horizon"]
        rep = r["by_horizon"].get(str(REP_HORIZON), {})
        summary_rows.append({
            "prototype": r["prototype"], "timeframe": r["timeframe"],
            "n_signals": r["n_signals"], "n_pairs": r["n_pairs"], "sparse": r["sparse"],
            f"mean_post_h{REP_HORIZON}": rep.get("mean_fwd_logret_post_cost"),
            f"null_mean_post_h{REP_HORIZON}": rep.get("null_mean_post_cost"),
            f"prob_null_ge_h{REP_HORIZON}": rep.get("prob_null_ge_strategy"),
            f"effect_size_h{REP_HORIZON}": rep.get("effect_size_vs_null"),
            f"hit_rate_h{REP_HORIZON}": rep.get("hit_rate_post_cost"),
        })
    pd.DataFrame(summary_rows).to_csv(OUT_DIR / "signal_probe_summary.csv", index=False)
    pd.DataFrame(by_pair_rows).to_csv(OUT_DIR / "signal_probe_by_pair.csv", index=False)
    pd.DataFrame(by_session_rows).to_csv(OUT_DIR / "signal_probe_by_session.csv", index=False)
    (OUT_DIR / "signal_probe_forward_returns.json").write_text(
        json.dumps({"strategy_evidence": False, "diagnostic_only": True,
                    "horizons": list(HORIZONS), "results": fwd_json}, indent=2) + "\n",
        encoding="utf-8")
    (OUT_DIR / "signal_probe_null_comparison.json").write_text(
        json.dumps({"strategy_evidence": False, "diagnostic_only": True,
                    "null_mode": "timestamp_random_same_pair (count+side preserved)",
                    "seeds": list(SEEDS),
                    "results": {r["prototype"]: r["by_horizon"] for r in results}},
                   indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "skipped_signal_probes.json").write_text(
        json.dumps({"diagnostic_only": True, "skipped": skipped,
                    "data_blocked": [
                        {"prototype": "carry_financing_swing",
                         "reason": "no local carry/swap-rate table; FRED has US leg only"},
                        {"prototype": "sub_hour_open_expansion",
                         "reason": "no local M1/M5/M15/M30 data to resolve the open bar"}]},
                   indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "signal_probe_meta.json").write_text(
        json.dumps({"generated_at_utc": datetime.now(tz=UTC).isoformat(),
                    "strategy_evidence": False, "diagnostic_only": True}, indent=2) + "\n",
        encoding="utf-8")

    print(pd.DataFrame(summary_rows).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

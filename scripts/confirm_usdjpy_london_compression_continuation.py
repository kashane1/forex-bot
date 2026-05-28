#!/usr/bin/env python3
"""Overfit-hardened confirmation of the USD_JPY London compression-continuation lead.

DIAGNOSTIC ONLY — counterfactual measurement, NOT a strategy, NOT a campaign, NOT a loop,
NO order placement, NO verdict change, NO approval. Implements the LOCKED definition in
``docs/research/USDJPY_LONDON_COMPRESSION_CONTINUATION_LOCKED_DEFINITION.md`` verbatim:

  * USD_JPY M15, LONDON session only, compressed state (>=3/4 percentile features <=0.20),
    first prior-16-bar-range break CONTINUATION, horizons h16 & h32, train+validation only.
  * Cost variants (round-trip pips): optimistic 2.2 / base 4.4 / conservative 5.8;
    whipsaw charges one extra round-trip.
  * Intrabar protective stops: none / 1.0x & 1.5x compressed-bar range / 1.0x ATR(14),
    adverse-first within the holding window (conservative).
  * Multiple-testing haircut: Bonferroni x12 (6 sessions x 2 horizons searched prior).

No threshold is tuned; no new session/horizon/cut/filter is searched. TEST sealed.

Outputs:
  research/usdjpy_london_compression_continuation/confirmation_summary.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ
from forex_bot.research.volatility_compression_expansion import (
    CompressionExpansionParams,
    compute_compression_features,
    session_bucket,
)
from forex_bot.strategies.indicators import atr as atr_indicator

INSTRUMENT = "USD_JPY"
PIP = 0.01
TRAIN_START = "2021-06-01"
VALIDATION_END = "2025-06-30"
TEST_LOCKBOX_START = "2025-07-01"
VAL_SPLIT = "2024-01-01"

OUT_DIR = ROOT / "research/usdjpy_london_compression_continuation"
OUT_JSON = OUT_DIR / "confirmation_summary.json"

PARAMS = CompressionExpansionParams()
PERCENTILE_FEATURES = ("range_pct", "atr_pct", "bandwidth_pct", "realized_vol_pct")
HORIZONS = (16, 32)
RANGE_LOOKBACK = PARAMS.range_lookback  # 16
COST_VARIANTS = {"optimistic": 2.2, "base": 4.4, "conservative": 5.8}
STOP_VARIANTS = ("none", "range_1.0x", "range_1.5x", "atr_1.0x")
N_PRIOR_CELLS = 12  # Bonferroni factor (6 sessions x 2 horizons)
MIN_TRADES_PER_SPLIT = 150


def _connect():
    bootstrap_environ()
    cfg = get_research_database_config()
    import psycopg

    conn = psycopg.connect(cfg.url, connect_timeout=15)
    conn.read_only = True
    return conn, cfg


def _load_m15(conn) -> pd.DataFrame:
    sql = """
        SELECT time_utc, bid_c, ask_c, mid_h, mid_l, mid_c
        FROM market_data.candles
        WHERE instrument = %s AND granularity = 'M15' AND complete
          AND time_utc >= %s AND time_utc < %s
        ORDER BY time_utc
    """
    with conn.cursor() as cur:
        cur.execute(sql, (INSTRUMENT, f"{TRAIN_START}T00:00:00+00:00",
                          f"{VALIDATION_END}T00:00:00+00:00"))
        rows = cur.fetchall()
        cols = [c.name for c in cur.description]
    df = pd.DataFrame(rows, columns=cols)
    df["time_utc"] = pd.to_datetime(df["time_utc"], utc=True)
    df = df.set_index("time_utc").sort_index()
    for c in ("bid_c", "ask_c", "mid_h", "mid_l", "mid_c"):
        df[c] = df[c].astype(float)
    return df


def _simulate_trades(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (London compressed decision bar, horizon): gross pips per stop variant."""
    comp = compute_compression_features(df, PARAMS)
    agree = sum((comp[f] <= PARAMS.primary_cut).astype(int) for f in PERCENTILE_FEATURES)
    compressed = (agree >= 3).to_numpy()
    sessions = np.array([session_bucket(t.to_pydatetime()) for t in df.index])
    is_london = sessions == "london"

    atr_px = atr_indicator(df["mid_h"], df["mid_l"], df["mid_c"], length=PARAMS.atr_len).to_numpy()
    prior_hi = df["mid_h"].rolling(RANGE_LOOKBACK).max().shift(1).to_numpy()
    prior_lo = df["mid_l"].rolling(RANGE_LOOKBACK).min().shift(1).to_numpy()
    highs = df["mid_h"].to_numpy()
    lows = df["mid_l"].to_numpy()
    closes = df["mid_c"].to_numpy()
    bar_range_px = (df["mid_h"] - df["mid_l"]).to_numpy()
    n = len(df)
    idx = df.index

    recs = []
    for i in range(n):
        if not (compressed[i] and is_london[i]):
            continue
        if np.isnan(prior_hi[i]) or np.isnan(prior_lo[i]) or np.isnan(atr_px[i]):
            continue
        phi, plo = prior_hi[i], prior_lo[i]
        for h in HORIZONS:
            if i + h >= n:
                continue
            # find first break (continuation direction = earlier break)
            first_up = first_dn = -1
            for j in range(i + 1, i + h + 1):
                if first_up < 0 and highs[j] > phi:
                    first_up = j
                if first_dn < 0 and lows[j] < plo:
                    first_dn = j
                if first_up >= 0 and first_dn >= 0:
                    break
            if first_up < 0 and first_dn < 0:
                continue  # no trade
            whipsaw = first_up >= 0 and first_dn >= 0
            if first_up >= 0 and (first_dn < 0 or first_up <= first_dn):
                direction, entry, jbreak = 1, phi, first_up
            else:
                direction, entry, jbreak = -1, plo, first_dn

            stop_dists = {
                "none": None,
                "range_1.0x": 1.0 * bar_range_px[i],
                "range_1.5x": 1.5 * bar_range_px[i],
                "atr_1.0x": 1.0 * atr_px[i],
            }
            row = {
                "t": idx[i], "horizon": h, "direction": direction, "whipsaw": whipsaw,
                "year": idx[i].year,
                "split": "train" if idx[i] < pd.Timestamp(VAL_SPLIT, tz="UTC") else "validation",
            }
            close_exit = closes[i + h]
            for sv, sd in stop_dists.items():
                if sd is None:
                    gross = (close_exit - entry) / PIP * direction
                else:
                    stop_level = entry - direction * sd
                    stopped = False
                    for j in range(jbreak, i + h + 1):
                        adverse = lows[j] if direction == 1 else highs[j]
                        if (direction == 1 and adverse <= stop_level) or (
                            direction == -1 and adverse >= stop_level):
                            stopped = True
                            break
                    gross = (-sd / PIP) if stopped else (close_exit - entry) / PIP * direction
                row[f"gross_{sv}"] = gross
            recs.append(row)

    return pd.DataFrame(recs)


def _two_sided_p(mean: float, std: float, n: int) -> float:
    if n < 2 or std == 0:
        return 1.0
    z = abs(mean) / (std / math.sqrt(n))
    return math.erfc(z / math.sqrt(2.0))  # normal two-sided


def _stats(net: pd.Series) -> dict:
    net = net.dropna()
    n = len(net)
    if n == 0:
        return {"n": 0}
    mean = float(net.mean())
    std = float(net.std(ddof=1)) if n > 1 else 0.0
    p = _two_sided_p(mean, std, n)
    # outlier sensitivity: drop top-5 by |pips|
    if n > 5:
        drop = net.reindex(net.abs().sort_values(ascending=False).index[5:])
        trimmed_mean = round(float(drop.mean()), 4)
    else:
        trimmed_mean = None
    return {
        "n": n,
        "mean_pips_net": round(mean, 4),
        "win_rate": round(float((net > 0).mean()), 4),
        "std_pips": round(std, 4),
        "t_stat": round(mean / (std / math.sqrt(n)), 4) if std else None,
        "p_two_sided": round(p, 6),
        "p_bonferroni_x12": round(min(1.0, p * N_PRIOR_CELLS), 6),
        "survives_haircut_p<0.05": bool(min(1.0, p * N_PRIOR_CELLS) < 0.05 and mean > 0),
        "trimmed_mean_drop_top5": trimmed_mean,
        "total_pips_net": round(float(net.sum()), 1),
    }


def main() -> int:
    conn, cfg = _connect()
    print(f"research DB: {cfg.redacted_url} (read-only)")
    try:
        df = _load_m15(conn)
    finally:
        conn.close()
    print(f"loaded {len(df):,} M15 bars")
    trades = _simulate_trades(df)
    print(f"London compressed continuation trades: {len(trades)}")

    result = {
        "_meta": {
            "kind": "london_compression_continuation_confirmation",
            "NOT_edge_claim": True,
            "NOT_strategy": True,
            "locked_def": "USDJPY M15 London-only compressed(>=3/4<=0.20) first-break continuation",
            "horizons": list(HORIZONS),
            "cost_variants_roundtrip_pips": COST_VARIANTS,
            "stop_variants": list(STOP_VARIANTS),
            "bonferroni_factor": N_PRIOR_CELLS,
            "min_trades_per_split": MIN_TRADES_PER_SPLIT,
            "test_lockbox_excluded": TEST_LOCKBOX_START,
            "stop_fill_rule": "adverse-first within holding window (conservative)",
        },
        "results": {},
        "per_year": {},
    }

    for h in HORIZONS:
        th = trades[trades["horizon"] == h]
        whip = th["whipsaw"].to_numpy()
        for sv in STOP_VARIANTS:
            gross = th[f"gross_{sv}"]
            for cv_name, cv in COST_VARIANTS.items():
                extra = np.where(whip, cv, 0.0)
                net = gross - cv - extra
                key = f"h{h}|stop={sv}|cost={cv_name}"
                result["results"][key] = {
                    "train": _stats(net[th["split"] == "train"]),
                    "validation": _stats(net[th["split"] == "validation"]),
                }

    # per-year robustness at base cost, no-stop and range_1.0x stop
    for h in HORIZONS:
        th = trades[trades["horizon"] == h]
        whip = th["whipsaw"].to_numpy()
        for sv in ("none", "range_1.0x"):
            net = th[f"gross_{sv}"] - COST_VARIANTS["base"] - np.where(whip, COST_VARIANTS["base"], 0.0)
            by_year = {}
            for yr, g in th.assign(net=net).groupby("year"):
                gg = g["net"].dropna()
                by_year[str(int(yr))] = {"n": len(gg),
                                         "mean_pips_net": round(float(gg.mean()), 4) if len(gg) else None,
                                         "split": g["split"].iloc[0]}
            result["per_year"][f"h{h}|stop={sv}|cost=base"] = by_year

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2, default=str))
    print(f"wrote {OUT_JSON} ({OUT_JSON.stat().st_size:,} B)")

    # console: the decision-relevant cells (base cost)
    print("\n=== base cost, per stop variant (train mean / val mean / val n / val bonf-p) ===")
    for h in HORIZONS:
        for sv in STOP_VARIANTS:
            r = result["results"][f"h{h}|stop={sv}|cost=base"]
            tr, va = r["train"], r["validation"]
            print(f" h{h} stop={sv:10s}: train {tr.get('mean_pips_net')} (n={tr.get('n')}) | "
                  f"val {va.get('mean_pips_net')} (n={va.get('n')}, bonfP={va.get('p_bonferroni_x12')}, "
                  f"haircut={va.get('survives_haircut_p<0.05')})")
    print("\n=== conservative cost, no-stop & range_1.0x (train/val mean) ===")
    for h in HORIZONS:
        for sv in ("none", "range_1.0x"):
            r = result["results"][f"h{h}|stop={sv}|cost=conservative"]
            print(f" h{h} stop={sv:10s}: train {r['train'].get('mean_pips_net')} | val {r['validation'].get('mean_pips_net')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

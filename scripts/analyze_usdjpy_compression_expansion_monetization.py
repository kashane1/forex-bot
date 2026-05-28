#!/usr/bin/env python3
"""Bounded, predeclared monetization diagnostic for USD_JPY post-compression states.

DIAGNOSTIC ONLY — counterfactual measurement, NOT a strategy, NOT a campaign, NOT a
loop, NO order placement, NO verdict change, NO approval.

Phase 3 found: compression → SMALLER absolute future range (vol clustering), direction
null, and only a mildly-elevated post-compression breakout follow-through. This script
steelmans the thesis by measuring per-trade expectancy (net of an optimistic round-trip
cost) for the structures the data actually suggests, on train AND validation:

  M1. Direction-agnostic straddle proxy (enter on first prior-range break, either side).
  M2. Breakout CONTINUATION (enter in the break direction, hold to horizon).
  M3. Fade the break (enter opposite the break, hold to horizon).
  M4. Session-specific continuation participation (M2 restricted to active sessions).
  M5. No-trade filter: fraction of compressed states that are cost-hostile.

Execution model (no lookahead): the decision bar ``i`` is a *completed* compressed M15
bar; the prior range is [rolling-low, rolling-high] over the lookback ending at ``i``;
we scan bars ``i+1 .. i+h`` for the first break of that range and enter AT the broken
level (a level fill is a neutral-to-slightly-optimistic proxy for next-bar-open). Exit
at the close of bar ``i+h``. PnL is in pips, minus a deliberately-optimistic round-trip
cost. Whipsaw (both sides break) charges the continuation/fade an extra round-trip.

Reads M15 read-only from the research DB. Train+validation only; TEST sealed.

Usage:
    python scripts/analyze_usdjpy_compression_expansion_monetization.py
"""

from __future__ import annotations

import json
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

INSTRUMENT = "USD_JPY"
PIP = 0.01
TRAIN_START = "2021-06-01"
VALIDATION_END = "2025-06-30"
TEST_LOCKBOX_START = "2025-07-01"
VAL_SPLIT = "2024-01-01"

OUT_DIR = ROOT / "research/usdjpy_vol_compression_expansion"
OUT_JSON = OUT_DIR / "monetization_diagnostic.json"

PARAMS = CompressionExpansionParams()
PERCENTILE_FEATURES = ("range_pct", "atr_pct", "bandwidth_pct", "realized_vol_pct")
HORIZONS = (16, 32)  # 4h, 8h — where the follow-through signal was clearest
ROUNDTRIP_COST_PIPS = 2 * 1.7 + 1.0  # optimistic: 4.4
ACTIVE_SESSIONS = {"london", "ny", "london_ny_overlap", "tokyo"}


def _connect():
    bootstrap_environ()
    cfg = get_research_database_config()
    import psycopg

    conn = psycopg.connect(cfg.url, connect_timeout=15)
    conn.read_only = True
    return conn, cfg


def _load_m15(conn) -> pd.DataFrame:
    sql = """
        SELECT time_utc, bid_c, ask_c, mid_o, mid_h, mid_l, mid_c
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
    for c in ("bid_c", "ask_c", "mid_o", "mid_h", "mid_l", "mid_c"):
        df[c] = df[c].astype(float)
    return df


def _simulate(df: pd.DataFrame, h: int) -> pd.DataFrame:
    """Per compressed decision bar, simulate first-break continuation & fade at horizon h.

    Returns a frame indexed by decision bar with columns: split, session, traded,
    direction, continuation_pips_net, fade_pips_net, whipsaw.
    """
    comp = compute_compression_features(df, PARAMS)
    agree = sum((comp[f] <= PARAMS.primary_cut).astype(int) for f in PERCENTILE_FEATURES)
    compressed = (agree >= 3).to_numpy()

    hi = df["mid_h"].rolling(PARAMS.range_lookback).max().shift(1).to_numpy()
    lo = df["mid_l"].rolling(PARAMS.range_lookback).min().shift(1).to_numpy()
    highs = df["mid_h"].to_numpy()
    lows = df["mid_l"].to_numpy()
    closes = df["mid_c"].to_numpy()
    n = len(df)
    idx = df.index

    recs = []
    for i in range(n):
        if not compressed[i] or np.isnan(hi[i]) or np.isnan(lo[i]):
            continue
        if i + h >= n:
            continue
        prior_hi, prior_lo = hi[i], lo[i]
        first_up = -1
        first_dn = -1
        for j in range(i + 1, i + h + 1):
            if first_up < 0 and highs[j] > prior_hi:
                first_up = j
            if first_dn < 0 and lows[j] < prior_lo:
                first_dn = j
            if first_up >= 0 and first_dn >= 0:
                break
        traded = first_up >= 0 or first_dn >= 0
        if not traded:
            recs.append((idx[i], False, 0, np.nan, np.nan, False))
            continue
        whipsaw = first_up >= 0 and first_dn >= 0
        # direction = the EARLIER break
        if first_up >= 0 and (first_dn < 0 or first_up <= first_dn):
            direction = 1
            entry = prior_hi
        else:
            direction = -1
            entry = prior_lo
        exit_px = closes[i + h]
        move_pips = (exit_px - entry) / PIP * direction
        extra = ROUNDTRIP_COST_PIPS if whipsaw else 0.0  # second leg cost on whipsaw
        cont_net = move_pips - ROUNDTRIP_COST_PIPS - extra
        fade_net = -move_pips - ROUNDTRIP_COST_PIPS - extra
        recs.append((idx[i], True, direction, cont_net, fade_net, whipsaw))

    out = pd.DataFrame(recs, columns=["t", "traded", "direction", "cont_net", "fade_net", "whipsaw"])
    out = out.set_index("t")
    out["split"] = np.where(out.index < pd.Timestamp(VAL_SPLIT, tz="UTC"), "train", "validation")
    out["session"] = [session_bucket(t.to_pydatetime()) for t in out.index]
    return out


def _stats(s: pd.Series) -> dict:
    s = s.dropna()
    if not len(s):
        return {"n": 0}
    return {
        "n": len(s),
        "mean_pips_net": round(float(s.mean()), 4),
        "median_pips_net": round(float(s.median()), 4),
        "win_rate": round(float((s > 0).mean()), 4),
        "total_pips_net": round(float(s.sum()), 1),
    }


def main() -> int:
    conn, cfg = _connect()
    print(f"research DB: {cfg.redacted_url} (read-only)")
    try:
        df = _load_m15(conn)
    finally:
        conn.close()
    print(f"loaded {len(df):,} M15 bars")

    result = {
        "_meta": {
            "kind": "vol_compression_expansion_monetization_diagnostic",
            "NOT_edge_claim": True,
            "NOT_strategy": True,
            "roundtrip_cost_pips_optimistic": ROUNDTRIP_COST_PIPS,
            "horizons": list(HORIZONS),
            "compressed_def": ">=3 of 4 percentile features <= 0.20",
            "execution": "enter at first prior-range break level in bars i+1..i+h; "
                         "exit at close[i+h]; whipsaw charges an extra round-trip",
            "test_lockbox_excluded": TEST_LOCKBOX_START,
        },
        "by_horizon": {},
    }

    for h in HORIZONS:
        sim = _simulate(df, h)
        traded = sim[sim["traded"]]
        block = {
            "n_compressed_decision_bars": len(sim),
            "n_traded": len(traded),
            "trade_participation": round(float(len(traded) / len(sim)), 4) if len(sim) else None,
            "whipsaw_rate_given_traded": round(float(traded["whipsaw"].mean()), 4) if len(traded) else None,
            "M2_continuation": {sp: _stats(traded.loc[traded["split"] == sp, "cont_net"])
                                for sp in ("train", "validation")},
            "M3_fade": {sp: _stats(traded.loc[traded["split"] == sp, "fade_net"])
                        for sp in ("train", "validation")},
            "M1_straddle_proxy": {
                # direction-agnostic: take the better of continuation/fade per trade is
                # hindsight; the honest straddle ~ continuation (you hold the triggered
                # side). Reported as continuation here; fade is its mirror.
                "note": "direction-agnostic straddle ≈ M2 continuation (triggered side held); "
                        "a true both-legs straddle pays >=2 costs and is strictly worse",
            },
            "M4_session_continuation_active_only": {
                sp: _stats(traded.loc[(traded["split"] == sp) & traded["session"].isin(ACTIVE_SESSIONS),
                                      "cont_net"])
                for sp in ("train", "validation")
            },
            "M2_continuation_by_session": {
                str(sess): {sp: _stats(g.loc[g["split"] == sp, "cont_net"])
                            for sp in ("train", "validation")}
                for sess, g in traded.groupby("session", observed=True)
            },
        }
        result["by_horizon"][f"h{h}"] = block

    # M5 no-trade filter: fraction of compressed states that are cost-hostile
    sim_any = _simulate(df, HORIZONS[0])
    hostile = ~sim_any["session"].isin(ACTIVE_SESSIONS)
    result["M5_no_trade_filter"] = {
        "cost_hostile_sessions": sorted(set(sim_any.loc[hostile, "session"])),
        "frac_compressed_in_hostile_sessions": round(float(hostile.mean()), 4),
        "note": "rollover/off_hours carry wider spread; excluding them is the adopted overlay",
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2, default=str))
    print(f"wrote {OUT_JSON} ({OUT_JSON.stat().st_size:,} B)")

    for h in HORIZONS:
        b = result["by_horizon"][f"h{h}"]
        print(f"\nh{h}: traded {b['n_traded']}/{b['n_compressed_decision_bars']} "
              f"(part={b['trade_participation']}, whipsaw={b['whipsaw_rate_given_traded']})")
        for m in ("M2_continuation", "M3_fade", "M4_session_continuation_active_only"):
            tr = b[m]["train"]
            va = b[m]["validation"]
            print(f"  {m:38s} train mean={tr.get('mean_pips_net')} wr={tr.get('win_rate')} n={tr.get('n')} "
                  f"| val mean={va.get('mean_pips_net')} wr={va.get('win_rate')} n={va.get('n')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

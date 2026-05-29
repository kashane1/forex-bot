#!/usr/bin/env python3
"""Build a read-only USD_JPY session / volatility / spread atlas.

This is a DESCRIPTIVE market-structure atlas, **not** an edge claim and **not** a
strategy. It reads materialized USD_JPY candles from the research Postgres DB
(``market_data.candles``) read-only and summarizes spread, volatility, directional
behavior and tradability by trading session, hour-of-day (NY + UTC), weekday and
volatility regime.

Sprint: external-thesis-sourcing-and-session-atlas-001 (Phase 2).

Hard constraints honored:
  * READ-ONLY: only SELECT queries are issued.
  * No strategy is implemented; no campaign is run; no verdict changes.
  * The 2025-07+ TEST window is a sealed lockbox and is EXCLUDED by default.
  * Credentials are never printed (only a redacted DB URL).
  * Only a compact JSON summary is written; no per-bar dumps are persisted.

Usage:
    python scripts/build_usdjpy_session_volatility_spread_atlas.py
    python scripts/build_usdjpy_session_volatility_spread_atlas.py --no-m1

Output:
    research/usdjpy_session_atlas/usdjpy_session_atlas_summary.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ

INSTRUMENT = "USD_JPY"
PIP = 0.01  # USD_JPY pip size

# C022 split convention. The TEST window (2025-07-01+) is a sealed lockbox and is
# NEVER part of this atlas.
TRAIN_START = "2021-06-01"
VALIDATION_END = "2025-06-30"
TEST_LOCKBOX_START = "2025-07-01"

OUT_DIR = ROOT / "research/usdjpy_session_atlas"
OUT_JSON = OUT_DIR / "usdjpy_session_atlas_summary.json"

# Forward-return / excursion horizons in M15 bars (15m, 1h, 2h, 4h).
FWD_HORIZONS = (1, 4, 8, 16)
EXCURSION_HORIZON = 16  # bars used for MFE/MAE-after-arbitrary-timestamp
RECENT_DIR_LOOKBACK = 4  # bars used to define "recent direction"
ATR_LEN = 14
VOL_PCTILE_WINDOW = 1920  # trailing M15 bars (~20 trading days) for rolling vol pct
BREAKOUT_LOOKBACK = 16  # bars defining the prior range for breakout/false-breakout
BREAKOUT_RESOLVE = 8  # bars allowed to confirm/fail a breakout

TZ_NY = ZoneInfo("America/New_York")
TZ_LON = ZoneInfo("Europe/London")
TZ_TOK = ZoneInfo("Asia/Tokyo")


# --------------------------------------------------------------------------- #
# Session classification (DST-correct via per-center local time)
# --------------------------------------------------------------------------- #
def _session_bucket(ts_utc: pd.Timestamp) -> str:
    """Assign one primary session bucket to a UTC timestamp.

    Windows are each center's local opening hours (DST handled by zoneinfo):
      Tokyo  09:00-15:00 JST   London 08:00-16:00 BST/GMT   NY 08:00-17:00 ET
    Priority: rollover > london_ny_overlap > ny > london > tokyo > off_hours.
    """
    ny = ts_utc.tz_convert(TZ_NY)
    lon = ts_utc.tz_convert(TZ_LON)
    tok = ts_utc.tz_convert(TZ_TOK)
    ny_active = 8 <= ny.hour < 17
    lon_active = 8 <= lon.hour < 16
    tok_active = 9 <= tok.hour < 15
    if ny.hour == 17:  # NY 17:00-18:00 ET ~ daily rollover / liquidity gap
        return "rollover"
    if lon_active and ny_active:
        return "london_ny_overlap"
    if ny_active:
        return "ny"
    if lon_active:
        return "london"
    if tok_active:
        return "tokyo"
    return "off_hours"


# --------------------------------------------------------------------------- #
# Data loading (read-only)
# --------------------------------------------------------------------------- #
def _connect():
    bootstrap_environ()
    cfg = get_research_database_config()
    import psycopg

    conn = psycopg.connect(cfg.url, connect_timeout=15)
    conn.read_only = True  # belt-and-suspenders: refuse writes
    return conn, cfg


def _load_m15(conn, start: str, end: str) -> pd.DataFrame:
    sql = """
        SELECT time_utc, bid_c, ask_c, mid_o, mid_h, mid_l, mid_c, volume
        FROM market_data.candles
        WHERE instrument = %s AND granularity = 'M15' AND complete
          AND time_utc >= %s AND time_utc < %s
        ORDER BY time_utc
    """
    with conn.cursor() as cur:
        cur.execute(sql, (INSTRUMENT, f"{start}T00:00:00+00:00", f"{end}T00:00:00+00:00"))
        rows = cur.fetchall()
        cols = [c.name for c in cur.description]
    df = pd.DataFrame(rows, columns=cols)
    df["time_utc"] = pd.to_datetime(df["time_utc"], utc=True)
    df = df.set_index("time_utc").sort_index()
    for c in ("bid_c", "ask_c", "mid_o", "mid_h", "mid_l", "mid_c"):
        df[c] = df[c].astype(float)
    return df


def _m1_spread_by_session(conn, start: str, end: str) -> dict:
    """Server-side M1 spread percentiles by NY-hour-derived session (read-only).

    Uses M1 (the finest spread granularity, ~1.84M rows) but aggregates entirely
    in Postgres so nothing large is transferred. Session here is approximated from
    NY local hour only (no overlap split) — a cross-check on the M15 spread atlas.
    """
    sql = """
        WITH base AS (
            SELECT (ask_c - bid_c) / %s AS spread_pips,
                   EXTRACT(HOUR FROM (time_utc AT TIME ZONE 'America/New_York'))::int AS ny_hour
            FROM market_data.candles
            WHERE instrument = %s AND granularity = 'M1' AND complete
              AND time_utc >= %s AND time_utc < %s
        ), tagged AS (
            SELECT spread_pips,
                   CASE
                     WHEN ny_hour = 17 THEN 'rollover'
                     WHEN ny_hour >= 8 AND ny_hour < 17 THEN 'london_ny_or_ny'
                     WHEN ny_hour >= 3 AND ny_hour < 8 THEN 'london'
                     WHEN ny_hour >= 19 OR ny_hour < 3 THEN 'tokyo'
                     ELSE 'off_hours'
                   END AS sess
            FROM base
        )
        SELECT sess, count(*) AS n,
               percentile_cont(0.50) WITHIN GROUP (ORDER BY spread_pips) AS p50,
               percentile_cont(0.90) WITHIN GROUP (ORDER BY spread_pips) AS p90,
               percentile_cont(0.95) WITHIN GROUP (ORDER BY spread_pips) AS p95,
               avg(spread_pips) AS mean
        FROM tagged GROUP BY sess ORDER BY sess
    """
    with conn.cursor() as cur:
        cur.execute(sql, (PIP, INSTRUMENT, f"{start}T00:00:00+00:00", f"{end}T00:00:00+00:00"))
        rows = cur.fetchall()
    return {
        r[0]: {
            "n": int(r[1]),
            "spread_pips_p50": round(float(r[2]), 4),
            "spread_pips_p90": round(float(r[3]), 4),
            "spread_pips_p95": round(float(r[4]), 4),
            "spread_pips_mean": round(float(r[5]), 4),
        }
        for r in rows
    }


# --------------------------------------------------------------------------- #
# Per-bar feature engineering (M15)
# --------------------------------------------------------------------------- #
def _atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int) -> pd.Series:
    prev = close.shift(1)
    tr = pd.concat([(high - low), (high - prev).abs(), (low - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    idx = out.index

    # --- spread ---
    out["spread_pips"] = (out["ask_c"] - out["bid_c"]) / PIP

    # --- volatility ---
    out["atr_px"] = _atr(out["mid_h"], out["mid_l"], out["mid_c"], ATR_LEN)
    out["atr_pips"] = out["atr_px"] / PIP
    out["range_pips"] = (out["mid_h"] - out["mid_l"]) / PIP
    out["spread_to_atr"] = out["spread_pips"] / out["atr_pips"].replace(0, np.nan)
    # trailing rolling volatility percentile (descriptive; uses only past bars)
    out["vol_pctile"] = (
        out["atr_px"].rolling(VOL_PCTILE_WINDOW, min_periods=ATR_LEN * 4).rank(pct=True)
    )
    out["vol_regime"] = pd.cut(
        out["vol_pctile"], bins=[-0.01, 1 / 3, 2 / 3, 1.01],
        labels=["low_vol", "mid_vol", "high_vol"],
    )

    # --- calendar / session ---
    out["session"] = [_session_bucket(t) for t in idx]
    out["ny_hour"] = idx.tz_convert(TZ_NY).hour
    out["utc_hour"] = idx.hour
    out["weekday"] = idx.tz_convert(TZ_NY).day_name()

    # --- forward returns (pips) over horizons ---
    for h in FWD_HORIZONS:
        out[f"fwd_pips_{h}"] = (out["mid_c"].shift(-h) - out["mid_c"]) / PIP

    # --- recent direction (sign of last-N return) ---
    recent = (out["mid_c"] - out["mid_c"].shift(RECENT_DIR_LOOKBACK))
    out["recent_dir"] = np.sign(recent)

    # --- forward MFE / MAE over excursion horizon (long perspective), in pips & ATR ---
    h = EXCURSION_HORIZON
    fwd_high = out["mid_h"].shift(-1).rolling(h).max().shift(-(h - 1))
    fwd_low = out["mid_l"].shift(-1).rolling(h).min().shift(-(h - 1))
    out["mfe_pips"] = (fwd_high - out["mid_c"]) / PIP
    out["mae_pips"] = (fwd_low - out["mid_c"]) / PIP  # <= 0 typically
    out["mfe_atr"] = out["mfe_pips"] / out["atr_pips"].replace(0, np.nan)
    out["mae_atr"] = out["mae_pips"] / out["atr_pips"].replace(0, np.nan)

    # --- breakout / false-breakout (prior-range break that closes back inside) ---
    prior_high = out["mid_h"].rolling(BREAKOUT_LOOKBACK).max().shift(1)
    prior_low = out["mid_l"].rolling(BREAKOUT_LOOKBACK).min().shift(1)
    up_break = out["mid_h"] > prior_high
    dn_break = out["mid_l"] < prior_low
    out["is_breakout"] = up_break | dn_break
    # failed if, within BREAKOUT_RESOLVE bars, close returns inside the prior range
    fwd_close_min = out["mid_c"].shift(-1).rolling(BREAKOUT_RESOLVE).min().shift(-(BREAKOUT_RESOLVE - 1))
    fwd_close_max = out["mid_c"].shift(-1).rolling(BREAKOUT_RESOLVE).max().shift(-(BREAKOUT_RESOLVE - 1))
    failed_up = up_break & (fwd_close_min < prior_high)
    failed_dn = dn_break & (fwd_close_max > prior_low)
    out["false_breakout"] = (failed_up | failed_dn) & out["is_breakout"]

    # --- whipsaw: short-horizon sign reversal of consecutive 1-bar returns ---
    r1 = out["mid_c"].diff()
    out["whipsaw"] = (np.sign(r1) != np.sign(r1.shift(1))) & (r1 != 0) & (r1.shift(1) != 0)

    return out


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #
def _q(s: pd.Series, p: float) -> float | None:
    s = s.dropna()
    return round(float(np.percentile(s, p)), 4) if len(s) else None


def _mean(s: pd.Series) -> float | None:
    s = s.dropna()
    return round(float(s.mean()), 4) if len(s) else None


def _directional_block(g: pd.DataFrame) -> dict:
    block = {}
    for h in FWD_HORIZONS:
        col = g[f"fwd_pips_{h}"].dropna()
        if not len(col):
            continue
        # trend continuation: forward move agrees with recent direction
        sub = g.loc[col.index]
        rd = sub["recent_dir"]
        valid = rd != 0
        cont = ((np.sign(col) == rd) & valid)
        rev = ((np.sign(col) == -rd) & valid)
        n_valid = int(valid.sum())
        block[f"h{h}"] = {
            "mean_fwd_pips": round(float(col.mean()), 4),
            "median_fwd_pips": round(float(col.median()), 4),
            "std_fwd_pips": round(float(col.std()), 4),
            "p_up": round(float((col > 0).mean()), 4),
            "p_trend_continuation": round(float(cont.sum() / n_valid), 4) if n_valid else None,
            "p_mean_reversion": round(float(rev.sum() / n_valid), 4) if n_valid else None,
            "n": len(col),
        }
    return block


def _aggregate(g: pd.DataFrame, global_median_range: float) -> dict:
    n = len(g)
    if n == 0:
        return {"n": 0}
    return {
        "n": n,
        "spread_pips": {
            "median": _q(g["spread_pips"], 50),
            "p90": _q(g["spread_pips"], 90),
            "p95": _q(g["spread_pips"], 95),
            "mean": _mean(g["spread_pips"]),
        },
        "volatility": {
            "atr_pips_median": _q(g["atr_pips"], 50),
            "range_pips_median": _q(g["range_pips"], 50),
            "range_pips_mean": _mean(g["range_pips"]),
            "spread_to_atr_median": _q(g["spread_to_atr"], 50),
            "range_expansion_prob": round(float((g["range_pips"] > global_median_range).mean()), 4),
        },
        "directional": _directional_block(g),
        "tradability": {
            "mfe_pips_mean": _mean(g["mfe_pips"]),
            "mae_pips_mean": _mean(g["mae_pips"]),
            "mfe_atr_mean": _mean(g["mfe_atr"]),
            "mae_atr_mean": _mean(g["mae_atr"]),
            "mfe_to_mae_abs": (
                round(abs(_mean(g["mfe_pips"]) / _mean(g["mae_pips"])), 4)
                if _mean(g["mae_pips"]) not in (None, 0)
                else None
            ),
            "breakout_rate": round(float(g["is_breakout"].mean()), 4),
            "false_breakout_rate_given_breakout": (
                round(float(g.loc[g["is_breakout"], "false_breakout"].mean()), 4)
                if int(g["is_breakout"].sum()) > 0
                else None
            ),
            "whipsaw_rate": round(float(g["whipsaw"].mean()), 4),
        },
    }


def _by(df: pd.DataFrame, key, gmr: float) -> dict:
    return {str(k): _aggregate(g, gmr) for k, g in df.groupby(key, observed=True)}


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", default=TRAIN_START)
    ap.add_argument("--end", default=VALIDATION_END, help="exclusive; TEST lockbox excluded")
    ap.add_argument("--no-m1", action="store_true", help="skip the M1 spread cross-check")
    args = ap.parse_args()

    if args.end > TEST_LOCKBOX_START:
        raise SystemExit(
            f"refusing to read past TEST lockbox start {TEST_LOCKBOX_START}: end={args.end}"
        )

    conn, cfg = _connect()
    print(f"research DB: {cfg.redacted_url} (read-only)")
    try:
        df = _load_m15(conn, args.start, args.end)
        print(f"loaded {len(df):,} M15 bars  {df.index.min()} .. {df.index.max()}")
        feats = _build_features(df)
        gmr = float(feats["range_pips"].median())

        # per-split tag (train vs validation) for coverage transparency
        val_start = pd.Timestamp("2024-01-01", tz="UTC")
        feats["split"] = np.where(feats.index < val_start, "train", "validation")

        m1_block = None
        if not args.no_m1:
            print("aggregating M1 spread by session (server-side)...")
            m1_block = _m1_spread_by_session(conn, args.start, args.end)
    finally:
        conn.close()

    summary = {
        "_meta": {
            "instrument": INSTRUMENT,
            "kind": "descriptive_session_volatility_spread_atlas",
            "NOT_edge_claim": True,
            "NOT_strategy": True,
            "window_start": args.start,
            "window_end_exclusive": args.end,
            "test_lockbox_start_excluded": TEST_LOCKBOX_START,
            "n_m15_bars": len(feats),
            "first_bar_utc": str(feats.index.min()),
            "last_bar_utc": str(feats.index.max()),
            "pip": PIP,
            "params": {
                "atr_len": ATR_LEN,
                "fwd_horizons_m15_bars": list(FWD_HORIZONS),
                "excursion_horizon_bars": EXCURSION_HORIZON,
                "recent_dir_lookback": RECENT_DIR_LOOKBACK,
                "vol_pctile_window_bars": VOL_PCTILE_WINDOW,
                "breakout_lookback": BREAKOUT_LOOKBACK,
                "breakout_resolve": BREAKOUT_RESOLVE,
                "global_median_range_pips": round(gmr, 4),
            },
            "session_definition": {
                "tokyo": "09:00-15:00 Asia/Tokyo",
                "london": "08:00-16:00 Europe/London",
                "ny": "08:00-17:00 America/New_York",
                "london_ny_overlap": "london AND ny active",
                "rollover": "17:00-18:00 America/New_York",
                "off_hours": "none of the above",
                "priority": "rollover > overlap > ny > london > tokyo > off_hours",
            },
        },
        "coverage_by_split": {
            s: int((feats["split"] == s).sum()) for s in ("train", "validation")
        },
        "by_session": _by(feats, "session", gmr),
        "by_ny_hour": _by(feats, "ny_hour", gmr),
        "by_utc_hour": _by(feats, "utc_hour", gmr),
        "by_weekday": _by(feats, "weekday", gmr),
        "by_vol_regime": _by(feats, "vol_regime", gmr),
        "m1_spread_by_session_crosscheck": m1_block,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2, default=str))
    print(f"wrote {OUT_JSON}  ({OUT_JSON.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

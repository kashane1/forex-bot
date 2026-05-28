#!/usr/bin/env python3
"""Build the read-only USD_JPY volatility-compression → expansion diagnostic dataset.

DIAGNOSTIC ONLY — not a strategy, not a campaign, no verdict change, no approval.

Reads USD_JPY M15 candles from the research Postgres DB (``market_data.candles``)
read-only over the **train+validation** window and joins, per M15 decision bar:

  * compression features (decision-time, no lookahead),
  * expansion labels (future bars; labels only),
  * session bucket + cost context (spread pips, spread/ATR),
  * volatility context (range/ATR/realized-vol trailing percentiles),
  * direction labels (up/down/agnostic expansion, breakout follow-through, false break).

The **TEST window (2025-07-01+) is a sealed lockbox and is excluded.** The full per-bar
dataset is written to a gitignored parquet; only a compact manifest JSON + a small
feature-preview CSV are committed.

Usage:
    python scripts/build_usdjpy_volatility_compression_expansion_dataset.py
"""

from __future__ import annotations

import argparse
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
    COMPRESSION_FEATURES,
    DIRECTION_AGNOSTIC_EXPANSION_LABELS,
    DIRECTIONAL_EXPANSION_LABELS,
    CompressionExpansionParams,
    compute_compression_features,
    compute_expansion_labels,
    session_bucket,
)

INSTRUMENT = "USD_JPY"
PIP = 0.01

TRAIN_START = "2021-06-01"
VALIDATION_END = "2025-06-30"  # exclusive
TEST_LOCKBOX_START = "2025-07-01"
VAL_SPLIT = "2024-01-01"

OUT_DIR = ROOT / "research/usdjpy_vol_compression_expansion"
MANIFEST = OUT_DIR / "dataset_manifest.json"
PREVIEW = OUT_DIR / "feature_preview.csv"
PARQUET = OUT_DIR / "dataset.parquet"  # gitignored


def _connect():
    bootstrap_environ()
    cfg = get_research_database_config()
    import psycopg

    conn = psycopg.connect(cfg.url, connect_timeout=15)
    conn.read_only = True
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


def _summ(s: pd.Series) -> dict:
    s = pd.to_numeric(s, errors="coerce").dropna()
    if not len(s):
        return {"n": 0}
    return {
        "n": len(s),
        "mean": round(float(s.mean()), 4),
        "p10": round(float(np.percentile(s, 10)), 4),
        "p50": round(float(np.percentile(s, 50)), 4),
        "p90": round(float(np.percentile(s, 90)), 4),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", default=TRAIN_START)
    ap.add_argument("--end", default=VALIDATION_END, help="exclusive; TEST lockbox excluded")
    args = ap.parse_args()
    if args.end > TEST_LOCKBOX_START:
        raise SystemExit(f"refusing to read past TEST lockbox {TEST_LOCKBOX_START}: {args.end}")

    params = CompressionExpansionParams()
    conn, cfg = _connect()
    print(f"research DB: {cfg.redacted_url} (read-only)")
    try:
        df = _load_m15(conn, args.start, args.end)
    finally:
        conn.close()
    print(f"loaded {len(df):,} M15 bars  {df.index.min()} .. {df.index.max()}")

    # --- features + labels ---
    comp = compute_compression_features(df, params)
    labels = compute_expansion_labels(df, params)

    ds = pd.DataFrame(index=df.index)
    ds["split"] = np.where(df.index < pd.Timestamp(VAL_SPLIT, tz="UTC"), "train", "validation")
    ds["session"] = [session_bucket(t.to_pydatetime()) for t in df.index]
    ds["spread_pips"] = (df["ask_c"] - df["bid_c"]) / PIP
    from forex_bot.strategies.indicators import atr as _atr

    ds["atr_pips"] = _atr(df["mid_h"], df["mid_l"], df["mid_c"], length=params.atr_len) / PIP
    ds["spread_to_atr"] = ds["spread_pips"] / ds["atr_pips"].replace(0, np.nan)
    ds = pd.concat([ds, comp, labels], axis=1)

    # direction labels are already inside `labels` (breakout_up/down/any, followthrough,
    # false_breakout per horizon); add a simple agnostic-vs-directional roll-up at the
    # primary horizon for convenience.
    ph = 8  # primary horizon for roll-ups (2h)
    ds["expand_up"] = ds[f"fwd_signed_move_pips_h{ph}"] > 0
    ds["expand_down"] = ds[f"fwd_signed_move_pips_h{ph}"] < 0

    # --- persist full dataset (gitignored) ---
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    wrote_parquet = True
    try:
        ds.to_parquet(PARQUET)
    except Exception as e:  # pragma: no cover - environment dependent
        wrote_parquet = False
        print(f"parquet not written ({type(e).__name__}: {e}); manifest/preview only")

    # --- compact preview (first 200 rows with valid expansion labels) ---
    preview_cols = (
        ["split", "session", "spread_pips", "atr_pips", "spread_to_atr"]
        + list(COMPRESSION_FEATURES)
        + [f"fwd_range_pips_h{ph}", f"fwd_signed_move_pips_h{ph}",
           f"breakout_any_h{ph}", f"breakout_followthrough_h{ph}", f"false_breakout_h{ph}"]
    )
    preview = ds[preview_cols].dropna(subset=[f"fwd_range_pips_h{ph}"]).head(200)
    preview.to_csv(PREVIEW)

    # --- manifest ---
    comp_summary = {c: _summ(ds[c]) for c in COMPRESSION_FEATURES}
    label_summary = {}
    for h in params.horizons:
        for base in ("fwd_range_pips", "fwd_signed_move_pips", "fwd_mfe_pips", "fwd_mae_pips"):
            col = f"{base}_h{h}"
            label_summary[col] = _summ(ds[col])
        for base in ("breakout_any", "breakout_up", "breakout_down",
                     "breakout_followthrough", "false_breakout"):
            col = f"{base}_h{h}"
            s = ds[col].dropna()
            label_summary[col] = {"n": len(s), "rate": round(float(s.mean()), 4) if len(s) else None}

    manifest = {
        "_meta": {
            "instrument": INSTRUMENT,
            "kind": "vol_compression_expansion_diagnostic_dataset",
            "NOT_edge_claim": True,
            "NOT_strategy": True,
            "window_start": args.start,
            "window_end_exclusive": args.end,
            "test_lockbox_start_excluded": TEST_LOCKBOX_START,
            "val_split": VAL_SPLIT,
            "n_bars": len(ds),
            "first_bar_utc": str(ds.index.min()),
            "last_bar_utc": str(ds.index.max()),
            "primary_horizon_bars": ph,
            "params": {
                "atr_len": params.atr_len, "pct_window": params.pct_window,
                "bb_len": params.bb_len, "bb_k": params.bb_k, "rv_len": params.rv_len,
                "inside_lookback": params.inside_lookback,
                "range_lookback": params.range_lookback,
                "horizons": list(params.horizons),
                "compression_cuts": list(params.compression_cuts),
                "primary_cut": params.primary_cut,
                "followthrough_atr_frac": params.followthrough_atr_frac,
            },
            "compression_features": list(COMPRESSION_FEATURES),
            "direction_agnostic_labels": list(DIRECTION_AGNOSTIC_EXPANSION_LABELS),
            "directional_labels": list(DIRECTIONAL_EXPANSION_LABELS),
            "parquet_written": wrote_parquet,
            "parquet_path_gitignored": str(PARQUET.relative_to(ROOT)),
        },
        "coverage_by_split": {s: int((ds["split"] == s).sum()) for s in ("train", "validation")},
        "coverage_by_session": {k: int(v) for k, v in ds["session"].value_counts().items()},
        "cost_context": {
            "spread_pips": _summ(ds["spread_pips"]),
            "atr_pips": _summ(ds["atr_pips"]),
            "spread_to_atr": _summ(ds["spread_to_atr"]),
        },
        "compression_feature_summary": comp_summary,
        "expansion_label_summary": label_summary,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, default=str))
    print(f"wrote {MANIFEST} ({MANIFEST.stat().st_size:,} B), {PREVIEW} ({len(preview)} rows)")
    if wrote_parquet:
        print(f"wrote {PARQUET} ({PARQUET.stat().st_size:,} B, gitignored)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

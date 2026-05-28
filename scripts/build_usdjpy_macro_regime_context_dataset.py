#!/usr/bin/env python3
"""Build the read-only USD_JPY macro-regime CONTEXT dataset (tradeability diagnostic).

DIAGNOSTIC ONLY — not a strategy, not a campaign, not fast-news trading. Joins, per M15
bar, USD/JPY tradeability metrics with SLOW lookahead-safe macro/rates/risk regime
context (as-of/lagged) and public-schedule event windows. Macro context is used only as a
tradeability conditioner / no-trade filter, never an entry signal. TEST sealed.

Outputs (compact committed; bulky parquet gitignored):
  research/usdjpy_macro_regime_context/context_manifest.json
  research/usdjpy_macro_regime_context/context_dataset.parquet   (gitignored)
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
from forex_bot.research.macro_regime_context import (
    MacroRegimeParams,
    asof_join,
    build_daily_regime_features,
    build_event_calendar,
    event_window_flags,
    nfp_release_datetimes,
    stabilization_bucket,
)
from forex_bot.research.macro_regime_context import (
    fomc_announcement_datetimes as _fomc,
)
from forex_bot.research.volatility_compression_expansion import (
    CompressionExpansionParams,
    breakout_labels,
    false_breakout,
    forward_range_pips,
)
from forex_bot.strategies.indicators import atr as atr_indicator

INSTRUMENT = "USD_JPY"
PIP = 0.01
TRAIN_START = "2021-06-01"
VALIDATION_END = "2025-06-30"
TEST_LOCKBOX_START = "2025-07-01"
VAL_SPLIT = "2024-01-01"
TRADEABILITY_HORIZON = 16  # 4h forward window for range/breakout-survival labels
WHIPSAW_FWD = 8

OUT_DIR = ROOT / "research/usdjpy_macro_regime_context"
MANIFEST = OUT_DIR / "context_manifest.json"
PARQUET = OUT_DIR / "context_dataset.parquet"

CTX_COLS = [
    "us_2y_yield", "us_10y_yield", "us_2s10s", "us_2y_trend", "us_10y_trend",
    "us_2y_regime", "vix", "vix_regime", "vix_trend", "sp500_trend",
    "broad_usd_trend", "risk_off",
]


def _connect():
    bootstrap_environ()
    cfg = get_research_database_config()
    import psycopg

    conn = psycopg.connect(cfg.url, connect_timeout=15)
    conn.read_only = True
    return conn, cfg


def _load_m15(conn, end: str) -> pd.DataFrame:
    sql = """
        SELECT time_utc, bid_c, ask_c, mid_o, mid_h, mid_l, mid_c
        FROM market_data.candles
        WHERE instrument=%s AND granularity='M15' AND complete
          AND time_utc >= %s AND time_utc < %s
        ORDER BY time_utc
    """
    with conn.cursor() as cur:
        cur.execute(sql, (INSTRUMENT, f"{TRAIN_START}T00:00:00+00:00", f"{end}T00:00:00+00:00"))
        rows = cur.fetchall()
        cols = [c.name for c in cur.description]
    df = pd.DataFrame(rows, columns=cols)
    df["time_utc"] = pd.to_datetime(df["time_utc"], utc=True)
    df = df.set_index("time_utc").sort_index()
    for c in ("bid_c", "ask_c", "mid_o", "mid_h", "mid_l", "mid_c"):
        df[c] = df[c].astype(float)
    return df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--end", default=VALIDATION_END)
    ap.add_argument("--lag-days", type=int, default=1, help="macro publication lag (latency knob)")
    args = ap.parse_args()
    if args.end > TEST_LOCKBOX_START:
        raise SystemExit(f"refusing to read past TEST lockbox {TEST_LOCKBOX_START}: {args.end}")

    mparams = MacroRegimeParams(publication_lag_days=args.lag_days)
    cparams = CompressionExpansionParams()
    conn, cfg = _connect()
    print(f"research DB: {cfg.redacted_url} (read-only)")
    try:
        df = _load_m15(conn, args.end)
    finally:
        conn.close()
    print(f"loaded {len(df):,} M15 bars  {df.index.min()} .. {df.index.max()}")

    out = pd.DataFrame(index=df.index)
    out["split"] = np.where(df.index < pd.Timestamp(VAL_SPLIT, tz="UTC"), "train", "validation")
    out["year"] = df.index.year

    # --- tradeability metrics ---
    out["spread_pips"] = (df["ask_c"] - df["bid_c"]) / PIP
    out["atr_pips"] = atr_indicator(df["mid_h"], df["mid_l"], df["mid_c"], length=cparams.atr_len) / PIP
    out["spread_to_atr"] = out["spread_pips"] / out["atr_pips"].replace(0, np.nan)
    out["fwd_range_pips"] = forward_range_pips(df, TRADEABILITY_HORIZON)
    bl = breakout_labels(df, TRADEABILITY_HORIZON, cparams)
    out["breakout_any"] = bl["breakout_any"]
    out["false_breakout"] = false_breakout(df, TRADEABILITY_HORIZON, cparams)
    # whipsaw: fraction of 1-bar return sign reversals over the next WHIPSAW_FWD bars
    r1 = df["mid_c"].diff()
    rev = (np.sign(r1) != np.sign(r1.shift(1))) & (r1 != 0) & (r1.shift(1) != 0)
    out["whipsaw_fwd"] = rev.shift(-WHIPSAW_FWD).rolling(WHIPSAW_FWD).mean().shift(-(WHIPSAW_FWD - 1))

    # --- slow macro context (as-of/lagged join; lookahead-safe) ---
    daily = build_daily_regime_features(params=mparams)
    ctx = asof_join(daily[CTX_COLS], df.index, mparams)
    out = pd.concat([out, ctx[CTX_COLS]], axis=1)

    # --- event windows (public schedule dates only) ---
    cal = build_event_calendar(TRAIN_START, args.end)
    all_ev = list(cal["time_utc"])
    nfp_ev = nfp_release_datetimes(TRAIN_START, args.end)
    fomc_ev = _fomc(TRAIN_START, args.end)
    fa = event_window_flags(df.index, all_ev, mparams)
    out["evt_any_window"] = fa["event_window"]
    out["evt_pre"] = fa["pre_event"]
    out["evt_post"] = fa["post_event"]
    out["hours_since_event"] = fa["hours_since_event"]
    out["stab_bucket"] = stabilization_bucket(fa["hours_since_event"], mparams)
    out["evt_nfp_window"] = event_window_flags(df.index, nfp_ev, mparams)["event_window"]
    out["evt_fomc_window"] = event_window_flags(df.index, fomc_ev, mparams)["event_window"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    wrote_parquet = True
    try:
        out.to_parquet(PARQUET)
    except Exception as e:  # pragma: no cover
        wrote_parquet = False
        print(f"parquet not written ({type(e).__name__}: {e})")

    def _ctxcov(col):
        vc = out[col].value_counts(dropna=False)
        return {str(k): int(v) for k, v in vc.items()}

    manifest = {
        "_meta": {
            "instrument": INSTRUMENT, "kind": "macro_regime_context_dataset",
            "NOT_edge_claim": True, "NOT_strategy": True, "NOT_fast_news": True,
            "macro_is": "tradeability conditioner / no-trade filter, never an entry",
            "window_start": TRAIN_START, "window_end_exclusive": args.end,
            "test_lockbox_excluded": TEST_LOCKBOX_START, "val_split": VAL_SPLIT,
            "publication_lag_days": args.lag_days, "tradeability_horizon_bars": TRADEABILITY_HORIZON,
            "n_bars": len(out), "parquet_written": wrote_parquet,
            "parquet_gitignored": str(PARQUET.relative_to(ROOT)),
            "macro_context_cols": CTX_COLS,
            "events": {"nfp": len(nfp_ev), "fomc": len(fomc_ev), "total": len(all_ev),
                       "deferred": ["US_CPI", "BOJ"]},
        },
        "coverage_by_split": {s: int((out["split"] == s).sum()) for s in ("train", "validation")},
        "context_coverage": {c: _ctxcov(c) for c in
                             ("us_2y_regime", "us_2y_trend", "vix_regime", "risk_off",
                              "stab_bucket", "evt_any_window", "evt_nfp_window", "evt_fomc_window")},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, default=str))
    print(f"wrote {MANIFEST} ({MANIFEST.stat().st_size:,} B); parquet={wrote_parquet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Run the C1 factor-validation analysis on the local research corpus.

Research-only. Reuses the locked M1/HTF confluence framework to re-derive the
single surviving state (``C1_trend_cont_long`` / ``_short``) across all seven
USD-legged majors and emit the descriptive artifacts the validation phases need:

* ``c1_validation/{pair}_c1_events.csv``  — per-event panel (forward response +
  regime covariates + signed extension) for C1 long and short;
* ``c1_validation/{pair}_c1_nulls.csv``   — random + session-matched null Z by
  horizon for C1 long and short (200 seeds);
* ``c1_validation/c1_robustness.csv``     — C1_long 30/60-min mean/t under
  baseline + one-knob-perturbed specs (alt EMA / slope / trend def / confluence
  depth), per pair.

NO trades, NO positions, NO PnL, NO optimisation, NO approval, NO OANDA APIs,
NO credentials beyond the local research DB URL.

Usage:
  python scripts/run_c1_factor_validation.py --pairs all --null-seeds 200
  python scripts/run_c1_factor_validation.py --pairs USD_JPY,EUR_USD --skip-robustness
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import time

import pandas as pd

from forex_bot.research import c1_factor_validation as c1v
from forex_bot.research import m1_response_matrix as mrm

DOCS = pathlib.Path("docs/research")
OUT = DOCS / "c1_validation"
M1_SOURCE = "oanda-practice-m1"
MATERIALIZED_SOURCE = "m1_materialized"
HTF_LOAD = {"M5": "M5", "M15": "M15", "H1": "H1", "H4": "H4M1"}

ALL_PAIRS = [
    "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "NZD_USD", "USD_CAD", "USD_CHF",
]

# Robustness specs: baseline + one perturbed knob each (NOT optimisation).
ROBUSTNESS_SPECS = [
    c1v.BASELINE,
    c1v.C1Spec(name="ema_30_60", ema_fast=30, ema_slow=60),
    c1v.C1Spec(name="ema_10_40", ema_fast=10, ema_slow=40),
    c1v.C1Spec(name="slope_lb_5", slope_lookback=5),
    c1v.C1Spec(
        name="trend_no_slope", trend_requires_slope=False,
        legs=(("H4", "aligned"), ("H1", "aligned"), ("M15", "aligned")),
    ),
    c1v.C1Spec(
        name="m15_strict",
        legs=(("H4", "trend"), ("H1", "trend"), ("M15", "trend")),
    ),
    c1v.C1Spec(name="drop_h4", legs=(("H1", "trend"), ("M15", "aligned"))),
    c1v.C1Spec(
        name="add_m5",
        legs=(("H4", "trend"), ("H1", "trend"), ("M15", "aligned"), ("M5", "aligned")),
    ),
]


def _load_env_var(name: str) -> bool:
    if os.environ.get(name, "").strip():
        return True
    for fn in (".env.local", ".env"):
        p = pathlib.Path(fn)
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            s = line.strip()
            if s.startswith(f"{name}="):
                val = s.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    os.environ[name] = val
                    return True
    return False


def _store():
    from forex_bot.data.postgres_candle_store import PostgresCandleStore
    from forex_bot.data.research_db import get_research_database_config

    return PostgresCandleStore(get_research_database_config())


def _rows_index(rows: list[dict]) -> pd.DatetimeIndex:
    return pd.to_datetime([r["time_utc"] for r in rows], utc=True).as_unit("ns")


def load_m1(store, pair: str) -> pd.DataFrame:
    rows = store.query_candles(instrument=pair, granularity="M1", source=M1_SOURCE)
    df = pd.DataFrame(
        {
            "mid_c": [float(r["mid_c"]) for r in rows],
            "spread_close": [float(r["spread_close"]) for r in rows],
        },
        index=_rows_index(rows),
    )
    return df.sort_index()


def load_raw_htf(store, pair: str) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for tf, gran in HTF_LOAD.items():
        rows = store.query_candles(
            instrument=pair, granularity=gran, source=MATERIALIZED_SOURCE
        )
        out[tf] = pd.DataFrame(
            {
                "open": [float(r["mid_o"]) for r in rows],
                "high": [float(r["mid_h"]) for r in rows],
                "low": [float(r["mid_l"]) for r in rows],
                "close": [float(r["mid_c"]) for r in rows],
            },
            index=_rows_index(rows),
        ).sort_index()
    return out


def run_pair(store, pair: str, *, seeds: int, skip_robustness: bool) -> dict:
    t0 = time.time()
    print(f"[load] {pair} M1 + HTF ...", flush=True)
    m1_df = load_m1(store, pair)
    raw = load_raw_htf(store, pair)
    print(
        f"[load] {pair} M1 bars={len(m1_df)} "
        f"span={m1_df.index[0]}..{m1_df.index[-1]} ({time.time()-t0:.0f}s)",
        flush=True,
    )

    # Baseline panel + nulls.
    frame = c1v.build_combined_frame(m1_df, raw, c1v.BASELINE)
    panel = c1v.build_c1_panel(m1_df, frame, pair, c1v.BASELINE)
    OUT.mkdir(parents=True, exist_ok=True)
    epath = OUT / f"{pair.lower()}_c1_events.csv"
    panel.to_csv(epath, index=False)
    n_long = int((panel["state"] == "C1_trend_cont_long").sum())
    n_short = int((panel["state"] == "C1_trend_cont_short").sum())
    print(f"[write] {epath} (long={n_long} short={n_short})", flush=True)

    nulls = c1v.c1_nulls(m1_df, frame, pair, seeds=seeds)
    npath = OUT / f"{pair.lower()}_c1_nulls.csv"
    nulls.to_csv(npath, index=False)
    print(f"[write] {npath} ({len(nulls)} rows)", flush=True)

    # Robustness: C1_long mean/t at 30/60 min under each spec.
    robustness_rows: list[dict] = []
    if not skip_robustness:
        for spec in ROBUSTNESS_SPECS:
            f_s = c1v.build_combined_frame(m1_df, raw, spec)
            p_s = c1v.build_c1_panel(m1_df, f_s, pair, spec)
            summ = mrm.summarize(
                p_s[p_s["state"] == "C1_trend_cont_long"], horizons_min=(30, 60)
            )
            for h in (30, 60):
                row_h = summ[summ["horizon_min"] == h]
                if row_h.empty:
                    continue
                r = row_h.iloc[0]
                robustness_rows.append(
                    {
                        "pair": pair,
                        "spec": spec.name,
                        "horizon_min": h,
                        "n": int(r["n"]),
                        "mean_ret": float(r["mean_ret"]),
                        "t_stat": float(r["t_stat"]),
                        "p_neg": float(r["p_neg"]),
                        "mean_spread": float(r["mean_spread"]),
                    }
                )
            print(f"[robust] {pair} {spec.name} done", flush=True)

    return {
        "pair": pair,
        "m1_bars": len(m1_df),
        "span_start": str(m1_df.index[0]),
        "span_end": str(m1_df.index[-1]),
        "n_c1_long_events": n_long,
        "n_c1_short_events": n_short,
        "robustness_rows": robustness_rows,
        "seconds": round(time.time() - t0, 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pairs", default="all", help="'all' or comma-separated list")
    ap.add_argument("--null-seeds", type=int, default=200)
    ap.add_argument("--skip-robustness", action="store_true")
    args = ap.parse_args()

    if not _load_env_var("FOREX_BOT_RESEARCH_DATABASE_URL"):
        raise SystemExit("Research DB URL not found in env or .env files — aborting.")

    pairs = ALL_PAIRS if args.pairs == "all" else [
        p.strip() for p in args.pairs.split(",") if p.strip()
    ]
    store = _store()
    OUT.mkdir(parents=True, exist_ok=True)

    metas = []
    all_robustness: list[dict] = []
    for pair in pairs:
        meta = run_pair(
            store, pair, seeds=args.null_seeds, skip_robustness=args.skip_robustness
        )
        all_robustness.extend(meta.pop("robustness_rows"))
        metas.append(meta)

    if all_robustness:
        rob = pd.DataFrame(all_robustness)
        rpath = OUT / "c1_robustness.csv"
        rob.to_csv(rpath, index=False)
        print(f"[write] {rpath} ({len(rob)} rows)", flush=True)

    meta_doc = {
        "m1_source": M1_SOURCE,
        "materialized_source": MATERIALIZED_SOURCE,
        "horizons_min": list(mrm.HORIZONS_MIN),
        "cooldown_min": mrm.COOLDOWN_MIN,
        "null_seeds": args.null_seeds,
        "pairs": metas,
    }
    (OUT / "c1_validation_meta.json").write_text(json.dumps(meta_doc, indent=2))
    print(f"[write] {OUT / 'c1_validation_meta.json'}", flush=True)


if __name__ == "__main__":
    main()

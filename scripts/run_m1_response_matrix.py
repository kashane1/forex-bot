#!/usr/bin/env python
"""Run the M1/HTF confluence response matrix on the local research corpus.

Research-only. Reads M1 + materialized M5/M15/H1/H4 (mid prices + per-bar
spread) from the local Postgres research store, builds the locked confluence
states, samples events (rising-edge + cooldown), and measures forward M1
response over 5/10/15/30/60 minutes. Optionally compares the strongest states to
random-timestamp and session-matched nulls.

NO trades, NO positions, NO PnL, NO optimization, NO approval, NO OANDA APIs.
Writes descriptive CSV/JSON artifacts under docs/research/.

Usage:
  python scripts/run_m1_response_matrix.py --pair USD_JPY
  python scripts/run_m1_response_matrix.py --pair EUR_USD \
      --null-states A2_pullback_long,B2_pullback_long --null-seeds 200
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib

import numpy as np
import pandas as pd

from forex_bot.research import m1_response_matrix as mrm

DOCS = pathlib.Path("docs/research")
M1_SOURCE = "oanda-practice-m1"
MATERIALIZED_SOURCE = "m1_materialized"
# Store granularity label -> state-frame timeframe key (H4 lives under "H4M1").
HTF_LOAD = {"M5": "M5", "M15": "M15", "H1": "H1", "H4": "H4M1"}
VOL_COL_BY_FAMILY = {"A": "M15_atr", "B": "H1_atr", "C": "H4_atr"}


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


def load_htf(store, pair: str, store_granularity: str) -> pd.DataFrame:
    rows = store.query_candles(
        instrument=pair, granularity=store_granularity, source=MATERIALIZED_SOURCE
    )
    df = pd.DataFrame(
        {
            "open": [float(r["mid_o"]) for r in rows],
            "high": [float(r["mid_h"]) for r in rows],
            "low": [float(r["mid_l"]) for r in rows],
            "close": [float(r["mid_c"]) for r in rows],
        },
        index=_rows_index(rows),
    )
    return df.sort_index()


def build_frame(store, pair: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (m1_df, confluence_frame)."""
    m1_df = load_m1(store, pair)
    htf_frames = {tf: load_htf(store, pair, g) for tf, g in HTF_LOAD.items()}
    frame = mrm.build_confluence_frame(m1_df, htf_frames)
    return m1_df, frame


def all_events_and_response(
    m1_df: pd.DataFrame, frame: pd.DataFrame, pair: str
) -> pd.DataFrame:
    states = mrm.confluence_states(frame)
    pieces = []
    for name, signed in states.items():
        fam = mrm.state_family(name)
        ev = mrm.extract_events(
            signed, frame, pair=pair, state=name, vol_col=VOL_COL_BY_FAMILY[fam]
        )
        if ev.empty:
            continue
        resp = mrm.forward_response(m1_df, ev, pair=pair)
        pieces.append(resp)
    if not pieces:
        return pd.DataFrame()
    return pd.concat(pieces, ignore_index=True)


def compute_nulls(
    m1_df: pd.DataFrame,
    frame: pd.DataFrame,
    pair: str,
    state_names: list[str],
    *,
    seeds: int,
) -> pd.DataFrame:
    states = mrm.confluence_states(frame)
    horizons = mrm.HORIZONS_MIN
    rows = []
    for name in state_names:
        signed = states[name]
        fam = mrm.state_family(name)
        ev = mrm.extract_events(
            signed, frame, pair=pair, state=name, vol_col=VOL_COL_BY_FAMILY[fam]
        )
        if ev.empty:
            continue
        sign = int(np.sign(signed.loc[signed != 0].iloc[0]))
        obs = mrm.summarize(
            mrm.forward_response(m1_df, ev, pair=pair), horizons_min=horizons
        ).set_index("horizon_min")
        n = len(ev)

        rand = {h: [] for h in horizons}
        matched = {h: [] for h in horizons}
        for s in range(seeds):
            r_ev = mrm.sample_random_events(
                m1_df, pair=pair, n=n, direction=sign, seed=1000 + s
            )
            r_sum = mrm.summarize(
                mrm.forward_response(m1_df, r_ev, pair=pair), horizons_min=horizons
            ).set_index("horizon_min")
            m_ev = mrm.sample_matched_null(m1_df, ev, pair=pair, seed=5000 + s)
            m_sum = mrm.summarize(
                mrm.forward_response(m1_df, m_ev, pair=pair), horizons_min=horizons
            ).set_index("horizon_min")
            for h in horizons:
                if h in r_sum.index:
                    rand[h].append(r_sum.loc[h, "mean_ret"])
                if h in m_sum.index:
                    matched[h].append(m_sum.loc[h, "mean_ret"])

        for h in horizons:
            if h not in obs.index:
                continue
            o = float(obs.loc[h, "mean_ret"])
            r_arr = np.asarray(rand[h], dtype=float)
            m_arr = np.asarray(matched[h], dtype=float)
            r_mean, r_std = float(r_arr.mean()), float(r_arr.std(ddof=1))
            m_mean, m_std = float(m_arr.mean()), float(m_arr.std(ddof=1))
            rows.append(
                {
                    "state": name,
                    "horizon_min": h,
                    "n": n,
                    "obs_mean_ret": o,
                    "rand_null_mean": r_mean,
                    "rand_null_std": r_std,
                    "rand_z": (o - r_mean) / r_std if r_std > 0 else float("nan"),
                    "matched_null_mean": m_mean,
                    "matched_null_std": m_std,
                    "matched_z": (o - m_mean) / m_std if m_std > 0 else float("nan"),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pair", required=True)
    ap.add_argument("--null-states", default="", help="comma-separated state names")
    ap.add_argument("--null-seeds", type=int, default=200)
    args = ap.parse_args()

    if not _load_env_var("FOREX_BOT_RESEARCH_DATABASE_URL"):
        raise SystemExit("Research DB URL not found in env or .env files — aborting.")

    pair = args.pair
    store = _store()
    print(f"[load] {pair} M1 + HTF ...", flush=True)
    m1_df, frame = build_frame(store, pair)
    print(f"[load] M1 bars={len(m1_df)} span={m1_df.index[0]}..{m1_df.index[-1]}", flush=True)

    resp = all_events_and_response(m1_df, frame, pair)
    summary = mrm.summarize(resp, horizons_min=mrm.HORIZONS_MIN)
    DOCS.mkdir(parents=True, exist_ok=True)
    csv_path = DOCS / f"{pair.lower()}_m1_response_matrix_summary.csv"
    summary.to_csv(csv_path, index=False)
    print(f"[write] {csv_path} ({len(summary)} rows)", flush=True)

    meta = {
        "pair": pair,
        "m1_bars": len(m1_df),
        "m1_source": M1_SOURCE,
        "span_start": str(m1_df.index[0]),
        "span_end": str(m1_df.index[-1]),
        "n_signed_states": int(summary["state"].nunique()) if not summary.empty else 0,
        "horizons_min": list(mrm.HORIZONS_MIN),
        "cooldown_min": mrm.COOLDOWN_MIN,
    }
    (DOCS / f"{pair.lower()}_m1_response_matrix_meta.json").write_text(
        json.dumps(meta, indent=2)
    )

    # Compact console view: 30-minute horizon, sorted by |t_stat|.
    h = 30
    view = summary[summary["horizon_min"] == h].copy()
    if not view.empty:
        view["abs_t"] = view["t_stat"].abs()
        view = view.sort_values("abs_t", ascending=False)
        print(f"\n=== {pair} response @ {h}min (sorted by |t|) ===", flush=True)
        cols = ["state", "n", "mean_ret", "t_stat", "hit_rate", "mfe_mae", "mean_spread"]
        print(view[cols].to_string(index=False), flush=True)

    if args.null_states:
        names = [s.strip() for s in args.null_states.split(",") if s.strip()]
        print(f"\n[nulls] computing for {names} ({args.null_seeds} seeds) ...", flush=True)
        nulls = compute_nulls(m1_df, frame, pair, names, seeds=args.null_seeds)
        npath = DOCS / f"{pair.lower()}_m1_response_matrix_nulls.csv"
        nulls.to_csv(npath, index=False)
        print(f"[write] {npath} ({len(nulls)} rows)", flush=True)
        print(nulls.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()

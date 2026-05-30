#!/usr/bin/env python
"""C1 high-volatility front-gate screen runner (research-only).

Applies the FROZEN Phase-1 hypothesis (docs/research/C1_HIGH_VOL_HYPOTHESIS.md):
filter C1_trend_cont_long events to the within-pair top-tertile H4-ATR
("high-volatility") regime on EUR_USD / USD_JPY / GBP_USD, then compute the
high-vol subset's null comparison against (1) a session+direction matched null,
(2) a randomised-timestamp null, and (3) a volatility-matched null (random bars
drawn only from high-vol M1 bars). The unconditional baseline is the all-events
C1_long mean. 200 seeds.

Event-study / cost / stability statistics for the subset are computed elsewhere
directly from the committed C1 event panels; this runner's job is the nulls,
which need the M1 series. NO trades, NO positions, NO PnL, NO optimisation, NO
OANDA, NO credentials beyond the local research DB URL.

Writes docs/research/c1_highvol_frontgate/{*.csv,*.json}.
"""

from __future__ import annotations

import json
import os
import pathlib

import numpy as np
import pandas as pd

from forex_bot.research import c1_factor_validation as c1v
from forex_bot.research import m1_response_matrix as mrm

DOCS = pathlib.Path("docs/research")
OUT = DOCS / "c1_highvol_frontgate"
PANELS = DOCS / "c1_validation"
M1_SOURCE = "oanda-practice-m1"
MATERIALIZED_SOURCE = "m1_materialized"
HTF_LOAD = {"M5": "M5", "M15": "M15", "H1": "H1", "H4": "H4M1"}
PAIRS = ["EUR_USD", "USD_JPY", "GBP_USD"]
VOL_Q = 2.0 / 3.0  # frozen top-tertile cut
SEEDS = 200
STATE = "C1_trend_cont_long"


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
    return pd.DataFrame(
        {
            "mid_c": [float(r["mid_c"]) for r in rows],
            "spread_close": [float(r["spread_close"]) for r in rows],
        },
        index=_rows_index(rows),
    ).sort_index()


def load_raw_htf(store, pair: str) -> dict[str, pd.DataFrame]:
    out = {}
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


def sample_vol_matched(m1_df, hv_mask, ref_events, *, pair, seed):
    """Session+direction-matched null drawn ONLY from high-vol M1 bars."""
    sessions = mrm.sessions_of(m1_df.index)
    rng = np.random.default_rng(seed)
    by_session = {}
    for sess in ref_events["session"].unique():
        by_session[sess] = np.flatnonzero((sessions == sess).to_numpy() & hv_mask)
    ts_list, dirs = [], []
    for _, ev in ref_events.iterrows():
        pool = by_session.get(ev["session"])
        if pool is None or pool.size == 0:
            continue
        pick = pool[rng.integers(0, pool.size)]
        ts_list.append(m1_df.index[pick])
        dirs.append(int(ev["direction"]))
    if not ts_list:
        return mrm._empty_events()
    ts = pd.DatetimeIndex(ts_list)
    order = np.argsort(ts.asi8)
    ts = ts[order]
    return pd.DataFrame(
        {
            "timestamp": ts,
            "pair": pair,
            "state": "_null_vol_matched",
            "direction": np.asarray(dirs)[order],
            "session": mrm.sessions_of(ts).to_numpy(),
            "spread": np.nan,
            "volatility": np.nan,
        }
    )


def run_pair(store, pair: str) -> dict:
    m1_df = load_m1(store, pair)
    raw = load_raw_htf(store, pair)
    frame = c1v.build_combined_frame(m1_df, raw, c1v.BASELINE)
    states = c1v.c1_signed(frame, c1v.BASELINE)
    signed = states[STATE]
    ev = mrm.extract_events(signed, frame, pair=pair, state=STATE, vol_col="H4_atr")
    resp = mrm.forward_response(m1_df, ev, pair=pair)

    # frozen high-vol threshold: top tertile of event-bar H4 ATR (pips).
    thr = float(resp["volatility"].quantile(VOL_Q))
    hv = resp[resp["volatility"] >= thr].copy()
    pip = mrm.pip_size(pair)
    hv_mask_m1 = (frame["H4_atr"].to_numpy() / pip) >= thr

    horizons = mrm.HORIZONS_MIN
    obs = mrm.summarize(hv, horizons_min=horizons).set_index("horizon_min")
    uncond = mrm.summarize(resp, horizons_min=horizons).set_index("horizon_min")
    n = len(hv)
    sign = 1

    rand = {h: [] for h in horizons}
    matched = {h: [] for h in horizons}
    volm = {h: [] for h in horizons}
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", "Mean of empty slice", RuntimeWarning)
        for s in range(SEEDS):
            r_ev = mrm.sample_random_events(m1_df, pair=pair, n=n, direction=sign, seed=1000 + s)
            m_ev = mrm.sample_matched_null(m1_df, hv, pair=pair, seed=5000 + s)
            v_ev = sample_vol_matched(m1_df, hv_mask_m1, hv, pair=pair, seed=9000 + s)
            for tag, e in (("r", r_ev), ("m", m_ev), ("v", v_ev)):
                summ = mrm.summarize(
                    mrm.forward_response(m1_df, e, pair=pair), horizons_min=horizons
                ).set_index("horizon_min")
                for h in horizons:
                    if h in summ.index:
                        {"r": rand, "m": matched, "v": volm}[tag][h].append(
                            summ.loc[h, "mean_ret"]
                        )

    def z(samples, o):
        a = np.asarray(samples, dtype=float)
        sd = float(a.std(ddof=1)) if a.size > 1 else float("nan")
        return (float(a.mean()) if a.size else float("nan"),
                sd, (o - a.mean()) / sd if sd and sd > 0 else float("nan"))

    rows = []
    for h in horizons:
        if h not in obs.index:
            continue
        o = float(obs.loc[h, "mean_ret"])
        rm, rs, rz = z(rand[h], o)
        mm, ms, mz = z(matched[h], o)
        vm, vs, vz = z(volm[h], o)
        rows.append({
            "pair": pair, "horizon_min": h, "n_hivol": n,
            "obs_mean_ret": o,
            "uncond_mean_ret": float(uncond.loc[h, "mean_ret"]) if h in uncond.index else float("nan"),
            "rand_null_mean": rm, "rand_z": rz,
            "matched_null_mean": mm, "matched_z": mz,
            "volmatched_null_mean": vm, "volmatched_z": vz,
        })

    OUT.mkdir(parents=True, exist_ok=True)
    hv.to_csv(OUT / f"{pair.lower()}_c1_hivol_events.csv", index=False)
    print(f"[{pair}] hi-vol n={n} thr_atr_pips={thr:.2f} "
          f"mean_ret60={float(obs.loc[60,'mean_ret']):.3f} "
          f"matched_z60={rows[-1]['matched_z']:.2f} volm_z60={rows[-1]['volmatched_z']:.2f}",
          flush=True)
    return {"pair": pair, "threshold_atr_pips": thr, "n_hivol": n,
            "n_all_c1_long": len(resp), "nulls": rows}


def main() -> None:
    if not _load_env_var("FOREX_BOT_RESEARCH_DATABASE_URL"):
        raise SystemExit("Research DB URL not found — aborting.")
    store = _store()
    OUT.mkdir(parents=True, exist_ok=True)
    all_rows, metas = [], []
    for pair in PAIRS:
        m = run_pair(store, pair)
        all_rows.extend(m.pop("nulls"))
        metas.append(m)
    pd.DataFrame(all_rows).to_csv(OUT / "c1_hivol_nulls.csv", index=False)
    (OUT / "c1_hivol_meta.json").write_text(json.dumps(
        {"pairs": metas, "seeds": SEEDS, "vol_quantile": VOL_Q,
         "horizons_min": list(mrm.HORIZONS_MIN), "state": STATE}, indent=2))
    print(f"[write] {OUT/'c1_hivol_nulls.csv'} + meta", flush=True)


if __name__ == "__main__":
    main()

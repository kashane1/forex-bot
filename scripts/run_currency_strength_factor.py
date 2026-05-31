#!/usr/bin/env python
"""Run the cross-implied currency-strength factor-validation study.

Research-only. Implements the FROZEN protocol
(``docs/research/CURRENCY_STRENGTH_FACTOR_PROTOCOL.md``). Constructs the factor,
measures forward response, runs four nulls, and emits cross-sectional +
robustness artifacts. NO trades, NO signals, NO PnL, NO approval, NO OANDA APIs,
NO credentials beyond the local research DB URL.

Outputs under docs/research/currency_strength/:
  construction_meta.json, collinearity.json, response_by_condition.csv,
  nulls.csv, events_long.csv, cross_sectional.csv, robustness.csv
"""
from __future__ import annotations

import json
import os
import pathlib

import numpy as np
import pandas as pd

from research.edge_discovery import currency_strength as cs

OUT = pathlib.Path("docs/research/currency_strength")
SOURCE = "m1_materialized"
GRAN = "M5"


def _load_env(name: str) -> bool:
    if os.environ.get(name, "").strip():
        return True
    for fn in (".env.local", ".env"):
        p = pathlib.Path(fn)
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            s = line.strip()
            if s.startswith(f"{name}="):
                v = s.split("=", 1)[1].strip().strip('"').strip("'")
                if v:
                    os.environ[name] = v
                    return True
    return False


def _store():
    from forex_bot.data.postgres_candle_store import PostgresCandleStore
    from forex_bot.data.research_db import get_research_database_config

    return PostgresCandleStore(get_research_database_config())


def load_prices(store) -> dict[str, pd.Series]:
    out = {}
    for inst in cs.INSTRUMENTS:
        rows = store.query_candles(instrument=inst, granularity=GRAN, source=SOURCE)
        idx = pd.to_datetime([r["time_utc"] for r in rows], utc=True).as_unit("ns")
        out[inst] = pd.Series([float(r["mid_c"]) for r in rows], index=idx).sort_index()
        print(f"[load] {inst} M5={len(out[inst])}", flush=True)
    return out


def collinearity(panels: cs.FactorPanels) -> dict:
    s = panels.stren.dropna()
    corr = s.corr()
    # PCA via SVD on standardized strengths
    x = (s - s.mean()) / s.std(ddof=0)
    x = x.dropna()
    u, sv, vt = np.linalg.svd(x.to_numpy(), full_matrices=False)
    var = (sv ** 2) / (sv ** 2).sum()
    # top loadings of PC1
    pc1 = dict(zip(cs.CURRENCIES, np.round(vt[0], 3), strict=False))
    return {
        "n_bars": len(s),
        "corr": {c: {d: round(float(corr.loc[c, d]), 3) for d in cs.CURRENCIES} for c in cs.CURRENCIES},
        "pca_var_ratio": [round(float(v), 4) for v in var],
        "pc1_loadings": pc1,
        "mean_abs_offdiag_corr": round(float(corr.where(~np.eye(len(corr), dtype=bool)).abs().mean().mean()), 3),
    }


def events_long(panels: cs.FactorPanels, ev: np.ndarray, horizons=(60, 240)) -> pd.DataFrame:
    sel = cs.selected_currency_col(panels, ev)
    idx = panels.cc.index
    years = idx.year.to_numpy()[ev]
    sess = cs._session_codes(idx)[ev]
    sess_names = np.array(["asia", "london", "overlap", "new_york", "late"])[sess]
    recs = []
    for mins in horizons:
        hb = cs.HORIZONS_BARS[mins]
        fwd = cs.forward_return(panels.cc, hb).to_numpy()
        for cond in cs.CONDITIONS:
            col = sel[cond]
            vals = fwd[ev, col] / 1e-4
            cur = np.array(cs.CURRENCIES)[col]
            for i in range(len(ev)):
                if np.isnan(vals[i]):
                    continue
                recs.append((cond, mins, cur[i], int(years[i]), sess_names[i], float(vals[i])))
    return pd.DataFrame(recs, columns=["condition", "horizon_min", "currency", "year", "session", "fwd_bp"])


def robustness(prices: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    # nearby lookbacks
    for lb in (24, 48, 96):
        p = cs.build_panels(prices, lookback=lb)
        ev = cs.event_index(p.logpx)
        resp = cs.gather_response(p, ev)
        nul = cs.null_comparison(p, ev, seeds=80)
        for cond in cs.CONDITIONS:
            for h in (60, 240):
                r = resp[(resp.condition == cond) & (resp.horizon_min == h)].iloc[0]
                zmt = nul[(nul.condition == cond) & (nul.horizon_min == h) & (nul.null == "matched_timestamps")].iloc[0]["z"]
                rows.append({"variant": f"lookback_{lb}", "condition": cond, "horizon_min": h,
                             "mean_bp": round(r["mean_bp"], 3), "matched_z": round(float(zmt), 2)})
    return pd.DataFrame(rows)


def main() -> None:
    if not _load_env("FOREX_BOT_RESEARCH_DATABASE_URL"):
        raise SystemExit("Research DB URL not found — aborting.")
    OUT.mkdir(parents=True, exist_ok=True)
    store = _store()
    prices = load_prices(store)

    panels = cs.build_panels(prices, lookback=cs.PRIMARY_L)
    ev = cs.event_index(panels.logpx)
    print(f"[panel] common M5 bars={len(panels.logpx)} events={len(ev)} "
          f"span={panels.logpx.index[0]}..{panels.logpx.index[-1]}", flush=True)

    # Construction meta
    sign_map = cs.currency_sign_map()
    meta = {
        "instruments": cs.INSTRUMENTS, "currencies": cs.CURRENCIES,
        "leg_counts": {c: len(sign_map[c]) for c in cs.CURRENCIES},
        "primary_L": cs.PRIMARY_L, "delta_D": cs.DELTA_D, "sample_every": cs.SAMPLE_EVERY,
        "horizons_min": list(cs.HORIZONS_BARS.keys()),
        "common_m5_bars": len(panels.logpx), "n_events": len(ev),
        "span_start": str(panels.logpx.index[0]), "span_end": str(panels.logpx.index[-1]),
        "dispersion_mean": round(float(panels.dispersion.mean()), 6),
        "spread_mean": round(float(panels.spread.mean()), 6),
        "source": SOURCE, "granularity": GRAN,
    }
    (OUT / "construction_meta.json").write_text(json.dumps(meta, indent=2))
    (OUT / "collinearity.json").write_text(json.dumps(collinearity(panels), indent=2))

    resp = cs.gather_response(panels, ev)
    resp.to_csv(OUT / "response_by_condition.csv", index=False)
    print("[write] response_by_condition.csv", flush=True)

    nul = cs.null_comparison(panels, ev, seeds=200)
    nul.to_csv(OUT / "nulls.csv", index=False)
    print("[write] nulls.csv", flush=True)

    el = events_long(panels, ev)
    el.to_csv(OUT / "events_long.csv", index=False)
    print(f"[write] events_long.csv ({len(el)})", flush=True)

    rob = robustness(prices)
    rob.to_csv(OUT / "robustness.csv", index=False)
    print("[write] robustness.csv", flush=True)
    print("[done]", flush=True)


if __name__ == "__main__":
    main()

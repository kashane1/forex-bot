#!/usr/bin/env python
"""Run the cross relative-value (triangular consistency) factor-validation study.

Research-only. Implements the FROZEN protocol
(``docs/research/CROSS_RELATIVE_VALUE_PROTOCOL.md``). Constructs triangular
residuals, measures deviation→reversion response, runs four nulls, and emits
cross-sectional + robustness + no-arb-artifact artifacts. NO trades, NO signals,
NO PnL, NO approval, NO OANDA APIs, NO credentials beyond the local research DB URL.

Outputs under docs/research/cross_relative_value/.
"""
from __future__ import annotations

import json
import os
import pathlib

import numpy as np
import pandas as pd
from research.edge_discovery.relative_value_spread import ar1_half_life

from research.edge_discovery import cross_relative_value as rv

OUT = pathlib.Path("docs/research/cross_relative_value")
SOURCE = "m1_materialized"
GRAN = "M5"
SHARED_LEG_PAIRS = [("EUR_JPY", "GBP_JPY"), ("EUR_JPY", "AUD_JPY"),
                    ("GBP_JPY", "AUD_JPY"), ("AUD_JPY", "NZD_JPY")]


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


def load(store) -> tuple[dict[str, pd.Series], dict[str, float]]:
    prices, rel_spread_bp = {}, {}
    for inst in rv.INSTRUMENTS:
        rows = store.query_candles(instrument=inst, granularity=GRAN, source=SOURCE)
        idx = pd.to_datetime([r["time_utc"] for r in rows], utc=True).as_unit("ns")
        mid = pd.Series([float(r["mid_c"]) for r in rows], index=idx).sort_index()
        sp = pd.Series([float(r["spread_close"]) for r in rows], index=idx).sort_index()
        prices[inst] = mid
        rel_spread_bp[inst] = float((sp / mid).mean() / 1e-4)  # mean relative spread (bp)
        print(f"[load] {inst} M5={len(mid)} rel_spread_bp={rel_spread_bp[inst]:.2f}", flush=True)
    return prices, rel_spread_bp


def main() -> None:
    if not _load_env("FOREX_BOT_RESEARCH_DATABASE_URL"):
        raise SystemExit("Research DB URL not found — aborting.")
    OUT.mkdir(parents=True, exist_ok=True)
    store = _store()
    prices, rel_spread_bp = load(store)

    logpx = rv.build_logprice_panel(prices)
    resid = rv.build_residuals(logpx)
    zpan = rv.zscore_residuals(resid)
    ev = rv.event_positions(len(logpx))
    print(f"[panel] common M5 bars={len(logpx)} events={len(ev)} "
          f"span={logpx.index[0]}..{logpx.index[-1]}", flush=True)

    # Construction meta + diagnostics + no-arb band
    diags = {}
    for c in rv.CROSSES:
        d = rv.relationship_diagnostics(resid[c])
        legs = rv.TRIANGLES[c]
        band = rel_spread_bp[c] + sum(rel_spread_bp[m] for m in legs)
        d["triangle_spread_band_bp"] = round(band, 2)
        d["resid_std_bp"] = round(d["resid_std_bp"], 3)
        diags[c] = d
    meta = {
        "instruments": rv.INSTRUMENTS, "triangles": {c: rv.TRIANGLES[c] for c in rv.CROSSES},
        "primary_L": rv.PRIMARY_L, "horizons_min": list(rv.HORIZONS_BARS.keys()),
        "z_stretch": rv.Z_STRETCH, "z_extreme": rv.Z_EXTREME,
        "common_m5_bars": len(logpx), "n_events": len(ev),
        "span_start": str(logpx.index[0]), "span_end": str(logpx.index[-1]),
        "diagnostics": diags, "rel_spread_bp": {k: round(v, 2) for k, v in rel_spread_bp.items()},
    }
    (OUT / "construction_meta.json").write_text(json.dumps(meta, indent=2))
    print("[write] construction_meta.json", flush=True)

    # Response per relationship + pooled
    per_rel = []
    for c in rv.CROSSES:
        r = rv.response_for_relationship(resid[c], zpan[c], ev)
        r.insert(0, "relationship", c)
        per_rel.append(r)
    per_rel_df = pd.concat(per_rel, ignore_index=True)
    per_rel_df.to_csv(OUT / "response_by_relationship.csv", index=False)
    pooled = per_rel_df.groupby(["bucket", "horizon_min"]).agg(
        mean_rev_bp=("mean_rev_bp", "mean"), p_revert=("p_revert", "mean"),
        mean_frac_closed=("mean_frac_closed", "mean"), n=("n", "sum")).reset_index()
    pooled.to_csv(OUT / "response_pooled.csv", index=False)
    print("[write] response_*.csv", flush=True)

    # Null comparison (primary)
    nul = rv.null_comparison(logpx, ev, seeds=200)
    nul.to_csv(OUT / "nulls.csv", index=False)
    print("[write] nulls.csv", flush=True)

    # Events-long for cross-sectional (stretched events, per relationship/year/session)
    sess_names = np.array(["asia", "london", "overlap", "new_york", "late"])
    sess = rv._session_codes(logpx.index)
    recs = []
    for c in rv.CROSSES:
        r = resid[c].to_numpy()
        z = zpan[c].to_numpy()
        for mins in (60, 240):
            hb = rv.HORIZONS_BARS[mins]
            for e in ev:
                if e + hb >= len(r) or np.isnan(z[e]) or abs(z[e]) < rv.Z_STRETCH:
                    continue
                rev = -np.sign(z[e]) * (r[e + hb] - r[e]) / 1e-4
                recs.append((c, mins, logpx.index[e].year,
                             sess_names[sess[e]], float(rev)))
    pd.DataFrame(recs, columns=["relationship", "horizon_min", "year", "session", "rev_bp"]
                 ).to_csv(OUT / "events_long.csv", index=False)
    print("[write] events_long.csv", flush=True)

    # Robustness: lookbacks, robust-z, thresholds (pooled randomized-rel null z)
    rob = []
    def pooled_z(**kw):
        nn = rv.null_comparison(logpx, ev, seeds=80, **kw)
        nn = nn[nn.null == "randomized_relationships"]
        return {int(h): (round(float(o), 3), round(float(z), 2))
                for h, o, z in zip(nn.horizon_min, nn.obs_bp, nn.z, strict=False)}
    for lb in (24, 96):
        for h, (o, z) in pooled_z(lookback=lb).items():
            rob.append({"variant": f"lookback_{lb}", "horizon_min": h, "obs_bp": o, "z": z})
    for h, (o, z) in pooled_z(robust=True).items():
        rob.append({"variant": "robust_z", "horizon_min": h, "obs_bp": o, "z": z})
    for thr in (1.5, 2.5):
        for h, (o, z) in pooled_z(z_stretch=thr).items():
            rob.append({"variant": f"thresh_{thr}", "horizon_min": h, "obs_bp": o, "z": z})
    pd.DataFrame(rob).to_csv(OUT / "robustness.csv", index=False)
    print("[write] robustness.csv", flush=True)

    # Shared-leg cointegration spreads (secondary relationship; half-life + stretched rev)
    from research.edge_discovery.relative_value_spread import rolling_z as _rz
    sl = []
    for a, b in SHARED_LEG_PAIRS:
        la, lb_ = logpx[a], logpx[b]
        beta = float(np.polyfit(lb_.to_numpy(), la.to_numpy(), 1)[0])
        spread = la - beta * lb_
        zs = _rz(spread, rv.PRIMARY_L).to_numpy()
        s = spread.to_numpy()
        hl = ar1_half_life(s)
        for mins in (60, 240):
            hb = rv.HORIZONS_BARS[mins]
            mask = (np.abs(zs[ev]) >= rv.Z_STRETCH) & (ev + hb < len(s))
            e = ev[mask]
            rev = -np.sign(zs[e]) * (s[e + hb] - s[e]) / 1e-4
            sl.append({"spread": f"{a}~{b}", "beta": round(beta, 3),
                       "half_life_bars": (round(hl["half_life_bars"], 1) if hl["half_life_bars"] else None),
                       "horizon_min": mins, "n": len(e),
                       "mean_rev_bp": round(float(np.nanmean(rev)), 3) if len(e) else None})
    pd.DataFrame(sl).to_csv(OUT / "shared_leg_spreads.csv", index=False)
    print("[write] shared_leg_spreads.csv", flush=True)
    print("[done]", flush=True)


if __name__ == "__main__":
    main()

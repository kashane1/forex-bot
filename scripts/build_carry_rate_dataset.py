#!/usr/bin/env python
"""Build the research-only carry / interest-rate-differential dataset from FRED.

Fetches harmonized OECD 3-month interbank rates (public FRED data; NO broker /
trading API), constructs per-currency rate series + per-instrument monthly carry
differentials, and writes provenance + diagnostics. NO trades, NO signals, NO
factor study, NO approval. Carry is a DATA asset, never presented as an edge.

Outputs under docs/research/carry_rates/.
"""
from __future__ import annotations

import json
import os
import pathlib
import time

import pandas as pd
from research.carry import carry_rates as cr
from research.cross_asset_features.fred import fetch_fred_observations

OUT = pathlib.Path("docs/research/carry_rates")
CACHE = pathlib.Path("data/external_features/.carry_rate_cache")
WINDOW_START = "1995-01-01"
WINDOW_END = "2026-05-31"
CORPUS_START = "2021-05-26"
CORPUS_END = "2026-05-26"
THROTTLE_S = 3.0


def _load_key() -> str:
    if os.environ.get("FRED_API_KEY", "").strip():
        return os.environ["FRED_API_KEY"]
    for fn in (".env.local", ".env"):
        p = pathlib.Path(fn)
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            s = line.strip()
            if s.startswith("FRED_API_KEY="):
                v = s.split("=", 1)[1].strip().strip('"').strip("'")
                if v:
                    return v
    raise SystemExit("FRED_API_KEY not found (env or .env) — aborting (no key, no fetch).")


def fetch_all(key: str) -> tuple[dict[str, pd.DataFrame], list[dict]]:
    CACHE.mkdir(parents=True, exist_ok=True)
    out, prov = {}, []
    for ccy in cr.CURRENCIES:
        sid = cr.RATE_SERIES[ccy]
        cache_path = CACHE / f"{sid}.csv"
        if cache_path.exists():
            df = pd.read_csv(cache_path, parse_dates=["date"])
            src = "cache"
        else:
            df = fetch_fred_observations(sid, api_key=key,
                                         observation_start=WINDOW_START, observation_end=WINDOW_END)
            df.to_csv(cache_path, index=False)
            src = "fred"
            time.sleep(THROTTLE_S)
        df["date"] = pd.to_datetime(df["date"], utc=True)
        out[ccy] = df
        prov.append({
            "currency": ccy, "series_id": sid, "source": src, "n_obs": len(df),
            "first": str(df["date"].min().date()), "last": str(df["date"].max().date()),
        })
        print(f"[fetch] {ccy} {sid} n={len(df)} ({src})", flush=True)
    return out, prov


def diagnostics(carry: pd.DataFrame, rate_matrix: pd.DataFrame) -> dict:
    corpus = carry[(carry["month"] >= CORPUS_START) & (carry["month"] <= CORPUS_END)]
    per_inst = {}
    for inst, g in corpus.groupby("instrument"):
        c = g["carry_diff"]
        per_inst[inst] = {
            "n_months": len(c),
            "mean_pct": round(float(c.mean()), 3), "std_pct": round(float(c.std()), 3),
            "min_pct": round(float(c.min()), 3), "max_pct": round(float(c.max()), 3),
            "pct_positive": round(float((c > 0).mean()), 3),
            "pct_negative": round(float((c < 0).mean()), 3),
            "sign_stable": bool((c > 0).all() or (c < 0).all()),
        }
    # currency ranking frequency over the corpus window (highest / lowest rate)
    rm = rate_matrix[(rate_matrix.index >= CORPUS_START) & (rate_matrix.index <= CORPUS_END)]
    highest = rm.idxmax(axis=1).value_counts(normalize=True).round(3).to_dict()
    lowest = rm.idxmin(axis=1).value_counts(normalize=True).round(3).to_dict()
    return {
        "corpus_window": [CORPUS_START, CORPUS_END],
        "n_months_corpus": int(rm.shape[0]),
        "per_instrument": per_inst,
        "rank_highest_freq": highest,
        "rank_lowest_freq": lowest,
    }


def main() -> None:
    key = _load_key()
    OUT.mkdir(parents=True, exist_ok=True)
    rate_by_ccy, prov = fetch_all(key)

    panel = cr.build_rate_panel(rate_by_ccy)
    panel.to_csv(OUT / "rate_series.csv", index=False)
    print(f"[write] rate_series.csv ({len(panel)})", flush=True)

    rate_matrix = cr.monthly_rate_matrix(panel)
    carry = cr.build_carry_differentials(rate_matrix)
    carry.to_csv(OUT / "carry_differentials.csv", index=False)
    print(f"[write] carry_differentials.csv ({len(carry)})", flush=True)

    tri = cr.triangular_rate_residual(rate_matrix)
    max_abs_resid = float(tri.abs().max().max())

    (OUT / "rate_provenance.json").write_text(json.dumps({
        "source": "FRED (Federal Reserve Bank of St. Louis), OECD 3-month interbank rates",
        "attribution": "OECD via FRED; harmonized series IR3TIB01<CC>M156N; public data.",
        "note_no_api_key": "FRED_API_KEY read from env/.env, NEVER committed.",
        "fetch_window": [WINDOW_START, WINDOW_END],
        "frequency": "monthly (annualized %)",
        "interbank_not_broker_financing": True,
        "series": prov,
        "triangular_rate_residual_max_abs_pct": round(max_abs_resid, 9),
        "strategy_evidence": False,
    }, indent=2))
    print(f"[write] rate_provenance.json (tri_resid_max={max_abs_resid:.2e})", flush=True)

    (OUT / "diagnostics.json").write_text(json.dumps(diagnostics(carry, rate_matrix), indent=2))
    print("[write] diagnostics.json", flush=True)
    print("[done]", flush=True)


if __name__ == "__main__":
    main()

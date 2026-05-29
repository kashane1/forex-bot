#!/usr/bin/env python3
"""Analyze whether SLOW macro/rates/calendar CONTEXT conditions USD/JPY tradeability.

DIAGNOSTIC ONLY. Reads the gitignored context parquet and reports, per slow-context cell,
the USD/JPY tradeability profile (cost spread/ATR, whipsaw, false-breakout, forward range)
on train AND validation. The question is *no-trade filtering / setup-conditioning* — never
a macro entry. Honest nulls reported. TEST sealed.

Output: research/usdjpy_macro_regime_context/analysis_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "research/usdjpy_macro_regime_context"
PARQUET = OUT_DIR / "context_dataset.parquet"
SUMMARY = OUT_DIR / "analysis_summary.json"

# context dimensions to condition on
CONTEXT_DIMS = [
    "us_2y_regime", "us_2y_trend", "us_10y_trend", "vix_regime", "vix_trend",
    "sp500_trend", "broad_usd_trend", "risk_off", "stab_bucket",
    "evt_any_window", "evt_pre", "evt_post", "evt_nfp_window", "evt_fomc_window",
]
# tradeability metrics: lower spread/atr, lower whipsaw, lower false-breakout = more tradeable
METRICS = ["spread_to_atr", "whipsaw_fwd", "false_breakout", "fwd_range_pips",
           "spread_pips", "atr_pips"]


def _profile(g: pd.DataFrame) -> dict:
    if not len(g):
        return {"n": 0}
    return {
        "n": len(g),
        "spread_to_atr_mean": round(float(g["spread_to_atr"].dropna().mean()), 4),
        "whipsaw_fwd_mean": round(float(g["whipsaw_fwd"].dropna().mean()), 4),
        "false_breakout_rate": round(float(g.loc[g["breakout_any"].fillna(False), "false_breakout"].mean()), 4)
        if int(g["breakout_any"].fillna(False).sum()) else None,
        "fwd_range_pips_median": round(float(g["fwd_range_pips"].dropna().median()), 4),
        "spread_pips_median": round(float(g["spread_pips"].dropna().median()), 4),
        "atr_pips_median": round(float(g["atr_pips"].dropna().median()), 4),
    }


def main() -> int:
    if not PARQUET.exists():
        raise SystemExit(f"missing {PARQUET}; run build_usdjpy_macro_regime_context_dataset.py first")
    ds = pd.read_parquet(PARQUET)
    print(f"loaded {len(ds):,} bars")

    summary = {
        "_meta": {
            "kind": "macro_regime_context_tradeability_analysis",
            "NOT_edge_claim": True, "NOT_strategy": True, "NOT_fast_news": True,
            "interpretation": "lower spread_to_atr / whipsaw / false_breakout = more tradeable; "
                              "macro context is a no-trade filter / conditioner, never an entry",
            "n_bars": len(ds),
            "metrics": METRICS,
        },
        "baseline": {sp: _profile(ds[ds["split"] == sp]) for sp in ("train", "validation")},
        "by_context": {},
    }

    for dim in CONTEXT_DIMS:
        block = {}
        for val, g in ds.groupby(dim, dropna=False, observed=True):
            key = str(val)
            block[key] = {sp: _profile(g[g["split"] == sp]) for sp in ("train", "validation")}
        summary["by_context"][dim] = block

    SUMMARY.write_text(json.dumps(summary, indent=2, default=str))
    print(f"wrote {SUMMARY} ({SUMMARY.stat().st_size:,} B)")

    # console: deviations vs baseline that are CONSISTENT across splits
    base = {sp: summary["baseline"][sp] for sp in ("train", "validation")}
    print(f"\nbaseline spread/atr t/v={base['train']['spread_to_atr_mean']}/{base['validation']['spread_to_atr_mean']} "
          f"whipsaw={base['train']['whipsaw_fwd_mean']}/{base['validation']['whipsaw_fwd_mean']} "
          f"falseBO={base['train']['false_breakout_rate']}/{base['validation']['false_breakout_rate']}")
    print("\n=== context cells where a hostility metric deviates CONSISTENTLY (both splits, same sign) ===")
    for dim, block in summary["by_context"].items():
        for val, sp in block.items():
            t, v = sp["train"], sp["validation"]
            if t.get("n", 0) < 300 or v.get("n", 0) < 300:
                continue
            for met, bkey in (("spread_to_atr_mean", "spread_to_atr_mean"),
                              ("whipsaw_fwd_mean", "whipsaw_fwd_mean"),
                              ("false_breakout_rate", "false_breakout_rate")):
                tb, vb = base["train"][bkey], base["validation"][bkey]
                tv, vv = t.get(met), v.get(met)
                if None in (tb, vb, tv, vv):
                    continue
                dt, dv = tv - tb, vv - vb
                if np.sign(dt) == np.sign(dv) and min(abs(dt / tb), abs(dv / vb)) > 0.05:
                    print(f"  {dim}={val:12s} {met}: train {tv} ({dt:+.4f}) val {vv} ({dv:+.4f}) "
                          f"n={t['n']}/{v['n']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

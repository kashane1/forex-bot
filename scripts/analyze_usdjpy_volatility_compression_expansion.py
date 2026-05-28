#!/usr/bin/env python3
"""Analyze the USD_JPY volatility-compression → expansion relationship (read-only).

DIAGNOSTIC ONLY. Answers, with PREDECLARED buckets (no tuning, no best-cell selection):

  1. Does compression predict larger future range?
  2. Does compression predict directional expansion?
  3. Does compression predict breakout follow-through?
  4. Does compression predict false breakout?
  5. Does any effect hold in BOTH train and validation?
  6. Does the effect survive spread/cost context?
  7. Is it session-dependent?
  8. Is it stronger in Tokyo→London / London→NY / NY windows?
  9. Is sample size preserved?
 10. Is it directionally tradable or only volatility-tradable?

Reads the gitignored dataset parquet produced by
``build_usdjpy_volatility_compression_expansion_dataset.py``. Reports null results
honestly; "expansion exists" is kept strictly separate from "tradable edge exists".

Usage:
    python scripts/analyze_usdjpy_volatility_compression_expansion.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.research.volatility_compression_expansion import (
    CompressionExpansionParams,
)

OUT_DIR = ROOT / "research/usdjpy_vol_compression_expansion"
PARQUET = OUT_DIR / "dataset.parquet"
SUMMARY = OUT_DIR / "analysis_summary.json"

PARAMS = CompressionExpansionParams()
PERCENTILE_FEATURES = ("range_pct", "atr_pct", "bandwidth_pct", "realized_vol_pct")
PRIMARY_HORIZON = 8
# Optimistic round-trip cost proxy (pips): two crossings of the active-session median
# spread (~1.7) + a small slippage allowance. Deliberately favorable to the thesis.
ROUNDTRIP_COST_PIPS = 2 * 1.7 + 1.0  # = 4.4


def _load() -> pd.DataFrame:
    if not PARQUET.exists():
        raise SystemExit(
            f"missing {PARQUET}; run build_usdjpy_volatility_compression_expansion_dataset.py first"
        )
    return pd.read_parquet(PARQUET)


def _compressed_flag(ds: pd.DataFrame, cut: float, min_agree: int = 3) -> pd.Series:
    """Consensus compression: >= min_agree of the 4 percentile features <= cut."""
    agree = sum((ds[f] <= cut).astype(int) for f in PERCENTILE_FEATURES)
    return agree >= min_agree


def _mean(s: pd.Series) -> float | None:
    s = s.dropna()
    return round(float(s.mean()), 4) if len(s) else None


def _rate(s: pd.Series) -> float | None:
    s = s.dropna()
    return round(float(s.mean()), 4) if len(s) else None


def _conditional_range(ds: pd.DataFrame, flag: pd.Series, h: int) -> dict:
    col = f"fwd_range_pips_h{h}"
    comp = ds.loc[flag, col]
    base = ds.loc[~flag, col]
    mc, mb = _mean(comp), _mean(base)
    return {
        "n_compressed": int(flag.sum()),
        "n_uncompressed": int((~flag).sum()),
        "mean_range_compressed": mc,
        "mean_range_uncompressed": mb,
        "ratio": round(mc / mb, 4) if (mc and mb) else None,
    }


def _relative_expansion(ds: pd.DataFrame, flag: pd.Series, h: int) -> dict:
    """Steelman the thesis: future range RELATIVE to the bar's own ATR. A compressed bar
    has low ATR, so even a modest absolute range could be a large *relative* expansion.
    rel = fwd_range_pips / atr_pips."""
    rel = (ds[f"fwd_range_pips_h{h}"] / ds["atr_pips"].replace(0, np.nan))
    comp = rel.loc[flag].dropna()
    base = rel.loc[~flag].dropna()
    mc = round(float(comp.mean()), 4) if len(comp) else None
    mb = round(float(base.mean()), 4) if len(base) else None
    return {
        "mean_fwd_range_over_atr_compressed": mc,
        "mean_fwd_range_over_atr_base": mb,
        "relative_ratio": round(mc / mb, 4) if (mc and mb) else None,
    }


def _directional(ds: pd.DataFrame, flag: pd.Series, h: int) -> dict:
    sm = ds.loc[flag, f"fwd_signed_move_pips_h{h}"].dropna()
    return {
        "mean_signed_move_pips": round(float(sm.mean()), 4) if len(sm) else None,
        "p_up": round(float((sm > 0).mean()), 4) if len(sm) else None,
        "mean_abs_move_pips": round(float(sm.abs().mean()), 4) if len(sm) else None,
        "n": len(sm),
    }


def _breakout_conditional(ds: pd.DataFrame, flag: pd.Series, h: int) -> dict:
    bo = ds[f"breakout_any_h{h}"].fillna(False)
    comp_bo = ds.loc[flag & bo]
    base_bo = ds.loc[(~flag) & bo]
    return {
        "p_followthrough_given_breakout_compressed": _rate(comp_bo[f"breakout_followthrough_h{h}"]),
        "p_followthrough_given_breakout_base": _rate(base_bo[f"breakout_followthrough_h{h}"]),
        "p_false_breakout_compressed": _rate(comp_bo[f"false_breakout_h{h}"]),
        "p_false_breakout_base": _rate(base_bo[f"false_breakout_h{h}"]),
        "breakout_rate_compressed": _rate(ds.loc[flag, f"breakout_any_h{h}"]),
        "breakout_rate_base": _rate(ds.loc[~flag, f"breakout_any_h{h}"]),
    }


def _cost_survival(ds: pd.DataFrame, flag: pd.Series, h: int) -> dict:
    """Optimistic: post-compression one-directional MFE (long perspective best case) and
    the larger of |MFE|/|MAE| vs round-trip cost. This is deliberately generous; a real
    strategy cannot pick the better side in advance."""
    sub = ds.loc[flag]
    mfe = sub[f"fwd_mfe_pips_h{h}"].dropna()
    mae = sub[f"fwd_mae_pips_h{h}"].dropna()
    best = pd.concat([mfe.abs(), mae.abs()], axis=1).max(axis=1)  # oracle side
    return {
        "mean_mfe_pips": round(float(mfe.mean()), 4) if len(mfe) else None,
        "mean_mae_pips": round(float(mae.mean()), 4) if len(mae) else None,
        "mean_oracle_best_excursion_pips": round(float(best.mean()), 4) if len(best) else None,
        "roundtrip_cost_pips": ROUNDTRIP_COST_PIPS,
        "oracle_best_minus_cost_pips": round(float(best.mean()) - ROUNDTRIP_COST_PIPS, 4) if len(best) else None,
        "mfe_minus_cost_pips": round(float(mfe.mean()) - ROUNDTRIP_COST_PIPS, 4) if len(mfe) else None,
        "note": "oracle_best picks the better of MFE/MAE in hindsight; NOT live-tradable",
    }


def _analyze_split(ds: pd.DataFrame, cut: float) -> dict:
    flag = _compressed_flag(ds, cut)
    out = {"compression_cut": cut, "horizons": {}}
    for h in PARAMS.horizons:
        out["horizons"][f"h{h}"] = {
            "range": _conditional_range(ds, flag, h),
            "relative_expansion": _relative_expansion(ds, flag, h),
            "directional": _directional(ds, flag, h),
            "breakout": _breakout_conditional(ds, flag, h),
            "cost": _cost_survival(ds, flag, h),
        }
    return out


def _by_session(ds: pd.DataFrame, cut: float, h: int) -> dict:
    flag = _compressed_flag(ds, cut)
    res = {}
    for sess, g in ds.groupby("session", observed=True):
        gflag = flag.loc[g.index]
        cr = _conditional_range(g, gflag, h)
        dr = _directional(g, gflag, h)
        res[str(sess)] = {
            "n_compressed": cr["n_compressed"],
            "range_ratio": cr["ratio"],
            "mean_range_compressed": cr["mean_range_compressed"],
            "p_up": dr["p_up"],
            "mean_signed_move_pips": dr["mean_signed_move_pips"],
        }
    return res


def main() -> int:
    ds = _load()
    print(f"loaded dataset: {len(ds):,} bars")
    summary = {
        "_meta": {
            "kind": "vol_compression_expansion_analysis",
            "NOT_edge_claim": True,
            "primary_horizon_bars": PRIMARY_HORIZON,
            "primary_cut": PARAMS.primary_cut,
            "compression_cut_grid": list(PARAMS.compression_cuts),
            "compressed_def": ">= 3 of 4 percentile features (range/atr/bandwidth/realized_vol) <= cut",
            "roundtrip_cost_pips_optimistic": ROUNDTRIP_COST_PIPS,
            "n_bars": len(ds),
        },
        "by_split": {},
        "robustness_grid_primary_horizon": {},
        "by_session_primary": {},
        "per_feature_range_ratio_primary": {},
    }

    # Q1-Q6,Q9,Q10: per split, primary cut, all horizons
    for split in ("train", "validation"):
        sub = ds[ds["split"] == split]
        summary["by_split"][split] = _analyze_split(sub, PARAMS.primary_cut)

    # Q5 robustness: range ratio at primary horizon across the predeclared cut grid, per split
    for split in ("train", "validation"):
        sub = ds[ds["split"] == split]
        grid = {}
        for cut in PARAMS.compression_cuts:
            flag = _compressed_flag(sub, cut)
            grid[str(cut)] = _conditional_range(sub, flag, PRIMARY_HORIZON)
        summary["robustness_grid_primary_horizon"][split] = grid

    # Q7,Q8: by session, per split, primary cut/horizon
    for split in ("train", "validation"):
        sub = ds[ds["split"] == split]
        summary["by_session_primary"][split] = _by_session(sub, PARAMS.primary_cut, PRIMARY_HORIZON)

    # per-single-feature range ratio (which compression notion matters most), full sample
    for feat in PERCENTILE_FEATURES:
        feat_ratio = {}
        for split in ("train", "validation"):
            sub = ds[ds["split"] == split]
            flag = sub[feat] <= PARAMS.primary_cut
            feat_ratio[split] = _conditional_range(sub, flag, PRIMARY_HORIZON)["ratio"]
        summary["per_feature_range_ratio_primary"][feat] = feat_ratio
    # inside-bar as a compression notion
    inside_ratio = {}
    for split in ("train", "validation"):
        sub = ds[ds["split"] == split]
        flag = sub["inside_bar_count"] >= 2
        inside_ratio[split] = _conditional_range(sub, flag, PRIMARY_HORIZON)["ratio"]
    summary["per_feature_range_ratio_primary"]["inside_bar_count>=2"] = inside_ratio

    SUMMARY.write_text(json.dumps(summary, indent=2, default=str))
    print(f"wrote {SUMMARY} ({SUMMARY.stat().st_size:,} B)")

    # console highlights
    for split in ("train", "validation"):
        h = PRIMARY_HORIZON
        blk = summary["by_split"][split]["horizons"][f"h{h}"]
        r = blk["range"]
        rel = blk["relative_expansion"]
        d = blk["directional"]
        c = blk["cost"]
        print(f"\n[{split}] h{h}: abs range ratio comp/base = {r['ratio']} "
              f"({r['mean_range_compressed']} vs {r['mean_range_uncompressed']}; "
              f"n_comp={r['n_compressed']}) | rel(range/ATR) ratio = {rel['relative_ratio']} "
              f"({rel['mean_fwd_range_over_atr_compressed']} vs {rel['mean_fwd_range_over_atr_base']})")
        print(f"          direction p_up={d['p_up']} signed={d['mean_signed_move_pips']} "
              f"| oracle_best-cost={c['oracle_best_minus_cost_pips']} mfe-cost={c['mfe_minus_cost_pips']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

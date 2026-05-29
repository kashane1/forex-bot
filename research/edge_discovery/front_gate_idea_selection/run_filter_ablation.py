#!/usr/bin/env python3
"""Phase 5 — filter ablation for the strongest surviving prototype.

Phase 4 left ``zscore_reversion_h4`` as the strongest *information* signal
(beats every structure-matched null) but with no robust post-cost edge
(net-negative under conservative cost, 2023-regime-dominated, pair/year
sign-flips). This phase asks the protocol's filter question: do principled
filters (low-volatility regime, stronger extension, quiet session, cost-
advantaged pair, direction) *add edge*, or do they only *reduce the sample*?

The filters are chosen on prior/structural grounds (NOT in-sample winners) to
avoid manufacturing an overfit result.

Diagnostic / level-2 only. No strategy, no campaign, no approval, no lockbox.

Run:
    PYTHONPATH=$PWD/src python -m \
        research.edge_discovery.front_gate_idea_selection.run_filter_ablation
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from research.edge_discovery.costs import financing_stress_fraction  # noqa: E402
from research.edge_discovery.filter_ablation import filter_ablation  # noqa: E402
from research.edge_discovery.front_gate_idea_selection.run_signal_probes import (  # noqa: E402
    _load_pairs,
)
from research.edge_discovery.matched_nulls import session_bucket_utc  # noqa: E402
from research.edge_discovery.real_data import resolve_h4_store_path  # noqa: E402

OUT_DIR = REPO_ROOT / "research" / "edge_discovery" / "front_gate_idea_selection"
WINDOW = 12
SLIP_PIPS = 0.2
Z_THRESH = 2.0
LENGTH = 20
COST_ADVANTAGED = {"USD_JPY", "GBP_USD", "AUD_USD", "EUR_USD"}  # Phase-2 cheapest pairs
FILTERS = ["f_low_vol", "f_strong_extension", "f_quiet_session", "f_cost_adv_pair", "f_long_side"]


def _build_signals(pairs) -> pd.DataFrame:
    rows = []
    for inst, pdat in pairs.items():
        mid = pdat.mid
        n = len(mid)
        s = pd.Series(mid)
        ma = s.rolling(LENGTH).mean().shift(1)
        sd = s.rolling(LENGTH).std().shift(1)
        z = (s - ma) / sd
        # trailing-window ATR percentile (no lookahead) for the vol-regime filter
        tr = np.maximum.reduce([
            pdat.high - pdat.low,
            np.abs(pdat.high - np.concatenate([[mid[0]], mid[:-1]])),
            np.abs(pdat.low - np.concatenate([[mid[0]], mid[:-1]])),
        ])
        atr = pd.Series(tr).rolling(14).mean()
        atr_pct = atr.rolling(250).apply(lambda a: (a[-1] >= a).mean(), raw=True).shift(1)
        slip_px = SLIP_PIPS * pdat.pip
        for i in range(n):
            zv = z.iloc[i]
            if not np.isfinite(zv) or abs(zv) < Z_THRESH:
                continue
            if i + WINDOW >= n:
                continue
            side = int(-np.sign(zv))
            entry, exit_ = mid[i], mid[i + WINDOW]
            if entry <= 0 or exit_ <= 0:
                continue
            raw = np.log(exit_ / entry)
            signed = side * raw
            cost = (pdat.spread_px[i] + 2 * slip_px) / entry
            # conservative: flat 1.5-pip spread + 0.2 slip + worst-case financing over the hold
            cons_cost = (1.5 * pdat.pip + 2 * slip_px) / entry + financing_stress_fraction(
                inst, bars_held=WINDOW, hours_per_bar=4.0)
            ts = pd.Timestamp(pdat.times[i])
            sess = session_bucket_utc(ts)
            pv = atr_pct.iloc[i]
            rows.append({
                "instrument": inst, "side": side, "year": ts.year,
                "log_return": signed, "log_return_post_cost": signed - cost,
                "log_return_post_cost_conservative": signed - cons_cost,
                "f_low_vol": bool(np.isfinite(pv) and pv <= 0.33),
                "f_strong_extension": bool(abs(zv) >= 2.5),
                "f_quiet_session": sess in ("asia", "london"),
                "f_cost_adv_pair": inst in COST_ADVANTAGED,
                "f_long_side": side > 0,
            })
    return pd.DataFrame(rows)


def _stage(s):
    return {
        "stage": s.stage, "filters_applied": list(s.filters_applied), "n": s.n,
        "reduction_ratio": round(s.reduction_ratio, 4),
        "expectancy": round(s.expectancy, 7),
        "expectancy_se": round(s.expectancy_se, 7),
        "post_cost_expectancy": round(s.post_cost_expectancy, 7)
        if s.post_cost_expectancy is not None else None,
        "hit_rate": round(s.hit_rate, 4),
        "top_pair_concentration": round(s.top_pair_concentration, 4),
    }


def main() -> int:
    db_path = resolve_h4_store_path(REPO_ROOT)
    if db_path is None:
        print("BLOCKED: store not found.", file=sys.stderr)
        return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    h4 = _load_pairs(db_path, "H4")
    signals = _build_signals(h4)
    res = filter_ablation(signals, filter_cols=FILTERS, value_col="log_return",
                          post_cost_col="log_return_post_cost", cumulative_order=FILTERS)

    # Decisive stationarity check: the edge-adding subset (low_vol & strong &
    # quiet session) post-cost by year and by pair, to test whether the filters
    # fix the Phase-4 2023-regime dominance or merely concentrate into it.
    sub = signals[signals["f_low_vol"] & signals["f_strong_extension"] & signals["f_quiet_session"]]
    by_year = {str(int(y)): {"n": len(g), "post_cost": round(float(g["log_return_post_cost"].mean()), 7)}
               for y, g in sub.groupby("year")}
    by_pair = {p: {"n": len(g), "post_cost": round(float(g["log_return_post_cost"].mean()), 7)}
               for p, g in sub.groupby("instrument")}
    n_pos_years = sum(1 for v in by_year.values() if v["post_cost"] > 0)
    cons_by_year = {str(int(y)): round(float(g["log_return_post_cost_conservative"].mean()), 7)
                    for y, g in sub.groupby("year")}
    n_pos_years_cons = sum(1 for v in cons_by_year.values() if v > 0)
    subset_stability = {
        "subset": "f_low_vol & f_strong_extension & f_quiet_session",
        "n": len(sub),
        "post_cost_overall_optimistic": round(float(sub["log_return_post_cost"].mean()), 7),
        "post_cost_overall_conservative": round(float(sub["log_return_post_cost_conservative"].mean()), 7),
        "positive_years_optimistic": f"{n_pos_years}/{len(by_year)}",
        "positive_years_conservative": f"{n_pos_years_cons}/{len(cons_by_year)}",
        "by_year_optimistic": by_year,
        "by_year_conservative": cons_by_year,
        "by_pair_optimistic": by_pair,
    }

    summary_rows = [{"kind": "trigger_only", **_stage(res.trigger_only)}]
    for s in res.single_filter:
        summary_rows.append({"kind": "single_filter", **_stage(s)})
    for s in res.cumulative:
        summary_rows.append({"kind": "cumulative", **_stage(s)})
    for s in res.leave_one_out:
        summary_rows.append({"kind": "leave_one_out", **_stage(s)})
    summary_rows.append({"kind": "all_filters", **_stage(res.all_filters)})
    pd.DataFrame(summary_rows).to_csv(OUT_DIR / "filter_ablation_probe_summary.csv", index=False)

    contrib_rows = [{
        "filter": c.filter,
        "marginal_expectancy_gain": round(c.marginal_expectancy_gain, 7),
        "leave_out_delta": round(c.leave_out_delta, 7),
        "reduction_ratio": round(c.reduction_ratio, 4),
        "edge_per_unit_reduction": round(c.edge_per_unit_reduction, 7),
        "flags": ";".join(c.flags),
    } for c in res.contributions]
    pd.DataFrame(contrib_rows).to_csv(OUT_DIR / "filter_contribution_scores.csv", index=False)

    failure_reasons = {
        c.filter: [f for f in c.flags if f != "FILTER_ADDS_EDGE"]
        for c in res.contributions
        if any(f in c.flags for f in ("FILTER_ONLY_REDUCES_SAMPLE", "FILTER_HURTS_EDGE",
                                      "FILTER_TOO_SPARSE", "FILTER_PAIR_SPECIFIC_ONLY"))
    }
    (OUT_DIR / "filter_failure_reasons.json").write_text(
        json.dumps({"strategy_evidence": False, "diagnostic_only": True,
                    "prototype": "zscore_reversion_h4", "window_bars": WINDOW,
                    "trigger_only_expectancy": round(res.trigger_only.expectancy, 7),
                    "trigger_only_post_cost": round(res.trigger_only.post_cost_expectancy, 7),
                    "all_filters_n": res.all_filters.n,
                    "all_filters_post_cost": round(res.all_filters.post_cost_expectancy, 7),
                    "failure_reasons": failure_reasons,
                    "edge_adding_subset_stability": subset_stability,
                    "notes": res.notes}, indent=2) + "\n", encoding="utf-8")

    print(pd.DataFrame(summary_rows).to_string(index=False))
    print("\nCONTRIBUTIONS:")
    print(pd.DataFrame(contrib_rows).to_string(index=False))
    print("\nEDGE-ADDING SUBSET (low_vol & strong & quiet), n=", subset_stability["n"])
    print("  optimistic  overall:", subset_stability["post_cost_overall_optimistic"],
          "pos-years:", subset_stability["positive_years_optimistic"])
    print("  conservative overall:", subset_stability["post_cost_overall_conservative"],
          "pos-years:", subset_stability["positive_years_conservative"])
    print("  by_year_conservative:", json.dumps(subset_stability["by_year_conservative"]))
    print("  by_pair_optimistic:", json.dumps(subset_stability["by_pair_optimistic"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

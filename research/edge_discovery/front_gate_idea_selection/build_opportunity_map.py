#!/usr/bin/env python3
"""Phase 2 — market opportunity-map refresh for the edge-discovery front gate.

Reads the local deduped bid/ask candle store (H4 + H1 on the seven majors) and
produces a compact opportunity map: spread/ATR, median ATR in pips, median
spread in pips, round-trip cost, cost-in-R for common stop sizes, session/
weekday/volatility behaviour, and cost-feasibility flags from the lab's
``cost_feasibility`` module.

Diagnostic / idea-screening only. No strategy, no campaign, no broker orders,
no test lockbox, no approval. Uses local existing data only.

Run:
    PYTHONPATH=$PWD/src python -m \
        research.edge_discovery.front_gate_idea_selection.build_opportunity_map
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.data.candle_dedupe import DEDUPE_POLICY  # noqa: E402
from forex_bot.data.db import Database  # noqa: E402
from forex_bot.data.repositories import CandleRepo  # noqa: E402
from research.cost_atlas.loader import candles_to_frame  # noqa: E402
from research.cost_atlas.metrics import compute_bar_metrics  # noqa: E402
from research.edge_discovery.cost_feasibility import (  # noqa: E402
    classify_cost_feasibility,
    min_target_r_to_overcome,
    round_trip_cost_pips,
)
from research.edge_discovery.real_data import SEVEN_MAJORS, resolve_h4_store_path  # noqa: E402

OUT_DIR = REPO_ROOT / "research" / "edge_discovery" / "front_gate_idea_selection"
TIMEFRAMES = ("H4", "H1")
SLIP_PIPS = 0.2
HOSTILE_RATIO = 0.25  # lab default; M5≈0.45 was hostile, H4 is far below


def _load_frame(db_path: Path, instrument: str, granularity: str) -> tuple[pd.DataFrame, dict]:
    db = Database(db_path)
    try:
        repo = CandleRepo(db)
        candles, stats = repo.list_with_dedupe_stats(
            instrument, granularity, completed_only=True
        )
    finally:
        db.close()
    frame = candles_to_frame(candles)
    prov = {
        "instrument": instrument,
        "granularity": granularity,
        "dedupe_policy": DEDUPE_POLICY,
        "raw_count": stats.raw_count,
        "deduped_count": stats.deduped_count,
        "bar_count": len(frame),
    }
    return frame, prov


def _cell_cost_row(label: str, spread_pips: float, atr_pips: float, ratio: float, kind: str) -> dict:
    """Cost summary for one aggregated cell, with cost-in-R at 1.0x/1.5x ATR stops."""
    rt = round_trip_cost_pips(spread_pips, slip_pips=SLIP_PIPS)
    cell = classify_cost_feasibility(
        label, ratio, hostile_ratio=HOSTILE_RATIO, spread_pips=spread_pips,
        stop_pips=max(atr_pips, 1e-9), kind=kind,
    )
    cost_in_r_1x = min_target_r_to_overcome(rt, max(atr_pips, 1e-9))
    cost_in_r_1_5x = min_target_r_to_overcome(rt, max(1.5 * atr_pips, 1e-9))
    return {
        "median_spread_pips": round(spread_pips, 4),
        "median_atr_pips": round(atr_pips, 4),
        "spread_atr_ratio": round(ratio, 5),
        "round_trip_cost_pips": round(rt, 4),
        "cost_in_R_stop_1.0xATR": round(cost_in_r_1x, 5),
        "cost_in_R_stop_1.5xATR": round(cost_in_r_1_5x, 5),
        "opportunity_score": round(cell.opportunity_score, 4),
        "flags": ";".join(cell.flags),
    }


def main() -> int:
    db_path = resolve_h4_store_path(REPO_ROOT)
    if db_path is None:
        print("BLOCKED: H4/H1 store not found (set EDGE_DISCOVERY_H4_DB).", file=sys.stderr)
        return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    per_tf_metrics: dict[str, pd.DataFrame] = {}
    provenance: list[dict] = []
    for tf in TIMEFRAMES:
        pieces = []
        for inst in SEVEN_MAJORS:
            frame, prov = _load_frame(db_path, inst, tf)
            provenance.append(prov)
            if frame.empty:
                continue
            m = compute_bar_metrics(inst, frame)
            m["instrument"] = inst
            m["timeframe"] = tf
            pieces.append(m)
        per_tf_metrics[tf] = pd.concat(pieces, ignore_index=False)

    all_bars = pd.concat(per_tf_metrics.values(), ignore_index=False)
    all_bars = all_bars.dropna(subset=["spread_to_atr_pct", "atr_pips"])
    all_bars["ratio"] = all_bars["spread_to_atr_pct"] / 100.0

    # ---- by pair x timeframe -------------------------------------------------
    pt_rows = []
    for (inst, tf), g in all_bars.groupby(["instrument", "timeframe"]):
        row = {"instrument": inst, "timeframe": tf, "n_bars": len(g)}
        row.update(_cell_cost_row(
            f"{inst}/{tf}",
            float(g["spread_pips"].median()),
            float(g["atr_pips"].median()),
            float(g["ratio"].median()),
            kind="pair",
        ))
        pt_rows.append(row)
    pt_df = pd.DataFrame(pt_rows).sort_values(["timeframe", "spread_atr_ratio"])
    pt_df.to_csv(OUT_DIR / "opportunity_map_by_pair_timeframe.csv", index=False)

    # ---- by pair x timeframe x session --------------------------------------
    sess_rows = []
    for (inst, tf, sess), g in all_bars.groupby(["instrument", "timeframe", "session"]):
        row = {"instrument": inst, "timeframe": tf, "session": sess, "n_bars": len(g)}
        row.update(_cell_cost_row(
            f"{inst}/{tf}/{sess}",
            float(g["spread_pips"].median()),
            float(g["atr_pips"].median()),
            float(g["ratio"].median()),
            kind="session",
        ))
        sess_rows.append(row)
    sess_df = pd.DataFrame(sess_rows).sort_values(["timeframe", "session", "spread_atr_ratio"])
    sess_df.to_csv(OUT_DIR / "opportunity_map_by_session.csv", index=False)

    # ---- by pair x timeframe x weekday --------------------------------------
    wd_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    wd_rows = []
    for (inst, tf, wd), g in all_bars.groupby(["instrument", "timeframe", "weekday"]):
        row = {"instrument": inst, "timeframe": tf, "weekday": wd, "n_bars": len(g)}
        row.update(_cell_cost_row(
            f"{inst}/{tf}/{wd}",
            float(g["spread_pips"].median()),
            float(g["atr_pips"].median()),
            float(g["ratio"].median()),
            kind=None,
        ))
        wd_rows.append(row)
    wd_df = pd.DataFrame(wd_rows)
    wd_df["_wd"] = wd_df["weekday"].map(lambda w: wd_order.index(w) if w in wd_order else 99)
    wd_df = wd_df.sort_values(["timeframe", "instrument", "_wd"]).drop(columns="_wd")
    wd_df.to_csv(OUT_DIR / "opportunity_map_by_weekday.csv", index=False)

    # ---- volatility-regime / session expansion (median ATR pips) ------------
    vol_expansion = {}
    for tf in TIMEFRAMES:
        sub = all_bars[all_bars["timeframe"] == tf]
        by_sess_atr = sub.groupby("session")["atr_pips"].median().round(3).to_dict()
        by_vol = sub.groupby("vol_regime")["atr_pips"].median().round(3).to_dict()
        vol_expansion[tf] = {
            "median_atr_pips_by_session": by_sess_atr,
            "median_atr_pips_by_vol_regime": by_vol,
        }

    # ---- cost-feasibility flags payload -------------------------------------
    flags_payload = {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "hostile_ratio": HOSTILE_RATIO,
        "by_pair_timeframe": pt_df.to_dict(orient="records"),
        "by_pair_timeframe_session": sess_df.to_dict(orient="records"),
        "hostile_cells": sess_df[sess_df["flags"].str.contains("HOSTILE")][
            ["instrument", "timeframe", "session", "spread_atr_ratio", "flags"]
        ].to_dict(orient="records"),
    }
    (OUT_DIR / "cost_feasibility_flags.json").write_text(
        json.dumps(flags_payload, indent=2) + "\n", encoding="utf-8"
    )

    # ---- summary -------------------------------------------------------------
    cheapest_pt = pt_df.nsmallest(5, "spread_atr_ratio")[
        ["instrument", "timeframe", "spread_atr_ratio", "flags"]
    ].to_dict(orient="records")
    cheapest_sess = sess_df.nsmallest(8, "spread_atr_ratio")[
        ["instrument", "timeframe", "session", "spread_atr_ratio", "flags"]
    ].to_dict(orient="records")
    most_vol_pt = pt_df.nlargest(5, "median_atr_pips")[
        ["instrument", "timeframe", "median_atr_pips"]
    ].to_dict(orient="records")
    usdjpy = pt_df[pt_df["instrument"] == "USD_JPY"][
        ["timeframe", "spread_atr_ratio", "median_atr_pips", "flags"]
    ].to_dict(orient="records")
    summary = {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "timeframes": list(TIMEFRAMES),
        "instruments": list(SEVEN_MAJORS),
        "hostile_ratio": HOSTILE_RATIO,
        "n_hostile_session_cells": int(sess_df["flags"].str.contains("HOSTILE").sum()),
        "cheapest_pair_timeframe": cheapest_pt,
        "cheapest_pair_timeframe_session": cheapest_sess,
        "most_volatile_pair_timeframe": most_vol_pt,
        "usd_jpy_cells": usdjpy,
        "volatility_expansion": vol_expansion,
        "provenance": provenance,
    }
    (OUT_DIR / "opportunity_map_summary.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8"
    )

    print(f"Wrote opportunity map to {OUT_DIR}")
    print(f"  pair x timeframe rows: {len(pt_df)}")
    print(f"  pair x timeframe x session rows: {len(sess_df)}")
    print(f"  pair x timeframe x weekday rows: {len(wd_df)}")
    print(f"  hostile session cells: {summary['n_hostile_session_cells']}")
    print("Cheapest pair/timeframe:")
    print(pt_df.head(5).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

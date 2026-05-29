#!/usr/bin/env python3
"""Phase 4 — matched-null + matrix-sanity screening for the surviving probes.

Phase 3 left two prototypes with forward-return information beyond a cost-
matched random-timestamp null: ``zscore_reversion_h4`` and
``failed_breakout_fade_h4``. This phase subjects them to the protocol's binding
test — *structure-matched* nulls (side-shuffled, pair-matched, session-matched,
holding-period-matched, full matched null) at the horizon they would trade
(h12) — plus pair-holdout / time-block-holdout fragility and a best-of-N
selection-noise check across the screened variants.

Diagnostic / level-2 only. No strategy, no campaign, no approval, no test
lockbox. Frames and ledgers are rebuilt in-memory from the local store (nothing
bulky is written).

Run:
    PYTHONPATH=$PWD/src python -m \
        research.edge_discovery.front_gate_idea_selection.run_matched_null_screening
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

from research.edge_discovery.costs import apply_cost_overlay  # noqa: E402
from research.edge_discovery.front_gate_idea_selection.data_access import load_frame  # noqa: E402
from research.edge_discovery.front_gate_idea_selection.run_signal_probes import (  # noqa: E402
    _load_pairs,
    proto_failed_breakout_fade,
    proto_zscore_reversion,
)
from research.edge_discovery.matched_nulls import (  # noqa: E402
    interpret_matched_null,
    matched_null_baseline,
)
from research.edge_discovery.multiple_comparison import (  # noqa: E402
    holdout_stability,
    matrix_sanity,
)
from research.edge_discovery.real_data import SEVEN_MAJORS, resolve_h4_store_path  # noqa: E402

OUT_DIR = REPO_ROOT / "research" / "edge_discovery" / "front_gate_idea_selection"
WINDOW = 12  # h12 — the horizon at which Phase 3 post-cost turned positive
SEEDS = range(40)
SLIP_PIPS = 0.2
MODES = (
    "timestamp_random_same_pair",
    "side_shuffled",
    "pair_matched_random",
    "session_matched_random",
    "holding_period_matched_random",
    "full_matched_null",
)


def _frames_by_pair(db_path: Path) -> dict[str, pd.DataFrame]:
    frames = {}
    for inst in SEVEN_MAJORS:
        frame = load_frame(db_path, inst, "H4")
        if not frame.empty:
            frames[inst] = frame
    return frames


def _per_row_post_cost(pairs, ledger, horizon):
    """Per-signal post-cost signed log-return with instrument + year, for the
    holdout-fragility checks (uses realized per-bar spread + slip)."""
    recs = []
    for inst, g in ledger.groupby("instrument"):
        pdat = pairs.get(inst)
        if pdat is None:
            continue
        n = len(pdat.mid)
        slip_px = SLIP_PIPS * pdat.pip
        for _, r in g.iterrows():
            pos = pdat.pos_by_time.get(np.datetime64(r["entry_time"]))
            if pos is None or pos + horizon >= n:
                continue
            entry, exit_ = pdat.mid[pos], pdat.mid[pos + horizon]
            if entry <= 0 or exit_ <= 0:
                continue
            raw = np.log(exit_ / entry)
            cost = (pdat.spread_px[pos] + 2 * slip_px) / entry
            recs.append({
                "instrument": inst,
                "year": pd.Timestamp(r["entry_time"]).year,
                "post": r["side"] * raw - cost,
            })
    return pd.DataFrame(recs)


def _holdout_blocks(df: pd.DataFrame, key: str):
    grp = df.groupby(key)["post"]
    values = {str(k): float(v) for k, v in grp.mean().items()}
    weights = {str(k): float(v) for k, v in grp.count().items()}
    return values, weights


def _screen(name, pairs, frames, ledger):
    ledger = ledger.copy()
    ledger["bars_held"] = WINDOW
    mode_rows = []
    for mode in MODES:
        try:
            res = matched_null_baseline(
                ledger, frames, mode=mode, window_bars=WINDOW, seeds=SEEDS,
                apply_cost_overlay_fn=apply_cost_overlay,
                cost_kwargs={"spread_pips": 1.5, "slip_pips": SLIP_PIPS},
            )
        except Exception as exc:
            mode_rows.append({"prototype": name, "mode": mode, "error": str(exc)})
            continue
        interp = interpret_matched_null(res)
        mode_rows.append({
            "prototype": name, "mode": mode,
            "n_trades": res.n_trades,
            "strategy_expectancy": round(res.strategy_expectancy, 7),
            "null_mean": round(res.null_mean, 7),
            "null_p95": round(res.null_p95, 7),
            "prob_null_ge_strategy": round(res.prob_null_ge_strategy, 4),
            "strategy_percentile": round(res.strategy_percentile, 2),
            "effect_size": round(res.effect_size, 3) if res.effect_size == res.effect_size else None,
            "flags": ";".join(interp["flags"]),
        })

    # holdout fragility on per-row post-cost h12
    rows = _per_row_post_cost(pairs, ledger, WINDOW)
    pair_vals, pair_w = _holdout_blocks(rows, "instrument")
    year_vals, year_w = _holdout_blocks(rows, "year")
    pair_ho = holdout_stability(pair_vals, kind="pair", weights=pair_w, higher_is_better=True)
    year_ho = holdout_stability(year_vals, kind="time_block", weights=year_w, higher_is_better=True)
    return mode_rows, {
        "prototype": name,
        "full_post_cost_h12": round(float(rows["post"].mean()), 7),
        "pair_holdout": {
            "full": round(pair_ho.full_value, 7), "min": round(pair_ho.min_value, 7),
            "max": round(pair_ho.max_value, 7), "sign_flips": pair_ho.sign_flips,
            "dominant_pair": pair_ho.dominant_group,
            "per_pair_mean": {k: round(v, 7) for k, v in pair_vals.items()},
        },
        "time_block_holdout": {
            "full": round(year_ho.full_value, 7), "min": round(year_ho.min_value, 7),
            "max": round(year_ho.max_value, 7), "sign_flips": year_ho.sign_flips,
            "dominant_year": year_ho.dominant_group,
            "per_year_mean": {k: round(v, 7) for k, v in year_vals.items()},
        },
    }


def main() -> int:
    db_path = resolve_h4_store_path(REPO_ROOT)
    if db_path is None:
        print("BLOCKED: store not found.", file=sys.stderr)
        return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    h4 = _load_pairs(db_path, "H4")
    frames = _frames_by_pair(db_path)
    protos = {
        "zscore_reversion_h4": proto_zscore_reversion(h4),
        "failed_breakout_fade_h4": proto_failed_breakout_fade(h4),
    }

    all_mode_rows, fragility = [], {}
    for name, ledger in protos.items():
        mode_rows, frag = _screen(name, h4, frames, ledger)
        all_mode_rows.extend(mode_rows)
        fragility[name] = frag

    mode_df = pd.DataFrame(all_mode_rows)
    mode_df.to_csv(OUT_DIR / "matched_null_probe_summary.csv", index=False)
    (OUT_DIR / "matched_null_probe_results.json").write_text(
        json.dumps({"strategy_evidence": False, "diagnostic_only": True,
                    "window_bars": WINDOW, "seeds": list(SEEDS),
                    "cost_overlay": {"spread_pips": 1.5, "slip_pips": SLIP_PIPS, "financing": True},
                    "modes": list(MODES), "results": all_mode_rows,
                    "fragility": fragility}, indent=2) + "\n", encoding="utf-8")

    # ---- best-of-N selection-noise across the screened variants -------------
    # Variants = the h12 post-cost expectancy of every Phase-3 prototype.
    fwd = json.loads((OUT_DIR / "signal_probe_forward_returns.json").read_text())["results"]
    rows = []
    for proto, hz in fwd.items():
        v = hz.get(str(WINDOW), {})
        if v.get("n"):
            rows.append({"variant": proto, "post_h12": v["mean_fwd_logret_post_cost"]})
    var_df = pd.DataFrame(rows)
    pair_vals = fragility["zscore_reversion_h4"]["pair_holdout"]["per_pair_mean"]
    pair_w = {k: 1.0 for k in pair_vals}
    ms = matrix_sanity(
        var_df, metric_col="post_h12", label_col="variant", higher_is_better=True,
        null_reference=0.0, group_kind="pair",
        best_group_values=pair_vals, best_group_weights=pair_w,
        too_many_variants=50,
    )
    matrix_payload = {
        "strategy_evidence": False, "diagnostic_only": True,
        "n_variants_screened_total": "6 prototypes x 5 horizons = 30 (forward-return screen)",
        "n_variants_in_matrix": int(ms.n_variants),
        "best_label": ms.best_label, "best_value": round(ms.best_value, 7),
        "median_value": round(ms.median_value, 7),
        "best_minus_median": round(ms.best_minus_median, 7),
        "null_reference": ms.null_reference,
        "best_vs_null": round(ms.best_vs_null, 7) if ms.best_vs_null is not None else None,
        "expected_max_under_null": round(ms.expected_max_under_null, 7),
        "deflated_improvement": round(ms.deflated_improvement, 7),
        "prob_best_le_null_max": round(ms.prob_best_le_null_max, 4),
        "fragility_score": round(ms.fragility_score, 4),
        "flags": list(ms.flags),
        "pair_holdout_sign_flips": ms.pair_holdout.sign_flips if ms.pair_holdout else None,
        "notes": ms.notes,
    }
    (OUT_DIR / "matrix_sanity_probe_results.json").write_text(
        json.dumps(matrix_payload, indent=2, default=str) + "\n", encoding="utf-8")

    (OUT_DIR / "probe_compatibility_gaps.json").write_text(
        json.dumps({"diagnostic_only": True, "gaps": [
            {"item": "carry/financing matched null",
             "reason": "no carry/swap-rate table locally; only worst-case forex_bot.financing proxy"},
            {"item": "sub-hour open-expansion matched null",
             "reason": "no local M1/M5/M15/M30 frames to define the open bar"},
            {"item": "holding_period_matched_random",
             "reason": "ledgers use a fixed h12 hold (bars_held=12); equivalent to pair_matched here"},
        ]}, indent=2) + "\n", encoding="utf-8")

    print(mode_df.to_string(index=False))
    print("\nMATRIX SANITY:", matrix_payload["flags"],
          "best", matrix_payload["best_label"],
          "prob_best_le_null_max", matrix_payload["prob_best_le_null_max"])
    for name, f in fragility.items():
        print(f"\n{name}: full_h12={f['full_post_cost_h12']} "
              f"pair_sign_flips={f['pair_holdout']['sign_flips']} "
              f"year_sign_flips={f['time_block_holdout']['sign_flips']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

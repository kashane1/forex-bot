"""Apply the edge-discovery lab retrospectively to C025 and C026.

Artifact-first, DB-optional. Uses only committed compact C025/C026 artifacts.
Runs the diagnostics those artifacts support (matrix-sanity on the candidate
metrics table; cost-feasibility on the spread/ATR diagnostics) and records the
diagnostics that cannot run because C025/C026 never persisted a per-trade or
per-signal ledger (matched-null, forward-return, entry/exit decomposition) as
SKIPPED — never fabricated.

Does NOT change any C025/C026 verdict, approve anything, or open the test
lockbox. Writes compact artifacts under
``research/edge_discovery/retrospectives/``.

    python scripts/run_edge_discovery_c025_c026_retrospective.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.edge_discovery.cost_feasibility import cost_feasibility_table
from research.edge_discovery.multiple_comparison import matrix_sanity
from research.null_baselines import load_campaign_011_deduped_null_baseline

OUT_DIR = ROOT / "research" / "edge_discovery" / "retrospectives"

SAFETY_META = {
    "diagnostic_only": True,
    "strategy_evidence": False,
    "not_approved": True,
    "approves_strategy": False,
    "test_lockbox_opened": False,
    "changes_campaign_verdict": False,
    "NOT_edge_claim": True,
}

CAMPAIGNS = {
    "C025": {
        "dir": ROOT / "research" / "campaign_025" / "train_matrix",
        "metrics": "train_matrix_metrics.csv",
        "pair_metrics": "train_matrix_pair_metrics.csv",
        "spread_atr": "train_matrix_spread_atr_diagnostics.json",
        "verdict": "REJECT_MATRIX_NO_TRAIN_CANDIDATE / TEST_LOCKBOX_CLOSED / NOT_APPROVED",
    },
    "C026": {
        "dir": ROOT / "research" / "campaign_026" / "timeframe_ladder",
        "metrics": "train_matrix_metrics.csv",
        "pair_metrics": "train_matrix_pair_metrics.csv",
        "spread_atr": "train_matrix_spread_atr_diagnostics.json",
        "verdict": "REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE / TEST_LOCKBOX_CLOSED / NOT_APPROVED",
    },
}

# Diagnostics that need a per-trade / per-signal ledger C025/C026 never emitted.
SKIPPED_DIAGNOSTICS = [
    {
        "diagnostic": "matched_null_benchmark",
        "module": "research.edge_discovery.matched_nulls",
        "required_inputs": ["per-trade or per-signal ledger (instrument, side, entry_time, bars_held)",
                            "per-pair candle frames"],
        "available_inputs": ["rolled-up candidate metrics CSV", "per-pair aggregate metrics CSV"],
        "ran": False,
        "skip_reason": "SKIPPED_TRADE_LEDGER_UNAVAILABLE",
        "future_fix": "future campaigns must emit a trade ledger (see FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md)",
    },
    {
        "diagnostic": "forward_return_information",
        "module": "research.edge_discovery.windows",
        "required_inputs": ["signal ledger (instrument, signal_time, side)", "per-pair candle frames"],
        "available_inputs": ["rolled-up candidate metrics CSV"],
        "ran": False,
        "skip_reason": "SKIPPED_SIGNAL_LEDGER_UNAVAILABLE",
        "future_fix": "future campaigns must emit a signal ledger + keep frames resolvable",
    },
    {
        "diagnostic": "entry_exit_decomposition",
        "module": "research.edge_discovery.studies.exit_asymmetry_*",
        "required_inputs": ["per-trade ledger with entries, exits, exit_reason, r_multiple"],
        "available_inputs": ["exit_reason summary counts only (no per-trade rows)"],
        "ran": False,
        "skip_reason": "SKIPPED_TRADE_LEDGER_UNAVAILABLE",
        "future_fix": "future campaigns must emit a per-trade ledger with exit_reason + r_multiple",
    },
    {
        "diagnostic": "filter_ablation",
        "module": "research.edge_discovery.filter_ablation",
        "required_inputs": ["per-signal staged funnel with boolean filter pass columns + value"],
        "available_inputs": ["aggregate gate-filter counts only (train_matrix_gate_filters.csv)"],
        "ran": False,
        "skip_reason": "SKIPPED_SIGNAL_LEDGER_UNAVAILABLE",
        "future_fix": "future campaigns must emit a per-signal funnel ledger (pass columns + value proxy)",
    },
]


def _matrix_sanity_for(name: str, cfg: dict, *, null_ref: float, null_std: float) -> dict:
    metrics_path = cfg["dir"] / cfg["metrics"]
    df = pd.read_csv(metrics_path)
    # Best candidate's per-pair expectancy (trade-weighted) for pair-holdout.
    best_group_values = None
    best_group_weights = None
    best_id = str(df.loc[df["expectancy_r"].idxmax(), "candidate_id"])
    pair_path = cfg["dir"] / cfg["pair_metrics"]
    if pair_path.is_file():
        pm = pd.read_csv(pair_path)
        pm = pm[pm["candidate_id"] == best_id]
        if not pm.empty:
            best_group_values = {str(r["pair"]): float(r["expectancy_r"]) for _, r in pm.iterrows()}
            best_group_weights = {str(r["pair"]): float(r["trade_count"]) for _, r in pm.iterrows()}
    res = matrix_sanity(
        df, metric_col="expectancy_r", label_col="candidate_id", higher_is_better=True,
        null_reference=null_ref, null_std=null_std,
        best_group_values=best_group_values, best_group_weights=best_group_weights,
        group_kind="pair", seed=20260528,
    )
    return {
        "input_csv": str(metrics_path.relative_to(ROOT)),
        "n_candidates": len(df),
        "best_candidate": best_id,
        "result": res.to_dict(),
    }


def _cost_feasibility_for(name: str, cfg: dict) -> dict:
    sa_path = cfg["dir"] / cfg["spread_atr"]
    with sa_path.open(encoding="utf-8") as fh:
        sa = json.load(fh)
    per_candidate = {k: float(v["avg_spread_atr_ratio"]) for k, v in sa.items()}
    # Timeframe-level summary (C026 spans M3/M15/M30; C025 is all M5).
    metrics = pd.read_csv(cfg["dir"] / cfg["metrics"])
    tf_col = "execution_timeframe" if "execution_timeframe" in metrics.columns else None
    tf_ratios: dict[str, float] = {}
    if tf_col is not None:
        merged = metrics[["candidate_id", tf_col]].copy()
        merged["ratio"] = merged["candidate_id"].map(per_candidate)
        tf_ratios = {str(tf): float(g["ratio"].median()) for tf, g in merged.groupby(tf_col)}
    else:
        tf_ratios = {"M5": float(pd.Series(per_candidate).median())}
    tf_table = cost_feasibility_table(tf_ratios, kind="timeframe")
    cand_table = cost_feasibility_table(per_candidate, kind="timeframe")
    n_hostile = int(cand_table["flags"].str.contains("COST_HOSTILE").sum())
    return {
        "input_json": str(sa_path.relative_to(ROOT)),
        "n_candidates": len(per_candidate),
        "n_cost_hostile_candidates": n_hostile,
        "timeframe_summary": tf_table.to_dict(orient="records"),
        "per_candidate": cand_table.to_dict(orient="records"),
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    null = load_campaign_011_deduped_null_baseline()
    null_ref = float(null["aggregate"]["aggregate_expectancy_r"])
    null_std = float(null["null_distribution"]["per_fold_expectancy_r_std"])
    stamp = datetime.now(UTC).isoformat()

    for name, cfg in CAMPAIGNS.items():
        ms = _matrix_sanity_for(name, cfg, null_ref=null_ref, null_std=null_std)
        ms_payload = {
            "_meta": {**SAFETY_META, "kind": "edge_discovery.retrospective.matrix_sanity",
                      "campaign": name, "campaign_verdict_unchanged": cfg["verdict"],
                      "c011_null_reference": null_ref, "c011_null_std": null_std,
                      "generated_at_utc": stamp},
            **ms,
        }
        (OUT_DIR / f"{name.lower()}_matrix_sanity.json").write_text(
            json.dumps(ms_payload, indent=2, default=str) + "\n", encoding="utf-8")

        cf = _cost_feasibility_for(name, cfg)
        cf_payload = {
            "_meta": {**SAFETY_META, "kind": "edge_discovery.retrospective.cost_feasibility",
                      "campaign": name, "campaign_verdict_unchanged": cfg["verdict"],
                      "generated_at_utc": stamp},
            **cf,
        }
        (OUT_DIR / f"{name.lower()}_cost_feasibility_retrospective.json").write_text(
            json.dumps(cf_payload, indent=2, default=str) + "\n", encoding="utf-8")
        print(f"{name}: matrix_sanity flags={ms['result']['flags']} | "
              f"cost hostile {cf['n_cost_hostile_candidates']}/{cf['n_candidates']}")

    gaps_payload = {
        "_meta": {**SAFETY_META, "kind": "edge_discovery.retrospective.compatibility_gaps",
                  "generated_at_utc": stamp,
                  "note": "C025/C026 persisted only rolled-up candidate metrics; "
                          "per-trade / per-signal ledgers were never committed."},
        "campaigns": list(CAMPAIGNS),
        "ran": ["matrix_sanity", "cost_feasibility"],
        "skipped": SKIPPED_DIAGNOSTICS,
    }
    (OUT_DIR / "retrospective_compatibility_gaps.json").write_text(
        json.dumps(gaps_payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote retrospective artifacts under {OUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Null-baseline bias audit (Phase 2 of the bias-of-fixtures sprint).

Sprint: ``research-bias-of-fixtures-audit-001``.

Audits CAMPAIGN_011 (the binding random-entry null baseline) against
the questions in
``docs/research/BIAS_OF_FIXTURES_AUDIT_001_PLAN.md`` §4 Q1:

  * fold coverage consistency
  * pair coverage consistency
  * trade-count distribution by pair and fold (any pair/fold ≫
    dominating?)
  * direction balance (long vs short)
  * session / hour-of-day distribution
  * exit-reason distribution
  * stop/time-exit shape vs the other CAMPAIGN_010-014 campaigns
    (within-range or outlier?)

The script is read-only: it consumes only the committed CAMPAIGN_011
trade ledgers and the four cross-reference campaigns' trade ledgers.
It does **not** rerun any backtest, does **not** approve any strategy,
does **not** change any campaign verdict, and does **not** propose
parameter changes.

Inputs (all committed):

  * ``backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/
     fold_NN_<PAIR>_trades.csv``  (the null itself)
  * ``backtests/CAMPAIGN_010_session_breakout/folds/...``
  * ``backtests/CAMPAIGN_012_regime_switcher_atr_percentile/folds/...``
  * ``backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/
     folds/...``
  * ``backtests/CAMPAIGN_014_calendar_event_window_anomaly/folds/...``
  * each campaign's ``walk_forward/results.json`` (provenance only)

Outputs:

  * ``research/edge_discovery/studies/outputs/real/bias_null_baseline.json``
  * ``research/edge_discovery/studies/outputs/real/bias_null_baseline.md``

Both carry the standard provenance block with ``data_kind = "real"``,
``exploratory_only = True``, and the
``verdict_word_ban_acknowledged = True`` / refusal block required by
the lab's reporting contract.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from research.edge_discovery.real_data import (
    SEVEN_MAJORS,
    StudyInput,
    StudyProvenance,
    assert_real_data_kind,
    load_campaign_trades,
    load_campaign_walk_forward_result,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs" / "real"

CAMPAIGNS: tuple[str, ...] = (
    "CAMPAIGN_010_session_breakout",
    "CAMPAIGN_011_random_entry_anchor",
    "CAMPAIGN_012_regime_switcher_atr_percentile",
    "CAMPAIGN_013_cross_pair_currency_strength_rotation",
    "CAMPAIGN_014_calendar_event_window_anomaly",
)
NULL_CAMPAIGN = "CAMPAIGN_011_random_entry_anchor"
N_FOLDS_EXPECTED = 8
N_PAIRS_EXPECTED = 7

# Bias-threshold defaults. These are descriptive labels, NOT pass/fail
# gates. The output annotates each finding with one of:
#   * "within_expected_range"
#   * "minor_deviation"
#   * "material_deviation"
# Phase 5 decides which deviations (if any) prompt a rule update.
DIRECTION_BALANCE_MINOR_THRESHOLD = 0.05  # 50 / 50 ± 5 pp
DIRECTION_BALANCE_MATERIAL_THRESHOLD = 0.15  # 50 / 50 ± 15 pp
DOMINANCE_MINOR_THRESHOLD = 0.20  # any pair / fold > 20 % of total
DOMINANCE_MATERIAL_THRESHOLD = 0.40  # any pair / fold > 40 % of total
HOUR_CLUSTERING_MINOR_THRESHOLD = 0.15  # any single UTC hour > 15 % of trades
HOUR_CLUSTERING_MATERIAL_THRESHOLD = 0.25


# ---------------------------------------------------------------------------
# Data assembly + provenance
# ---------------------------------------------------------------------------


def _load_all_trades() -> pd.DataFrame:
    """Concatenate trade ledgers across the five campaigns."""
    frames: list[pd.DataFrame] = []
    for name in CAMPAIGNS:
        df = load_campaign_trades(REPO_ROOT / "backtests" / name)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def _build_provenance() -> StudyProvenance:
    inputs: list[StudyInput] = []
    earliest: pd.Timestamp | None = None
    latest: pd.Timestamp | None = None
    for name in CAMPAIGNS:
        result = load_campaign_walk_forward_result(REPO_ROOT / "backtests" / name)
        inputs.append(
            StudyInput(
                kind="campaign_walk_forward_results",
                path=result.source_path,
                sha256=result.source_sha256,
                rows=len(result.fold_metrics),
                extra={"overall_verdict": result.overall_verdict},
            )
        )
        plan = result.plan
        if isinstance(plan, dict):
            for top_key in ("universe_start", "universe_end"):
                val = plan.get(top_key)
                if val:
                    ts = pd.Timestamp(val, tz="UTC")
                    if top_key == "universe_start":
                        earliest = ts if earliest is None or ts < earliest else earliest
                    else:
                        latest = ts if latest is None or ts > latest else latest
            for fold in plan.get("folds", []):
                if not isinstance(fold, dict):
                    continue
                for key in ("train_start", "validation_start", "test_start"):
                    val = fold.get(key)
                    if val:
                        ts = pd.Timestamp(val, tz="UTC")
                        earliest = ts if earliest is None or ts < earliest else earliest
                for key in ("train_end", "validation_end", "test_end"):
                    val = fold.get(key)
                    if val:
                        ts = pd.Timestamp(val, tz="UTC")
                        latest = ts if latest is None or ts > latest else latest
    coverage = {
        "start_utc": str(earliest) if earliest is not None else "",
        "end_utc": str(latest) if latest is not None else "",
    }
    prov = StudyProvenance(
        data_kind="real",
        inputs=inputs,
        date_coverage=coverage,
        pair_universe=list(SEVEN_MAJORS),
        limitations=[
            "This is an audit of the CAMPAIGN_011 null baseline as a",
            "fixture. It does not approve, reverse, or revive any",
            "strategy verdict. It does not perform a new backtest.",
            "It does not propose parameter changes (e.g. a different",
            "random-entry interval or different stop multiple).",
            "It does not need the gitignored H4 SQLite candle store.",
        ],
        exploratory_only=True,
    )
    assert_real_data_kind(prov)
    return prov


# ---------------------------------------------------------------------------
# Coverage checks
# ---------------------------------------------------------------------------


def _coverage_audit(df: pd.DataFrame, campaign: str) -> dict[str, object]:
    """Per-campaign coverage: which (fold × pair) cells have any trades."""
    sub = df[df["campaign_name"] == campaign]
    folds = sorted(sub["fold_index"].unique().tolist())
    pairs = sorted(sub["instrument"].unique().tolist())
    grid = sub.groupby(["fold_index", "instrument"]).size().unstack(fill_value=0)
    # Re-index to expected universe so missing slots show up as 0.
    grid = grid.reindex(
        index=range(N_FOLDS_EXPECTED),
        columns=list(SEVEN_MAJORS),
        fill_value=0,
    )
    empty_cells = [
        (int(f), p)
        for f in grid.index
        for p in grid.columns
        if int(grid.at[f, p]) == 0
    ]
    return {
        "campaign": campaign,
        "n_folds_with_trades": len(folds),
        "n_pairs_with_trades": len(pairs),
        "folds_present": [int(f) for f in folds],
        "pairs_present": pairs,
        "expected_grid_size": N_FOLDS_EXPECTED * N_PAIRS_EXPECTED,
        "n_empty_cells": len(empty_cells),
        "empty_cells": empty_cells,
    }


# ---------------------------------------------------------------------------
# Distribution checks
# ---------------------------------------------------------------------------


def _trade_count_dispersion(df: pd.DataFrame, campaign: str) -> dict[str, object]:
    sub = df[df["campaign_name"] == campaign]
    n = len(sub)
    if n == 0:
        return {"campaign": campaign, "n_trades": 0}
    # Per-pair shares
    by_pair = sub.groupby("instrument").size().to_dict()
    by_pair_share = {k: v / n for k, v in by_pair.items()}
    pair_max = max(by_pair_share.values())
    pair_max_name = max(by_pair_share, key=by_pair_share.get)
    # Per-fold shares
    by_fold = sub.groupby("fold_index").size().to_dict()
    by_fold_share = {int(k): v / n for k, v in by_fold.items()}
    fold_max = max(by_fold_share.values())
    fold_max_name = int(max(by_fold_share, key=by_fold_share.get))
    # Classification
    def _label(x: float, minor: float, material: float) -> str:
        if x >= material:
            return "material_deviation"
        if x >= minor:
            return "minor_deviation"
        return "within_expected_range"
    return {
        "campaign": campaign,
        "n_trades": int(n),
        "trades_by_pair": {k: int(v) for k, v in by_pair.items()},
        "trades_by_pair_share": by_pair_share,
        "trades_by_fold": {int(k): int(v) for k, v in by_fold.items()},
        "trades_by_fold_share": by_fold_share,
        "max_pair_share": float(pair_max),
        "max_pair": pair_max_name,
        "max_pair_class": _label(pair_max, DOMINANCE_MINOR_THRESHOLD, DOMINANCE_MATERIAL_THRESHOLD),
        "max_fold_share": float(fold_max),
        "max_fold": fold_max_name,
        "max_fold_class": _label(fold_max, DOMINANCE_MINOR_THRESHOLD, DOMINANCE_MATERIAL_THRESHOLD),
    }


def _direction_balance(df: pd.DataFrame, campaign: str) -> dict[str, object]:
    sub = df[df["campaign_name"] == campaign]
    n = len(sub)
    if n == 0:
        return {"campaign": campaign, "n_trades": 0}
    n_long = int((sub["side"] == "long").sum())
    n_short = int((sub["side"] == "short").sum())
    long_share = n_long / n
    short_share = n_short / n
    deviation = abs(long_share - 0.5)
    if deviation >= DIRECTION_BALANCE_MATERIAL_THRESHOLD:
        cls = "material_deviation"
    elif deviation >= DIRECTION_BALANCE_MINOR_THRESHOLD:
        cls = "minor_deviation"
    else:
        cls = "within_expected_range"
    return {
        "campaign": campaign,
        "n_trades": int(n),
        "n_long": n_long,
        "n_short": n_short,
        "long_share": float(long_share),
        "short_share": float(short_share),
        "deviation_from_balanced": float(deviation),
        "classification": cls,
    }


def _hour_clustering(df: pd.DataFrame, campaign: str) -> dict[str, object]:
    sub = df[df["campaign_name"] == campaign]
    n = len(sub)
    if n == 0:
        return {"campaign": campaign, "n_trades": 0}
    hours = sub["entry_time"].dt.hour
    by_hour = hours.value_counts().sort_index().to_dict()
    shares = {int(h): int(v) / n for h, v in by_hour.items()}
    max_share = max(shares.values())
    max_hour = int(max(shares, key=shares.get))
    if max_share >= HOUR_CLUSTERING_MATERIAL_THRESHOLD:
        cls = "material_deviation"
    elif max_share >= HOUR_CLUSTERING_MINOR_THRESHOLD:
        cls = "minor_deviation"
    else:
        cls = "within_expected_range"
    return {
        "campaign": campaign,
        "n_trades": int(n),
        "hour_counts_utc": {int(h): int(v) for h, v in by_hour.items()},
        "hour_shares_utc": shares,
        "max_hour_share": float(max_share),
        "max_hour_utc": max_hour,
        "classification": cls,
    }


def _exit_reason_distribution(df: pd.DataFrame, campaign: str) -> dict[str, object]:
    sub = df[df["campaign_name"] == campaign]
    n = len(sub)
    if n == 0:
        return {"campaign": campaign, "n_trades": 0}
    counts = sub["exit_reason"].value_counts().to_dict()
    return {
        "campaign": campaign,
        "n_trades": int(n),
        "by_exit_reason": {str(k): int(v) for k, v in counts.items()},
        "share_by_exit_reason": {str(k): float(v) / n for k, v in counts.items()},
    }


# ---------------------------------------------------------------------------
# Null-vs-other comparison (is the null a structural outlier?)
# ---------------------------------------------------------------------------


def _null_vs_others_shape(df: pd.DataFrame) -> dict[str, object]:
    """Compute per-campaign aggregate exit-shape metrics and tag where
    CAMPAIGN_011 lands relative to the four candidate campaigns.

    The intent is *not* to compare strategies — it's to tell whether
    the null's exit-shape sits *inside* the cross-campaign distribution
    (legitimate as a baseline) or *outside* it (would mean the null is
    a structural outlier that doesn't represent what candidates do
    against the same engine).
    """
    rows = []
    for name in CAMPAIGNS:
        sub = df[df["campaign_name"] == name]
        if sub.empty:
            continue
        stop = sub[sub["exit_reason"] == "stop"]["r_multiple"]
        time = sub[sub["exit_reason"] == "time"]["r_multiple"]
        rows.append(
            {
                "campaign": name,
                "n": len(sub),
                "stop_rate": float((sub["exit_reason"] == "stop").mean()),
                "time_rate": float((sub["exit_reason"] == "time").mean()),
                "mean_r_given_stop": float(stop.mean()) if not stop.empty else float("nan"),
                "mean_r_given_time": float(time.mean()) if not time.empty else float("nan"),
                "mean_r_overall": float(sub["r_multiple"].mean()),
            }
        )
    null_row = next((r for r in rows if r["campaign"] == NULL_CAMPAIGN), None)
    others = [r for r in rows if r["campaign"] != NULL_CAMPAIGN]
    if null_row is None or not others:
        return {"rows": rows, "null_outlier": False, "notes": "could not compute"}

    def _bounds(metric: str) -> tuple[float, float]:
        values = [r[metric] for r in others if not pd.isna(r[metric])]
        return min(values), max(values)

    summary = {"rows": rows, "null_compare": {}}
    for metric in (
        "stop_rate",
        "time_rate",
        "mean_r_given_stop",
        "mean_r_given_time",
        "mean_r_overall",
    ):
        lo, hi = _bounds(metric)
        null_val = null_row[metric]
        outside = bool(null_val < lo or null_val > hi)
        summary["null_compare"][metric] = {
            "null_value": float(null_val),
            "others_min": float(lo),
            "others_max": float(hi),
            "null_is_outside_others_range": outside,
        }
    summary["null_outlier"] = any(
        v["null_is_outside_others_range"] for v in summary["null_compare"].values()
    )
    return summary


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _build_markdown(payload: dict) -> str:
    lines: list[str] = []
    lines.append("# Bias-of-Fixtures Audit — Null Baseline (Phase 2)")
    lines.append("")
    lines.append(
        "> Exploratory lab output. Not a strategy verdict. Does not approve, "
        "reverse, or revive any strategy. Verdict-word ban acknowledged."
    )
    lines.append("")

    head = payload["headline"]
    lines.append("## Headline")
    lines.append("")
    lines.append(f"- n_campaigns: {head['n_campaigns']}")
    lines.append(f"- n_trades_total: {head['n_trades_total']}")
    lines.append(f"- null_campaign: `{head['null_campaign']}`")
    lines.append(f"- null_trade_count: {head['null_trade_count']}")
    lines.append(f"- null_coverage_complete: {head['null_coverage_complete']}")
    lines.append(f"- null_outlier_vs_others_any_metric: {head['null_outlier_vs_others_any_metric']}")
    lines.append("")

    lines.append("## Coverage")
    lines.append("")
    lines.append("| campaign | folds with trades | pairs with trades | empty (fold,pair) cells |")
    lines.append("|---|---:|---:|---:|")
    for row in payload["coverage"]:
        lines.append(
            f"| {row['campaign']} | {row['n_folds_with_trades']} | "
            f"{row['n_pairs_with_trades']} | {row['n_empty_cells']} |"
        )
    lines.append("")

    lines.append("## Trade-count dispersion (null highlighted)")
    lines.append("")
    lines.append("| campaign | n_trades | max_pair_share | max_pair | max_fold_share | max_fold | classification |")
    lines.append("|---|---:|---:|---|---:|---:|---|")
    for row in payload["dispersion"]:
        if row.get("n_trades", 0) == 0:
            continue
        cls = f"{row['max_pair_class']} / {row['max_fold_class']}"
        lines.append(
            f"| {row['campaign']} | {row['n_trades']} | "
            f"{row['max_pair_share']:.3f} | {row['max_pair']} | "
            f"{row['max_fold_share']:.3f} | {row['max_fold']} | {cls} |"
        )
    lines.append("")

    lines.append("## Direction balance")
    lines.append("")
    lines.append("| campaign | n | long_share | short_share | |Δ|–from-50/50 | classification |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for row in payload["direction_balance"]:
        if row.get("n_trades", 0) == 0:
            continue
        lines.append(
            f"| {row['campaign']} | {row['n_trades']} | "
            f"{row['long_share']:.3f} | {row['short_share']:.3f} | "
            f"{row['deviation_from_balanced']:.3f} | {row['classification']} |"
        )
    lines.append("")

    lines.append("## Session / hour-of-day clustering")
    lines.append("")
    lines.append("| campaign | n | max_hour_utc | max_hour_share | classification |")
    lines.append("|---|---:|---:|---:|---|")
    for row in payload["hour_clustering"]:
        if row.get("n_trades", 0) == 0:
            continue
        lines.append(
            f"| {row['campaign']} | {row['n_trades']} | "
            f"{row['max_hour_utc']} | {row['max_hour_share']:.3f} | "
            f"{row['classification']} |"
        )
    lines.append("")

    lines.append("## Exit-reason distribution")
    lines.append("")
    lines.append("| campaign | stop | time | eod | shares |")
    lines.append("|---|---:|---:|---:|---|")
    for row in payload["exit_reason"]:
        if row.get("n_trades", 0) == 0:
            continue
        counts = row["by_exit_reason"]
        shares = row["share_by_exit_reason"]
        sh = " / ".join(f"{k}: {shares.get(k, 0.0):.3f}" for k in ("stop", "time", "eod"))
        lines.append(
            f"| {row['campaign']} | {counts.get('stop', 0)} | "
            f"{counts.get('time', 0)} | {counts.get('eod', 0)} | {sh} |"
        )
    lines.append("")

    lines.append("## Null-vs-others exit-shape comparison")
    lines.append("")
    lines.append("Question: does the null sit *inside* the range that the four candidate")
    lines.append("campaigns span on each shape metric? If yes, the null is a structurally")
    lines.append("legitimate baseline. If no, the null is an outlier.")
    lines.append("")
    lines.append("| metric | null_value | others_min | others_max | null_outside_range |")
    lines.append("|---|---:|---:|---:|:---:|")
    for metric, v in payload["null_vs_others"]["null_compare"].items():
        lines.append(
            f"| {metric} | {v['null_value']:.4f} | {v['others_min']:.4f} | "
            f"{v['others_max']:.4f} | {'**YES**' if v['null_is_outside_others_range'] else 'no'} |"
        )
    lines.append("")

    lines.append("## Interpretation (Phase-2 only)")
    lines.append("")
    lines.append(payload["interpretation"])
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Provenance and refusals")
    lines.append("")
    prov = payload["provenance"]
    lines.append(f"- data_kind: `{prov['data_kind']}`")
    lines.append(f"- exploratory_only: `{prov['exploratory_only']}`")
    lines.append(f"- inputs: {len(prov['inputs'])} artifact(s)")
    lines.append(f"- verdict_word_ban_acknowledged: `{payload['verdict_word_ban_acknowledged']}`")
    refusals = payload["refusals"]
    lines.append("- refusals:")
    for k, v in refusals.items():
        lines.append(f"  - {k}: `{v}`")
    lines.append("")

    return "\n".join(lines)


def _interpretation(payload: dict) -> str:
    head = payload["headline"]
    if head["null_outlier_vs_others_any_metric"]:
        outside = [
            m for m, v in payload["null_vs_others"]["null_compare"].items()
            if v["null_is_outside_others_range"]
        ]
        return (
            "The null sits **outside** the cross-campaign range on at least one "
            "shape metric: " + ", ".join(f"`{m}`" for m in outside) + ". "
            "This does not automatically disqualify the null — by construction "
            "the random-entry baseline can legitimately have a different shape "
            "than rule-based candidates. The audit's purpose is to surface "
            "this, not to silently bury it. Phase 5 decides whether the "
            "deviation requires a documentation note or a rule update."
        )
    return (
        "The null sits inside the cross-campaign range on every shape metric "
        "audited here. That is consistent with CAMPAIGN_011 being a "
        "structurally legitimate random-entry baseline against the same exit "
        "engine the four candidate campaigns use."
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    trades = _load_all_trades()
    if trades.empty:
        raise RuntimeError("no trades loaded from any campaign — abort")

    provenance = _build_provenance()

    coverage_rows = [_coverage_audit(trades, c) for c in CAMPAIGNS]
    dispersion_rows = [_trade_count_dispersion(trades, c) for c in CAMPAIGNS]
    direction_rows = [_direction_balance(trades, c) for c in CAMPAIGNS]
    hour_rows = [_hour_clustering(trades, c) for c in CAMPAIGNS]
    exit_rows = [_exit_reason_distribution(trades, c) for c in CAMPAIGNS]
    nvo = _null_vs_others_shape(trades)

    null_cov = next(r for r in coverage_rows if r["campaign"] == NULL_CAMPAIGN)
    null_coverage_complete = bool(
        null_cov["n_folds_with_trades"] == N_FOLDS_EXPECTED
        and null_cov["n_pairs_with_trades"] == N_PAIRS_EXPECTED
        and null_cov["n_empty_cells"] == 0
    )
    null_n_trades = int(trades[trades["campaign_name"] == NULL_CAMPAIGN].shape[0])

    payload: dict[str, object] = {
        "study_id": "bias_null_baseline",
        "sprint": "research-bias-of-fixtures-audit-001",
        "phase": 2,
        "headline": {
            "n_campaigns": len(CAMPAIGNS),
            "n_trades_total": int(trades.shape[0]),
            "null_campaign": NULL_CAMPAIGN,
            "null_trade_count": null_n_trades,
            "null_coverage_complete": null_coverage_complete,
            "null_outlier_vs_others_any_metric": nvo["null_outlier"],
        },
        "coverage": coverage_rows,
        "dispersion": dispersion_rows,
        "direction_balance": direction_rows,
        "hour_clustering": hour_rows,
        "exit_reason": exit_rows,
        "null_vs_others": nvo,
        "provenance": provenance.to_dict(),
        "verdict_word_ban_acknowledged": True,
        "refusals": {
            "approves_strategy": False,
            "changes_campaign_verdict": False,
            "proposes_parameter_tune": False,
            "writes_to_approved_strategies_yaml": False,
        },
    }
    payload["interpretation"] = _interpretation(payload)

    (OUTPUTS / "bias_null_baseline.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    (OUTPUTS / "bias_null_baseline.md").write_text(_build_markdown(payload), encoding="utf-8")


if __name__ == "__main__":
    run()

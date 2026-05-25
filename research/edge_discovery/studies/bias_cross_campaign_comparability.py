"""Cross-campaign comparability audit (Phase 3).

Sprint: ``research-bias-of-fixtures-audit-001``.

Checks whether CAMPAIGN_010 - CAMPAIGN_014 are comparable enough for
the lab's cross-campaign screens. The four axes that turned out
identical in Phase 1 (8-fold layout, 7-pair universe, H4 + FillModel
+ signal_bar_close, trade-CSV schema) are re-asserted here as
invariants, and the one axis that turned out NOT identical
(trade-window populations across train / validation / test) is
quantified and its effect on the exit-asymmetry headline numbers is
measured.

Read-only. No backtest. No strategy approval. No campaign verdict
change. No parameter tune.

Inputs (all committed):
  * ``backtests/CAMPAIGN_0{10,11,12,13,14}_*/walk_forward/plan.json``
  * ``backtests/CAMPAIGN_0{10,11,12,13,14}_*/walk_forward/results.json``
  * ``backtests/CAMPAIGN_0{10,11,12,13,14}_*/folds/fold_NN/
       fold_NN_<PAIR>_summary.json``
  * ``backtests/CAMPAIGN_0{10,11,12,13,14}_*/folds/fold_NN/
       fold_NN_<PAIR>_trades.csv``

Outputs:
  * ``research/edge_discovery/studies/outputs/real/
       bias_cross_campaign_comparability.json``
  * ``research/edge_discovery/studies/outputs/real/
       bias_cross_campaign_comparability.md``

Both carry the standard provenance + refusals block. Verdict-word
ban acknowledged.
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


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


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
            "This is an audit of cross-campaign artifact comparability.",
            "It does not re-execute any backtest, does not approve any",
            "strategy, does not change any campaign verdict, and does",
            "not propose parameter changes.",
            "The trade-window comparability finding (F0-2) is structural;",
            "fixing it would require re-running CAMPAIGN_012-014 with a",
            "test-window-only trade ledger, which is out of scope for",
            "this audit.",
        ],
        exploratory_only=True,
    )
    assert_real_data_kind(prov)
    return prov


# ---------------------------------------------------------------------------
# Invariant checks (re-assert what Phase 1 found)
# ---------------------------------------------------------------------------


def _fold_layout_invariant(campaigns: tuple[str, ...]) -> dict[str, object]:
    layouts: dict[str, list[tuple[int, str, str, str, str, str, str]]] = {}
    for name in campaigns:
        plan = json.loads(
            (REPO_ROOT / "backtests" / name / "walk_forward" / "plan.json").read_text()
        )
        layouts[name] = [
            (
                int(f["fold_index"]),
                str(f["train_start"]),
                str(f["train_end"]),
                str(f["validation_start"]),
                str(f["validation_end"]),
                str(f["test_start"]),
                str(f["test_end"]),
            )
            for f in plan.get("folds", [])
        ]
    base = layouts[campaigns[0]]
    all_same = all(layouts[c] == base for c in campaigns)
    return {
        "all_campaigns_share_fold_layout": all_same,
        "n_folds": len(base),
        "fold_layout_reference_campaign": campaigns[0],
        "fold_layout_reference": [
            {
                "fold_index": f[0],
                "train_start": f[1],
                "train_end": f[2],
                "validation_start": f[3],
                "validation_end": f[4],
                "test_start": f[5],
                "test_end": f[6],
            }
            for f in base
        ],
        "deviating_campaigns": [c for c in campaigns if layouts[c] != base],
    }


def _pair_universe_invariant(campaigns: tuple[str, ...]) -> dict[str, object]:
    universes: dict[str, list[str]] = {}
    for name in campaigns:
        folds_dir = REPO_ROOT / "backtests" / name / "folds"
        pairs: set[str] = set()
        for p in folds_dir.glob("fold_*/fold_*_*_summary.json"):
            stem = p.stem  # fold_NN_PAIR_summary
            parts = stem.split("_")
            # fold_NN_<PAIR_PARTS>_summary; pair joined by _
            pair = "_".join(parts[2:-1])
            pairs.add(pair)
        universes[name] = sorted(pairs)
    base = universes[campaigns[0]]
    return {
        "all_campaigns_share_pair_universe": all(universes[c] == base for c in campaigns),
        "pair_universe_reference_campaign": campaigns[0],
        "pair_universe_reference": base,
        "deviating_campaigns": {
            c: list(set(universes[c]).symmetric_difference(base))
            for c in campaigns
            if universes[c] != base
        },
    }


def _cost_assumption_invariant(campaigns: tuple[str, ...]) -> dict[str, object]:
    """Sample fold-00 EUR_USD summary for fill_model / fill_timing /
    granularity. The exit-asymmetry sprint already pinned these
    identical across all 5 campaigns; we re-assert that here."""
    by_campaign: dict[str, dict[str, str]] = {}
    for name in campaigns:
        p = REPO_ROOT / "backtests" / name / "folds" / "fold_00" / "fold_00_EUR_USD_summary.json"
        d = json.loads(p.read_text())
        by_campaign[name] = {
            "granularity": str(d.get("granularity")),
            "fill_model": str(d.get("fill_model")),
            "fill_timing": str(d.get("fill_timing")),
        }
    base = by_campaign[campaigns[0]]
    deviations = {c: by_campaign[c] for c in campaigns if by_campaign[c] != base}
    return {
        "all_share_cost_assumptions": not deviations,
        "reference_campaign": campaigns[0],
        "reference_values": base,
        "deviating_campaigns": deviations,
    }


def _schema_invariant(campaigns: tuple[str, ...]) -> dict[str, object]:
    """Iterate every trade-CSV across all folds and confirm a single
    column-set across the whole 280-CSV corpus."""
    seen: set[tuple[str, ...]] = set()
    by_campaign: dict[str, set[tuple[str, ...]]] = {c: set() for c in campaigns}
    for name in campaigns:
        for p in (REPO_ROOT / "backtests" / name / "folds").glob(
            "fold_*/fold_*_*_trades.csv"
        ):
            with open(p, encoding="utf-8") as f:
                header = tuple(next(iter(f)).strip().split(","))
                seen.add(header)
                by_campaign[name].add(header)
    return {
        "single_column_set_across_all_campaigns": len(seen) == 1,
        "column_count": len(next(iter(seen))) if seen else 0,
        "columns": list(next(iter(seen))) if seen else [],
        "per_campaign_distinct_headers": {
            k: len(v) for k, v in by_campaign.items()
        },
    }


def _exit_reason_vocab_invariant(campaigns: tuple[str, ...]) -> dict[str, object]:
    by_campaign: dict[str, list[str]] = {}
    for name in campaigns:
        all_reasons: set[str] = set()
        for p in (REPO_ROOT / "backtests" / name / "folds").glob(
            "fold_*/fold_*_*_trades.csv"
        ):
            df = pd.read_csv(p, usecols=["exit_reason"])
            all_reasons.update(df["exit_reason"].dropna().astype(str).unique().tolist())
        by_campaign[name] = sorted(all_reasons)
    base = by_campaign[campaigns[0]]
    return {
        "all_share_exit_vocab": all(by_campaign[c] == base for c in campaigns),
        "reference_vocab": base,
        "per_campaign_vocab": by_campaign,
    }


# ---------------------------------------------------------------------------
# Trade-window population audit
# ---------------------------------------------------------------------------


def _trade_window_populations(trades: pd.DataFrame) -> dict[str, object]:
    rows = []
    for name in CAMPAIGNS:
        plan = json.loads(
            (REPO_ROOT / "backtests" / name / "walk_forward" / "plan.json").read_text()
        )
        sub = trades[trades["campaign_name"] == name]
        in_test = 0
        in_validation_only = 0
        in_train_only = 0
        n_total = 0
        for fold in plan.get("folds", []):
            fi = int(fold["fold_index"])
            trs = pd.Timestamp(fold["train_start"]).tz_localize("UTC")
            tre = pd.Timestamp(fold["train_end"]).tz_localize("UTC") + pd.Timedelta(days=1)
            vs = pd.Timestamp(fold["validation_start"]).tz_localize("UTC")
            ve = pd.Timestamp(fold["validation_end"]).tz_localize("UTC") + pd.Timedelta(days=1)
            ts = pd.Timestamp(fold["test_start"]).tz_localize("UTC")
            te = pd.Timestamp(fold["test_end"]).tz_localize("UTC") + pd.Timedelta(days=1)
            fold_trades = sub[sub["fold_index"] == fi]
            n_total += len(fold_trades)
            in_test += int(((fold_trades["entry_time"] >= ts) & (fold_trades["entry_time"] < te)).sum())
            in_validation_only += int(((fold_trades["entry_time"] >= vs) & (fold_trades["entry_time"] < ve)).sum())
            in_train_only += int(((fold_trades["entry_time"] >= trs) & (fold_trades["entry_time"] < tre)).sum())
        share_test = in_test / n_total if n_total else float("nan")
        share_val = in_validation_only / n_total if n_total else float("nan")
        share_train = in_train_only / n_total if n_total else float("nan")
        rows.append(
            {
                "campaign": name,
                "n_total_trades": int(n_total),
                "n_in_test_window": int(in_test),
                "n_in_validation_window": int(in_validation_only),
                "n_in_train_window": int(in_train_only),
                "share_in_test_window": float(share_test),
                "share_in_validation_window": float(share_val),
                "share_in_train_window": float(share_train),
                "test_only_coverage": "complete" if share_test >= 0.99 else "partial",
            }
        )
    return {"per_campaign": rows}


# ---------------------------------------------------------------------------
# Headline-survival check: re-run exit-asymmetry summary on test-only trades
# ---------------------------------------------------------------------------


def _test_only_mask(trades: pd.DataFrame) -> pd.Series:
    """Boolean mask: which trades have entry_time inside the
    matched fold's test window."""
    mask = pd.Series(False, index=trades.index)
    for name in CAMPAIGNS:
        plan = json.loads(
            (REPO_ROOT / "backtests" / name / "walk_forward" / "plan.json").read_text()
        )
        sub_idx = trades.index[trades["campaign_name"] == name]
        for fold in plan.get("folds", []):
            fi = int(fold["fold_index"])
            ts = pd.Timestamp(fold["test_start"]).tz_localize("UTC")
            te = pd.Timestamp(fold["test_end"]).tz_localize("UTC") + pd.Timedelta(days=1)
            in_fold = trades.loc[sub_idx, "fold_index"] == fi
            in_test = (trades.loc[sub_idx, "entry_time"] >= ts) & (
                trades.loc[sub_idx, "entry_time"] < te
            )
            mask.loc[sub_idx[in_fold & in_test]] = True
    return mask


def _campaign_exit_shape(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for name in CAMPAIGNS:
        sub = df[df["campaign_name"] == name]
        if sub.empty:
            out[name] = {}
            continue
        stop = sub.loc[sub["exit_reason"] == "stop", "r_multiple"]
        time = sub.loc[sub["exit_reason"] == "time", "r_multiple"]
        out[name] = {
            "n": len(sub),
            "mean_r_overall": float(sub["r_multiple"].mean()),
            "stop_rate": float((sub["exit_reason"] == "stop").mean()),
            "time_rate": float((sub["exit_reason"] == "time").mean()),
            "mean_r_given_stop": float(stop.mean()) if not stop.empty else float("nan"),
            "mean_r_given_time": float(time.mean()) if not time.empty else float("nan"),
        }
    return out


def _headline_survival(trades: pd.DataFrame) -> dict[str, object]:
    """Compare the exit-asymmetry headline on full ledger vs test-only."""
    full = _campaign_exit_shape(trades)
    mask = _test_only_mask(trades)
    test_only = _campaign_exit_shape(trades[mask])
    rows = []
    for name in CAMPAIGNS:
        f = full[name]
        t = test_only[name]
        if not f or not t:
            continue
        d_mean_time = t.get("mean_r_given_time", float("nan")) - f.get("mean_r_given_time", float("nan"))
        d_mean_overall = t.get("mean_r_overall", float("nan")) - f.get("mean_r_overall", float("nan"))
        rows.append(
            {
                "campaign": name,
                "n_full": f["n"],
                "n_test_only": t["n"],
                "mean_r_given_time_full": f.get("mean_r_given_time"),
                "mean_r_given_time_test_only": t.get("mean_r_given_time"),
                "delta_mean_r_given_time": float(d_mean_time),
                "mean_r_overall_full": f.get("mean_r_overall"),
                "mean_r_overall_test_only": t.get("mean_r_overall"),
                "delta_mean_r_overall": float(d_mean_overall),
            }
        )
    # Did every campaign still have positive mean_r_given_time test-only?
    all_positive_time = all(
        (r["mean_r_given_time_test_only"] or 0) > 0
        for r in rows
        if r.get("mean_r_given_time_test_only") is not None and not pd.isna(r["mean_r_given_time_test_only"])
    )
    # Did every campaign still lose overall?
    all_negative_overall = all(
        (r["mean_r_overall_test_only"] or 0) <= 0
        for r in rows
        if r.get("mean_r_overall_test_only") is not None and not pd.isna(r["mean_r_overall_test_only"])
    )
    # Did the null still produce the highest mean_r_given_time among the 5?
    by_name = {r["campaign"]: r for r in rows}
    null_time = by_name.get(NULL_CAMPAIGN, {}).get("mean_r_given_time_test_only")
    null_still_highest = (
        all(
            (by_name[c].get("mean_r_given_time_test_only", -1e9) <= null_time + 1e-9)
            for c in CAMPAIGNS
        )
        if null_time is not None
        else False
    )
    return {
        "per_campaign": rows,
        "all_campaigns_positive_mean_r_given_time_test_only": bool(all_positive_time),
        "all_campaigns_negative_mean_r_overall_test_only": bool(all_negative_overall),
        "null_still_highest_mean_r_given_time_test_only": bool(null_still_highest),
        "exit_asymmetry_headline_survives_test_only_restriction": bool(
            all_positive_time and all_negative_overall
        ),
    }


# ---------------------------------------------------------------------------
# Per-campaign coverage anomalies (empty fold-pair cells)
# ---------------------------------------------------------------------------


def _coverage_anomalies(trades: pd.DataFrame) -> dict[str, object]:
    rows = []
    for name in CAMPAIGNS:
        sub = trades[trades["campaign_name"] == name]
        grid = sub.groupby(["fold_index", "instrument"]).size().unstack(fill_value=0)
        grid = grid.reindex(index=range(8), columns=list(SEVEN_MAJORS), fill_value=0)
        empty = [(int(f), p) for f in grid.index for p in grid.columns if int(grid.at[f, p]) == 0]
        rows.append(
            {
                "campaign": name,
                "n_empty_fold_pair_cells_out_of_56": len(empty),
                "empty_cells": empty,
            }
        )
    return {"per_campaign": rows}


# ---------------------------------------------------------------------------
# Classification: which differences are harmless / weakens / etc.
# ---------------------------------------------------------------------------


def _classify_differences(payload: dict) -> list[dict[str, str]]:
    """Map each observed difference to one of the five rubric labels
    from the plan §4 Q2:
      - harmless
      - needs_documentation
      - weakens_comparison
      - invalidates_comparison
      - requires_repair_sprint
    """
    findings: list[dict[str, str]] = []

    # Fold layout
    flo = payload["invariants"]["fold_layout"]
    if flo["all_campaigns_share_fold_layout"]:
        findings.append(
            {
                "axis": "fold_layout",
                "observed": "identical 8-fold layout across all 5 campaigns",
                "classification": "harmless",
                "rationale": "no comparability cost; comparison preserved",
            }
        )
    else:
        findings.append(
            {
                "axis": "fold_layout",
                "observed": f"deviating campaigns: {flo['deviating_campaigns']}",
                "classification": "invalidates_comparison",
                "rationale": "different fold windows make per-fold metrics non-comparable",
            }
        )

    # Pair universe
    puo = payload["invariants"]["pair_universe"]
    if puo["all_campaigns_share_pair_universe"]:
        findings.append(
            {
                "axis": "pair_universe",
                "observed": "identical 7-major universe across all 5 campaigns",
                "classification": "harmless",
                "rationale": "no comparability cost",
            }
        )
    else:
        findings.append(
            {
                "axis": "pair_universe",
                "observed": str(puo["deviating_campaigns"]),
                "classification": "weakens_comparison",
                "rationale": "different per-pair contributions to aggregates",
            }
        )

    # Cost assumptions
    co = payload["invariants"]["cost_assumptions"]
    if co["all_share_cost_assumptions"]:
        findings.append(
            {
                "axis": "fill_model_fill_timing_granularity",
                "observed": "identical across all 5 campaigns",
                "classification": "harmless",
                "rationale": "engine-level assumptions match; no comparability cost",
            }
        )
    else:
        findings.append(
            {
                "axis": "fill_model_fill_timing_granularity",
                "observed": str(co["deviating_campaigns"]),
                "classification": "weakens_comparison",
                "rationale": "different slippage / timing distorts cost-shape comparisons",
            }
        )

    # Schema
    so = payload["invariants"]["schema"]
    if so["single_column_set_across_all_campaigns"]:
        findings.append(
            {
                "axis": "trade_csv_schema",
                "observed": f"single {so['column_count']}-column schema across all 280 trade CSVs",
                "classification": "harmless",
                "rationale": "no comparability cost",
            }
        )
    else:
        findings.append(
            {
                "axis": "trade_csv_schema",
                "observed": f"per-campaign distinct headers: {so['per_campaign_distinct_headers']}",
                "classification": "weakens_comparison",
                "rationale": "schema drift requires loader-side coercion",
            }
        )

    # Exit-reason vocab
    eo = payload["invariants"]["exit_reason_vocab"]
    if eo["all_share_exit_vocab"]:
        findings.append(
            {
                "axis": "exit_reason_vocabulary",
                "observed": f"vocabulary {eo['reference_vocab']} identical across 5",
                "classification": "harmless",
                "rationale": "no comparability cost",
            }
        )
    else:
        findings.append(
            {
                "axis": "exit_reason_vocabulary",
                "observed": str(eo["per_campaign_vocab"]),
                "classification": "weakens_comparison",
                "rationale": "different exit-reason classes break conditional-mean comparison",
            }
        )

    # Trade window populations -- the headline finding
    tw = payload["trade_window_populations"]["per_campaign"]
    test_only_campaigns = [r["campaign"] for r in tw if r["test_only_coverage"] == "complete"]
    partial = [r for r in tw if r["test_only_coverage"] == "partial"]
    if not partial:
        findings.append(
            {
                "axis": "trade_window_population",
                "observed": "every campaign trades only on its test window",
                "classification": "harmless",
                "rationale": "fully comparable OOS windows",
            }
        )
    else:
        # The survival check tells us whether the bias actually flipped any headline
        survival = payload["headline_survival"]
        if survival["exit_asymmetry_headline_survives_test_only_restriction"]:
            cls = "needs_documentation"
            rationale = (
                "trade-window asymmetry exists but the cross-campaign exit-"
                "asymmetry headline survives the test-only restriction; the "
                "screens themselves remain correct because they are cell-level "
                "(per fold per pair) and the test-only restriction tightens "
                "rather than loosens them"
            )
        else:
            cls = "weakens_comparison"
            rationale = (
                "trade-window asymmetry materially changes the headline numbers; "
                "any cross-campaign comparison that did not restrict to test-only "
                "is suspect"
            )
        partial_names = [r["campaign"] for r in partial]
        findings.append(
            {
                "axis": "trade_window_population",
                "observed": (
                    f"test-only complete: {test_only_campaigns}; "
                    f"partial (mixed train/validation/test): {partial_names}"
                ),
                "classification": cls,
                "rationale": rationale,
            }
        )

    # Per-campaign coverage anomalies (empty fold-pair cells)
    anomalies = payload["coverage_anomalies"]["per_campaign"]
    empty_total = {a["campaign"]: a["n_empty_fold_pair_cells_out_of_56"] for a in anomalies}
    if all(v == 0 for v in empty_total.values()):
        findings.append(
            {
                "axis": "coverage_anomalies",
                "observed": "every campaign has trades in every (fold, pair) cell",
                "classification": "harmless",
                "rationale": "no coverage gap to worry about",
            }
        )
    else:
        nonzero = {k: v for k, v in empty_total.items() if v > 0}
        cls = "needs_documentation"
        if any(v > 14 for v in nonzero.values()):  # > 25% empty
            cls = "weakens_comparison"
        findings.append(
            {
                "axis": "coverage_anomalies",
                "observed": f"empty cells: {nonzero}",
                "classification": cls,
                "rationale": (
                    "empty cells are a strategy property (no signal), not a "
                    "fixture defect, but they reduce per-pair sample size in "
                    "cross-campaign aggregates and should be documented"
                ),
            }
        )

    return findings


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _build_markdown(payload: dict) -> str:
    lines: list[str] = []
    lines.append("# Bias-of-Fixtures Audit — Cross-Campaign Comparability (Phase 3)")
    lines.append("")
    lines.append(
        "> Exploratory lab output. Not a strategy verdict. Does not approve, "
        "reverse, or revive any strategy. Verdict-word ban acknowledged."
    )
    lines.append("")

    head = payload["headline"]
    lines.append("## Headline")
    lines.append("")
    for k in (
        "n_campaigns",
        "n_invariant_axes_pass",
        "n_invariant_axes_total",
        "trade_window_asymmetry_present",
        "exit_asymmetry_headline_survives_test_only_restriction",
        "max_classification_severity",
    ):
        lines.append(f"- {k}: {head[k]}")
    lines.append("")

    lines.append("## Invariant axes (Phase-1 facts re-asserted as code)")
    lines.append("")
    inv = payload["invariants"]
    lines.append(f"- **fold_layout**: all campaigns share layout = `{inv['fold_layout']['all_campaigns_share_fold_layout']}`")
    lines.append(f"- **pair_universe**: all campaigns share universe = `{inv['pair_universe']['all_campaigns_share_pair_universe']}`")
    lines.append(f"- **cost_assumptions**: all share fill_model + fill_timing + granularity = `{inv['cost_assumptions']['all_share_cost_assumptions']}`")
    lines.append(f"- **trade_csv_schema**: single column-set across all 280 CSVs = `{inv['schema']['single_column_set_across_all_campaigns']}`  (count = {inv['schema']['column_count']})")
    lines.append(f"- **exit_reason_vocab**: all share vocabulary = `{inv['exit_reason_vocab']['all_share_exit_vocab']}`  (`{inv['exit_reason_vocab']['reference_vocab']}`)")
    lines.append("")

    lines.append("## Trade-window populations (the F0-2 finding, quantified)")
    lines.append("")
    lines.append("| campaign | n_total | in test | in validation | in train | share test | coverage |")
    lines.append("|---|---:|---:|---:|---:|---:|---|")
    for r in payload["trade_window_populations"]["per_campaign"]:
        lines.append(
            f"| {r['campaign']} | {r['n_total_trades']} | {r['n_in_test_window']} | "
            f"{r['n_in_validation_window']} | {r['n_in_train_window']} | "
            f"{r['share_in_test_window']:.3f} | {r['test_only_coverage']} |"
        )
    lines.append("")

    lines.append("## Headline-number survival under test-only restriction")
    lines.append("")
    lines.append("| campaign | n_full | n_test_only | mean_R given_time (full) | mean_R given_time (test-only) | Δ | mean_R_overall (full) | mean_R_overall (test-only) | Δ |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in payload["headline_survival"]["per_campaign"]:
        lines.append(
            f"| {r['campaign']} | {r['n_full']} | {r['n_test_only']} | "
            f"{r.get('mean_r_given_time_full', float('nan')):.4f} | "
            f"{r.get('mean_r_given_time_test_only', float('nan')):.4f} | "
            f"{r['delta_mean_r_given_time']:+.4f} | "
            f"{r.get('mean_r_overall_full', float('nan')):.4f} | "
            f"{r.get('mean_r_overall_test_only', float('nan')):.4f} | "
            f"{r['delta_mean_r_overall']:+.4f} |"
        )
    lines.append("")
    lines.append("**Survival summary:**")
    s = payload["headline_survival"]
    lines.append(f"- all_campaigns_positive_mean_r_given_time_test_only: {s['all_campaigns_positive_mean_r_given_time_test_only']}")
    lines.append(f"- all_campaigns_negative_mean_r_overall_test_only:    {s['all_campaigns_negative_mean_r_overall_test_only']}")
    lines.append(f"- null_still_highest_mean_r_given_time_test_only:     {s['null_still_highest_mean_r_given_time_test_only']}")
    lines.append(f"- exit_asymmetry_headline_survives_test_only:         {s['exit_asymmetry_headline_survives_test_only_restriction']}")
    lines.append("")

    lines.append("## Per-campaign coverage anomalies")
    lines.append("")
    lines.append("| campaign | empty (fold,pair) cells out of 56 |")
    lines.append("|---|---:|")
    for r in payload["coverage_anomalies"]["per_campaign"]:
        lines.append(f"| {r['campaign']} | {r['n_empty_fold_pair_cells_out_of_56']} |")
    lines.append("")

    lines.append("## Differences classification")
    lines.append("")
    lines.append("| axis | observed | classification | rationale |")
    lines.append("|---|---|---|---|")
    for f in payload["classification"]:
        lines.append(f"| {f['axis']} | {f['observed']} | **{f['classification']}** | {f['rationale']} |")
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _load_all_trades() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for name in CAMPAIGNS:
        df = load_campaign_trades(REPO_ROOT / "backtests" / name)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def run() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    trades = _load_all_trades()
    if trades.empty:
        raise RuntimeError("no trades loaded; abort")

    provenance = _build_provenance()
    invariants = {
        "fold_layout": _fold_layout_invariant(CAMPAIGNS),
        "pair_universe": _pair_universe_invariant(CAMPAIGNS),
        "cost_assumptions": _cost_assumption_invariant(CAMPAIGNS),
        "schema": _schema_invariant(CAMPAIGNS),
        "exit_reason_vocab": _exit_reason_vocab_invariant(CAMPAIGNS),
    }
    tw = _trade_window_populations(trades)
    survival = _headline_survival(trades)
    coverage = _coverage_anomalies(trades)

    payload: dict[str, object] = {
        "study_id": "bias_cross_campaign_comparability",
        "sprint": "research-bias-of-fixtures-audit-001",
        "phase": 3,
        "headline": {
            "n_campaigns": len(CAMPAIGNS),
            "n_invariant_axes_total": 5,
            "n_invariant_axes_pass": int(
                sum(
                    [
                        invariants["fold_layout"]["all_campaigns_share_fold_layout"],
                        invariants["pair_universe"]["all_campaigns_share_pair_universe"],
                        invariants["cost_assumptions"]["all_share_cost_assumptions"],
                        invariants["schema"]["single_column_set_across_all_campaigns"],
                        invariants["exit_reason_vocab"]["all_share_exit_vocab"],
                    ]
                )
            ),
            "trade_window_asymmetry_present": any(
                r["test_only_coverage"] == "partial"
                for r in tw["per_campaign"]
            ),
            "exit_asymmetry_headline_survives_test_only_restriction": survival[
                "exit_asymmetry_headline_survives_test_only_restriction"
            ],
            "max_classification_severity": "",
        },
        "invariants": invariants,
        "trade_window_populations": tw,
        "headline_survival": survival,
        "coverage_anomalies": coverage,
        "provenance": provenance.to_dict(),
        "verdict_word_ban_acknowledged": True,
        "refusals": {
            "approves_strategy": False,
            "changes_campaign_verdict": False,
            "proposes_parameter_tune": False,
            "writes_to_approved_strategies_yaml": False,
        },
    }
    payload["classification"] = _classify_differences(payload)
    # Compute max severity for the headline
    severity_rank = {
        "harmless": 0,
        "needs_documentation": 1,
        "weakens_comparison": 2,
        "invalidates_comparison": 3,
        "requires_repair_sprint": 4,
    }
    max_sev = max(
        severity_rank[f["classification"]]
        for f in payload["classification"]
    )
    payload["headline"]["max_classification_severity"] = next(
        k for k, v in severity_rank.items() if v == max_sev
    )

    (OUTPUTS / "bias_cross_campaign_comparability.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    (OUTPUTS / "bias_cross_campaign_comparability.md").write_text(
        _build_markdown(payload), encoding="utf-8"
    )


if __name__ == "__main__":
    run()

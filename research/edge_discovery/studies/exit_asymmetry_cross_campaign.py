"""Cross-campaign exit-asymmetry study (Phases 1 + 2).

Sprint: ``research-exit-asymmetry-cross-campaign-001``.

This script is the diagnostic, descriptive lab study that asks
whether the −1 R-stop / small-positive-time-exit payoff shape
that surfaced inside the EUR_USD / CAMPAIGN_012 falsification probe
is a recurring property of the lab's exit engine across every
committed CAMPAIGN_010 - CAMPAIGN_014 trade ledger.

It is **not** a strategy proposal. It does not approve any candidate
and it does not change any campaign verdict. CAMPAIGN_010 - 014 all
remain REJECT-anchored regardless of what this script's tables
contain.

Inputs (all committed, all local):

  * ``backtests/CAMPAIGN_010_session_breakout/folds/fold_NN/fold_NN_<PAIR>_trades.csv``
  * ``backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/fold_NN_<PAIR>_trades.csv``
  * ``backtests/CAMPAIGN_012_regime_switcher_atr_percentile/folds/fold_NN/fold_NN_<PAIR>_trades.csv``
  * ``backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/folds/fold_NN/fold_NN_<PAIR>_trades.csv``
  * ``backtests/CAMPAIGN_014_calendar_event_window_anomaly/folds/fold_NN/fold_NN_<PAIR>_trades.csv``
  * ``backtests/CAMPAIGN_010-014/walk_forward/results.json`` (provenance only)

Outputs:

  * ``research/edge_discovery/studies/outputs/real/exit_asymmetry_cross_campaign.json``
  * ``research/edge_discovery/studies/outputs/real/exit_asymmetry_cross_campaign.md``

The JSON output carries the structural-pattern check, the per-campaign
exit-shape summaries, the per-(campaign, instrument) exit-shape
summaries, the per-(campaign, fold) stop-rate dispersion, and the
list of (campaign, instrument) cells whose mean_R_given_time gap vs
CAMPAIGN_011 exceeds the +0.05 R material-gap floor — these are the
cells that Phase 3's robustness script will subsequently screen.

Exploratory lab output. Not strategy evidence. Verdict-word ban
acknowledged in JSON: ``verdict_word_ban_acknowledged = True``.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
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

# Lab thresholds carried in from the prior sprints.
MATERIAL_GAP_R = 0.05  # per-pair gap floor (hydrate sprint §A.2 / probe §A.1)
HARD_STOP_R_LE = -0.95  # what "stop crystallised at −1 R" means in this study
TIME_EXIT_SMALL_BAND_LO = -0.5
TIME_EXIT_SMALL_BAND_HI = +0.5


# ---------------------------------------------------------------------------
# Data assembly
# ---------------------------------------------------------------------------


def _load_all_trades() -> pd.DataFrame:
    """Concatenate trade ledgers across all 5 campaigns, preserving
    every original column and adding ``campaign_name`` / ``fold_index``."""
    frames: list[pd.DataFrame] = []
    for name in CAMPAIGNS:
        df = load_campaign_trades(REPO_ROOT / "backtests" / name)
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    return out


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
                extra={
                    "overall_verdict": result.overall_verdict,
                    "strategy_evidence": result.strategy_evidence,
                },
            )
        )
        # Pull fold time range from the plan if present. The committed
        # walk_forward JSONs use flat keys train_start / train_end /
        # validation_start / validation_end / test_start / test_end on
        # each fold dict, and universe_start / universe_end at the
        # top level of plan.
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
            folds = plan.get("folds", [])
            for fold in folds:
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
            "Trade ledgers are read-only; this study does not regenerate",
            "any backtest and cannot revise per-campaign verdicts.",
            "Mean_R_given_time being positive in CAMPAIGN_011 (random-entry",
            "null) confirms the shape is an exit-engine artifact, not a",
            "strategy edge; positive time-exit means under the null are",
            "by definition not exploitable signal.",
            "This study does not propose parameter changes (e.g. wider",
            "stops or longer time-budgets) — that would be strategy",
            "tuning and is out of scope for this sprint.",
        ],
        exploratory_only=True,
    )
    assert_real_data_kind(prov)
    return prov


# ---------------------------------------------------------------------------
# Aggregation primitives
# ---------------------------------------------------------------------------


def _exit_shape_row(group: pd.DataFrame) -> dict[str, float]:
    """Return the exit-shape summary for a group of trades.

    Includes per-exit-reason rates and conditional means."""
    n = len(group)
    n_stop = int((group["exit_reason"] == "stop").sum())
    n_time = int((group["exit_reason"] == "time").sum())
    n_eod = int((group["exit_reason"] == "eod").sum())
    n_other = n - n_stop - n_time - n_eod
    r = group["r_multiple"]
    stop_r = group.loc[group["exit_reason"] == "stop", "r_multiple"]
    time_r = group.loc[group["exit_reason"] == "time", "r_multiple"]
    eod_r = group.loc[group["exit_reason"] == "eod", "r_multiple"]
    # Hard stop / small-time-band fractions
    hard_stop_share = float((stop_r <= HARD_STOP_R_LE).mean()) if len(stop_r) > 0 else float("nan")
    small_time_share = (
        float(((time_r > TIME_EXIT_SMALL_BAND_LO) & (time_r < TIME_EXIT_SMALL_BAND_HI)).mean())
        if len(time_r) > 0
        else float("nan")
    )
    # Decomposition: who explains the gross losses / gross gains
    neg_r = r[r < 0]
    pos_r = r[r > 0]
    gross_loss_total = float(neg_r.sum()) if not neg_r.empty else 0.0
    gross_gain_total = float(pos_r.sum()) if not pos_r.empty else 0.0
    stop_neg_total = float(stop_r[stop_r < 0].sum()) if not stop_r.empty else 0.0
    time_pos_total = float(time_r[time_r > 0].sum()) if not time_r.empty else 0.0
    return {
        "n_total": int(n),
        "n_stop": n_stop,
        "n_time": n_time,
        "n_eod": n_eod,
        "n_other": int(n_other),
        "stop_rate": n_stop / n if n > 0 else float("nan"),
        "time_rate": n_time / n if n > 0 else float("nan"),
        "eod_rate": n_eod / n if n > 0 else float("nan"),
        "mean_r_overall": float(r.mean()) if n > 0 else float("nan"),
        "median_r_overall": float(r.median()) if n > 0 else float("nan"),
        "sum_r_overall": float(r.sum()) if n > 0 else 0.0,
        "mean_r_given_stop": float(stop_r.mean()) if not stop_r.empty else float("nan"),
        "median_r_given_stop": float(stop_r.median()) if not stop_r.empty else float("nan"),
        "mean_r_given_time": float(time_r.mean()) if not time_r.empty else float("nan"),
        "median_r_given_time": float(time_r.median()) if not time_r.empty else float("nan"),
        "mean_r_given_eod": float(eod_r.mean()) if not eod_r.empty else float("nan"),
        "median_r_given_eod": float(eod_r.median()) if not eod_r.empty else float("nan"),
        "pct_stops_at_or_below_hard_stop": hard_stop_share,
        "pct_time_exits_in_small_band": small_time_share,
        "share_gross_loss_from_stops": (
            stop_neg_total / gross_loss_total if gross_loss_total < 0 else float("nan")
        ),
        "share_gross_gain_from_time_exits": (
            time_pos_total / gross_gain_total if gross_gain_total > 0 else float("nan")
        ),
    }


def _group_apply_exit_shape(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """Apply ``_exit_shape_row`` to each group identified by ``by``."""
    rows: list[dict[str, object]] = []
    for keys, group in df.groupby(by, sort=True, observed=True):
        keys_tuple = keys if isinstance(keys, tuple) else (keys,)
        row: dict[str, object] = dict(zip(by, keys_tuple, strict=True))
        row.update(_exit_shape_row(group))
        rows.append(row)
    return pd.DataFrame(rows)


def _per_campaign_summary(df: pd.DataFrame) -> pd.DataFrame:
    return _group_apply_exit_shape(df, ["campaign_name"])


def _per_campaign_side_summary(df: pd.DataFrame) -> pd.DataFrame:
    return _group_apply_exit_shape(df, ["campaign_name", "side"])


def _per_campaign_pair_summary(df: pd.DataFrame) -> pd.DataFrame:
    return _group_apply_exit_shape(df, ["campaign_name", "instrument"])


def _per_campaign_fold_summary(df: pd.DataFrame) -> pd.DataFrame:
    return _group_apply_exit_shape(df, ["campaign_name", "fold_index"])


def _per_campaign_pair_fold_summary(df: pd.DataFrame) -> pd.DataFrame:
    return _group_apply_exit_shape(df, ["campaign_name", "instrument", "fold_index"])


# ---------------------------------------------------------------------------
# Structural-pattern check (Phase 0 §6)
# ---------------------------------------------------------------------------


def _check_structural_pattern(
    per_campaign: pd.DataFrame,
    per_campaign_pair_fold: pd.DataFrame,
) -> dict[str, object]:
    """Return the Phase 0 §6 structural-pattern check verdict.

    Four conditions:
      1. Universal hard stop: ≥ 90% of stop trades across all 5
         campaigns have r ≤ −0.95.
      2. Universal time-exit small-positive shape: ≥ 70% of time
         trades in the [−0.5, +0.5] band AND mean_r_given_time > 0
         in ≥ 4/5 campaigns including the null.
      3. Null shares the shape: mean_r_given_stop and stop_rate of
         CAMPAIGN_011 within ±0.05 of the median of the other 4.
      4. Fold-noise driver: per-(campaign, pair) std of stop_rate
         across folds ≥ 0.05 (median across all 35 = 5 × 7 cells).
    """
    rows_c = per_campaign.set_index("campaign_name")
    # Condition 1
    cond_1_pct = {
        c: float(rows_c.loc[c, "pct_stops_at_or_below_hard_stop"])
        for c in CAMPAIGNS
    }
    cond_1_pass = all(v >= 0.90 for v in cond_1_pct.values())

    # Condition 2
    small_band_pct = {
        c: float(rows_c.loc[c, "pct_time_exits_in_small_band"])
        for c in CAMPAIGNS
    }
    mean_time_pos = {
        c: float(rows_c.loc[c, "mean_r_given_time"]) > 0
        for c in CAMPAIGNS
    }
    # ≥ 4/5 campaigns including the null have positive mean_r_given_time
    cond_2_band_pass = all(v >= 0.70 for v in small_band_pct.values())
    cond_2_mean_pass = (
        sum(int(v) for v in mean_time_pos.values()) >= 4
        and mean_time_pos[NULL_CAMPAIGN]
    )
    cond_2_pass = cond_2_band_pass and cond_2_mean_pass

    # Condition 3 — null inside the cross-campaign cloud
    other_stop_rates = [
        float(rows_c.loc[c, "stop_rate"]) for c in CAMPAIGNS if c != NULL_CAMPAIGN
    ]
    other_mean_r_stop = [
        float(rows_c.loc[c, "mean_r_given_stop"]) for c in CAMPAIGNS if c != NULL_CAMPAIGN
    ]
    null_stop_rate = float(rows_c.loc[NULL_CAMPAIGN, "stop_rate"])
    null_mean_r_stop = float(rows_c.loc[NULL_CAMPAIGN, "mean_r_given_stop"])
    median_other_stop_rate = float(np.median(other_stop_rates))
    median_other_mean_r_stop = float(np.median(other_mean_r_stop))
    cond_3_stop_rate_pass = abs(null_stop_rate - median_other_stop_rate) <= 0.05
    cond_3_mean_r_pass = abs(null_mean_r_stop - median_other_mean_r_stop) <= 0.05
    cond_3_pass = cond_3_stop_rate_pass and cond_3_mean_r_pass

    # Condition 4 — fold-noise driver
    stop_rate_std = (
        per_campaign_pair_fold.groupby(["campaign_name", "instrument"], observed=True)[
            "stop_rate"
        ]
        .std(ddof=0)
        .reset_index()
    )
    stop_rate_std_median = float(stop_rate_std["stop_rate"].median())
    cond_4_pass = stop_rate_std_median >= 0.05

    all_pass = cond_1_pass and cond_2_pass and cond_3_pass and cond_4_pass

    return {
        "condition_1_universal_hard_stop": {
            "threshold_pct_stops_at_or_below_minus_0_95_R_per_campaign": 0.90,
            "per_campaign_pct": cond_1_pct,
            "pass": bool(cond_1_pass),
        },
        "condition_2_universal_small_positive_time_shape": {
            "threshold_pct_time_exits_in_band_per_campaign": 0.70,
            "per_campaign_pct_in_band": small_band_pct,
            "per_campaign_mean_r_given_time_positive": mean_time_pos,
            "pass": bool(cond_2_pass),
        },
        "condition_3_null_shares_shape": {
            "threshold_abs_diff": 0.05,
            "null_stop_rate": null_stop_rate,
            "median_other_stop_rate": median_other_stop_rate,
            "abs_diff_stop_rate": abs(null_stop_rate - median_other_stop_rate),
            "null_mean_r_given_stop": null_mean_r_stop,
            "median_other_mean_r_given_stop": median_other_mean_r_stop,
            "abs_diff_mean_r_given_stop": abs(null_mean_r_stop - median_other_mean_r_stop),
            "pass": bool(cond_3_pass),
        },
        "condition_4_fold_noise_driver": {
            "threshold_median_per_pair_stop_rate_std": 0.05,
            "observed_median_per_pair_stop_rate_std": stop_rate_std_median,
            "pass": bool(cond_4_pass),
        },
        "classification": (
            "STRUCTURAL_FAILURE_PATTERN_CONFIRMED" if all_pass
            else "STRUCTURAL_FAILURE_PATTERN_PARTIAL"
        ),
        "all_conditions_pass": bool(all_pass),
    }


# ---------------------------------------------------------------------------
# Above-floor cells worth screening in Phase 3
# ---------------------------------------------------------------------------


def _above_floor_cells_vs_null(
    per_campaign_pair: pd.DataFrame,
) -> list[dict[str, object]]:
    """Return the (campaign, instrument) cells whose mean_r_given_time
    or mean_r_overall exceeds CAMPAIGN_011's matched cell by ≥ +0.05 R.

    Phase 3 will run the LOO / t-stat / R-9 screens on each.
    """
    null = per_campaign_pair[
        per_campaign_pair["campaign_name"] == NULL_CAMPAIGN
    ].set_index("instrument")
    out: list[dict[str, object]] = []
    for _, row in per_campaign_pair.iterrows():
        if row["campaign_name"] == NULL_CAMPAIGN:
            continue
        pair = row["instrument"]
        if pair not in null.index:
            continue
        null_row = null.loc[pair]
        time_gap = float(row["mean_r_given_time"]) - float(null_row["mean_r_given_time"])
        overall_gap = float(row["mean_r_overall"]) - float(null_row["mean_r_overall"])
        if time_gap >= MATERIAL_GAP_R or overall_gap >= MATERIAL_GAP_R:
            out.append({
                "campaign_name": row["campaign_name"],
                "instrument": pair,
                "mean_r_overall_candidate": float(row["mean_r_overall"]),
                "mean_r_overall_null": float(null_row["mean_r_overall"]),
                "mean_r_overall_gap": overall_gap,
                "mean_r_given_time_candidate": float(row["mean_r_given_time"]),
                "mean_r_given_time_null": float(null_row["mean_r_given_time"]),
                "mean_r_given_time_gap": time_gap,
                "above_floor_on_overall": overall_gap >= MATERIAL_GAP_R,
                "above_floor_on_time_only": time_gap >= MATERIAL_GAP_R,
                "n_trades_candidate": int(row["n_total"]),
                "n_trades_null": int(null_row["n_total"]),
            })
    out.sort(key=lambda x: max(float(x["mean_r_given_time_gap"]),
                               float(x["mean_r_overall_gap"])),
             reverse=True)
    return out


# ---------------------------------------------------------------------------
# Output rendering
# ---------------------------------------------------------------------------


def _frame_to_records(df: pd.DataFrame) -> list[dict[str, object]]:
    """JSON-friendly record list with python-native types."""
    records: list[dict[str, object]] = []
    for _, row in df.iterrows():
        rec: dict[str, object] = {}
        for col, val in row.items():
            if isinstance(val, np.integer):
                rec[col] = int(val)
            elif isinstance(val, np.floating):
                rec[col] = float(val)
            else:
                rec[col] = val
        records.append(rec)
    return records


def _round_records(records: list[dict[str, object]], *, ndigits: int = 4) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for r in records:
        d: dict[str, object] = {}
        for k, v in r.items():
            if isinstance(v, float):
                d[k] = round(v, ndigits) if not np.isnan(v) else None
            else:
                d[k] = v
        out.append(d)
    return out


def _build_markdown(
    payload: dict[str, object],
) -> str:
    lines: list[str] = []
    lines.append("# Cross-Campaign Exit-Asymmetry — Phases 1 + 2 Output")
    lines.append("")
    lines.append("**Sprint:** `research-exit-asymmetry-cross-campaign-001`")
    lines.append("**Phase:** 1 + 2 (extraction + descriptive aggregation)")
    lines.append("**Date:** 2026-05-24")
    lines.append("")
    lines.append("> Exploratory lab output. **No strategy approved.** **No campaign**")
    lines.append("> **verdict changed.** Paper / demo / live remain blocked.")
    lines.append("> CAMPAIGN_010 - CAMPAIGN_014 remain REJECT-anchored.")
    lines.append("")
    lines.append("## Headline numbers")
    lines.append("")
    headline = payload["headline"]
    lines.append(f"- Trades loaded: **{headline['n_trades_total']:,}** across {headline['n_campaigns']} campaigns × {headline['n_pairs']} pairs × {headline['n_folds_per_campaign']} folds per campaign.")
    lines.append(f"- Observed `exit_reason` vocabulary: `{headline['exit_reason_vocabulary']}`.")
    lines.append("")
    lines.append("## Per-campaign exit shape")
    lines.append("")
    lines.append("| campaign | n_total | stop_rate | time_rate | mean_R_given_stop | mean_R_given_time | mean_R_overall | sum_R_overall | pct_stops≤−0.95 | pct_time∈[−0.5,+0.5] |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for rec in payload["per_campaign"]:
        lines.append(
            f"| {rec['campaign_name']} "
            f"| {rec['n_total']:,} "
            f"| {rec['stop_rate']:.3f} "
            f"| {rec['time_rate']:.3f} "
            f"| {rec['mean_r_given_stop']:.4f} "
            f"| {rec['mean_r_given_time']:.4f} "
            f"| {rec['mean_r_overall']:.4f} "
            f"| {rec['sum_r_overall']:.3f} "
            f"| {rec['pct_stops_at_or_below_hard_stop']:.3f} "
            f"| {rec['pct_time_exits_in_small_band']:.3f} |"
        )
    lines.append("")
    lines.append("## Structural-pattern check (Phase 0 §6)")
    lines.append("")
    sp = payload["structural_pattern_check"]
    lines.append(f"**Classification:** `{sp['classification']}`")
    lines.append("")
    lines.append(f"- Condition 1 (universal hard stop, ≥ 90% stops at or below −0.95 R): **{'PASS' if sp['condition_1_universal_hard_stop']['pass'] else 'NOT MET'}**")
    for c, v in sp["condition_1_universal_hard_stop"]["per_campaign_pct"].items():
        lines.append(f"  - {c}: {v:.3f}")
    lines.append(f"- Condition 2 (universal small-positive time shape): **{'PASS' if sp['condition_2_universal_small_positive_time_shape']['pass'] else 'NOT MET'}**")
    for c, v in sp["condition_2_universal_small_positive_time_shape"]["per_campaign_pct_in_band"].items():
        pos = sp["condition_2_universal_small_positive_time_shape"]["per_campaign_mean_r_given_time_positive"][c]
        lines.append(f"  - {c}: pct_in_band={v:.3f}, mean_r_given_time>0={pos}")
    lines.append(f"- Condition 3 (null shares the shape, |Δ| ≤ 0.05 vs median of others): **{'PASS' if sp['condition_3_null_shares_shape']['pass'] else 'NOT MET'}**")
    lines.append(f"  - null stop_rate {sp['condition_3_null_shares_shape']['null_stop_rate']:.4f} vs median {sp['condition_3_null_shares_shape']['median_other_stop_rate']:.4f} (|Δ|={sp['condition_3_null_shares_shape']['abs_diff_stop_rate']:.4f})")
    lines.append(f"  - null mean_R_given_stop {sp['condition_3_null_shares_shape']['null_mean_r_given_stop']:.4f} vs median {sp['condition_3_null_shares_shape']['median_other_mean_r_given_stop']:.4f} (|Δ|={sp['condition_3_null_shares_shape']['abs_diff_mean_r_given_stop']:.4f})")
    lines.append(f"- Condition 4 (fold-noise driver, median per-pair stop_rate σ ≥ 0.05): **{'PASS' if sp['condition_4_fold_noise_driver']['pass'] else 'NOT MET'}** (observed {sp['condition_4_fold_noise_driver']['observed_median_per_pair_stop_rate_std']:.4f})")
    lines.append("")
    lines.append("## Decomposition of gross losses and gross gains")
    lines.append("")
    lines.append("| campaign | share_gross_loss_from_stops | share_gross_gain_from_time_exits |")
    lines.append("|---|---:|---:|")
    for rec in payload["per_campaign"]:
        lines.append(
            f"| {rec['campaign_name']} | "
            f"{rec['share_gross_loss_from_stops']:.3f} | "
            f"{rec['share_gross_gain_from_time_exits']:.3f} |"
        )
    lines.append("")
    lines.append("## Per-(campaign, side) — does long vs short share the pattern?")
    lines.append("")
    lines.append("| campaign | side | n | stop_rate | mean_R_given_stop | mean_R_given_time | mean_R_overall |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for rec in payload["per_campaign_side"]:
        lines.append(
            f"| {rec['campaign_name']} | {rec['side']} | {rec['n_total']:,} "
            f"| {rec['stop_rate']:.3f} | {rec['mean_r_given_stop']:.4f} "
            f"| {rec['mean_r_given_time']:.4f} | {rec['mean_r_overall']:.4f} |"
        )
    lines.append("")
    lines.append("## Above-floor cells worth Phase 3 screening")
    lines.append("")
    cells = payload["above_floor_cells_vs_null"]
    if cells:
        lines.append("Cells whose `mean_R_given_time` or `mean_R_overall` clears the +0.05 R floor against CAMPAIGN_011's matched cell. **Listed for Phase 3 robustness screens only — none of these is approved.**")
        lines.append("")
        lines.append("| campaign | instrument | n_cand | n_null | gap mean_R_overall | gap mean_R_given_time |")
        lines.append("|---|---|---:|---:|---:|---:|")
        for cell in cells:
            lines.append(
                f"| {cell['campaign_name']} | {cell['instrument']} "
                f"| {cell['n_trades_candidate']:,} | {cell['n_trades_null']:,} "
                f"| {cell['mean_r_overall_gap']:+.4f} | {cell['mean_r_given_time_gap']:+.4f} |"
            )
    else:
        lines.append("None. No (campaign, instrument) cell clears the +0.05 R floor on either mean_R_overall or mean_R_given_time vs CAMPAIGN_011.")
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    prov = payload["provenance"]
    lines.append(f"- data_kind: `{prov['data_kind']}`")
    lines.append(f"- pair_universe: `{prov['pair_universe']}`")
    lines.append(f"- date_coverage: {prov['date_coverage']['start_utc']} → {prov['date_coverage']['end_utc']}")
    lines.append(f"- inputs ({len(prov['inputs'])}):")
    for inp in prov["inputs"]:
        lines.append(f"  - {inp['kind']} · {inp['path']} · sha256 `{inp['sha256'][:12]}...`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("This output **does not approve** any strategy and **does not change**")
    lines.append("any campaign verdict. The classification fields above describe the")
    lines.append("lab's structural-pattern check; they do not promote any candidate.")
    return "\n".join(lines) + "\n"


def main() -> dict[str, object]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    prov = _build_provenance()
    trades = _load_all_trades()
    per_campaign = _per_campaign_summary(trades)
    per_campaign_side = _per_campaign_side_summary(trades)
    per_campaign_pair = _per_campaign_pair_summary(trades)
    per_campaign_fold = _per_campaign_fold_summary(trades)
    per_campaign_pair_fold = _per_campaign_pair_fold_summary(trades)
    pattern = _check_structural_pattern(per_campaign, per_campaign_pair_fold)
    above_floor = _above_floor_cells_vs_null(per_campaign_pair)

    payload: dict[str, object] = {
        "verdict_word_ban_acknowledged": True,
        "sprint_id": "research-exit-asymmetry-cross-campaign-001",
        "phase": "1+2",
        "headline": {
            "n_trades_total": len(trades),
            "n_campaigns": len(CAMPAIGNS),
            "n_pairs": len(SEVEN_MAJORS),
            "n_folds_per_campaign": 8,
            "exit_reason_vocabulary": sorted(trades["exit_reason"].unique().tolist()),
            "campaigns": list(CAMPAIGNS),
            "null_campaign": NULL_CAMPAIGN,
            "material_gap_r_floor": MATERIAL_GAP_R,
            "hard_stop_r_threshold": HARD_STOP_R_LE,
            "time_exit_small_band": [TIME_EXIT_SMALL_BAND_LO, TIME_EXIT_SMALL_BAND_HI],
        },
        "per_campaign": _round_records(_frame_to_records(per_campaign)),
        "per_campaign_side": _round_records(_frame_to_records(per_campaign_side)),
        "per_campaign_pair": _round_records(_frame_to_records(per_campaign_pair)),
        "per_campaign_fold": _round_records(_frame_to_records(per_campaign_fold)),
        "per_campaign_pair_fold_stop_rate_dispersion": {
            "median_per_pair_stop_rate_std_across_folds": pattern[
                "condition_4_fold_noise_driver"
            ]["observed_median_per_pair_stop_rate_std"],
        },
        "structural_pattern_check": pattern,
        "above_floor_cells_vs_null": above_floor,
        "provenance": prov.to_dict(),
        "refusals": {
            "approves_strategy": False,
            "changes_campaign_verdict": False,
            "proposes_parameter_tune": False,
            "writes_to_approved_strategies_yaml": False,
        },
    }

    out_json = OUTPUTS / "exit_asymmetry_cross_campaign.json"
    out_md = OUTPUTS / "exit_asymmetry_cross_campaign.md"
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")
    out_md.write_text(_build_markdown(payload), encoding="utf-8")
    return payload


if __name__ == "__main__":
    main()

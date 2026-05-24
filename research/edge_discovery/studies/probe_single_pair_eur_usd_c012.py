"""Single-pair probe — extract the EUR_USD / CAMPAIGN_012 evidence
slice and its CAMPAIGN_011 EUR_USD null counterpart.

Phase 1 of the research-edge-discovery-lab-single-pair-probe-001
sprint. This is a pure extraction: no decisions, no classification,
no recommendation — just a clean, reproducible dump of the per-fold
metrics and the per-trade ledger for EUR_USD under CAMPAIGN_012,
side-by-side with CAMPAIGN_011's EUR_USD numbers.

Outputs go to research/edge_discovery/studies/outputs/real/
probe_single_pair_eur_usd_c012.{json,md}. Phase 2's robustness
script consumes the JSON.

Exploratory lab output. Not strategy evidence. CAMPAIGN_012 remains
REJECT.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.edge_discovery.real_data import (
    StudyInput,
    StudyProvenance,
    assert_real_data_kind,
    fold_pair_summaries_to_frame,
    load_campaign_fold_pair_summaries,
    load_campaign_trades,
    load_campaign_walk_forward_result,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs" / "real"

PAIR = "EUR_USD"
CAMPAIGN_DIR = REPO_ROOT / "backtests" / "CAMPAIGN_012_regime_switcher_atr_percentile"
NULL_DIR = REPO_ROOT / "backtests" / "CAMPAIGN_011_random_entry_anchor"


def _per_fold_for_pair(campaign_dir: Path, pair: str) -> pd.DataFrame:
    """Return one row per fold for the given pair under the given
    campaign, sorted by fold index. Columns include every metric
    available in the committed summary JSON."""
    summaries = load_campaign_fold_pair_summaries(campaign_dir)
    df = fold_pair_summaries_to_frame(summaries)
    return df[df["instrument"] == pair].sort_values("fold_index").reset_index(drop=True)


def _drawdown_streak(r_series: pd.Series) -> dict[str, float]:
    """Compute the maximum cumulative-R drawdown and the longest
    losing-streak (consecutive trades with r_multiple <= 0)."""
    if r_series.empty:
        return {"max_drawdown_r": 0.0, "longest_losing_streak": 0, "longest_winning_streak": 0}
    cum = r_series.cumsum().to_numpy()
    running_max = np.maximum.accumulate(cum)
    drawdown = cum - running_max
    max_dd = float(drawdown.min())
    # streaks
    longest_loss = current_loss = 0
    longest_win = current_win = 0
    for r in r_series:
        if r <= 0:
            current_loss += 1
            longest_loss = max(longest_loss, current_loss)
            current_win = 0
        else:
            current_win += 1
            longest_win = max(longest_win, current_win)
            current_loss = 0
    return {
        "max_drawdown_r": max_dd,
        "longest_losing_streak": int(longest_loss),
        "longest_winning_streak": int(longest_win),
    }


def run() -> Path:
    cand_per_fold = _per_fold_for_pair(CAMPAIGN_DIR, PAIR)
    null_per_fold = _per_fold_for_pair(NULL_DIR, PAIR)

    # Load the per-trade ledger for both campaigns, EUR_USD only.
    cand_trades = load_campaign_trades(CAMPAIGN_DIR, instruments=[PAIR])
    null_trades = load_campaign_trades(NULL_DIR, instruments=[PAIR])

    cand_wf = load_campaign_walk_forward_result(CAMPAIGN_DIR)
    null_wf = load_campaign_walk_forward_result(NULL_DIR)

    # --- per-fold gap ---
    # Outer join on fold_index so we always have 8 paired rows.
    merged = pd.merge(
        cand_per_fold[["fold_index", "metric_expectancy_r", "metric_trade_count",
                       "metric_total_return_pct", "metric_profit_factor",
                       "metric_win_rate", "metric_max_drawdown_pct",
                       "metric_average_spread_paid_pips"]],
        null_per_fold[["fold_index", "metric_expectancy_r", "metric_trade_count"]].rename(
            columns={
                "metric_expectancy_r": "null_metric_expectancy_r",
                "metric_trade_count": "null_metric_trade_count",
            }
        ),
        on="fold_index",
        how="outer",
    ).sort_values("fold_index").reset_index(drop=True)
    merged["per_fold_gap_r"] = merged["metric_expectancy_r"] - merged["null_metric_expectancy_r"]

    # --- aggregate gap ---
    cand_mean = float(cand_per_fold["metric_expectancy_r"].mean())
    null_mean = float(null_per_fold["metric_expectancy_r"].mean())
    mean_gap = cand_mean - null_mean
    median_cand = float(cand_per_fold["metric_expectancy_r"].median())
    median_null = float(null_per_fold["metric_expectancy_r"].median())
    median_gap = float(merged["per_fold_gap_r"].median())

    # SE of the mean gap: treat per-fold expectancy R values as 8
    # independent observations.
    n_folds = int(len(cand_per_fold))
    cand_std = float(cand_per_fold["metric_expectancy_r"].std(ddof=1))
    null_std = float(null_per_fold["metric_expectancy_r"].std(ddof=1))
    # Conservative SE assuming independent across folds (paired-diff SE).
    gap_std = float(merged["per_fold_gap_r"].std(ddof=1))
    se_mean_gap = gap_std / np.sqrt(n_folds) if n_folds > 1 else float("nan")
    t_stat = mean_gap / se_mean_gap if se_mean_gap and se_mean_gap > 0 else float("nan")

    # --- per-fold direction / dominance ---
    cand_positive_folds = int((cand_per_fold["metric_expectancy_r"] > 0).sum())
    gap_positive_folds = int((merged["per_fold_gap_r"] > 0).sum())

    # Cumulative R per fold (expectancy × trade_count is an approx of
    # "R contribution"). Use trade-level cumulative R for the candidate
    # (more accurate) by groupby fold_index.
    cand_trades_with_r = cand_trades.copy()
    cand_trades_with_r["r_multiple"] = cand_trades_with_r["r_multiple"].astype(float)
    fold_cum_r = (
        cand_trades_with_r.groupby("fold_index")["r_multiple"].sum().to_dict()
    )
    total_r = float(sum(fold_cum_r.values()))
    top_fold = (
        max(fold_cum_r.items(), key=lambda kv: kv[1]) if fold_cum_r else (None, 0.0)
    )
    top_fold_idx = top_fold[0]
    top_fold_cum_r = float(top_fold[1])
    top_fold_share = (
        abs(top_fold_cum_r) / max(abs(total_r), 1e-12) if total_r != 0 else 0.0
    )
    fold_cum_share_signed = {
        int(k): (float(v) / total_r if total_r != 0 else 0.0)
        for k, v in fold_cum_r.items()
    }

    # --- drawdown / streaks for candidate ---
    # Use chronological order of trades for the streak measurement.
    cand_chrono = cand_trades_with_r.sort_values("entry_time").reset_index(drop=True)
    streaks = _drawdown_streak(cand_chrono["r_multiple"])

    # --- direction / exit / session distributions (candidate only) ---
    side_counts = cand_chrono["side"].astype(str).value_counts().to_dict()
    side_mean_r = (
        cand_chrono.groupby(cand_chrono["side"].astype(str))["r_multiple"]
        .mean()
        .to_dict()
    )
    exit_counts = cand_chrono["exit_reason"].astype(str).value_counts().to_dict()
    exit_mean_r = (
        cand_chrono.groupby(cand_chrono["exit_reason"].astype(str))["r_multiple"]
        .mean()
        .to_dict()
    )
    # Hour-of-day breakdown for entry timestamps (UTC).
    cand_chrono["entry_hour_utc"] = cand_chrono["entry_time"].dt.hour
    hour_counts = cand_chrono["entry_hour_utc"].value_counts().sort_index().to_dict()
    hour_mean_r = cand_chrono.groupby("entry_hour_utc")["r_multiple"].mean().to_dict()

    # --- top-N trade dominance ---
    sorted_r = cand_chrono["r_multiple"].sort_values(ascending=False)
    top5_pct_n = max(1, int(len(sorted_r) * 0.05))
    top10_pct_n = max(1, int(len(sorted_r) * 0.10))
    top5_share = (
        float(sorted_r.head(top5_pct_n).sum() / max(abs(sorted_r.sum()), 1e-12))
        if sorted_r.sum() != 0 else 0.0
    )
    top10_share = (
        float(sorted_r.head(top10_pct_n).sum() / max(abs(sorted_r.sum()), 1e-12))
        if sorted_r.sum() != 0 else 0.0
    )

    # --- provenance ---
    prov = StudyProvenance(
        data_kind="real",
        inputs=[
            StudyInput(
                kind="campaign_fold_summaries",
                path=str(CAMPAIGN_DIR.relative_to(REPO_ROOT) / "folds"),
                sha256="(56 per-fold per-pair JSON bundle; candidate)",
                rows=len(cand_per_fold) * 7,
                extra={"campaign_name": CAMPAIGN_DIR.name, "role": "candidate", "pair": PAIR},
            ),
            StudyInput(
                kind="campaign_fold_summaries",
                path=str(NULL_DIR.relative_to(REPO_ROOT) / "folds"),
                sha256="(56 per-fold per-pair JSON bundle; null)",
                rows=len(null_per_fold) * 7,
                extra={"campaign_name": NULL_DIR.name, "role": "null", "pair": PAIR},
            ),
            StudyInput(
                kind="campaign_trades",
                path=str(CAMPAIGN_DIR.relative_to(REPO_ROOT)),
                sha256="(per-fold EUR_USD trade CSV bundle)",
                rows=int(len(cand_trades)),
                extra={"campaign_name": CAMPAIGN_DIR.name, "pair": PAIR},
            ),
            StudyInput(
                kind="campaign_walk_forward_results",
                path=str(Path(cand_wf.source_path).relative_to(REPO_ROOT)),
                sha256=cand_wf.source_sha256,
                rows=int(cand_wf.aggregate.get("total_trades_across_folds", 0)),
                extra={"campaign_name": cand_wf.campaign_name, "role": "candidate_aggregate"},
            ),
            StudyInput(
                kind="campaign_walk_forward_results",
                path=str(Path(null_wf.source_path).relative_to(REPO_ROOT)),
                sha256=null_wf.source_sha256,
                rows=int(null_wf.aggregate.get("total_trades_across_folds", 0)),
                extra={"campaign_name": null_wf.campaign_name, "role": "null_aggregate"},
            ),
        ],
        date_coverage={
            "start_utc": str(cand_chrono["entry_time"].min()) if len(cand_chrono) else "",
            "end_utc": str(cand_chrono["exit_time"].max()) if len(cand_chrono) else "",
        },
        pair_universe=[PAIR],
        limitations=[
            "Per-fold expectancy R values are aggregations of small "
            "samples (CAMPAIGN_012 EUR_USD per-fold trade counts range "
            "27-105; CAMPAIGN_011 EUR_USD per-fold range 8-27).",
            "Standard error of the mean gap treats the 8 per-fold "
            "gap values as IID — a coarse approximation that ignores "
            "across-fold correlations from the same underlying market.",
            "Dominance shares are computed on raw r_multiple sums; "
            "they do not net out the lab's full cost overlay.",
            "No campaign verdict is changed by this extraction. "
            "CAMPAIGN_012 remains REJECT.",
        ],
        exploratory_only=True,
    )
    assert_real_data_kind(prov)

    payload = {
        "study_label": "probe_single_pair_eur_usd_c012",
        "pair": PAIR,
        "candidate_campaign": CAMPAIGN_DIR.name,
        "null_campaign": NULL_DIR.name,
        "n_folds": n_folds,
        "candidate": {
            "per_fold": cand_per_fold.to_dict(orient="records"),
            "mean_expectancy_r": cand_mean,
            "median_expectancy_r": median_cand,
            "std_expectancy_r": cand_std,
            "n_folds_positive_expectancy": cand_positive_folds,
            "total_trades": int(cand_per_fold["metric_trade_count"].sum()),
        },
        "null": {
            "per_fold": null_per_fold.to_dict(orient="records"),
            "mean_expectancy_r": null_mean,
            "median_expectancy_r": median_null,
            "std_expectancy_r": null_std,
            "total_trades": int(null_per_fold["metric_trade_count"].sum()),
        },
        "merged_per_fold": merged.to_dict(orient="records"),
        "gap": {
            "mean_gap_r": mean_gap,
            "median_gap_r": median_gap,
            "gap_std": gap_std,
            "se_mean_gap": se_mean_gap,
            "t_stat": t_stat,
            "n_folds_with_positive_gap": gap_positive_folds,
        },
        "candidate_dominance": {
            "total_r_across_folds": total_r,
            "fold_cum_r": {int(k): float(v) for k, v in fold_cum_r.items()},
            "fold_cum_share_signed": fold_cum_share_signed,
            "top_fold_index": int(top_fold_idx) if top_fold_idx is not None else None,
            "top_fold_cum_r": top_fold_cum_r,
            "top_fold_share_of_abs_total": top_fold_share,
            "top_5pct_trades_share_of_total": top5_share,
            "top_10pct_trades_share_of_total": top10_share,
        },
        "candidate_distribution": {
            "side_counts": {str(k): int(v) for k, v in side_counts.items()},
            "side_mean_r": {str(k): float(v) for k, v in side_mean_r.items()},
            "exit_reason_counts": {str(k): int(v) for k, v in exit_counts.items()},
            "exit_reason_mean_r": {str(k): float(v) for k, v in exit_mean_r.items()},
            "entry_hour_utc_counts": {int(k): int(v) for k, v in hour_counts.items()},
            "entry_hour_utc_mean_r": {int(k): float(v) for k, v in hour_mean_r.items()},
        },
        "candidate_streaks": streaks,
        "provenance": prov.to_dict(),
        "verdict_word_ban_acknowledged": True,
        "notes": [
            "Phase 1 extraction only — no classification yet.",
            "Phase 2 robustness script consumes this JSON.",
            "Lab output. Does not approve any strategy or change any "
            "campaign verdict.",
        ],
    }

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUTS / "probe_single_pair_eur_usd_c012.json"
    md_path = OUTPUTS / "probe_single_pair_eur_usd_c012.md"
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    _write_markdown(md_path, payload)
    return md_path


def _write_markdown(md_path: Path, p: dict[str, object]) -> None:
    lines: list[str] = []
    lines.append(f"# Single-pair probe (Phase 1 extraction) — {p['study_label']}")
    lines.append("")
    lines.append("> Exploratory lab output. Not a strategy verdict; does not approve,")
    lines.append("> promote, or change any campaign status. CAMPAIGN_012 remains REJECT;")
    lines.append("> CAMPAIGN_011 remains the null model.")
    lines.append("")
    prov = p["provenance"]
    lines.append("## Provenance")
    lines.append(f"- data_kind: `{prov['data_kind']}`")
    lines.append(f"- pair: `{p['pair']}`")
    lines.append(f"- candidate: `{p['candidate_campaign']}`")
    lines.append(f"- null: `{p['null_campaign']}`")
    lines.append(f"- date coverage: `{prov['date_coverage']['start_utc']}` → `{prov['date_coverage']['end_utc']}`")
    lines.append("- limitations:")
    for limit in prov["limitations"]:
        lines.append(f"  - {limit}")
    lines.append("")
    lines.append("## Per-fold candidate vs null")
    lines.append("")
    lines.append("| fold | C012 expectancy R | C012 trades | C012 PF | C012 ret % | C011 expectancy R | C011 trades | gap R |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in p["merged_per_fold"]:
        lines.append(
            f"| {int(row['fold_index'])} | {float(row['metric_expectancy_r']):+.4f} | "
            f"{int(row['metric_trade_count'])} | {float(row['metric_profit_factor']):.3f} | "
            f"{float(row['metric_total_return_pct']):+.3f} | "
            f"{float(row['null_metric_expectancy_r']):+.4f} | "
            f"{int(row['null_metric_trade_count'])} | "
            f"**{float(row['per_fold_gap_r']):+.4f}** |"
        )
    lines.append("")
    cand = p["candidate"]
    null = p["null"]
    gap = p["gap"]
    lines.append("## Aggregate gap")
    lines.append("")
    lines.append(f"- C012 EUR_USD: mean = **`{cand['mean_expectancy_r']:+.4f}`** R, "
                 f"median = **`{cand['median_expectancy_r']:+.4f}`** R, "
                 f"std = `{cand['std_expectancy_r']:.4f}`, "
                 f"positive folds = **{cand['n_folds_positive_expectancy']} / {p['n_folds']}**, "
                 f"total trades = {cand['total_trades']}")
    lines.append(f"- C011 EUR_USD (null): mean = **`{null['mean_expectancy_r']:+.4f}`** R, "
                 f"median = `{null['median_expectancy_r']:+.4f}`, "
                 f"std = `{null['std_expectancy_r']:.4f}`, total trades = {null['total_trades']}")
    lines.append(f"- **Mean gap R = `{gap['mean_gap_r']:+.4f}`** "
                 f"(median gap = `{gap['median_gap_r']:+.4f}`)")
    lines.append(f"- Gap std across folds = `{gap['gap_std']:.4f}`; "
                 f"SE of mean gap = `{gap['se_mean_gap']:.4f}`; t-stat = `{gap['t_stat']:.3f}`")
    lines.append(f"- Folds with positive gap (C012 ≥ null): **{gap['n_folds_with_positive_gap']} / {p['n_folds']}**")
    lines.append("")
    lines.append("## Candidate dominance — where does the R come from?")
    lines.append("")
    dom = p["candidate_dominance"]
    lines.append(f"- Total cumulative R across folds (sum of trade-level R): **`{dom['total_r_across_folds']:+.3f}`**")
    lines.append(f"- Top fold: **fold {dom['top_fold_index']}**, cumulative R = `{dom['top_fold_cum_r']:+.3f}`")
    lines.append(f"- Top-fold share of |total R|: **`{dom['top_fold_share_of_abs_total']:.3f}`** ({dom['top_fold_share_of_abs_total']*100:.1f}%)")
    lines.append(f"- Top 5 % of trades share of total R: `{dom['top_5pct_trades_share_of_total']:.3f}`")
    lines.append(f"- Top 10 % of trades share of total R: `{dom['top_10pct_trades_share_of_total']:.3f}`")
    lines.append("")
    lines.append("### Per-fold cumulative R contribution")
    lines.append("")
    lines.append("| fold | cum R | signed share of total |")
    lines.append("|---:|---:|---:|")
    for fold_idx in sorted(dom["fold_cum_r"]):
        lines.append(
            f"| {fold_idx} | {dom['fold_cum_r'][fold_idx]:+.3f} | "
            f"{dom['fold_cum_share_signed'][fold_idx]:+.3f} |"
        )
    lines.append("")
    dist = p["candidate_distribution"]
    lines.append("## Candidate trade-level distribution")
    lines.append("")
    lines.append("### Side (long vs short)")
    lines.append("")
    lines.append("| side | n | mean R |")
    lines.append("|---|---:|---:|")
    for side in sorted(dist["side_counts"]):
        lines.append(f"| {side} | {dist['side_counts'][side]} | {dist['side_mean_r'].get(side, 0):+.4f} |")
    lines.append("")
    lines.append("### Exit reason")
    lines.append("")
    lines.append("| reason | n | mean R |")
    lines.append("|---|---:|---:|")
    for reason in sorted(dist["exit_reason_counts"]):
        lines.append(f"| {reason} | {dist['exit_reason_counts'][reason]} | {dist['exit_reason_mean_r'].get(reason, 0):+.4f} |")
    lines.append("")
    lines.append("### Entry hour UTC")
    lines.append("")
    lines.append("| hour | n | mean R |")
    lines.append("|---:|---:|---:|")
    for h in sorted(dist["entry_hour_utc_counts"]):
        lines.append(f"| {h:02d} | {dist['entry_hour_utc_counts'][h]} | {dist['entry_hour_utc_mean_r'].get(h, 0):+.4f} |")
    lines.append("")
    streaks = p["candidate_streaks"]
    lines.append("## Candidate streaks (chronological)")
    lines.append("")
    lines.append(f"- Max drawdown (cumulative R): `{streaks['max_drawdown_r']:+.3f}`")
    lines.append(f"- Longest losing streak: `{streaks['longest_losing_streak']}` trades")
    lines.append(f"- Longest winning streak: `{streaks['longest_winning_streak']}` trades")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    for n in p["notes"]:
        lines.append(f"- {n}")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    out = run()
    print(f"wrote {out}")

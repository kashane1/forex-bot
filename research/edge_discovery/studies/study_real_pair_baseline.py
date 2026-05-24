"""Real-data study — pair-level baseline across CAMPAIGN_010-014
folds, compared against the CAMPAIGN_011 random-entry null.

The prior synthetic-fixture pair-baseline study cited verbatim values
from the CAMPAIGN_001-009 report Markdown. This real-data version
goes one layer deeper: it consumes the committed per-fold per-pair
``fold_NN_<PAIR>_summary.json`` files from CAMPAIGN_010-014 and
computes, per pair:

  * the per-pair mean expectancy R averaged across the eight folds
  * the per-pair fold-count where expectancy R cleared the
    CAMPAIGN_011 null by ≥ +0.05 R (the lab's material-gap floor)
  * the per-pair fold-count where expectancy R is strictly positive
  * total trades and average spread across folds × campaigns

CAMPAIGN_011 supplies the per-pair null floor — per-pair
expectancy-R averaged across CAMPAIGN_011's eight folds, NOT a global
campaign aggregate, so the test is "this pair, this strategy: did
they materially beat the same pair under a random-entry null on the
same universe and same fold layout?"

Output: research/edge_discovery/studies/outputs/real/
        real_study_pair_baseline.{json,md}

Exploratory lab output. Not strategy evidence. No campaign verdict
changes.
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
    fold_pair_summaries_to_frame,
    load_campaign_fold_pair_summaries,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs" / "real"

CAMPAIGNS_TO_STUDY = (
    "CAMPAIGN_010_session_breakout",
    "CAMPAIGN_012_regime_switcher_atr_percentile",
    "CAMPAIGN_013_cross_pair_currency_strength_rotation",
    "CAMPAIGN_014_calendar_event_window_anomaly",
)
NULL_CAMPAIGN = "CAMPAIGN_011_random_entry_anchor"
MATERIAL_GAP_R = 0.05


def _load_all() -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for c in (NULL_CAMPAIGN,) + CAMPAIGNS_TO_STUDY:
        summaries = load_campaign_fold_pair_summaries(REPO_ROOT / "backtests" / c)
        out[c] = fold_pair_summaries_to_frame(summaries)
    return out


def _per_pair_per_campaign(df: pd.DataFrame) -> pd.DataFrame:
    """Reduce a per-fold per-pair frame to one row per pair: mean
    expectancy R across folds, total trades, average spread."""
    rows = []
    for instr, sub in df.groupby("instrument"):
        rows.append({
            "instrument": str(instr),
            "n_folds": len(sub),
            "mean_expectancy_r": float(sub["metric_expectancy_r"].astype(float).mean()),
            "median_expectancy_r": float(sub["metric_expectancy_r"].astype(float).median()),
            "std_expectancy_r": float(sub["metric_expectancy_r"].astype(float).std(ddof=1)) if len(sub) > 1 else 0.0,
            "total_trades": int(sub["metric_trade_count"].astype(int).sum()),
            "avg_spread_pips": float(sub["metric_average_spread_paid_pips"].astype(float).mean()),
            "n_folds_positive_expectancy": int((sub["metric_expectancy_r"].astype(float) > 0).sum()),
        })
    return pd.DataFrame(rows).sort_values("instrument").reset_index(drop=True)


def _per_pair_gap_table(
    null_per_pair: pd.DataFrame,
    campaign_per_pair: dict[str, pd.DataFrame],
) -> list[dict[str, object]]:
    """For each pair, compute the gap from each campaign's per-pair
    expectancy R to the null's per-pair expectancy R."""
    null_lookup = null_per_pair.set_index("instrument")["mean_expectancy_r"].to_dict()
    rows: list[dict[str, object]] = []
    for pair in SEVEN_MAJORS:
        null_r = float(null_lookup.get(pair, 0.0))
        gaps_by_campaign: dict[str, float] = {}
        camp_r_by_campaign: dict[str, float] = {}
        for c, df in campaign_per_pair.items():
            d = df.set_index("instrument")
            if pair not in d.index:
                continue
            camp_r = float(d.loc[pair, "mean_expectancy_r"])
            camp_r_by_campaign[c] = camp_r
            gaps_by_campaign[c] = round(camp_r - null_r, 4)
        if not gaps_by_campaign:
            continue
        best_c, best_g = max(gaps_by_campaign.items(), key=lambda kv: kv[1])
        n_above = sum(1 for g in gaps_by_campaign.values() if g >= MATERIAL_GAP_R)
        rows.append({
            "pair": pair,
            "null_r": null_r,
            "campaign_r_by_campaign": camp_r_by_campaign,
            "gap_r_by_campaign": gaps_by_campaign,
            "best_campaign": best_c,
            "best_gap_r": best_g,
            "n_materially_above_null": n_above,
        })
    return rows


def run() -> Path:
    frames = _load_all()
    null_per_pair = _per_pair_per_campaign(frames[NULL_CAMPAIGN])
    per_pair_by_campaign: dict[str, pd.DataFrame] = {
        c: _per_pair_per_campaign(frames[c]) for c in CAMPAIGNS_TO_STUDY
    }
    gap_table = _per_pair_gap_table(null_per_pair, per_pair_by_campaign)
    summary_pairs_materially_above = [
        r["pair"] for r in gap_table if int(r["n_materially_above_null"]) > 0  # type: ignore[arg-type]
    ]
    summary_pairs_with_any_positive_gap = [
        r["pair"] for r in gap_table if float(r["best_gap_r"]) > 0  # type: ignore[arg-type]
    ]

    # Provenance inputs: 5 campaign fold-summaries directories.
    inputs = [
        StudyInput(
            kind="campaign_fold_summaries",
            path=f"backtests/{c}/folds",
            sha256="(56 per-fold per-pair JSON bundle)",
            rows=len(frames[c]),
            extra={"campaign_name": c, "role": "null" if c == NULL_CAMPAIGN else "candidate"},
        )
        for c in (NULL_CAMPAIGN,) + CAMPAIGNS_TO_STUDY
    ]
    prov = StudyProvenance(
        data_kind="real",
        inputs=inputs,
        date_coverage={
            "start_utc": "2020-01-01T00:00:00+00:00",
            "end_utc": "2026-05-19T21:00:00+00:00",
        },
        pair_universe=list(SEVEN_MAJORS),
        limitations=[
            f"Material-gap floor is +{MATERIAL_GAP_R} R per-pair; this is the "
            "lab's universe-wide material threshold per the candidate "
            "ranking rules, NOT a significance test.",
            "Per-pair mean expectancy R is computed across the 8 walk-"
            "forward folds. Folds use rolling test windows, so this is "
            "an across-time aggregation per pair.",
            "CAMPAIGN_011 supplies the null floor per pair, not a global "
            "scalar — same universe, same fold layout, random entries.",
            "No campaign verdict is changed by this study. CAMPAIGN_010, "
            "012, 013, 014 remain REJECT and CAMPAIGN_011 remains the "
            "null model.",
        ],
        exploratory_only=True,
    )
    assert_real_data_kind(prov)

    payload = {
        "study_label": "real_pair_baseline",
        "null_campaign": NULL_CAMPAIGN,
        "candidate_campaigns": list(CAMPAIGNS_TO_STUDY),
        "null_per_pair": null_per_pair.to_dict(orient="records"),
        "candidate_per_pair_by_campaign": {
            c: df.to_dict(orient="records")
            for c, df in per_pair_by_campaign.items()
        },
        "gap_table": gap_table,
        "rollup": {
            "pairs_materially_above_null_in_any_candidate": summary_pairs_materially_above,
            "pairs_with_any_positive_gap": summary_pairs_with_any_positive_gap,
            "material_gap_floor_r": MATERIAL_GAP_R,
        },
        "provenance": prov.to_dict(),
        "verdict_word_ban_acknowledged": True,
        "notes": [
            "If a future real candidate's per-pair mean R clears this "
            "table's pairs by the material gap, the candidate has a "
            "defensible starting point for a formal pre-commit on those "
            "pairs only — broadcast claims (\"works on all pairs\") "
            "remain forbidden by the lab's pair-concentration ranking "
            "rule.",
            "The current real-data answer to 'is there a pair where any "
            "of CAMPAIGN_010-014 cleanly beat the random-entry null?' "
            "is captured by `pairs_materially_above_null_in_any_candidate`.",
        ],
    }

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUTS / "real_study_pair_baseline.json"
    md_path = OUTPUTS / "real_study_pair_baseline.md"
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    _write_markdown(md_path, payload)
    return md_path


def _write_markdown(md_path: Path, p: dict[str, object]) -> None:
    lines: list[str] = []
    lines.append(f"# Edge-discovery study (real data) — {p['study_label']}")
    lines.append("")
    lines.append("> Exploratory lab output. Not a strategy verdict; does not approve,")
    lines.append("> promote, or change any campaign status. CAMPAIGN_010 / 012 / 013 /")
    lines.append("> 014 remain REJECT; CAMPAIGN_011 remains the null model.")
    lines.append("")
    lines.append("## Provenance")
    prov = p["provenance"]
    lines.append(f"- data_kind: `{prov['data_kind']}`")
    lines.append(f"- pair universe: `{prov['pair_universe']}`")
    lines.append(f"- date coverage: `{prov['date_coverage']['start_utc']}` → `{prov['date_coverage']['end_utc']}`")
    lines.append("- limitations:")
    for limit in prov["limitations"]:
        lines.append(f"  - {limit}")
    lines.append("")
    lines.append("## Null per pair (CAMPAIGN_011 mean expectancy R across 8 folds)")
    lines.append("")
    lines.append("| pair | mean R | median R | std R | n folds positive | total trades | avg spread (pips) |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for row in p["null_per_pair"]:
        lines.append(
            f"| {row['instrument']} | {row['mean_expectancy_r']:+.4f} | "
            f"{row['median_expectancy_r']:+.4f} | {row['std_expectancy_r']:.4f} | "
            f"{int(row['n_folds_positive_expectancy'])} | {int(row['total_trades'])} | "
            f"{row['avg_spread_pips']:.2f} |"
        )
    lines.append("")
    lines.append("## Gap-from-null table (one row per pair, columns are candidates)")
    lines.append("")
    candidate_campaigns = p["candidate_campaigns"]
    header_cols = ["pair", "null R"]
    for c in candidate_campaigns:
        short = c.replace("CAMPAIGN_", "C")
        header_cols.append(f"{short} R")
        header_cols.append(f"gap {short}")
    header_cols.extend(["best campaign", "best gap", "n above null"])
    lines.append("| " + " | ".join(header_cols) + " |")
    lines.append("|" + "|".join(["---"] * len(header_cols)) + "|")
    for row in p["gap_table"]:
        cells: list[str] = [str(row["pair"]), f"{row['null_r']:+.4f}"]
        for c in candidate_campaigns:
            cr = row["campaign_r_by_campaign"].get(c)
            gr = row["gap_r_by_campaign"].get(c)
            cells.append(f"{cr:+.4f}" if cr is not None else "—")
            cells.append(f"{gr:+.4f}" if gr is not None else "—")
        best_short = str(row["best_campaign"]).replace("CAMPAIGN_", "C")
        cells.append(best_short)
        cells.append(f"{row['best_gap_r']:+.4f}")
        cells.append(str(row["n_materially_above_null"]))
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("## Roll-up")
    rollup = p["rollup"]
    lines.append(f"- Material-gap floor: **`+{rollup['material_gap_floor_r']}`** R")
    lines.append(
        f"- Pairs where ANY candidate cleared the null by the material "
        f"gap: **`{rollup['pairs_materially_above_null_in_any_candidate']}`**"
    )
    lines.append(
        f"- Pairs where ANY candidate had ANY positive gap (even within "
        f"noise): **`{rollup['pairs_with_any_positive_gap']}`**"
    )
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

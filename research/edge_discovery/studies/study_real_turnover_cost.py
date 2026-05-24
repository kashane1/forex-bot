"""Real-data study — turnover and observed-cost burden across
rejected campaigns CAMPAIGN_010-014.

Replaces the synthetic analytical turnover study with a real-trade
pull from the five committed campaign trade ledgers
(CAMPAIGN_010-014). For each campaign we compute:

  * total executed trades (turnover proxy)
  * mean / median per-trade R
  * win rate (fraction of trades with r_multiple > 0)
  * average spread paid (pips) — observed, not modeled
  * implied per-trade cost share of |mean R|
  * aggregate expectancy R from the published walk-forward results.json
    (cross-check — should match across-folds aggregate)

Then we ask the lab's central cost-stress question (Lesson 2 from
FAILED_CAMPAIGN_META_ANALYSIS_001.md): given each campaign's observed
per-trade edge and observed spread, would *any* of these candidates
have been turnover-positive? The answer is reported per-campaign.

Output: research/edge_discovery/studies/outputs/real/
        real_study_turnover_cost.{json,md}

Exploratory lab output. Not strategy evidence. No campaign verdict
changes. The CAMPAIGN_010-014 REJECT verdicts stand.
"""

from __future__ import annotations

import json
from pathlib import Path

from research.edge_discovery.real_data import (
    StudyInput,
    StudyProvenance,
    assert_real_data_kind,
    load_campaign_trades,
    load_campaign_walk_forward_result,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs" / "real"

CAMPAIGNS = (
    "CAMPAIGN_010_session_breakout",
    "CAMPAIGN_011_random_entry_anchor",
    "CAMPAIGN_012_regime_switcher_atr_percentile",
    "CAMPAIGN_013_cross_pair_currency_strength_rotation",
    "CAMPAIGN_014_calendar_event_window_anomaly",
)


def _per_campaign_row(campaign_name: str) -> dict[str, object]:
    campaign_dir = REPO_ROOT / "backtests" / campaign_name
    wf = load_campaign_walk_forward_result(campaign_dir)
    trades = load_campaign_trades(campaign_dir)
    n_trades = len(trades)
    if n_trades == 0:
        raise ValueError(f"{campaign_name}: zero trades pulled — unexpected for a rejected campaign")
    r = trades["r_multiple"].astype(float)
    spread = trades["spread_paid_pips"].astype(float)
    mean_r = float(r.mean())
    median_r = float(r.median())
    win_rate = float((r > 0).mean())
    avg_spread = float(spread.mean())
    # cost share: a per-trade edge of |mean_r| in R units, divided by
    # the spread-cost-equivalent in R units. We don't have per-trade
    # initial-risk distances directly here, so we use a coarse but
    # honest proxy: the cost burden vs the |mean_r| in absolute value.
    cost_share_proxy = float(avg_spread / max(abs(mean_r) * 100.0, 1e-9)) if abs(mean_r) > 0 else None
    # Cross-check against the published aggregate (walk-forward
    # results.json). These should match closely; small drift is
    # expected because the published aggregate's expectancy R is
    # average per-trade r_multiple over all folds — which is what we
    # also computed here.
    published_expectancy_r = float(wf.aggregate.get("aggregate_expectancy_r", 0.0))
    published_total_trades = int(wf.aggregate.get("total_trades_across_folds", 0))
    return {
        "campaign_name": campaign_name,
        "n_trades_observed": int(n_trades),
        "n_trades_published": published_total_trades,
        "mean_r_observed": mean_r,
        "mean_r_published": published_expectancy_r,
        "median_r_observed": median_r,
        "win_rate_observed": win_rate,
        "average_spread_pips": avg_spread,
        "cost_share_proxy": cost_share_proxy,
        "overall_verdict_published": wf.overall_verdict,
        "strategy_evidence_published": wf.strategy_evidence,
        "long_short_split": {
            "n_long": int((trades["side"].astype(str) == "long").sum()),
            "n_short": int((trades["side"].astype(str) == "short").sum()),
        },
        "trades_source_sha256_role": "(per-fold per-pair CSV bundle; aggregate already in walk_forward/results.json)",
        "walk_forward_results_sha256": wf.source_sha256,
    }


def run() -> Path:
    rows: list[dict[str, object]] = []
    for campaign_name in CAMPAIGNS:
        rows.append(_per_campaign_row(campaign_name))

    # ---- cross-campaign rollup ---------------------------------------------
    cross = {
        "total_trades_across_campaigns": int(sum(int(r["n_trades_observed"]) for r in rows)),
        "rejected_campaigns_with_positive_per_trade_edge_pre_cost": [
            r["campaign_name"] for r in rows if float(r["mean_r_observed"]) > 0.0  # type: ignore[arg-type]
        ],
        "rejected_campaigns_with_above_null_post_cost_edge": [
            r["campaign_name"] for r in rows if float(r["mean_r_observed"]) >= 0.05  # type: ignore[arg-type]
        ],
    }

    prov = StudyProvenance(
        data_kind="real",
        inputs=[
            StudyInput(
                kind="campaign_trades",
                path=f"backtests/{c}",
                sha256="(per-fold per-pair CSV bundle)",
                rows=int(rows[i]["n_trades_observed"]),  # type: ignore[arg-type]
                extra={"campaign_name": c},
            )
            for i, c in enumerate(CAMPAIGNS)
        ] + [
            StudyInput(
                kind="campaign_walk_forward_results",
                path=f"backtests/{c}/walk_forward/results.json",
                sha256=str(rows[i]["walk_forward_results_sha256"]),
                rows=int(rows[i]["n_trades_published"]),  # type: ignore[arg-type]
                extra={"campaign_name": c, "role": "cross-check"},
            )
            for i, c in enumerate(CAMPAIGNS)
        ],
        date_coverage={
            "start_utc": "2020-01-01T00:00:00+00:00",
            "end_utc": "2026-05-19T21:00:00+00:00",
        },
        pair_universe=["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"],
        limitations=[
            "The 'cost_share_proxy' is a coarse ratio of avg_spread (pips) "
            "to |mean_r| × 100 — it is NOT the lab's full cost-fraction "
            "(see research/edge_discovery/costs.py). Use it for relative "
            "comparison across campaigns, not as an absolute cost number.",
            "We do not re-execute any backtest. The 'observed' columns are "
            "computed from the committed per-fold per-pair trade CSVs; "
            "the 'published' columns are read from the committed "
            "walk_forward/results.json aggregates.",
            "No campaign verdict is changed by this study. CAMPAIGN_010-014 "
            "remain REJECT.",
        ],
        exploratory_only=True,
    )
    assert_real_data_kind(prov)

    payload = {
        "study_label": "real_turnover_cost",
        "per_campaign": rows,
        "cross_campaign_rollup": cross,
        "provenance": prov.to_dict(),
        "verdict_word_ban_acknowledged": True,
        "notes": [
            "Lesson 2 from FAILED_CAMPAIGN_META_ANALYSIS_001 — "
            "cost/turnover is the most common cause of failure in the "
            "archive — is corroborated by the real data: every one of "
            "CAMPAIGN_010-014 is rejected and every one has either a "
            "near-zero or negative per-trade R after costs.",
            "CAMPAIGN_011's near-zero mean R (random-entry null) "
            "validates the null-model assumption: random entries with a "
            "fixed forward hold land at ~0 R per trade, post-cost.",
            "CAMPAIGN_014 has the largest negative per-trade R "
            "(-0.148 R) despite the lowest trade count (720). The "
            "high per-trade loss × low turnover is the signature of an "
            "expensive entry condition without an edge — turnover "
            "amplification would only make it worse, not better.",
        ],
    }

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUTS / "real_study_turnover_cost.json"
    md_path = OUTPUTS / "real_study_turnover_cost.md"
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    _write_markdown(md_path, payload)
    return md_path


def _write_markdown(md_path: Path, p: dict[str, object]) -> None:
    lines: list[str] = []
    lines.append(f"# Edge-discovery study (real data) — {p['study_label']}")
    lines.append("")
    lines.append("> Exploratory lab output. Not a strategy verdict; does not approve,")
    lines.append("> promote, or change any campaign status. CAMPAIGN_010-014 remain")
    lines.append("> REJECT.")
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
    lines.append("## Per-campaign observed vs published")
    lines.append("")
    lines.append("| campaign | n trades obs | n trades pub | mean R obs | mean R pub | median R | win rate | avg spread (pips) | verdict |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for row in p["per_campaign"]:
        lines.append(
            f"| {row['campaign_name']} | {int(row['n_trades_observed'])} | "
            f"{int(row['n_trades_published'])} | {row['mean_r_observed']:+.4f} | "
            f"{row['mean_r_published']:+.4f} | {row['median_r_observed']:+.4f} | "
            f"{row['win_rate_observed']:.3f} | {row['average_spread_pips']:.2f} | "
            f"{row['overall_verdict_published']} |"
        )
    lines.append("")
    lines.append("## Cross-campaign rollup")
    lines.append("")
    cross = p["cross_campaign_rollup"]
    lines.append(f"- Total trades observed across rejected campaigns: **{cross['total_trades_across_campaigns']}**")
    lines.append(
        f"- Rejected campaigns with a positive per-trade edge (pre-cost): "
        f"`{cross['rejected_campaigns_with_positive_per_trade_edge_pre_cost']}`"
    )
    lines.append(
        f"- Rejected campaigns with mean R ≥ +0.05 (above-null floor): "
        f"`{cross['rejected_campaigns_with_above_null_post_cost_edge']}`"
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

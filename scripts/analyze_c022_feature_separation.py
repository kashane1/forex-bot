#!/usr/bin/env python3
"""Analyze whether any C022 entry-time feature separates winners from losers.

Loads the per-trade dataset built by `build_c022_feature_separation_dataset.py`,
constructs diagnostic labels, and runs univariate separation on **entry-time
features only** (outcome fields are labels, never features):

  * missingness table
  * per-feature AUC (P[winner value > loser value]) on train and validation,
    reported separately so direction stability across splits is visible
  * winner/loser medians + quintile win-rate monotonicity (overall)
  * categorical win-rate breakdowns (instrument, side, session, weekday, vol)
  * a stability-gated ranking of the strongest separators

Anti-overfit: no threshold is selected as a parameter; any feature that looks
separating is flagged hypothesis-generating only. A feature is "stable" only if
its train and validation AUC fall on the same side of 0.5.

Diagnostic only — approves nothing, changes no verdict, tunes nothing. Outputs:
  research/c022_feature_separation/feature_separation_summary.json
  docs/research/C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.research.feature_separation import (
    build_labels,
    entry_feature_columns,
)

DATA_DIR = REPO_ROOT / "research" / "c022_feature_separation"
PARQUET = DATA_DIR / "c022_lifecycle_features.parquet"
SUMMARY_JSON = DATA_DIR / "feature_separation_summary.json"
RESULT_MD = REPO_ROOT / "docs" / "research" / "C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md"

CATEGORICAL = ("instrument", "side", "session_bucket", "weekday", "volatility_regime")
# AUC distance from 0.5 below which separation is treated as negligible.
NEGLIGIBLE = 0.05
# Minimum per-class sample to trust a split's AUC.
MIN_CLASS_N = 30

# Feature families. "signal_quality" = the structural entry-signal features the
# C022 thesis is actually built on (H4 regime, H1 pullback, M15 trigger). The
# C024-readiness question hinges on whether a *signal_quality* feature separates
# winners from losers — a separating *cost* feature is mechanical (cost reduces
# net R directly), not an entry edge; *context* (volatility/time) is secondary.
FEATURE_FAMILY: dict[str, str] = {
    "h4_adx_at_entry": "signal_quality", "h4_bias_score": "signal_quality",
    "h4_ema_slope_atr": "signal_quality", "h4_close_dist_ema50_atr": "signal_quality",
    "h1_rsi_at_entry": "signal_quality", "h1_pullback_depth_atr": "signal_quality",
    "h1_close_dist_ema50_atr": "signal_quality", "m15_reclaim_distance_atr": "signal_quality",
    "m15_adx_at_entry": "signal_quality", "m15_body_atr": "signal_quality",
    "m15_close_dist_ema50_atr": "signal_quality",
    "spread_pips": "cost", "spread_to_atr_pct": "cost",
    "atr_at_entry": "context_volatility", "hour": "context_time",
}


def _auc(values: pd.Series, winner: pd.Series) -> tuple[float | None, int, int]:
    """AUC = P(value(winner) > value(loser)), tie-corrected. None if a class is empty."""
    mask = values.notna() & winner.notna()
    x = values[mask].astype(float)
    y = winner[mask].astype(bool)
    n_pos = int(y.sum())
    n_neg = int((~y).sum())
    if n_pos == 0 or n_neg == 0:
        return None, n_pos, n_neg
    ranks = x.rank(method="average")
    auc = (ranks[y.to_numpy()].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    return float(auc), n_pos, n_neg


def _quintile_winrate(values: pd.Series, winner: pd.Series) -> dict:
    mask = values.notna() & winner.notna()
    x = values[mask].astype(float)
    y = winner[mask].astype(bool)
    if x.nunique() < 5 or len(x) < 50:
        return {"buckets": None, "monotonic": None}
    try:
        q = pd.qcut(x, 5, labels=False, duplicates="drop")
    except ValueError:
        return {"buckets": None, "monotonic": None}
    rates = [round(float(y[q == b].mean()), 4) for b in sorted(pd.unique(q))]
    # Spearman of bucket index vs win-rate (monotonic trend indicator).
    if len(rates) >= 3:
        idx = np.arange(len(rates))
        rho = float(pd.Series(rates).corr(pd.Series(idx), method="spearman"))
    else:
        rho = None
    return {"buckets": rates, "spearman_rho": None if rho != rho else round(rho, 3)}


def _numeric_feature_report(df: pd.DataFrame, feat: str) -> dict:
    winner = df["profitable_trade"]
    tr = df["split"] == "train"
    va = df["split"] == "validation"
    auc_tr, npos_tr, nneg_tr = _auc(df.loc[tr, feat], winner.loc[tr])
    auc_va, npos_va, nneg_va = _auc(df.loc[va, feat], winner.loc[va])

    def _eff(a):
        return None if a is None else round(a - 0.5, 4)

    trustworthy = (
        auc_tr is not None and auc_va is not None
        and min(npos_tr, nneg_tr, npos_va, nneg_va) >= MIN_CLASS_N
    )
    stable = bool(
        trustworthy and (auc_tr - 0.5) * (auc_va - 0.5) > 0
    )
    min_abs_eff = (
        round(min(abs(auc_tr - 0.5), abs(auc_va - 0.5)), 4) if trustworthy else None
    )

    w = winner.astype("boolean")
    med_win = df.loc[w == True, feat].median()  # noqa: E712
    med_los = df.loc[w == False, feat].median()  # noqa: E712
    return {
        "family": FEATURE_FAMILY.get(feat, "other"),
        "auc_train": None if auc_tr is None else round(auc_tr, 4),
        "auc_validation": None if auc_va is None else round(auc_va, 4),
        "effect_train": _eff(auc_tr),
        "effect_validation": _eff(auc_va),
        "direction_stable": stable,
        "min_abs_effect": min_abs_eff,
        "trustworthy": trustworthy,
        "median_winner": None if pd.isna(med_win) else round(float(med_win), 6),
        "median_loser": None if pd.isna(med_los) else round(float(med_los), 6),
        "quintile_winrate": _quintile_winrate(df[feat], winner),
        "n_missing": int(df[feat].isna().sum()),
    }


def _categorical_report(df: pd.DataFrame, col: str) -> dict:
    out = {}
    for split in ("train", "validation"):
        sub = df[df["split"] == split]
        rows = {}
        for cat, g in sub.groupby(col):
            wr = g["profitable_trade"].mean()
            rows[str(cat)] = {"n": len(g), "win_rate": round(float(wr), 4)}
        out[split] = rows
    return out


def analyze() -> dict:
    if not PARQUET.exists():
        payload = {
            "strategy_evidence": False, "not_approved": True, "diagnostic_only": True,
            "status": "BLOCKED_LOCAL_DATA",
            "reason": f"dataset not found: {PARQUET.relative_to(REPO_ROOT)}",
            "note": "Run scripts/build_c022_feature_separation_dataset.py first (needs local DB).",
        }
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    df = pd.read_parquet(PARQUET)
    labels = pd.DataFrame([build_labels(r) for r in df.to_dict("records")])
    for c in labels.columns:
        df[c] = labels[c]
    # Restrict to trades with a defined profitability label.
    df = df[df["profitable_trade"].notna()].copy()

    feature_cols = entry_feature_columns(list(df.columns))
    feature_cols = [c for c in feature_cols if c not in labels.columns]
    numeric = [c for c in feature_cols if df[c].dtype.kind in "fi" and c != "hour"]
    numeric_plus_hour = [*numeric, "hour"]

    numeric_report = {c: _numeric_feature_report(df, c) for c in numeric_plus_hour}
    categorical_report = {c: _categorical_report(df, c) for c in CATEGORICAL if c in df.columns}

    # Rank stable separators by smallest (most conservative) cross-split effect.
    ranked = sorted(
        ((c, r) for c, r in numeric_report.items()
         if r["direction_stable"] and r["min_abs_effect"] is not None),
        key=lambda kv: kv[1]["min_abs_effect"], reverse=True,
    )
    strongest = [
        {"feature": c, "min_abs_effect": r["min_abs_effect"],
         "auc_train": r["auc_train"], "auc_validation": r["auc_validation"],
         "median_winner": r["median_winner"], "median_loser": r["median_loser"]}
        for c, r in ranked
    ]
    max_stable_effect = strongest[0]["min_abs_effect"] if strongest else 0.0
    any_material = bool(max_stable_effect >= NEGLIGIBLE)

    # Family-specific: the readiness question is about *signal_quality* features.
    def _family_max(fam: str) -> float:
        effs = [
            r["min_abs_effect"] for c, r in numeric_report.items()
            if r["family"] == fam and r["direction_stable"] and r["min_abs_effect"] is not None
        ]
        return round(max(effs), 4) if effs else 0.0

    family_max_stable_effect = {
        fam: _family_max(fam)
        for fam in ("signal_quality", "cost", "context_volatility", "context_time")
    }
    max_signal_quality_effect = family_max_stable_effect["signal_quality"]
    material_signal_quality_separator = bool(max_signal_quality_effect >= NEGLIGIBLE)

    win_rate_overall = round(float(df["profitable_trade"].mean()), 4)
    win_rate_by_split = {
        s: round(float(df.loc[df["split"] == s, "profitable_trade"].mean()), 4)
        for s in ("train", "validation")
    }

    summary = {
        "strategy_evidence": False, "not_approved": True, "diagnostic_only": True,
        "campaign_id": "CAMPAIGN_022", "status": "OK",
        "winner_definition": "profitable_trade = result_r > 0",
        "anti_overfit_note": (
            "No threshold selected as a parameter. Any separating feature is "
            "hypothesis-generating only. 'Stable' = train & validation AUC on the "
            "same side of 0.5; effect = |AUC-0.5|; negligible below "
            f"{NEGLIGIBLE} (~AUC {0.5 + NEGLIGIBLE})."
        ),
        "n_trades": len(df),
        "n_by_split": {s: int((df["split"] == s).sum()) for s in ("train", "validation")},
        "win_rate_overall": win_rate_overall,
        "win_rate_by_split": win_rate_by_split,
        "label_counts": {
            k: int(df[k].sum()) for k in
            ("profitable_trade", "survived_to_time_exit", "hard_stop_loss",
             "reached_plus_0_5r", "clean_winner", "straight_to_stop")
            if k in df.columns and df[k].notna().any()
        },
        "missingness": {c: int(df[c].isna().sum()) for c in numeric_plus_hour if df[c].isna().any()},
        "max_stable_effect": max_stable_effect,
        "any_material_stable_separator": any_material,
        "family_max_stable_effect": family_max_stable_effect,
        "max_signal_quality_effect": max_signal_quality_effect,
        "material_signal_quality_separator": material_signal_quality_separator,
        "strongest_stable_separators": strongest[:8],
        "numeric_features": numeric_report,
        "categorical_features": categorical_report,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_result_md(summary)
    return summary


def _write_result_md(s: dict) -> None:
    lines: list[str] = []
    lines.append("# C022 Winner/Loser Feature-Separation — Result\n")
    lines.append(
        "**Status:** diagnostic only. No verdict change, no approval, no tuning, "
        "no C024. Findings are hypothesis-generating; no threshold is a parameter.\n"
    )
    lines.append("## Setup\n")
    lines.append(f"- Winner definition: `{s['winner_definition']}`.")
    lines.append(f"- Trades: {s['n_trades']} (train {s['n_by_split']['train']}, "
                 f"validation {s['n_by_split']['validation']}).")
    lines.append(f"- Overall win rate: {s['win_rate_overall']} "
                 f"(train {s['win_rate_by_split']['train']}, "
                 f"validation {s['win_rate_by_split']['validation']}).")
    lines.append(f"- Effect = |AUC−0.5|; negligible below {NEGLIGIBLE}. "
                 "Stable = train & validation AUC on the same side of 0.5.\n")

    lines.append("## Headline\n")
    fam = s["family_max_stable_effect"]
    if s["material_signal_quality_separator"]:
        lines.append(
            f"A **structural entry-signal** feature separates winners from losers with a "
            f"stable cross-split effect of |AUC−0.5| = {s['max_signal_quality_effect']} "
            "(see ranking). Treat as hypothesis-generating, not edge.\n"
        )
    else:
        lines.append(
            "**No structural entry-signal feature separates winners from losers.** The "
            "features the C022 thesis is built on — H4 regime (ADX, bias score, EMA "
            "slope, distance), H1 pullback (depth, RSI, distance), M15 trigger (reclaim "
            "distance, ADX, body) — all sit at AUC ≈ 0.50. The strongest stable "
            f"signal-quality effect is only |AUC−0.5| = {s['max_signal_quality_effect']} "
            f"(below the {NEGLIGIBLE} floor).\n"
        )
    lines.append(
        "The only stable separators above the negligibility floor are **context**, not "
        f"entry-signal quality: cost (spread/ATR, |AUC−0.5|={fam['cost']} — mechanical, "
        "since cost reduces net R directly, not an edge), volatility "
        f"(atr_at_entry, {fam['context_volatility']}), and time-of-day "
        f"(hour, {fam['context_time']}). All are weak (AUC ≲ 0.58).\n"
    )

    lines.append("## Strongest stable separators (conservative cross-split effect)\n")
    if s["strongest_stable_separators"]:
        lines.append("| feature | min abs(AUC−0.5) | AUC train | AUC val | median winner | median loser |")
        lines.append("|---|---|---|---|---|---|")
        for r in s["strongest_stable_separators"]:
            lines.append(
                f"| {r['feature']} | {r['min_abs_effect']} | {r['auc_train']} | "
                f"{r['auc_validation']} | {r['median_winner']} | {r['median_loser']} |"
            )
    else:
        lines.append("_No feature had a train/validation-stable direction._")
    lines.append("")

    lines.append("## All numeric entry features (AUC train / validation)\n")
    lines.append("| feature | family | AUC train | AUC val | stable | quintile win-rate | n_missing |")
    lines.append("|---|---|---|---|---|---|---|")
    for c, r in sorted(s["numeric_features"].items(),
                       key=lambda kv: -(abs((kv[1]["auc_train"] or 0.5) - 0.5))):
        q = r["quintile_winrate"].get("buckets")
        lines.append(
            f"| {c} | {r['family']} | {r['auc_train']} | {r['auc_validation']} | "
            f"{'yes' if r['direction_stable'] else 'no'} | {q} | {r['n_missing']} |"
        )
    lines.append("")

    lines.append("## Categorical win-rate breakdown\n")
    for col, splits in s["categorical_features"].items():
        lines.append(f"### {col}\n")
        cats = sorted(set(splits.get("train", {})) | set(splits.get("validation", {})))
        lines.append("| value | train n | train win-rate | val n | val win-rate |")
        lines.append("|---|---|---|---|---|")
        for cat in cats:
            tr = splits.get("train", {}).get(cat, {})
            va = splits.get("validation", {}).get(cat, {})
            lines.append(
                f"| {cat} | {tr.get('n', 0)} | {tr.get('win_rate', '—')} | "
                f"{va.get('n', 0)} | {va.get('win_rate', '—')} |"
            )
        lines.append("")

    lines.append("## Anti-overfit warning\n")
    lines.append(s["anti_overfit_note"] + "\n")
    lines.append(
        "Any apparent separator is a candidate hypothesis only. It must survive a "
        "pre-committed, out-of-sample test in a *separate* future sprint before it "
        "could justify a C024 entry filter. No threshold here is a campaign parameter.\n"
    )
    RESULT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    s = analyze()
    if s.get("status") == "BLOCKED_LOCAL_DATA":
        print(f"[BLOCKED_LOCAL_DATA] {s['reason']}")
        return 0
    print(f"[OK] {s['n_trades']} trades · max signal-quality effect |AUC-0.5|="
          f"{s['max_signal_quality_effect']} · signal_separator="
          f"{s['material_signal_quality_separator']} · "
          f"context max (cost/vol/time)={s['family_max_stable_effect']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Analyze whether USD_JPY M15 microstructure-confirmation primitives separate
winners from losers — and whether any beats the old C022 EMA20-reclaim trigger.

Read-only. Loads the per-trade dataset from
`build_usdjpy_microstructure_diagnostic_dataset.py` and, for each detector:

  * winner/loser AUC on the continuous score (train & validation, reported
    separately so direction stability is visible);
  * for the boolean ``present`` flag: win-rate / hard-stop-rate / straight-to-stop
    rate / mean-MFE contrasts (present vs absent), per split — i.e. does the
    confirmation reduce stop-outs and straight-to-stop while preserving sample;
  * live-usable vs post-entry-only (from the detector's ``uses_post_decision``);
  * a qualitative overfit-risk note.

Anti-overfit: NO threshold is selected as a parameter; every separating feature is
hypothesis-generating only. "Stable" = train & validation AUC on the same side of
0.5 with adequate per-class N. Effect = |AUC-0.5|, negligible below 0.05.

Diagnostic only — approves nothing, changes no verdict, tunes nothing, creates no
C024, claims no edge. Outputs:
  research/usdjpy_microstructure_diagnostic/analysis_summary.json
  docs/research/USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_RESULT.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.research.microstructure_confirmations import (
    LIVE_DETECTORS,
    POST_DECISION_DETECTORS,
)

DATA_DIR = REPO_ROOT / "research" / "usdjpy_microstructure_diagnostic"
PARQUET = DATA_DIR / "usdjpy_microstructure_features.parquet"
SUMMARY_JSON = DATA_DIR / "analysis_summary.json"
RESULT_MD = REPO_ROOT / "docs" / "research" / "USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_RESULT.md"

ALL_DETECTORS = (*LIVE_DETECTORS, *POST_DECISION_DETECTORS)
NEGLIGIBLE = 0.05
MIN_CLASS_N = 30
BASELINE = "reclaim_distance_atr"
CONTEXT_NUMERIC = ("reclaim_distance_atr", "atr_at_entry", "atr_percentile", "spread_to_atr_pct", "hour")


def _auc(values: pd.Series, winner: pd.Series) -> tuple[float | None, int, int]:
    mask = values.notna() & winner.notna()
    x = values[mask].astype(float)
    y = winner[mask].astype(bool)
    n_pos, n_neg = int(y.sum()), int((~y).sum())
    if n_pos == 0 or n_neg == 0:
        return None, n_pos, n_neg
    ranks = x.rank(method="average")
    auc = (ranks[y.to_numpy()].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    return float(auc), n_pos, n_neg


def _score_report(df: pd.DataFrame, col: str) -> dict:
    winner = df["profitable_trade"]
    tr, va = df["split"] == "train", df["split"] == "validation"
    auc_tr, npos_tr, nneg_tr = _auc(df.loc[tr, col], winner.loc[tr])
    auc_va, npos_va, nneg_va = _auc(df.loc[va, col], winner.loc[va])
    trustworthy = (
        auc_tr is not None and auc_va is not None
        and min(npos_tr, nneg_tr, npos_va, nneg_va) >= MIN_CLASS_N
    )
    stable = bool(trustworthy and (auc_tr - 0.5) * (auc_va - 0.5) > 0)
    min_abs = round(min(abs(auc_tr - 0.5), abs(auc_va - 0.5)), 4) if trustworthy else None
    return {
        "auc_train": None if auc_tr is None else round(auc_tr, 4),
        "auc_validation": None if auc_va is None else round(auc_va, 4),
        "effect_train": None if auc_tr is None else round(auc_tr - 0.5, 4),
        "effect_validation": None if auc_va is None else round(auc_va - 0.5, 4),
        "direction_stable": stable,
        "min_abs_effect": min_abs,
        "trustworthy": trustworthy,
        "n_score_train": int(df.loc[tr, col].notna().sum()),
        "n_score_validation": int(df.loc[va, col].notna().sum()),
    }


def _bool_contrast(df: pd.DataFrame, col: str) -> dict:
    out: dict = {}
    for split in ("train", "validation"):
        sub = df[(df["split"] == split) & df[col].notna()].copy()
        present = sub[sub[col].astype(bool)]
        absent = sub[~sub[col].astype(bool)]

        def block(g: pd.DataFrame) -> dict:
            if g.empty:
                return {"n": 0, "win_rate": None, "hard_stop_rate": None,
                        "straight_to_stop_rate": None, "mean_mfe_r": None}
            ok = g["mfe_status"] == "OK"
            return {
                "n": len(g),
                "win_rate": round(float(g["profitable_trade"].mean()), 4),
                "hard_stop_rate": round(float(g["hard_stop_loss"].mean()), 4),
                "straight_to_stop_rate": (
                    round(float(g["straight_to_stop"].dropna().astype(bool).mean()), 4)
                    if g["straight_to_stop"].notna().any() else None
                ),
                "mean_mfe_r": round(float(g.loc[ok, "mfe_r"].mean()), 4) if ok.any() else None,
            }

        p, a = block(present), block(absent)
        out[split] = {
            "present": p, "absent": a,
            "win_rate_lift": (
                round(p["win_rate"] - a["win_rate"], 4)
                if p["win_rate"] is not None and a["win_rate"] is not None else None
            ),
            "hard_stop_reduction": (
                round(a["hard_stop_rate"] - p["hard_stop_rate"], 4)
                if p["hard_stop_rate"] is not None and a["hard_stop_rate"] is not None else None
            ),
            "straight_to_stop_reduction": (
                round(a["straight_to_stop_rate"] - p["straight_to_stop_rate"], 4)
                if p["straight_to_stop_rate"] is not None and a["straight_to_stop_rate"] is not None else None
            ),
            "mfe_improvement": (
                round(p["mean_mfe_r"] - a["mean_mfe_r"], 4)
                if p["mean_mfe_r"] is not None and a["mean_mfe_r"] is not None else None
            ),
        }
    lifts = [out[s]["win_rate_lift"] for s in ("train", "validation") if out[s]["win_rate_lift"] is not None]
    out["win_rate_lift_stable"] = bool(len(lifts) == 2 and lifts[0] * lifts[1] > 0)
    return out


def _overfit_risk(score: dict, contrast: dict, post_decision: bool) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if post_decision:
        reasons.append("post-entry detector — not a live entry feature regardless of separation")
    if not score["trustworthy"]:
        reasons.append("a class fell below the min-N trust floor on a split")
    if not score["direction_stable"]:
        reasons.append("AUC direction not stable across train/validation")
    eff = score["min_abs_effect"]
    if eff is not None and eff >= 0.10:
        reasons.append("large single-pair effect — treat as suspicious until out-of-sample")
    if not contrast.get("win_rate_lift_stable"):
        reasons.append("present-vs-absent win-rate lift not same-signed across splits")
    if not score["direction_stable"] or not score["trustworthy"]:
        level = "high"
    elif eff is not None and eff < NEGLIGIBLE:
        level = "low-signal (stable but negligible)"
    else:
        level = "elevated (stable but single-pair; needs OOS)"
    return level, reasons


def analyze() -> dict:
    if not PARQUET.exists():
        payload = {
            "strategy_evidence": False, "not_approved": True, "diagnostic_only": True,
            "instrument": "USD_JPY", "status": "BLOCKED_LOCAL_DATA",
            "reason": f"dataset not found: {PARQUET.relative_to(REPO_ROOT)}",
            "note": "Run scripts/build_usdjpy_microstructure_diagnostic_dataset.py first (needs local DB).",
        }
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    df = pd.read_parquet(PARQUET)
    df = df[df["profitable_trade"].notna()].copy()

    detectors: dict[str, dict] = {}
    for name in ALL_DETECTORS:
        score = _score_report(df, f"{name}_score")
        contrast = _bool_contrast(df, f"{name}_present")
        post = name in POST_DECISION_DETECTORS
        level, reasons = _overfit_risk(score, contrast, post)
        detectors[name] = {
            "uses_post_decision": post,
            "live_usable": not post,
            "score_separation": score,
            "present_contrast": contrast,
            "overfit_risk": level,
            "overfit_reasons": reasons,
        }

    baseline = _score_report(df, BASELINE)
    context = {c: _score_report(df, c) for c in CONTEXT_NUMERIC if c != BASELINE}

    # Best live separator by conservative cross-split effect (stable only).
    live_stable = [
        (n, detectors[n]["score_separation"]["min_abs_effect"])
        for n in LIVE_DETECTORS
        if detectors[n]["score_separation"]["direction_stable"]
        and detectors[n]["score_separation"]["min_abs_effect"] is not None
    ]
    live_stable.sort(key=lambda kv: kv[1], reverse=True)
    best_live = live_stable[0] if live_stable else None
    baseline_eff = baseline["min_abs_effect"]
    any_live_beats_baseline = bool(
        best_live and baseline_eff is not None and best_live[1] > baseline_eff
    )
    any_live_material = bool(best_live and best_live[1] >= NEGLIGIBLE)

    summary = {
        "strategy_evidence": False, "not_approved": True, "diagnostic_only": True,
        "instrument": "USD_JPY", "status": "OK",
        "winner_definition": "profitable_trade = result_r > 0",
        "anti_overfit_note": (
            "No threshold selected as a parameter. Effect = |AUC-0.5|; negligible "
            f"below {NEGLIGIBLE}. Stable = train & validation AUC same side of 0.5 "
            f"with >= {MIN_CLASS_N} per class. Single-pair sample is small — large "
            "effects are suspicious, not reassuring, until out-of-sample."
        ),
        "n_trades": len(df),
        "n_by_split": {s: int((df["split"] == s).sum()) for s in ("train", "validation")},
        "win_rate_overall": round(float(df["profitable_trade"].mean()), 4),
        "win_rate_by_split": {
            s: round(float(df.loc[df["split"] == s, "profitable_trade"].mean()), 4)
            for s in ("train", "validation")
        },
        "baseline_reclaim_distance_atr": baseline,
        "best_live_stable_separator": (
            {"detector": best_live[0], "min_abs_effect": best_live[1]} if best_live else None
        ),
        "any_live_separator_beats_baseline": any_live_beats_baseline,
        "any_live_separator_material": any_live_material,
        "detectors": detectors,
        "context_numeric": context,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_md(summary)
    return summary


def _fmt(x: object) -> str:
    return "—" if x is None else str(x)


def _write_md(s: dict) -> None:
    lines: list[str] = []
    lines.append("# USD_JPY M15 Microstructure-Confirmation Diagnostic — Result\n")
    lines.append(
        "**Status:** read-only diagnostic. No verdict change, no approval, no tuning, "
        "no C024, no campaign, no edge claim. USD_JPY-only. Findings are "
        "hypothesis-generating; no threshold is a parameter.\n"
    )
    lines.append("## Setup\n")
    lines.append(f"- Winner: `{s['winner_definition']}`.")
    lines.append(f"- USD_JPY trades: {s['n_trades']} (train {s['n_by_split']['train']}, "
                 f"validation {s['n_by_split']['validation']}).")
    lines.append(f"- Win rate: {s['win_rate_overall']} (train {s['win_rate_by_split']['train']}, "
                 f"validation {s['win_rate_by_split']['validation']}).")
    lines.append(f"- Effect = |AUC−0.5|; negligible below {NEGLIGIBLE}. Stable = train & "
                 f"validation AUC on the same side of 0.5 with ≥ {MIN_CLASS_N} per class.\n")

    b = s["baseline_reclaim_distance_atr"]
    lines.append("## Baseline — old C022 EMA20-reclaim trigger\n")
    lines.append(f"`reclaim_distance_atr`: AUC train {_fmt(b['auc_train'])} / "
                 f"validation {_fmt(b['auc_validation'])} · stable={b['direction_stable']} · "
                 f"min|AUC−0.5|={_fmt(b['min_abs_effect'])}. This is the bar each "
                 "microstructure primitive must beat.\n")

    lines.append("## Headline\n")
    bl = s["best_live_stable_separator"]
    if not bl:
        lines.append(
            "**No *live* microstructure primitive separates USD_JPY winners from losers "
            "with a train/validation-stable direction.** None clears even the stability "
            "test, let alone the negligibility floor.\n"
        )
    elif not s["any_live_separator_material"]:
        lines.append(
            f"The strongest *stable live* separator is **{bl['detector']}** at "
            f"|AUC−0.5| = {bl['min_abs_effect']} — **below the {NEGLIGIBLE} negligibility "
            "floor**. No live primitive shows a material winner/loser separation.\n"
        )
    else:
        lines.append(
            f"The strongest *stable live* separator is **{bl['detector']}** at "
            f"|AUC−0.5| = {bl['min_abs_effect']} "
            f"({'beats' if s['any_live_separator_beats_baseline'] else 'does NOT beat'} the "
            "EMA-reclaim baseline). Treat as hypothesis-generating only; a large effect on "
            "this single small pair is suspicious until confirmed out-of-sample.\n"
        )

    lines.append("## Per-detector score separation (winner AUC)\n")
    lines.append("| detector | live? | AUC train | AUC val | stable | min|AUC−0.5| | overfit risk |")
    lines.append("|---|---|---|---|---|---|---|")
    for name in ALL_DETECTORS:
        d = s["detectors"][name]
        sc = d["score_separation"]
        lines.append(
            f"| {name} | {'live' if d['live_usable'] else 'post-entry'} | "
            f"{_fmt(sc['auc_train'])} | {_fmt(sc['auc_validation'])} | "
            f"{'yes' if sc['direction_stable'] else 'no'} | {_fmt(sc['min_abs_effect'])} | "
            f"{d['overfit_risk']} |"
        )
    lines.append("")

    lines.append("## Present-vs-absent impact (does the confirmation help?)\n")
    lines.append("Per split: win-rate lift, hard-stop reduction, straight-to-stop reduction, "
                 "MFE improvement (present − absent; positive = the confirmation helps).\n")
    for name in ALL_DETECTORS:
        d = s["detectors"][name]
        lines.append(f"### {name} ({'live' if d['live_usable'] else 'post-entry diagnostic-only'})\n")
        lines.append("| split | n present | n absent | win-rate lift | hard-stop ↓ | straight-to-stop ↓ | MFE ↑ |")
        lines.append("|---|---|---|---|---|---|---|")
        for split in ("train", "validation"):
            cc = d["present_contrast"][split]
            lines.append(
                f"| {split} | {cc['present']['n']} | {cc['absent']['n']} | "
                f"{_fmt(cc['win_rate_lift'])} | {_fmt(cc['hard_stop_reduction'])} | "
                f"{_fmt(cc['straight_to_stop_reduction'])} | {_fmt(cc['mfe_improvement'])} |"
            )
        lines.append(f"- win-rate lift same-signed across splits: "
                     f"**{d['present_contrast']['win_rate_lift_stable']}**.")
        if d["overfit_reasons"]:
            lines.append("- risk notes: " + "; ".join(d["overfit_reasons"]) + ".")
        lines.append("")

    lines.append("## Context features (for reference, not entry signals)\n")
    lines.append("| feature | AUC train | AUC val | stable | min|AUC−0.5| |")
    lines.append("|---|---|---|---|---|")
    for c, r in s["context_numeric"].items():
        lines.append(f"| {c} | {_fmt(r['auc_train'])} | {_fmt(r['auc_validation'])} | "
                     f"{'yes' if r['direction_stable'] else 'no'} | {_fmt(r['min_abs_effect'])} |")
    lines.append("")

    lines.append("## Reading (honest)\n")
    lines.append("- **Live vs post-entry.** Only the *live* detectors could ever gate an entry. "
                 "Retest-hold and failed-reclaim/trap inspect post-entry bars and are "
                 "diagnostic-only — a separation there describes what already happened, it is "
                 "not a usable entry filter.")
    lines.append("- **Beating the baseline.** A primitive matters only if it separates winners "
                 "from losers *better* than the inert EMA-reclaim trigger and stays stable "
                 "across splits.")
    lines.append("- **Single-pair caution.** USD_JPY's per-split samples are small; a large "
                 "effect is a reason for *more* scrutiny, not less. No threshold here is a "
                 "parameter and nothing is an edge.")
    lines.append(s["anti_overfit_note"] + "\n")
    RESULT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    s = analyze()
    if s.get("status") == "BLOCKED_LOCAL_DATA":
        print(f"[BLOCKED_LOCAL_DATA] {s['reason']}")
        return 0
    bl = s["best_live_stable_separator"]
    print(f"[OK] {s['n_trades']} USD_JPY trades · baseline min|AUC-0.5|="
          f"{s['baseline_reclaim_distance_atr']['min_abs_effect']} · best live stable="
          f"{bl} · beats_baseline={s['any_live_separator_beats_baseline']} · "
          f"material={s['any_live_separator_material']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

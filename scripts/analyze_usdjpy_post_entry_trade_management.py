#!/usr/bin/env python3
"""Analyze whether USD_JPY post-entry events separate manageable trade outcomes.

Read-only. Loads the post-entry dataset and asks, for each LIVE-MANAGEABLE event at each
horizon, restricted to trades still OPEN at that horizon (the only ones a management
decision could act on): does the event flag eventual hard-stop losers vs time-exit
survivors / winners, and how much winner damage would early-exiting cause?

Event direction:
  * EXIT-type (present → expect a worse outcome): early_reclaim_failure, no_continuation,
    early_adverse_expansion, trap_or_failed_breakout, range_compression_after_entry.
    Useful if present → higher hard-stop rate / lower win rate, stably, with limited
    winner damage.
  * HOLD-type (present → expect a better outcome): early_retest_hold,
    early_favorable_displacement, reached_plus_025, reached_plus_05.

Anti-overfit: no threshold selected as a parameter; horizons are the fixed 2/4/8/16.
"Stable" = same-signed effect on train and validation with adequate sample. Hindsight-
only events are reported separately and flagged UNUSABLE for live management.

Diagnostic only — approves nothing, changes no verdict, tunes nothing, creates no C024,
claims no edge. Outputs:
  research/usdjpy_trade_management_diagnostic/post_entry_analysis_summary.json
  docs/research/USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_RESULT.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.research.post_entry_trade_management import DEFAULT_HORIZONS, liveness_of

DATA_DIR = REPO_ROOT / "research" / "usdjpy_trade_management_diagnostic"
PARQUET = DATA_DIR / "usdjpy_post_entry_features.parquet"
SUMMARY_JSON = DATA_DIR / "post_entry_analysis_summary.json"
RESULT_MD = REPO_ROOT / "docs" / "research" / "USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_RESULT.md"

HORIZONS = DEFAULT_HORIZONS
MIN_CLASS_N = 25  # trust floor for a present/absent subgroup on one split (USD_JPY is small)

EXIT_TYPE = (
    "early_reclaim_failure", "no_continuation", "early_adverse_expansion",
    "range_compression_after_entry",
)
HOLD_TYPE = (
    "early_retest_hold", "early_favorable_displacement",
    "reached_plus_025", "reached_plus_05",
)


def _rate(g: pd.Series) -> float | None:
    return round(float(g.mean()), 4) if len(g) else None


def _lift(p: dict, a: dict, key: str) -> float | None:
    if p[key] is None or a[key] is None:
        return None
    return round(p[key] - a[key], 4)


def _contrast(df: pd.DataFrame, event_col: str, horizon: int | None) -> dict:
    """Present-vs-absent contrast on trades still open at the horizon, per split."""
    out: dict = {}
    open_col = f"open_at_h{horizon}" if horizon is not None else None
    for split in ("train", "validation"):
        sub = df[(df["split"] == split) & df[event_col].notna()].copy()
        if open_col is not None and open_col in sub.columns:
            sub = sub[sub[open_col].astype(bool)]
        present = sub[sub[event_col].astype(bool)]
        absent = sub[~sub[event_col].astype(bool)]

        def block(g: pd.DataFrame) -> dict:
            return {
                "n": len(g),
                "hard_stop_rate": _rate(g["hard_stop_loss"]) if len(g) else None,
                "win_rate": _rate(g["profitable_trade"]) if len(g) else None,
                "straight_to_stop_rate": (
                    _rate(g["straight_to_stop"].dropna().astype(bool)) if g["straight_to_stop"].notna().any() else None
                ),
                "mean_result_r": round(float(g["result_r"].mean()), 4) if g["result_r"].notna().any() else None,
            }

        p, a = block(present), block(absent)
        trustworthy = p["n"] >= MIN_CLASS_N and a["n"] >= MIN_CLASS_N
        out[split] = {
            "n_present": p["n"], "n_absent": a["n"], "trustworthy": trustworthy,
            "present": p, "absent": a,
            "hard_stop_lift": _lift(p, a, "hard_stop_rate"),
            "win_rate_lift": _lift(p, a, "win_rate"),
            "straight_to_stop_lift": _lift(p, a, "straight_to_stop_rate"),
            "result_r_gap": _lift(p, a, "mean_result_r"),
        }
    return out


def _stability(contrast: dict, key: str) -> bool:
    vals = [
        contrast[s][key] for s in ("train", "validation")
        if contrast[s][key] is not None and contrast[s]["trustworthy"]
    ]
    return bool(len(vals) == 2 and vals[0] * vals[1] > 0)


def _evaluate(df: pd.DataFrame, base: str, direction: str) -> dict:
    horizons = [None] if base == "trap_or_failed_breakout" else list(HORIZONS)
    per_h: dict = {}
    for h in horizons:
        col = base if h is None else f"{base}_h{h}"
        if col not in df.columns:
            continue
        contrast = _contrast(df, col, h if base != "trap_or_failed_breakout" else 2)
        # For EXIT-type, "useful" = present → MORE hard stops (positive hard_stop_lift)
        # and LOWER win rate; winner damage = win_rate of present group.
        hs_stable = _stability(contrast, "hard_stop_lift")
        wr_stable = _stability(contrast, "win_rate_lift")
        winner_damage = {
            s: contrast[s]["present"]["win_rate"] for s in ("train", "validation")
        }
        per_h[str(h)] = {
            "column": col,
            "contrast": contrast,
            "hard_stop_lift_stable": hs_stable,
            "win_rate_lift_stable": wr_stable,
            "winner_damage_present_win_rate": winner_damage,
        }
    return {"direction": direction, "liveness": liveness_of(
        f"{base}_h2" if base != "trap_or_failed_breakout" else base), "by_horizon": per_h}


def _useful_exit_signal(ev: dict) -> bool:
    """A stable EXIT-type signal: present → higher hard-stop AND lower win-rate, both
    same-signed across splits, on a trusted subgroup."""
    for blk in ev["by_horizon"].values():
        if not (blk["hard_stop_lift_stable"] and blk["win_rate_lift_stable"]):
            continue
        c = blk["contrast"]
        if all(c[s]["hard_stop_lift"] is not None and c[s]["hard_stop_lift"] > 0
               and c[s]["win_rate_lift"] is not None and c[s]["win_rate_lift"] < 0
               for s in ("train", "validation")):
            return True
    return False


def analyze() -> dict:
    if not PARQUET.exists():
        payload = {"strategy_evidence": False, "not_approved": True, "diagnostic_only": True,
                   "instrument": "USD_JPY", "status": "BLOCKED_LOCAL_DATA",
                   "reason": f"dataset not found: {PARQUET.relative_to(REPO_ROOT)}"}
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    df = pd.read_parquet(PARQUET)
    df = df[df["profitable_trade"].notna()].copy()

    exit_eval = {b: _evaluate(df, b, "exit") for b in EXIT_TYPE}
    exit_eval["trap_or_failed_breakout"] = _evaluate(df, "trap_or_failed_breakout", "exit")
    hold_eval = {b: _evaluate(df, b, "hold") for b in HOLD_TYPE}

    # Hindsight-only references (strong but UNUSABLE): mae_by full path proxied by mae_r.
    hindsight_note = {
        "time_to_first_minus_05": "hindsight_only — full path; not knowable live at decision time",
        "mae_r": "hindsight_only — realized adverse excursion at exit",
    }

    useful_exit = [b for b, ev in exit_eval.items() if _useful_exit_signal(ev)]
    # HOLD usefulness: present → higher win-rate, stable.
    useful_hold = [
        b for b, ev in hold_eval.items()
        if any(blk["win_rate_lift_stable"]
               and all(blk["contrast"][s]["win_rate_lift"] is not None
                       and blk["contrast"][s]["win_rate_lift"] > 0 for s in ("train", "validation"))
               for blk in ev["by_horizon"].values())
    ]

    summary = {
        "strategy_evidence": False, "not_approved": True, "diagnostic_only": True,
        "instrument": "USD_JPY", "status": "OK",
        "framing": "post-entry TRADE-MANAGEMENT separation; restricted to trades still "
                   "open at each horizon; not entry alpha; counterfactual gains (Phase 4) "
                   "would be optimistic.",
        "min_class_n": MIN_CLASS_N,
        "n_trades": len(df),
        "n_by_split": {s: int((df["split"] == s).sum()) for s in ("train", "validation")},
        "realized_mean_r_by_split": {
            s: round(float(df.loc[df["split"] == s, "result_r"].mean()), 6)
            for s in ("train", "validation")
        },
        "hard_stop_rate_overall": round(float(df["hard_stop_loss"].mean()), 4),
        "exit_type_events": exit_eval,
        "hold_type_events": hold_eval,
        "useful_stable_exit_signals": useful_exit,
        "useful_stable_hold_signals": useful_hold,
        "any_useful_live_manageable_signal": bool(useful_exit or useful_hold),
        "hindsight_only_note": hindsight_note,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_md(summary)
    return summary


def _fmt(x: object) -> str:
    return "—" if x is None else str(x)


def _event_table(ev: dict) -> list[str]:
    lines = ["| horizon | n present (tr/va) | hard-stop lift (tr/va) | win-rate lift (tr/va) | winner-damage win-rate (tr/va) | stable? |",
             "|---|---|---|---|---|---|"]
    for h, blk in ev["by_horizon"].items():
        c = blk["contrast"]
        npr = f"{c['train']['n_present']}/{c['validation']['n_present']}"
        hsl = f"{_fmt(c['train']['hard_stop_lift'])}/{_fmt(c['validation']['hard_stop_lift'])}"
        wrl = f"{_fmt(c['train']['win_rate_lift'])}/{_fmt(c['validation']['win_rate_lift'])}"
        wd = blk["winner_damage_present_win_rate"]
        wds = f"{_fmt(wd['train'])}/{_fmt(wd['validation'])}"
        stable = "yes" if (blk["hard_stop_lift_stable"] and blk["win_rate_lift_stable"]) else "no"
        label = "all" if h == "None" else h
        lines.append(f"| {label} | {npr} | {hsl} | {wrl} | {wds} | {stable} |")
    return lines


def _write_md(s: dict) -> None:
    lines: list[str] = []
    lines.append("# USD_JPY Post-Entry Trade-Management Diagnostic — Result\n")
    lines.append("**Status:** read-only diagnostic. No verdict change, no approval, no tuning, "
             "no C024, no campaign, no edge claim. USD_JPY-only. Post-entry events are "
             "TRADE-MANAGEMENT diagnostics, never entry alpha; nothing here is a tradable rule.\n")
    lines.append("## Setup\n")
    lines.append(f"- USD_JPY trades: {s['n_trades']} (train {s['n_by_split']['train']}, "
             f"validation {s['n_by_split']['validation']}); realized mean R "
             f"{s['realized_mean_r_by_split']}; overall hard-stop rate {s['hard_stop_rate_overall']}.")
    lines.append("- Each event is evaluated **only on trades still open at the horizon** "
             "(the only trades a management decision could act on), present vs absent, per split.")
    lines.append(f"- 'Stable' = same-signed lift on train & validation with ≥ {s['min_class_n']} "
             "per subgroup. Horizons are the fixed 2/4/8/16 M15 bars; no threshold is tuned.\n")

    lines.append("## Headline\n")
    if not s["any_useful_live_manageable_signal"]:
        lines.append("**No live-manageable post-entry event gives a stable, trustworthy "
                 "exit- or hold-management edge.** No EXIT-type event stably flags eventual "
                 "hard-stops while lowering win-rate; no HOLD-type event stably raises win-rate "
                 "— at least not without flagging so many winners that early-exiting would do "
                 "as much damage as good. See the per-event tables.\n")
    else:
        lines.append(f"Candidate stable live-manageable signals — EXIT-type: "
                 f"{s['useful_stable_exit_signals'] or 'none'}; HOLD-type: "
                 f"{s['useful_stable_hold_signals'] or 'none'}. Treat as hypothesis-generating "
                 "only; winner damage and optimistic-counterfactual caveats apply (Phase 4).\n")

    lines.append("## EXIT-type events (present → expect worse outcome)\n")
    for b, ev in s["exit_type_events"].items():
        lines.append(f"### {b} ({ev['liveness']})\n")
        lines += _event_table(ev)
        lines.append("")
    lines.append("## HOLD-type events (present → expect better outcome)\n")
    for b, ev in s["hold_type_events"].items():
        lines.append(f"### {b} ({ev['liveness']})\n")
        lines += _event_table(ev)
        lines.append("")

    lines.append("## Hindsight-only references (UNUSABLE for live management)\n")
    lines.append("Full-path fields (e.g. realized MAE at exit, full time-to-threshold) often "
             "separate outcomes strongly, but they are only knowable at/after exit and "
             "**cannot** drive a live management decision. They are excluded from the "
             "usefulness verdict by construction.\n")

    lines.append("## Reading (honest)\n")
    lines.append("- **Restricted to still-open trades.** A management signal only matters for "
             "trades not already closed at the horizon; the tables reflect that subset.")
    lines.append("- **Winner damage.** For EXIT-type signals, the 'winner-damage win-rate' is the "
             "share of flagged (would-exit) trades that were actually winners — early-exiting "
             "them forfeits those wins. A high value means the signal cuts winners.")
    lines.append("- **Optimistic counterfactuals.** Any apparent gain is upper-bounded; the Phase 4 "
             "counterfactual (if run) assumes perfect action at the bar and ignores execution "
             "cost. Nothing here is tradable, and no threshold is a parameter.\n")
    RESULT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    s = analyze()
    if s.get("status") == "BLOCKED_LOCAL_DATA":
        print(f"[BLOCKED_LOCAL_DATA] {s['reason']}")
        return 0
    print(f"[OK] {s['n_trades']} USD_JPY trades · useful_exit={s['useful_stable_exit_signals']} · "
          f"useful_hold={s['useful_stable_hold_signals']} · "
          f"any_useful={s['any_useful_live_manageable_signal']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

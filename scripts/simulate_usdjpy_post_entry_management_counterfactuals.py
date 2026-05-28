#!/usr/bin/env python3
"""Diagnostic counterfactual early-exit simulation for USD_JPY post-entry management.

Read-only and DIAGNOSTIC ONLY. For a SMALL, predeclared set of exit rules (fixed event
+ fixed horizon — never mined from outcomes), it asks: if we had exited every flagged
trade still open at the horizon, at the next-bar-open after the horizon, how would the
realized USD_JPY expectancy have changed — and how much winner damage would that cause?

These counterfactuals are OPTIMISTIC: they assume the signal is acted on perfectly, mark
the exit at mid open (no spread/slippage on the early exit), and do not net out the
documented entry-edge problem. They are NOT tradable results and adopt no rule. No
verdict changes; no historical metric is rewritten; no C024; no approval.

Usage (local, with .env sourced for the research DB):
  set -a && source .env && set +a
  python scripts/simulate_usdjpy_post_entry_management_counterfactuals.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.research.microstructure_confirmations import MicrostructureParams, build_context
from forex_bot.research.post_entry_trade_management import (
    PostEntryParams,
    compute_post_entry_events,
)

INSTRUMENT = "USD_JPY"
CAMPAIGN_DIR = REPO_ROOT / "backtests" / "CAMPAIGN_022_h4_h1_pullback_resolution"
OUT_DIR = REPO_ROOT / "research" / "usdjpy_trade_management_diagnostic"
OUT_JSON = OUT_DIR / "post_entry_counterfactuals.json"
OUT_MD = REPO_ROOT / "docs" / "research" / "USDJPY_POST_ENTRY_MANAGEMENT_COUNTERFACTUALS.md"

SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2021-06-01", "2023-12-31"),
    "validation": ("2024-01-01", "2025-06-30"),
}
M15_PARAMS = MicrostructureParams()
PE_PARAMS = PostEntryParams()

# Predeclared exit rules (event_base, horizon). FIXED — not selected from performance.
EXIT_RULES = [
    ("early_reclaim_failure", 2),
    ("early_reclaim_failure", 4),
    ("early_adverse_expansion", 2),
    ("no_continuation", 4),
    ("trap_or_failed_breakout", 2),
]


def _parse(s: str) -> datetime:
    return datetime.fromisoformat(s).replace(tzinfo=UTC)


def _classify_exit(reason: object) -> str:
    r = str(reason).strip().lower()
    if r in {"stop", "hard_stop", "protective_stop", "stop_loss"}:
        return "hard_stop"
    if r in {"time", "time_stop", "max_hold", "timeout"}:
        return "time_stop"
    return r


def _load_usdjpy_trades() -> pd.DataFrame:
    frames = []
    for split in SPLITS:
        path = CAMPAIGN_DIR / split / "base" / f"c022_{INSTRUMENT}_{split}_base_trades.csv"
        if path.exists():
            df = pd.read_csv(path)
            df = df[df["instrument"] == INSTRUMENT].copy()
            df["split"] = split
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _try_store():
    try:
        from forex_bot.data.postgres_candle_store import PostgresCandleStore
        from forex_bot.data.research_db import get_research_database_config
        from forex_bot.research.campaign_022_loader import load_c022_frames
    except Exception as e:  # pragma: no cover
        return None, None, f"import failed: {type(e).__name__}: {e}"
    try:
        store = PostgresCandleStore(get_research_database_config(require=True))
        return store, load_c022_frames, None
    except Exception as e:
        return None, None, f"research DB unavailable: {type(e).__name__}: {e}"


def _build_rows(trades, load_frames, store) -> list[dict]:
    ctx_by_split, idx_by_split, m15_by_split = {}, {}, {}
    for split, (frm, to) in SPLITS.items():
        frames = load_frames(store, INSTRUMENT, from_dt=_parse(frm), to_dt=_parse(to))
        m15df = frames.m15.completed_only().df
        ctx_by_split[split] = build_context(
            m15df["open"].to_numpy(), m15df["high"].to_numpy(),
            m15df["low"].to_numpy(), m15df["close"].to_numpy(), M15_PARAMS,
        )
        idx_by_split[split] = pd.to_datetime(m15df.index, utc=True)
        m15_by_split[split] = m15df

    rows = []
    for _, t in trades.iterrows():
        split = str(t["split"])
        ctx, idx, m15df = ctx_by_split[split], idx_by_split[split], m15_by_split[split]
        side = str(t["side"])
        sign = 1 if side.strip().lower() in {"long", "buy"} else -1
        entry_time = pd.Timestamp(t["entry_time"]).tz_convert("UTC")
        exit_time = pd.Timestamp(t["exit_time"]).tz_convert("UTC")
        entry_price = float(t["entry_price"])
        stop_price = float(t["stop_price"])
        risk = abs(entry_price - stop_price)
        result_r = float(t["r_multiple"]) if pd.notna(t.get("r_multiple")) else None

        post_mask = np.asarray((idx > entry_time) & (idx <= exit_time))
        pos = np.flatnonzero(post_mask)
        post_open = m15df["open"].to_numpy()[pos]
        events = compute_post_entry_events(
            side=side, entry_price=entry_price, stop_price=stop_price,
            post_high=ctx.high[pos], post_low=ctx.low[pos], post_close=ctx.close[pos],
            post_ema=ctx.ema[pos], post_atr=ctx.atr[pos], params=PE_PARAMS,
        )
        # next-bar-open R after each horizon (mark; None if not still open / zero risk)
        exit_r_at = {}
        n = len(pos)
        for h in PE_PARAMS.horizons:
            if risk > 0 and n > h:  # still open after horizon h; next bar = post index h (0-based)
                exit_r_at[h] = float(sign * (post_open[h] - entry_price) / risk)
            else:
                exit_r_at[h] = None
        rows.append({
            "split": split, "result_r": result_r,
            "exit_class": _classify_exit(t.get("exit_reason")),
            "events": events, "exit_r_at": exit_r_at,
        })
    return rows


def _simulate(rows: list[dict], event_base: str, horizon: int) -> dict:
    flag_col = event_base if event_base == "trap_or_failed_breakout" else f"{event_base}_h{horizon}"
    open_col = f"open_at_h{horizon}"
    per_split = {}
    for split in ("train", "validation"):
        srows = [r for r in rows if r["split"] == split and r["result_r"] is not None]
        realized = np.array([r["result_r"] for r in srows], dtype=float)
        new = realized.copy()
        affected = 0
        winners_cut = 0
        winner_r_lost = 0.0
        stops_avoided = 0
        stop_r_saved = 0.0
        for i, r in enumerate(srows):
            ev = r["events"]
            flagged = bool(ev.get(flag_col)) if ev.get(flag_col) is not None else False
            still_open = bool(ev.get(open_col)) if ev.get(open_col) is not None else False
            exit_r = r["exit_r_at"].get(horizon)
            if flagged and still_open and exit_r is not None:
                affected += 1
                new[i] = exit_r
                if r["result_r"] > 0:  # would-be winner cut early
                    winners_cut += 1
                    winner_r_lost += (r["result_r"] - exit_r)
                if r["exit_class"] == "hard_stop":  # would-be hard stop exited earlier
                    stops_avoided += 1
                    stop_r_saved += (exit_r - r["result_r"])
        per_split[split] = {
            "n": len(srows),
            "affected": affected,
            "realized_mean_r": round(float(realized.mean()), 5) if len(realized) else None,
            "counterfactual_mean_r": round(float(new.mean()), 5) if len(new) else None,
            "expectancy_delta_r": round(float(new.mean() - realized.mean()), 5) if len(new) else None,
            "winners_cut": winners_cut,
            "winner_r_lost_total": round(winner_r_lost, 4),
            "stops_exited_early": stops_avoided,
            "stop_r_saved_total": round(stop_r_saved, 4),
        }
    deltas = [per_split[s]["expectancy_delta_r"] for s in ("train", "validation")
              if per_split[s]["expectancy_delta_r"] is not None]
    return {
        "rule": f"exit if {flag_col} and still open at h{horizon} (next-bar-open mark)",
        "event_base": event_base, "horizon": horizon,
        "per_split": per_split,
        "delta_positive_both_splits": bool(len(deltas) == 2 and deltas[0] > 0 and deltas[1] > 0),
        "delta_stable_sign": bool(len(deltas) == 2 and deltas[0] * deltas[1] > 0),
    }


def main() -> int:
    trades = _load_usdjpy_trades()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if trades.empty:
        OUT_JSON.write_text(json.dumps({"status": "NO_TRADES"}, indent=2), encoding="utf-8")
        print("[NO_TRADES]")
        return 0
    store, load_frames, err = _try_store()
    if store is None:
        payload = {"status": "BLOCKED_LOCAL_DATA", "reason": err}
        OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"[BLOCKED_LOCAL_DATA] {err}")
        return 0

    rows = _build_rows(trades, load_frames, store)
    sims = [_simulate(rows, base, h) for base, h in EXIT_RULES]
    payload = {
        "strategy_evidence": False, "not_approved": True, "diagnostic_only": True,
        "instrument": INSTRUMENT, "status": "OK",
        "caveat": (
            "OPTIMISTIC counterfactuals: assume perfect action at the bar, mid open marks "
            "(no spread/slippage on the early exit), and do not net out the entry-edge "
            "problem. NOT tradable; no rule adopted; no verdict changed."
        ),
        "exit_timing": "next-bar-open after the horizon",
        "rules": sims,
        "any_rule_improves_both_splits": bool(any(s["delta_positive_both_splits"] for s in sims)),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_md(payload)
    print(f"[OK] {len(sims)} predeclared exit rules simulated · "
          f"any_improves_both_splits={payload['any_rule_improves_both_splits']}")
    return 0


def _fmt(x: object) -> str:
    return "—" if x is None else str(x)


def _write_md(p: dict) -> None:
    lines: list[str] = []
    lines.append("# USD_JPY Post-Entry Management — Diagnostic Counterfactuals\n")
    lines.append("**Status:** read-only, DIAGNOSTIC ONLY. No verdict change, no approval, no "
                 "tuning, no C024, no rule adopted. USD_JPY-only.\n")
    lines.append("> **Optimistic caveat.** " + p["caveat"] + " Exit timing: "
                 f"{p['exit_timing']}.\n")
    lines.append("## Predeclared exit rules (fixed event + horizon, not mined)\n")
    lines.append("| rule | split | n | affected | realized mean R | counterfactual mean R | Δ expectancy R | stops exited early | winners cut | winner R lost |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for s in p["rules"]:
        for split in ("train", "validation"):
            b = s["per_split"][split]
            lines.append(
                f"| {s['event_base']}@h{s['horizon']} | {split} | {b['n']} | {b['affected']} | "
                f"{_fmt(b['realized_mean_r'])} | {_fmt(b['counterfactual_mean_r'])} | "
                f"{_fmt(b['expectancy_delta_r'])} | {b['stops_exited_early']} | "
                f"{b['winners_cut']} | {_fmt(b['winner_r_lost_total'])} |"
            )
    lines.append("")
    lines.append("## Reading (honest)\n")
    lines.append(f"- Any rule with a **positive** expectancy delta on **both** splits: "
                 f"**{p['any_rule_improves_both_splits']}**.")
    lines.append("- Even a positive delta here is an **upper bound**: it assumes perfect, "
                 "cost-free action at the bar and ignores the entry-edge problem already "
                 "documented. A rule that only helps because it cuts trades to a mid mark is "
                 "not a demonstrated tradable edge.")
    lines.append("- **Winner damage** (winners cut, winner R lost) is the cost of acting on "
                 "an exit signal; weigh it against stops exited early. A rule that saves stop "
                 "losses but forfeits comparable winner R is not net-useful.")
    lines.append("- No rule is adopted; no threshold is a parameter; this is input to the "
                 "readiness decision only.\n")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

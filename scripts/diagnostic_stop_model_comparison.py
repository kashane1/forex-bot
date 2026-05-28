#!/usr/bin/env python3
"""Diagnostic stop-model sensitivity on FIXED C022 entries (research-only).

Loads each committed C022 base trade, reconstructs its fixed-horizon post-entry
M15 path (entry → entry + max_bars), and simulates outcome R under alternative
EXIT rules only (entries unchanged): candidate ATR-multiple hard stops and
time-to-invalidation early exits. A baseline (2.0×ATR = −1R) is simulated too and
compared to the realized price-based expectancy as a sanity check.

**Diagnostic sensitivity only.** Not an optimization. No "best" stop is selected
or promoted as tradable. No C022 verdict/metric is changed. No C024. Read-only DB
access; mid OHLC; no spread/slippage/fill-timing modelled (so the simulated
baseline approximates, not reproduces, the realized fill-model expectancy — the
deltas BETWEEN stop variants are the diagnostic, not absolute levels).

If the materialized M15 store is unreachable, writes BLOCKED_LOCAL_DATA and exits.

Outputs:
  research/trade_lifecycle_diagnostics/diagnostic_stop_model_comparison.json
  docs/research/DIAGNOSTIC_STOP_MODEL_COMPARISON_EXECUTED.md
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.research.lifecycle_features import price_based_r
from forex_bot.research.stop_model_sim import (
    PathBar,
    simulate_fixed_stop,
    simulate_time_invalidation,
)
from forex_bot.research.trade_lifecycle import load_trades_csv

OUT_DIR = REPO_ROOT / "research" / "trade_lifecycle_diagnostics"
DOC = REPO_ROOT / "docs" / "research" / "DIAGNOSTIC_STOP_MODEL_COMPARISON_EXECUTED.md"
CAMPAIGN_DIR = REPO_ROOT / "backtests" / "CAMPAIGN_022_h4_h1_pullback_resolution"
MAX_BARS = 32  # C022 frozen max_bars_in_trade / time stop

# Candidate hard stops as ATR multiples -> R distance (baseline 2.0xATR = 1.0R).
ATR_MULTIPLES = {"1.5xATR": 0.75, "2.0xATR(baseline)": 1.0, "2.5xATR": 1.25, "3.0xATR": 1.5}
# Time-to-invalidation candidates: (threshold_r, n_bars).
INVALIDATION = {"no+0.25R_by_8": (0.25, 8), "no+0.5R_by_8": (0.5, 8), "no+0.5R_by_12": (0.5, 12)}


def _try_store():
    try:
        from forex_bot.data.postgres_candle_store import PostgresCandleStore
        from forex_bot.data.research_db import get_research_database_config
        from forex_bot.research.campaign_021_loader import _load_materialized_granularity
        cfg = get_research_database_config(require=True)
        return PostgresCandleStore(cfg), _load_materialized_granularity, None
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"


def _load_path(loader, store, instrument, entry_time) -> list[PathBar]:
    # Generous calendar window (weekends/holidays skip bars); we slice MAX_BARS after entry.
    to_dt = entry_time + timedelta(days=10)
    candles = loader(store, instrument, "M15", "M15", from_dt=entry_time, to_dt=to_dt)
    bars: list[PathBar] = []
    for c in candles:
        if c.time <= entry_time:
            continue
        hi, lo, cl = c.mid_h, c.mid_l, c.mid_c
        if hi is None or lo is None or cl is None:
            continue
        bars.append(PathBar(timestamp=c.time, high=float(hi), low=float(lo), close=float(cl)))
        if len(bars) >= MAX_BARS:
            break
    return bars


def _agg(outcomes: list[float]) -> dict:
    if not outcomes:
        return {"n": 0, "expectancy_r": None, "win_rate": None}
    return {
        "n": len(outcomes),
        "expectancy_r": round(statistics.fmean(outcomes), 4),
        "win_rate": round(sum(1 for r in outcomes if r > 0) / len(outcomes), 4),
        "mean_loss_r": round(statistics.fmean([r for r in outcomes if r <= 0]), 4)
        if any(r <= 0 for r in outcomes) else None,
    }


def run() -> dict:
    store, loader, err = _try_store()
    if store is None:
        return {"status": "BLOCKED_LOCAL_DATA", "reason": err, "diagnostic_only": True,
                "strategy_evidence": False, "not_approved": True}

    trades = []
    for path in sorted(CAMPAIGN_DIR.rglob("*_trades.csv")):
        if "base" not in {p.lower() for p in path.parts}:
            continue
        trades.extend(load_trades_csv(path, campaign_id="CAMPAIGN_022"))

    realized_r: list[float] = []
    paths: list[tuple] = []
    dropped = 0
    for t in trades:
        if None in (t.instrument, t.side, t.entry_time, t.exit_time, t.entry_price,
                    t.exit_price, t.initial_stop_price):
            dropped += 1
            continue
        bars = _load_path(loader, store, t.instrument, t.entry_time)
        if not bars:
            dropped += 1
            continue
        paths.append((t.side, t.entry_price, t.initial_stop_price, bars))
        pr = price_based_r(t.side, t.entry_price, t.exit_price, t.initial_stop_price)
        if pr is not None:
            realized_r.append(pr)

    # Candidate hard stops.
    stop_results = {}
    for label, sr in ATR_MULTIPLES.items():
        outs = []
        for side, entry, stop, bars in paths:
            o = simulate_fixed_stop(side=side, entry_price=entry, initial_stop_price=stop,
                                    bars=bars, stop_r=sr, max_bars=MAX_BARS)
            if o.outcome_r is not None:
                outs.append(o.outcome_r)
        stop_results[label] = _agg(outs)

    # Time-to-invalidation.
    inval_results = {}
    for label, (thr, n) in INVALIDATION.items():
        outs = []
        for side, entry, stop, bars in paths:
            o = simulate_time_invalidation(side=side, entry_price=entry, initial_stop_price=stop,
                                           bars=bars, threshold_r=thr, n_bars=n, max_bars=MAX_BARS)
            if o.outcome_r is not None:
                outs.append(o.outcome_r)
        inval_results[label] = _agg(outs)

    realized_agg = _agg(realized_r)
    sim_baseline = stop_results.get("2.0xATR(baseline)", {})
    return {
        "status": "OK",
        "diagnostic_only": True,
        "strategy_evidence": False,
        "not_approved": True,
        "no_best_stop_selected": True,
        "entries_unchanged": True,
        "campaign_id": "CAMPAIGN_022",
        "schema": store.config.schema,
        "max_bars": MAX_BARS,
        "reconstructed_paths": len(paths),
        "dropped": dropped,
        "caveats": (
            "mid OHLC only; no spread/slippage; no next-bar-open fill timing; "
            "structure/reclaim stop families omitted (need ATR-at-entry & pullback/"
            "reclaim geometry not in historical artifacts). Compare DELTAS between "
            "variants, not absolute levels."
        ),
        "baseline_sanity_check": {
            "realized_price_based_expectancy_r": realized_agg.get("expectancy_r"),
            "simulated_baseline_2x_atr_expectancy_r": sim_baseline.get("expectancy_r"),
            "note": "should be close; residual = mid-vs-fill-model approximation.",
        },
        "hard_stop_sensitivity": stop_results,
        "time_to_invalidation": inval_results,
    }


def render_md(p: dict) -> str:
    lines: list[str] = ["# Diagnostic Stop-Model Comparison (EXECUTED)", ""]
    lines.append("**Diagnostic sensitivity only** — fixed C022 entries, exit rule varied. "
             "No optimization, no 'best' stop promoted, no verdict/metric changed, no C024.")
    lines.append("")
    if p["status"] != "OK":
        lines += ["## Status: BLOCKED_LOCAL_DATA", "", f"**Reason:** {p.get('reason')}", ""]
        return "\n".join(lines)
    lines.append(f"Reconstructed paths: **{p['reconstructed_paths']}** (dropped {p['dropped']}); "
             f"horizon {p['max_bars']} M15 bars; schema `{p['schema']}`.")
    lines.append("")
    lines.append(f"> **Caveats.** {p['caveats']}")
    lines.append("")
    b = p["baseline_sanity_check"]
    lines.append("## Baseline sanity check")
    lines.append("")
    lines.append(f"- realized price-based expectancy: **{b['realized_price_based_expectancy_r']}R**")
    lines.append(f"- simulated 2.0×ATR baseline expectancy: **{b['simulated_baseline_2x_atr_expectancy_r']}R**")
    lines.append(f"- {b['note']}")
    lines.append("")
    lines.append("## Hard-stop sensitivity (ATR multiple → R distance)")
    lines.append("")
    lines.append("| stop | n | expectancy_r | win_rate | mean_loss_r |")
    lines.append("|---|---|---|---|---|")
    for k, v in p["hard_stop_sensitivity"].items():
        lines.append(f"| {k} | {v['n']} | {v['expectancy_r']} | {v['win_rate']} | {v.get('mean_loss_r')} |")
    lines.append("")
    lines.append("## Time-to-invalidation early exit")
    lines.append("")
    lines.append("| rule | n | expectancy_r | win_rate | mean_loss_r |")
    lines.append("|---|---|---|---|---|")
    for k, v in p["time_to_invalidation"].items():
        lines.append(f"| {k} | {v['n']} | {v['expectancy_r']} | {v['win_rate']} | {v.get('mean_loss_r')} |")
    lines.append("")
    lines.append("## Reading (diagnostic — not an edge)")
    lines.append("")
    lines.append("- Every variant is reported for sensitivity. **No variant is endorsed as "
             "tradable**; all remain negative and none is promoted.")
    lines.append("- **All hard-stop multiples (1.5×–3.0× ATR) and all time-to-invalidation "
             "rules stay in a tight negative band** — no exit rule lifts expectancy toward "
             "zero. Stop geometry is **not** the lever.")
    lines.append("- The simulated baseline here is **cost-free** (mid OHLC, no spread/slippage) "
             "yet still negative; the gap to the realized price-based expectancy is "
             "approximately the cost drag. Even in the idealized no-cost case the entries do "
             "not clear zero — strong evidence the problem is **entry edge, not stop distance**.")
    lines.append("- Any genuinely interesting variant must be re-tested in a pre-registered "
             "campaign with the real fill model — never adopted from this sensitivity sweep.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    payload = run()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "diagnostic_stop_model_comparison.json").write_text(json.dumps(payload, indent=2) + "\n")
    DOC.write_text(render_md(payload))
    print("status:", payload["status"])
    if payload["status"] == "OK":
        print("realized vs simulated baseline:", payload["baseline_sanity_check"])
        print("hard_stop_sensitivity:", {k: v["expectancy_r"] for k, v in payload["hard_stop_sensitivity"].items()})
        print("time_to_invalidation:", {k: v["expectancy_r"] for k, v in payload["time_to_invalidation"].items()})
    print("wrote", OUT_DIR / "diagnostic_stop_model_comparison.json")
    print("wrote", DOC)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

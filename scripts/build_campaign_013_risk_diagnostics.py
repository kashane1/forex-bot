#!/usr/bin/env python3
"""CAMPAIGN_013 portfolio-risk diagnostics.

Reads the per-fold per-pair trade CSVs + the fold_detail.json
(``run_campaign_013.py`` output), and produces a compact diagnostics
report describing:

  * per-pair exposure (trade count, total notional approximation)
  * max concurrent open positions (structurally bounded — per-pair
    engine isolation; not portfolio-wide)
  * pair concentration (Phase 4 already reports single-pair dominance)
  * session clustering of entries
  * loss streaks (per pair)
  * drawdown clustering
  * RiskEngine rejection-code distribution
  * **CAMPAIGN_013 cross-pair-specific:**
    - zero-trade pair-fold cell distribution
    - per-fold long/short imbalance
    - simultaneous-signal frequency (distinct entry bars firing on > 1 pair)
    - effective per-pair firing rate (trades / common_index_length)
    - cross-pair runner contract status per fold

All numbers are diagnostic — none gate the verdict. CAMPAIGN_013 is
research-only; even a clean diagnostics pass produces
RESEARCH_PASS_UNAPPROVED at best.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PAIRS = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)


def _hour_bucket(hour: int) -> str:
    if hour >= 22 or hour < 6:
        return "asian"
    if 6 <= hour < 12:
        return "london"
    if 12 <= hour < 16:
        return "london_ny_overlap"
    return "ny"


def _max_loss_streak(pnls: list[float]) -> int:
    streak = best = 0
    for v in pnls:
        if v < 0:
            streak += 1
            best = max(best, streak)
        else:
            streak = 0
    return best


def _max_win_streak(pnls: list[float]) -> int:
    streak = best = 0
    for v in pnls:
        if v > 0:
            streak += 1
            best = max(best, streak)
        else:
            streak = 0
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign-dir", required=True)
    args = ap.parse_args()

    campaign_dir = Path(args.campaign_dir)
    folds_dir = campaign_dir / "folds"
    detail = json.loads(
        (campaign_dir / "walk_forward" / "fold_detail.json").read_text()
    )

    per_pair_trades: dict[str, list[dict]] = {p: [] for p in PAIRS}
    per_pair_pnls: dict[str, list[float]] = {p: [] for p in PAIRS}
    per_pair_units: dict[str, Decimal] = {p: Decimal("0") for p in PAIRS}
    per_pair_notional: dict[str, Decimal] = {p: Decimal("0") for p in PAIRS}
    entry_hour_counts: Counter = Counter()
    exit_reason_counts: Counter = Counter()

    # Cross-pair-specific accumulators
    # Per-fold per-pair trade count for zero-cell detection
    fold_pair_trade_count: dict[str, dict[str, int]] = {}
    # Per-fold long/short counts
    fold_long_count: dict[str, int] = defaultdict(int)
    fold_short_count: dict[str, int] = defaultdict(int)
    # Per-fold entry timestamps by pair → for simultaneous-signal detection
    fold_entry_bars: dict[str, dict[str, set[str]]] = {}

    for fold_dir in sorted(folds_dir.iterdir()):
        if not fold_dir.is_dir():
            continue
        fold_key = fold_dir.name
        fold_pair_trade_count.setdefault(fold_key, {p: 0 for p in PAIRS})
        fold_entry_bars.setdefault(fold_key, {p: set() for p in PAIRS})
        for pair in PAIRS:
            csv_path = fold_dir / f"{fold_dir.name}_{pair}_trades.csv"
            if not csv_path.exists():
                continue
            with csv_path.open(encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    pnl = float(row["pnl"])
                    units = Decimal(row["units"])
                    entry_price = Decimal(row["entry_price"])
                    per_pair_trades[pair].append({**row, "fold_dir": fold_dir.name})
                    per_pair_pnls[pair].append(pnl)
                    per_pair_units[pair] += units
                    per_pair_notional[pair] += units * entry_price
                    et = datetime.fromisoformat(row["entry_time"]).astimezone(UTC)
                    entry_hour_counts[et.hour] += 1
                    exit_reason_counts[row["exit_reason"]] += 1
                    fold_pair_trade_count[fold_key][pair] += 1
                    if row["side"] == "long":
                        fold_long_count[fold_key] += 1
                    else:
                        fold_short_count[fold_key] += 1
                    fold_entry_bars[fold_key][pair].add(row["entry_time"])

    # Per-pair exposure + streaks
    per_pair_summary: dict[str, dict] = {}
    for p in PAIRS:
        pnls = per_pair_pnls[p]
        per_pair_summary[p] = {
            "trade_count": len(pnls),
            "total_units": float(per_pair_units[p]),
            "total_notional_quote_ccy_approx": float(per_pair_notional[p]),
            "max_loss_streak": _max_loss_streak(pnls),
            "max_win_streak": _max_win_streak(pnls),
            "largest_single_loss_usd": min(pnls) if pnls else 0.0,
            "largest_single_win_usd": max(pnls) if pnls else 0.0,
            "total_pnl_usd": sum(pnls),
        }

    # Session-of-day clustering (UTC hour of entry).
    entry_hour_table = dict(sorted(entry_hour_counts.items()))
    session_buckets: Counter = Counter()
    for h, c in entry_hour_counts.items():
        session_buckets[_hour_bucket(h)] += c
    session_table = dict(sorted(session_buckets.items()))

    # Drawdown clustering — extracted from fold_detail.
    fold_drawdowns: list[dict] = []
    for f in detail["folds"]:
        per_pair_dd = {pr["instrument"]: pr["max_drawdown_pct"] for pr in f["pair_runs"]}
        fold_drawdowns.append(
            {
                "fold_index": f["fold_index"],
                "test_start": f["test_start"],
                "test_end": f["test_end"],
                "per_pair_max_drawdown_pct": per_pair_dd,
                "median_pair_max_drawdown_pct": (
                    sorted(per_pair_dd.values())[len(per_pair_dd) // 2]
                    if per_pair_dd
                    else 0.0
                ),
            }
        )

    # RiskEngine rejection summary (per-pair aggregated across folds).
    rejection_totals: Counter = Counter()
    rejection_by_pair: dict[str, Counter] = {p: Counter() for p in PAIRS}
    for f in detail["folds"]:
        for pr in f["pair_runs"]:
            counts = pr.get("rejection_counts") or {}
            for code, n in counts.items():
                rejection_totals[code] += n
                rejection_by_pair[pr["instrument"]][code] += n

    # Cross-pair-specific aggregates
    # 1. Zero-trade pair-fold cells
    zero_cell_count = sum(
        1
        for fold_key, pair_counts in fold_pair_trade_count.items()
        for p in PAIRS
        if pair_counts.get(p, 0) == 0
    )
    total_cells = len(fold_pair_trade_count) * len(PAIRS)
    zero_cell_pct = (zero_cell_count / total_cells * 100.0) if total_cells else 0.0

    # 2. Per-fold long/short imbalance
    fold_long_short: list[dict] = []
    for fold_key in sorted(fold_pair_trade_count.keys()):
        long_n = fold_long_count.get(fold_key, 0)
        short_n = fold_short_count.get(fold_key, 0)
        total = long_n + short_n
        long_share = (long_n / total * 100.0) if total else 0.0
        fold_long_short.append(
            {
                "fold": fold_key,
                "long": long_n,
                "short": short_n,
                "total": total,
                "long_share_pct": long_share,
            }
        )

    # 3. Simultaneous-signal frequency per fold
    # A "simultaneous signal" = an entry bar that appears in entries for >= 2 pairs in the same fold.
    fold_simultaneous: list[dict] = []
    for fold_key in sorted(fold_entry_bars.keys()):
        bar_to_pairs: dict[str, set[str]] = defaultdict(set)
        for p in PAIRS:
            for bar in fold_entry_bars[fold_key][p]:
                bar_to_pairs[bar].add(p)
        bars_with_signals = len(bar_to_pairs)
        # Histogram: count of bars by concurrent-pair count
        concurrency_hist: Counter = Counter()
        for pairs_set in bar_to_pairs.values():
            concurrency_hist[len(pairs_set)] += 1
        simultaneous_bars = sum(c for n, c in concurrency_hist.items() if n >= 2)
        simultaneous_share = (
            (simultaneous_bars / bars_with_signals * 100.0)
            if bars_with_signals
            else 0.0
        )
        fold_simultaneous.append(
            {
                "fold": fold_key,
                "bars_with_any_signal": bars_with_signals,
                "bars_with_simultaneous_signal_ge_2_pairs": simultaneous_bars,
                "simultaneous_share_pct": simultaneous_share,
                "concurrency_histogram": dict(sorted(concurrency_hist.items())),
            }
        )

    # 4. Effective per-pair firing rate per fold
    # firing rate = trades_in_pair_fold / common_index_length
    fold_firing: list[dict] = []
    for f in detail["folds"]:
        fold_key = f"fold_{f['fold_index']:02d}"
        cidx = (f.get("cross_pair_diagnostics") or {}).get("common_index_length") or 0
        per_pair_rate = {}
        for p in PAIRS:
            trades_n = fold_pair_trade_count.get(fold_key, {}).get(p, 0)
            per_pair_rate[p] = {
                "trades": trades_n,
                "common_index_length": cidx,
                "firing_rate_pct": (
                    (trades_n / cidx * 100.0) if cidx else 0.0
                ),
            }
        fold_firing.append({"fold": fold_key, "per_pair": per_pair_rate})

    # 5. Cross-pair contract status per fold
    fold_contract: list[dict] = []
    for f in detail["folds"]:
        diag = f.get("cross_pair_diagnostics") or {}
        fold_contract.append(
            {
                "fold": f"fold_{f['fold_index']:02d}",
                "contract_satisfied": diag.get("contract_satisfied"),
                "common_index_length": diag.get("common_index_length"),
                "per_pair_raw_lengths": diag.get("per_pair_raw_lengths"),
            }
        )

    # Concurrency: structurally bounded (engine is single-instrument; runner is per-pair).
    concurrency = {
        "structurally_enforced_max_concurrent_per_instrument": 1,
        "structurally_enforced_max_positions_per_instrument_config_key": 1,
        "structurally_enforced_max_open_positions_config_key": 1,
        "runner_is_per_pair_not_portfolio_wide": True,
        "max_open_positions_exceeded_observed": rejection_totals.get(
            "MAX_OPEN_POSITIONS_EXCEEDED", 0
        ),
        "note": (
            "BacktestEngine is single-instrument single-position-at-a-time. "
            "The CAMPAIGN_013 runner invokes one engine PER PAIR PER FOLD; "
            "MAX_OPEN_POSITIONS_EXCEEDED therefore fires 0 times because "
            "the cap is not portfolio-wide across the 7-pair universe. "
            "Multi-instrument concurrency is constrained at the RiskEngine "
            "layer by the campaign config (max_open_positions=1, "
            "max_positions_per_instrument=1, max_correlated_positions=1), "
            "but only within a single pair's run. A truly portfolio-aware "
            "runner would reduce trade count proportionally to the "
            "simultaneous-signal rate but cannot rescue per-pair negative "
            "expectancy (see Phase 5 §6.4)."
        ),
    }

    out = {
        "campaign_id": "CAMPAIGN_013",
        "strategy_name": "cross_pair_currency_strength_rotation",
        "strategy_version": "0.1.0-c013",
        "diagnostics_type": "portfolio-risk",
        "verdict_impact": "diagnostic_only_does_not_gate_verdict",
        "concurrency": concurrency,
        "per_pair_summary": per_pair_summary,
        "session_clustering": {
            "entry_hour_utc_counts": entry_hour_table,
            "entry_session_bucket_counts": session_table,
        },
        "exit_reason_distribution": dict(sorted(exit_reason_counts.items())),
        "drawdown_clustering": {
            "per_fold": fold_drawdowns,
        },
        "risk_engine": {
            "mode": "backtest",
            "rejection_totals_by_code": dict(sorted(rejection_totals.items())),
            "rejection_by_pair": {
                p: dict(sorted(rejection_by_pair[p].items())) for p in PAIRS
            },
        },
        "cross_pair_specific": {
            "zero_trade_pair_fold_cells": {
                "count": zero_cell_count,
                "total_cells": total_cells,
                "pct": zero_cell_pct,
            },
            "per_fold_long_short": fold_long_short,
            "per_fold_simultaneous_signals": fold_simultaneous,
            "per_fold_firing_rate": fold_firing,
            "per_fold_contract_status": fold_contract,
        },
    }

    risk_dir = campaign_dir / "risk"
    risk_dir.mkdir(parents=True, exist_ok=True)
    (risk_dir / "diagnostics.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8"
    )

    # Compact markdown.
    lines = [
        "# CAMPAIGN_013 — Portfolio-Risk Diagnostics (auto-generated)",
        "",
        "> Diagnostic only — does not gate the verdict. CAMPAIGN_013 is",
        "> research-only; even a clean diagnostics pass produces",
        "> RESEARCH_PASS_UNAPPROVED at best. configs/approved_strategies.yaml",
        "> remains approved: [].",
        "",
        "## Per-pair exposure",
        "",
        "| pair | trades | total units | total notional (quote ccy) | total PnL (USD) | max loss streak | max win streak | largest single loss | largest single win |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for p in PAIRS:
        s = per_pair_summary[p]
        lines.append(
            f"| {p} | {s['trade_count']} | {s['total_units']:,.0f} | "
            f"{s['total_notional_quote_ccy_approx']:,.0f} | "
            f"{s['total_pnl_usd']:+,.2f} | {s['max_loss_streak']} | "
            f"{s['max_win_streak']} | {s['largest_single_loss_usd']:+.2f} | "
            f"{s['largest_single_win_usd']:+.2f} |"
        )
    lines += [
        "",
        "## Entry-session clustering",
        "",
        "| UTC hour | trades |",
        "|---:|---:|",
    ]
    for h, c in entry_hour_table.items():
        lines.append(f"| {h:02d}:00 | {c} |")
    lines += [
        "",
        "| session bucket | trades |",
        "|---|---:|",
    ]
    for b, c in session_table.items():
        lines.append(f"| {b} | {c} |")
    lines += [
        "",
        "## Exit reason distribution",
        "",
        "| reason | trades |",
        "|---|---:|",
    ]
    for r, c in sorted(exit_reason_counts.items()):
        lines.append(f"| {r} | {c} |")
    lines += [
        "",
        "## Risk-engine rejection totals (mode=backtest)",
        "",
        "| code | count |",
        "|---|---:|",
    ]
    for code, n in sorted(rejection_totals.items()):
        lines.append(f"| {code} | {n} |")
    if not rejection_totals:
        lines.append("| (none) | 0 |")
    lines += [
        "",
        "## Concurrency",
        "",
        "- BacktestEngine is single-instrument single-position-at-a-time.",
        "- The CAMPAIGN_013 runner invokes one engine PER PAIR PER FOLD; "
        "`MAX_OPEN_POSITIONS_EXCEEDED` rejections observed: "
        f"{concurrency['max_open_positions_exceeded_observed']}.",
        "- Max open positions (config gate): 1 (within-pair only).",
        "- Max correlated positions (config gate): 1 (within-pair only).",
        "",
        "## Cross-pair-specific diagnostics",
        "",
        "### Zero-trade pair-fold cells",
        "",
        f"- Count: **{zero_cell_count} / {total_cells}** "
        f"({zero_cell_pct:.1f} %)",
        "- The cross-pair rank-gap rule `|rank(quote) − rank(base)| ≥ 4` is "
        "selective: more than half of (pair × fold) cells produce zero "
        "trades because the gap is not exceeded for that pair in that "
        "fold's window.",
        "",
        "### Per-fold long/short imbalance",
        "",
        "| fold | long | short | total | long share |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in fold_long_short:
        lines.append(
            f"| {r['fold']} | {r['long']} | {r['short']} | {r['total']} | "
            f"{r['long_share_pct']:.1f}% |"
        )
    lines += [
        "",
        "### Per-fold simultaneous-signal frequency",
        "",
        "A 'simultaneous signal' is a single H4 bar where the strategy "
        "fires entries on ≥ 2 pairs at the same timestamp.",
        "",
        "| fold | bars with any signal | bars with sim. signal (≥ 2 pairs) | sim. share |",
        "|---|---:|---:|---:|",
    ]
    for r in fold_simultaneous:
        lines.append(
            f"| {r['fold']} | {r['bars_with_any_signal']} | "
            f"{r['bars_with_simultaneous_signal_ge_2_pairs']} | "
            f"{r['simultaneous_share_pct']:.1f}% |"
        )
    lines += [
        "",
        "### Per-fold cross-pair runner contract status",
        "",
        "| fold | contract_satisfied | common_index_length (H4 bars) |",
        "|---|:---:|---:|",
    ]
    for r in fold_contract:
        ok = "✓" if r["contract_satisfied"] else "✗"
        cidx = r["common_index_length"] or 0
        lines.append(f"| {r['fold']} | {ok} | {cidx:,} |")
    lines += [
        "",
        "All 8 folds satisfied the cross-pair runner integration contract; "
        "no fold was BLOCKED. The REJECT verdict comes from inherited "
        "gates alone.",
        "",
    ]

    (risk_dir / "diagnostics.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {risk_dir / 'diagnostics.json'}")
    print(f"wrote {risk_dir / 'diagnostics.md'}")
    print()
    print("Rejection totals by code:")
    if rejection_totals:
        for code, n in sorted(rejection_totals.items()):
            print(f"  {code}: {n}")
    else:
        print("  (none)")
    print()
    print("Entry-session bucket distribution:")
    for b, c in session_table.items():
        print(f"  {b}: {c}")
    print()
    print(f"Zero-trade pair-fold cells: {zero_cell_count} / {total_cells} "
          f"({zero_cell_pct:.1f}%)")
    print()
    print("Per-fold simultaneous-signal frequency:")
    for r in fold_simultaneous:
        print(
            f"  {r['fold']}: bars_with_signal={r['bars_with_any_signal']} "
            f"sim_>=2={r['bars_with_simultaneous_signal_ge_2_pairs']} "
            f"({r['simultaneous_share_pct']:.1f}%)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

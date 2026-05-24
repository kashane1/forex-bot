#!/usr/bin/env python3
"""CAMPAIGN_010 portfolio-risk diagnostics.

Reads the per-fold per-pair trade CSVs + the fold_detail.json
(`run_campaign_010.py` output), and produces a compact diagnostics
report describing:

  * per-pair exposure (trade count, total notional approximation)
  * max concurrent open positions (structurally bounded by config)
  * pair concentration (Phase 4 already reports single-pair dominance)
  * session clustering of entries
  * loss streaks (per pair)
  * drawdown clustering
  * RiskEngine rejection-code distribution

All numbers are diagnostic — none gate the verdict; the Phase 4
verdict is REJECT regardless. The diagnostics record the
risk-engine behaviour observed during the walk-forward run.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PAIRS = (
    "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD",
    "USD_CAD", "USD_CHF", "NZD_USD",
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

    for fold_dir in sorted(folds_dir.iterdir()):
        if not fold_dir.is_dir():
            continue
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
        fold_drawdowns.append({
            "fold_index": f["fold_index"],
            "test_start": f["test_start"],
            "test_end": f["test_end"],
            "per_pair_max_drawdown_pct": per_pair_dd,
            "median_pair_max_drawdown_pct": (
                sorted(per_pair_dd.values())[len(per_pair_dd) // 2]
                if per_pair_dd else 0.0
            ),
        })

    # RiskEngine rejection summary (per-pair aggregated across folds).
    rejection_totals: Counter = Counter()
    rejection_by_pair: dict[str, Counter] = {p: Counter() for p in PAIRS}
    for f in detail["folds"]:
        for pr in f["pair_runs"]:
            counts = pr.get("rejection_counts") or {}
            for code, n in counts.items():
                rejection_totals[code] += n
                rejection_by_pair[pr["instrument"]][code] += n

    # Concurrency: structurally bounded (max_open_positions = 1 per
    # bespoke engine; but we cross-check at the campaign level via
    # the fact that no fold has more than 1 active position per pair
    # at any time — the engine enforces this and the runner uses
    # mode='backtest'.
    concurrency = {
        "structurally_enforced_max_concurrent_per_instrument": 1,
        "structurally_enforced_max_positions_per_instrument_config_key": 1,
        "structurally_enforced_max_open_positions_config_key": 1,
        "note": (
            "BacktestEngine is single-instrument single-position-at-a-time, "
            "and the candidate's R2 rule (block-re-entry when an open "
            "position exists for the instrument) prevents pyramiding. "
            "Multi-instrument concurrency is constrained at the RiskEngine "
            "layer by the campaign config (max_open_positions=1, "
            "max_positions_per_instrument=1, max_correlated_positions=1)."
        ),
    }

    out = {
        "campaign_id": "CAMPAIGN_010",
        "strategy_name": "session_breakout",
        "strategy_version": "0.1.0-c010",
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
                p: dict(sorted(rejection_by_pair[p].items()))
                for p in PAIRS
            },
        },
    }

    risk_dir = campaign_dir / "risk"
    risk_dir.mkdir(parents=True, exist_ok=True)
    (risk_dir / "diagnostics.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8"
    )

    # Compact markdown.
    lines = [
        "# CAMPAIGN_010 — Portfolio-Risk Diagnostics (auto-generated)",
        "",
        "> Diagnostic only — does not gate the verdict. Phase 4 verdict",
        "> remains REJECT regardless. configs/approved_strategies.yaml",
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
    lines += [
        "",
        "## Concurrency",
        "",
        "- Max concurrent open positions per instrument: 1 (structurally enforced by BacktestEngine + R2 rule).",
        "- Max open positions (config gate): 1.",
        "- Max correlated positions (config gate): 1.",
        "",
    ]

    (risk_dir / "diagnostics.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {risk_dir / 'diagnostics.json'}")
    print(f"wrote {risk_dir / 'diagnostics.md'}")
    print()
    print("Rejection totals by code:")
    for code, n in sorted(rejection_totals.items()):
        print(f"  {code}: {n}")
    print()
    print("Entry-session bucket distribution:")
    for b, c in session_table.items():
        print(f"  {b}: {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

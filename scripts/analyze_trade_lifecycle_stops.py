#!/usr/bin/env python3
"""Stop-loss and exit diagnostics from *realized* campaign trade outcomes.

Read-only. Loads committed per-pair trade CSVs (default: CAMPAIGN_022, the only
campaign with committed per-trade data — see TRADE_LIFECYCLE_ARTIFACT_INVENTORY)
via the normalized lifecycle loader and reports, per campaign / split / cost /
pair and in aggregate:

  trade count, expectancy R, win rate, avg win R, avg loss R, breakeven win rate,
  exit-reason distribution, mean & median R by exit reason, hard-stop share,
  time-stop share, near-full-loss share (R <= -0.9), large-win share (R >= +1.0),
  and a bars-held distribution.

It uses ONLY realized outcomes. It makes **no** claim about what an alternative
stop would have done — that needs per-bar MFE/MAE (Phase 4/5). Nothing here is a
verdict, an approval, or a tuning result.

Outputs (compact — no per-trade dumps):
  research/trade_lifecycle_diagnostics/stop_exit_summary.json
  research/trade_lifecycle_diagnostics/stop_exit_summary.md

Usage:
    python scripts/analyze_trade_lifecycle_stops.py
    python scripts/analyze_trade_lifecycle_stops.py --campaign-dir backtests/CAMPAIGN_022_h4_h1_pullback_resolution --campaign-id CAMPAIGN_022
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.research.trade_lifecycle import TradeLifecycleRecord, load_trades_csv

OUT_DIR_DEFAULT = REPO_ROOT / "research" / "trade_lifecycle_diagnostics"

DEFAULT_CAMPAIGN_DIR = "backtests/CAMPAIGN_022_h4_h1_pullback_resolution"
DEFAULT_CAMPAIGN_ID = "CAMPAIGN_022"

SPLIT_TOKENS = ("train", "validation", "full", "test")
COST_TOKENS = ("base", "stress_2x", "stress_15x")

# Exit-reason normalization: classify each realized exit as hard-stop or time-stop.
HARD_STOP_REASONS = {"stop", "hard_stop", "protective_stop", "stop_loss"}
TIME_STOP_REASONS = {"time", "time_stop", "max_hold", "timeout"}


def _split_of(path: Path) -> str | None:
    parts = {p.lower() for p in path.parts}
    for s in SPLIT_TOKENS:
        if s in parts:
            return s
    return None


def _cost_of(path: Path) -> str:
    parts = {p.lower() for p in path.parts}
    for c in COST_TOKENS:
        if c in parts:
            return c
    return "base"


def _instrument_of(name: str) -> str | None:
    m = re.search(r"_([A-Z]{3}_[A-Z]{3})_", name)
    return m.group(1) if m else None


def _classify_exit(reason: str | None) -> str:
    if reason is None:
        return "unknown"
    r = reason.lower()
    if r in HARD_STOP_REASONS:
        return "hard_stop"
    if r in TIME_STOP_REASONS:
        return "time_stop"
    return reason


def _quantile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return float("nan")
    idx = q * (len(sorted_vals) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def _round(x: float | None, n: int = 4) -> float | None:
    if x is None:
        return None
    if isinstance(x, float) and (x != x):  # NaN
        return None
    return round(x, n)


def diagnose_group(records: list[TradeLifecycleRecord]) -> dict:
    """Realized stop/exit diagnostics for one set of trades."""
    rs = [r.result_r for r in records if r.result_r is not None]
    n = len(rs)
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r <= 0]
    avg_win = statistics.fmean(wins) if wins else None
    avg_loss = statistics.fmean(losses) if losses else None

    breakeven_wr = None
    if avg_win is not None and avg_loss is not None and (avg_win - avg_loss) != 0:
        breakeven_wr = abs(avg_loss) / (avg_win + abs(avg_loss))

    # Exit-reason buckets.
    exit_classes = [_classify_exit(r.exit_reason) for r in records]
    exit_dist = Counter(exit_classes)
    r_by_exit: dict[str, list[float]] = defaultdict(list)
    for rec, cls in zip(records, exit_classes, strict=True):
        if rec.result_r is not None:
            r_by_exit[cls].append(rec.result_r)

    exit_stats = {}
    for cls, vals in r_by_exit.items():
        exit_stats[cls] = {
            "count": len(vals),
            "share": _round(len(vals) / n) if n else None,
            "mean_r": _round(statistics.fmean(vals)) if vals else None,
            "median_r": _round(statistics.median(vals)) if vals else None,
        }

    bars = sorted(r.bars_held for r in records if r.bars_held is not None)
    bars_dist = None
    if bars:
        bars_dist = {
            "min": bars[0],
            "p25": _round(_quantile(bars, 0.25), 1),
            "median": _round(statistics.median(bars), 1),
            "mean": _round(statistics.fmean(bars), 1),
            "p75": _round(_quantile(bars, 0.75), 1),
            "max": bars[-1],
        }

    return {
        "trade_count": n,
        "expectancy_r": _round(statistics.fmean(rs)) if rs else None,
        "median_r": _round(statistics.median(rs)) if rs else None,
        "win_rate": _round(len(wins) / n) if n else None,
        "avg_win_r": _round(avg_win),
        "avg_loss_r": _round(avg_loss),
        "breakeven_win_rate": _round(breakeven_wr),
        "hard_stop_share": _round(exit_dist.get("hard_stop", 0) / n) if n else None,
        "time_stop_share": _round(exit_dist.get("time_stop", 0) / n) if n else None,
        "near_full_loss_share": _round(sum(1 for r in rs if r <= -0.9) / n) if n else None,
        "large_win_share": _round(sum(1 for r in rs if r >= 1.0) / n) if n else None,
        "exit_reason_distribution": dict(exit_dist),
        "r_by_exit_reason": exit_stats,
        "bars_held_distribution": bars_dist,
    }


def discover_trade_csvs(campaign_dir: Path) -> list[Path]:
    return sorted(campaign_dir.rglob("*_trades.csv"))


def load_all(campaign_dir: Path, campaign_id: str) -> list[tuple[str, str, str, list[TradeLifecycleRecord]]]:
    """Return (split, cost, pair, records) tuples for each trade CSV."""
    out = []
    for path in discover_trade_csvs(campaign_dir):
        split = _split_of(path) or "unknown"
        cost = _cost_of(path)
        pair = _instrument_of(path.name) or "UNKNOWN"
        recs = load_trades_csv(path, campaign_id=campaign_id, split=split)
        out.append((split, cost, pair, recs))
    return out


def build_report(campaign_dir: Path, campaign_id: str) -> dict:
    groups = load_all(campaign_dir, campaign_id)

    # Aggregate buckets keyed by (split, cost) and (split, cost, pair).
    by_split_cost: dict[tuple[str, str], list[TradeLifecycleRecord]] = defaultdict(list)
    by_split_cost_pair: dict[tuple[str, str, str], list[TradeLifecycleRecord]] = defaultdict(list)
    base_all: list[TradeLifecycleRecord] = []

    for split, cost, pair, recs in groups:
        by_split_cost[(split, cost)].extend(recs)
        by_split_cost_pair[(split, cost, pair)].extend(recs)
        if cost == "base" and split in ("train", "validation"):
            base_all.extend(recs)

    split_cost_report = {
        f"{s}/{c}": diagnose_group(recs) for (s, c), recs in sorted(by_split_cost.items())
    }
    pair_report: dict[str, dict] = {}
    for (s, c, p), recs in sorted(by_split_cost_pair.items()):
        pair_report.setdefault(f"{s}/{c}", {})[p] = diagnose_group(recs)

    overall_base = diagnose_group(base_all)

    # Reproduction check vs CAMPAIGN_022_BEHAVIOR_DIAGNOSTICS.md (base train+val).
    repro = None
    if campaign_id == "CAMPAIGN_022":
        repro = {
            "base_train_val_trades": overall_base["trade_count"],
            "expected_trades_approx": 2396,
            "trades_match": overall_base["trade_count"] == 2396,
            "hard_stop_share": overall_base["hard_stop_share"],
            "time_stop_share": overall_base["time_stop_share"],
            "hard_stop_share_approx_60pct": (
                overall_base["hard_stop_share"] is not None
                and 0.57 <= overall_base["hard_stop_share"] <= 0.63
            ),
            "stop_bucket_negative": (
                overall_base["r_by_exit_reason"].get("hard_stop", {}).get("mean_r", 0) < 0
            ),
            "time_bucket_positive": (
                overall_base["r_by_exit_reason"].get("time_stop", {}).get("mean_r", 0) > 0
            ),
        }

    failure_modes = _identify_failure_modes(overall_base, pair_report)

    return {
        "strategy_evidence": False,
        "not_approved": True,
        "diagnostic_only": True,
        "uses_realized_outcomes_only": True,
        "no_alternative_stop_claims": True,
        "campaign_id": campaign_id,
        "campaign_dir": str(campaign_dir.relative_to(REPO_ROOT)),
        "overall_base_train_val": overall_base,
        "by_split_cost": split_cost_report,
        "by_pair": pair_report,
        "c022_reproduction_check": repro,
        "failure_modes": failure_modes,
    }


def _identify_failure_modes(overall: dict, pair_report: dict) -> dict:
    modes = {}
    hs = overall.get("hard_stop_share")
    if hs is not None and hs >= 0.5:
        modes["high_hard_stop_share"] = (
            f"{hs:.0%} of trades exit at the hard stop — the dominant exit. "
            "Favorable continuation, where present, is cut off before it pays."
        )
    ts_mean = overall.get("r_by_exit_reason", {}).get("time_stop", {}).get("mean_r")
    ts_share = overall.get("time_stop_share")
    if ts_mean is not None and ts_mean > 0 and ts_share is not None and ts_share < 0.5:
        modes["favorable_time_exits_too_few"] = (
            f"time-exits average {ts_mean:+.2f}R but are only {ts_share:.0%} of trades — "
            "the edge exists for survivors but too few survive the stop."
        )
    # Pair concentration of hard stops within base/train.
    base_train = pair_report.get("train/base", {})
    if base_train:
        worst = sorted(
            ((p, d.get("hard_stop_share") or 0.0) for p, d in base_train.items()),
            key=lambda kv: kv[1],
            reverse=True,
        )
        modes["hard_stop_share_by_pair_train_base"] = {
            p: round(s, 3) for p, s in worst
        }
    nfl = overall.get("near_full_loss_share")
    if nfl is not None and nfl >= 0.35:
        modes["near_full_loss_concentration"] = (
            f"{nfl:.0%} of trades lose >= 0.9R — losses cluster near the full stop, "
            "not partial exits."
        )
    return modes


def _fmt(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append("# Trade Lifecycle — Stop & Exit Diagnostics (realized outcomes)")
    lines.append("")
    lines.append(f"**Campaign:** {report['campaign_id']} · **Dir:** `{report['campaign_dir']}`")
    lines.append("")
    lines.append("Generated by `scripts/analyze_trade_lifecycle_stops.py`. **Diagnostic "
             "only** — realized outcomes, no alternative-stop claims, no verdict, no "
             "approval, no tuning.")
    lines.append("")

    o = report["overall_base_train_val"]
    lines.append("## Overall (base cost, train+validation)")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---|")
    for k in ("trade_count", "expectancy_r", "median_r", "win_rate", "avg_win_r",
              "avg_loss_r", "breakeven_win_rate", "hard_stop_share", "time_stop_share",
              "near_full_loss_share", "large_win_share"):
        lines.append(f"| {k} | {_fmt(o.get(k))} |")
    lines.append("")
    lines.append("### R by exit reason (base train+val)")
    lines.append("")
    lines.append("| exit | count | share | mean R | median R |")
    lines.append("|---|---|---|---|---|")
    for cls, st in o.get("r_by_exit_reason", {}).items():
        lines.append(f"| {cls} | {st['count']} | {_fmt(st['share'])} | "
                 f"{_fmt(st['mean_r'])} | {_fmt(st['median_r'])} |")
    lines.append("")
    bd = o.get("bars_held_distribution")
    if bd:
        lines.append(f"Bars held — min {bd['min']}, p25 {bd['p25']}, median {bd['median']}, "
                 f"mean {bd['mean']}, p75 {bd['p75']}, max {bd['max']}.")
        lines.append("")

    repro = report.get("c022_reproduction_check")
    if repro:
        lines.append("## C022 reproduction check")
        lines.append("")
        lines.append("| check | value |")
        lines.append("|---|---|")
        for k, v in repro.items():
            lines.append(f"| {k} | {_fmt(v)} |")
        lines.append("")

    lines.append("## By split / cost")
    lines.append("")
    lines.append("| group | trades | exp R | win% | hard-stop% | time-stop% | time-exit mean R |")
    lines.append("|---|---|---|---|---|---|---|")
    for grp, d in report["by_split_cost"].items():
        te = d.get("r_by_exit_reason", {}).get("time_stop", {}).get("mean_r")
        lines.append(f"| {grp} | {d['trade_count']} | {_fmt(d['expectancy_r'])} | "
                 f"{_fmt(d['win_rate'])} | {_fmt(d['hard_stop_share'])} | "
                 f"{_fmt(d['time_stop_share'])} | {_fmt(te)} |")
    lines.append("")

    lines.append("## By pair (train/base)")
    lines.append("")
    tb = report["by_pair"].get("train/base", {})
    if tb:
        lines.append("| pair | trades | exp R | win% | hard-stop% | near-full-loss% |")
        lines.append("|---|---|---|---|---|---|")
        for pair, d in sorted(tb.items()):
            lines.append(f"| {pair} | {d['trade_count']} | {_fmt(d['expectancy_r'])} | "
                     f"{_fmt(d['win_rate'])} | {_fmt(d['hard_stop_share'])} | "
                     f"{_fmt(d['near_full_loss_share'])} |")
        lines.append("")

    lines.append("## Failure modes (realized-outcome reading)")
    lines.append("")
    for k, v in report["failure_modes"].items():
        if isinstance(v, dict):
            lines.append(f"- **{k}**:")
            for pk, pv in v.items():
                lines.append(f"  - {pk}: {pv}")
        else:
            lines.append(f"- **{k}**: {v}")
    lines.append("")
    lines.append("> These describe *what realized trades did*. Whether a different stop "
             "would have helped requires per-bar MFE/MAE (Phase 4/5), not these "
             "outcomes.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign-dir", default=DEFAULT_CAMPAIGN_DIR)
    ap.add_argument("--campaign-id", default=DEFAULT_CAMPAIGN_ID)
    ap.add_argument("--out-dir", default=str(OUT_DIR_DEFAULT))
    args = ap.parse_args()

    campaign_dir = (REPO_ROOT / args.campaign_dir).resolve()
    if not campaign_dir.is_dir():
        print(f"campaign dir not found: {campaign_dir}")
        return 1

    report = build_report(campaign_dir, args.campaign_id)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "stop_exit_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    (out_dir / "stop_exit_summary.md").write_text(render_md(report))

    o = report["overall_base_train_val"]
    print(f"{args.campaign_id}: {o['trade_count']} base train+val trades, "
          f"exp {o['expectancy_r']}R, hard-stop {o['hard_stop_share']}, "
          f"time-stop {o['time_stop_share']}")
    if report.get("c022_reproduction_check"):
        print("reproduction:", report["c022_reproduction_check"])
    print(f"wrote {out_dir/'stop_exit_summary.json'}")
    print(f"wrote {out_dir/'stop_exit_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

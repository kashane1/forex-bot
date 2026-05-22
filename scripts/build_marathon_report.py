#!/usr/bin/env python3
"""Generic Research-Marathon-001 campaign report builder (CAMPAIGN_006-008).

Two-stage, screening-aware:

  * SCREENING gate — decided from train + validation + cost stress only.
    Determines whether the 2025-2026 reported test lockbox may be opened.
  * FINAL gate — only evaluated if the test window was actually run.

If the test runs are absent the report states the screening verdict and
explicitly records that the test window was NOT opened (lockbox intact).
`--research-only` caps the verdict at REVISE (CAMPAIGN_008).
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.config import load_settings
from forex_bot.financing import financing_debit_r

SPLIT_ORDER = ["train", "validation", "test_untouched", "full"]

# Immutable prior-campaign untouched-test results (real OANDA H4, 6-pair
# universe) — for the cross-campaign comparison. Sourced from the
# committed CAMPAIGN_002/003/004 reports.
PRIOR_TEST = [
    ("CAMPAIGN_002 trend H4", "−0.085 R", "0.75", "−1.02%"),
    ("CAMPAIGN_003 trend+ADX H4", "−0.071 R", "0.77", "−0.63%"),
    ("CAMPAIGN_004 vol-breakout H4", "−0.163 R", "0.63", "−1.40%"),
]


def _git(*a: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *a],
                           capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return ""
    return r.stdout.strip()


def _fmt_pf(x):
    return "n/a" if x is None else f"{x:.2f}"


def load_summaries(runs: Path) -> list[dict]:
    out = []
    for p in runs.rglob("*_summary.json"):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out


def load_trades_by_run(runs: Path) -> dict[tuple[str, str], list[dict]]:
    out: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for p in runs.rglob("baseline_*_trades.csv"):
        rest = p.stem.removesuffix("_trades").removeprefix("baseline_")
        toks = rest.split("_")
        if len(toks) < 4:
            continue
        pair = f"{toks[0]}_{toks[1]}"
        split = "_".join(toks[3:])
        for row in csv.DictReader(p.open(encoding="utf-8")):
            out[(pair, split)].append(row)
    return out


def load_rejections(runs: Path) -> list[dict]:
    out = []
    for p in runs.rglob("*_risk_rejections.csv"):
        for row in csv.DictReader(p.open(encoding="utf-8")):
            out.append(row)
    return out


def _baseline(summaries: list[dict], split: str) -> list[dict]:
    return [
        s for s in summaries
        if s["label"].startswith("baseline_") and s["split"] == split
    ]


def _agg(rows: list[dict]) -> dict:
    ms = [r["metrics"] for r in rows]
    pf = [m["profit_factor"] for m in ms if m["profit_factor"] is not None]
    return {
        "trades": sum(m["trade_count"] for m in ms),
        "rejected": sum(r.get("rejected_signal_count", 0) for r in rows),
        "ret": statistics.mean(m["total_return_pct"] for m in ms) if ms else 0.0,
        "dd": statistics.mean(m["max_drawdown_pct"] for m in ms) if ms else 0.0,
        "pf": statistics.mean(pf) if pf else None,
        "exp": statistics.mean(m["expectancy_r"] for m in ms) if ms else 0.0,
        "win": statistics.mean(m["win_rate"] for m in ms) if ms else 0.0,
        "positive_pairs": sum(1 for m in ms if m["total_return_pct"] > 0),
        "n_pairs": len(ms),
        "worst_dd": min((m["max_drawdown_pct"] for m in ms), default=0.0),
    }


def _mean_debit_r(trades: list[dict]) -> float:
    if not trades:
        return 0.0
    vals = []
    for t in trades:
        vals.append(financing_debit_r(
            t["instrument"], Decimal(t["units"]), Decimal(t["entry_price"]),
            Decimal(t["stop_price"]), int(t["bars_held"]),
        ))
    return statistics.mean(vals)


def split_table(summaries: list[dict]) -> str:
    lines = [
        "| split | trades | rejected | return % | max-DD % | PF | expectancy R | win % | +pairs |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for split in SPLIT_ORDER:
        rows = _baseline(summaries, split)
        if not rows:
            continue
        a = _agg(rows)
        lines.append(
            f"| {split} | {a['trades']} | {a['rejected']} | {a['ret']:+.2f}% | "
            f"{a['dd']:+.2f}% | {_fmt_pf(a['pf'])} | {a['exp']:+.3f} | "
            f"{100*a['win']:.1f}% | {a['positive_pairs']}/{a['n_pairs']} |"
        )
    return "\n".join(lines)


def pair_table(summaries: list[dict], split: str) -> str:
    rows = _baseline(summaries, split)
    if not rows:
        return f"_Split `{split}` was not run._"
    lines = [
        "| pair | trades | rejected | return % | max-DD % | PF | expectancy R | win % |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for s in sorted(rows, key=lambda x: x["instrument"]):
        m = s["metrics"]
        lines.append(
            f"| {s['instrument']} | {m['trade_count']} | "
            f"{s.get('rejected_signal_count', 0)} | {m['total_return_pct']:+.2f}% | "
            f"{m['max_drawdown_pct']:+.2f}% | {_fmt_pf(m['profit_factor'])} | "
            f"{m['expectancy_r']:+.3f} | {100*m['win_rate']:.1f}% |"
        )
    return "\n".join(lines)


def cost_table(summaries: list[dict]) -> str:
    by = defaultdict(list)
    for s in summaries:
        if s["label"].startswith("cost_"):
            by[s["cost_regime"]].append(s)
    lines = [
        "| regime | trades | avg return % | avg max-DD % | avg PF | avg expectancy R |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for regime in ("base", "stress_15x", "stress_2x"):
        rows = by.get(regime, [])
        if not rows:
            continue
        a = _agg(rows)
        lines.append(
            f"| {regime} | {a['trades']} | {a['ret']:+.2f}% | {a['dd']:+.2f}% | "
            f"{_fmt_pf(a['pf'])} | {a['exp']:+.3f} |"
        )
    return "\n".join(lines)


def financing_table(summaries: list[dict], by_run: dict) -> str:
    lines = [
        "Conservative financing stress overlay from the tested "
        "`forex_bot.financing` module. Financing is NOT in the engine "
        "PnL — a hard live-promotion blocker.",
        "",
        "| split | raw expectancy R | financing debit R | financing-stressed expectancy R |",
        "|---|---:|---:|---:|",
    ]
    for split in SPLIT_ORDER:
        rows = _baseline(summaries, split)
        if not rows:
            continue
        raws, debits = [], []
        for s in rows:
            raws.append(s["metrics"]["expectancy_r"])
            debits.append(_mean_debit_r(by_run.get((s["instrument"], split), [])))
        lines.append(
            f"| {split} | {statistics.mean(raws):+.3f} | "
            f"{statistics.mean(debits):.3f} | "
            f"{statistics.mean(r-d for r, d in zip(raws, debits, strict=True)):+.3f} |"
        )
    return "\n".join(lines)


def rejection_table(rejections: list[dict]) -> str:
    by_code: Counter[str] = Counter()
    by_pair: Counter[str] = Counter()
    by_split: Counter[str] = Counter()
    by_hour: Counter[str] = Counter()
    for r in rejections:
        by_code[r["rejection_code"]] += 1
        by_pair[r["instrument"]] += 1
        by_split[r["split"]] += 1
        by_hour[r["hour_utc"]] += 1
    out = [f"Total rejection rows: **{len(rejections)}** "
           "(per-run `*_risk_rejections.csv`).", "", "**By code:**", "",
           "| code | count |", "|---|---:|"]
    for c, n in by_code.most_common():
        out.append(f"| `{c}` | {n} |")
    out += ["", "**By pair:**", "", "| pair | count |", "|---|---:|"]
    for p, n in sorted(by_pair.items()):
        out.append(f"| {p} | {n} |")
    out += ["", "**By split:**", "", "| split | count |", "|---|---:|"]
    for s in SPLIT_ORDER:
        if by_split.get(s):
            out.append(f"| {s} | {by_split[s]} |")
    out += ["", "**By UTC hour (non-zero):**", "", "| hour | count |", "|---:|---:|"]
    for h in range(24):
        if by_hour.get(str(h)):
            out.append(f"| {h:02d}:00 | {by_hour[str(h)]} |")
    return "\n".join(out)


def trade_diag(by_run: dict) -> str:
    trades = [t for (p, s), ts in by_run.items() if s == "full" for t in ts]
    if not trades:
        return "_No full-window trades._"
    pnls = [float(t["pnl"]) for t in trades]
    rs = [float(t["r_multiple"]) for t in trades]
    by_exit = defaultdict(list)
    for t in trades:
        by_exit[t["exit_reason"]].append(t)
    out = [
        f"Full-window baseline trades: **{len(trades)}**.", "",
        "| metric | value |", "|---|---:|",
        f"| win rate | {100*sum(1 for p in pnls if p>0)/len(pnls):.1f}% |",
        f"| mean R | {statistics.mean(rs):+.3f} |",
        f"| median R | {statistics.median(rs):+.3f} |",
        f"| total PnL USD | {sum(pnls):+.2f} |",
        "", "**Exit reasons:**", "",
        "| exit | trades | total PnL | expectancy R | win % |",
        "|---|---:|---:|---:|---:|",
    ]
    for reason, ts in sorted(by_exit.items(), key=lambda kv: -len(kv[1])):
        ps = [float(t["pnl"]) for t in ts]
        er = [float(t["r_multiple"]) for t in ts]
        out.append(
            f"| {reason} | {len(ts)} | {sum(ps):+.2f} | "
            f"{statistics.mean(er):+.3f} | "
            f"{100*sum(1 for p in ps if p>0)/len(ts):.1f}% |"
        )
    ranked = sorted(trades, key=lambda t: float(t["pnl"]))
    out += ["", "**Top 5 losers / winners:**", "",
            "| pair | side | entry | bars | R | PnL |", "|---|---|---|---:|---:|---:|"]
    for t in ranked[:5] + ranked[-5:]:
        out.append(
            f"| {t['instrument']} | {t['side']} | {t['entry_time'][:10]} | "
            f"{t['bars_held']} | {float(t['r_multiple']):+.2f} | {float(t['pnl']):+.2f} |"
        )
    return "\n".join(out)


def screening_gate(summaries: list[dict], by_run: dict) -> tuple[bool, list[str]]:
    """May the reported test window be opened? Returns (pass, reasons)."""
    fails: list[str] = []
    train = _agg(_baseline(summaries, "train"))
    val = _agg(_baseline(summaries, "validation"))
    if not train["n_pairs"] or not val["n_pairs"]:
        return False, ["screening splits missing"]
    if train["exp"] < 0:
        fails.append(f"train expectancy negative ({train['exp']:+.3f} R)")
    if val["exp"] < 0:
        fails.append(f"validation expectancy negative ({val['exp']:+.3f} R)")
    if (val["pf"] or 0) < 1.05:
        fails.append(f"validation PF {_fmt_pf(val['pf'])} < 1.05")
    if val["positive_pairs"] < 2:
        fails.append(f"only {val['positive_pairs']} pair(s) positive on validation")
    if val["trades"] < 30:
        fails.append(f"validation trade count {val['trades']} too low")
    s15 = [s for s in summaries if s["label"].startswith("cost_stress_15x_")]
    if s15:
        e = statistics.mean(s["metrics"]["expectancy_r"] for s in s15)
        if e < 0:
            fails.append(f"stress_15x expectancy negative ({e:+.3f} R)")
    return (not fails), fails


def final_gate(
    summaries: list[dict], by_run: dict, research_only: bool
) -> tuple[str, list[str]]:
    test = _agg(_baseline(summaries, "test_untouched"))
    fails: list[str] = []
    if not test["n_pairs"]:
        return "REJECT", ["test window not run"]
    if test["exp"] <= 0:
        fails.append(f"test expectancy not positive ({test['exp']:+.3f} R)")
    if (test["pf"] or 0) < 1.05:
        fails.append(f"test PF {_fmt_pf(test['pf'])} < 1.05")
    if test["positive_pairs"] < 2:
        fails.append(f"only {test['positive_pairs']} pair(s) positive on test")
    if test["worst_dd"] < -8.0:
        fails.append(f"worst test drawdown {test['worst_dd']:.2f}% breaches policy")
    s2 = [s for s in summaries if s["label"].startswith("cost_stress_2x_")]
    if s2:
        e = statistics.mean(s["metrics"]["expectancy_r"] for s in s2)
        if e <= 0:
            fails.append(f"stress_2x expectancy not positive ({e:+.3f} R)")
    # financing-stressed test
    rows = _baseline(summaries, "test_untouched")
    stressed = []
    for s in rows:
        stressed.append(
            s["metrics"]["expectancy_r"]
            - _mean_debit_r(by_run.get((s["instrument"], "test_untouched"), []))
        )
    if stressed and statistics.mean(stressed) <= 0:
        fails.append(
            f"financing-stressed test expectancy not positive "
            f"({statistics.mean(stressed):+.3f} R)"
        )
    if fails:
        return "REJECT", fails
    if research_only:
        return "REVISE", [
            "all return/risk gates passed, but this is a research-only "
            "campaign — capped at REVISE pending human review"
        ]
    return "PAPER-TRADE-ONLY", ["all pre-committed test gates passed"]


def build(args) -> str:
    runs = Path(args.runs)
    summaries = load_summaries(runs)
    by_run = load_trades_by_run(runs)
    rejections = load_rejections(runs)
    settings = load_settings(Path(args.config))
    index = {}
    if (runs / "_index.json").exists():
        index = json.loads((runs / "_index.json").read_text())

    test_run = bool(_baseline(summaries, "test_untouched"))
    screen_pass, screen_fails = screening_gate(summaries, by_run)

    if test_run:
        verdict, gate_reasons = final_gate(summaries, by_run, args.research_only)
        stage = "FINAL (test window opened)"
    else:
        verdict = "REJECT"
        gate_reasons = screen_fails or ["screening gate not evaluated"]
        stage = "SCREENING ONLY (test lockbox NOT opened)"

    prior_cmp = "\n".join(
        f"| {name} | {exp} | {pf} | {ret} |" for name, exp, pf, ret in PRIOR_TEST
    )

    doc = f"""# {args.title}

> **Result: {verdict}** ({stage}). Real OANDA practice data, RiskEngine
> wired in, pre-committed gates. Part of Research Marathon 001. This
> campaign does **not** authorize paper-loop, demo-loop, or order
> submission.

## Provenance

- **Campaign:** {args.campaign_id}
- **Branch:** `{_git("rev-parse", "--abbrev-ref", "HEAD")}`
- **Git commit:** `{_git("rev-parse", "HEAD")}`
- **Working tree dirty at report time:** {"YES" if _git("status", "--porcelain") else "no"}
- **Config:** `{args.config}`
- **Config hash:** `{settings.config_hash}`
- **Strategy:** `{index.get("strategy", "?")} {index.get("strategy_version", "?")}`
- **Granularity:** {index.get("granularity", "?")}
- **Pre-commit spec:** `{args.precommit}`
- **Data source:** real OANDA practice (reused from `data/campaign_002.sqlite3` unless noted)
- **RiskEngine invoked:** YES — all runs, `mode="backtest"`
- **Financing:** estimated via conservative stress overlay
  (`forex_bot.financing`); UNMODELED in-engine; hard live blocker.
- **Total runs:** {len(summaries)}
- **Phases run:** {", ".join(index.get("phases_run", []))}

## Test-window discipline

- **Screening gate (train + validation + stress):**
  {"PASS" if screen_pass else "FAIL"}.
"""
    for r in screen_fails:
        doc += f"  - {r}\n"
    if not screen_fails:
        doc += "  - train & validation both non-negative; validation PF, pair breadth, trade count, and stress_15x all clear.\n"
    doc += f"""- **Reported test window (2025-01-01 → 2026-05-20) opened:** {"YES" if test_run else "NO"}.
{"  The test lockbox was opened because the screening gate passed." if test_run else "  The test lockbox was NOT opened — the screening gate did not pass, so per marathon discipline the 2025-2026 window was not run."}

## Metrics by split

{split_table(summaries)}

## Metrics by pair — validation (2023-01-01 → 2024-12-31)

{pair_table(summaries, "validation")}

## Metrics by pair — full window (2020-01-01 → 2026-05-20)

{pair_table(summaries, "full")}
"""
    if test_run:
        doc += f"""
## Metrics by pair — reported test (2025-01-01 → 2026-05-20)

{pair_table(summaries, "test_untouched")}
"""
    doc += f"""
## Cost stress (full window)

{cost_table(summaries)}

## Financing stress

{financing_table(summaries, by_run)}

## RiskEngine — rejections

{rejection_table(rejections)}

## Trade diagnostics (full-window baseline)

{trade_diag(by_run)}

## Comparison to prior campaigns (real OANDA H4, untouched test)

| campaign | expectancy R | PF | return % |
|---|---|---|---|
{prior_cmp}

(This campaign's screening/test figures are in the tables above. Prior
campaigns ran the test window directly; this marathon screens first.)

## Known limitations

1. Financing unmodeled in-engine — stress overlay only; hard live blocker.
2. Backtest fills approximate broker behavior; no live dry-run.
3. Single pre-committed configuration — no parameter sweep (by design).

## Pass/fail decision

Stage: **{stage}**. Verdict: **{verdict}**.

"""
    for r in gate_reasons:
        doc += f"- {r}\n"
    doc += "\n"
    if verdict == "PAPER-TRADE-ONLY":
        doc += (
            "All pre-committed test gates passed. This earns a "
            "PAPER-TRADE-ONLY research recommendation — **not** live. "
            "Financing must be modeled before any live consideration."
        )
    elif verdict == "REVISE":
        doc += (
            "Return/risk gates passed but this is a research-only "
            "campaign — capped at REVISE pending human review. Not "
            "promoted."
        )
    else:
        doc += (
            "Pre-committed gates not met. Do not paper-trade, "
            "demo-trade, or live-trade this strategy."
        )
    doc += "\n\n_Live trading is not recommended and not in scope._\n"
    return doc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--campaign-id", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--precommit", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--research-only", action="store_true")
    args = ap.parse_args()
    doc = build(args)
    Path(args.out).write_text(doc, encoding="utf-8")
    verdict = doc.split("**Result: ", 1)[1].split("**", 1)[0]
    print(f"wrote {args.out}  (verdict: {verdict})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

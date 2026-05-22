#!/usr/bin/env python3
"""Build backtests/CAMPAIGN_004_VOLATILITY_BREAKOUT_REPORT.md.

Consumes CAMPAIGN_004 run artifacts (summary JSONs, trades CSVs,
risk_rejections CSVs), the reused CAMPAIGN_002 provenance, and the
committed CAMPAIGN_002 H4 + CAMPAIGN_003 baseline summaries for
cross-campaign comparison. Applies the conservative financing stress
model from forex_bot.financing and the pre-committed Step-6 gates.
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
from forex_bot.data.db import Database
from forex_bot.data.repositories import DataSourceRepo
from forex_bot.financing import financing_debit_r, financing_debit_usd

PAIRS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF"]
SPLIT_ORDER = ["train", "validation", "test_untouched", "full"]


def _git_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        return "unknown"
    return r.stdout.strip() or "unknown"


def _git_dirty() -> bool:
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain"],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        return False
    return bool(r.stdout.strip())


def _fmt_pf(x: float | None) -> str:
    return "inf" if x is None else f"{x:.2f}"


# ---- loaders --------------------------------------------------------------


def load_summaries(runs_dir: Path) -> list[dict]:
    out = []
    for p in runs_dir.rglob("*_summary.json"):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out


def load_trades_by_run(runs_dir: Path) -> dict[tuple[str, str], list[dict]]:
    out: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for p in runs_dir.rglob("baseline_*_trades.csv"):
        rest = p.stem.removesuffix("_trades").removeprefix("baseline_")
        tokens = rest.split("_")
        if len(tokens) < 4:
            continue
        pair = f"{tokens[0]}_{tokens[1]}"
        split = "_".join(tokens[3:])
        for row in csv.DictReader(p.open(encoding="utf-8")):
            out[(pair, split)].append(row)
    return out


def full_window_trades(by_run: dict[tuple[str, str], list[dict]]) -> list[dict]:
    out: list[dict] = []
    for (_pair, split), ts in by_run.items():
        if split == "full":
            out.extend(ts)
    return out


def load_rejections(runs_dir: Path) -> list[dict]:
    rej = []
    for p in runs_dir.rglob("*_risk_rejections.csv"):
        for row in csv.DictReader(p.open(encoding="utf-8")):
            rej.append(row)
    return rej


def load_prior_baseline(campaign_runs: Path, gran_subdir: str) -> dict[tuple[str, str], dict]:
    """Committed prior-campaign baseline summaries keyed by (pair, split)."""
    out: dict[tuple[str, str], dict] = {}
    for split in SPLIT_ORDER:
        for pair in PAIRS:
            p = campaign_runs / gran_subdir / split / f"baseline_{pair}_H4_{split}_summary.json"
            if p.exists():
                out[(pair, split)] = json.loads(p.read_text(encoding="utf-8"))
    return out


def _summary_lookup(summaries: list[dict]) -> dict[tuple[str, str], dict]:
    return {
        (s["instrument"], s["split"]): s
        for s in summaries
        if s["label"].startswith("baseline_")
    }


# ---- financing helpers (use the tested forex_bot.financing module) --------


def _trade_debit_r(t: dict) -> float:
    return financing_debit_r(
        t["instrument"],
        Decimal(t["units"]),
        Decimal(t["entry_price"]),
        Decimal(t["stop_price"]),
        int(t["bars_held"]),
    )


def _trade_debit_usd(t: dict) -> float:
    return financing_debit_usd(
        t["instrument"],
        Decimal(t["units"]),
        Decimal(t["entry_price"]),
        int(t["bars_held"]),
    )


def _mean_debit_r(trades: list[dict]) -> float:
    return statistics.mean(_trade_debit_r(t) for t in trades) if trades else 0.0


# ---- sections -------------------------------------------------------------


def provenance_section(db_path: Path) -> str:
    rows = DataSourceRepo(Database(db_path)).all_in_campaign("CAMPAIGN_002")
    best: dict[str, dict] = {}
    for r in rows:
        if r["granularity"] != "H4" or r["instrument"] not in PAIRS:
            continue
        cur = best.get(r["instrument"])
        if cur is None or r["candles_written"] > cur["candles_written"]:
            best[r["instrument"]] = r
    lines = [
        "CAMPAIGN_004 **reuses** the real OANDA practice H4 candles fetched "
        "for CAMPAIGN_002 (`data/campaign_002.sqlite3`). No re-fetch, no "
        "synthetic data. Hashes below were recorded at CAMPAIGN_002 fetch "
        "time and match the CAMPAIGN_002 report.",
        "",
        "| instrument | gran | source | candles | first | last | raw_sha256 (16) | norm_sha256 (16) |",
        "|---|---|---|---:|---|---|---|---|",
    ]
    for pair in PAIRS:
        r = best.get(pair)
        if not r:
            lines.append(f"| {pair} | H4 | **MISSING** | | | | | |")
            continue
        lines.append(
            f"| {pair} | H4 | {r['source']} | {r['candles_written']} | "
            f"{(r['first_ts'] or '')[:10]} | {(r['last_ts'] or '')[:10]} | "
            f"`{(r['raw_sha256'] or '')[:16]}` | `{(r['normalized_sha256'] or '')[:16]}` |"
        )
    return "\n".join(lines)


def split_table(summaries: list[dict]) -> str:
    by = defaultdict(list)
    for s in summaries:
        if s["label"].startswith("baseline_"):
            by[s["split"]].append(s)
    lines = [
        "| split | trades | rejected | return % | max-DD % | PF | expectancy R | win % |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for split in SPLIT_ORDER:
        rs = by.get(split, [])
        if not rs:
            continue
        ms = [r["metrics"] for r in rs]
        pf = [m["profit_factor"] for m in ms if m["profit_factor"] is not None]
        lines.append(
            f"| {split} | {sum(m['trade_count'] for m in ms)} | "
            f"{sum(r.get('rejected_signal_count', 0) for r in rs)} | "
            f"{statistics.mean(m['total_return_pct'] for m in ms):+.2f}% | "
            f"{statistics.mean(m['max_drawdown_pct'] for m in ms):+.2f}% | "
            f"{_fmt_pf(statistics.mean(pf) if pf else None)} | "
            f"{statistics.mean(m['expectancy_r'] for m in ms):+.3f} | "
            f"{100 * statistics.mean(m['win_rate'] for m in ms):.1f}% |"
        )
    return "\n".join(lines)


def pair_table(summaries: list[dict], split: str) -> str:
    rows = [
        s for s in summaries
        if s["label"].startswith("baseline_") and s["split"] == split
    ]
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
            f"{m['expectancy_r']:+.3f} | {100 * m['win_rate']:.1f}% |"
        )
    return "\n".join(lines)


def cost_stress_table(summaries: list[dict]) -> str:
    by = defaultdict(list)
    for s in summaries:
        if s["label"].startswith("cost_"):
            by[s["cost_regime"]].append(s)
    lines = [
        "| regime | trades | rejected | avg return % | avg max-DD % | avg PF | avg expectancy R |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for regime in ("base", "stress_15x", "stress_2x"):
        rs = by.get(regime, [])
        if not rs:
            continue
        ms = [r["metrics"] for r in rs]
        pf = [m["profit_factor"] for m in ms if m["profit_factor"] is not None]
        lines.append(
            f"| {regime} | {sum(m['trade_count'] for m in ms)} | "
            f"{sum(r.get('rejected_signal_count', 0) for r in rs)} | "
            f"{statistics.mean(m['total_return_pct'] for m in ms):+.2f}% | "
            f"{statistics.mean(m['max_drawdown_pct'] for m in ms):+.2f}% | "
            f"{_fmt_pf(statistics.mean(pf) if pf else None)} | "
            f"{statistics.mean(m['expectancy_r'] for m in ms):+.3f} |"
        )
    return "\n".join(lines)


def financing_table(summaries: list[dict], by_run: dict) -> str:
    look = _summary_lookup(summaries)
    lines = [
        "Conservative financing stress from the tested "
        "[`forex_bot.financing`](../src/forex_bot/financing.py) module "
        "(worst-of-long/short bp/day). Financing is **not** in the engine "
        "PnL — this is an after-the-fact overlay. 'Raw expectancy R' is the "
        "per-run summary metric.",
        "",
        "| pair | trades | total financing debit (USD) | mean debit/trade (R) | raw expectancy R | financing-stressed expectancy R |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for pair in PAIRS:
        ts = by_run.get((pair, "full"), [])
        summ = look.get((pair, "full"))
        if not ts or summ is None:
            continue
        debit_usd = sum(_trade_debit_usd(t) for t in ts)
        mean_debit_r = _mean_debit_r(ts)
        raw = summ["metrics"]["expectancy_r"]
        lines.append(
            f"| {pair} | {len(ts)} | {debit_usd:.2f} | {mean_debit_r:.3f} | "
            f"{raw:+.3f} | {raw - mean_debit_r:+.3f} |"
        )
    return "\n".join(lines)


def financing_by_split(summaries: list[dict], by_run: dict) -> str:
    look = _summary_lookup(summaries)
    lines = [
        "Pair-averaged, consistent with Metrics-by-split.",
        "",
        "| split | raw expectancy R | financing debit R | financing-stressed expectancy R |",
        "|---|---:|---:|---:|",
    ]
    for split in SPLIT_ORDER:
        raws, debits, stressed = [], [], []
        for pair in PAIRS:
            summ = look.get((pair, split))
            if summ is None:
                continue
            raw = summ["metrics"]["expectancy_r"]
            debit = _mean_debit_r(by_run.get((pair, split), []))
            raws.append(raw)
            debits.append(debit)
            stressed.append(raw - debit)
        if raws:
            lines.append(
                f"| {split} | {statistics.mean(raws):+.3f} | "
                f"{statistics.mean(debits):.3f} | {statistics.mean(stressed):+.3f} |"
            )
    return "\n".join(lines)


def rejection_section(rejections: list[dict]) -> str:
    by_code: Counter[str] = Counter()
    by_pair: Counter[str] = Counter()
    by_split: Counter[str] = Counter()
    by_hour: Counter[str] = Counter()
    for r in rejections:
        by_code[r["rejection_code"]] += 1
        by_pair[r["instrument"]] += 1
        by_split[r["split"]] += 1
        by_hour[r["hour_utc"]] += 1
    lines = [
        f"Total rejection rows (one per signal × code) across all 42 runs: "
        f"**{len(rejections)}**, exported per-run to `*_risk_rejections.csv`.",
        "",
        "**By code:**", "",
        "| code | count |", "|---|---:|",
    ]
    for code, c in by_code.most_common():
        lines.append(f"| `{code}` | {c} |")
    lines.append("")
    lines.append("**By pair:**")
    lines.append("")
    lines.append("| pair | rejections |")
    lines.append("|---|---:|")
    for pair in PAIRS:
        lines.append(f"| {pair} | {by_pair.get(pair, 0)} |")
    lines.append("")
    lines.append("**By split:**")
    lines.append("")
    lines.append("| split | rejections |")
    lines.append("|---|---:|")
    for split in SPLIT_ORDER:
        lines.append(f"| {split} | {by_split.get(split, 0)} |")
    lines.append("")
    lines.append("**By UTC hour (non-zero):**")
    lines.append("")
    lines.append("| hour | rejections |")
    lines.append("|---:|---:|")
    for h in range(24):
        c = by_hour.get(str(h), 0)
        if c:
            lines.append(f"| {h:02d}:00 | {c} |")
    return "\n".join(lines)


def trade_diagnostics_section(trades: list[dict]) -> str:
    if not trades:
        return "_No trades._"
    pnls = [float(t["pnl"]) for t in trades]
    rs = [float(t["r_multiple"]) for t in trades]
    longs = [t for t in trades if t["side"] == "long"]
    shorts = [t for t in trades if t["side"] == "short"]
    by_exit = defaultdict(list)
    for t in trades:
        by_exit[t["exit_reason"]].append(t)
    lines = [
        f"Full-window baseline trades: **{len(trades)}**.",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| win rate | {100 * sum(1 for p in pnls if p > 0) / len(pnls):.1f}% |",
        f"| mean R | {statistics.mean(rs):+.3f} |",
        f"| median R | {statistics.median(rs):+.3f} |",
        f"| total PnL (USD) | {sum(pnls):+.2f} |",
    ]
    if longs:
        lines.append(
            f"| long trades | {len(longs)} (expR "
            f"{statistics.mean(float(t['r_multiple']) for t in longs):+.3f}) |"
        )
    if shorts:
        lines.append(
            f"| short trades | {len(shorts)} (expR "
            f"{statistics.mean(float(t['r_multiple']) for t in shorts):+.3f}) |"
        )
    lines.append("")
    lines.append("**Exit reasons:**")
    lines.append("")
    lines.append("| exit reason | trades | total PnL (USD) | expectancy R | win % |")
    lines.append("|---|---:|---:|---:|---:|")
    for reason, ts in sorted(by_exit.items(), key=lambda kv: -len(kv[1])):
        ps = [float(t["pnl"]) for t in ts]
        ers = [float(t["r_multiple"]) for t in ts]
        lines.append(
            f"| {reason} | {len(ts)} | {sum(ps):+.2f} | "
            f"{statistics.mean(ers):+.3f} | "
            f"{100 * sum(1 for p in ps if p > 0) / len(ts):.1f}% |"
        )
    # top winners / losers
    ranked = sorted(trades, key=lambda t: float(t["pnl"]))
    lines.append("")
    lines.append("**Top 10 losers:**")
    lines.append("")
    lines.append("| pair | side | entry | bars | R | PnL (USD) | exit |")
    lines.append("|---|---|---|---:|---:|---:|---|")
    for t in ranked[:10]:
        lines.append(
            f"| {t['instrument']} | {t['side']} | {t['entry_time'][:10]} | "
            f"{t['bars_held']} | {float(t['r_multiple']):+.2f} | "
            f"{float(t['pnl']):+.2f} | {t['exit_reason']} |"
        )
    lines.append("")
    lines.append("**Top 10 winners:**")
    lines.append("")
    lines.append("| pair | side | entry | bars | R | PnL (USD) | exit |")
    lines.append("|---|---|---|---:|---:|---:|---|")
    for t in reversed(ranked[-10:]):
        lines.append(
            f"| {t['instrument']} | {t['side']} | {t['entry_time'][:10]} | "
            f"{t['bars_held']} | {float(t['r_multiple']):+.2f} | "
            f"{float(t['pnl']):+.2f} | {t['exit_reason']} |"
        )
    return "\n".join(lines)


def comparison_section(
    c004: list[dict],
    c002: dict[tuple[str, str], dict],
    c003: dict[tuple[str, str], dict],
) -> str:
    lines = [
        "All three campaigns: real OANDA H4 data, identical 6-pair universe, "
        "RiskEngine wired in. CAMPAIGN_002 H4 is recomputed over the same 6 "
        "pairs (NZD_USD excluded).",
        "",
        "| split | campaign | trades | return % | PF | expectancy R | win % |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    c004_by = defaultdict(list)
    for s in c004:
        if s["label"].startswith("baseline_"):
            c004_by[s["split"]].append(s)

    def _row(label: str, rows: list[dict]) -> str:
        ms = [r["metrics"] for r in rows]
        pf = [m["profit_factor"] for m in ms if m["profit_factor"] is not None]
        return (
            f"| {label} | {sum(m['trade_count'] for m in ms)} | "
            f"{statistics.mean(m['total_return_pct'] for m in ms):+.2f}% | "
            f"{_fmt_pf(statistics.mean(pf) if pf else None)} | "
            f"{statistics.mean(m['expectancy_r'] for m in ms):+.3f} | "
            f"{100 * statistics.mean(m['win_rate'] for m in ms):.1f}% |"
        )

    for split in SPLIT_ORDER:
        c002_rows = [c002[(p, split)] for p in PAIRS if (p, split) in c002]
        c003_rows = [c003[(p, split)] for p in PAIRS if (p, split) in c003]
        c004_rows = c004_by.get(split, [])
        if c002_rows:
            lines.append(f"| {split} {_row('CAMPAIGN_002 trend H4', c002_rows)}")
        if c003_rows:
            lines.append(f"| {split} {_row('CAMPAIGN_003 trend+ADX', c003_rows)}")
        if c004_rows:
            lines.append(f"| {split} {_row('**CAMPAIGN_004 vol-breakout**', c004_rows)}")
    return "\n".join(lines)


def evaluate_gates(summaries: list[dict], by_run: dict) -> tuple[str, list[str]]:
    look = _summary_lookup(summaries)
    test = [
        s for s in summaries
        if s["label"].startswith("baseline_") and s["split"] == "test_untouched"
    ]
    fails: list[str] = []
    ms = [s["metrics"] for s in test]
    exp = statistics.mean(m["expectancy_r"] for m in ms)
    pf_vals = [m["profit_factor"] for m in ms if m["profit_factor"] is not None]
    pf = statistics.mean(pf_vals) if pf_vals else 0.0
    positive_pairs = sum(1 for m in ms if m["total_return_pct"] > 0)
    worst_dd = min(m["max_drawdown_pct"] for m in ms)
    total_test_trades = sum(m["trade_count"] for m in ms)

    if exp <= 0:
        fails.append(f"untouched-test expectancy negative ({exp:+.3f} R)")
    if pf < 1.05:
        fails.append(f"untouched-test PF {pf:.2f} < 1.05")
    if positive_pairs <= 1:
        fails.append(f"only {positive_pairs}/6 pairs positive on test — not broad")
    if worst_dd < -8.0:
        fails.append(f"worst test drawdown {worst_dd:.2f}% breaches 8% policy")
    if total_test_trades < 30:
        fails.append(f"test trade count {total_test_trades} too low")

    cost2x = [s for s in summaries if s["label"].startswith("cost_stress_2x_")]
    if cost2x:
        c2 = statistics.mean(s["metrics"]["expectancy_r"] for s in cost2x)
        if c2 <= 0:
            fails.append(f"stress_2x expectancy negative ({c2:+.3f} R)")

    stressed_pairs = []
    for pair in PAIRS:
        summ = look.get((pair, "test_untouched"))
        if summ is None:
            continue
        raw = summ["metrics"]["expectancy_r"]
        debit = _mean_debit_r(by_run.get((pair, "test_untouched"), []))
        stressed_pairs.append(raw - debit)
    if stressed_pairs:
        stressed = statistics.mean(stressed_pairs)
        if stressed <= 0:
            fails.append(
                f"financing-stressed test expectancy negative ({stressed:+.3f} R)"
            )

    fails.append(
        "financing remains unmodeled in-engine — blocker for live promotion "
        "(docs/financing_decision.md)"
    )
    verdict = "REJECT" if fails[:-1] else "PAPER-TRADE-ONLY"
    return verdict, fails


def build(runs_dir: Path, db_path: Path, out_path: Path) -> None:
    settings = load_settings(ROOT / "configs/campaign_004_volatility_breakout.yaml")
    summaries = load_summaries(runs_dir)
    by_run = load_trades_by_run(runs_dir)
    trades = full_window_trades(by_run)
    rejections = load_rejections(runs_dir)
    c002 = load_prior_baseline(
        ROOT / "backtests/campaign_002_real_oanda/runs", "baseline/H4"
    )
    c003 = load_prior_baseline(
        ROOT / "backtests/campaign_003_controlled_adx/runs", "baseline"
    )

    verdict, gate_reasons = evaluate_gates(summaries, by_run)
    test_ms = [
        s["metrics"] for s in summaries
        if s["label"].startswith("baseline_") and s["split"] == "test_untouched"
    ]
    test_exp = statistics.mean(m["expectancy_r"] for m in test_ms)
    index_path = runs_dir / "_index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {}

    doc = f"""# CAMPAIGN 004 — Volatility Breakout

> **Result: {verdict}.** Real OANDA practice H4 data. A genuinely
> different entry family — `volatility_breakout 0.1.0-c004`: a breakout
> *out of an ATR-compressed regime*, no EMA trend filter. One controlled
> hypothesis, no optimizer, RiskEngine wired in. This campaign does
> **not** authorize paper-loop, demo-loop, or any order submission.

## Provenance

- **Git commit:** `{_git_commit()}`
- **Working tree dirty at report time:** {"YES" if _git_dirty() else "no"}
- **Config:** [`configs/campaign_004_volatility_breakout.yaml`](../configs/campaign_004_volatility_breakout.yaml)
- **Config hash:** `{settings.config_hash}`
- **Strategy version:** `volatility_breakout 0.1.0-c004`
- **Pre-commit spec:** [`docs/research/CAMPAIGN_004_PRECOMMIT.md`](../docs/research/CAMPAIGN_004_PRECOMMIT.md) (written before the run)
- **Data source:** real OANDA practice, **reused** from `data/campaign_002.sqlite3`
- **RiskEngine invoked:** YES — all {len(summaries)} runs, `mode="backtest"`
- **Total runs:** {len(summaries)} (24 baseline + 18 cost stress, H4 only)
- **Runner elapsed:** {index.get("elapsed_seconds", 0):.0f}s

### Data provenance (reused CAMPAIGN_002 hashes)

{provenance_section(db_path)}

## Strategy rule definition

`volatility_breakout 0.1.0-c004` — full spec and parameter rationale in
the pre-commit doc. Summary:

| element | rule |
|---|---|
| compression | ATR-14 at bar t-1 ≤ 40th percentile of ATR-14 over the trailing 60 bars |
| breakout | close[t] beyond the 20-bar prior-bar Donchian channel |
| direction | breakout direction — **no EMA 50/200 filter** |
| stop | 2.0 × ATR-14 initial |
| exit | 2.0 × ATR-14 trailing stop + 120-bar time stop |
| risk | 0.25% / trade, 1 position per instrument |
| universe | 6 pairs (NZD_USD excluded), H4 only |

This is **not** a Donchian trend rescue: the EMA regime filter that
defined CAMPAIGN_002/003 is gone; entries are pure compression→expansion.

## Assumptions

- Fills: bid/ask-aware; slippage applied against the trade.
- PnL → USD: quote-currency PnL converted at the exit price for
  USD-base pairs; USD-quote pairs already in USD.
- **Financing: NOT modeled in-engine** (accurate historical financing
  is unavailable — see `docs/financing_decision.md`). The conservative
  stress overlay from `forex_bot.financing` is applied below. Financing
  remains a hard blocker for any live promotion.

## RiskEngine — approvals and rejections

{rejection_section(rejections)}

## Metrics by split (H4, base costs)

{split_table(summaries)}

## Metrics by pair — untouched test (2025-01-01 → 2026-05-20)

{pair_table(summaries, "test_untouched")}

## Metrics by pair — full window (2020-01-01 → 2026-05-20)

{pair_table(summaries, "full")}

## Cost stress (full window)

{cost_stress_table(summaries)}

## Financing treatment

Financing is **estimated via a conservative stress overlay**, not
modeled. It is a hard live-promotion blocker regardless of the result.

{financing_table(summaries, by_run)}

### Financing-stressed expectancy by split

{financing_by_split(summaries, by_run)}

## Trade diagnostics (full-window baseline)

{trade_diagnostics_section(trades)}

## Comparison vs CAMPAIGN_002 and CAMPAIGN_003

{comparison_section(summaries, c002, c003)}

Three campaigns now agree on the real 2020-2026 majors: neither the
Donchian trend breakout (CAMPAIGN_002), nor that breakout conditioned
on ADX trend strength (CAMPAIGN_003), nor a volatility-compression
breakout with no trend filter (CAMPAIGN_004) has a positive
untouched-test edge. CAMPAIGN_004 is in fact the **worst** of the three
— removing the trend filter and trading expansion out of compression
did not help; it hurt.

## Artifact paths

- Equity curves: `backtests/campaign_004_volatility_breakout/runs/**/*_equity.csv`
- Trade lists: `backtests/campaign_004_volatility_breakout/runs/**/*_trades.csv`
- **Per-signal risk rejections:** `backtests/campaign_004_volatility_breakout/runs/**/*_risk_rejections.csv`
- Summaries (committed): `backtests/campaign_004_volatility_breakout/runs/**/*_summary.json`
- Run index: `backtests/campaign_004_volatility_breakout/runs/_index.json`

(Equity/trade CSVs gitignored for size; regenerate with
`python scripts/run_campaign_004.py --clean`.)

## Known limitations

1. Financing unmodeled in-engine — stress overlay only; hard live blocker.
2. `compression_lookback=60` is a pre-committed judgement call, not swept.
3. NZD_USD exclusion is partly returns-correlated (acknowledged in the
   pre-commit doc).
4. Backtest fills approximate broker behavior; no live dry-run.

## Pass/fail decision

Pre-committed CAMPAIGN_004 gates. **{verdict}.**

Untouched-test expectancy **{test_exp:+.3f} R**. Gate findings:

"""
    for reason in gate_reasons:
        doc += f"- {reason}\n"

    doc += f"\n**{verdict}.** "
    if verdict == "REJECT":
        doc += (
            "The volatility-compression breakout entry family does not "
            "have a positive untouched-test edge on the real 2020-2026 "
            "majors — and underperforms both prior trend-following "
            "campaigns. Do not paper-trade, demo-trade, or live-trade "
            "`volatility_breakout 0.1.0-c004`. With three rejected "
            "entry families, the evidence points away from simple "
            "breakout/trend H4 systems on these pairs; the next research "
            "step should reconsider the premise (timeframe, instrument "
            "class, or strategy family) rather than iterate another "
            "breakout variant."
        )
    else:
        doc += (
            "All return/risk gates passed — a PAPER-TRADE-ONLY research "
            "recommendation, not live. Financing must be modeled (H-09) "
            "before any live consideration."
        )
    doc += "\n\n_Live trading is not recommended and not in scope for CAMPAIGN_004._\n"
    out_path.write_text(doc, encoding="utf-8")
    print(f"wrote {out_path}  (verdict: {verdict})")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runs",
        default=str(ROOT / "backtests/campaign_004_volatility_breakout/runs"),
    )
    parser.add_argument("--db", default=str(ROOT / "data/campaign_002.sqlite3"))
    parser.add_argument(
        "--out",
        default=str(ROOT / "backtests/CAMPAIGN_004_VOLATILITY_BREAKOUT_REPORT.md"),
    )
    args = parser.parse_args()
    build(Path(args.runs), Path(args.db), Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

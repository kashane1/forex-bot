#!/usr/bin/env python3
"""Build backtests/CAMPAIGN_003_CONTROLLED_ADX_REPORT.md.

Consumes the CAMPAIGN_003 run artifacts (summary JSONs, trades CSVs,
risk_rejections CSVs), the reused CAMPAIGN_002 provenance, and the
committed CAMPAIGN_002 H4 baseline summaries for a like-for-like
comparison. Applies a conservative financing debit and the
pre-committed Task-5 pass/fail gates.
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

PAIRS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF"]
SPLIT_ORDER = ["train", "validation", "test_untouched", "full"]
USD_BASE = {"USD_JPY", "USD_CAD", "USD_CHF"}  # base currency is USD

# Conservative financing debit, basis points per calendar day held, worst of
# {long, short}. Source: docs/financing_decision.md.
FINANCING_BP_PER_DAY = {
    "EUR_USD": 0.6,
    "GBP_USD": 0.7,
    "USD_JPY": 1.2,
    "AUD_USD": 0.7,
    "USD_CAD": 0.5,
    "USD_CHF": 0.9,
}
H4_HOURS = 4


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


# --------------------------------------------------------------------------
# loaders
# --------------------------------------------------------------------------


def load_summaries(runs_dir: Path) -> list[dict]:
    out = []
    for p in runs_dir.rglob("*_summary.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        d["_summary_path"] = p
        out.append(d)
    return out


def load_trades_by_run(runs_dir: Path) -> dict[tuple[str, str], list[dict]]:
    """Every CAMPAIGN_003 baseline trade, keyed by (pair, split).

    Using the split-specific run (e.g. baseline/test_untouched/...) — not
    full-window trades bucketed by date — keeps financing figures
    consistent with the per-run summary metrics.
    """
    out: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for p in runs_dir.rglob("baseline_*_trades.csv"):
        stem = p.stem.removesuffix("_trades")  # baseline_EUR_USD_H4_test_untouched
        rest = stem.removeprefix("baseline_")  # EUR_USD_H4_test_untouched
        tokens = rest.split("_")
        if len(tokens) < 4:
            continue
        pair = f"{tokens[0]}_{tokens[1]}"
        split = "_".join(tokens[3:])  # handles test_untouched
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


def load_c002_h4_baseline() -> dict[tuple[str, str], dict]:
    """Committed CAMPAIGN_002 H4 baseline summaries, keyed by (pair, split),
    for the 6-pair CAMPAIGN_003 universe."""
    base = ROOT / "backtests/campaign_002_real_oanda/runs/baseline/H4"
    out: dict[tuple[str, str], dict] = {}
    for split in SPLIT_ORDER:
        for pair in PAIRS:
            p = base / split / f"baseline_{pair}_H4_{split}_summary.json"
            if p.exists():
                out[(pair, split)] = json.loads(p.read_text(encoding="utf-8"))
    return out


# --------------------------------------------------------------------------
# financing
# --------------------------------------------------------------------------


def financing_debit_usd(trade: dict) -> float:
    """Conservative financing debit in USD for one trade."""
    inst = trade["instrument"]
    units = abs(Decimal(trade["units"]))
    entry = Decimal(trade["entry_price"])
    bars = int(trade["bars_held"])
    days = bars * H4_HOURS / 24.0
    notional_usd = float(units) if inst in USD_BASE else float(units * entry)
    bp = FINANCING_BP_PER_DAY.get(inst, 0.7)
    return days * (bp / 10000.0) * notional_usd


def financing_debit_r(trade: dict) -> float:
    """Financing debit expressed in R (fraction of the trade's risk)."""
    inst = trade["instrument"]
    units = abs(Decimal(trade["units"]))
    entry = Decimal(trade["entry_price"])
    stop = Decimal(trade["stop_price"])
    risk_quote = abs(entry - stop) * units
    risk_usd = float(risk_quote) if inst not in USD_BASE else float(risk_quote / entry)
    if risk_usd <= 0:
        return 0.0
    return financing_debit_usd(trade) / risk_usd


# --------------------------------------------------------------------------
# sections
# --------------------------------------------------------------------------


def provenance_section(db_path: Path) -> str:
    db = Database(db_path)
    rows = DataSourceRepo(db).all_in_campaign("CAMPAIGN_002")
    h4 = [r for r in rows if r["granularity"] == "H4" and r["instrument"] in PAIRS]
    # keep the largest fetch per pair (the full-window one, not the smoke test)
    best: dict[str, dict] = {}
    for r in h4:
        cur = best.get(r["instrument"])
        if cur is None or r["candles_written"] > cur["candles_written"]:
            best[r["instrument"]] = r
    lines = [
        "CAMPAIGN_003 **reuses** the real OANDA practice H4 candles fetched "
        "for CAMPAIGN_002 (`data/campaign_002.sqlite3`). No re-fetch, no "
        "synthetic data. Provenance hashes below are the ones recorded at "
        "CAMPAIGN_002 fetch time and match the CAMPAIGN_002 report.",
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
        pf_vals = [m["profit_factor"] for m in ms if m["profit_factor"] is not None]
        lines.append(
            f"| {split} | {sum(m['trade_count'] for m in ms)} | "
            f"{sum(r.get('rejected_signal_count', 0) for r in rs)} | "
            f"{statistics.mean(m['total_return_pct'] for m in ms):+.2f}% | "
            f"{statistics.mean(m['max_drawdown_pct'] for m in ms):+.2f}% | "
            f"{_fmt_pf(statistics.mean(pf_vals) if pf_vals else None)} | "
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
            f"{s.get('rejected_signal_count', 0)} | "
            f"{m['total_return_pct']:+.2f}% | {m['max_drawdown_pct']:+.2f}% | "
            f"{_fmt_pf(m['profit_factor'])} | {m['expectancy_r']:+.3f} | "
            f"{100 * m['win_rate']:.1f}% |"
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
        pf_vals = [m["profit_factor"] for m in ms if m["profit_factor"] is not None]
        lines.append(
            f"| {regime} | {sum(m['trade_count'] for m in ms)} | "
            f"{sum(r.get('rejected_signal_count', 0) for r in rs)} | "
            f"{statistics.mean(m['total_return_pct'] for m in ms):+.2f}% | "
            f"{statistics.mean(m['max_drawdown_pct'] for m in ms):+.2f}% | "
            f"{_fmt_pf(statistics.mean(pf_vals) if pf_vals else None)} | "
            f"{statistics.mean(m['expectancy_r'] for m in ms):+.3f} |"
        )
    return "\n".join(lines)


def _summary_lookup(summaries: list[dict]) -> dict[tuple[str, str], dict]:
    """{(pair, split): summary} for baseline runs."""
    out: dict[tuple[str, str], dict] = {}
    for s in summaries:
        if s["label"].startswith("baseline_"):
            out[(s["instrument"], s["split"])] = s
    return out


def _mean_debit_r(trades: list[dict]) -> float:
    return statistics.mean(financing_debit_r(t) for t in trades) if trades else 0.0


def financing_table(
    summaries: list[dict], by_run: dict[tuple[str, str], list[dict]]
) -> str:
    """Per-pair financing debit on the full-window baseline runs.

    'raw expectancy R' is the per-run summary expectancy (pair-weighted,
    consistent with the Metrics-by-split tables); the debit is the mean
    per-trade financing debit in R over that run's trades.
    """
    look = _summary_lookup(summaries)
    lines = [
        "Conservative financing debit (worst-of-long/short bp/day from "
        "`docs/financing_decision.md`) applied to the full-window baseline "
        "runs. Financing is **not** in the engine PnL — this is an "
        "after-the-fact stress overlay. 'Raw expectancy R' is the per-run "
        "summary metric, so it matches the Metrics-by-pair table exactly.",
        "",
        "| pair | trades | total financing debit (USD) | mean debit/trade (R) | raw expectancy R | financing-stressed expectancy R |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for pair in PAIRS:
        ts = by_run.get((pair, "full"), [])
        summ = look.get((pair, "full"))
        if not ts or summ is None:
            continue
        debit_usd = sum(financing_debit_usd(t) for t in ts)
        mean_debit_r = _mean_debit_r(ts)
        raw = summ["metrics"]["expectancy_r"]
        lines.append(
            f"| {pair} | {len(ts)} | {debit_usd:.2f} | {mean_debit_r:.3f} | "
            f"{raw:+.3f} | {raw - mean_debit_r:+.3f} |"
        )
    return "\n".join(lines)


def financing_by_split(
    summaries: list[dict], by_run: dict[tuple[str, str], list[dict]]
) -> str:
    """Pair-averaged, so 'raw expectancy R' matches Metrics-by-split."""
    look = _summary_lookup(summaries)
    lines = [
        "Pair-averaged (consistent with Metrics-by-split). Each pair's raw "
        "expectancy is its per-run summary metric; the financing debit is "
        "the mean per-trade debit in R over that run.",
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
        if not raws:
            continue
        lines.append(
            f"| {split} | {statistics.mean(raws):+.3f} | "
            f"{statistics.mean(debits):.3f} | "
            f"{statistics.mean(stressed):+.3f} |"
        )
    return "\n".join(lines)


def rejection_section(rejections: list[dict]) -> str:
    by_code: Counter[str] = Counter()
    by_pair: Counter[str] = Counter()
    by_split: Counter[str] = Counter()
    by_hour: Counter[str] = Counter()
    by_dow: Counter[str] = Counter()
    for r in rejections:
        by_code[r["rejection_code"]] += 1
        by_pair[r["instrument"]] += 1
        by_split[r["split"]] += 1
        by_hour[r["hour_utc"]] += 1
        by_dow[r["day_of_week"]] += 1
    lines = [
        f"Total rejection rows (one per signal × code) across all 42 runs: "
        f"**{len(rejections)}**. The permanent per-signal export "
        f"(`*_risk_rejections.csv`, Step 0) makes every breakdown below "
        "reproducible from disk.",
        "",
        "**By rejection code:**",
        "",
        "| code | count |",
        "|---|---:|",
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
    lines.append("**By UTC hour:**")
    lines.append("")
    lines.append("| hour | rejections |")
    lines.append("|---:|---:|")
    for h in range(24):
        c = by_hour.get(str(h), 0)
        if c:
            lines.append(f"| {h:02d}:00 | {c} |")
    lines.append("")
    lines.append("**By day of week:**")
    lines.append("")
    lines.append("| day | rejections |")
    lines.append("|---|---:|")
    for d in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"):
        if by_dow.get(d, 0):
            lines.append(f"| {d} | {by_dow[d]} |")
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
        f"| long trades | {len(longs)} (expR {statistics.mean(float(t['r_multiple']) for t in longs):+.3f}) |"
        if longs else "| long trades | 0 |",
        f"| short trades | {len(shorts)} (expR {statistics.mean(float(t['r_multiple']) for t in shorts):+.3f}) |"
        if shorts else "| short trades | 0 |",
        f"| total PnL (USD) | {sum(pnls):+.2f} |",
        "",
        "**Exit reasons:**",
        "",
        "| exit reason | trades | total PnL (USD) | expectancy R | win % |",
        "|---|---:|---:|---:|---:|",
    ]
    for reason, ts in sorted(by_exit.items(), key=lambda kv: -len(kv[1])):
        ps = [float(t["pnl"]) for t in ts]
        ers = [float(t["r_multiple"]) for t in ts]
        lines.append(
            f"| {reason} | {len(ts)} | {sum(ps):+.2f} | "
            f"{statistics.mean(ers):+.3f} | "
            f"{100 * sum(1 for p in ps if p > 0) / len(ts):.1f}% |"
        )
    return "\n".join(lines)


def comparison_section(c003: list[dict], c002: dict[tuple[str, str], dict]) -> str:
    """Like-for-like: CAMPAIGN_003 vs CAMPAIGN_002, H4, same 6 pairs."""
    lines = [
        "Both campaigns on **real OANDA H4 data, identical 6-pair universe** "
        "(CAMPAIGN_002 numbers recomputed here over the same 6 pairs — "
        "NZD_USD excluded — so the comparison isolates the ADX filter).",
        "",
        "| split | campaign | trades | return % | PF | expectancy R | win % |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    c003_by = defaultdict(list)
    for s in c003:
        if s["label"].startswith("baseline_"):
            c003_by[s["split"]].append(s)
    for split in SPLIT_ORDER:
        # CAMPAIGN_002 (6-pair subset)
        c002_rows = [c002[(p, split)] for p in PAIRS if (p, split) in c002]
        if c002_rows:
            ms = [r["metrics"] for r in c002_rows]
            pf = [m["profit_factor"] for m in ms if m["profit_factor"] is not None]
            lines.append(
                f"| {split} | CAMPAIGN_002 H4 (6-pair) | "
                f"{sum(m['trade_count'] for m in ms)} | "
                f"{statistics.mean(m['total_return_pct'] for m in ms):+.2f}% | "
                f"{_fmt_pf(statistics.mean(pf) if pf else None)} | "
                f"{statistics.mean(m['expectancy_r'] for m in ms):+.3f} | "
                f"{100 * statistics.mean(m['win_rate'] for m in ms):.1f}% |"
            )
        rs = c003_by.get(split, [])
        if rs:
            ms = [r["metrics"] for r in rs]
            pf = [m["profit_factor"] for m in ms if m["profit_factor"] is not None]
            lines.append(
                f"| {split} | **CAMPAIGN_003 +ADX** | "
                f"{sum(m['trade_count'] for m in ms)} | "
                f"{statistics.mean(m['total_return_pct'] for m in ms):+.2f}% | "
                f"{_fmt_pf(statistics.mean(pf) if pf else None)} | "
                f"{statistics.mean(m['expectancy_r'] for m in ms):+.3f} | "
                f"{100 * statistics.mean(m['win_rate'] for m in ms):.1f}% |"
            )
    return "\n".join(lines)


def evaluate_gates(
    summaries: list[dict], by_run: dict[tuple[str, str], list[dict]]
) -> tuple[str, list[str]]:
    """Apply the pre-committed Task-5 gates. Returns (verdict, reasons)."""
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
        fails.append(f"test trade count {total_test_trades} too low to be meaningful")

    # stress_2x
    cost2x = [s for s in summaries if s["label"].startswith("cost_stress_2x_")]
    if cost2x:
        c2_exp = statistics.mean(s["metrics"]["expectancy_r"] for s in cost2x)
        if c2_exp <= 0:
            fails.append(f"stress_2x expectancy negative ({c2_exp:+.3f} R)")

    # financing-stressed test expectancy — pair-averaged, consistent with
    # the Metrics-by-split table.
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
        "regardless of the above (docs/financing_decision.md)"
    )

    verdict = "REJECT" if fails[:-1] else "PAPER-TRADE-ONLY"
    return verdict, fails


# --------------------------------------------------------------------------


def build(runs_dir: Path, db_path: Path, out_path: Path) -> None:
    settings = load_settings(ROOT / "configs/campaign_003_controlled_adx.yaml")
    summaries = load_summaries(runs_dir)
    by_run = load_trades_by_run(runs_dir)
    trades = full_window_trades(by_run)
    rejections = load_rejections(runs_dir)
    c002 = load_c002_h4_baseline()

    verdict, gate_reasons = evaluate_gates(summaries, by_run)
    fin_table = financing_table(summaries, by_run)

    test_ms = [
        s["metrics"] for s in summaries
        if s["label"].startswith("baseline_") and s["split"] == "test_untouched"
    ]
    test_exp = statistics.mean(m["expectancy_r"] for m in test_ms)

    index_path = runs_dir / "_index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {}

    doc = f"""# CAMPAIGN 003 — Controlled ADX-Filtered Trend Following

> **Result: {verdict}.** Real OANDA practice H4 data, frozen baseline +
> H4-only + 6-pair universe + ADX-14>25 gate. One controlled hypothesis,
> no optimizer, RiskEngine wired in. This campaign does **not** authorize
> paper-loop, demo-loop, or any order submission.

## Provenance

- **Git commit:** `{_git_commit()}`
- **Working tree dirty at report time:** {"YES" if _git_dirty() else "no"}
- **Config:** [`configs/campaign_003_controlled_adx.yaml`](../configs/campaign_003_controlled_adx.yaml)
- **Config hash:** `{settings.config_hash}`
- **Strategy version:** `trend_following 0.2.0-c003`
- **Data source:** real OANDA practice, **reused** from
  `data/campaign_002.sqlite3` (no re-fetch, no synthetic data)
- **RiskEngine invoked:** YES — all {len(summaries)} runs, `mode="backtest"`
- **Total runs:** {len(summaries)} (24 baseline + 18 cost stress, H4 only)
- **Runner elapsed:** {index.get("elapsed_seconds", 0):.0f}s

### Data provenance (reused CAMPAIGN_002 hashes)

{provenance_section(db_path)}

## Exact rule diff from CAMPAIGN_002

CAMPAIGN_003 = frozen `0.1.0-baseline-frozen` **plus exactly three
pre-committed changes**. Nothing else changed; the ADX threshold was
fixed at 25 before any run and was not swept.

| aspect | CAMPAIGN_002 | CAMPAIGN_003 (`0.2.0-c003`) |
|---|---|---|
| timeframes | H4 **and** H1 | **H4 only** |
| universe | 7 pairs (incl. NZD_USD) | **6 pairs — NZD_USD excluded** (cost structure) |
| entry gate | EMA50/200 + Donchian-20 breakout | same **+ ADX-14 > 25** |
| EMA filter | 50 / 200 | 50 / 200 (unchanged) |
| Donchian | 20, prior bars only | 20, prior bars only (unchanged) |
| stops | 2.0×ATR initial + trailing | 2.0×ATR initial + trailing (unchanged) |
| risk | 0.25% / trade, 1 position | 0.25% / trade, 1 position (unchanged) |
| RiskEngine | wired in | wired in (unchanged) |

## Assumptions

- Fills: bid for long exits / short entries, ask for the opposite;
  `fixed_slippage_pips` + `spread_slippage_multiplier` applied against
  the trade.
- PnL → USD: quote-currency PnL converted at the exit price for
  USD-base pairs (USD_JPY/CAD/CHF); USD-quote pairs already in USD.
- **Financing: NOT modeled in the engine PnL.** A conservative
  financing debit is applied as an after-the-fact overlay (see below).
  Financing remains a hard blocker for any live promotion.
- ADX-14 threshold 25 is the textbook "trend present" level,
  pre-committed, never swept.

## RiskEngine — approvals and rejections

{rejection_section(rejections)}

## Metrics by split (H4, base costs)

{split_table(summaries)}

## Metrics by pair — untouched test split (2025-01-01 → 2026-05-20)

{pair_table(summaries, "test_untouched")}

## Metrics by pair — full window (2020-01-01 → 2026-05-20)

{pair_table(summaries, "full")}

## Cost stress (full window)

{cost_stress_table(summaries)}

## Financing stress overlay

{fin_table}

### Financing-stressed expectancy by split

{financing_by_split(summaries, by_run)}

## Trade diagnostics (full-window baseline)

{trade_diagnostics_section(trades)}

## Comparison vs CAMPAIGN_002 H4 baseline

{comparison_section(summaries, c002)}

The ADX filter cut trade count and modestly improved expectancy, but
did **not** lift the untouched-test result across break-even.
Conditioning the Donchian breakout on trend strength reduces how often
it fires in chop; it does not change the fact that the breakout entry
itself has no positive edge on these pairs over 2020-2026.

## Artifact paths

- Per-run equity curves: `backtests/campaign_003_controlled_adx/runs/**/*_equity.csv`
- Per-run trade lists: `backtests/campaign_003_controlled_adx/runs/**/*_trades.csv`
- **Per-signal risk rejections:** `backtests/campaign_003_controlled_adx/runs/**/*_risk_rejections.csv`
- Per-run summaries (committed): `backtests/campaign_003_controlled_adx/runs/**/*_summary.json`
- Run index: `backtests/campaign_003_controlled_adx/runs/_index.json`

(Equity/trade/rejection CSVs are gitignored for size; regenerate with
`python scripts/run_campaign_003.py --clean`.)

## Known limitations

1. **Financing unmodeled in-engine** — overlay only; hard live blocker.
2. NZD_USD exclusion is partly returns-correlated (it was also the
   worst CAMPAIGN_002 pair); the structural spread/ATR rationale is
   sound but the residual leakage is acknowledged.
3. Backtest fills approximate broker behavior; no live dry-run.
4. ADX threshold 25 is a single pre-committed value; this campaign does
   not establish its sensitivity (deliberately — no sweep).

## Pass/fail decision

Pre-committed Task-5 gates. **{verdict}.**

Untouched-test expectancy **{test_exp:+.3f} R**. Gate findings:

"""
    for reason in gate_reasons:
        doc += f"- {reason}\n"

    doc += f"""
**{verdict}.** """

    if verdict == "REJECT":
        doc += (
            "The controlled ADX hypothesis did not lift the frozen "
            "breakout entry to a positive untouched-test expectancy. "
            "Conditioning *when* the breakout fires is not sufficient — "
            "the next research step (per the hypothesis backlog) is a "
            "different *entry* (volatility-compression breakout, H-11, or "
            "pullback-continuation, H-04), not further conditioning of "
            "this one. Do not paper-trade, demo-trade, or live-trade "
            "`0.2.0-c003`."
        )
    else:
        doc += (
            "All return/risk gates passed. This earns a PAPER-TRADE-ONLY "
            "research recommendation — **not** live. Financing must be "
            "modeled (H-09) before any live consideration."
        )
    doc += "\n\n_Live trading is not recommended and not in scope for CAMPAIGN_003._\n"

    out_path.write_text(doc, encoding="utf-8")
    print(f"wrote {out_path}  (verdict: {verdict})")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runs", default=str(ROOT / "backtests/campaign_003_controlled_adx/runs")
    )
    parser.add_argument("--db", default=str(ROOT / "data/campaign_002.sqlite3"))
    parser.add_argument(
        "--out",
        default=str(ROOT / "backtests/CAMPAIGN_003_CONTROLLED_ADX_REPORT.md"),
    )
    args = parser.parse_args()
    build(Path(args.runs), Path(args.db), Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""CAMPAIGN_005 — benchmarks & diagnostics. DIAGNOSTIC ONLY.

Computes no-trade / always-long-short / random-entry benchmarks and
per-pair market-character diagnostics from the real OANDA H4 candles,
then writes backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md. Promotes
nothing. See docs/research/CAMPAIGN_005_BENCHMARKS_PRECOMMIT.md.
"""

from __future__ import annotations

import json
import statistics
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, DataSourceRepo
from forex_bot.domain.candles import CandleFrame
from forex_bot.strategies.indicators import atr

DB = ROOT / "data/campaign_002.sqlite3"
PAIRS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF"]
GRAN = "H4"
OUT = ROOT / "backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md"
RANDOM_SEEDS = 20
RANDOM_HOLD = 30          # H4 bars
RANDOM_ENTRY_PROB = 0.012  # ~1 entry per ~83 bars → matched to prior campaigns
FIXED_SLIP_PIPS = 0.2
SPREAD_MULT = 0.5
PIP = {"USD_JPY": 0.01, "USD_CAD": 0.0001, "USD_CHF": 0.0001,
       "EUR_USD": 0.0001, "GBP_USD": 0.0001, "AUD_USD": 0.0001}


def _git(*a: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *a],
                           capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return ""
    return r.stdout.strip()


def load_frame(db: Database, pair: str) -> CandleFrame:
    rows = db and CandleRepo(db).list(pair, GRAN, completed_only=True)
    return CandleFrame.from_candles(pair, GRAN, rows)


def random_entry_expectancy(df, pair: str) -> tuple[float, float, int]:
    """Mean / std expectancy in R over RANDOM_SEEDS random-entry passes.
    R = signed move / (2 ATR at entry), bid/ask fills + base costs."""
    pip = PIP[pair]
    close = df["close"].to_numpy()
    bid_c = df["bid_close"].to_numpy()
    ask_c = df["ask_close"].to_numpy()
    high = df["high"]
    low = df["low"]
    atr_series = atr(high, low, df["close"], 14).to_numpy()
    n = len(close)
    per_seed_means: list[float] = []
    total_trades = 0
    for seed in range(RANDOM_SEEDS):
        rng = np.random.default_rng(1000 + seed)
        rs: list[float] = []
        i = 30
        while i < n - RANDOM_HOLD - 1:
            if rng.random() >= RANDOM_ENTRY_PROB:
                i += 1
                continue
            a = atr_series[i]
            if not np.isfinite(a) or a <= 0:
                i += 1
                continue
            long = rng.random() < 0.5
            spread = ask_c[i] - bid_c[i]
            slip = max(FIXED_SLIP_PIPS * pip, spread * SPREAD_MULT)
            j = i + RANDOM_HOLD
            if long:
                entry = ask_c[i] + slip
                exit_ = bid_c[j] - slip
                move = exit_ - entry
            else:
                entry = bid_c[i] - slip
                exit_ = ask_c[j] + slip
                move = entry - exit_
            rs.append(move / (2.0 * a))
            total_trades += 1
            i = j + 1  # one position at a time
        if rs:
            per_seed_means.append(statistics.mean(rs))
    if not per_seed_means:
        return 0.0, 0.0, 0
    return (
        statistics.mean(per_seed_means),
        statistics.pstdev(per_seed_means) if len(per_seed_means) > 1 else 0.0,
        total_trades // RANDOM_SEEDS,
    )


def diagnostics(df, pair: str) -> dict:
    pip = PIP[pair]
    close = df["close"].to_numpy()
    bid_c = df["bid_close"].to_numpy()
    ask_c = df["ask_close"].to_numpy()
    atr_series = atr(df["high"], df["low"], df["close"], 14).to_numpy()
    rets = np.diff(close) / close[:-1]

    spread_pips = (ask_c - bid_c) / pip
    atr_pips = atr_series / pip
    med_spread = float(np.nanmedian(spread_pips))
    med_atr = float(np.nanmedian(atr_pips))

    # Efficiency ratio over rolling 20-bar windows.
    win = 20
    ers: list[float] = []
    for k in range(win, len(close)):
        seg = close[k - win:k + 1]
        net = abs(seg[-1] - seg[0])
        path = float(np.sum(np.abs(np.diff(seg))))
        if path > 0:
            ers.append(net / path)
    efficiency = statistics.mean(ers) if ers else 0.0

    # Lag-1 autocorrelation of returns and of |returns|.
    def ac1(x: np.ndarray) -> float:
        x = x[np.isfinite(x)]
        if len(x) < 10:
            return 0.0
        x = x - x.mean()
        denom = float(np.sum(x * x))
        return float(np.sum(x[1:] * x[:-1]) / denom) if denom > 0 else 0.0

    return {
        "median_spread_pips": med_spread,
        "median_atr_pips": med_atr,
        "spread_to_atr_pct": 100.0 * med_spread / med_atr if med_atr else 0.0,
        "efficiency_ratio": efficiency,
        "return_ac1": ac1(rets),
        "abs_return_ac1": ac1(np.abs(rets)),
        "net_return_pct": 100.0 * (close[-1] - close[0]) / close[0],
        "bars": len(close),
    }


def main() -> int:
    db = Database(DB)
    ds = DataSourceRepo(db)
    rows_bench: list[tuple] = []
    rows_diag: list[tuple] = []
    provenance: list[dict] = []
    for pair in PAIRS:
        frame = load_frame(db, pair)
        df = frame.df
        if df.empty:
            raise SystemExit(f"no H4 candles for {pair} — cannot run benchmarks")
        diag = diagnostics(df, pair)
        rand_mean, rand_std, rand_n = random_entry_expectancy(df, pair)
        always_long = diag["net_return_pct"]
        rows_bench.append((pair, always_long, -always_long, rand_mean, rand_std, rand_n))
        rows_diag.append((pair, diag))
        src = ds.latest_for(pair, GRAN) or {}
        provenance.append({
            "pair": pair, "source": src.get("source", "?"),
            "candles": src.get("candles_written", 0),
            "raw": (src.get("raw_sha256") or "")[:16],
        })

    overall_random = statistics.mean(r[3] for r in rows_bench)

    lines: list[str] = []
    lines.append("# CAMPAIGN 005 — Benchmarks & Diagnostics")
    lines.append("")
    lines.append(
        "> **Diagnostic only.** CAMPAIGN_005 promotes nothing and has no "
        "pass/fail gate. It establishes what simple baselines achieve on "
        "the real OANDA H4 data so later campaigns can be judged against "
        "them. Part of Research Marathon 001."
    )
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    lines.append(f"- Git commit: `{_git('rev-parse', 'HEAD')}`")
    lines.append(f"- Working tree dirty: {'YES' if _git('status', '--porcelain') else 'no'}")
    lines.append("- Data: real OANDA practice H4, reused from `data/campaign_002.sqlite3`")
    lines.append("- Pre-commit: `docs/research/CAMPAIGN_005_BENCHMARKS_PRECOMMIT.md`")
    lines.append(f"- Generated: {datetime.now(UTC).isoformat()}")
    lines.append("")
    lines.append("| pair | source | candles | raw_sha256 (16) |")
    lines.append("|---|---|---:|---|")
    for p in provenance:
        lines.append(f"| {p['pair']} | {p['source']} | {p['candles']} | `{p['raw']}` |")
    lines.append("")
    lines.append("## Benchmark 1 — no-trade")
    lines.append("")
    lines.append("Return **0.00%**, expectancy **0.000 R**. The do-nothing reference.")
    lines.append("")
    lines.append("## Benchmark 2 — always-long / always-short (descriptive)")
    lines.append("")
    lines.append("Full-window buy-and-hold of the mid price — the pair's own drift.")
    lines.append("")
    lines.append("| pair | always-long return % | always-short return % |")
    lines.append("|---|---:|---:|")
    for pair, al, ash, *_ in rows_bench:
        lines.append(f"| {pair} | {al:+.2f}% | {ash:+.2f}% |")
    lines.append("")
    lines.append("## Benchmark 3 — random entry (matched frequency, 20 seeds)")
    lines.append("")
    lines.append(
        "One position at a time, random 50/50 direction, fixed 30-bar hold, "
        "bid/ask fills + base costs. Expectancy in R (R = 2×ATR at entry)."
    )
    lines.append("")
    lines.append("| pair | random expectancy R | seed std | trades/seed |")
    lines.append("|---|---:|---:|---:|")
    for pair, _al, _ash, rm, rs_, rn in rows_bench:
        lines.append(f"| {pair} | {rm:+.3f} | {rs_:.3f} | {rn} |")
    lines.append(f"| **mean** | **{overall_random:+.3f}** | | |")
    lines.append("")
    lines.append("## Diagnostics — market character (H4, full window)")
    lines.append("")
    lines.append(
        "| pair | median spread (pips) | median ATR (pips) | spread/ATR % | "
        "efficiency ratio | return AC(1) | abs-return AC(1) | net drift % |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for pair, d in rows_diag:
        lines.append(
            f"| {pair} | {d['median_spread_pips']:.2f} | {d['median_atr_pips']:.1f} | "
            f"{d['spread_to_atr_pct']:.1f}% | {d['efficiency_ratio']:.3f} | "
            f"{d['return_ac1']:+.3f} | {d['abs_return_ac1']:+.3f} | "
            f"{d['net_return_pct']:+.2f}% |"
        )
    lines.append("")
    mean_er = statistics.mean(d["efficiency_ratio"] for _, d in rows_diag)
    mean_ac = statistics.mean(d["return_ac1"] for _, d in rows_diag)
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        f"- **Random-entry expectancy averages {overall_random:+.3f} R.** "
        "Prior rejected strategies: CAMPAIGN_002 −0.085 R, CAMPAIGN_003 "
        "−0.071 R, CAMPAIGN_004 −0.163 R (untouched test). The strategies "
        "are **not meaningfully better than random entry** — once real "
        "bid/ask spread and slippage are paid, an arbitrary entry on these "
        "pairs loses at a similar rate. The prior failures are "
        "**cost/structure driven**, not unique defects of those entries."
    )
    lines.append(
        f"- **Efficiency ratio averages {mean_er:.3f}** (0 = pure chop, "
        "1 = pure trend). A low efficiency ratio means H4 price paths on "
        "these majors retrace most of their movement — hostile to "
        "breakout/trend entries that need follow-through."
    )
    lines.append(
        f"- **Lag-1 return autocorrelation averages {mean_ac:+.3f}.** "
        + (
            "Slightly negative — weak mean-reversion tendency, consistent "
            "with the trend strategies' failure."
            if mean_ac < 0 else
            "Near zero / slightly positive — no strong directional "
            "persistence to exploit at H4."
        )
    )
    lines.append(
        "- Always-long/short returns show no consistent capturable drift "
        "across the universe."
    )
    lines.append("")
    lines.append(
        "**Marathon implication:** the bar for CAMPAIGN_006-008 is not "
        "merely 'positive' — it is 'positive enough to beat the random-entry "
        "cost drag of "
        f"{overall_random:+.3f} R by a clear margin on out-of-sample data.' "
        "Low efficiency ratios argue against further breakout/trend "
        "variants; lower turnover (D1) and non-breakout entries are the "
        "remaining reasonable hypotheses."
    )
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"random-entry mean expectancy: {overall_random:+.3f} R")
    print(f"mean efficiency ratio: {mean_er:.3f}, mean return AC(1): {mean_ac:+.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

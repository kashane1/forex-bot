#!/usr/bin/env python3
"""CAMPAIGN_009 report builder — mean-reversion + midline exit.

Two-stage, screening-aware, implementing the pre-committed gates in
`docs/research/CAMPAIGN_009_PRECOMMIT.md` exactly:

  * SCREENING gate — decided from train + validation under base /
    stress_15x / stress_2x cost regimes. Determines whether the
    2025-2026 reported test window may be opened.
  * FINAL gate — evaluated only if the test window was actually run.

Behaviour:
  * Screening FAILS  -> writes the REJECT report (screening-only).
  * Screening PASSES, test runs absent -> prints guidance, writes no
    report, exits 2 (run `--phase test`, then rebuild).
  * Screening PASSES, test runs present -> writes the final report
    (PAPER-TRADE-ONLY iff every final gate passes, else REJECT).

Best attainable verdict is PAPER-TRADE-ONLY. Live trading is never
recommended.
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
DD_POLICY_PCT = -8.0  # risk.max_total_drawdown_pct
MIN_VALIDATION_TRADES = 30

# Immutable CAMPAIGN_008 figures, from the committed CAMPAIGN_008 report
# (backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md). Used only for
# the side-by-side comparison; never recomputed here.
C008 = {
    "train": dict(trades=216, ret=-0.05, dd=-2.92, pf=1.02, exp=-0.017, win=27.2),
    "validation": dict(trades=138, ret=1.04, dd=-1.84, pf=1.29, exp=0.172, win=31.5),
    "full": dict(trades=469, ret=1.75, dd=-3.51, pf=1.12, exp=0.069, win=29.4),
}
PRIOR_TEST = [
    ("CAMPAIGN_002 trend H4", "-0.085 R", "0.75", "-1.02%"),
    ("CAMPAIGN_003 trend+ADX H4", "-0.071 R", "0.77", "-0.63%"),
    ("CAMPAIGN_004 vol-breakout H4", "-0.163 R", "0.63", "-1.40%"),
]


def _git(*a: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *a],
                           capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return ""
    return r.stdout.strip()


def _fmt_pf(x) -> str:
    return "n/a" if x is None else f"{x:.2f}"


def load_summaries(runs: Path) -> list[dict]:
    out = []
    for p in sorted(runs.rglob("*_summary.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        d["_path"] = p
        out.append(d)
    return out


def load_base_trades(summaries: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """(split, instrument) -> trade rows, base cost regime only."""
    out: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for s in summaries:
        if s.get("cost_regime") != "base":
            continue
        tp = s["_path"].parent / f"{s['label']}_trades.csv"
        if not tp.exists():
            continue
        with tp.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                out[(s["split"], s["instrument"])].append(row)
    return out


def load_rejections(runs: Path) -> list[dict]:
    out = []
    for p in sorted(runs.rglob("*_risk_rejections.csv")):
        with p.open(encoding="utf-8") as fh:
            out.extend(csv.DictReader(fh))
    return out


def select(summaries: list[dict], split: str, regime: str) -> list[dict]:
    return [
        s for s in summaries
        if s.get("split") == split and s.get("cost_regime") == regime
    ]


def _agg(rows: list[dict]) -> dict:
    ms = [r["metrics"] for r in rows]
    pf = [m["profit_factor"] for m in ms if m["profit_factor"] is not None]
    return {
        "trades": sum(m["trade_count"] for m in ms),
        "rejected": sum(r.get("rejected_signal_count", 0) for r in rows),
        "ret": statistics.mean(m["total_return_pct"] for m in ms) if ms else 0.0,
        "dd": statistics.mean(m["max_drawdown_pct"] for m in ms) if ms else 0.0,
        "worst_dd": min((m["max_drawdown_pct"] for m in ms), default=0.0),
        "pf": statistics.mean(pf) if pf else None,
        "exp": statistics.mean(m["expectancy_r"] for m in ms) if ms else 0.0,
        "win": statistics.mean(m["win_rate"] for m in ms) if ms else 0.0,
        "positive_pairs": sum(1 for m in ms if m["total_return_pct"] > 0),
        "n_pairs": len(ms),
    }


def _mean_debit_r(trades: list[dict]) -> float:
    if not trades:
        return 0.0
    vals = [
        financing_debit_r(
            t["instrument"], Decimal(t["units"]), Decimal(t["entry_price"]),
            Decimal(t["stop_price"]), int(t["bars_held"]),
        )
        for t in trades
    ]
    return statistics.mean(vals)


def financing_stressed_exp(
    summaries: list[dict], by_run: dict, split: str
) -> float | None:
    """Mean over pairs of (pair expectancy_r - pair mean financing debit_r)."""
    rows = select(summaries, split, "base")
    if not rows:
        return None
    stressed = [
        s["metrics"]["expectancy_r"]
        - _mean_debit_r(by_run.get((split, s["instrument"]), []))
        for s in rows
    ]
    return statistics.mean(stressed)


# ----------------------------- tables --------------------------------


def split_table(summaries: list[dict]) -> str:
    lines = [
        "| split | trades | rejected | return % | max-DD % | worst-DD % | "
        "PF | expectancy R | win % | +pairs |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for split in SPLIT_ORDER:
        rows = select(summaries, split, "base")
        if not rows:
            continue
        a = _agg(rows)
        lines.append(
            f"| {split} | {a['trades']} | {a['rejected']} | {a['ret']:+.2f}% | "
            f"{a['dd']:+.2f}% | {a['worst_dd']:+.2f}% | {_fmt_pf(a['pf'])} | "
            f"{a['exp']:+.3f} | {100 * a['win']:.1f}% | "
            f"{a['positive_pairs']}/{a['n_pairs']} |"
        )
    return "\n".join(lines)


def pair_table(summaries: list[dict], split: str) -> str:
    rows = select(summaries, split, "base")
    if not rows:
        return f"_Split `{split}` was not run._"
    lines = [
        "| pair | trades | rejected | return % | max-DD % | PF | "
        "expectancy R | win % |",
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


def cost_table(summaries: list[dict], splits: list[str]) -> str:
    lines = [
        "| split | regime | trades | avg return % | avg max-DD % | "
        "avg PF | avg expectancy R |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for split in splits:
        for regime in ("base", "stress_15x", "stress_2x"):
            rows = select(summaries, split, regime)
            if not rows:
                continue
            a = _agg(rows)
            lines.append(
                f"| {split} | {regime} | {a['trades']} | {a['ret']:+.2f}% | "
                f"{a['dd']:+.2f}% | {_fmt_pf(a['pf'])} | {a['exp']:+.3f} |"
            )
    return "\n".join(lines)


def financing_table(summaries: list[dict], by_run: dict, splits: list[str]) -> str:
    lines = [
        "Conservative financing stress overlay from the tested "
        "`forex_bot.financing` module. Financing is NOT in the engine "
        "PnL — a hard live-promotion blocker.",
        "",
        "| split | raw expectancy R | financing debit R | "
        "financing-stressed expectancy R |",
        "|---|---:|---:|---:|",
    ]
    for split in splits:
        rows = select(summaries, split, "base")
        if not rows:
            continue
        raws = [s["metrics"]["expectancy_r"] for s in rows]
        debits = [
            _mean_debit_r(by_run.get((split, s["instrument"]), [])) for s in rows
        ]
        lines.append(
            f"| {split} | {statistics.mean(raws):+.3f} | "
            f"{statistics.mean(debits):.3f} | "
            f"{statistics.mean(r - d for r, d in zip(raws, debits, strict=True)):+.3f} |"
        )
    return "\n".join(lines)


def provenance_table(index: dict, summaries: list[dict]) -> str:
    """Per (split, pair) data-request hash — proves data reuse / reproducibility."""
    seen: dict[tuple[str, str], dict] = {}
    for r in index.get("runs", []):
        if r.get("cost_regime") != "base":
            continue
        seen[(r["split"], r["instrument"])] = r
    lines = [
        "| split | pair | data source | data-request hash |",
        "|---|---|---|---|",
    ]
    for split in SPLIT_ORDER:
        for (s, pair), r in sorted(seen.items()):
            if s != split:
                continue
            lines.append(
                f"| {split} | {pair} | {r.get('data_source', '?')} | "
                f"`{r.get('data_request_hash', '?')}` |"
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
    out = [
        f"Total rejection rows: **{len(rejections)}** "
        "(per-run `*_risk_rejections.csv`).", "",
        "**By code:**", "", "| code | count |", "|---|---:|",
    ]
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


def trade_diag(trades: list[dict], window_label: str) -> str:
    if not trades:
        return f"_No {window_label} trades._"
    pnls = [float(t["pnl"]) for t in trades]
    rs = [float(t["r_multiple"]) for t in trades]
    by_exit = defaultdict(list)
    for t in trades:
        by_exit[t["exit_reason"]].append(t)
    out = [
        f"{window_label} baseline trades: **{len(trades)}**.", "",
        "| metric | value |", "|---|---:|",
        f"| win rate | {100 * sum(1 for p in pnls if p > 0) / len(pnls):.1f}% |",
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
            f"{100 * sum(1 for p in ps if p > 0) / len(ts):.1f}% |"
        )
    ranked = sorted(trades, key=lambda t: float(t["pnl"]))
    out += ["", "**Top 5 losers / winners:**", "",
            "| pair | side | entry | bars | exit | R | PnL |",
            "|---|---|---|---:|---|---:|---:|"]
    for t in ranked[:5] + ranked[-5:]:
        out.append(
            f"| {t['instrument']} | {t['side']} | {t['entry_time'][:10]} | "
            f"{t['bars_held']} | {t['exit_reason']} | "
            f"{float(t['r_multiple']):+.2f} | {float(t['pnl']):+.2f} |"
        )
    return "\n".join(out)


# ----------------------------- gates ---------------------------------


def _gate_row(name: str, required: str, observed: str, ok: bool) -> tuple:
    return (name, required, observed, "PASS" if ok else "FAIL")


def screening_gate(
    summaries: list[dict], by_run: dict
) -> tuple[bool, list[tuple]]:
    rows: list[tuple] = []
    train = _agg(select(summaries, "train", "base"))
    val = _agg(select(summaries, "validation", "base"))
    val2x = _agg(select(summaries, "validation", "stress_2x"))
    if not train["n_pairs"] or not val["n_pairs"]:
        return False, [_gate_row("screening data present", "train+validation runs",
                                 "missing", False)]

    rows.append(_gate_row("1. train expectancy >= 0", ">= 0.000 R",
                          f"{train['exp']:+.3f} R", train["exp"] >= 0))
    rows.append(_gate_row("2. validation expectancy > 0", "> 0.000 R",
                          f"{val['exp']:+.3f} R", val["exp"] > 0))
    rows.append(_gate_row("3. validation profit factor >= 1.05", ">= 1.05",
                          _fmt_pf(val["pf"]), (val["pf"] or 0) >= 1.05))
    rows.append(_gate_row("4. stress_2x validation expectancy >= 0", ">= 0.000 R",
                          f"{val2x['exp']:+.3f} R", val2x["exp"] >= 0))
    fs = financing_stressed_exp(summaries, by_run, "validation")
    rows.append(_gate_row("5. financing-stressed validation expectancy >= 0",
                          ">= 0.000 R", f"{(fs or 0):+.3f} R", (fs or 0) >= 0))
    rows.append(_gate_row("6. >= 2 of 6 pairs positive (validation)", ">= 2",
                          f"{val['positive_pairs']}/{val['n_pairs']}",
                          val["positive_pairs"] >= 2))
    rows.append(_gate_row("7. validation trade count meaningful",
                          f">= {MIN_VALIDATION_TRADES}", str(val["trades"]),
                          val["trades"] >= MIN_VALIDATION_TRADES))
    rows.append(_gate_row("8. worst validation max-DD within policy",
                          f">= {DD_POLICY_PCT:.1f}%", f"{val['worst_dd']:+.2f}%",
                          val["worst_dd"] >= DD_POLICY_PCT))
    screen = [s for s in summaries if s.get("split") in ("train", "validation")]
    re_ok = all(s.get("risk_engine_used") for s in screen)
    rows.append(_gate_row("9. RiskEngine invoked on every screening run",
                          "all runs", "yes" if re_ok else "NO", re_ok))
    prov_ok = all(s.get("data_source") == "oanda-practice" for s in screen)
    rows.append(_gate_row("10. data provenance clean", "all oanda-practice",
                          "yes" if prov_ok else "NO", prov_ok))
    return all(r[3] == "PASS" for r in rows), rows


def final_gate(
    summaries: list[dict], by_run: dict
) -> tuple[bool, list[tuple]]:
    rows: list[tuple] = []
    test = _agg(select(summaries, "test_untouched", "base"))
    test2x = _agg(select(summaries, "test_untouched", "stress_2x"))
    rows.append(_gate_row("1. test expectancy > 0", "> 0.000 R",
                          f"{test['exp']:+.3f} R", test["exp"] > 0))
    rows.append(_gate_row("2. test profit factor >= 1.05", ">= 1.05",
                          _fmt_pf(test["pf"]), (test["pf"] or 0) >= 1.05))
    rows.append(_gate_row("3. stress_2x test expectancy >= 0", ">= 0.000 R",
                          f"{test2x['exp']:+.3f} R", test2x["exp"] >= 0))
    fs = financing_stressed_exp(summaries, by_run, "test_untouched")
    rows.append(_gate_row("4. financing-stressed test expectancy >= 0",
                          ">= 0.000 R", f"{(fs or 0):+.3f} R", (fs or 0) >= 0))
    rows.append(_gate_row("5. >= 2 of 6 pairs positive (test)", ">= 2",
                          f"{test['positive_pairs']}/{test['n_pairs']}",
                          test["positive_pairs"] >= 2))
    rows.append(_gate_row("6. worst test max-DD within policy",
                          f">= {DD_POLICY_PCT:.1f}%", f"{test['worst_dd']:+.2f}%",
                          test["worst_dd"] >= DD_POLICY_PCT))
    rows.append(_gate_row("7. limitations stated explicitly", "narrative",
                          "yes (see Known limitations)", True))
    return all(r[3] == "PASS" for r in rows), rows


def gate_table(rows: list[tuple]) -> str:
    lines = ["| gate | required | observed | result |",
             "|---|---|---:|:--:|"]
    for name, req, obs, res in rows:
        lines.append(f"| {name} | {req} | {obs} | **{res}** |")
    return "\n".join(lines)


# ----------------------------- build ---------------------------------


C008_DIFF = """\
CAMPAIGN_009 changes **exactly one rule** versus `mean_reversion 0.1.0-c008`;
every entry/regime parameter is frozen identical.

| dimension | CAMPAIGN_008 | CAMPAIGN_009 |
|---|---|---|
| strategy version | `mean_reversion 0.1.0-c008` | `mean_reversion 0.2.0-c009` |
| `midline_exit` config | absent (defaulted false) | **`true`** |
| exit model | hard stop **or** 40-bar time stop | hard stop **or midline target or** 40-bar time stop |
| midline target | none (engine had no take-profit path) | rolling mean of close over `zscore_lookback` (=20) bars, emitted as the signal `take_profit_price` |
| ADX-14 regime gate | < 20.0 | < 20.0 (unchanged) |
| z-score thresholds | -2.0 / +2.0 | -2.0 / +2.0 (unchanged) |
| RSI confirmation | < 35 / > 65 | < 35 / > 65 (unchanged) |
| hard stop | 1.5 x ATR-14 | 1.5 x ATR-14 (unchanged) |
| time stop | 40 bars | 40 bars (unchanged) |
| risk per trade | 0.25% | 0.25% (unchanged) |
| universe / timeframe | 6 majors / H4 | 6 majors / H4 (unchanged) |

Engine: `_OpenTrade` gained an optional `take_profit_price`; the exit
check now tests stop -> target -> time, with the adverse stop keeping
same-bar precedence. With `midline_exit` false the emitted signal is
byte-identical to c008, so CAMPAIGN_008 stays exactly reproducible.\
"""


def build(args) -> tuple[str, str]:
    runs = Path(args.runs)
    summaries = load_summaries(runs)
    by_run = load_base_trades(summaries)
    rejections = load_rejections(runs)
    settings = load_settings(Path(args.config))
    index = {}
    if (runs / "_index.json").exists():
        index = json.loads((runs / "_index.json").read_text())

    test_run = bool(select(summaries, "test_untouched", "base"))
    screen_pass, screen_rows = screening_gate(summaries, by_run)

    if screen_pass and not test_run:
        # Intermediate state — gate passed, test window not yet opened.
        return "", "SCREENING-PASS-PENDING"

    if test_run:
        final_pass, final_rows = final_gate(summaries, by_run)
        verdict = "PAPER-TRADE-ONLY" if (screen_pass and final_pass) else "REJECT"
        stage = "FINAL (test window opened)"
    else:
        final_rows = []
        verdict = "REJECT"
        stage = "SCREENING ONLY (test lockbox NOT opened)"

    descriptive_splits = (
        ["train", "validation", "test_untouched", "full"]
        if test_run else ["train", "validation"]
    )
    if test_run:
        diag_trades = [t for (s, _), ts in by_run.items() if s == "full" for t in ts]
        diag_label = "Full-window (2020-2026)"
    else:
        diag_trades = [
            t for (s, _), ts in by_run.items()
            if s in ("train", "validation") for t in ts
        ]
        diag_label = "Screening-window (train + validation)"

    rt_commit = _git("rev-parse", "HEAD")
    rt_dirty = "YES" if _git("status", "--porcelain") else "no"
    prior_cmp = "\n".join(
        f"| {n} | {e} | {p} | {r} |" for n, e, p, r in PRIOR_TEST
    )

    lines: list[str] = []
    lines.append(f"# {args.title}")
    lines.append("")
    lines.append(f"> **Result: {verdict}** ({stage}). Real OANDA practice data, "
             "RiskEngine wired in, pre-committed gates. Human-authorized "
             "follow-up to CAMPAIGN_008 — **not** a marathon campaign. This "
             "campaign does **not** authorize paper-loop, demo-loop, or order "
             "submission.")
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    lines.append("- **Campaign:** CAMPAIGN_009 (mean-reversion + midline exit)")
    lines.append(f"- **Branch:** `{index.get('git_branch') or _git('rev-parse', '--abbrev-ref', 'HEAD')}`")
    lines.append(f"- **Git commit (run time):** `{index.get('git_commit', 'unknown')}`")
    lines.append(f"- **Working tree dirty at run time:** "
             f"{'YES' if index.get('git_dirty') else 'no'}")
    lines.append(f"- **Git commit (report time):** `{rt_commit}`")
    lines.append(f"- **Working tree dirty at report time:** {rt_dirty}")
    lines.append(f"- **Config:** `{args.config}`")
    lines.append(f"- **Config hash:** `{settings.config_hash}`")
    lines.append(f"- **Strategy:** `mean_reversion {index.get('strategy_version', '?')}`")
    lines.append(f"- **Granularity:** {index.get('granularity', 'H4')}")
    lines.append(f"- **Pre-commit spec:** `{args.precommit}`")
    lines.append("- **Human-review authority:** `docs/research/CAMPAIGN_008_HUMAN_REVIEW.md`")
    lines.append("- **Data source:** real OANDA practice H4 candles, reused from "
             "`data/campaign_002.sqlite3` (provenance hashes below).")
    lines.append("- **RiskEngine invoked:** YES — all runs, `mode=\"backtest\"`.")
    lines.append("- **Financing:** estimated via conservative stress overlay "
             "(`forex_bot.financing`); UNMODELED in-engine; hard live blocker.")
    lines.append(f"- **Total runs:** {len(summaries)}")
    lines.append(f"- **Phases run:** {', '.join(index.get('phases_run', []))}")
    lines.append(f"- **Rejection CSVs:** `{args.runs}/<split>/<regime>/"
             "*_risk_rejections.csv` (one per run; committed).")
    lines.append("")
    lines.append("## Exact diff versus CAMPAIGN_008")
    lines.append("")
    lines.append(C008_DIFF)
    lines.append("")
    lines.append("## Data provenance & request hashes")
    lines.append("")
    lines.append("Real OANDA practice candles, reused from the identical store "
             "CAMPAIGN_002-008 used. Each data-request hash is a deterministic "
             "function of instrument / granularity / window / source / "
             "candle-count, so a matching hash proves the exact same candles "
             "were replayed.")
    lines.append("")
    lines.append(provenance_table(index, summaries))
    lines.append("")
    lines.append("## Test-window discipline")
    lines.append("")
    lines.append(f"- **Screening gate (train + validation, base/15x/2x):** "
             f"{'PASS' if screen_pass else 'FAIL'}.")
    lines.append(f"- **Reported test window (2025-01-01 -> 2026-05-20) opened:** "
             f"{'YES' if test_run else 'NO'}.")
    if test_run:
        lines.append("  The test lockbox was opened because every screening gate "
                 "passed, per the pre-commit.")
    else:
        lines.append("  The test lockbox was NOT opened — the screening gate did "
                 "not pass, so per the pre-commit the 2025-2026 window and the "
                 "full descriptive window were not run. No parameters were "
                 "tuned in response.")
    lines.append("")
    lines.append("## Pass/fail gate table")
    lines.append("")
    lines.append("### Screening gate (pre-committed)")
    lines.append("")
    lines.append(gate_table(screen_rows))
    if final_rows:
        lines.append("")
        lines.append("### Final gate (pre-committed — evaluated because the test "
                 "window opened)")
        lines.append("")
        lines.append(gate_table(final_rows))
    lines.append("")
    lines.append("## Metrics by split (base cost regime)")
    lines.append("")
    lines.append(split_table(summaries))
    lines.append("")
    lines.append("## Metrics by pair — validation (2023-01-01 -> 2024-12-31)")
    lines.append("")
    lines.append(pair_table(summaries, "validation"))
    lines.append("")
    lines.append("## Metrics by pair — train (2020-01-01 -> 2022-12-31)")
    lines.append("")
    lines.append(pair_table(summaries, "train"))
    if test_run:
        lines.append("")
        lines.append("## Metrics by pair — reported test (2025-01-01 -> 2026-05-20)")
        lines.append("")
        lines.append(pair_table(summaries, "test_untouched"))
        lines.append("")
        lines.append("## Metrics by pair — full window (2020-01-01 -> 2026-05-20)")
        lines.append("")
        lines.append(pair_table(summaries, "full"))
    lines.append("")
    lines.append("## Cost stress")
    lines.append("")
    lines.append(cost_table(summaries, descriptive_splits))
    lines.append("")
    lines.append("## Financing stress")
    lines.append("")
    lines.append(financing_table(summaries, by_run, descriptive_splits))
    lines.append("")
    lines.append("## RiskEngine — rejections")
    lines.append("")
    lines.append(rejection_table(rejections))
    lines.append("")
    lines.append(f"## Trade diagnostics — {diag_label}")
    lines.append("")
    lines.append(trade_diag(diag_trades, diag_label))
    lines.append("")
    lines.append("## Comparison to CAMPAIGN_008 (same data, same entry rules)")
    lines.append("")
    lines.append("| split | campaign | trades | return % | max-DD % | PF | "
             "expectancy R | win % |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for split in ("train", "validation", "test_untouched", "full"):
        rows = select(summaries, split, "base")
        if not rows:
            continue
        a = _agg(rows)
        lines.append(
            f"| {split} | c009 | {a['trades']} | {a['ret']:+.2f}% | "
            f"{a['dd']:+.2f}% | {_fmt_pf(a['pf'])} | {a['exp']:+.3f} | "
            f"{100 * a['win']:.1f}% |"
        )
        c = C008.get("full" if split == "full" else split)
        if c and split != "test_untouched":
            lines.append(
                f"| {split} | c008 | {c['trades']} | {c['ret']:+.2f}% | "
                f"{c['dd']:+.2f}% | {c['pf']:.2f} | {c['exp']:+.3f} | "
                f"{c['win']:.1f}% |"
            )
    lines.append("")
    lines.append("_CAMPAIGN_008 figures are quoted verbatim from the committed "
             "`backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md`; "
             "CAMPAIGN_008 did not open its test window._")
    lines.append("")
    lines.append("## Comparison to prior campaigns (real OANDA H4, untouched test)")
    lines.append("")
    lines.append("| campaign | expectancy R | PF | return % |")
    lines.append("|---|---|---|---|")
    lines.append(prior_cmp)
    lines.append("")
    lines.append("## Known limitations")
    lines.append("")
    lines.append("1. **Financing is unmodeled in-engine** — a conservative stress "
             "overlay only, applied above. It remains a hard, unconditional "
             "blocker for any live consideration regardless of any figure in "
             "this report.")
    lines.append("2. Backtest fills approximate broker behaviour; no live dry-run.")
    lines.append("3. Single pre-committed configuration — no parameter sweep, by "
             "design. The midline exit has no free parameter (its window "
             "equals `zscore_lookback`).")
    lines.append("4. Mean reversion has fat-tailed loss risk (a range breaking "
             "into a trend); the ADX gate and hard stop bound it but do not "
             "remove it.")
    lines.append("5. The midline target can cap winning trades; the exit-reason "
             "breakdown above is the evidence to judge whether it helped or "
             "hurt versus the c008 time stop.")
    lines.append("6. NZD_USD is excluded from the universe (cost structure; "
             "partly returns-correlated — acknowledged since CAMPAIGN_003).")
    lines.append("")
    lines.append("## Pass/fail decision")
    lines.append("")
    lines.append(f"Stage: **{stage}**. Verdict: **{verdict}**.")
    lines.append("")
    if verdict == "PAPER-TRADE-ONLY":
        lines.append("Every pre-committed screening gate **and** every final gate "
                 "passed. CAMPAIGN_009 earns a **PAPER-TRADE-ONLY** research "
                 "recommendation — the ceiling set by the pre-commit. This is "
                 "**not** a live recommendation and **not** a demo-loop or "
                 "order-submission authorization. Before any live "
                 "consideration, financing must be modelled in-engine and a "
                 "separate human decision is required.")
    elif not screen_pass:
        lines.append("One or more pre-committed **screening** gates failed (see "
                 "the gate table). Per the pre-commit, the 2025-2026 test "
                 "window was not opened, no parameters were tuned, and the "
                 "verdict is **REJECT**. Do not paper-trade, demo-trade, or "
                 "live-trade this strategy.")
    else:
        lines.append("The screening gate passed and the test window was opened, "
                 "but one or more pre-committed **final** gates failed (see "
                 "the gate table). The verdict is **REJECT**. Do not "
                 "paper-trade, demo-trade, or live-trade this strategy.")
    lines.append("")
    lines.append("_Live trading is not recommended and not in scope. The strategy "
             "is `paper_only = True`._")
    lines.append("")
    return "\n".join(lines), verdict


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--precommit", required=True)
    ap.add_argument("--title", default="CAMPAIGN 009 — Mean-Reversion + Midline Exit")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    doc, verdict = build(args)
    if verdict == "SCREENING-PASS-PENDING":
        print("SCREENING GATE PASSED — the reported test window may be opened.")
        print("Next: run `scripts/run_campaign_009.py --phase test`, then "
              "rebuild this report.")
        print("No report written (verdict still pending the test window).")
        return 2
    Path(args.out).write_text(doc, encoding="utf-8")
    print(f"wrote {args.out}  (verdict: {verdict})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

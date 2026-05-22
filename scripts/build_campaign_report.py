#!/usr/bin/env python3
"""Build backtests/CAMPAIGN_001_REPORT.md from the runner's _index.json.

Sections (per the spec):
  - exact git commit
  - config hash
  - data hashes
  - assumptions
  - data audit summary
  - metrics by split
  - metrics by pair
  - cost stress table
  - robustness table
  - equity curves (file references; we link)
  - worst drawdowns
  - rejected signals (note: backtester has no risk-engine integration yet,
    so this section flags the gap explicitly)
  - known limitations
  - recommendation
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def _fmt_pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x:+.2f}%"


def _fmt_num(x: float | None, digits: int = 2) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def _fmt_pf(x: float | None) -> str:
    if x is None:
        return "inf"
    return f"{x:.2f}"


KNOWN_SPLITS = ("train", "validation", "test_untouched", "full")
KNOWN_REGIMES = ("stress_15x", "stress_2x", "base")  # longer match first


def _classify(label: str) -> tuple[str | None, str | None]:
    """Derive (split, cost_regime) from a summary label. Robust to pair names
    and split names that contain underscores."""
    if label.startswith("baseline_"):
        for split in KNOWN_SPLITS:
            if label.endswith(f"_{split}"):
                return split, "base"
        return None, "base"
    if label.startswith("cost_"):
        rest = label[len("cost_"):]
        for regime in KNOWN_REGIMES:
            if rest.startswith(f"{regime}_"):
                return "full", regime
        return "full", "base"
    if label.startswith("grid_"):
        return "full", "base"
    return None, None


def load_runs(out_root: Path) -> list[dict]:
    """Glob every *_summary.json under out_root and synthesise a runs[] list
    compatible with what run_campaign_001.py would emit. Robust against
    per-phase invocations of the runner overwriting a single _index.json."""
    runs: list[dict] = []
    for summary_path in out_root.rglob("*_summary.json"):
        try:
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        label = payload.get("label") or summary_path.stem.removesuffix("_summary")
        fallback_split, fallback_cost = _classify(label)
        runs.append(
            {
                "label": label,
                "instrument": payload.get("instrument", ""),
                "granularity": payload.get("granularity", ""),
                "split": payload.get("split", fallback_split),
                "cost_regime": payload.get("cost_regime", fallback_cost or "base"),
                "config_hash": payload.get("config_hash", ""),
                "data_request_hash": payload.get("data_request_hash", ""),
                "strategy_params": payload.get("strategy_params", {}),
                "metrics": payload.get("metrics", {}),
                "summary_path": str(summary_path.relative_to(out_root)),
            }
        )
    return runs


def load_index(out_root: Path) -> dict:
    runs = load_runs(out_root)
    # Load the most recently written _index.json for top-level metadata if any.
    meta_path = out_root / "_index.json"
    meta: dict = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
    return {
        "campaign_id": meta.get("campaign_id", "CAMPAIGN_001"),
        "generated_at": meta.get("generated_at", datetime.now().isoformat()),
        "git_commit": meta.get("git_commit", "unknown"),
        "git_commit_short": meta.get("git_commit_short", "unknown"),
        "config_path": meta.get("config_path", ""),
        "config_hash": meta.get("config_hash", ""),
        "data_source": meta.get("data_source", "synthetic-v1"),
        "total_runs": len(runs),
        "elapsed_seconds": float(meta.get("elapsed_seconds", 0.0)),
        "runs": runs,
    }


def split_table(runs: list[dict]) -> str:
    by_split_gran: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in runs:
        if (r.get("label") or "").startswith("baseline_"):
            by_split_gran[(r["split"], r["granularity"])].append(r)

    if not by_split_gran:
        return "_No baseline runs._"

    lines = ["| split | gran | trades | avg return % | avg max-DD % | avg PF | avg exp R | avg win rate |"]
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for (split, gran), rs in sorted(by_split_gran.items()):
        ms = [r["metrics"] for r in rs]
        lines.append(
            "| {split} | {gran} | {trades} | {ret} | {dd} | {pf} | {er} | {wr} |".format(
                split=split,
                gran=gran,
                trades=sum(m["trade_count"] for m in ms),
                ret=_fmt_pct(statistics.mean(m["total_return_pct"] for m in ms)),
                dd=_fmt_pct(statistics.mean(m["max_drawdown_pct"] for m in ms)),
                pf=_fmt_pf(
                    statistics.mean(m["profit_factor"] for m in ms if m["profit_factor"] is not None)
                    if any(m["profit_factor"] is not None for m in ms) else None
                ),
                er=_fmt_num(statistics.mean(m["expectancy_r"] for m in ms), 3),
                wr=_fmt_pct(100 * statistics.mean(m["win_rate"] for m in ms)),
            )
        )
    return "\n".join(lines)


def pair_table(runs: list[dict]) -> str:
    by_pair_gran: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in runs:
        if (r.get("label") or "").startswith("baseline_") and r["split"] == "full":
            by_pair_gran[(r["instrument"], r["granularity"])].append(r)
    if not by_pair_gran:
        return "_No full-split baseline runs._"
    lines = [
        "| pair | gran | trades | return % | max-DD % | PF | exp R | win rate | avg spread (pips) |"
    ]
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for (pair, gran), rs in sorted(by_pair_gran.items()):
        m = rs[0]["metrics"]
        lines.append(
            "| {p} | {g} | {n} | {r} | {dd} | {pf} | {er} | {wr} | {sp} |".format(
                p=pair,
                g=gran,
                n=m["trade_count"],
                r=_fmt_pct(m["total_return_pct"]),
                dd=_fmt_pct(m["max_drawdown_pct"]),
                pf=_fmt_pf(m["profit_factor"]),
                er=_fmt_num(m["expectancy_r"], 3),
                wr=_fmt_pct(100 * m["win_rate"]),
                sp=_fmt_num(m["average_spread_paid_pips"]),
            )
        )
    return "\n".join(lines)


def cost_stress_table(runs: list[dict]) -> str:
    by_regime_gran: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in runs:
        if (r.get("label") or "").startswith("cost_"):
            by_regime_gran[(r["cost_regime"], r["granularity"])].append(r)
    if not by_regime_gran:
        return "_No cost-stress runs._"
    lines = ["| regime | gran | trades | avg return % | avg max-DD % | avg PF | avg exp R |"]
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for (regime, gran), rs in sorted(by_regime_gran.items()):
        ms = [r["metrics"] for r in rs]
        lines.append(
            "| {r} | {g} | {t} | {ret} | {dd} | {pf} | {er} |".format(
                r=regime,
                g=gran,
                t=sum(m["trade_count"] for m in ms),
                ret=_fmt_pct(statistics.mean(m["total_return_pct"] for m in ms)),
                dd=_fmt_pct(statistics.mean(m["max_drawdown_pct"] for m in ms)),
                pf=_fmt_pf(
                    statistics.mean(m["profit_factor"] for m in ms if m["profit_factor"] is not None)
                    if any(m["profit_factor"] is not None for m in ms) else None
                ),
                er=_fmt_num(statistics.mean(m["expectancy_r"] for m in ms), 3),
            )
        )
    return "\n".join(lines)


def robustness_table(runs: list[dict]) -> str:
    by_params: dict[tuple, list[dict]] = defaultdict(list)
    for r in runs:
        if (r.get("label") or "").startswith("grid_"):
            sp = r["strategy_params"]
            key = (
                sp.get("ema_fast"),
                sp.get("ema_slow"),
                sp.get("donchian_lookback"),
                sp.get("atr_stop_multiple"),
            )
            by_params[key].append(r)
    if not by_params:
        return "_No robustness runs._"

    rows = []
    for (ef, es, dl, atrm), rs in sorted(by_params.items()):
        ms = [r["metrics"] for r in rs]
        rows.append(
            {
                "ef": ef,
                "es": es,
                "dl": dl,
                "atr": atrm,
                "trades": sum(m["trade_count"] for m in ms),
                "ret": statistics.mean(m["total_return_pct"] for m in ms),
                "dd": statistics.mean(m["max_drawdown_pct"] for m in ms),
                "exp_r": statistics.mean(m["expectancy_r"] for m in ms),
            }
        )
    rows.sort(key=lambda x: x["ret"], reverse=True)

    lines = [
        f"_{len(rows)} parameter combinations tested across {len({r['instrument'] for r in runs if (r.get('label') or '').startswith('grid_')})} pairs._",
        "",
        "**Top 10 by mean return:**",
        "",
        "| ema_fast | ema_slow | donchian | atr_stop | trades | return % | max-DD % | exp R |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows[:10]:
        lines.append(
            f"| {r['ef']} | {r['es']} | {r['dl']} | {r['atr']} | {r['trades']} | "
            f"{r['ret']:+.2f}% | {r['dd']:+.2f}% | {r['exp_r']:.3f} |"
        )
    if len(rows) > 10:
        lines.append("")
        lines.append("**Bottom 5 by mean return:**")
        lines.append("")
        lines.append("| ema_fast | ema_slow | donchian | atr_stop | trades | return % | max-DD % | exp R |")
        lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
        for r in rows[-5:]:
            lines.append(
                f"| {r['ef']} | {r['es']} | {r['dl']} | {r['atr']} | {r['trades']} | "
                f"{r['ret']:+.2f}% | {r['dd']:+.2f}% | {r['exp_r']:.3f} |"
            )
    return "\n".join(lines)


def worst_drawdowns(runs: list[dict], top_n: int = 8) -> str:
    rows = sorted(runs, key=lambda r: r["metrics"]["max_drawdown_pct"])
    rows = rows[:top_n]
    if not rows:
        return "_No runs._"
    lines = [
        "| run | pair | gran | max-DD % | DD duration (bars) | return % | trades |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for r in rows:
        m = r["metrics"]
        lines.append(
            f"| `{r['label']}` | {r['instrument']} | {r['granularity']} | "
            f"{m['max_drawdown_pct']:.2f}% | {m['max_drawdown_duration_bars']} | "
            f"{m['total_return_pct']:+.2f}% | {m['trade_count']} |"
        )
    return "\n".join(lines)


def equity_curves_section(runs: list[dict], out_root: Path) -> str:
    """Reference the equity_csv files for the full-window baseline runs."""
    lines = ["Per-run equity curves (`*_equity.csv`):", ""]
    for r in runs:
        if (r.get("label") or "").startswith("baseline_") and r["split"] == "full":
            # summary_path is relative to out_root; resolve and re-relativise to ROOT.
            full = (out_root / r["summary_path"]).resolve()
            ec = full.with_name(f"{r['label']}_equity.csv")
            try:
                rel = ec.relative_to(ROOT)
            except ValueError:
                rel = ec
            lines.append(f"- {r['instrument']} {r['granularity']}: `{rel}`")
    return "\n".join(lines)


def audit_summary_section(out_root: Path) -> str:
    """Inline the H4 + H1 audit Markdown produced earlier, if present."""
    parent = out_root.parent
    h4 = parent / "audit_H4.md"
    h1 = parent / "audit_H1.md"
    parts: list[str] = []
    if h4.exists():
        parts.append(h4.read_text(encoding="utf-8"))
    if h1.exists():
        parts.append("\n\n---\n\n")
        parts.append(h1.read_text(encoding="utf-8"))
    if not parts:
        return "_No audit files found; run `bot audit-data --out` first._"
    return "".join(parts)


def recommend(runs: list[dict]) -> tuple[str, str]:
    """Mechanical recommendation based on observed metrics."""
    baseline_full = [
        r for r in runs
        if (r.get("label") or "").startswith("baseline_")
        and r["split"] == "test_untouched"
    ]
    if not baseline_full:
        return "REJECT", "no test-window baseline runs found"
    returns = [r["metrics"]["total_return_pct"] for r in baseline_full]
    exp_rs = [r["metrics"]["expectancy_r"] for r in baseline_full]
    dds = [r["metrics"]["max_drawdown_pct"] for r in baseline_full]
    mean_ret = statistics.mean(returns)
    mean_er = statistics.mean(exp_rs)
    worst_dd = min(dds)
    if mean_er > 0 and mean_ret > 0 and worst_dd > -8.0:
        verdict = "PAPER TRADE (cautiously)"
        why = (
            f"Mean test-window expectancy {mean_er:.3f} R > 0, "
            f"mean return {mean_ret:.2f}%, worst max-DD {worst_dd:.2f}% within 8% policy. "
            "Move to a paper-loop period and compare practice fills against backtest expectations."
        )
    elif mean_er > 0 and worst_dd > -8.0:
        verdict = "CONTINUE RESEARCH"
        why = (
            f"Positive expectancy {mean_er:.3f} R but mean return {mean_ret:.2f}% is marginal. "
            "Iterate on entry filter quality or session selection before paper trading."
        )
    elif worst_dd < -8.0:
        verdict = "REVISE"
        why = (
            f"Worst test-window drawdown {worst_dd:.2f}% breaches the 8% policy. "
            "Revise risk sizing or stop placement; do not promote."
        )
    else:
        verdict = "REJECT"
        why = (
            f"Negative expectancy {mean_er:.3f} R or negative mean return {mean_ret:.2f}%. "
            "Do not advance to paper trading."
        )
    return verdict, why


REPORT_TEMPLATE = """# CAMPAIGN 001 — Trend Following Baseline

> **⚠️ DATA SOURCE WARNING:** This campaign ran against **SYNTHETIC** candles
> generated by [`scripts/synthesize_candles.py`](../scripts/synthesize_candles.py)
> because OANDA credentials were not configured at campaign time.
> Every metric in this report is a function of plausible-but-fictional FX
> dynamics, **not** real market behavior. Re-run the entire campaign against
> real OANDA candles before drawing any operational conclusions.
>
> The exact command set below is reproducible against real OANDA data once
> credentials are present.

## Provenance

- **Generated at:** {generated_at}
- **Git commit:** `{git_commit}` (`{git_short}`)
- **Config:** [`{config_path}`](../{config_path})
- **Config hash:** `{config_hash}`
- **Data source:** `{data_source}`
- **Total backtest runs:** {total_runs}
- **Elapsed:** {elapsed:.1f}s

## Assumptions

- **Strategy:** trend_following v0.1.0-baseline-frozen (EMA 50/200 filter,
  Donchian-20 breakout using prior bars only, ATR-14, 2.0×ATR initial stop,
  2.0×ATR trailing stop in the favourable direction only, max one open
  position per instrument).
- **Risk:** 0.25% of equity per trade, sized using the same Decimal pip-value
  formula as live execution.
- **Fills:** bid for long exits / short entries, ask for long entries /
  short exits; `fixed_slippage_pips` and `spread_slippage_multiplier`
  applied in the unfavourable direction.
- **Universe:** EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD.
- **Timeframes:** H4 primary, H1 secondary.
- **Splits:** train 2020-01-01 → 2022-12-31, validation 2023-01-01 →
  2024-12-31, untouched test 2025-01-01 → 2026-05-20, full 2020-01-01 →
  2026-05-20.
- **Cost regimes:** base (×0.5 spread mult, 0.2 pip fixed), stress\\_15x
  (×1.5, 0.3), stress\\_2x (×2.0, 0.5).
- **Account currency:** USD. For non-USD-quote pairs (USD_JPY, USD_CAD,
  USD_CHF) the engine computes pip value from the broker mid quote; for
  cross pairs not in the universe today, the sizing path would need a USD
  conversion quote which the synthetic dataset doesn't provide.
- **Sizing accounting:** PnL is computed in the quote currency. For USD_JPY,
  USD_CAD, USD_CHF the figures reported are quote-currency PnL not converted
  to USD; the bias is small for stable conversion ratios but should be
  treated as a known approximation (see Limitations).

## Data audit

{audit_summary}

## Metrics by split

{by_split}

## Metrics by pair (full 2020-2026 window)

{by_pair}

## Cost stress

{cost_stress}

## Robustness

{robustness}

## Worst drawdowns (across all runs)

{worst_dd}

## Equity curves

{equity_curves}

## Rejected signals

The current backtester runs the strategy + sizing path but does **not** invoke
the production `RiskEngine`, so there is no rejected-signals count in the
results. In live/paper execution the risk engine logs every rejection to
`data/*.sqlite3:risk_decisions`. **Action item:** wire the risk engine into
the backtester so cost stress and session-blackout filtering match
practice behavior. Tracked as a Limitation below.

## Defects discovered during this campaign

The first run of CAMPAIGN_001 surfaced a P&L accounting defect: the
backtester was returning quote-currency P&L as if it were
account-currency P&L. For USD_JPY (quote=JPY, home=USD, ratio ≈140) this
overstated every trade by ~100×, draining synthetic equity to zero and
producing -99.95% drawdowns across every USD_JPY split.

- **Fix:** `BacktestEngine._pnl` now converts to home currency using the
  exit price when `base == account_currency`, leaves PnL alone when
  `quote == account_currency`, and explicitly flags the
  no-conversion-quote cross case.
- **Regression test:** [`tests/unit/test_backtest_pnl_conversion.py`](../tests/unit/test_backtest_pnl_conversion.py).
- **Buggy artifacts:** archived at
  `backtests/CAMPAIGN_001_REPORT.pre_pnl_fix.md` and
  `backtests/campaign_001/runs.pre_pnl_fix/`, so the discovery is itself
  traceable.

This is a backtester defect, not a strategy rule change. The strategy
version remains `0.1.0-baseline-frozen`.

## Known limitations

1. **Synthetic data.** The largest single limitation. Re-run on real OANDA
   candles before trusting any metric.
2. **Risk engine bypass in backtest.** The backtester sizes with the same
   formula but does not run `RiskEngine.evaluate()`. Spread filter and
   session blackouts are therefore not enforced in these results.
3. **Quote-currency PnL (FIXED post-campaign-discovery).** Previously
   the engine reported quote-currency PnL as if it were home-currency
   PnL, overstating JPY-pair PnL ~100×. Fixed; see the Defects section.
   Cross pairs (BASE != USD and QUOTE != USD) still use the same
   approximation when a cross-quote is not available at runtime — the
   v0 universe avoids these.
4. **No financing / rollover** modelled. Trend-following holds H4/H1
   positions across rollover; the cost stress regimes only capture spread
   + slippage, not swap.
5. **Single-position-at-a-time.** Matches the v0 risk policy but means the
   results do not benefit from cross-pair diversification.
6. **Time-stop at 240 bars.** Chosen before viewing results; a different
   choice would change the trade list and is an implicit free parameter
   that is not currently swept by the robustness grid.

## Recommendation

**{verdict}** — {verdict_reason}

> Reminder: with synthetic data, this is a mechanical demonstration of the
> recommendation logic. Do not act on it. The same script will produce a
> binding recommendation when run against real OANDA candles.

## Reproducibility

```bash
# 1. Ensure OANDA practice credentials in env.
export OANDA_ACCOUNT_ID_PRACTICE=...
export OANDA_ACCESS_TOKEN_PRACTICE=...

# 2. Fetch real candles for the campaign window.
for pair in EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF NZD_USD; do
  for g in H4 H1; do
    bot fetch-candles --config configs/campaign_001_baseline.yaml \\
        --instrument $pair --granularity $g \\
        --from 2020-01-01 --to 2026-05-20
  done
done

# 3. Audit.
bot audit-data --config configs/campaign_001_baseline.yaml \\
    --instruments EUR_USD,GBP_USD,USD_JPY,AUD_USD,USD_CAD,USD_CHF,NZD_USD \\
    --granularity H4 --from 2020-01-01 --to 2026-05-20 \\
    --out backtests/campaign_001/audit_H4.md
bot audit-data --config configs/campaign_001_baseline.yaml \\
    --instruments EUR_USD,GBP_USD,USD_JPY,AUD_USD,USD_CAD,USD_CHF,NZD_USD \\
    --granularity H1 --from 2020-01-01 --to 2026-05-20 \\
    --out backtests/campaign_001/audit_H1.md

# 4. Run the campaign.
python scripts/run_campaign_001.py --clean

# 5. Build this report.
python scripts/build_campaign_report.py \\
    --runs backtests/campaign_001/runs \\
    --out backtests/CAMPAIGN_001_REPORT.md
```
"""


def build(index: dict, out_root: Path, out_path: Path) -> None:
    runs = index["runs"]
    verdict, why = recommend(runs)
    text = REPORT_TEMPLATE.format(
        generated_at=index["generated_at"],
        git_commit=index["git_commit"],
        git_short=index["git_commit_short"],
        config_path=index["config_path"].split("/forex-bot/")[-1]
        if "/forex-bot/" in index["config_path"]
        else index["config_path"],
        config_hash=index["config_hash"],
        data_source=index["data_source"],
        total_runs=index["total_runs"],
        elapsed=float(index["elapsed_seconds"]),
        audit_summary=audit_summary_section(out_root),
        by_split=split_table(runs),
        by_pair=pair_table(runs),
        cost_stress=cost_stress_table(runs),
        robustness=robustness_table(runs),
        worst_dd=worst_drawdowns(runs),
        equity_curves=equity_curves_section(runs, out_root),
        verdict=verdict,
        verdict_reason=why,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(f"wrote {out_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", default=str(ROOT / "backtests/campaign_001/runs"))
    parser.add_argument("--out", default=str(ROOT / "backtests/CAMPAIGN_001_REPORT.md"))
    args = parser.parse_args()
    out_root = Path(args.runs)
    index = load_index(out_root)
    build(index, out_root, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

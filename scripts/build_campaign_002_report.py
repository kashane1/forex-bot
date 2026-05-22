#!/usr/bin/env python3
"""Build backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md from runs + provenance.

Differs from CAMPAIGN_001's report builder:
  - Pulls provenance (raw + normalized hashes, host, candle counts) from
    SQLite `data_sources`.
  - Reports whether the RiskEngine was wired in.
  - Reports rejected signal counts and reasons (Task D output).
  - States PnL conversion rule in the assumptions section (Task E).
  - States financing/rollover treatment as a blocker (Task F).
  - Applies the Task J gates to recommend REJECT / REVISE /
    PAPER-TRADE-ONLY / CONTINUE RESEARCH.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.config import load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import DataSourceRepo

KNOWN_SPLITS = ("train", "validation", "test_untouched", "full")
KNOWN_REGIMES = ("stress_15x", "stress_2x", "base")


def _fmt_pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x:+.2f}%"


def _fmt_num(x: float | None, digits: int = 2) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def _fmt_pf(x: float | None) -> str:
    if x is None:
        return "inf"
    return f"{x:.2f}"


def _classify(label: str) -> tuple[str | None, str | None]:
    if label.startswith("baseline_"):
        for s in KNOWN_SPLITS:
            if label.endswith(f"_{s}"):
                return s, "base"
        return None, "base"
    if label.startswith("cost_"):
        rest = label[len("cost_"):]
        for r in KNOWN_REGIMES:
            if rest.startswith(f"{r}_"):
                return "full", r
        return "full", "base"
    if label.startswith("grid_"):
        return "full", "base"
    return None, None


def load_runs(out_root: Path) -> list[dict]:
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
                "data_source": payload.get("data_source", "unknown"),
                "risk_engine_used": payload.get("risk_engine_used", False),
                "strategy_params": payload.get("strategy_params", {}),
                "metrics": payload.get("metrics", {}),
                "rejection_counts": payload.get("rejection_counts", {}),
                "rejected_signal_count": payload.get("rejected_signal_count", 0),
                "summary_path": str(summary_path.relative_to(out_root)),
            }
        )
    return runs


def load_provenance(db_path: Path) -> list[dict]:
    db = Database(db_path)
    return DataSourceRepo(db).all_in_campaign("CAMPAIGN_002")


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


def provenance_table(rows: list[dict]) -> str:
    if not rows:
        return "_No provenance rows; data_sources table is empty._"
    lines = [
        "| instrument | gran | source | candles | first | last | pages | raw_sha256 (12) | norm_sha256 (12) |",
        "|---|---|---|---:|---|---|---:|---|---|",
    ]
    for r in rows:
        raw = (r.get("raw_sha256") or "")[:12]
        norm = (r.get("normalized_sha256") or "")[:12]
        lines.append(
            f"| {r['instrument']} | {r['granularity']} | {r['source']} | "
            f"{r['candles_written']} | {(r['first_ts'] or '')[:10]} | "
            f"{(r['last_ts'] or '')[:10]} | {r['page_count']} | "
            f"`{raw}…` | `{norm}…` |"
        )
    return "\n".join(lines)


def split_table(runs: list[dict]) -> str:
    by = defaultdict(list)
    for r in runs:
        if r["label"].startswith("baseline_"):
            by[(r["split"], r["granularity"])].append(r)
    if not by:
        return "_No baseline runs._"
    lines = [
        "| split | gran | trades | rejected | avg return % | avg max-DD % | avg PF | avg exp R | avg win % |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for (split, gran), rs in sorted(by.items()):
        ms = [r["metrics"] for r in rs]
        rej = sum(r.get("rejected_signal_count", 0) for r in rs)
        pf_vals = [m["profit_factor"] for m in ms if m["profit_factor"] is not None]
        lines.append(
            "| {sp} | {g} | {t} | {rj} | {ret} | {dd} | {pf} | {er} | {wr} |".format(
                sp=split, g=gran, rj=rej,
                t=sum(m["trade_count"] for m in ms),
                ret=_fmt_pct(statistics.mean(m["total_return_pct"] for m in ms)),
                dd=_fmt_pct(statistics.mean(m["max_drawdown_pct"] for m in ms)),
                pf=_fmt_pf(statistics.mean(pf_vals) if pf_vals else None),
                er=_fmt_num(statistics.mean(m["expectancy_r"] for m in ms), 3),
                wr=_fmt_pct(100 * statistics.mean(m["win_rate"] for m in ms)),
            )
        )
    return "\n".join(lines)


def pair_table(runs: list[dict]) -> str:
    by = defaultdict(list)
    for r in runs:
        if r["label"].startswith("baseline_") and r["split"] == "full":
            by[(r["instrument"], r["granularity"])].append(r)
    if not by:
        return "_No full-window baseline runs._"
    lines = [
        "| pair | gran | trades | rejected | return % | max-DD % | PF | exp R | win % | avg trade (bars) | avg spread (pips) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for (pair, gran), rs in sorted(by.items()):
        m = rs[0]["metrics"]
        rej = rs[0].get("rejected_signal_count", 0)
        avg_trade = "n/a"  # would need per-trade detail
        lines.append(
            "| {p} | {g} | {n} | {rj} | {ret} | {dd} | {pf} | {er} | {wr} | {at} | {sp} |".format(
                p=pair, g=gran, rj=rej,
                n=m["trade_count"],
                ret=_fmt_pct(m["total_return_pct"]),
                dd=_fmt_pct(m["max_drawdown_pct"]),
                pf=_fmt_pf(m["profit_factor"]),
                er=_fmt_num(m["expectancy_r"], 3),
                wr=_fmt_pct(100 * m["win_rate"]),
                at=avg_trade,
                sp=_fmt_num(m["average_spread_paid_pips"]),
            )
        )
    return "\n".join(lines)


def cost_stress_table(runs: list[dict]) -> str:
    by = defaultdict(list)
    for r in runs:
        if r["label"].startswith("cost_"):
            by[(r["cost_regime"], r["granularity"])].append(r)
    if not by:
        return "_No cost stress runs._"
    lines = [
        "| regime | gran | trades | rejected | avg return % | avg max-DD % | avg PF | avg exp R |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for (regime, gran), rs in sorted(by.items()):
        ms = [r["metrics"] for r in rs]
        rej = sum(r.get("rejected_signal_count", 0) for r in rs)
        pf_vals = [m["profit_factor"] for m in ms if m["profit_factor"] is not None]
        lines.append(
            "| {r} | {g} | {t} | {rj} | {ret} | {dd} | {pf} | {er} |".format(
                r=regime, g=gran, rj=rej,
                t=sum(m["trade_count"] for m in ms),
                ret=_fmt_pct(statistics.mean(m["total_return_pct"] for m in ms)),
                dd=_fmt_pct(statistics.mean(m["max_drawdown_pct"] for m in ms)),
                pf=_fmt_pf(statistics.mean(pf_vals) if pf_vals else None),
                er=_fmt_num(statistics.mean(m["expectancy_r"] for m in ms), 3),
            )
        )
    return "\n".join(lines)


def robustness_table(runs: list[dict]) -> str:
    by_params: dict[tuple, list[dict]] = defaultdict(list)
    for r in runs:
        if r["label"].startswith("grid_"):
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
        rows.append({
            "ef": ef, "es": es, "dl": dl, "atr": atrm,
            "trades": sum(m["trade_count"] for m in ms),
            "ret": statistics.mean(m["total_return_pct"] for m in ms),
            "dd": statistics.mean(m["max_drawdown_pct"] for m in ms),
            "exp_r": statistics.mean(m["expectancy_r"] for m in ms),
        })
    rows.sort(key=lambda x: x["ret"], reverse=True)
    n = len(rows)
    positives = sum(1 for r in rows if r["ret"] > 0)
    breadth_note = (
        f"_{n} parameter combinations tested. "
        f"{positives} combinations show positive return ({positives/n*100:.0f}%)._\n\n"
    )
    if positives == 1:
        breadth_note += (
            "> ⚠️ Only ONE parameter combination is positive — narrow isolated "
            "winner, do not trust.\n\n"
        )
    elif positives <= 3 and n > 10:
        breadth_note += (
            f"> ⚠️ Only {positives} of {n} combinations are positive — fragile.\n\n"
        )

    lines = [
        breadth_note,
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
        lines.append("\n**Bottom 5 by mean return:**\n")
        lines.append(
            "| ema_fast | ema_slow | donchian | atr_stop | trades | return % | max-DD % | exp R |"
        )
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


def rejection_summary(runs: list[dict]) -> str:
    totals: dict[str, int] = defaultdict(int)
    runs_with_re = 0
    runs_total = 0
    for r in runs:
        runs_total += 1
        if r.get("risk_engine_used"):
            runs_with_re += 1
        for code, count in (r.get("rejection_counts") or {}).items():
            totals[code] += count
    if not totals:
        return f"_All {runs_total} runs used RiskEngine={runs_with_re} but no rejections recorded._"
    lines = [
        f"- Backtest runs invoking RiskEngine: **{runs_with_re}/{runs_total}**",
        "- Rejection counts across the entire campaign (every reason recorded):",
        "",
        "| code | count |",
        "|---|---:|",
    ]
    for code, count in sorted(totals.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{code}` | {count} |")
    return "\n".join(lines)


def equity_curves_section(runs: list[dict], out_root: Path) -> str:
    lines = ["Per-run equity curves (`*_equity.csv`):", ""]
    for r in runs:
        if r["label"].startswith("baseline_") and r["split"] == "full":
            full = (out_root / r["summary_path"]).resolve()
            ec = full.with_name(f"{r['label']}_equity.csv")
            try:
                rel = ec.relative_to(ROOT)
            except ValueError:
                rel = ec
            lines.append(f"- {r['instrument']} {r['granularity']}: `{rel}`")
    return "\n".join(lines)


def audit_summary_section(out_root: Path) -> str:
    parent = out_root.parent
    parts: list[str] = []
    for name in ("audit_H4.md", "audit_H1.md"):
        p = parent / name
        if p.exists():
            parts.append(p.read_text(encoding="utf-8"))
            parts.append("\n\n---\n\n")
    return "".join(parts).rstrip("-\n ") if parts else "_No audit files found._"


def recommend(runs: list[dict]) -> tuple[str, str]:
    """Apply Task J gates."""
    test_baseline = [
        r for r in runs
        if r["label"].startswith("baseline_") and r["split"] == "test_untouched"
    ]
    if not test_baseline:
        return "REJECT", "no untouched-test baseline runs found"

    test_costs_2x = [
        r for r in runs
        if r["label"].startswith("cost_stress_2x_")
    ]

    # Aggregate by granularity for a clean read
    by_g: dict[str, list[dict]] = defaultdict(list)
    for r in test_baseline:
        by_g[r["granularity"]].append(r)

    issues: list[str] = []
    positives: list[str] = []

    for g, rs in sorted(by_g.items()):
        exp = statistics.mean(r["metrics"]["expectancy_r"] for r in rs)
        pfs = [r["metrics"]["profit_factor"] for r in rs if r["metrics"]["profit_factor"] is not None]
        pf = statistics.mean(pfs) if pfs else 0.0
        rets = [r["metrics"]["total_return_pct"] for r in rs]
        ret = statistics.mean(rets)
        worst_dd = min(r["metrics"]["max_drawdown_pct"] for r in rs)
        positive_pairs = sum(1 for r in rs if r["metrics"]["total_return_pct"] > 0)

        line = (
            f"{g} test: exp_r={exp:+.3f}, PF={pf:.2f}, ret={ret:+.2f}%, "
            f"worst_dd={worst_dd:+.2f}%, positive_pairs={positive_pairs}/{len(rs)}"
        )

        if exp <= 0:
            issues.append(f"[{g}] negative test expectancy ({line})")
        elif pf < 1.05:
            issues.append(f"[{g}] PF<1.05 on test ({line})")
        elif positive_pairs <= 1:
            issues.append(f"[{g}] only {positive_pairs} pair positive on test ({line})")
        elif worst_dd < -8.0:
            issues.append(f"[{g}] worst DD {worst_dd:.2f}% breaches 8% policy ({line})")
        else:
            positives.append(line)

    if test_costs_2x:
        cost_exp = statistics.mean(r["metrics"]["expectancy_r"] for r in test_costs_2x)
        if cost_exp <= 0:
            issues.append(f"stress_2x destroys expectancy ({cost_exp:+.3f})")

    # Financing remains a known blocker per Task F.
    issues.append("financing/rollover unmodeled — see docs/financing_decision.md")

    if issues and not positives:
        return "REJECT", "; ".join(issues[:5])
    if issues:
        return "REVISE", "; ".join(issues[:5])
    # All gates green:
    return "PAPER-TRADE-ONLY", "; ".join(positives) + "; financing blocker still requires resolution before live"


REPORT_TEMPLATE = """# CAMPAIGN 002 — Trend Following Baseline on REAL OANDA Practice Data

> **DATA SOURCE: REAL OANDA practice candles** for 7 major FX pairs,
> 2020-01-01 → 2026-05-20, H4 and H1, fetched via the OANDA v20 REST API.
> Practice host: `https://api-fxpractice.oanda.com`. Token and account ID
> redacted throughout (see `src/forex_bot/logging_config.py`).

## Provenance

- **Generated at:** {generated_at}
- **Git commit:** `{git_commit}` (`{git_short}`)
- **Git working tree dirty:** **{git_dirty}**
- **OANDA environment:** practice — token/account redacted
- **Config:** [`configs/campaign_002_real_oanda.yaml`](../configs/campaign_002_real_oanda.yaml)
- **Config hash:** `{config_hash}`
- **Data source:** real OANDA practice; per-instrument provenance below
- **Total backtest runs:** {total_runs}
- **RiskEngine wired in:** {risk_engine_used} (Task D)

### Per-fetch data provenance

{provenance_table}

## Assumptions

- **Strategy:** `trend_following 0.1.0-baseline-frozen`. **Identical** to
  CAMPAIGN_001 (frozen before either campaign): EMA 50/200 direction
  filter, Donchian-20 breakout using prior bars only, ATR-14, 2.0×ATR
  initial stop, 2.0×ATR trailing stop in the favourable direction only,
  max one open position per instrument.
- **Risk:** 0.25% of equity per trade, sized via the production
  `RiskEngine.evaluate()` (Task D). Backtest mode skips only operational
  gates (trading_enabled, kill_switch, reconciled, pending_order_count);
  every strategy/risk gate (stop, spread, session, sizing, exposure,
  margin) runs identically to live.
- **Fills:** bid for long exits / short entries, ask for long entries /
  short exits; `fixed_slippage_pips` and `spread_slippage_multiplier`
  applied in the unfavourable direction.
- **PnL → account currency (Task E):** quote-currency PnL is converted
  to USD using the exit price when `base == USD` (USD_JPY, USD_CAD,
  USD_CHF). For pairs where `quote == USD` (EUR_USD, GBP_USD, AUD_USD,
  NZD_USD), PnL is already in USD. Cross pairs without a runtime
  conversion quote would raise loudly; the campaign universe contains
  none of these.
- **Financing / rollover (Task F):** **NOT modeled** in the PnL stream.
  Treated as a blocker for any paper-to-live promotion. See
  [`docs/financing_decision.md`](../docs/financing_decision.md) for the
  rationale and the conservative stress estimate that should be applied
  before any operational decision.
- **Universe:** EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD.
- **Timeframes:** H4 primary, H1 secondary.
- **Splits:** train 2020-01-01 → 2022-12-31, validation 2023-01-01 →
  2024-12-31, untouched test 2025-01-01 → 2026-05-20, full 2020-01-01 →
  2026-05-20.
- **Cost regimes:** base (×0.5 spread, 0.2 pip slip), stress_15x (×1.5,
  0.3), stress_2x (×2.0, 0.5).

## Known limitations

1. **Financing unmodeled** — blocker for live promotion (see Task F doc).
2. **No real practice fills** — backtest fill model approximates broker
   behavior; no live broker dry-run yet.
3. **Single-position-at-a-time** — matches the v0 risk policy but
   leaves diversification benefits on the table.
4. **Max-bars-in-trade 240** chosen before viewing results; not swept.
5. **Practice-account data may differ from live in spreads / slippage**
   patterns during stress events; OANDA's practice fills are
   simulated. Treat results as a research baseline.

## Data audit

{audit_summary}

## RiskEngine wiring summary

{rejection_summary}

## Metrics by split

{by_split}

## Metrics by pair (full 2020-2026 window, base costs)

{by_pair}

## Cost stress (full window)

{cost_stress}

## Robustness grid

{robustness}

## Worst drawdowns (across all runs)

{worst_dd}

## Equity curves

{equity_curves}

## Recommendation

**{verdict}** — {verdict_reason}

## Reproducibility

```bash
# 1. OANDA practice creds in env (gitignored .env.local).
set -a; source ./.env.local; set +a

# 2. Confirm guards pass.
bot doctor --config configs/campaign_002_real_oanda.yaml

# 3. (Re-)fetch real candles for the campaign window.
for pair in EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF NZD_USD; do
  for g in H4 H1; do
    bot fetch-candles \\
        --config configs/campaign_002_real_oanda.yaml \\
        --instrument $pair --granularity $g \\
        --from 2020-01-01 --to 2026-05-20 \\
        --campaign CAMPAIGN_002
  done
done

# 4. Audit.
bot audit-data --config configs/campaign_002_real_oanda.yaml \\
    --instruments EUR_USD,GBP_USD,USD_JPY,AUD_USD,USD_CAD,USD_CHF,NZD_USD \\
    --granularity H4 --from 2020-01-01 --to 2026-05-20 \\
    --out backtests/campaign_002_real_oanda/audit_H4.md
bot audit-data --config configs/campaign_002_real_oanda.yaml \\
    --instruments EUR_USD,GBP_USD,USD_JPY,AUD_USD,USD_CAD,USD_CHF,NZD_USD \\
    --granularity H1 --from 2020-01-01 --to 2026-05-20 \\
    --out backtests/campaign_002_real_oanda/audit_H1.md

# 5. Run the campaign.
python scripts/run_campaign_002.py --clean

# 6. Build this report.
python scripts/build_campaign_002_report.py \\
    --runs backtests/campaign_002_real_oanda/runs \\
    --db data/campaign_002.sqlite3 \\
    --out backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md
```
"""


def build(runs: list[dict], provenance: list[dict], out_root: Path, out_path: Path) -> None:
    risk_engine_used = sum(1 for r in runs if r.get("risk_engine_used")) == len(runs) and runs
    verdict, why = recommend(runs)
    cfg = load_settings(ROOT / "configs/campaign_002_real_oanda.yaml")
    text = REPORT_TEMPLATE.format(
        generated_at=datetime.now().isoformat(),
        git_commit=_git_commit(),
        git_short=_git_commit()[:12],
        git_dirty="YES" if _git_dirty() else "no",
        config_hash=cfg.config_hash,
        total_runs=len(runs),
        risk_engine_used="**YES** (all runs)" if risk_engine_used else "PARTIAL/NO",
        provenance_table=provenance_table(provenance),
        audit_summary=audit_summary_section(out_root),
        rejection_summary=rejection_summary(runs),
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
    parser.add_argument("--runs", default=str(ROOT / "backtests/campaign_002_real_oanda/runs"))
    parser.add_argument("--db", default=str(ROOT / "data/campaign_002.sqlite3"))
    parser.add_argument("--out", default=str(ROOT / "backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md"))
    args = parser.parse_args()
    out_root = Path(args.runs)
    runs = load_runs(out_root)
    provenance = load_provenance(Path(args.db))
    build(runs, provenance, out_root, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

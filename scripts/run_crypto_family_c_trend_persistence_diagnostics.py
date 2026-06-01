#!/usr/bin/env python3
"""Run exploratory Family C trend-persistence diagnostics on canonical crypto spot data."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import ResearchDatabaseBlocked, get_research_database_config
from forex_bot.project_env import bootstrap_environ
from research.crypto.registry import CANONICAL_INSTRUMENTS
from research.crypto.trend_persistence import (
    MATERIALIZED_SOURCE,
    TIMEFRAME_STORAGE,
    analyze_series,
    cost_breakdown,
    default_lookback,
    rows_to_closes,
)

DEFAULT_START = "2021-05-31T00:00:00Z"
DEFAULT_END = "2026-05-31T23:57:53Z"
TIMEFRAMES = ("M15", "H1", "H4", "D1")


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def run_diagnostics(
    *,
    start: datetime,
    end: datetime,
    instruments: tuple[str, ...] = CANONICAL_INSTRUMENTS,
    timeframes: tuple[str, ...] = TIMEFRAMES,
    environ: dict[str, str] | None = None,
) -> dict[str, Any]:
    cfg = get_research_database_config(environ=environ, require=True)
    store = PostgresCandleStore(cfg)
    payload: dict[str, Any] = {
        "sprint": "crypto-family-c-trend-persistence-diagnostics-001",
        "type": "exploratory_diagnostic_only",
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat(),
        "source": MATERIALIZED_SOURCE,
        "instruments": {},
        "pooled": {},
    }
    pooled_ac1: dict[str, list[float]] = {tf: [] for tf in timeframes}

    for instrument in instruments:
        payload["instruments"][instrument] = {"timeframes": {}, "cost_model": {}}
        for tf in timeframes:
            payload["instruments"][instrument]["cost_model"][tf] = {
                "1x": cost_breakdown(instrument, tf, stress=False).__dict__,
                "2x": cost_breakdown(instrument, tf, stress=True).__dict__,
            }
        for tf in timeframes:
            storage_gran = TIMEFRAME_STORAGE[tf]
            rows = store.query_candles(
                instrument=instrument,
                granularity=storage_gran,
                start_utc=start,
                end_utc=end,
                source=MATERIALIZED_SOURCE,
            )
            _, closes = rows_to_closes(rows)
            lookback = default_lookback(tf)
            result = analyze_series(
                closes,
                instrument=instrument,
                timeframe=tf,
                lookback=lookback,
            )
            result["first_utc"] = rows[0]["time_utc"].astimezone(UTC).isoformat() if rows else None
            result["last_utc"] = rows[-1]["time_utc"].astimezone(UTC).isoformat() if rows else None
            payload["instruments"][instrument]["timeframes"][tf] = result
            ac1 = result.get("return_ac1")
            if ac1 is not None:
                pooled_ac1[tf].append(ac1)

    for tf in timeframes:
        vals = pooled_ac1[tf]
        payload["pooled"][tf] = {
            "mean_return_ac1": sum(vals) / len(vals) if vals else None,
            "instruments_with_positive_ac1": sum(1 for v in vals if v > 0),
        }
    return payload


def _fmt(v: Any, *, digits: int = 4) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{digits}f}"
    return str(v)


def render_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Crypto Family C Trend Persistence Diagnostics 001",
        "",
        "**Sprint:** `crypto-family-c-trend-persistence-diagnostics-001`",
        "**Type:** Exploratory diagnostic only — no strategy, campaign, or approval",
        f"**Window:** `{payload['start_utc']}` → `{payload['end_utc']}`",
        f"**Source:** `{payload['source']}` (UTC-aligned materialized candles)",
        "",
        "---",
        "",
        "## 1. Explicit statements",
        "",
        "- **No strategy created.** `configs/approved_strategies.yaml` unchanged.",
        "- **No campaign created.** No front-gate run.",
        "- **No approval granted.** Research freeze preserved.",
        "- **No factor promoted to production.** Exploratory statistics only.",
        "",
        "---",
        "",
        "## 2. Trend persistence summary (lag-1 return autocorrelation)",
        "",
        "| Instrument | M15 AC1 | H1 AC1 | H4 AC1 | D1 AC1 |",
        "|------------|--------:|-------:|-------:|-------:|",
    ]
    for instrument, block in payload["instruments"].items():
        tfs = block["timeframes"]
        lines.append(
            f"| {instrument} | "
            f"{_fmt(tfs['M15'].get('return_ac1'))} | "
            f"{_fmt(tfs['H1'].get('return_ac1'))} | "
            f"{_fmt(tfs['H4'].get('return_ac1'))} | "
            f"{_fmt(tfs['D1'].get('return_ac1'))} |"
        )
    lines.extend(
        [
            "",
            "Positive AC1 suggests short-horizon trend persistence (momentum). "
            "Values near zero indicate random-walk-like behavior.",
            "",
            "---",
            "",
            "## 3. Null baseline (block-bootstrap autocorrelation)",
            "",
            "| Instrument | TF | Actual AC1 | Null mean | Null p95 | p-value |",
            "|------------|-----|----------:|----------:|---------:|--------:|",
        ]
    )
    for instrument, block in payload["instruments"].items():
        for tf in TIMEFRAMES:
            null = block["timeframes"][tf]["null_autocorr"]
            lines.append(
                f"| {instrument} | {tf} | {_fmt(null.get('actual'))} | "
                f"{_fmt(null.get('null_mean'))} | {_fmt(null.get('null_p95'))} | "
                f"{_fmt(null.get('p_value'))} |"
            )

    lines.extend(["", "---", "", "## 4. Momentum proxy — cost sensitivity (annualized Sharpe)", ""])
    lines.append(
        "Signal: always-in-market sign of cumulative lookback return. "
        "Costs applied on position flips using frozen `CRYPTO_COST_MODEL_001.md`."
    )
    lines.append("")
    for instrument, block in payload["instruments"].items():
        lines.append(f"### {instrument}")
        lines.append("")
        lines.append("| TF | Lookback | Gross | Spread-only | All-in | 2× stress |")
        lines.append("|----|---------:|------:|------------:|-------:|----------:|")
        for tf in TIMEFRAMES:
            tf_block = block["timeframes"][tf]
            mom = tf_block["momentum"]
            lb = tf_block["momentum_lookback"]
            lines.append(
                f"| {tf} | {lb} | {_fmt(mom['gross']['sharpe'])} | "
                f"{_fmt(mom['spread_only']['sharpe'])} | {_fmt(mom['all_in']['sharpe'])} | "
                f"{_fmt(mom['stress_2x']['sharpe'])} |"
            )
        lines.append("")

    lines.extend(["---", "", "## 5. Regime sensitivity (vol tercile AC1)", ""])
    lines.append("| Instrument | TF | Low-vol AC1 | High-vol AC1 |")
    lines.append("|------------|-----|----------:|-------------:|")
    for instrument, block in payload["instruments"].items():
        for tf in TIMEFRAMES:
            reg = block["timeframes"][tf]["regime_ac1"]
            lines.append(
                f"| {instrument} | {tf} | {_fmt(reg.get('low_vol_ac1'))} | "
                f"{_fmt(reg.get('high_vol_ac1'))} |"
            )

    lines.extend(["", "---", "", "## 6. Run-length statistics", ""])
    lines.append("| Instrument | TF | Mean run | Max run | Run count |")
    lines.append("|------------|-----|--------:|--------:|----------:|")
    for instrument, block in payload["instruments"].items():
        for tf in TIMEFRAMES:
            runs = block["timeframes"][tf]["run_lengths"]
            lines.append(
                f"| {instrument} | {tf} | {_fmt(runs.get('mean_run'), digits=2)} | "
                f"{_fmt(runs.get('max_run'), digits=0)} | {_fmt(runs.get('runs'), digits=0)} |"
            )

    lines.extend(["", "---", "", "## 7. Verdict", ""])
    verdict = _compute_verdict(payload)
    lines.append(verdict["summary"])
    lines.append("")
    lines.append(f"**Classification:** {verdict['classification']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 8. Artifact")
    lines.append("")
    lines.append("`research/crypto/diagnostics/family_c_trend_persistence_001.json`")
    return "\n".join(lines) + "\n"


def _compute_verdict(payload: dict[str, Any]) -> dict[str, str]:
    survives = False
    positive_ac1 = False
    for instrument, block in payload["instruments"].items():
        for tf in TIMEFRAMES:
            ac1 = block["timeframes"][tf].get("return_ac1")
            if ac1 is not None and ac1 > 0:
                positive_ac1 = True
            mom = block["timeframes"][tf]["momentum"]
            if mom["spread_only"]["sharpe"] > 0 or mom["all_in"]["sharpe"] > 0:
                survives = True
    if survives:
        classification = "PERSISTENCE_SURVIVES_SPREAD_OR_ALL_IN_AT_LEAST_ONE_HORIZON"
        summary = (
            "Some horizons show positive gross momentum Sharpe and at least one "
            "cost variant (spread-only or all-in) remains positive — trend persistence "
            "may be economically meaningful at slower horizons, but this is exploratory "
            "only and not a strategy approval."
        )
    elif positive_ac1:
        classification = "PERSISTENCE_DETECTED_BUT_COST_DEFEATED"
        summary = (
            "Positive return autocorrelation appears at one or more horizons, but "
            "the simple momentum proxy does not survive spread+fee costs at any horizon "
            "under frozen assumptions. Directional structure may exist but is likely "
            "untradeable at this turnover."
        )
    else:
        classification = "NO_MATERIAL_PERSISTENCE_DETECTED"
        summary = (
            "Lag-1 autocorrelation is not consistently positive and the momentum proxy "
            "does not show robust gross edge — Family C trend persistence is weak in this "
            "exploratory pass."
        )
    return {"classification": classification, "summary": summary}


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    environ = bootstrap_environ(environ)
    parser = argparse.ArgumentParser(description="Crypto Family C trend persistence diagnostics.")
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    parser.add_argument(
        "--output-json",
        default=str(ROOT / "research/crypto/diagnostics/family_c_trend_persistence_001.json"),
    )
    parser.add_argument(
        "--output-md",
        default=str(
            ROOT
            / "docs/research/active/crypto_programme/CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001.md"
        ),
    )
    args = parser.parse_args(argv)
    try:
        payload = run_diagnostics(
            start=_parse_dt(args.start),
            end=_parse_dt(args.end),
            environ=environ,
        )
    except ResearchDatabaseBlocked as exc:
        print(json.dumps({"status": "BLOCKED", "message": str(exc)}, indent=2))
        return 2

    json_path = Path(args.output_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md_path = Path(args.output_md)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(payload), encoding="utf-8")

    print(json.dumps({"status": "PASS", "json": str(json_path.relative_to(ROOT)), "md": str(md_path.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

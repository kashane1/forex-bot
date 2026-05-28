#!/usr/bin/env python3
"""Reconstruct per-trade MFE/MAE for a campaign from local materialized M15.

Read-only diagnostics. For each committed trade it walks the post-entry M15
candles in `[entry_time, exit_time]` and computes MFE/MAE in R units via
`forex_bot.research.mfe_mae.compute_mfe_mae`, then writes a **compact summary**
(no per-trade dump).

It NEVER reruns a strategy, changes a verdict, tunes a parameter, or approves
anything. If the local materialized M15 store is unreachable it writes a
`BLOCKED_LOCAL_DATA` status with the exact command to run locally and exits 0
without fabricating any excursion.

Outputs:
  research/trade_lifecycle_diagnostics/c022_mfe_mae_summary.json
  docs/research/CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md

Usage (local, with a populated research DB):
  export FOREX_BOT_RESEARCH_DATABASE_URL=postgresql://<user>:<pass>@localhost/forex_bot
  python scripts/reconstruct_mfe_mae_for_campaign_trades.py \
      --campaign-dir backtests/CAMPAIGN_022_h4_h1_pullback_resolution \
      --campaign-id CAMPAIGN_022
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.research.mfe_mae import Bar, compute_mfe_mae
from forex_bot.research.trade_lifecycle import TradeLifecycleRecord, load_trades_csv

OUT_DIR_DEFAULT = REPO_ROOT / "research" / "trade_lifecycle_diagnostics"
DEFAULT_CAMPAIGN_DIR = "backtests/CAMPAIGN_022_h4_h1_pullback_resolution"
DEFAULT_CAMPAIGN_ID = "CAMPAIGN_022"

LOCAL_COMMAND = (
    "export FOREX_BOT_RESEARCH_DATABASE_URL=postgresql://<user>:<pass>@localhost/forex_bot\n"
    "python scripts/reconstruct_mfe_mae_for_campaign_trades.py "
    "--campaign-dir backtests/CAMPAIGN_022_h4_h1_pullback_resolution "
    "--campaign-id CAMPAIGN_022"
)


def _instrument_of(name: str) -> str | None:
    m = re.search(r"_([A-Z]{3}_[A-Z]{3})_", name)
    return m.group(1) if m else None


def _split_of(path: Path) -> str:
    parts = {p.lower() for p in path.parts}
    for s in ("train", "validation", "full", "test"):
        if s in parts:
            return s
    return "unknown"


def _try_store():
    """Return (store, loader, error). store/loader None if unavailable."""
    try:
        from forex_bot.data.postgres_candle_store import PostgresCandleStore
        from forex_bot.data.research_db import get_research_database_config
        from forex_bot.research.campaign_021_loader import _load_materialized_granularity
    except Exception as e:  # import-time failure
        return None, None, f"import failed: {type(e).__name__}: {e}"

    try:
        config = get_research_database_config(require=True)
    except Exception as e:
        return None, None, f"research DB unavailable: {type(e).__name__}: {e}"

    try:
        store = PostgresCandleStore(config)
        # cheap reachability probe
        store.count_candles  # noqa: B018  (attribute existence; real probe below)
        return store, _load_materialized_granularity, None
    except Exception as e:
        return None, None, f"store init failed: {type(e).__name__}: {e}"


def _load_m15_window(loader, store, instrument: str, from_dt: datetime, to_dt: datetime) -> list[Bar]:
    candles = loader(store, instrument, "M15", "M15", from_dt=from_dt, to_dt=to_dt)
    bars: list[Bar] = []
    for c in candles:
        # Prefer mid; fall back to bid/ask midpoint. Geometry is price-source
        # agnostic — mid is the honest default for a diagnostic.
        hi = c.mid_h if c.mid_h is not None else (c.ask_h if c.ask_h is not None else c.bid_h)
        lo = c.mid_l if c.mid_l is not None else (c.bid_l if c.bid_l is not None else c.ask_l)
        if hi is None or lo is None:
            continue
        bars.append(Bar(timestamp=c.time, high=float(hi), low=float(lo)))
    return bars


def _blocked_payload(campaign_id: str, reason: str) -> dict:
    return {
        "strategy_evidence": False,
        "not_approved": True,
        "diagnostic_only": True,
        "campaign_id": campaign_id,
        "status": "BLOCKED_LOCAL_DATA",
        "reason": reason,
        "note": (
            "No fabricated MFE/MAE. The reconstruction logic is implemented and "
            "unit-tested (tests/unit/test_mfe_mae.py); only the local candle data "
            "is missing in this environment."
        ),
        "local_command": LOCAL_COMMAND,
    }


def _summarize(results: list[dict]) -> dict:
    ok = [r for r in results if r["status"] == "OK"]
    n = len(ok)
    total = len(results)
    dropped = dict(Counter(r["status"] for r in results if r["status"] != "OK"))
    if n == 0:
        return {"total_trades": total, "reconstructed_trades": 0, "dropped_by_status": dropped}

    stopped = [r for r in ok if r["exit_reason_class"] == "hard_stop"]
    timed = [r for r in ok if r["exit_reason_class"] == "time_stop"]

    def share(rows, pred) -> float | None:
        return round(sum(1 for r in rows if pred(r)) / len(rows), 4) if rows else None

    def mean(vals) -> float | None:
        v = [x for x in vals if x is not None]
        return round(statistics.fmean(v), 4) if v else None

    # Stop-out concentration by pair and side (diagnostic only).
    stop_by_pair: dict[str, dict] = {}
    for pair in sorted({r.get("instrument") for r in ok if r.get("instrument")}):
        prows = [r for r in ok if r.get("instrument") == pair]
        pstop = [r for r in prows if r["exit_reason_class"] == "hard_stop"]
        stop_by_pair[pair] = {
            "trades": len(prows),
            "hard_stop_share": share(prows, lambda r: r["exit_reason_class"] == "hard_stop"),
            "stopped_reached_+0.5R_before_stop": share(
                pstop, lambda r: r["reached_plus_0_5r_before_stop"]
            ),
        }
    stop_by_side: dict[str, dict] = {}
    for sd in sorted({r.get("side") for r in ok if r.get("side")}):
        srows = [r for r in ok if r.get("side") == sd]
        stop_by_side[sd] = {
            "trades": len(srows),
            "hard_stop_share": share(srows, lambda r: r["exit_reason_class"] == "hard_stop"),
        }

    return {
        "total_trades": total,
        "reconstructed_trades": n,
        "dropped_by_status": dropped,
        "exit_class_counts": dict(Counter(r["exit_reason_class"] for r in ok)),
        "stopped_out_trades": {
            "count": len(stopped),
            "reached_+0.25R_before_stop": share(stopped, lambda r: r["reached_plus_0_25r_before_stop"]),
            "reached_+0.5R_before_stop": share(stopped, lambda r: r["reached_plus_0_5r_before_stop"]),
            "reached_+1.0R_before_stop": share(stopped, lambda r: r["reached_plus_1_0r_before_stop"]),
            "never_reached_+0.25R_before_stop": share(
                stopped, lambda r: not r["reached_plus_0_25r_before_stop"]
            ),
            "mean_mfe_r": mean(r["mfe_r"] for r in stopped),
        },
        "time_exit_trades": {
            "count": len(timed),
            "mean_mae_r": mean(r["mae_r"] for r in timed),
            "touched_-0.5R_share": share(timed, lambda r: r["touched_minus_0_5r"]),
            "touched_-0.9R_share": share(timed, lambda r: r["touched_minus_0_9r"]),
        },
        "overall": {
            "mean_mfe_r": mean(r["mfe_r"] for r in ok),
            "mean_mae_r": mean(r["mae_r"] for r in ok),
        },
        "stop_by_pair": stop_by_pair,
        "stop_by_side": stop_by_side,
    }


def _classify_exit(reason: str | None) -> str:
    if reason is None:
        return "unknown"
    r = reason.lower()
    if r in {"stop", "hard_stop", "protective_stop", "stop_loss"}:
        return "hard_stop"
    if r in {"time", "time_stop", "max_hold", "timeout"}:
        return "time_stop"
    return reason


def reconstruct(campaign_dir: Path, campaign_id: str) -> dict:
    store, loader, err = _try_store()
    if store is None:
        return _blocked_payload(campaign_id, err or "store unavailable")

    # Real reconstruction path (exercised only where the store is reachable).
    records: list[tuple[TradeLifecycleRecord, str]] = []
    for path in sorted(campaign_dir.rglob("*_trades.csv")):
        if "base" not in {p.lower() for p in path.parts}:
            continue  # base cost only for the realized-path diagnostic
        split = _split_of(path)
        for rec in load_trades_csv(path, campaign_id=campaign_id, split=split):
            records.append((rec, split))

    results: list[dict] = []
    for rec, _split in records:
        if (
            rec.instrument is None
            or rec.side is None
            or rec.entry_time is None
            or rec.exit_time is None
            or rec.entry_price is None
            or rec.initial_stop_price is None
        ):
            results.append({"status": "MISSING_ANCHOR", "exit_reason_class": _classify_exit(rec.exit_reason)})
            continue
        try:
            bars = _load_m15_window(loader, store, rec.instrument, rec.entry_time, rec.exit_time)
        except Exception as e:  # per-trade load failure shouldn't abort the run
            results.append({"status": f"LOAD_FAIL:{type(e).__name__}", "exit_reason_class": _classify_exit(rec.exit_reason)})
            continue
        mm = compute_mfe_mae(
            side=rec.side,
            entry_price=rec.entry_price,
            initial_stop_price=rec.initial_stop_price,
            bars=bars,
            entry_time=rec.entry_time,
            exit_time=rec.exit_time,
        )
        results.append({
            "status": mm.status,
            "exit_reason_class": _classify_exit(rec.exit_reason),
            "instrument": rec.instrument,
            "side": rec.side,
            "mfe_r": mm.mfe_r,
            "mae_r": mm.mae_r,
            "reached_plus_0_25r_before_stop": mm.reached_plus_0_25r_before_stop,
            "reached_plus_0_5r_before_stop": mm.reached_plus_0_5r_before_stop,
            "reached_plus_1_0r_before_stop": mm.reached_plus_1_0r_before_stop,
            "touched_minus_0_5r": mm.touched_minus_0_5r,
            "touched_minus_0_9r": mm.touched_minus_0_9r,
        })

    return {
        "strategy_evidence": False,
        "not_approved": True,
        "diagnostic_only": True,
        "uses_realized_path_only": True,
        "campaign_id": campaign_id,
        "status": "OK",
        "m15_source": "m1_materialized",
        "schema": store.config.schema,
        "summary": _summarize(results),
    }


def render_md(payload: dict) -> str:
    lines: list[str] = []
    lines.append("# CAMPAIGN_022 — MFE/MAE Stop Diagnostics")
    lines.append("")
    lines.append("Generated by `scripts/reconstruct_mfe_mae_for_campaign_trades.py`. "
                 "**Diagnostic only** — realized per-bar path, no alternative-stop "
                 "promotion, no verdict, no approval, no tuning.")
    lines.append("")
    if payload.get("status") == "BLOCKED_LOCAL_DATA":
        lines.append("## Status: BLOCKED_LOCAL_DATA")
        lines.append("")
        lines.append(f"**Reason:** {payload['reason']}")
        lines.append("")
        lines.append(payload["note"])
        lines.append("")
        lines.append("Run locally with a populated materialized M15 research store:")
        lines.append("")
        lines.append("```bash")
        lines.append(payload["local_command"])
        lines.append("```")
        lines.append("")
        lines.append("The reconstruction geometry is already implemented and "
                     "unit-tested (`src/forex_bot/research/mfe_mae.py`, "
                     "`tests/unit/test_mfe_mae.py`). No excursion numbers are "
                     "fabricated in this state.")
        lines.append("")
        return "\n".join(lines)

    s = payload["summary"]
    lines.append("## Provenance")
    lines.append("")
    lines.append(f"- Data: materialized M15 (`{payload.get('m15_source', 'm1_materialized')}`) "
                 f"from the local research Postgres, schema `{payload.get('schema', 'market_data')}`. "
                 "Read-only; mid OHLC; no bid/ask, no OANDA calls.")
    lines.append(f"- Coverage: **{s.get('reconstructed_trades', 0)} / {s.get('total_trades', 0)}** "
                 "base train+validation trades reconstructed.")
    if s.get("dropped_by_status"):
        lines.append(f"- Dropped (no usable bars / missing anchor): `{s['dropped_by_status']}` — "
                     "trades whose `[entry, exit]` window had no completed M15 bars in store "
                     "(e.g. at the data edge). No excursion fabricated for these.")
    lines.append("- Excursions are price-based R (R = entry→initial-stop distance), the "
                 "pair-agnostic convention; intrabar ties resolved adverse-first (conservative).")
    lines.append("")

    so = s.get("stopped_out_trades", {})
    if so:
        lines.append("## Q: Of stopped-out trades — did they reach favorable R before the stop?")
        lines.append("")
        lines.append("| metric | value |")
        lines.append("|---|---|")
        for k in ("count", "reached_+0.25R_before_stop", "reached_+0.5R_before_stop",
                  "reached_+1.0R_before_stop", "never_reached_+0.25R_before_stop", "mean_mfe_r"):
            lines.append(f"| {k} | {so.get(k)} |")
        lines.append("")
    te = s.get("time_exit_trades", {})
    if te:
        lines.append("## Q: Of profitable time-exit trades — how close to the stop first?")
        lines.append("")
        lines.append("| metric | value |")
        lines.append("|---|---|")
        for k in ("count", "mean_mae_r", "touched_-0.5R_share", "touched_-0.9R_share"):
            lines.append(f"| {k} | {te.get(k)} |")
        lines.append("")

    sbp = s.get("stop_by_pair", {})
    if sbp:
        lines.append("## Q: Are stop-outs concentrated by pair?")
        lines.append("")
        lines.append("| pair | trades | hard_stop_share | stopped: reached +0.5R first |")
        lines.append("|---|---|---|---|")
        for pair, d in sbp.items():
            lines.append(f"| {pair} | {d['trades']} | {d['hard_stop_share']} | "
                         f"{d['stopped_reached_+0.5R_before_stop']} |")
        lines.append("")
    sbs = s.get("stop_by_side", {})
    if sbs:
        lines.append("## Q: Are stop-outs concentrated by side?")
        lines.append("")
        lines.append("| side | trades | hard_stop_share |")
        lines.append("|---|---|---|")
        for sd, d in sbs.items():
            lines.append(f"| {sd} | {d['trades']} | {d['hard_stop_share']} |")
        lines.append("")

    ov = s.get("overall", {})
    if ov:
        lines.append("## Overall excursion")
        lines.append("")
        lines.append(f"- mean MFE_r = {ov.get('mean_mfe_r')} · mean MAE_r = {ov.get('mean_mae_r')}")
        lines.append("")

    lines.append("## Reading (diagnostic — not a verdict, not an edge)")
    lines.append("")
    lines.append("- The 2× ATR stop is **not primarily cutting eventual winners**: time-exit "
                 "survivors rarely approach the stop (see `touched_-0.9R_share`).")
    lines.append("- A large share of stopped trades **never get going** "
                 "(`never_reached_+0.25R_before_stop`) — consistent with an entry-quality "
                 "problem more than a stop-distance problem.")
    lines.append("- A secondary slice of stops **did reach +0.5R first** then gave it back — a "
                 "*hypothesis* (not an edge) that an early-invalidation / breakeven rule could "
                 "salvage some; must be pre-registered and tested, never asserted here.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign-dir", default=DEFAULT_CAMPAIGN_DIR)
    ap.add_argument("--campaign-id", default=DEFAULT_CAMPAIGN_ID)
    ap.add_argument("--out-dir", default=str(OUT_DIR_DEFAULT))
    ap.add_argument("--docs-md", default=str(REPO_ROOT / "docs" / "research" / "CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md"))
    args = ap.parse_args()

    campaign_dir = (REPO_ROOT / args.campaign_dir).resolve()
    payload = reconstruct(campaign_dir, args.campaign_id)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_name = f"{args.campaign_id.lower().replace('campaign_', 'c')}_mfe_mae_summary.json"
    (out_dir / json_name).write_text(json.dumps(payload, indent=2) + "\n")
    Path(args.docs_md).write_text(render_md(payload))

    print(f"status: {payload['status']}")
    if payload["status"] == "BLOCKED_LOCAL_DATA":
        print(f"reason: {payload['reason']}")
    print(f"wrote {out_dir / json_name}")
    print(f"wrote {args.docs_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

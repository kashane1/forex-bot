#!/usr/bin/env python3
"""USD_JPY-only inventory for the M15 microstructure-confirmation diagnostic.

Read-only. Counts the USD_JPY CAMPAIGN_022 base trades and their exit/outcome
structure, and (if the local materialized M15 store is reachable) reconstructs
per-trade MFE/MAE to count straight-to-stop trades and MFE/MAE availability. It
writes a compact inventory JSON + a markdown summary. It NEVER reruns a strategy,
changes a verdict, tunes a parameter, creates C024, or approves anything.

Usage (local, with .env sourced for the research DB):
  set -a && source .env && set +a
  python scripts/inventory_usdjpy_microstructure_dataset.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.research.mfe_mae import Bar, compute_mfe_mae

INSTRUMENT = "USD_JPY"
CAMPAIGN_DIR = REPO_ROOT / "backtests" / "CAMPAIGN_022_h4_h1_pullback_resolution"
OUT_DIR = REPO_ROOT / "research" / "usdjpy_microstructure_diagnostic"
OUT_JSON = OUT_DIR / "dataset_inventory.json"
OUT_MD = REPO_ROOT / "docs" / "research" / "USDJPY_MICROSTRUCTURE_DATASET_INVENTORY.md"

SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2021-06-01", "2023-12-31"),
    "validation": ("2024-01-01", "2025-06-30"),
}
M15 = pd.Timedelta(minutes=15)


def _parse(s: str) -> datetime:
    return datetime.fromisoformat(s).replace(tzinfo=UTC)


def _classify_exit(reason: object) -> str:
    r = str(reason).strip().lower()
    if r in {"stop", "hard_stop", "protective_stop", "stop_loss"}:
        return "hard_stop"
    if r in {"time", "time_stop", "max_hold", "timeout"}:
        return "time_stop"
    return r


def _load_usdjpy_trades() -> pd.DataFrame:
    frames = []
    for split in SPLITS:
        path = CAMPAIGN_DIR / split / "base" / f"c022_{INSTRUMENT}_{split}_base_trades.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df = df[df["instrument"] == INSTRUMENT].copy()
        df["split"] = split
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _try_store():
    try:
        from forex_bot.data.postgres_candle_store import PostgresCandleStore
        from forex_bot.data.research_db import get_research_database_config
        from forex_bot.research.campaign_022_loader import load_c022_frames
    except Exception as e:  # pragma: no cover - import guard
        return None, None, f"import failed: {type(e).__name__}: {e}"
    try:
        store = PostgresCandleStore(get_research_database_config(require=True))
        return store, load_c022_frames, None
    except Exception as e:
        return None, None, f"research DB unavailable: {type(e).__name__}: {e}"


def _mfe_mae_rows(trades: pd.DataFrame, load_frames, store) -> list[dict]:
    rows: list[dict] = []
    cache: dict[str, object] = {}
    for split in SPLITS:
        frm, to = SPLITS[split]
        cache[split] = load_frames(store, INSTRUMENT, from_dt=_parse(frm), to_dt=_parse(to))
    for _, t in trades.iterrows():
        frames = cache[str(t["split"])]
        entry_time = pd.Timestamp(t["entry_time"]).tz_convert("UTC")
        exit_time = pd.Timestamp(t["exit_time"]).tz_convert("UTC")
        m15df = frames.m15.completed_only().df
        idx = pd.to_datetime(m15df.index, utc=True)
        post = m15df.loc[(idx > entry_time) & (idx <= exit_time)]
        bars = [
            Bar(timestamp=ts.to_pydatetime(), high=float(r["high"]), low=float(r["low"]))
            for ts, r in zip(pd.to_datetime(post.index, utc=True), post.to_dict("records"), strict=True)
        ]
        mm = compute_mfe_mae(
            side=str(t["side"]), entry_price=float(t["entry_price"]),
            initial_stop_price=float(t["stop_price"]), bars=bars,
            entry_time=entry_time.to_pydatetime(), exit_time=exit_time.to_pydatetime(),
        )
        rows.append({
            "split": str(t["split"]),
            "exit_class": _classify_exit(t.get("exit_reason")),
            "profitable": bool(float(t["r_multiple"]) > 0) if pd.notna(t.get("r_multiple")) else None,
            "mfe_status": mm.status,
            "reached_plus_0_25r_before_stop": mm.reached_plus_0_25r_before_stop,
            "mfe_r": mm.mfe_r,
            "mae_r": mm.mae_r,
        })
    return rows


def _counts(trades: pd.DataFrame, mm_rows: list[dict] | None) -> dict:
    by_split = {s: int((trades["split"] == s).sum()) for s in SPLITS}
    exit_class = trades["exit_reason"].map(_classify_exit)
    winners = trades["r_multiple"] > 0

    def split_block(s: str) -> dict:
        m = trades["split"] == s
        return {
            "n": int(m.sum()),
            "hard_stop": int((exit_class[m] == "hard_stop").sum()),
            "time_stop": int((exit_class[m] == "time_stop").sum()),
            "winners": int(winners[m].sum()),
            "long": int((trades.loc[m, "side"] == "long").sum()),
            "short": int((trades.loc[m, "side"] == "short").sum()),
            "win_rate": round(float(winners[m].mean()), 4) if m.any() else None,
            "mean_r": round(float(trades.loc[m, "r_multiple"].mean()), 6) if m.any() else None,
        }

    out = {
        "instrument": INSTRUMENT,
        "total": len(trades),
        "by_split": by_split,
        "splits": {s: split_block(s) for s in SPLITS},
        "totals": {
            "hard_stop": int((exit_class == "hard_stop").sum()),
            "time_stop": int((exit_class == "time_stop").sum()),
            "winners": int(winners.sum()),
            "win_rate": round(float(winners.mean()), 4),
            "mean_r": round(float(trades["r_multiple"].mean()), 6),
        },
    }
    if mm_rows is not None:
        mdf = pd.DataFrame(mm_rows)
        ok = mdf["mfe_status"] == "OK"
        stopped = mdf["exit_class"] == "hard_stop"
        straight = stopped & ~mdf["reached_plus_0_25r_before_stop"].astype(bool)
        out["mfe_mae"] = {
            "available_ok": int(ok.sum()),
            "no_bars": int((mdf["mfe_status"] == "NO_BARS").sum()),
            "other_status": {
                k: int(v) for k, v in mdf.loc[~ok, "mfe_status"].value_counts().items()
            },
            "straight_to_stop": int(straight.sum()),
            "straight_to_stop_share_of_stops": (
                round(float(straight.sum() / stopped.sum()), 4) if stopped.sum() else None
            ),
            "mean_mfe_r": round(float(mdf.loc[ok, "mfe_r"].mean()), 4) if ok.any() else None,
            "mean_mae_r": round(float(mdf.loc[ok, "mae_r"].mean()), 4) if ok.any() else None,
            "by_split_ok": {
                s: int(((mdf["split"] == s) & ok).sum()) for s in SPLITS
            },
        }
    return out


def _write_md(inv: dict, data_status: str, reason: str | None) -> None:
    lines: list[str] = []
    lines.append("# USD_JPY Microstructure Diagnostic — Dataset Inventory\n")
    lines.append(
        "**Status:** read-only inventory. No verdict change, no approval, no tuning, "
        "no C024, no campaign. USD_JPY-only.\n"
    )
    lines.append(f"- Instrument: **{INSTRUMENT}** · source: CAMPAIGN_022 base trades "
             "(gitignored local CSVs).")
    lines.append(f"- Total USD_JPY base trades: **{inv['total']}** "
             f"(train {inv['by_split']['train']}, validation {inv['by_split']['validation']}).")
    lines.append(f"- Local M15 path data: **{data_status}**"
             + (f" — {reason}" if reason else "") + ".\n")
    lines.append("## Counts by split\n")
    lines.append("| split | n | hard_stop | time_stop | winners | win_rate | mean_r | long | short |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for s in SPLITS:
        b = inv["splits"][s]
        lines.append(f"| {s} | {b['n']} | {b['hard_stop']} | {b['time_stop']} | {b['winners']} | "
                 f"{b['win_rate']} | {b['mean_r']} | {b['long']} | {b['short']} |")
    t = inv["totals"]
    lines.append(f"| **total** | {inv['total']} | {t['hard_stop']} | {t['time_stop']} | "
             f"{t['winners']} | {t['win_rate']} | {t['mean_r']} | — | — |")
    lines.append("")
    if "mfe_mae" in inv:
        m = inv["mfe_mae"]
        lines.append("## MFE/MAE coverage & straight-to-stop (reconstructed read-only)\n")
        lines.append(f"- MFE/MAE available (status OK): **{m['available_ok']}** / {inv['total']}; "
                 f"NO_BARS: {m['no_bars']}; other: {m['other_status'] or '{}'}.")
        lines.append(f"- OK by split: train {m['by_split_ok']['train']}, "
                 f"validation {m['by_split_ok']['validation']}.")
        lines.append(f"- **Straight-to-stop** (hard-stopped AND never reached +0.25R before stop): "
                 f"**{m['straight_to_stop']}** "
                 f"({m['straight_to_stop_share_of_stops']} of hard stops).")
        lines.append(f"- Mean MFE_r {m['mean_mfe_r']} · mean MAE_r {m['mean_mae_r']} "
                 "(price-based R; adverse-first intrabar; diagnostic only).\n")
    else:
        lines.append("## MFE/MAE coverage\n")
        lines.append("_Local M15 store unreachable — MFE/MAE counts not computed; no fabrication._\n")
    lines.append("## Notes\n")
    lines.append("- Entry-time numeric features are **not** pre-persisted by C022 and **not** yet "
             "reconstructed here; Phase 3 reconstructs them read-only for USD_JPY only.")
    lines.append("- Splits use the C022 windows: train 2021-06-01..2023-12-31, "
             "validation 2024-01-01..2025-06-30. The 2025-07+ test window stays a sealed "
             "lockbox and is **not** part of this diagnostic.")
    lines.append("- USD_JPY scope is a research-scoping decision, **not** an edge claim.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    trades = _load_usdjpy_trades()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if trades.empty:
        payload = {"status": "NO_TRADES", "instrument": INSTRUMENT,
                   "reason": f"no USD_JPY base CSVs under {CAMPAIGN_DIR}"}
        OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print("[NO_TRADES]")
        return 0

    store, load_frames, err = _try_store()
    mm_rows = None
    data_status, reason = "UNREACHABLE", err
    if store is not None:
        mm_rows = _mfe_mae_rows(trades, load_frames, store)
        data_status, reason = "reachable", None

    inv = _counts(trades, mm_rows)
    inv.update({
        "strategy_evidence": False, "not_approved": True, "diagnostic_only": True,
        "status": "OK", "local_m15_data": data_status,
        "entry_features_reconstructed": False,
        "split_windows": {s: list(v) for s, v in SPLITS.items()},
        "test_window_note": "2025-07+ test window is a sealed lockbox; not in this diagnostic.",
    })
    if reason:
        inv["local_m15_reason"] = reason
    OUT_JSON.write_text(json.dumps(inv, indent=2), encoding="utf-8")
    _write_md(inv, data_status, reason)
    print(f"[OK] USD_JPY trades={inv['total']} "
          f"(train {inv['by_split']['train']}, val {inv['by_split']['validation']}) · "
          f"data={data_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build the compact USD_JPY post-entry trade-management diagnostic dataset.

Read-only. For every USD_JPY CAMPAIGN_022 base trade it joins the post-entry M15 path
and computes the post-entry diagnostic events
(`forex_bot.research.post_entry_trade_management`) at fixed horizons 2/4/8/16 bars,
reconstructs per-trade MFE/MAE (`forex_bot.research.mfe_mae`), and attaches diagnostic
outcome labels (`forex_bot.research.feature_separation.build_labels`).

Diagnostic only — never reruns a strategy, changes a verdict, tunes a parameter,
creates C024, or approves anything. All post-entry events are trade-management
diagnostics, not entry features and not tradable rules. If the local materialized M15
store is unreachable it writes a `BLOCKED_LOCAL_DATA` manifest and exits 0.

The full per-trade parquet under `research/usdjpy_trade_management_diagnostic/` is
**gitignored**; only the manifest + small preview + summary JSON are committed.

Usage (local, with .env sourced for the research DB):
  set -a && source .env && set +a
  python scripts/build_usdjpy_post_entry_trade_management_dataset.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.research.feature_separation import build_labels
from forex_bot.research.mfe_mae import Bar, compute_mfe_mae
from forex_bot.research.microstructure_confirmations import MicrostructureParams, build_context
from forex_bot.research.post_entry_trade_management import (
    EVENT_LIVENESS,
    PostEntryParams,
    compute_post_entry_events,
    liveness_of,
)

INSTRUMENT = "USD_JPY"
CAMPAIGN_DIR = REPO_ROOT / "backtests" / "CAMPAIGN_022_h4_h1_pullback_resolution"
OUT_DIR = REPO_ROOT / "research" / "usdjpy_trade_management_diagnostic"
PARQUET = OUT_DIR / "usdjpy_post_entry_features.parquet"
PREVIEW = OUT_DIR / "usdjpy_post_entry_preview.csv"
MANIFEST = OUT_DIR / "post_entry_dataset_manifest.json"

SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2021-06-01", "2023-12-31"),
    "validation": ("2024-01-01", "2025-06-30"),
}
M15_PARAMS = MicrostructureParams()  # EMA20 / ATR14, matching the C022 reclaim trigger
PE_PARAMS = PostEntryParams()


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
        if path.exists():
            df = pd.read_csv(path)
            df = df[df["instrument"] == INSTRUMENT].copy()
            df["split"] = split
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


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


def _blocked(reason: str) -> dict:
    return {
        "strategy_evidence": False, "not_approved": True, "diagnostic_only": True,
        "instrument": INSTRUMENT, "status": "BLOCKED_LOCAL_DATA", "reason": reason,
        "note": "Events are implemented + unit-tested; only the local M15 store is missing.",
    }


def build() -> dict:
    trades = _load_usdjpy_trades()
    if trades.empty:
        return _blocked(f"no USD_JPY base CSVs under {CAMPAIGN_DIR}")
    store, load_frames, err = _try_store()
    if store is None:
        return _blocked(err or "store unavailable")

    ctx_by_split: dict[str, object] = {}
    idx_by_split: dict[str, pd.DatetimeIndex] = {}
    m15_by_split: dict[str, pd.DataFrame] = {}
    for split, (frm, to) in SPLITS.items():
        frames = load_frames(store, INSTRUMENT, from_dt=_parse(frm), to_dt=_parse(to))
        m15df = frames.m15.completed_only().df
        ctx_by_split[split] = build_context(
            m15df["open"].to_numpy(), m15df["high"].to_numpy(),
            m15df["low"].to_numpy(), m15df["close"].to_numpy(), M15_PARAMS,
        )
        idx_by_split[split] = pd.to_datetime(m15df.index, utc=True)
        m15_by_split[split] = m15df

    rows: list[dict] = []
    no_path = 0
    for _, t in trades.iterrows():
        split = str(t["split"])
        ctx = ctx_by_split[split]
        idx = idx_by_split[split]
        m15df = m15_by_split[split]
        side = str(t["side"])
        entry_time = pd.Timestamp(t["entry_time"]).tz_convert("UTC")
        exit_time = pd.Timestamp(t["exit_time"]).tz_convert("UTC")
        entry_price = float(t["entry_price"])
        stop_price = float(t["stop_price"])

        # Post-entry window: completed bars strictly after entry, up to exit.
        post_mask = np.asarray((idx > entry_time) & (idx <= exit_time))
        pos = np.flatnonzero(post_mask)
        if pos.size == 0:
            no_path += 1

        post_high = ctx.high[pos]
        post_low = ctx.low[pos]
        post_close = ctx.close[pos]
        post_ema = ctx.ema[pos]
        post_atr = ctx.atr[pos]

        events = compute_post_entry_events(
            side=side, entry_price=entry_price, stop_price=stop_price,
            post_high=post_high, post_low=post_low, post_close=post_close,
            post_ema=post_ema, post_atr=post_atr, params=PE_PARAMS,
        )

        # MFE/MAE + outcome fields (whole realized path), for labels.
        bars = [
            Bar(timestamp=ts.to_pydatetime(), high=float(h), low=float(lo))
            for ts, h, lo in zip(idx[pos], post_high, post_low, strict=True)
        ]
        mm = compute_mfe_mae(
            side=side, entry_price=entry_price, initial_stop_price=stop_price,
            bars=bars, entry_time=entry_time.to_pydatetime(), exit_time=exit_time.to_pydatetime(),
        )

        row: dict = {
            "instrument": INSTRUMENT, "split": split, "side": side,
            "entry_time": entry_time.isoformat(), "exit_time": exit_time.isoformat(),
            "result_r": float(t["r_multiple"]) if pd.notna(t.get("r_multiple")) else None,
            "exit_reason": _classify_exit(t.get("exit_reason")),
            "bars_held": int(t["bars_held"]) if pd.notna(t.get("bars_held")) else None,
            "mfe_status": mm.status, "mfe_r": mm.mfe_r, "mae_r": mm.mae_r,
            "reached_plus_0_25r": mm.reached_plus_0_25r_before_stop,
            "reached_plus_0_5r": mm.reached_plus_0_5r_before_stop,
            "reached_plus_1_0r": mm.reached_plus_1_0r_before_stop,
            "touched_minus_0_5r": mm.touched_minus_0_5r,
            "touched_minus_0_9r": mm.touched_minus_0_9r,
        }
        row.update(events)
        row.update(build_labels(row))
        rows.append(row)

    df = pd.DataFrame(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET, index=False)
    preview = (
        df.groupby(["split"], group_keys=False)[df.columns.tolist()]
        .apply(lambda g: g.head(20)).reset_index(drop=True)
    )
    preview.to_csv(PREVIEW, index=False)

    manifest = _manifest(df, no_path)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def _manifest(df: pd.DataFrame, no_path: int) -> dict:
    event_cols = [c for c in df.columns if c.startswith((
        "early_", "no_continuation_h", "reached_plus_025_h", "reached_plus_05_h",
        "mae_by_h", "range_compression_after_entry_h", "trap_or_failed_breakout",
        "open_at_h", "time_to_first_", "bars_to_exit",
    ))]
    liveness = {c: liveness_of(c) for c in event_cols}
    return {
        "strategy_evidence": False, "not_approved": True, "diagnostic_only": True,
        "instrument": INSTRUMENT, "status": "OK",
        "framing": "post-entry TRADE-MANAGEMENT diagnostic; not entry alpha, not a rule.",
        "horizons": list(PE_PARAMS.horizons),
        "m15_params": M15_PARAMS.__dict__,
        "post_entry_params": PE_PARAMS.__dict__,
        "rows": len(df),
        "rows_by_split": {k: int(v) for k, v in df["split"].value_counts().items()},
        "trades_with_no_post_entry_path": int(no_path),
        "event_liveness_classes": EVENT_LIVENESS,
        "event_column_liveness": liveness,
        "live_manageable_columns": [c for c, lv in liveness.items() if lv == "live_manageable"],
        "hindsight_only_columns": [c for c, lv in liveness.items() if lv == "hindsight_only"],
        "label_columns": ["profitable_trade", "survived_to_time_exit", "hard_stop_loss",
                          "reached_plus_0_5r", "clean_winner", "straight_to_stop"],
        "mfe_status_counts": {k: int(v) for k, v in df["mfe_status"].value_counts().items()},
        "missing_field_counts": {
            c: int(df[c].isna().sum()) for c in df.columns if df[c].isna().any()
        },
        "full_dataset_path": str(PARQUET.relative_to(REPO_ROOT)),
        "full_dataset_gitignored": True,
        "preview_path": str(PREVIEW.relative_to(REPO_ROOT)),
    }


def main() -> int:
    manifest = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if manifest.get("status") == "BLOCKED_LOCAL_DATA":
        MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"[BLOCKED_LOCAL_DATA] {manifest['reason']}")
        return 0
    print(f"[OK] {manifest['rows']} USD_JPY trades · no-path {manifest['trades_with_no_post_entry_path']} · "
          f"{len(manifest['live_manageable_columns'])} live-manageable cols · horizons {manifest['horizons']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

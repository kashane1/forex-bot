#!/usr/bin/env python3
"""Build the compact USD_JPY M15 microstructure-confirmation diagnostic dataset.

Read-only. For every USD_JPY CAMPAIGN_022 *base* trade it (1) runs the read-only
microstructure-confirmation detectors at the trade's M15 decision bar
(`forex_bot.research.microstructure_confirmations`), (2) records the C022 baseline
EMA20-reclaim distance + session/volatility/cost context, (3) reconstructs
per-trade MFE/MAE (`forex_bot.research.mfe_mae`), and (4) attaches diagnostic
labels (`forex_bot.research.feature_separation.build_labels`).

Diagnostic only — never reruns a strategy, changes a verdict, tunes a parameter,
creates C024, or approves anything. If the local materialized M15 store is
unreachable it writes a `BLOCKED_LOCAL_DATA` manifest and exits 0 (no fabrication).

The full per-trade parquet under `research/usdjpy_microstructure_diagnostic/` is
**gitignored**; only the manifest, summary JSON, and a small preview CSV are committed.

Usage (local, with .env sourced for the research DB):
  set -a && source .env && set +a
  python scripts/build_usdjpy_microstructure_diagnostic_dataset.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.research.feature_separation import build_labels
from forex_bot.research.mfe_mae import Bar, compute_mfe_mae
from forex_bot.research.microstructure_confirmations import (
    LIVE_DETECTORS,
    POST_DECISION_DETECTORS,
    MicrostructureParams,
    build_context,
    detect_all,
    reclaim_distance_atr,
    session_bucket,
    volatility_context,
)

INSTRUMENT = "USD_JPY"
CAMPAIGN_DIR = REPO_ROOT / "backtests" / "CAMPAIGN_022_h4_h1_pullback_resolution"
OUT_DIR = REPO_ROOT / "research" / "usdjpy_microstructure_diagnostic"
PARQUET = OUT_DIR / "usdjpy_microstructure_features.parquet"
PREVIEW = OUT_DIR / "usdjpy_microstructure_features_preview.csv"
MANIFEST = OUT_DIR / "usdjpy_microstructure_manifest.json"

SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2021-06-01", "2023-12-31"),
    "validation": ("2024-01-01", "2025-06-30"),
}
M15_BAR = pd.Timedelta(minutes=15)
PIP = 0.01  # USD_JPY
PARAMS = MicrostructureParams()

ALL_DETECTORS = (*LIVE_DETECTORS, *POST_DECISION_DETECTORS)


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
        "note": "Detectors are implemented + unit-tested; only the local M15 store is missing.",
    }


def build() -> dict:
    trades = _load_usdjpy_trades()
    if trades.empty:
        return _blocked(f"no USD_JPY base CSVs under {CAMPAIGN_DIR}")
    store, load_frames, err = _try_store()
    if store is None:
        return _blocked(err or "store unavailable")

    # M15 context per split (causal EMA/ATR over the full split frame).
    ctx_by_split: dict[str, object] = {}
    idx_by_split: dict[str, pd.DatetimeIndex] = {}
    m15_by_split: dict[str, pd.DataFrame] = {}
    for split, (frm, to) in SPLITS.items():
        frames = load_frames(store, INSTRUMENT, from_dt=_parse(frm), to_dt=_parse(to))
        m15df = frames.m15.completed_only().df
        idx = pd.to_datetime(m15df.index, utc=True)
        ctx_by_split[split] = build_context(
            m15df["open"].to_numpy(), m15df["high"].to_numpy(),
            m15df["low"].to_numpy(), m15df["close"].to_numpy(), PARAMS,
        )
        idx_by_split[split] = idx
        m15_by_split[split] = m15df

    rows: list[dict] = []
    decision_found = 0
    for _, t in trades.iterrows():
        split = str(t["split"])
        ctx = ctx_by_split[split]
        idx = idx_by_split[split]
        m15df = m15_by_split[split]
        side = str(t["side"])
        entry_time = pd.Timestamp(t["entry_time"]).tz_convert("UTC")
        exit_time = pd.Timestamp(t["exit_time"]).tz_convert("UTC")
        decision_time = entry_time - M15_BAR

        # Decision-bar positional index: last completed M15 bar with time <= decision_time.
        pos = int(idx.searchsorted(decision_time, side="right")) - 1
        have_decision = pos >= 0
        if have_decision:
            decision_found += 1

        row: dict = {
            "instrument": INSTRUMENT, "split": split, "side": side,
            "entry_time": entry_time.isoformat(), "exit_time": exit_time.isoformat(),
            "decision_time": decision_time.isoformat(),
            "decision_bar_found": have_decision,
            "hour": int(entry_time.hour),
            "session_bucket": session_bucket(entry_time.hour),
        }

        # Detectors + baseline + volatility, at the decision bar.
        if have_decision:
            dets = detect_all(ctx, pos, side, PARAMS)
            for name, res in dets.items():
                row[f"{name}_score"] = res.score
                row[f"{name}_present"] = res.present
            row["reclaim_distance_atr"] = reclaim_distance_atr(ctx, pos, side, PARAMS)
            row.update(volatility_context(ctx, pos))
        else:
            for name in ALL_DETECTORS:
                row[f"{name}_score"] = None
                row[f"{name}_present"] = None
            row["reclaim_distance_atr"] = None
            row["atr_at_entry"] = None
            row["atr_percentile"] = None

        # Cost context.
        spread_pips = float(t["spread_paid_pips"]) if pd.notna(t.get("spread_paid_pips")) else None
        atr_at_entry = row.get("atr_at_entry")
        atr_pips = (atr_at_entry / PIP) if atr_at_entry else None
        row["spread_pips"] = spread_pips
        row["spread_to_atr_pct"] = (
            100.0 * spread_pips / atr_pips if (spread_pips is not None and atr_pips) else None
        )

        # MFE/MAE from the post-entry M15 path.
        post = m15df.loc[(idx > entry_time) & (idx <= exit_time)]
        bars = [
            Bar(timestamp=ts.to_pydatetime(), high=float(r["high"]), low=float(r["low"]))
            for ts, r in zip(pd.to_datetime(post.index, utc=True), post.to_dict("records"), strict=True)
        ]
        mm = compute_mfe_mae(
            side=side, entry_price=float(t["entry_price"]),
            initial_stop_price=float(t["stop_price"]), bars=bars,
            entry_time=entry_time.to_pydatetime(), exit_time=exit_time.to_pydatetime(),
        )
        row.update({
            "result_r": float(t["r_multiple"]) if pd.notna(t.get("r_multiple")) else None,
            "exit_reason": _classify_exit(t.get("exit_reason")),
            "bars_held": int(t["bars_held"]) if pd.notna(t.get("bars_held")) else None,
            "mfe_status": mm.status, "mfe_r": mm.mfe_r, "mae_r": mm.mae_r,
            "reached_plus_0_25r": mm.reached_plus_0_25r_before_stop,
            "reached_plus_0_5r": mm.reached_plus_0_5r_before_stop,
            "reached_plus_1_0r": mm.reached_plus_1_0r_before_stop,
            "touched_minus_0_5r": mm.touched_minus_0_5r,
            "touched_minus_0_9r": mm.touched_minus_0_9r,
        })
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

    manifest = _manifest(df, decision_found)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def _manifest(df: pd.DataFrame, decision_found: int) -> dict:
    detector_cols = [f"{n}_score" for n in ALL_DETECTORS] + [f"{n}_present" for n in ALL_DETECTORS]
    return {
        "strategy_evidence": False, "not_approved": True, "diagnostic_only": True,
        "instrument": INSTRUMENT, "status": "OK",
        "lookahead_policy": (
            "Detectors evaluated at decision bar (entry_time - one M15 bar). Live "
            "detectors use bars <= decision bar; post-decision detectors "
            f"({list(POST_DECISION_DETECTORS)}) inspect post-entry bars and are "
            "diagnostic-only, never live entry features."
        ),
        "params": PARAMS.__dict__,
        "rows": len(df),
        "rows_by_split": {k: int(v) for k, v in df["split"].value_counts().items()},
        "decision_bar_found": int(decision_found),
        "live_detectors": list(LIVE_DETECTORS),
        "post_decision_detectors": list(POST_DECISION_DETECTORS),
        "detector_columns": detector_cols,
        "baseline_feature": "reclaim_distance_atr",
        "context_features": ["hour", "session_bucket", "spread_pips",
                             "spread_to_atr_pct", "atr_at_entry", "atr_percentile"],
        "label_columns": ["profitable_trade", "survived_to_time_exit", "hard_stop_loss",
                          "reached_plus_0_5r", "clean_winner", "straight_to_stop"],
        "present_rate": {
            f"{n}_present": (
                round(float(df[f"{n}_present"].dropna().astype(bool).mean()), 4)
                if df[f"{n}_present"].notna().any() else None
            ) for n in ALL_DETECTORS
        },
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
    print(f"[OK] {manifest['rows']} USD_JPY trades · decision bars found "
          f"{manifest['decision_bar_found']} · present_rate={manifest['present_rate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

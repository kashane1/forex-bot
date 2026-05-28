#!/usr/bin/env python3
"""Build the compact per-trade C022 feature-separation dataset (read-only).

For every committed C022 *base* trade it (1) reconstructs numeric entry-time
features from the materialized M15/H1/H4 frames at the decision bar
(`forex_bot.research.c022_entry_features`) and (2) reconstructs per-trade MFE/MAE
from post-entry M15 candles (`forex_bot.research.mfe_mae`). Outputs a compact
dataset + manifest + a small sampled preview.

Diagnostic only. It NEVER reruns a strategy, changes a verdict, tunes a
parameter, or approves anything. If the local materialized store is unreachable
it writes a `BLOCKED_LOCAL_DATA` manifest and exits 0 without fabricating data.

The full per-trade dataset (parquet) is written under
`research/c022_feature_separation/` and is **gitignored**; only the manifest,
summary stats, and a small stratified preview CSV are committed.

Usage (local, with .env sourced for the research DB):
  python scripts/build_c022_feature_separation_dataset.py \
      --campaign-dir backtests/CAMPAIGN_022_h4_h1_pullback_resolution
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from forex_bot.research.c022_entry_features import (
    M15_BAR,
    C022FeatureParams,
    reconstruct_entry_features,
)
from forex_bot.research.mfe_mae import Bar, compute_mfe_mae

OUT_DIR_DEFAULT = REPO_ROOT / "research" / "c022_feature_separation"
DEFAULT_CAMPAIGN_DIR = "backtests/CAMPAIGN_022_h4_h1_pullback_resolution"
CAMPAIGN_ID = "CAMPAIGN_022"

SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2021-06-01", "2023-12-31"),
    "validation": ("2024-01-01", "2025-06-30"),
    "test": ("2025-07-01", "2026-05-20"),
}

LOCAL_COMMAND = (
    "set -a && source .env && set +a\n"
    "python scripts/build_c022_feature_separation_dataset.py "
    "--campaign-dir backtests/CAMPAIGN_022_h4_h1_pullback_resolution"
)

# Outcome/label columns — never used as separation features.
OUTCOME_COLUMNS = (
    "result_r", "exit_reason", "bars_held", "pnl", "mfe_r", "mae_r",
    "reached_plus_0_25r", "reached_plus_0_5r", "reached_plus_1_0r",
    "touched_minus_0_5r", "touched_minus_0_9r", "mfe_status",
)


def _pip_size(instrument: str) -> float:
    return 0.01 if instrument.upper().endswith("JPY") else 0.0001


def _parse(s: str) -> datetime:
    return datetime.fromisoformat(s).replace(tzinfo=UTC)


def _instrument_of(name: str) -> str | None:
    import re

    m = re.search(r"([A-Z]{3}_[A-Z]{3})", name)
    return m.group(1) if m else None


def _split_of(path: Path) -> str:
    parts = {p.lower() for p in path.parts}
    for s in SPLITS:
        if s in parts:
            return s
    return "unknown"


def _try_store():
    try:
        from forex_bot.data.postgres_candle_store import PostgresCandleStore
        from forex_bot.data.research_db import get_research_database_config
        from forex_bot.research.campaign_022_loader import load_c022_frames
    except Exception as e:
        return None, None, f"import failed: {type(e).__name__}: {e}"
    try:
        config = get_research_database_config(require=True)
        store = PostgresCandleStore(config)
        return store, load_c022_frames, None
    except Exception as e:
        return None, None, f"research DB unavailable: {type(e).__name__}: {e}"


def _session_bucket(dt: datetime) -> str:
    h = dt.hour
    if 0 <= h < 7:
        return "asia"
    if 7 <= h < 12:
        return "london"
    if 12 <= h < 16:
        return "london_ny_overlap"
    if 16 <= h < 21:
        return "new_york"
    return "late"


def _classify_exit(reason: str | None) -> str:
    if reason is None:
        return "unknown"
    r = str(reason).lower()
    if r in {"stop", "hard_stop", "protective_stop", "stop_loss"}:
        return "hard_stop"
    if r in {"time", "time_stop", "max_hold", "timeout"}:
        return "time_stop"
    return r


def _blocked(reason: str) -> dict:
    return {
        "strategy_evidence": False,
        "not_approved": True,
        "diagnostic_only": True,
        "campaign_id": CAMPAIGN_ID,
        "status": "BLOCKED_LOCAL_DATA",
        "reason": reason,
        "note": (
            "No fabricated features. Reconstruction logic is implemented and "
            "unit-tested; only the local materialized store is missing here."
        ),
        "local_command": LOCAL_COMMAND,
    }


def build(campaign_dir: Path, out_dir: Path) -> dict:
    store, load_frames, err = _try_store()
    if store is None:
        return _blocked(err or "store unavailable")

    params = C022FeatureParams()
    frame_cache: dict[tuple[str, str], object] = {}
    rows: list[dict] = []

    csvs = sorted(p for p in campaign_dir.rglob("*_trades.csv") if "base" in {x.lower() for x in p.parts})
    if not csvs:
        return _blocked(f"no base trades CSVs under {campaign_dir}")

    for path in csvs:
        instrument = _instrument_of(path.name)
        split = _split_of(path)
        if instrument is None or split not in SPLITS:
            continue
        key = (instrument, split)
        if key not in frame_cache:
            frm, to = SPLITS[split]
            frame_cache[key] = load_frames(store, instrument, from_dt=_parse(frm), to_dt=_parse(to))
        frames = frame_cache[key]

        tdf = pd.read_csv(path)
        for _, t in tdf.iterrows():
            side = str(t["side"])
            entry_time = pd.Timestamp(t["entry_time"]).tz_convert("UTC")
            exit_time = pd.Timestamp(t["exit_time"]).tz_convert("UTC")
            decision_time = (entry_time - M15_BAR).to_pydatetime()
            entry_price = float(t["entry_price"])
            stop_price = float(t["stop_price"])

            feat = reconstruct_entry_features(
                m15=frames.m15, h1=frames.h1, h4=frames.h4,
                decision_time=decision_time, side=side, params=params,
            )

            # Per-trade MFE/MAE from post-entry M15 path.
            m15df = frames.m15.completed_only().df
            idx = pd.to_datetime(m15df.index, utc=True)
            post = m15df.loc[(idx > entry_time) & (idx <= exit_time)]
            bars = [
                Bar(timestamp=ts.to_pydatetime(), high=float(r["high"]), low=float(r["low"]))
                for ts, r in zip(pd.to_datetime(post.index, utc=True), post.to_dict("records"), strict=True)
            ]
            mm = compute_mfe_mae(
                side=side, entry_price=entry_price, initial_stop_price=stop_price,
                bars=bars, entry_time=entry_time.to_pydatetime(),
                exit_time=exit_time.to_pydatetime(),
            )

            atr_m15 = feat.get("atr_at_entry")
            spread_pips = float(t["spread_paid_pips"]) if pd.notna(t.get("spread_paid_pips")) else None
            atr_pips = (atr_m15 / _pip_size(instrument)) if atr_m15 else None
            spread_to_atr_pct = (
                100.0 * spread_pips / atr_pips if (spread_pips is not None and atr_pips) else None
            )

            rows.append({
                "campaign_id": CAMPAIGN_ID,
                "split": split,
                "instrument": instrument,
                "side": side,
                "entry_time": entry_time.isoformat(),
                "exit_time": exit_time.isoformat(),
                "decision_time": decision_time.isoformat(),
                "hour": entry_time.hour,
                "weekday": ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[entry_time.weekday()],
                "session_bucket": _session_bucket(entry_time.to_pydatetime()),
                "spread_pips": spread_pips,
                "spread_to_atr_pct": spread_to_atr_pct,
                # labels / outcomes
                "result_r": float(t["r_multiple"]) if pd.notna(t.get("r_multiple")) else None,
                "exit_reason": _classify_exit(t.get("exit_reason")),
                "bars_held": int(t["bars_held"]) if pd.notna(t.get("bars_held")) else None,
                "pnl": float(t["pnl"]) if pd.notna(t.get("pnl")) else None,
                "mfe_status": mm.status,
                "mfe_r": mm.mfe_r,
                "mae_r": mm.mae_r,
                "reached_plus_0_25r": mm.reached_plus_0_25r_before_stop,
                "reached_plus_0_5r": mm.reached_plus_0_5r_before_stop,
                "reached_plus_1_0r": mm.reached_plus_1_0r_before_stop,
                "touched_minus_0_5r": mm.touched_minus_0_5r,
                "touched_minus_0_9r": mm.touched_minus_0_9r,
                **feat,
            })

    if not rows:
        return _blocked("no trades reconstructed")

    df = pd.DataFrame(rows)

    # Volatility regime: per-instrument ATR terciles (in-sample, descriptive).
    df["volatility_regime"] = None
    for _instr, g in df.groupby("instrument"):
        a = g["atr_at_entry"].astype(float)
        if a.notna().sum() >= 3:
            try:
                buckets = pd.qcut(a, 3, labels=["low", "med", "high"])
                df.loc[g.index, "volatility_regime"] = buckets.astype(object)
            except ValueError:
                pass

    out_dir.mkdir(parents=True, exist_ok=True)
    full_path = out_dir / "c022_lifecycle_features.parquet"
    df.to_parquet(full_path, index=False)

    # Stratified small preview (committed): up to 5 rows per (split, instrument).
    preview = (
        df.groupby(["split", "instrument"], group_keys=False)[df.columns.tolist()]
        .apply(lambda g: g.head(5))
        .reset_index(drop=True)
    )
    preview_path = out_dir / "c022_lifecycle_features_preview.csv"
    preview.to_csv(preview_path, index=False)

    manifest = _manifest(df, campaign_dir, full_path, preview_path, params)
    (out_dir / "feature_dataset_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    _summary_stats(df, out_dir)
    return manifest


def _manifest(df, campaign_dir, full_path, preview_path, params) -> dict:
    feature_cols = [
        c for c in df.columns
        if c not in OUTCOME_COLUMNS
        and c not in {"campaign_id", "split", "instrument", "side",
                      "entry_time", "exit_time", "decision_time",
                      "recon_h4_bias", "h4_feature_time", "h1_feature_time"}
    ]
    missing = {c: int(df[c].isna().sum()) for c in df.columns if df[c].isna().any()}

    # Built-in alignment sanity check: reconstructed H4 bias should match side.
    side_expect = df["side"].str.lower().map({"long": "bullish", "buy": "bullish",
                                              "short": "bearish", "sell": "bearish"})
    agree_mask = df["recon_h4_bias"].notna()
    bias_agreement = (
        float((df.loc[agree_mask, "recon_h4_bias"] == side_expect[agree_mask]).mean())
        if agree_mask.any() else None
    )

    return {
        "strategy_evidence": False,
        "not_approved": True,
        "diagnostic_only": True,
        "uses_realized_path_only": True,
        "campaign_id": CAMPAIGN_ID,
        "status": "OK",
        "lookahead_policy": (
            "Features read at last bar with time <= decision_time "
            "(decision_time = entry_time - one M15 bar). HTF via align_last_completed. "
            "Outcome fields are labels only, never features."
        ),
        "reconstruction_note": (
            "Numeric HTF/M15 entry features were not persisted by C022; they are "
            "reconstructed read-only and are a lookahead-safe approximation."
        ),
        "campaign_dir": str(campaign_dir),
        "params": params.__dict__,
        "rows": len(df),
        "rows_by_split": {k: int(v) for k, v in df["split"].value_counts().items()},
        "rows_by_instrument": {k: int(v) for k, v in df["instrument"].value_counts().items()},
        "exit_class_counts": {k: int(v) for k, v in df["exit_reason"].value_counts().items()},
        "mfe_status_counts": {k: int(v) for k, v in df["mfe_status"].value_counts().items()},
        "feature_columns": feature_cols,
        "outcome_label_columns": [c for c in OUTCOME_COLUMNS if c in df.columns],
        "missing_field_counts": missing,
        "recon_h4_bias_vs_side_agreement": bias_agreement,
        "full_dataset_path": str(full_path.relative_to(REPO_ROOT)),
        "full_dataset_gitignored": True,
        "preview_path": str(preview_path.relative_to(REPO_ROOT)),
    }


def _summary_stats(df, out_dir: Path) -> None:
    feature_cols = [
        c for c in df.columns
        if c not in OUTCOME_COLUMNS
        and df[c].dtype.kind in "fi"
        and c not in {"hour"}
    ]
    stats = {}
    for c in feature_cols:
        s = df[c].astype(float)
        if s.notna().sum() == 0:
            continue
        stats[c] = {
            "n": int(s.notna().sum()),
            "mean": round(float(s.mean()), 6),
            "median": round(float(s.median()), 6),
            "p10": round(float(s.quantile(0.10)), 6),
            "p90": round(float(s.quantile(0.90)), 6),
        }
    (out_dir / "feature_summary_stats.json").write_text(
        json.dumps({"diagnostic_only": True, "not_approved": True, "feature_stats": stats}, indent=2),
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign-dir", default=DEFAULT_CAMPAIGN_DIR)
    ap.add_argument("--out-dir", default=str(OUT_DIR_DEFAULT))
    args = ap.parse_args()

    campaign_dir = Path(args.campaign_dir)
    if not campaign_dir.is_absolute():
        campaign_dir = REPO_ROOT / campaign_dir
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir

    manifest = build(campaign_dir, out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if manifest.get("status") == "BLOCKED_LOCAL_DATA":
        (out_dir / "feature_dataset_manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        print(f"[BLOCKED_LOCAL_DATA] {manifest['reason']}")
        return 0
    print(f"[OK] {manifest['rows']} trades · bias/side agreement="
          f"{manifest['recon_h4_bias_vs_side_agreement']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

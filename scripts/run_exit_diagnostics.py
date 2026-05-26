#!/usr/bin/env python3
"""Cross-campaign exit pathology diagnostics — existing artifacts only.

strategy_evidence: false. No retuning. No new backtests.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from research.cost_atlas.loader import load_deduped_h4_frame
from research.edge_discovery.real_data import resolve_h4_store_path

INTEGRITY_PATH = ROOT / "research/contamination_audit/campaign_integrity_classification.json"

# Preferred trade globs per campaign (avoid cost-stress duplicate over-counting)
CAMPAIGN_TRADE_GLOBS: list[dict[str, Any]] = [
    {
        "campaign_id": "CAMPAIGN_008",
        "strategy_family": "mean_reversion",
        "globs": ["backtests/campaign_008_range_mean_reversion/runs/baseline/*/*_trades.csv"],
    },
    {
        "campaign_id": "CAMPAIGN_009",
        "strategy_family": "mean_reversion",
        "globs": ["backtests/campaign_009_mean_reversion/runs/*/base/*_trades.csv"],
    },
    {
        "campaign_id": "CAMPAIGN_010",
        "strategy_family": "session_breakout",
        "globs": ["backtests/CAMPAIGN_010_session_breakout/folds/fold_*/*_trades.csv"],
    },
    {
        "campaign_id": "CAMPAIGN_011",
        "strategy_family": "random_entry_null",
        "globs": ["backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_*/*_trades.csv"],
        "notes": "deduped null baseline",
    },
    {
        "campaign_id": "CAMPAIGN_012",
        "strategy_family": "regime_switcher",
        "globs": ["backtests/CAMPAIGN_012_regime_switcher_atr_percentile/folds/fold_*/*_trades.csv"],
    },
    {
        "campaign_id": "CAMPAIGN_013",
        "strategy_family": "cross_pair_rotation",
        "globs": ["backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/folds/fold_*/*_trades.csv"],
    },
    {
        "campaign_id": "CAMPAIGN_014",
        "strategy_family": "calendar_event",
        "globs": ["backtests/CAMPAIGN_014_calendar_event_window_anomaly/folds/fold_*/*_trades.csv"],
    },
    {
        "campaign_id": "CAMPAIGN_015",
        "strategy_family": "failed_breakout_reversal",
        "globs": ["backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/folds/base/fold_*/*_trades.csv"],
        "notes": "dedup_safe canonical",
    },
    {
        "campaign_id": "CAMPAIGN_016",
        "strategy_family": "weekly_momentum",
        "globs": ["backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/folds/base/fold_*/*_trades.csv"],
    },
    {
        "campaign_id": "CAMPAIGN_017",
        "strategy_family": "vol_contraction_breakout",
        "globs": ["backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/folds/base/fold_*/*_trades.csv"],
    },
    {
        "campaign_id": "CAMPAIGN_002",
        "strategy_family": "trend_following",
        "globs": ["backtests/campaign_002_real_oanda/runs/baseline/H4/full/*_trades.csv"],
    },
    {
        "campaign_id": "CAMPAIGN_003",
        "strategy_family": "trend_adx",
        "globs": ["backtests/campaign_003_controlled_adx/runs/baseline/full/*_trades.csv"],
    },
    {
        "campaign_id": "CAMPAIGN_004",
        "strategy_family": "volatility_breakout",
        "globs": ["backtests/campaign_004_volatility_breakout/runs/baseline/full/*_trades.csv"],
    },
    {
        "campaign_id": "CAMPAIGN_007",
        "strategy_family": "pullback",
        "globs": ["backtests/campaign_007_h4_pullback/runs/baseline/full/*_trades.csv"],
    },
]

FOLD_RE = re.compile(r"fold_(\d+)")
SPLIT_RE = re.compile(r"/(train|validation|full|base)/")


def _load_integrity() -> dict[str, str]:
    if not INTEGRITY_PATH.is_file():
        return {}
    data = json.loads(INTEGRITY_PATH.read_text(encoding="utf-8"))
    return {c["campaign_id"]: c["evidence_integrity_status"] for c in data.get("classifications", [])}


def _session_from_hour(hour: int) -> str:
    if 0 <= hour < 7:
        return "asia"
    if 7 <= hour < 12:
        return "london"
    if 12 <= hour < 17:
        return "london_ny_overlap"
    if 17 <= hour < 22:
        return "ny"
    return "asia_late"


def _infer_meta(path: Path) -> dict[str, str | None]:
    s = str(path)
    fold = None
    m = FOLD_RE.search(s)
    if m:
        fold = m.group(1)
    split = None
    if "train" in s:
        split = "train"
    elif "validation" in s:
        split = "validation"
    elif "full" in s:
        split = "full"
    elif "/base/" in s or "/folds/fold_" in s:
        split = "fold"
    cost = "2xcost" if "2xcost" in s else "base"
    return {"fold": fold, "split": split, "cost_regime": cost}


def _collect_trade_paths(globs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in globs:
        paths.extend(sorted(ROOT.glob(pattern)))
    return paths


def _read_trades(paths: list[Path], campaign_id: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in paths:
        try:
            df = pd.read_csv(path)
        except (OSError, pd.errors.EmptyDataError):
            continue
        meta = _infer_meta(path)
        df["campaign_id"] = campaign_id
        df["source_path"] = str(path.relative_to(ROOT))
        df["fold"] = meta["fold"]
        df["split"] = meta["split"]
        df["cost_regime"] = meta["cost_regime"]
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    if "entry_time" in out.columns:
        out["entry_time"] = pd.to_datetime(out["entry_time"], utc=True, errors="coerce")
    if "exit_time" in out.columns:
        out["exit_time"] = pd.to_datetime(out["exit_time"], utc=True, errors="coerce")
    if "entry_time" in out.columns:
        out["session"] = out["entry_time"].dt.hour.map(_session_from_hour)
    if "r_multiple" in out.columns:
        out["winner"] = out["r_multiple"].astype(float) > 0
    return out


def _column_present(df: pd.DataFrame, col: str) -> bool:
    return col in df.columns and df[col].notna().any()


def build_inventory(integrity: dict[str, str]) -> dict[str, Any]:
    campaigns: list[dict[str, Any]] = []
    for spec in CAMPAIGN_TRADE_GLOBS:
        cid = spec["campaign_id"]
        paths = _collect_trade_paths(spec["globs"])
        sample = paths[0] if paths else None
        cols: set[str] = set()
        if sample and sample.is_file():
            cols = set(pd.read_csv(sample, nrows=1).columns)
        status = integrity.get(cid, "UNKNOWN")
        usable = len(paths) > 0 and "exit_reason" in cols and "r_multiple" in cols
        campaigns.append(
            {
                "campaign_id": cid,
                "strategy_family": spec["strategy_family"],
                "evidence_integrity_status": status,
                "artifact_paths_found": len(paths),
                "sample_path": str(sample.relative_to(ROOT)) if sample else None,
                "trade_list_found": len(paths) > 0,
                "exit_reason_available": "exit_reason" in cols,
                "bars_held_available": "bars_held" in cols,
                "r_multiple_available": "r_multiple" in cols,
                "spread_paid_available": "spread_paid_pips" in cols,
                "ambiguous_exit_available": "ambiguous_exit" in cols or "fill_timing" in cols,
                "gap_fill_available": "gap_fill" in cols,
                "stop_price_available": "stop_price" in cols,
                "usable_for_diagnostics": usable,
                "notes": spec.get("notes", ""),
            }
        )
    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "campaigns": campaigns,
    }


def _exit_stats(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty or "exit_reason" not in df.columns:
        return {}
    out: dict[str, Any] = {}
    r = df["r_multiple"].astype(float)
    for reason, grp in df.groupby("exit_reason"):
        gr = grp["r_multiple"].astype(float)
        out[str(reason)] = {
            "count": len(grp),
            "share_pct": round(100.0 * len(grp) / len(df), 2),
            "expectancy_r": round(float(gr.mean()), 4),
            "median_r": round(float(gr.median()), 4),
            "win_rate_pct": round(100.0 * float((gr > 0).mean()), 2),
            "avg_bars_held": round(float(grp["bars_held"].mean()), 2) if "bars_held" in grp else None,
        }
    out["_total_trades"] = len(df)
    out["_overall_exp_r"] = round(float(r.mean()), 4)
    return out


def build_cross_campaign_matrix(integrity: dict[str, str]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    campaign_summaries: dict[str, Any] = {}
    for spec in CAMPAIGN_TRADE_GLOBS:
        cid = spec["campaign_id"]
        paths = _collect_trade_paths(spec["globs"])
        df = _read_trades(paths, cid)
        if df.empty:
            continue
        stats = _exit_stats(df)
        campaign_summaries[cid] = {
            "strategy_family": spec["strategy_family"],
            "evidence_integrity_status": integrity.get(cid, "UNKNOWN"),
            "total_trades": stats.pop("_total_trades", 0),
            "overall_exp_r": stats.pop("_overall_exp_r", None),
            "by_exit_reason": stats,
        }
        for reason, s in stats.items():
            rows.append(
                {
                    "campaign_id": cid,
                    "strategy_family": spec["strategy_family"],
                    "evidence_integrity_status": integrity.get(cid, "UNKNOWN"),
                    "exit_reason": reason,
                    **s,
                }
            )
        # pair x exit for top exits
        if "instrument" in df.columns:
            for (inst, reason), grp in df.groupby(["instrument", "exit_reason"]):
                if len(grp) < 3:
                    continue
                gr = grp["r_multiple"].astype(float)
                rows.append(
                    {
                        "campaign_id": cid,
                        "strategy_family": spec["strategy_family"],
                        "evidence_integrity_status": integrity.get(cid, "UNKNOWN"),
                        "exit_reason": f"{reason}@{inst}",
                        "count": len(grp),
                        "expectancy_r": round(float(gr.mean()), 4),
                        "median_r": round(float(gr.median()), 4),
                        "win_rate_pct": round(100.0 * float((gr > 0).mean()), 2),
                    }
                )
    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "campaign_summaries": campaign_summaries,
        "matrix_rows": rows,
    }


def _load_c008_c009() -> tuple[pd.DataFrame, pd.DataFrame]:
    c8_paths = _collect_trade_paths(CAMPAIGN_TRADE_GLOBS[0]["globs"])
    c9_paths = _collect_trade_paths(CAMPAIGN_TRADE_GLOBS[1]["globs"])
    return _read_trades(c8_paths, "CAMPAIGN_008"), _read_trades(c9_paths, "CAMPAIGN_009")


def build_c008_c009_forensics(c008: pd.DataFrame, c009: pd.DataFrame) -> dict[str, Any]:
    def _cohort(df: pd.DataFrame, split: str, exit_reason: str | None = None, winner: bool | None = None) -> dict[str, Any]:
        sub = df[df["split"] == split] if "split" in df.columns else df
        if exit_reason:
            sub = sub[sub["exit_reason"] == exit_reason]
        if winner is True:
            sub = sub[sub["winner"]]
        elif winner is False:
            sub = sub[~sub["winner"]]
        if sub.empty:
            return {"trade_count": 0}
        r = sub["r_multiple"].astype(float)
        return {
            "trade_count": len(sub),
            "expectancy_r": round(float(r.mean()), 4),
            "median_r": round(float(r.median()), 4),
            "avg_bars_held": round(float(sub["bars_held"].mean()), 2),
            "avg_spread_pips": round(float(sub["spread_paid_pips"].mean()), 3)
            if "spread_paid_pips" in sub
            else None,
            "by_pair": {str(k): int(v) for k, v in sub["instrument"].value_counts().items()},
            "by_session": {str(k): int(v) for k, v in sub["session"].value_counts().items()},
        }

    # C009 midline: trades that exited at target vs C008 time
    c9_target = c009[c009["exit_reason"] == "target"] if not c009.empty else pd.DataFrame()
    c008[c008["exit_reason"] == "time"] if not c008.empty else pd.DataFrame()

    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "c008": {
            "train_stop": _cohort(c008, "train", "stop"),
            "train_time": _cohort(c008, "train", "time"),
            "validation_stop": _cohort(c008, "validation", "stop"),
            "validation_time": _cohort(c008, "validation", "time"),
            "validation_time_winners": _cohort(c008, "validation", "time", winner=True),
            "train_stop_losers": _cohort(c008, "train", "stop", winner=False),
        },
        "c009": {
            "train_by_exit": _exit_stats(c009[c009["split"] == "train"]) if not c009.empty else {},
            "validation_by_exit": _exit_stats(c009[c009["split"] == "validation"]) if not c009.empty else {},
            "target_exit_count": len(c9_target),
            "target_exit_exp_r": round(float(c9_target["r_multiple"].mean()), 4) if len(c9_target) else None,
        },
        "c008_vs_c009_comparison": {
            "c008_validation_time_exp_r": round(
                float(c008.loc[(c008["split"] == "validation") & (c008["exit_reason"] == "time"), "r_multiple"].mean()),
                4,
            )
            if len(c008)
            else None,
            "c009_validation_target_exp_r": round(float(c9_target["r_multiple"].mean()), 4)
            if len(c9_target)
            else None,
            "c009_validation_time_count": len(c009[(c009["split"] == "validation") & (c009["exit_reason"] == "time")])
            if not c009.empty
            else 0,
            "interpretation_note": (
                "C009 added target exits; validation winners shift from C008 time-only to target+time mix. "
                "Train worsened despite higher win rate — target may cap tail winners on some pairs."
            ),
        },
    }


def _stop_distance_pips(row: pd.Series) -> float | None:
    if pd.isna(row.get("entry_price")) or pd.isna(row.get("stop_price")):
        return None
    entry = float(row["entry_price"])
    stop = float(row["stop_price"])
    inst = str(row.get("instrument", ""))
    dist = abs(entry - stop)
    if "JPY" in inst:
        return dist * 100.0
    return dist * 10000.0


def _compute_mae_mfe(trades: pd.DataFrame, repo_root: Path) -> pd.DataFrame:
    db_path = resolve_h4_store_path(repo_root)
    if db_path is None or trades.empty:
        return pd.DataFrame()
    records: list[dict[str, Any]] = []
    cache: dict[str, pd.DataFrame] = {}
    for _, trade in trades.iterrows():
        inst = str(trade["instrument"])
        if inst not in cache:
            frame, _ = load_deduped_h4_frame(repo_root, inst, db_path=db_path)
            cache[inst] = frame
        frame = cache[inst]
        entry_t = trade["entry_time"]
        exit_t = trade["exit_time"]
        if pd.isna(entry_t) or pd.isna(exit_t):
            continue
        window = frame[(frame.index >= entry_t) & (frame.index <= exit_t)]
        if window.empty:
            continue
        entry = float(trade["entry_price"])
        stop = float(trade["stop_price"]) if pd.notna(trade.get("stop_price")) else None
        side = str(trade["side"])
        if side == "long":
            mae_price = float(window["low"].min())
            mfe_price = float(window["high"].max())
            mae = entry - mae_price
            mfe = mfe_price - entry
        else:
            mae_price = float(window["high"].max())
            mfe_price = float(window["low"].min())
            mae = mae_price - entry
            mfe = entry - mfe_price
        stop_dist = abs(entry - stop) if stop is not None else None
        mae_r = mae / stop_dist if stop_dist and stop_dist > 0 else None
        mfe_r = mfe / stop_dist if stop_dist and stop_dist > 0 else None
        records.append(
            {
                "campaign_id": trade.get("campaign_id"),
                "split": trade.get("split"),
                "exit_reason": trade.get("exit_reason"),
                "instrument": inst,
                "side": side,
                "r_multiple": float(trade["r_multiple"]),
                "bars_held": int(trade["bars_held"]),
                "stop_distance_pips": round(_stop_distance_pips(trade) or 0, 2),
                "mae_r": round(mae_r, 4) if mae_r is not None else None,
                "mfe_r": round(mfe_r, 4) if mfe_r is not None else None,
                "reached_1r_favorable": mfe_r is not None and mfe_r >= 1.0,
                "stopped_before_1r_favorable": mae_r is not None and mfe_r is not None and mfe_r < 1.0 and str(trade.get("exit_reason")) == "stop",
            }
        )
    return pd.DataFrame(records)


def build_mae_mfe(c008: pd.DataFrame, c009: pd.DataFrame) -> dict[str, Any]:
    c008_m = _compute_mae_mfe(c008, ROOT)
    c009_m = _compute_mae_mfe(c009, ROOT)

    def _summarize(df: pd.DataFrame, label: str) -> dict[str, Any]:
        if df.empty:
            return {"status": "BLOCKED", "label": label}
        stop = df[df["exit_reason"] == "stop"]
        time_df = df[df["exit_reason"] == "time"]
        target = df[df["exit_reason"] == "target"]
        return {
            "label": label,
            "trades_computed": len(df),
            "stop_trades": len(stop),
            "stop_median_mae_r": round(float(stop["mae_r"].median()), 4) if len(stop) else None,
            "stop_median_mfe_r": round(float(stop["mfe_r"].median()), 4) if len(stop) else None,
            "stop_pct_reached_1r_before_stop": round(
                100.0 * float(stop["reached_1r_favorable"].mean()), 2
            )
            if len(stop)
            else None,
            "stop_pct_never_1r_favorable": round(
                100.0 * float((~stop["reached_1r_favorable"]).mean()), 2
            )
            if len(stop)
            else None,
            "time_trades_median_mfe_r": round(float(time_df["mfe_r"].median()), 4) if len(time_df) else None,
            "time_trades_median_mae_r": round(float(time_df["mae_r"].median()), 4) if len(time_df) else None,
            "target_trades_median_mfe_r": round(float(target["mfe_r"].median()), 4) if len(target) else None,
            "median_stop_distance_pips": round(float(df["stop_distance_pips"].median()), 2),
            "by_split": {
                str(split): {
                    "stop_median_mfe_r": round(float(g[g["exit_reason"] == "stop"]["mfe_r"].median()), 4)
                    if len(g[g["exit_reason"] == "stop"])
                    else None,
                    "time_median_mfe_r": round(float(g[g["exit_reason"] == "time"]["mfe_r"].median()), 4)
                    if len(g[g["exit_reason"] == "time"])
                    else None,
                }
                for split, g in df.groupby("split")
            },
        }

    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "mae_mfe_computed": not c008_m.empty,
        "method": "H4 deduped candles between entry_time and exit_time; R normalized by entry-stop distance",
        "c008": _summarize(c008_m, "CAMPAIGN_008"),
        "c009": _summarize(c009_m, "CAMPAIGN_009"),
        "interpretation": {
            "stops_tight_or_bad_entry": (
                "If stop exits show low MFE (<1R) before stop, entries likely invalid or stop correctly placed. "
                "If high MFE but still stopped, stop may be tight relative to noise."
            ),
            "time_exit_role": "Time exits with high MFE suggest delayed reversion captured after adverse excursion.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "research" / "exit_diagnostics")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    integrity = _load_integrity()
    inventory = build_inventory(integrity)
    matrix = build_cross_campaign_matrix(integrity)
    c008, c009 = _load_c008_c009()
    forensics = build_c008_c009_forensics(c008, c009)
    mae_mfe = build_mae_mfe(c008, c009)

    (args.output_dir / "exit_artifact_inventory.json").write_text(
        json.dumps(inventory, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "cross_campaign_exit_matrix.json").write_text(
        json.dumps(matrix, indent=2) + "\n", encoding="utf-8"
    )
    with (args.output_dir / "cross_campaign_exit_matrix.csv").open("w", encoding="utf-8", newline="") as fh:
        if matrix["matrix_rows"]:
            writer = csv.DictWriter(fh, fieldnames=list(matrix["matrix_rows"][0].keys()))
            writer.writeheader()
            writer.writerows(matrix["matrix_rows"])
    (args.output_dir / "c008_c009_exit_forensics.json").write_text(
        json.dumps(forensics, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "stop_distance_adverse_excursion.json").write_text(
        json.dumps(mae_mfe, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote exit diagnostics to {args.output_dir}")
    usable = sum(1 for c in inventory["campaigns"] if c["usable_for_diagnostics"])
    print(f"  Campaigns with usable trades: {usable}/{len(inventory['campaigns'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

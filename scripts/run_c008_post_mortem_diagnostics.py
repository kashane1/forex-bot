#!/usr/bin/env python3
"""C008/C009 post-mortem diagnostics — read existing artifacts only.

strategy_evidence: false. No retuning. No new backtests.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from research.confluence.grader import grade_confluence
from research.confluence.models import CrossAssetState, TimeframeState
from research.confluence.states import (
    aggregate_d1_from_h4,
    compute_h4_setup,
    compute_timeframe_state,
    resample_h4_to_d1,
)
from research.cost_atlas.loader import load_deduped_h4_frame
from research.cross_asset_features.alignment import align_wide_frame_to_h4, load_normalized_wide
from research.edge_discovery.real_data import resolve_h4_store_path

C008_PAIRS = ("EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF")
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
VAL_END = pd.Timestamp("2025-01-01", tz="UTC")


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


def _weekday_name(ts: pd.Timestamp) -> str:
    return ts.day_name()


def _load_campaign_trades(campaign_dir: Path, split_dirs: tuple[str, ...]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for split in split_dirs:
        pattern = f"backtests/campaign_{campaign_dir}/runs"
        base = ROOT / pattern / split
        if not base.is_dir():
            continue
        for path in sorted(base.glob("*/*_trades.csv")):
            df = pd.read_csv(path)
            df["split"] = split.replace("baseline/", "").replace("base", split)
            if "train" in str(path):
                df["split"] = "train"
            elif "validation" in str(path):
                df["split"] = "validation"
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["entry_time"] = pd.to_datetime(out["entry_time"], utc=True)
    out["exit_time"] = pd.to_datetime(out["exit_time"], utc=True)
    out["hour_utc"] = out["entry_time"].dt.hour
    out["weekday"] = out["entry_time"].map(_weekday_name)
    out["session"] = out["hour_utc"].map(_session_from_hour)
    out["winner"] = out["r_multiple"] > 0
    return out


def _load_c008_trades() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for split in ("train", "validation"):
        for pair in C008_PAIRS:
            path = (
                ROOT
                / "backtests/campaign_008_range_mean_reversion/runs/baseline"
                / split
                / f"baseline_{pair}_H4_{split}_trades.csv"
            )
            if not path.is_file():
                continue
            df = pd.read_csv(path)
            df["split"] = split
            df["campaign"] = "C008"
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["entry_time"] = pd.to_datetime(out["entry_time"], utc=True)
    out["exit_time"] = pd.to_datetime(out["exit_time"], utc=True)
    out["hour_utc"] = out["entry_time"].dt.hour
    out["weekday"] = out["entry_time"].map(_weekday_name)
    out["session"] = out["hour_utc"].map(_session_from_hour)
    out["winner"] = out["r_multiple"] > 0
    return out


def _load_c009_trades() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for split in ("train", "validation"):
        for pair in C008_PAIRS:
            path = (
                ROOT
                / "backtests/campaign_009_mean_reversion/runs"
                / split
                / "base"
                / f"{split}_base_{pair}_H4_trades.csv"
            )
            if not path.is_file():
                continue
            df = pd.read_csv(path)
            df["split"] = split
            df["campaign"] = "C009"
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["entry_time"] = pd.to_datetime(out["entry_time"], utc=True)
    out["exit_time"] = pd.to_datetime(out["exit_time"], utc=True)
    out["hour_utc"] = out["entry_time"].dt.hour
    out["weekday"] = out["entry_time"].map(_weekday_name)
    out["session"] = out["hour_utc"].map(_session_from_hour)
    out["winner"] = out["r_multiple"] > 0
    return out


def _summary_stats(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"trade_count": 0}
    r = df["r_multiple"].astype(float)
    return {
        "trade_count": len(df),
        "expectancy_r": round(float(r.mean()), 4),
        "median_r": round(float(r.median()), 4),
        "win_rate_pct": round(100.0 * float(df["winner"].mean()), 2),
        "profit_factor": round(
            float(df.loc[df["pnl"] > 0, "pnl"].sum() / abs(df.loc[df["pnl"] < 0, "pnl"].sum()))
            if (df["pnl"] < 0).any()
            else None,
            4,
        )
        if (df["pnl"] < 0).any()
        else None,
        "avg_bars_held": round(float(df["bars_held"].mean()), 2),
        "avg_spread_paid_pips": round(float(df["spread_paid_pips"].mean()), 3),
    }


def _bucket_counts(df: pd.DataFrame, col: str) -> dict[str, int]:
    return {str(k): int(v) for k, v in df[col].value_counts().items()}


def _group_stats(df: pd.DataFrame, group_col: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, grp in df.groupby(group_col):
        out[str(key)] = _summary_stats(grp)
    return out


def _outlier_share(df: pd.DataFrame, top_n: int = 5) -> dict[str, Any]:
    if df.empty:
        return {}
    winners = df[df["winner"]].sort_values("r_multiple", ascending=False)
    total_win_r = float(winners["r_multiple"].sum()) if len(winners) else 0.0
    top = winners.head(top_n)
    top_r = float(top["r_multiple"].sum()) if len(top) else 0.0
    return {
        "top_n": top_n,
        "top_n_r_sum": round(top_r, 4),
        "all_winners_r_sum": round(total_win_r, 4),
        "top_n_share_of_winner_r": round(top_r / total_win_r, 4) if total_win_r else 0.0,
    }


def build_trade_anatomy(c008: pd.DataFrame) -> dict[str, Any]:
    train = c008[c008["split"] == "train"]
    val = c008[c008["split"] == "validation"]
    train_losers = train[~train["winner"]]
    val_winners = val[val["winner"]]

    exit_by_split: dict[str, Any] = {}
    for split_name, subset in (("train", train), ("validation", val)):
        exit_by_split[split_name] = {}
        for exit_reason, grp in subset.groupby("exit_reason"):
            exit_by_split[split_name][str(exit_reason)] = _summary_stats(grp)

    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "campaign": "CAMPAIGN_008",
        "strategy_version": "mean_reversion 0.1.0-c008",
        "overall": {
            "train": _summary_stats(train),
            "validation": _summary_stats(val),
            "full_screening": _summary_stats(c008),
        },
        "by_pair": {
            "train": _group_stats(train, "instrument"),
            "validation": _group_stats(val, "instrument"),
        },
        "by_session": {
            "train": _group_stats(train, "session"),
            "validation": _group_stats(val, "session"),
        },
        "by_weekday": {
            "train": _group_stats(train, "weekday"),
            "validation": _group_stats(val, "weekday"),
        },
        "by_side": {
            "train": _group_stats(train, "side"),
            "validation": _group_stats(val, "side"),
        },
        "by_exit_reason": exit_by_split,
        "r_distribution": {
            "train": _bucket_counts(train.assign(r_bucket=pd.cut(train["r_multiple"], bins=[-10, -1, 0, 1, 3, 10])), "r_bucket"),
            "validation": _bucket_counts(
                val.assign(r_bucket=pd.cut(val["r_multiple"], bins=[-10, -1, 0, 1, 3, 10])),
                "r_bucket",
            ),
        },
        "train_losers_vs_validation_winners": {
            "train_losers": _summary_stats(train_losers),
            "validation_winners": _summary_stats(val_winners),
            "train_loser_exit_mix": _bucket_counts(train_losers, "exit_reason"),
            "validation_winner_exit_mix": _bucket_counts(val_winners, "exit_reason"),
            "validation_winner_pair_mix": _bucket_counts(val_winners, "instrument"),
            "validation_winner_session_mix": _bucket_counts(val_winners, "session"),
            "validation_winner_outlier_share": _outlier_share(val),
            "train_loser_spread_pips_mean": round(float(train_losers["spread_paid_pips"].mean()), 3)
            if len(train_losers)
            else None,
            "validation_winner_spread_pips_mean": round(float(val_winners["spread_paid_pips"].mean()), 3)
            if len(val_winners)
            else None,
        },
        "explicit_disclaimer": "Descriptive trade anatomy only. Not strategy evidence.",
    }


def _cross_asset_from_row(row: pd.Series) -> dict[str, Any]:
    def _val(*keys: str) -> float | None:
        for k in keys:
            if k in row.index and pd.notna(row[k]):
                return float(row[k])
        return None

    dxy = _val("broad_usd_index", "dxy")
    vix = _val("vix")
    us10y = _val("us_10y_yield", "us10y")
    spread = _val("us_10y_minus_2y")
    sp500_ret = _val("sp500_1d_return")
    oil_ret = _val("oil_wti_1d_return")
    dxy_chg = _val("broad_usd_index_1d_change")
    vix_chg = _val("vix_1d_change")

    usd = "unknown"
    if dxy is not None:
        usd = "strengthening" if dxy > 97 else "weakening" if dxy < 96 else "neutral"
    risk = "unknown"
    if vix is not None:
        risk = "risk_off" if vix > 25 else "risk_on" if vix < 20 else "neutral"
    rates = "unknown"
    if us10y is not None:
        rates = "higher" if us10y > 1.66 else "flat"
    curve = "unknown"
    if spread is not None:
        curve = "inverted" if spread < 0 else "positive"

    return {
        "usd_regime": usd,
        "risk_regime": risk,
        "rates_bias": rates,
        "yield_curve": curve,
        "vix_level": round(vix, 2) if vix is not None else None,
        "vix_change_bucket": "up" if (vix_chg or 0) > 0 else "down" if vix_chg is not None else "unknown",
        "dxy_change_bucket": "up" if (dxy_chg or 0) > 0 else "down" if dxy_chg is not None else "unknown",
        "sp500_return_sign": "up" if (sp500_ret or 0) > 0 else "down" if sp500_ret is not None else "unknown",
        "oil_return_sign": "up" if (oil_ret or 0) > 0 else "down" if oil_ret is not None else "unknown",
    }


def _join_cross_asset(trades: pd.DataFrame, repo_root: Path) -> pd.DataFrame:
    csv_path = repo_root / "research/cross_asset_features/normalized_features.csv"
    if not csv_path.is_file():
        return trades
    wide = load_normalized_wide(csv_path)
    db_path = resolve_h4_store_path(repo_root)
    if db_path is None:
        return trades

    enriched_rows: list[dict[str, Any]] = []
    for instrument in trades["instrument"].unique():
        inst_trades = trades[trades["instrument"] == instrument]
        frame, _ = load_deduped_h4_frame(repo_root, instrument, db_path=db_path)
        aligned = align_wide_frame_to_h4(frame.index, wide)
        idx_map = {ts: i for i, ts in enumerate(frame.index)}
        for _, trade in inst_trades.iterrows():
            entry = trade["entry_time"]
            if entry not in idx_map:
                # nearest prior bar
                prior = frame.index[frame.index <= entry]
                if len(prior) == 0:
                    continue
                entry = prior[-1]
            i = idx_map[entry]
            row = aligned.iloc[i]
            regime = _cross_asset_from_row(row)
            enriched_rows.append({**trade.to_dict(), **regime})
    if not enriched_rows:
        return trades
    return pd.DataFrame(enriched_rows)


def build_cross_asset_overlay(c008: pd.DataFrame, repo_root: Path) -> dict[str, Any]:
    enriched = _join_cross_asset(c008, repo_root)
    if enriched.empty or "usd_regime" not in enriched.columns:
        return {
            "strategy_evidence": False,
            "diagnostic_only": True,
            "generated_at_utc": datetime.now(tz=UTC).isoformat(),
            "status": "BLOCKED_NO_CROSS_ASSET_JOIN",
            "explicit_disclaimer": "Descriptive regime overlay only.",
        }

    def _regime_mix(subset: pd.DataFrame) -> dict[str, dict[str, int]]:
        cols = ["usd_regime", "risk_regime", "rates_bias", "yield_curve", "sp500_return_sign", "oil_return_sign"]
        return {col: _bucket_counts(subset, col) for col in cols if col in subset.columns}

    train = enriched[enriched["split"] == "train"]
    val = enriched[enriched["split"] == "validation"]
    winners = enriched[enriched["winner"]]
    losers = enriched[~enriched["winner"]]

    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "campaign": "CAMPAIGN_008",
        "trades_joined": len(enriched),
        "regime_mix": {
            "train": _regime_mix(train),
            "validation": _regime_mix(val),
        },
        "winners_vs_losers": {
            "winners": _regime_mix(winners),
            "losers": _regime_mix(losers),
        },
        "by_pair_validation": {
            pair: _regime_mix(enriched[(enriched["split"] == "validation") & (enriched["instrument"] == pair)])
            for pair in C008_PAIRS
        },
        "expectancy_by_usd_regime": {
            split: {
                str(k): round(float(v), 4)
                for k, v in enriched[enriched["split"] == split].groupby("usd_regime")["r_multiple"].mean().items()
            }
            for split in ("train", "validation")
        },
        "explicit_disclaimer": "Descriptive regime overlay only. No edge claims.",
    }


def _cross_asset_state_from_row(row: pd.Series) -> CrossAssetState:
    d = _cross_asset_from_row(row)
    missing = []
    if d["usd_regime"] == "unknown":
        missing.append("dxy")
    if d["risk_regime"] == "unknown":
        missing.append("vix")
    if d["rates_bias"] == "unknown":
        missing.append("us10y")
    return CrossAssetState(
        usd_regime=d["usd_regime"],  # type: ignore[arg-type]
        risk_regime=d["risk_regime"],  # type: ignore[arg-type]
        rates_bias=d["rates_bias"],  # type: ignore[arg-type]
        missing_features=tuple(missing),
    )


def build_confluence_overlay(c008: pd.DataFrame, c009: pd.DataFrame, repo_root: Path) -> dict[str, Any]:
    csv_path = repo_root / "research/cross_asset_features/normalized_features.csv"
    wide = load_normalized_wide(csv_path) if csv_path.is_file() else None
    db_path = resolve_h4_store_path(repo_root)
    if db_path is None or wide is None:
        return {
            "strategy_evidence": False,
            "status": "BLOCKED_NO_H4_OR_FEATURES",
            "explicit_disclaimer": "Descriptive confluence overlay only.",
        }

    def _score_trades(trades: pd.DataFrame, campaign: str) -> list[dict[str, Any]]:
        scores: list[dict[str, Any]] = []
        for instrument in trades["instrument"].unique():
            inst = trades[trades["instrument"] == instrument]
            frame, _ = load_deduped_h4_frame(repo_root, instrument, db_path=db_path)
            d1 = resample_h4_to_d1(frame)
            w1 = aggregate_d1_from_h4(frame)
            w1_state = compute_timeframe_state(w1) if len(w1) >= 60 else "unknown"
            d1_state = compute_timeframe_state(d1) if len(d1) >= 60 else "unknown"
            h4_setup = compute_h4_setup(frame)
            aligned = align_wide_frame_to_h4(frame.index, wide)
            idx_map = {ts: i for i, ts in enumerate(frame.index)}
            for _, trade in inst.iterrows():
                entry = trade["entry_time"]
                if entry not in idx_map:
                    prior = frame.index[frame.index <= entry]
                    if len(prior) == 0:
                        continue
                    entry = prior[-1]
                i = idx_map[entry]
                bar = frame.iloc[i]
                spread_to_atr = float(bar.get("spread_to_atr_pct", 5.0))
                cross = _cross_asset_state_from_row(aligned.iloc[i])
                tf = TimeframeState(w1=w1_state, d1=d1_state, h4_setup=h4_setup, h1_trigger="unknown")
                score = grade_confluence(
                    side=str(trade["side"]),
                    timeframe=tf,
                    cross_asset=cross,
                    cost_spread_to_atr_pct=spread_to_atr,
                    h4_setup_for_mr=True,
                )
                scores.append(
                    {
                        "campaign": campaign,
                        "instrument": instrument,
                        "split": trade["split"],
                        "winner": bool(trade["winner"]),
                        "r_multiple": float(trade["r_multiple"]),
                        "grade": score.grade,
                        "reason_codes": list(score.reason_codes),
                    }
                )
        return scores

    c008_scores = _score_trades(c008, "C008")
    c009_scores = _score_trades(c009, "C009") if not c009.empty else []

    def _summarize(scores: list[dict[str, Any]], *, split: str | None = None, winners_only: bool | None = None) -> dict[str, Any]:
        subset = scores
        if split:
            subset = [s for s in subset if s["split"] == split]
        if winners_only is True:
            subset = [s for s in subset if s["winner"]]
        if winners_only is False:
            subset = [s for s in subset if not s["winner"]]
        grades = Counter(s["grade"] for s in subset)
        reasons = Counter(rc for s in subset for rc in s["reason_codes"])
        exp = (
            round(sum(s["r_multiple"] for s in subset) / len(subset), 4) if subset else None
        )
        return {
            "trade_count": len(subset),
            "expectancy_r": exp,
            "grade_distribution": dict(grades),
            "top_reason_codes": reasons.most_common(10),
        }

    all_c008 = c008_scores
    reason_compare = Counter(rc for s in all_c008 for rc in s["reason_codes"])

    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "c008": {
            "overall": _summarize(all_c008),
            "train": _summarize(all_c008, split="train"),
            "validation": _summarize(all_c008, split="validation"),
            "train_losers": _summarize(all_c008, split="train", winners_only=False),
            "validation_winners": _summarize(all_c008, split="validation", winners_only=True),
        },
        "c009": {
            "overall": _summarize(c009_scores),
            "train": _summarize(c009_scores, split="train"),
            "validation": _summarize(c009_scores, split="validation"),
        }
        if c009_scores
        else {"status": "no_c009_trades"},
        "top_reason_codes_c008": reason_compare.most_common(15),
        "explicit_disclaimer": (
            "Descriptive confluence overlay. Not A-grade profitability claim. Not strategy evidence."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="C008 post-mortem diagnostics")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "research" / "c008_post_mortem")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    c008 = _load_c008_trades()
    c009 = _load_c009_trades()
    if c008.empty:
        print("BLOCKED: no C008 trade CSVs found locally", file=sys.stderr)
        return 2

    anatomy = build_trade_anatomy(c008)
    regime = build_cross_asset_overlay(c008, ROOT)
    confluence = build_confluence_overlay(c008, c009, ROOT)

    (args.output_dir / "c008_trade_anatomy.json").write_text(
        json.dumps(anatomy, indent=2, default=str) + "\n", encoding="utf-8"
    )
    (args.output_dir / "c008_cross_asset_regime_overlay.json").write_text(
        json.dumps(regime, indent=2, default=str) + "\n", encoding="utf-8"
    )
    (args.output_dir / "c008_confluence_overlay.json").write_text(
        json.dumps(confluence, indent=2, default=str) + "\n", encoding="utf-8"
    )
    print(f"Wrote diagnostics to {args.output_dir}")
    print(f"  C008 trades: {len(c008)} train={len(c008[c008['split']=='train'])} val={len(c008[c008['split']=='validation'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

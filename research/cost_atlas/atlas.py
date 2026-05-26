"""Aggregate cost atlas and flag hostile windows."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from research.backtrader_lane.fold_windows import load_fold_plan
from research.cost_atlas.loader import SEVEN_PAIR_UNIVERSE, load_deduped_h4_frame
from research.cost_atlas.metrics import compute_bar_metrics


def _agg_stats(series: pd.Series) -> dict[str, float]:
    s = series.dropna()
    if s.empty:
        return {"count": 0.0}
    return {
        "count": float(len(s)),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "p90": float(s.quantile(0.90)),
        "p95": float(s.quantile(0.95)),
        "max": float(s.max()),
    }


def assign_fold_index(ts: datetime, fold_ranges: list[tuple[int, date, date]]) -> int | None:
    d = ts.astimezone(UTC).date() if ts.tzinfo else ts.date()
    for fold_idx, start, end in fold_ranges:
        if start <= d <= end:
            return fold_idx
    return None


def aggregate_group(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for keys, grp in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys, strict=True))
        row.update(_agg_stats(grp["spread_pips"]))
        row["spread_pips_median"] = row.pop("median", None)
        spread_atr = grp["spread_to_atr_pct"]
        sa = _agg_stats(spread_atr)
        row["spread_to_atr_pct_mean"] = sa.get("mean")
        row["spread_to_atr_pct_median"] = sa.get("median")
        row["spread_to_atr_pct_p90"] = sa.get("p90")
        row["spread_to_atr_pct_p95"] = sa.get("p95")
        rows.append(row)
    return pd.DataFrame(rows)


def flag_cost_hostile_cells(
    pair_session_df: pd.DataFrame,
    *,
    top_decile_quantile: float = 0.90,
    p90_multiplier: float = 1.5,
) -> list[dict[str, Any]]:
    """Flag cells in top decile spread/ATR or abnormal p90/p95."""
    if pair_session_df.empty:
        return []
    metric = pair_session_df["spread_to_atr_pct_median"].astype(float)
    threshold = float(metric.quantile(top_decile_quantile))
    global_p90 = float(metric.quantile(0.90))
    hostile: list[dict[str, Any]] = []
    for _, row in pair_session_df.iterrows():
        med = float(row.get("spread_to_atr_pct_median", 0) or 0)
        p90 = float(row.get("spread_to_atr_pct_p90", 0) or 0)
        reasons: list[str] = []
        if med >= threshold:
            reasons.append("top_decile_spread_to_atr")
        if p90 >= global_p90 * p90_multiplier:
            reasons.append("elevated_p90_spread_to_atr")
        if med >= float(row.get("spread_to_atr_pct_p95", med)):
            reasons.append("median_near_p95")
        if reasons:
            hostile.append(
                {
                    "instrument": row.get("instrument"),
                    "session": row.get("session"),
                    "weekday": row.get("weekday"),
                    "vol_regime": row.get("vol_regime"),
                    "fold_index": row.get("fold_index"),
                    "spread_to_atr_pct_median": med,
                    "reasons": reasons,
                }
            )
    return hostile


def classify_cost_state(
    spread_to_atr_pct: float,
    *,
    acceptable_max: float = 8.0,
    marginal_max: float = 12.0,
) -> str:
    """Map spread/ATR pct to cost state (aligns with paper.yaml max_spread_to_atr_pct=8)."""
    if spread_to_atr_pct != spread_to_atr_pct:  # NaN
        return "unknown"
    if spread_to_atr_pct <= acceptable_max:
        return "acceptable"
    if spread_to_atr_pct <= marginal_max:
        return "marginal"
    return "hostile"


@dataclass
class AtlasBuildResult:
    summary: dict[str, Any]
    hostile_windows: list[dict[str, Any]]
    pair_session_csv: pd.DataFrame
    all_bars: pd.DataFrame = field(repr=False)
    provenance: list[dict[str, Any]] = field(default_factory=list)
    data_kind: str = "real"


def build_cost_atlas(
    repo_root: Path,
    *,
    instruments: tuple[str, ...] = SEVEN_PAIR_UNIVERSE,
    fold_plan_path: Path | None = None,
    db_path: Path | None = None,
) -> AtlasBuildResult:
    fold_ranges: list[tuple[int, date, date]] = []
    if fold_plan_path is None:
        fold_plan_path = (
            repo_root / "backtests" / "CAMPAIGN_011_random_entry_anchor" / "walk_forward" / "plan.json"
        )
    if fold_plan_path.is_file():
        plan = load_fold_plan(fold_plan_path)
        fold_ranges = [(f.fold_index, f.test_start, f.test_end) for f in plan.folds]

    pieces: list[pd.DataFrame] = []
    provenance: list[dict[str, Any]] = []
    for instrument in instruments:
        frame, prov = load_deduped_h4_frame(repo_root, instrument, db_path=db_path)
        metrics = compute_bar_metrics(instrument, frame)
        metrics["instrument"] = instrument
        if fold_ranges:
            metrics["fold_index"] = metrics.index.map(
                lambda ts: assign_fold_index(ts.to_pydatetime(), fold_ranges)
            )
        else:
            metrics["fold_index"] = None
        pieces.append(metrics)
        provenance.append(prov)

    all_bars = pd.concat(pieces, ignore_index=False)
    all_bars["cost_state"] = all_bars["spread_to_atr_pct"].map(
        lambda v: classify_cost_state(float(v)) if pd.notna(v) else "unknown"
    )

    pair_session = aggregate_group(all_bars, ["instrument", "session"])
    pair_weekday = aggregate_group(all_bars, ["instrument", "weekday"])
    pair_vol = aggregate_group(all_bars, ["instrument", "vol_regime"])
    session_vol = aggregate_group(all_bars, ["session", "vol_regime"])
    pair_fold = (
        aggregate_group(all_bars.dropna(subset=["fold_index"]), ["instrument", "fold_index"])
        if all_bars["fold_index"].notna().any()
        else pd.DataFrame()
    )

    hostile = flag_cost_hostile_cells(pair_session)
    rollover_hostile = all_bars[all_bars["rollover_adjacent"]]["spread_to_atr_pct"].median()
    summary = {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "instruments": list(instruments),
        "bar_count": len(all_bars),
        "dedupe_policy": "keep_last",
        "fold_plan": str(fold_plan_path) if fold_plan_path.is_file() else None,
        "global_spread_pips": _agg_stats(all_bars["spread_pips"]),
        "global_spread_to_atr_pct": _agg_stats(all_bars["spread_to_atr_pct"]),
        "cost_state_counts": all_bars["cost_state"].value_counts().to_dict(),
        "session_counts": all_bars["session"].value_counts().to_dict(),
        "pair_session_rows": len(pair_session),
        "hostile_cell_count": len(hostile),
        "rollover_adjacent_median_spread_to_atr_pct": float(rollover_hostile)
        if pd.notna(rollover_hostile)
        else None,
        "aggregations": {
            "pair_session": pair_session.to_dict(orient="records"),
            "pair_weekday": pair_weekday.to_dict(orient="records"),
            "pair_vol_regime": pair_vol.to_dict(orient="records"),
            "session_vol_regime": session_vol.to_dict(orient="records"),
            "pair_fold": pair_fold.to_dict(orient="records") if not pair_fold.empty else [],
        },
        "future_gating_recommendations": [
            "Reject or downgrade entries when cost_state == hostile",
            "Apply session-specific spread/ATR caps from pair_session p90",
            "Avoid rollover-adjacent windows when median spread/ATR exceeds global p90",
        ],
    }
    return AtlasBuildResult(
        summary=summary,
        hostile_windows=hostile,
        pair_session_csv=pair_session,
        all_bars=all_bars,
        provenance=provenance,
        data_kind="real",
    )


def write_cost_atlas_outputs(result: AtlasBuildResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "cost_atlas_summary.json").write_text(
        json.dumps(result.summary, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    (output_dir / "cost_hostile_windows.json").write_text(
        json.dumps(
            {
                "strategy_evidence": False,
                "diagnostic_only": True,
                "hostile_windows": result.hostile_windows,
            },
            indent=2,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )
    result.pair_session_csv.to_csv(output_dir / "pair_session_spread_atr.csv", index=False)

"""Real-data study — session / time-of-day forward returns on real
H4 OHLC, with a synthetic-fallback path for fresh-clone CI.

For each H4 close in the available candle frame, compute a fixed
forward-window LONG log-return and bin by UTC hour-of-day. The H4
universe always closes at one of six UTC hours (02, 06, 10, 14, 18,
22); the study answers "is any session systematically above the
random-entry null on this pair, post-cost?"

This is a capability + descriptive study. It does NOT test
significance. The lab's null comparison gives a within-null vs
materially-above-null band.

Real-data path:
  * H4 OHLC: data/campaign_002.sqlite3 (operator-local; resolved via
    research.edge_discovery.real_data.resolve_h4_store_path).
  * Instrument: EUR_USD (full coverage 2020-01-01 → 2026-05-19).

Synthetic-fallback path (used when the real store is unavailable):
  * H4 OHLC: research/edge_discovery/sample_fixtures/
            synthetic_EUR_USD_H4.csv (480 bars).

Output: research/edge_discovery/studies/outputs/real/
        real_study_session_by_hour.{json,md}

The provenance block makes the fallback explicit
(``data_kind = "synthetic-fallback"``) — never silently substitute.

Exploratory lab output. Not strategy evidence.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from research.edge_discovery.costs import apply_cost_overlay
from research.edge_discovery.loaders import CandleSample, load_candles_csv
from research.edge_discovery.null import random_null_baseline
from research.edge_discovery.real_data import (
    StudyInput,
    StudyProvenance,
    assert_real_data_kind,
    load_h4_candles_from_sqlite,
    resolve_h4_store_path,
)
from research.edge_discovery.windows import Side, compute_forward_returns

REPO_ROOT = Path(__file__).resolve().parents[3]
SYNTHETIC_H4 = REPO_ROOT / "research" / "edge_discovery" / "sample_fixtures" / "synthetic_EUR_USD_H4.csv"
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs" / "real"

PAIR = "EUR_USD"
WINDOW_BARS = 4  # H4 * 4 = 16 hours forward
SIDE = Side.LONG
SEEDS = tuple(range(20))
MATERIAL_STDS = 1.5  # band threshold in null-std units


@dataclass(frozen=True)
class HydrationResult:
    sample: CandleSample
    data_kind: str  # "real" or "synthetic-fallback"
    fallback_reason: str | None


def _hydrate_candles() -> HydrationResult:
    """Try to load the real H4 EUR_USD slice from the SQLite store.
    Fall back to the synthetic 480-bar fixture if the store is
    unavailable, with the reason captured for the provenance block."""
    db_path = resolve_h4_store_path(REPO_ROOT)
    if db_path is None:
        sample = load_candles_csv(SYNTHETIC_H4)
        return HydrationResult(
            sample=sample,
            data_kind="synthetic-fallback",
            fallback_reason="H4 SQLite store not found at any candidate path "
            "(data/campaign_002.sqlite3, $EDGE_DISCOVERY_H4_DB, or worktree-relative)",
        )
    try:
        sample = load_h4_candles_from_sqlite(db_path, PAIR)
    except (FileNotFoundError, ValueError) as exc:
        sample = load_candles_csv(SYNTHETIC_H4)
        return HydrationResult(
            sample=sample,
            data_kind="synthetic-fallback",
            fallback_reason=f"H4 SQLite load failed: {exc!s}",
        )
    return HydrationResult(sample=sample, data_kind="real", fallback_reason=None)


def run() -> Path:
    hyd = _hydrate_candles()
    sample = hyd.sample

    # Each H4 close is a "signal"; the side is fixed LONG. The label
    # is the UTC hour-of-day so the by-group breakdown lights up
    # automatically.
    times = sample.frame.index
    labels = [f"UTC_{ts.hour:02d}" for ts in times]
    fr = compute_forward_returns(
        sample.frame,
        list(times),
        window_bars=WINDOW_BARS,
        side=SIDE,
        labels=labels,
    )
    if fr.n_signals == 0:
        per_hour: dict[str, dict[str, float]] = {}
        overall_mean = 0.0
        with_costs = pd.DataFrame()
        null = None
    else:
        with_costs = apply_cost_overlay(fr.per_signal, sample.instrument)
        null = random_null_baseline(
            sample.frame,
            n_trades=max(len(with_costs), 1),
            window_bars=WINDOW_BARS,
            seeds=SEEDS,
            apply_cost_overlay_fn=apply_cost_overlay,
            instrument=sample.instrument,
        )

        per_hour = {}
        for hour_label, sub in with_costs.groupby("label"):
            r = sub["log_return_post_cost"].astype(float)
            per_hour[str(hour_label)] = {
                "n": len(sub),
                "mean_post_cost": float(r.mean()),
                "std_post_cost": float(r.std(ddof=1)) if len(sub) > 1 else 0.0,
                "median_post_cost": float(r.median()),
                "win_rate": float((r > 0).mean()),
            }
        overall_mean = float(with_costs["log_return_post_cost"].mean())

    null_mean = float(null.mean_of_means) if null is not None else 0.0
    null_std = float(null.std_of_means) if null is not None else 0.0
    overall_band = (
        "within_null"
        if null is None or null_std == 0 or abs(overall_mean - null_mean) < MATERIAL_STDS * null_std
        else (
            "materially_above_null"
            if overall_mean > null_mean
            else "materially_below_null"
        )
    )

    # Per-hour band classification.
    per_hour_bands: dict[str, str] = {}
    if null_std > 0:
        for hour_label, stats in per_hour.items():
            gap = stats["mean_post_cost"] - null_mean
            if abs(gap) < MATERIAL_STDS * null_std:
                per_hour_bands[hour_label] = "within_null"
            elif gap > 0:
                per_hour_bands[hour_label] = "materially_above_null"
            else:
                per_hour_bands[hour_label] = "materially_below_null"
    else:
        for hour_label in per_hour:
            per_hour_bands[hour_label] = "within_null"

    # Build provenance — real or synthetic-fallback.
    if hyd.data_kind == "real":
        inputs = [
            StudyInput(
                kind="h4_sqlite_store",
                path=sample.source_path,
                sha256=sample.source_sha256[:64],
                rows=sample.row_count,
                extra={"instrument": PAIR, "granularity": "H4"},
            ),
        ]
        limitations = [
            "Each H4 bar contributes one signal; per-hour samples are "
            "large (>1,000 per hour over the full 2020-2026 universe) "
            "but each is heavily auto-correlated with its neighbors.",
            "This study uses LONG-side forward returns only. A "
            "complement run with SHORT side (or two-sided) would be a "
            "follow-up.",
            "Post-cost = mid-close return minus the lab's "
            "EUR_USD-shaped spread + slip overlay; this is not the "
            "exact cost model the formal campaigns use for evidence — "
            "see research/edge_discovery/costs.py.",
            "Lab output only. Does not approve any strategy or change "
            "any campaign verdict.",
        ]
    else:
        inputs = [
            StudyInput(
                kind="candle_csv",
                path=str(SYNTHETIC_H4.relative_to(REPO_ROOT)),
                sha256=sample.source_sha256,
                rows=sample.row_count,
                extra={"instrument": PAIR, "granularity": "H4", "synthetic": True},
            ),
        ]
        limitations = [
            f"Synthetic-fallback: {hyd.fallback_reason}. The numbers "
            "below describe a 480-bar GBM fixture and are NOT a real-data "
            "session study.",
            "To rerun on real data, set $EDGE_DISCOVERY_H4_DB to a valid "
            "campaign_002.sqlite3 path, or create the canonical symlink "
            "at data/campaign_002.sqlite3 and re-execute this script.",
            "Lab output only. Does not approve any strategy or change "
            "any campaign verdict.",
        ]

    prov = StudyProvenance(
        data_kind=hyd.data_kind,
        inputs=inputs,
        date_coverage={
            "start_utc": str(sample.frame.index.min()) if len(sample.frame) else "",
            "end_utc": str(sample.frame.index.max()) if len(sample.frame) else "",
        },
        pair_universe=[PAIR],
        limitations=limitations,
        exploratory_only=True,
    )
    assert_real_data_kind(prov)

    payload = {
        "study_label": "real_session_by_hour",
        "instrument": PAIR,
        "granularity": "H4",
        "window_bars": WINDOW_BARS,
        "side": SIDE.name,
        "n_signals": int(fr.n_signals),
        "dropped_trailing": int(fr.dropped_trailing),
        "overall_mean_post_cost": overall_mean,
        "null_mean": null_mean,
        "null_std": null_std,
        "material_band_threshold_stds": MATERIAL_STDS,
        "overall_band": overall_band,
        "per_hour": per_hour,
        "per_hour_bands": per_hour_bands,
        "provenance": prov.to_dict(),
        "verdict_word_ban_acknowledged": True,
        "notes": [
            "If a session bin lands `materially_above_null` for many "
            "years on a real H4 store, that is worth a deeper look — "
            "but never a strategy approval directly from this output.",
            "A follow-up study should sweep PAIR over the seven majors "
            "and emit one row per (pair, hour) so the cross-pair signal "
            "is visible.",
        ],
    }

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUTS / "real_study_session_by_hour.json"
    md_path = OUTPUTS / "real_study_session_by_hour.md"
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    _write_markdown(md_path, payload)
    return md_path


def _write_markdown(md_path: Path, p: dict[str, object]) -> None:
    lines: list[str] = []
    lines.append(f"# Edge-discovery study (real data) — {p['study_label']}")
    lines.append("")
    lines.append("> Exploratory lab output. Not a strategy verdict; does not approve,")
    lines.append("> promote, or change any campaign status.")
    lines.append("")
    lines.append("## Provenance")
    prov = p["provenance"]
    lines.append(f"- data_kind: `{prov['data_kind']}`")
    lines.append(f"- pair universe: `{prov['pair_universe']}`")
    lines.append(f"- date coverage: `{prov['date_coverage']['start_utc']}` → `{prov['date_coverage']['end_utc']}`")
    lines.append("- inputs:")
    for i in prov["inputs"]:
        lines.append(f"  - `{i['kind']}` — `{i['path']}` — rows=`{i['rows']}` — sha256=`{i['sha256'][:16]}…`")
    lines.append("- limitations:")
    for limit in prov["limitations"]:
        lines.append(f"  - {limit}")
    lines.append("")
    lines.append("## Aggregate")
    lines.append("")
    lines.append(f"- Instrument: `{p['instrument']}`, Granularity: `{p['granularity']}`, Forward window: `{p['window_bars']}` bars")
    lines.append(f"- Side: `{p['side']}`, signals used: `{p['n_signals']}`")
    lines.append(f"- Overall mean post-cost: **`{p['overall_mean_post_cost']:+.6f}`**")
    lines.append(f"- Null mean: **`{p['null_mean']:+.6f}`**, null std: `{p['null_std']:.6f}`")
    lines.append(f"- Material-band threshold: `{p['material_band_threshold_stds']}` null stds → overall band: **`{p['overall_band']}`**")
    lines.append("")
    lines.append("## Per-UTC-hour breakdown")
    lines.append("")
    lines.append("| hour | n | mean post-cost | std | median | win rate | band |")
    lines.append("|---|---:|---:|---:|---:|---:|---|")
    per_hour = p["per_hour"]
    per_hour_bands = p["per_hour_bands"]
    for hour in sorted(per_hour.keys()):
        stats = per_hour[hour]
        band = per_hour_bands.get(hour, "?")
        lines.append(
            f"| {hour} | {int(stats['n'])} | {stats['mean_post_cost']:+.6f} | "
            f"{stats['std_post_cost']:.6f} | {stats['median_post_cost']:+.6f} | "
            f"{stats['win_rate']:.3f} | {band} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    for n in p["notes"]:
        lines.append(f"- {n}")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    out = run()
    print(f"wrote {out}")

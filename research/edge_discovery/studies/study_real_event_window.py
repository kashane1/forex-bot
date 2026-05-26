"""Real-data study — CAMPAIGN_014 event-window continuation vs reversal.

Replaces the prior synthetic event-window study's input fixtures with
the committed real artifacts:

  * trades:  committed CAMPAIGN_014 per-fold per-pair trade CSVs (real
             event-window-triggered entries over 2021-06-24 → 2026-05-19)
  * events:  research/calendar/fixtures/campaign_014_events.json
             (281 events × 5 classes, official sources)
  * null:    CAMPAIGN_011 deduped canonical null rollup (the
             binding null baseline per CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)

Each executed trade is matched to its nearest event in the fixture
(within a ±24 h tolerance window — H4 bar size × 6 bars on either
side). Trades that don't match any event in that window are reported
separately under ``unattributed`` so the dominance-share and per-class
breakdown are honest.

Output: research/edge_discovery/studies/outputs/real/
        real_study_event_window.{json,md}

Exploratory lab output. Not strategy evidence. The CAMPAIGN_014
campaign verdict (REJECT) is not changed by this study. Per the
verdict-word ban, this script may not write ``APPROVE`` / ``PASS`` /
``PROMOTE``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from research.edge_discovery.real_data import (
    SEVEN_MAJORS,
    StudyInput,
    StudyProvenance,
    _sha256_of_path,
    assert_real_data_kind,
    load_campaign_trades,
    load_canonical_null_baseline_rollup,
    load_event_fixture_json,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
CAMPAIGN_014_DIR = REPO_ROOT / "backtests" / "CAMPAIGN_014_calendar_event_window_anomaly"
CANONICAL_NULL_JSON = (
    REPO_ROOT / "research" / "null_baselines" / "campaign_011_deduped_null_baseline.json"
)
EVENTS_PATH = REPO_ROOT / "research" / "calendar" / "fixtures" / "campaign_014_events.json"
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs" / "real"

# H4 ±6 bars = ±24 hours. The CAMPAIGN_014 strategy fires on a
# pre-event window (per its IMPLEMENTATION_SPEC) and exits inside a
# fixed post-event window, so a trade's entry should be within a day
# of its triggering event.
MATCH_TOLERANCE = pd.Timedelta(hours=24)

# Material gap (R units) above the CAMPAIGN_011 null per the lab's
# ranking rules §1.4 (and CAMPAIGN_011_NULL_BASELINE_INTERPRETATION
# §2.1's aggregate-R 0.05 floor).
MATERIAL_GAP_R = 0.05


def _match_trade_to_event(
    trade_entry: pd.Timestamp,
    events_index: pd.DatetimeIndex,
    events_classes: list[str],
    tolerance: pd.Timedelta,
) -> str | None:
    """Find the event class whose ``event_time_utc`` is closest to the
    trade's ``entry_time``, within the tolerance window.

    Returns ``None`` if the nearest event is further away than
    ``tolerance`` — those trades are reported under the
    ``unattributed`` bucket.
    """
    if len(events_index) == 0:
        return None
    pos = events_index.searchsorted(trade_entry, side="left")
    candidates: list[int] = []
    if pos < len(events_index):
        candidates.append(int(pos))
    if pos > 0:
        candidates.append(int(pos - 1))
    best_pos = None
    best_delta: pd.Timedelta | None = None
    for c in candidates:
        delta = abs(events_index[c] - trade_entry)
        if best_delta is None or delta < best_delta:
            best_delta = delta
            best_pos = c
    if best_pos is None or best_delta is None or best_delta > tolerance:
        return None
    return events_classes[best_pos]


def _per_class_breakdown(labeled: pd.DataFrame) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for cls, sub in labeled.groupby("event_class"):
        r = sub["r_multiple"].astype(float)
        out[str(cls)] = {
            "n": len(sub),
            "mean_r": float(r.mean()),
            "median_r": float(r.median()),
            "win_rate": float((r > 0).mean()),
            "long_share": float((sub["side"].astype(str) == "long").mean()),
            "average_spread_paid_pips": float(sub["spread_paid_pips"].astype(float).mean()),
        }
    return out


def _dominance_share(breakdown: dict[str, dict[str, float]]) -> dict[str, float]:
    total = sum(int(v["n"]) for v in breakdown.values()) or 1
    return {k: int(v["n"]) / total for k, v in breakdown.items()}


def _zero_trade_classes(present: list[str], breakdown: dict[str, dict[str, float]]) -> list[str]:
    return sorted(set(present) - set(breakdown.keys()))


def run() -> Path:
    # ---- load real inputs ---------------------------------------------------
    trades = load_campaign_trades(CAMPAIGN_014_DIR)
    events = load_event_fixture_json(EVENTS_PATH)
    null_rollup = load_canonical_null_baseline_rollup(CANONICAL_NULL_JSON)

    # ---- assign event class to every trade ----------------------------------
    events_index = events.frame.index
    events_classes_list = events.frame["event_class"].tolist()
    labeled_rows = []
    unattributed_n = 0
    for _, t in trades.iterrows():
        cls = _match_trade_to_event(t["entry_time"], events_index, events_classes_list, MATCH_TOLERANCE)
        if cls is None:
            unattributed_n += 1
            continue
        labeled_rows.append({**t.to_dict(), "event_class": cls})
    labeled = pd.DataFrame(labeled_rows)

    # ---- per-class breakdown ------------------------------------------------
    breakdown = _per_class_breakdown(labeled) if not labeled.empty else {}
    dominance = _dominance_share(breakdown)
    zero_classes = _zero_trade_classes(list(events.classes), breakdown)

    # ---- continuation vs reversal -------------------------------------------
    # Each trade in CAMPAIGN_014's trades CSV already encodes side
    # (long/short). The expected-direction analysis: per event class,
    # how often did long trades win vs short trades.
    cont_rev: dict[str, dict[str, float]] = {}
    if not labeled.empty:
        for cls, sub in labeled.groupby("event_class"):
            long_rows = sub[sub["side"].astype(str) == "long"]
            short_rows = sub[sub["side"].astype(str) == "short"]
            cont_rev[str(cls)] = {
                "n_long": len(long_rows),
                "n_short": len(short_rows),
                "long_mean_r": float(long_rows["r_multiple"].astype(float).mean()) if len(long_rows) else 0.0,
                "short_mean_r": float(short_rows["r_multiple"].astype(float).mean()) if len(short_rows) else 0.0,
                "long_win_rate": float((long_rows["r_multiple"].astype(float) > 0).mean()) if len(long_rows) else 0.0,
                "short_win_rate": float((short_rows["r_multiple"].astype(float) > 0).mean()) if len(short_rows) else 0.0,
            }

    # ---- null-baseline comparison ------------------------------------------
    # Use the published CAMPAIGN_011 aggregate expectancy R as the null
    # band centre. Compute the gap between CAMPAIGN_014's overall mean R
    # and the CAMPAIGN_011 null.
    null_mean_r = float(null_rollup["aggregate"]["aggregate_expectancy_r"])
    overall_r = float(trades["r_multiple"].astype(float).mean()) if len(trades) else 0.0
    gap_r = overall_r - null_mean_r
    band = (
        "materially_below_null" if gap_r <= -MATERIAL_GAP_R
        else "materially_above_null" if gap_r >= MATERIAL_GAP_R
        else "within_null"
    )

    # ---- provenance ---------------------------------------------------------
    prov = StudyProvenance(
        data_kind="real",
        inputs=[
            StudyInput(
                kind="campaign_trades",
                path=str(Path(CAMPAIGN_014_DIR).relative_to(REPO_ROOT)),
                sha256="(per-fold per-pair CSV bundle; see fold_detail.json)",
                rows=len(trades),
                extra={"campaign_name": CAMPAIGN_014_DIR.name, "tolerance_hours": int(MATCH_TOLERANCE.total_seconds() // 3600)},
            ),
            StudyInput(
                kind="event_fixture_json",
                path=str(EVENTS_PATH.relative_to(REPO_ROOT)),
                sha256=events.source_sha256,
                rows=events.event_count,
                extra={"classes": list(events.classes)},
            ),
            StudyInput(
                kind="canonical_null_baseline_rollup",
                path=str(CANONICAL_NULL_JSON.relative_to(REPO_ROOT)),
                sha256=_sha256_of_path(CANONICAL_NULL_JSON),
                rows=int(null_rollup["aggregate"]["total_trades"]),
                extra={
                    "role": "null_baseline",
                    "campaign_id": null_rollup.get("campaign_id"),
                    "dedupe_policy": null_rollup.get("data_dedupe_policy"),
                },
            ),
        ],
        date_coverage={
            "start_utc": str(trades["entry_time"].min()) if len(trades) else "",
            "end_utc": str(trades["exit_time"].max()) if len(trades) else "",
        },
        pair_universe=sorted(set(trades["instrument"].astype(str)) & set(SEVEN_MAJORS)),
        limitations=[
            "CPI events are NOT in the committed fixture — coverage is "
            "NFP / FOMC / ECB / BoJ / BoE only.",
            "Per-trade event class is matched by nearest event within "
            f"±{int(MATCH_TOLERANCE.total_seconds() // 3600)}h; trades that "
            "don't fall within any event window are bucketed as "
            "'unattributed' rather than dropped silently.",
            "This study aggregates over CAMPAIGN_014's published trades — "
            "it does NOT re-execute any backtest, change the CAMPAIGN_014 "
            "REJECT verdict, or claim strategy evidence.",
            "The null baseline is the CAMPAIGN_011 published "
            f"aggregate_expectancy_r ({null_mean_r:+.4f}); the lab does NOT regenerate "
            "the null here.",
        ],
        exploratory_only=True,
    )
    assert_real_data_kind(prov)

    payload: dict[str, object] = {
        "study_label": "real_event_window_continuation_vs_reversal",
        "campaign_source": CAMPAIGN_014_DIR.name,
        "null_source": str(null_rollup.get("campaign_id", "CAMPAIGN_011")),
        "n_trades": len(trades),
        "n_trades_unattributed": int(unattributed_n),
        "n_trades_labeled": len(labeled),
        "overall_mean_r": overall_r,
        "null_mean_r": null_mean_r,
        "gap_r": gap_r,
        "band": band,
        "material_gap_r_floor": MATERIAL_GAP_R,
        "per_class_breakdown": breakdown,
        "dominance_share": dominance,
        "zero_trade_event_classes_in_fixture": zero_classes,
        "continuation_vs_reversal_by_class": cont_rev,
        "provenance": prov.to_dict(),
        "verdict_word_ban_acknowledged": True,
        "notes": [
            "Exploratory output only — does not approve any strategy.",
            "CAMPAIGN_014 remains REJECT; this study aggregates its "
            "published trades.",
            "Lab graduation criteria for any future event-window candidate "
            "require gap_r >= +0.05 R AND a non-dominant per-class "
            "distribution (see EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md).",
        ],
    }

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUTS / "real_study_event_window.json"
    md_path = OUTPUTS / "real_study_event_window.md"
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    _write_markdown(md_path, payload)
    return md_path


def _write_markdown(md_path: Path, p: dict[str, object]) -> None:
    lines: list[str] = []
    lines.append(f"# Edge-discovery study (real data) — {p['study_label']}")
    lines.append("")
    lines.append("> Exploratory lab output. Not a strategy verdict; does not approve,")
    lines.append("> promote, or change any campaign status. CAMPAIGN_014 remains")
    lines.append("> REJECT and CAMPAIGN_011 remains the null model.")
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
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
    lines.append("## Aggregate vs CAMPAIGN_011 null")
    lines.append("")
    lines.append(f"- CAMPAIGN_014 overall mean R: **`{p['overall_mean_r']:+.4f}`**")
    lines.append(f"- CAMPAIGN_011 null mean R: **`{p['null_mean_r']:+.4f}`**")
    lines.append(f"- Gap: **`{p['gap_r']:+.4f}` R** → band: **`{p['band']}`**")
    lines.append(f"- Material-gap floor: `{p['material_gap_r_floor']:+.2f}` R")
    lines.append("")
    lines.append("## Per-class breakdown (matched within ±24h of an event)")
    lines.append("")
    lines.append("| class | n | mean R | median R | win rate | long share | avg spread (pips) | dominance % |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for cls in sorted(p["per_class_breakdown"].keys()):
        row = p["per_class_breakdown"][cls]
        share = p["dominance_share"].get(cls, 0.0)
        lines.append(
            f"| {cls} | {int(row['n'])} | {row['mean_r']:+.4f} | {row['median_r']:+.4f} | "
            f"{row['win_rate']:.3f} | {row['long_share']:.3f} | "
            f"{row['average_spread_paid_pips']:.2f} | {share:.3f} |"
        )
    lines.append("")
    lines.append(f"- Trades unattributed to any event window: **{p['n_trades_unattributed']}** / {p['n_trades']}")
    lines.append(
        f"- Event classes in fixture with zero matched trades: "
        f"`{p['zero_trade_event_classes_in_fixture']}`"
    )
    lines.append("")
    lines.append("## Continuation vs reversal (long vs short by class)")
    lines.append("")
    lines.append("| class | n long | long mean R | long win rate | n short | short mean R | short win rate |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for cls in sorted(p["continuation_vs_reversal_by_class"].keys()):
        cr = p["continuation_vs_reversal_by_class"][cls]
        lines.append(
            f"| {cls} | {int(cr['n_long'])} | {cr['long_mean_r']:+.4f} | "
            f"{cr['long_win_rate']:.3f} | {int(cr['n_short'])} | "
            f"{cr['short_mean_r']:+.4f} | {cr['short_win_rate']:.3f} |"
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

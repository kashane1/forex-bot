"""Study 1 — event-window direction and per-class breakdown.

For each event class in the input event fixture, compute the post-cost
forward return over a fixed forward window, broken down by class, and
compare against a sample-matched random-entry null.

Designed to surface — when run against a real NFP/FOMC/CPI fixture —
the patterns the sprint brief's CAMPAIGN_014 narrative warned about:

  * one event class dominating the trade count;
  * an event class producing zero trades because a session / data
    filter blocked the trigger bar;
  * an aggregate direction that lives entirely on the dominant class.

This run uses the committed synthetic fixtures so the JSON / MD
artifacts are reproducible. The same script, pointed at a real event
fixture and a real H4 candle CSV, will run unchanged.
"""

from __future__ import annotations

from pathlib import Path

from research.edge_discovery.costs import apply_cost_overlay
from research.edge_discovery.loaders import load_candles_csv, load_event_fixture
from research.edge_discovery.null import random_null_baseline
from research.edge_discovery.report import summarize_study, write_study_report
from research.edge_discovery.windows import Side, compute_forward_returns

REPO_ROOT = Path(__file__).resolve().parents[3]
H4_FIXTURE = REPO_ROOT / "research" / "edge_discovery" / "sample_fixtures" / "synthetic_EUR_USD_H4.csv"
EVENTS_FIXTURE = REPO_ROOT / "research" / "edge_discovery" / "sample_fixtures" / "synthetic_events.csv"
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs"

WINDOW_BARS = 6  # H4 * 6 = 24 hours forward
SIDE = Side.LONG
SEEDS = range(20)


def _dominance_share(by_group: dict[str, dict[str, float]]) -> dict[str, float]:
    total = sum(int(v["n"]) for v in by_group.values()) or 1
    return {k: int(v["n"]) / total for k, v in by_group.items()}


def _zero_trade_classes(present_classes: list[str], by_group: dict[str, dict[str, float]]) -> list[str]:
    return sorted(set(present_classes) - set(by_group.keys()))


def run() -> Path:
    sample = load_candles_csv(H4_FIXTURE)
    events = load_event_fixture(EVENTS_FIXTURE)

    fr = compute_forward_returns(
        sample.frame,
        events.frame.index,
        window_bars=WINDOW_BARS,
        side=SIDE,
        labels=events.frame["event_class"].tolist(),
    )
    with_costs = apply_cost_overlay(fr.per_signal, sample.instrument)
    null = random_null_baseline(
        sample.frame,
        n_trades=max(len(with_costs), 1),
        window_bars=WINDOW_BARS,
        seeds=SEEDS,
        apply_cost_overlay_fn=apply_cost_overlay,
        instrument=sample.instrument,
    )

    summary = summarize_study(
        "event_window_direction",
        with_costs,
        instrument=sample.instrument,
        granularity=sample.granularity,
        window_bars=WINDOW_BARS,
        null=null,
        dropped_trailing=fr.dropped_trailing,
        dropped_missing=fr.dropped_missing,
        inputs={
            "candles_path": str(Path(sample.source_path).resolve().relative_to(REPO_ROOT)),
            "candles_sha256": sample.source_sha256,
            "events_path": str(Path(events.source_path).resolve().relative_to(REPO_ROOT)),
            "events_sha256": events.source_sha256,
            "side": SIDE.name,
            "seeds": list(SEEDS),
            "event_classes_in_fixture": list(events.classes),
        },
        notes=[
            "Synthetic fixture run — not strategy evidence; illustrative only.",
            "Real-fixture run: point candles_path at the SQLite-derived H4 CSV "
            "and events_path at the real NFP/FOMC fixture; no other change.",
            f"Per-class dominance share (n / total): {_dominance_share(_force_groups(with_costs, summary_n=fr.n_signals))}",
            f"Event classes in fixture with ZERO matched trades: {_zero_trade_classes(list(events.classes), _force_groups(with_costs, summary_n=fr.n_signals))}",
            "Reminder: post-cost mean must clearly beat the random-entry null "
            "(see EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md); aggregate sign "
            "alone does not graduate.",
        ],
    )

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUTS / "study_event_window.json"
    md_path = OUTPUTS / "study_event_window.md"
    write_study_report(summary, json_path=json_path, md_path=md_path)
    return md_path


def _force_groups(with_costs, summary_n: int) -> dict[str, dict[str, float]]:
    """Lightweight by-class breakdown for the note line — recomputed
    locally because the summary's by_group is keyed differently."""
    out: dict[str, dict[str, float]] = {}
    if summary_n == 0:
        return out
    for cls, sub in with_costs.groupby("label"):
        out[str(cls)] = {"n": float(len(sub))}
    return out


if __name__ == "__main__":
    p = run()
    print(f"wrote {p}")

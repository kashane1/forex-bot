"""Study 4 (optional) — session / time-of-day forward returns.

Bins every H4 close in the candle fixture by UTC hour-of-day and
computes the post-cost LONG forward-return mean over a fixed window
for each session, with a sample-matched random null.

The H4 fixture has six distinct close hours per trading day (02:00,
06:00, 10:00, 14:00, 18:00, 22:00 UTC), so the per-session sample
sizes are small and the study is deliberately descriptive — it answers
"could session-of-day be worth a closer look?" with the lab's null
band, not a significance test.

This is a *capability* study: the same script run against a longer
hydrated H4 store would carry the same shape and much larger per-
session n.
"""

from __future__ import annotations

from pathlib import Path

from research.edge_discovery.costs import apply_cost_overlay
from research.edge_discovery.loaders import load_candles_csv
from research.edge_discovery.null import random_null_baseline
from research.edge_discovery.report import summarize_study, write_study_report
from research.edge_discovery.windows import Side, compute_forward_returns

REPO_ROOT = Path(__file__).resolve().parents[3]
H4_FIXTURE = REPO_ROOT / "research" / "edge_discovery" / "sample_fixtures" / "synthetic_EUR_USD_H4.csv"
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs"

WINDOW_BARS = 4  # H4 * 4 = 16 hours forward
SIDE = Side.LONG
SEEDS = range(20)


def run() -> Path:
    sample = load_candles_csv(H4_FIXTURE)
    times = sample.frame.index
    # Use every bar as a "signal" — the side is fixed LONG; the lab is
    # asking "if you bought at the close of any H4 bar in this hour of
    # day, what was the next-window post-cost return on average?"
    labels = [f"UTC_{ts.hour:02d}" for ts in times]
    fr = compute_forward_returns(
        sample.frame,
        list(times),
        window_bars=WINDOW_BARS,
        side=SIDE,
        labels=labels,
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
        "session_time_of_day",
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
            "side": SIDE.name,
            "seeds": list(SEEDS),
        },
        notes=[
            "Synthetic fixture run — not strategy evidence; illustrative only.",
            "Per-session sample size is small in the committed fixture; rerun "
            "against a hydrated H4 store for meaningful per-hour n.",
            "Reading: a session is worth a closer look only if its post-cost "
            "mean materially exceeds the per-session null band — not if it is "
            "merely 'positive'.",
        ],
    )

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUTS / "study_session.json"
    md_path = OUTPUTS / "study_session.md"
    write_study_report(summary, json_path=json_path, md_path=md_path)
    return md_path


if __name__ == "__main__":
    p = run()
    print(f"wrote {p}")

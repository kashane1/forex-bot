"""Regenerate the committed synthetic fixtures.

Idempotent — same seed → identical CSV bytes. Run from the repo root:

    python research/edge_discovery/sample_fixtures/_generate_fixtures.py

The committed CSVs are the source of truth for tests; this script
exists so an updated fixture can be re-derived deterministically.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SEED = 42
N_BARS = 480  # ~80 trading days at H4
START = datetime(2024, 1, 2, 22, 0, tzinfo=UTC)
START_PRICE = 1.1000
TYPICAL_VOL = 0.0010  # H4 stddev of log-returns ~10 pips for EUR_USD-ish


def _h4_grid(start: datetime, n: int) -> list[datetime]:
    """Generate H4 close timestamps skipping weekend bars (Fri 22:00 →
    Mon 02:00). Matches the shape of OANDA's H4 trading day."""
    out: list[datetime] = []
    t = start
    step = timedelta(hours=4)
    while len(out) < n:
        # OANDA H4 close hours run 22:00..18:00 UTC across the trading
        # day; Friday's 22:00 bar is the last of the week, weekend bars
        # are skipped. The synthetic grid uses the same skip pattern.
        if t.weekday() == 5:  # Saturday
            t = t + timedelta(days=2)
            continue
        if t.weekday() == 6:  # Sunday
            t = t + timedelta(days=1)
            continue
        out.append(t)
        t = t + step
    return out


def _generate_candles() -> str:
    rng = np.random.default_rng(SEED)
    log_returns = rng.normal(loc=0.0, scale=TYPICAL_VOL, size=N_BARS)
    closes = START_PRICE * np.exp(np.cumsum(log_returns))
    opens = np.concatenate(([START_PRICE], closes[:-1]))
    # Half-bar range as a noisy fraction of close.
    range_frac = np.abs(rng.normal(loc=TYPICAL_VOL * 1.2, scale=TYPICAL_VOL * 0.3, size=N_BARS))
    highs = np.maximum(opens, closes) + closes * range_frac
    lows = np.minimum(opens, closes) - closes * range_frac
    # Constant 1.5-pip spread.
    half_spread = 0.00015 / 2
    bid_o = opens - half_spread
    bid_h = highs - half_spread
    bid_l = lows - half_spread
    bid_c = closes - half_spread
    ask_o = opens + half_spread
    ask_h = highs + half_spread
    ask_l = lows + half_spread
    ask_c = closes + half_spread
    times = _h4_grid(START, N_BARS)

    rows = ["time,granularity,bid_o,bid_h,bid_l,bid_c,ask_o,ask_h,ask_l,ask_c,volume,complete"]
    for t, bo, bh, bl, bc, ao, ah, al, ac in zip(
        times, bid_o, bid_h, bid_l, bid_c, ask_o, ask_h, ask_l, ask_c, strict=True
    ):
        ts = t.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        rows.append(
            f"{ts},H4,{bo:.5f},{bh:.5f},{bl:.5f},{bc:.5f},"
            f"{ao:.5f},{ah:.5f},{al:.5f},{ac:.5f},10000,True"
        )
    return "\n".join(rows) + "\n"


def _generate_events() -> str:
    """Six synthetic events across NFP / FOMC / CPI classes.

    Timestamps are picked to land on times that exist in the candle
    grid, so the event-window study has at least one matched signal per
    class. Real NFP/FOMC release times would replace this in a study
    run against actual event fixtures.
    """
    times = _h4_grid(START, N_BARS)
    chosen = [
        (times[40], "NFP"),
        (times[80], "FOMC"),
        (times[120], "CPI"),
        (times[160], "NFP"),
        (times[200], "FOMC"),
        (times[240], "CPI"),
    ]
    rows = ["time,event_class"]
    for t, cls in chosen:
        rows.append(f"{t.strftime('%Y-%m-%dT%H:%M:%S+00:00')},{cls}")
    return "\n".join(rows) + "\n"


def main() -> None:
    (HERE / "synthetic_EUR_USD_H4.csv").write_text(_generate_candles(), encoding="utf-8")
    (HERE / "synthetic_events.csv").write_text(_generate_events(), encoding="utf-8")
    print(f"wrote synthetic_EUR_USD_H4.csv ({N_BARS} rows) and synthetic_events.csv (6 rows)")


if __name__ == "__main__":
    main()

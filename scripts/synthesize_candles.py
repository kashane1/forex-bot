#!/usr/bin/env python3
"""Synthetic candle generator for CAMPAIGN_001 fallback.

THIS IS NOT REAL OANDA DATA. The generator produces plausible bid/ask
H4/H1 candles for 7 major FX pairs across a configurable window. The
SQLite `candles.source` column is set to "synthetic-v1" so any
downstream consumer can distinguish.

Usage:
    python scripts/synthesize_candles.py \\
        --db data/campaign.sqlite3 \\
        --pairs EUR_USD,GBP_USD,USD_JPY,AUD_USD,USD_CAD,USD_CHF,NZD_USD \\
        --granularities H4,H1 \\
        --from 2020-01-01 --to 2026-05-20

It also seeds the `instruments` table with the synthetic instruments so
the backtest CLI can find pip metadata.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Allow running directly without `pip install -e .`.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, InstrumentRepo
from forex_bot.domain.candles import Candle
from forex_bot.domain.instruments import Instrument

GRANULARITY_HOURS: dict[str, float] = {"H4": 4.0, "H1": 1.0}


@dataclass(frozen=True)
class PairProfile:
    """Calibration parameters for a plausible-but-fictional FX pair series."""

    name: str
    pip_location: int
    display_precision: int
    start_price: float
    annual_vol: float           # log-vol per year
    annual_drift: float         # log-drift per year
    typical_spread_pips: float
    spread_jitter_pips: float
    regime_switch_per_year: float = 4.0


PROFILES: list[PairProfile] = [
    PairProfile("EUR_USD", -4, 5, 1.10, 0.08, 0.005, 0.8, 0.6),
    PairProfile("GBP_USD", -4, 5, 1.30, 0.09, 0.002, 1.2, 0.9),
    PairProfile("USD_JPY", -2, 3, 140.00, 0.09, 0.010, 1.4, 1.0),
    PairProfile("AUD_USD", -4, 5, 0.70, 0.10, -0.001, 1.0, 0.8),
    PairProfile("USD_CAD", -4, 5, 1.35, 0.07, 0.001, 1.2, 0.8),
    PairProfile("USD_CHF", -4, 5, 0.92, 0.08, -0.002, 1.0, 0.7),
    PairProfile("NZD_USD", -4, 5, 0.65, 0.11, -0.002, 1.4, 1.0),
]


def _bar_times(start: datetime, end: datetime, hours: float) -> list[datetime]:
    """Return bar timestamps inside [start, end), skipping Sat 17:00 ET → Sun 17:00 ET.

    OANDA aligns the trading week to NY 17:00. To stay simple and avoid a TZ
    dance, we use UTC bar boundaries and remove bars whose start falls between
    Friday 22:00 UTC and Sunday 22:00 UTC (approx, after DST handwaving).
    """
    step = timedelta(hours=hours)
    cursor = start
    bars: list[datetime] = []
    while cursor < end:
        weekday = cursor.weekday()  # Mon=0 ... Sun=6
        utc_hour = cursor.hour
        in_weekend = (
            (weekday == 4 and utc_hour >= 22)
            or weekday == 5
            or (weekday == 6 and utc_hour < 22)
        )
        if not in_weekend:
            bars.append(cursor)
        cursor += step
    return bars


def _simulate_pair(
    profile: PairProfile, times: list[datetime], rng: np.random.Generator
) -> list[Candle]:
    if not times:
        return []
    n = len(times)
    hours_per_year = 252 * 24
    bar_hours = (times[1] - times[0]).total_seconds() / 3600 if n > 1 else 4.0
    bars_per_year = hours_per_year / bar_hours

    # Regime: cycle through bullish, bearish, and choppy at random intervals.
    bar_drift = np.zeros(n)
    bar_vol = np.zeros(n)
    cur_idx = 0
    while cur_idx < n:
        regime = rng.choice(["up", "down", "chop"], p=[0.35, 0.35, 0.30])
        # Each regime lasts a few months on average.
        run_bars = max(int(bars_per_year / profile.regime_switch_per_year), 10)
        run_bars = max(20, int(rng.normal(run_bars, run_bars * 0.3)))
        end_idx = min(cur_idx + run_bars, n)
        if regime == "up":
            mu = profile.annual_drift / bars_per_year + 0.0005 / bars_per_year
            sigma = profile.annual_vol / math.sqrt(bars_per_year) * 0.9
        elif regime == "down":
            mu = -profile.annual_drift / bars_per_year - 0.0005 / bars_per_year
            sigma = profile.annual_vol / math.sqrt(bars_per_year) * 0.9
        else:
            mu = 0.0
            sigma = profile.annual_vol / math.sqrt(bars_per_year) * 0.6
        bar_drift[cur_idx:end_idx] = mu
        bar_vol[cur_idx:end_idx] = sigma
        cur_idx = end_idx

    log_returns = rng.normal(bar_drift, bar_vol)
    log_price = np.log(profile.start_price) + np.cumsum(log_returns)
    mid = np.exp(log_price)

    # Intra-bar excursion: high/low around the mid open→close midpoint.
    half_range = np.abs(rng.normal(0, bar_vol * 0.5)) * mid
    half_range = np.clip(half_range, mid * 0.0001, mid * 0.01)

    # Bid/ask spread in price units.
    pip_size = 10 ** profile.pip_location
    spread_pips = np.abs(
        rng.normal(profile.typical_spread_pips, profile.spread_jitter_pips, size=n)
    ) + profile.typical_spread_pips * 0.3
    # Occasional spread spikes (~0.3% of bars) to give the audit something to flag.
    spike_mask = rng.random(n) < 0.003
    spread_pips[spike_mask] *= rng.uniform(5.0, 12.0, size=spike_mask.sum())
    half_spread = (spread_pips * pip_size) / 2.0

    # Construct OHLC for the mid series. Open of bar i = close of bar i-1.
    opens = np.empty(n)
    opens[0] = profile.start_price
    opens[1:] = mid[:-1]
    closes = mid
    highs = np.maximum(opens, closes) + half_range
    lows = np.minimum(opens, closes) - half_range

    candles: list[Candle] = []
    for i in range(n):
        o, h, low, c = float(opens[i]), float(highs[i]), float(lows[i]), float(closes[i])
        hs = float(half_spread[i])

        def _dec(v: float) -> Decimal:
            return Decimal(str(round(v, profile.display_precision)))

        candles.append(
            Candle(
                instrument=profile.name,
                granularity="H4" if abs(bar_hours - 4.0) < 0.01 else "H1",  # type: ignore[arg-type]
                time=times[i],
                complete=True,
                volume=int(rng.uniform(500, 2500)),
                bid_o=_dec(o - hs),
                bid_h=_dec(h - hs),
                bid_l=_dec(low - hs),
                bid_c=_dec(c - hs),
                ask_o=_dec(o + hs),
                ask_h=_dec(h + hs),
                ask_l=_dec(low + hs),
                ask_c=_dec(c + hs),
            )
        )
    return candles


def _make_instrument(profile: PairProfile) -> Instrument:
    return Instrument(
        name=profile.name,
        type="CURRENCY",
        display_precision=profile.display_precision,
        pip_location=profile.pip_location,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        maximum_order_units=Decimal("100000000"),
        margin_rate=Decimal("0.02"),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--pairs", required=True, help="comma-separated")
    parser.add_argument("--granularities", default="H4,H1")
    parser.add_argument("--from", dest="from_date", required=True)
    parser.add_argument("--to", dest="to_date", required=True)
    parser.add_argument("--seed", type=int, default=20260521)
    args = parser.parse_args()

    pair_names = [p.strip().upper() for p in args.pairs.split(",")]
    profiles = [p for p in PROFILES if p.name in pair_names]
    missing = set(pair_names) - {p.name for p in profiles}
    if missing:
        print(f"unknown pairs: {sorted(missing)}", file=sys.stderr)
        return 2

    grans = [g.strip().upper() for g in args.granularities.split(",")]
    for g in grans:
        if g not in GRANULARITY_HOURS:
            print(f"unsupported granularity: {g}", file=sys.stderr)
            return 2

    start = datetime.fromisoformat(args.from_date).replace(tzinfo=UTC)
    end = datetime.fromisoformat(args.to_date).replace(tzinfo=UTC)

    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    db = Database(args.db)
    instr_repo = InstrumentRepo(db)
    candle_repo = CandleRepo(db)

    print(
        "==================================================================\n"
        " SYNTHETIC DATA GENERATION (NOT OANDA)                            \n"
        " This populates the SQLite ledger with fabricated bid/ask candles \n"
        " calibrated to plausible-but-fictional FX dynamics. Source column \n"
        " on every candle is 'synthetic-v1'.                               \n"
        "==================================================================\n"
    )

    for profile in profiles:
        instrument = _make_instrument(profile)
        instr_repo.upsert(instrument, raw={"name": profile.name, "synthetic": True})
        for gran in grans:
            hours = GRANULARITY_HOURS[gran]
            times = _bar_times(start, end, hours)
            # Independent seed per (pair, gran) so series are reproducible and
            # H1 and H4 series for the same pair are NOT exact resamplings.
            seed = args.seed ^ hash(profile.name) ^ hash(gran)
            rng = np.random.default_rng(seed & 0xFFFFFFFF)
            candles = _simulate_pair(profile, times, rng)
            # Override the granularity field correctly (the generator infers
            # from bar_hours, but make it explicit per call).
            candles = [c.model_copy(update={"granularity": gran}) for c in candles]
            written = candle_repo.upsert_many(
                candles,
                source="synthetic-v1",
                price_components="BA",
                request_hash=f"synthetic|{profile.name}|{gran}|{args.from_date}|{args.to_date}|{args.seed}",
            )
            print(f"  {profile.name} {gran}: {written} bars ({times[0]} → {times[-1]})")

    print("\nDone. Remember: SYNTHETIC, not OANDA.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

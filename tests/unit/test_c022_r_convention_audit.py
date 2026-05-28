"""Characterization tests for the C022 r_multiple convention quirk.

These LOCK an empirically proven inconsistency in the committed CAMPAIGN_022
trade artifacts (read-only): at a hard stop the price-based R is exactly −1 for
every pair (exit == stop), but the recorded `r_multiple` is correct (−1) only for
USD-*quote* pairs. For USD-*base* pairs (USD_JPY/USD_CAD/USD_CHF) the recorded R
is scaled by 1/rate (recorded_r * rate == −1).

The tests do NOT assert this is desirable — they document current reality so a
future repair sprint has a regression anchor. They never modify the artifacts.
See docs/research/C022_R_MULTIPLE_CONVENTION_AUDIT.md.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
C022_BASE = REPO_ROOT / "backtests" / "CAMPAIGN_022_h4_h1_pullback_resolution" / "train" / "base"

USD_QUOTE = ("EUR_USD", "GBP_USD", "AUD_USD", "NZD_USD")
USD_BASE = ("USD_JPY", "USD_CAD", "USD_CHF")


def _price_based_r(side: str, entry: float, exit_: float, stop: float) -> float | None:
    risk = abs(entry - stop)
    if risk == 0:
        return None
    return (exit_ - entry) / risk if side == "long" else (entry - exit_) / risk


def _stop_rows(pair: str):
    f = C022_BASE / f"c022_{pair}_train_base_trades.csv"
    if not f.exists():
        return None
    rows = []
    with f.open(newline="") as fh:
        for row in csv.DictReader(fh):
            if row["exit_reason"] != "stop":
                continue
            rows.append(row)
    return rows


@pytest.mark.parametrize("pair", USD_QUOTE)
def test_usd_quote_pairs_record_minus_one_r_at_stop(pair: str):
    rows = _stop_rows(pair)
    if not rows:
        pytest.skip(f"{pair} committed trades absent")
    for row in rows:
        r = float(row["r_multiple"])
        pr = _price_based_r(row["side"], float(row["entry_price"]),
                            float(row["exit_price"]), float(row["stop_price"]))
        assert pr == pytest.approx(-1.0, abs=1e-6)
        # USD-quote: recorded R matches the price-based R (correct convention).
        assert r == pytest.approx(-1.0, abs=1e-6)


@pytest.mark.parametrize("pair", USD_BASE)
def test_usd_base_pairs_record_r_scaled_by_inverse_rate(pair: str):
    rows = _stop_rows(pair)
    if not rows:
        pytest.skip(f"{pair} committed trades absent")
    for row in rows:
        r = float(row["r_multiple"])
        exit_ = float(row["exit_price"])  # == stop_price at a stop; quote per 1 USD
        pr = _price_based_r(row["side"], float(row["entry_price"]), exit_,
                            float(row["stop_price"]))
        assert pr == pytest.approx(-1.0, abs=1e-6)
        # Proven quirk: recorded_r is the price-based R divided by the rate.
        assert r * exit_ == pytest.approx(-1.0, abs=1e-3)
        # And (except CHF whose rate~0.93) recorded R understates the true -1R loss.
        if pair in ("USD_JPY", "USD_CAD"):
            assert r > -0.9  # i.e. NOT counted as a near-full-loss, despite being one


def test_price_based_r_helper_is_pair_agnostic():
    # The corrected convention yields -1 at stop for any quote scale.
    assert _price_based_r("short", 110.01, 110.14, 110.14) == pytest.approx(-1.0)
    assert _price_based_r("long", 1.2704, 1.26845, 1.26845) == pytest.approx(-1.0)
    assert _price_based_r("short", 1.19067, 1.19198, 1.19198) == pytest.approx(-1.0)

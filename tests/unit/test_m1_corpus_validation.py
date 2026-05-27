from __future__ import annotations

from forex_bot.data.m1_corpus_validation import (
    classify_count_delta,
    classify_quality,
    extreme_spread_threshold,
)


def test_classify_count_delta_exact_pass() -> None:
    assert classify_count_delta(1000, 1000) == "PASS"


def test_classify_count_delta_small_warn() -> None:
    assert classify_count_delta(1004, 1000) == "WARN"


def test_extreme_spread_threshold_jpy() -> None:
    assert extreme_spread_threshold("USD_JPY") > extreme_spread_threshold("EUR_USD")


def test_classify_quality_duplicate_fail() -> None:
    assert (
        classify_quality(
            {
                "duplicate_timestamps": 1,
                "bid_ask_violations": 0,
                "ohlc_violations": 0,
                "negative_or_zero_spreads": 0,
                "missing_minutes": 0,
                "expected_weekday_minutes": 1000,
                "extreme_spreads": 0,
            }
        )
        == "FAIL"
    )

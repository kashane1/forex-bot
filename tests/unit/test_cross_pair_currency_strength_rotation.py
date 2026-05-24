"""Unit tests for ``CrossPairCurrencyStrengthRotationStrategy`` (CAMPAIGN_013).

These tests are research-only and prove the cross-pair currency-strength
rotation candidate is **deterministic, no-lookahead, and structurally
safe**. A passing suite is NOT strategy approval; the candidate is a
research scaffold and cannot be added to
``configs/approved_strategies.yaml`` without the full six-evidence
ladder + a deliberate human approval action per
``STRATEGY_APPROVAL_PROCESS.md``. ``configs/approved_strategies.yaml``
remains ``approved: []``; the strategy is not enabled in any active
loop.

See:
- docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md
- docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md
- docs/research/NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml
from pydantic import ValidationError

from forex_bot.config import (
    CrossPairCurrencyStrengthRotationStrategyConfig,
    StrategyConfig,
)
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.cross_pair_currency_strength_rotation import (
    EXPECTED_PAIRS,
    NON_USD_CURRENCIES,
    CrossPairCurrencyStrengthRotationStrategy,
    _compute_ranks,
    _compute_strength,
    _log_return_n,
    _parse_pair,
)

# ---------------------------------------------------------------------------
# Constants + helpers
# ---------------------------------------------------------------------------

# Use NY-standard H4 alignment: UTC bar opens at 22, 02, 06, 10, 14, 18
# (matches CAMPAIGN_010 / 011 / 012 alignment).
_H4_HOURS_UTC: tuple[int, ...] = (22, 2, 6, 10, 14, 18)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STRATEGY_SOURCE = (
    _REPO_ROOT
    / "src"
    / "forex_bot"
    / "strategies"
    / "cross_pair_currency_strength_rotation.py"
).read_text(encoding="utf-8")


def _bar_time(base: datetime, idx: int) -> datetime:
    return base + timedelta(hours=4 * idx)


def _make_candle(
    time: datetime,
    *,
    open_: float,
    high: float,
    low: float,
    close: float,
    complete: bool = True,
    instrument: str = "EUR_USD",
) -> Candle:
    spread = Decimal("0.00010")
    # Round to 5 decimals to match OANDA H4 quote precision.
    mid_o = Decimal(str(round(open_, 5)))
    mid_h = Decimal(str(round(high, 5)))
    mid_l = Decimal(str(round(low, 5)))
    mid_c = Decimal(str(round(close, 5)))
    return Candle(
        instrument=instrument,
        granularity="H4",
        time=time,
        complete=complete,
        volume=1000,
        bid_o=mid_o - spread / 2,
        bid_h=mid_h - spread / 2,
        bid_l=mid_l - spread / 2,
        bid_c=mid_c - spread / 2,
        ask_o=mid_o + spread / 2,
        ask_h=mid_h + spread / 2,
        ask_l=mid_l + spread / 2,
        ask_c=mid_c + spread / 2,
    )


def _build_h4_frame(
    n: int,
    *,
    base_close: float = 1.0800,
    range_size: float = 0.0010,
    start: datetime | None = None,
    instrument: str = "EUR_USD",
) -> CandleFrame:
    """Build a simple H4 frame of n identical-spec bars. ATR converges to range_size."""
    base = start or datetime(2024, 11, 4, _H4_HOURS_UTC[0], tzinfo=UTC)
    candles: list[Candle] = []
    for i in range(n):
        t = _bar_time(base, i)
        candles.append(
            _make_candle(
                t,
                open_=base_close,
                high=base_close + range_size / 2,
                low=base_close - range_size / 2,
                close=base_close,
                instrument=instrument,
            )
        )
    return CandleFrame.from_candles(instrument, "H4", candles)


def _make_cross_pair_closes(
    strengths_pair_to_return: dict[str, float],
    *,
    lookback_bars: int = 24,
    base_levels: dict[str, float] | None = None,
) -> dict[str, pd.Series]:
    """Build the cross_pair_closes dict by constructing per-pair close
    series whose first-vs-last log return equals the requested return.

    For each pair, builds a series of length ``lookback_bars + 1`` where
    `close[0] = base_level` and `close[-1] = base_level * exp(return)`.
    Intermediate values are linearly interpolated (irrelevant to the
    log-return calculation, which uses only the endpoints).
    """
    defaults = {
        "EUR_USD": 1.0800,
        "GBP_USD": 1.2500,
        "USD_JPY": 150.00,
        "AUD_USD": 0.6500,
        "USD_CAD": 1.3500,
        "USD_CHF": 0.8800,
        "NZD_USD": 0.6000,
    }
    levels = base_levels or defaults
    out: dict[str, pd.Series] = {}
    n = lookback_bars
    times = pd.date_range("2024-11-04T22:00:00Z", periods=n + 1, freq="4h")
    for pair, r in strengths_pair_to_return.items():
        start_level = levels[pair]
        end_level = start_level * float(np.exp(r))
        values = np.linspace(start_level, end_level, n + 1)
        out[pair] = pd.Series(values, index=times)
    return out


def _ctx(
    frame: CandleFrame,
    instrument: Instrument,
    *,
    config: dict,
    open_position_units: Decimal = Decimal("0"),
) -> StrategyContext:
    last_close = float(frame.df["close"].iloc[-1]) if len(frame) else 1.0800
    quote_time = (
        frame.df.index[-1].to_pydatetime()
        if len(frame)
        else datetime(2024, 11, 4, tzinfo=UTC)
    )
    quote = Quote(
        instrument=instrument.name,
        time=quote_time,
        bid=Decimal(str(last_close - 0.0001)),
        ask=Decimal(str(last_close + 0.0001)),
    )
    position = Position(
        instrument=instrument.name,
        long_units=open_position_units,
    )
    return StrategyContext(
        instrument=instrument,
        candles=frame,
        market_state=MarketState(
            quote=quote,
            spread_snapshot=SpreadSnapshot(
                instrument=instrument.name,
                time=quote.time,
                bid=quote.bid,
                ask=quote.ask,
                spread_pips=Decimal("2.0"),
            ),
        ),
        open_positions=[position],
        config=config,
    )


def _default_cfg(**overrides) -> dict:
    cfg = {
        "version": "0.1.0-c013",
        "timeframe": "H4",
        "currency_strength_lookback_bars": 24,
        "rank_gap_threshold": 4,
        "atr_lookback": 14,
        "atr_stop_multiple": 2.0,
        "trailing_stop_atr_multiple": None,
        "max_bars_in_trade": 6,
        "min_atr_pips": {},
    }
    cfg.update(overrides)
    return cfg


# ===========================================================================
# 1. Config defaults / validation (11 cases)
# ===========================================================================


def test_default_config_matches_frozen_spec():
    c = CrossPairCurrencyStrengthRotationStrategyConfig(version="0.1.0-c013")
    assert c.version == "0.1.0-c013"
    assert c.timeframe == "H4"
    assert c.currency_strength_lookback_bars == 24
    assert c.rank_gap_threshold == 4
    assert c.atr_lookback == 14
    assert c.atr_stop_multiple == 2.0
    assert c.trailing_stop_atr_multiple is None
    assert c.max_bars_in_trade == 6
    assert c.min_atr_pips == {}


def test_config_rejects_non_positive_currency_strength_lookback_bars():
    for bad in (-1, 0, 1):
        with pytest.raises(
            ValidationError, match="currency_strength_lookback_bars must be"
        ):
            CrossPairCurrencyStrengthRotationStrategyConfig(
                version="0.1.0-c013", currency_strength_lookback_bars=bad
            )


def test_config_rejects_rank_gap_threshold_below_1():
    for bad in (-1, 0):
        with pytest.raises(ValidationError, match="rank_gap_threshold must be"):
            CrossPairCurrencyStrengthRotationStrategyConfig(
                version="0.1.0-c013", rank_gap_threshold=bad
            )


def test_config_rejects_rank_gap_threshold_above_7():
    for bad in (8, 9, 100):
        with pytest.raises(ValidationError, match="rank_gap_threshold must be"):
            CrossPairCurrencyStrengthRotationStrategyConfig(
                version="0.1.0-c013", rank_gap_threshold=bad
            )


def test_config_rejects_non_positive_atr_lookback():
    for bad in (-1, 0, 1):
        with pytest.raises(ValidationError, match="atr_lookback must be"):
            CrossPairCurrencyStrengthRotationStrategyConfig(
                version="0.1.0-c013", atr_lookback=bad
            )


def test_config_rejects_non_positive_atr_stop_multiple():
    for bad in (-1.0, 0.0):
        with pytest.raises(ValidationError, match="atr_stop_multiple must be"):
            CrossPairCurrencyStrengthRotationStrategyConfig(
                version="0.1.0-c013", atr_stop_multiple=bad
            )


def test_config_rejects_non_positive_max_bars_in_trade():
    for bad in (-1, 0):
        with pytest.raises(ValidationError, match="max_bars_in_trade must be"):
            CrossPairCurrencyStrengthRotationStrategyConfig(
                version="0.1.0-c013", max_bars_in_trade=bad
            )


def test_config_rejects_non_null_trailing_stop_in_v1():
    """The cross-pair rotator uses time-stop only in v1."""
    with pytest.raises(
        ValidationError, match="trailing_stop_atr_multiple must be None"
    ):
        CrossPairCurrencyStrengthRotationStrategyConfig(
            version="0.1.0-c013", trailing_stop_atr_multiple=1.5
        )


def test_config_rejects_extra_fields():
    """extra='forbid' is the standing convention for every StrategyConfig."""
    with pytest.raises(ValidationError):
        CrossPairCurrencyStrengthRotationStrategyConfig(
            version="0.1.0-c013", undocumented_extra_field="surprise"
        )


def test_strategy_config_enabled_check_rejects_missing_nested():
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "strategy.cross_pair_currency_strength_rotation config required when enabled"
        ),
    ):
        StrategyConfig(enabled=["cross_pair_currency_strength_rotation"])


def test_rank_gap_threshold_extremes_within_range_accepted():
    """1 and 7 are both inclusive valid values."""
    c1 = CrossPairCurrencyStrengthRotationStrategyConfig(
        version="0.1.0-c013", rank_gap_threshold=1
    )
    c7 = CrossPairCurrencyStrengthRotationStrategyConfig(
        version="0.1.0-c013", rank_gap_threshold=7
    )
    assert c1.rank_gap_threshold == 1
    assert c7.rank_gap_threshold == 7


# ===========================================================================
# 2. Pair parser / universe validation (2 cases)
# ===========================================================================


def test_parse_pair_parses_base_quote():
    assert _parse_pair("EUR_USD") == ("EUR", "USD")
    assert _parse_pair("USD_JPY") == ("USD", "JPY")
    assert _parse_pair("AUD_USD") == ("AUD", "USD")


def test_parse_pair_rejects_malformed():
    bad_names = ["EURUSD", "EUR_USD_JPY", "", "_USD", "EUR_", "eur_usd", "EUR/USD"]
    for bad in bad_names:
        with pytest.raises(ValueError):
            _parse_pair(bad)


# ===========================================================================
# 3. Currency-strength mapping (5 cases)
# ===========================================================================


def test_strength_usd_base_pair_positive_sign_for_non_usd_currency():
    """USD-base pairs: rising pair = non-USD currency strengthens."""
    # EUR_USD rising → EUR strength positive.
    returns = {p: 0.0 for p in EXPECTED_PAIRS}
    returns["EUR_USD"] = +0.01  # 1% log return
    strength = _compute_strength(returns)
    assert strength["EUR"] == pytest.approx(+0.01)


def test_strength_usd_quote_pair_inverted_sign_for_non_usd_currency():
    """USD-quote pairs: rising pair = non-USD currency weakens (invert sign)."""
    # USD_JPY rising → JPY strength negative.
    returns = {p: 0.0 for p in EXPECTED_PAIRS}
    returns["USD_JPY"] = +0.01
    strength = _compute_strength(returns)
    assert strength["JPY"] == pytest.approx(-0.01)


def test_strength_usd_is_negative_mean_of_non_usd():
    """USD strength = −mean(non-USD strengths)."""
    # Set EUR, GBP, AUD, NZD strengths to +0.01 each (via USD-base
    # pairs rising); set JPY, CAD, CHF strengths to -0.01 each (via
    # USD-quote pairs rising). Then mean(non-USD) = (0.04 - 0.03) / 7
    # ≈ 0.00143; USD strength ≈ -0.00143.
    returns = {p: 0.0 for p in EXPECTED_PAIRS}
    returns["EUR_USD"] = +0.01
    returns["GBP_USD"] = +0.01
    returns["AUD_USD"] = +0.01
    returns["NZD_USD"] = +0.01
    returns["USD_JPY"] = +0.01  # JPY strength -0.01
    returns["USD_CAD"] = +0.01  # CAD strength -0.01
    returns["USD_CHF"] = +0.01  # CHF strength -0.01
    strength = _compute_strength(returns)
    non_usd_total = sum(
        strength[c] for c in ("EUR", "GBP", "AUD", "NZD", "JPY", "CAD", "CHF")
    )
    assert strength["USD"] == pytest.approx(-non_usd_total / 7)


def test_strength_deterministic_for_same_input():
    """Same returns → same strength scores."""
    returns = {p: float(i * 0.001) for i, p in enumerate(EXPECTED_PAIRS)}
    s1 = _compute_strength(returns)
    s2 = _compute_strength(returns)
    assert s1 == s2


def test_strength_includes_all_8_currencies():
    """All 8 currencies (USD + 7 non-USD) must be present."""
    returns = {p: 0.0 for p in EXPECTED_PAIRS}
    strength = _compute_strength(returns)
    expected = {"USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"}
    assert set(strength.keys()) == expected


# ===========================================================================
# 4. Rank computation (4 cases)
# ===========================================================================


def test_ranks_are_deterministic():
    """Same strength → same ranks."""
    strength = {
        "USD": 0.0, "EUR": 0.05, "GBP": 0.03, "JPY": -0.02,
        "AUD": 0.01, "CAD": -0.01, "CHF": 0.02, "NZD": -0.03,
    }
    r1 = _compute_ranks(strength)
    r2 = _compute_ranks(strength)
    assert r1 == r2


def test_ranks_strongest_is_rank_1_weakest_is_rank_8():
    strength = {
        "USD": 0.0, "EUR": 0.05, "GBP": 0.03, "JPY": -0.02,
        "AUD": 0.01, "CAD": -0.01, "CHF": 0.02, "NZD": -0.03,
    }
    ranks = _compute_ranks(strength)
    # EUR has the highest strength → rank 1; NZD has the lowest → rank 8.
    assert ranks["EUR"] == 1
    assert ranks["NZD"] == 8
    assert set(ranks.values()) == {1, 2, 3, 4, 5, 6, 7, 8}


def test_ranks_tiebreak_is_alphabetic():
    """Ties broken by ascending currency code for determinism."""
    # AUD and EUR tied at 0.05; alphabetic order → AUD ranks first.
    strength = {
        "USD": 0.0, "EUR": 0.05, "GBP": 0.0, "JPY": 0.0,
        "AUD": 0.05, "CAD": 0.0, "CHF": 0.0, "NZD": 0.0,
    }
    ranks = _compute_ranks(strength)
    assert ranks["AUD"] == 1
    assert ranks["EUR"] == 2


def test_ranks_independent_of_input_dict_iteration_order():
    """Same strength values inserted in different orders → same ranks."""
    pairs = [
        ("USD", 0.0), ("EUR", 0.05), ("GBP", 0.03), ("JPY", -0.02),
        ("AUD", 0.01), ("CAD", -0.01), ("CHF", 0.02), ("NZD", -0.03),
    ]
    s_forward = dict(pairs)
    s_reverse = dict(reversed(pairs))
    assert _compute_ranks(s_forward) == _compute_ranks(s_reverse)


# ===========================================================================
# 5. Rank-gap rule (3 cases)
# ===========================================================================


def test_rank_gap_below_threshold_no_signal(eur_usd: Instrument):
    """|rank_gap| < threshold → None."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    # All currencies near zero → tight ranks → small gaps.
    returns = {p: 0.0001 * (i - 3) for i, p in enumerate(EXPECTED_PAIRS)}
    closes = _make_cross_pair_closes(returns)
    cfg = _default_cfg(rank_gap_threshold=7)  # extreme threshold → never fires
    cfg["cross_pair_closes"] = closes
    frame = _build_h4_frame(60)
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_rank_gap_equals_threshold_signal_fires(eur_usd: Instrument):
    """|rank_gap| == threshold → signal (inclusive)."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    # Build returns such that EUR is rank 1 (strongest) and USD is rank
    # ≥ 5 (so rank_gap = rank(USD) - rank(EUR) ≥ 4).
    # Set EUR very strong (+0.05 EUR_USD return), other USD-base pairs
    # mildly positive, and USD-quote pairs (USD_JPY/CAD/CHF) very negative
    # to push their non-USD currencies' strengths up — pushing USD to
    # weakest.
    returns = {
        "EUR_USD": +0.05,   # EUR very strong
        "GBP_USD": +0.02,
        "AUD_USD": +0.02,
        "NZD_USD": +0.02,
        "USD_JPY": -0.02,   # JPY very strong (invert)
        "USD_CAD": -0.02,   # CAD strong
        "USD_CHF": -0.02,   # CHF strong
    }
    closes = _make_cross_pair_closes(returns)
    cfg = _default_cfg(rank_gap_threshold=4)
    cfg["cross_pair_closes"] = closes
    frame = _build_h4_frame(60)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    # With EUR very strong and USD pushed weakest, gap should be ≥ 4
    # (top-half vs bottom-half) → fires.
    assert sig is not None
    assert sig.side == "long"  # EUR_USD long because base (EUR) is stronger


def test_rank_gap_above_threshold_signal_fires(eur_usd: Instrument):
    """|rank_gap| > threshold → signal."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    returns = {
        "EUR_USD": +0.10,
        "GBP_USD": +0.05,
        "AUD_USD": +0.05,
        "NZD_USD": +0.05,
        "USD_JPY": -0.05,
        "USD_CAD": -0.05,
        "USD_CHF": -0.05,
    }
    closes = _make_cross_pair_closes(returns)
    cfg = _default_cfg(rank_gap_threshold=3)  # easier to clear
    cfg["cross_pair_closes"] = closes
    frame = _build_h4_frame(60)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert sig is not None
    assert sig.side == "long"
    assert abs(sig.features["rank_gap"]) >= 3


# ===========================================================================
# 6. Side selection (2 cases)
# ===========================================================================


def test_side_long_when_base_stronger_than_quote(eur_usd: Instrument):
    """For EUR_USD: base (EUR) much stronger than quote (USD) → long."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    # EUR very strong; USD very weak.
    returns = {
        "EUR_USD": +0.10,
        "GBP_USD": +0.05,
        "AUD_USD": +0.05,
        "NZD_USD": +0.05,
        "USD_JPY": -0.05,
        "USD_CAD": -0.05,
        "USD_CHF": -0.05,
    }
    closes = _make_cross_pair_closes(returns)
    cfg = _default_cfg()
    cfg["cross_pair_closes"] = closes
    frame = _build_h4_frame(60)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert sig is not None
    assert sig.side == "long"
    assert sig.features["base_currency"] == "EUR"
    assert sig.features["quote_currency"] == "USD"
    assert sig.features["rank_gap"] > 0


def test_side_short_when_base_weaker_than_quote(eur_usd: Instrument):
    """For EUR_USD: base (EUR) much weaker than quote (USD) → short."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    # EUR very weak; USD very strong (all USD-base pairs falling, all
    # USD-quote pairs rising).
    returns = {
        "EUR_USD": -0.10,   # EUR weak
        "GBP_USD": -0.05,
        "AUD_USD": -0.05,
        "NZD_USD": -0.05,
        "USD_JPY": +0.05,   # JPY weak (USD strong)
        "USD_CAD": +0.05,
        "USD_CHF": +0.05,
    }
    closes = _make_cross_pair_closes(returns)
    cfg = _default_cfg()
    cfg["cross_pair_closes"] = closes
    frame = _build_h4_frame(60)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert sig is not None
    assert sig.side == "short"
    assert sig.features["rank_gap"] < 0


# ===========================================================================
# 7. Strategy core — R1 / R2 / R6 / R7 (4 cases)
# ===========================================================================


def test_warmup_returns_none_when_too_few_bars(eur_usd: Instrument):
    """R1: less than warmup_bars_required() completed bars → None."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    frame = _build_h4_frame(10)  # < 50
    cfg = _default_cfg()
    cfg["cross_pair_closes"] = _make_cross_pair_closes(
        {p: 0.0 for p in EXPECTED_PAIRS}
    )
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_no_signal_when_open_position_present(eur_usd: Instrument):
    """R2: an open position blocks re-entry."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    returns = {
        "EUR_USD": +0.10, "GBP_USD": +0.05, "AUD_USD": +0.05,
        "NZD_USD": +0.05, "USD_JPY": -0.05, "USD_CAD": -0.05,
        "USD_CHF": -0.05,
    }
    closes = _make_cross_pair_closes(returns)
    cfg = _default_cfg()
    cfg["cross_pair_closes"] = closes
    frame = _build_h4_frame(60)
    assert (
        strat.generate_signal(
            _ctx(
                frame, eur_usd, config=cfg,
                open_position_units=Decimal("1000"),
            )
        )
        is None
    )


def test_fail_closed_when_h4_atr_is_zero(eur_usd: Instrument):
    """R6: prior_atr_h4 <= 0 → None."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    returns = {
        "EUR_USD": +0.10, "GBP_USD": +0.05, "AUD_USD": +0.05,
        "NZD_USD": +0.05, "USD_JPY": -0.05, "USD_CAD": -0.05,
        "USD_CHF": -0.05,
    }
    closes = _make_cross_pair_closes(returns)
    cfg = _default_cfg()
    cfg["cross_pair_closes"] = closes
    # Flat H4 bars on EUR_USD → ATR = 0.
    frame = _build_h4_frame(60, range_size=0.0)
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_stop_placement_long_and_short(eur_usd: Instrument):
    """R7: long-stop below close; short-stop above close; both at 2.0 * prior_atr_h4."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    # Long
    returns_long = {
        "EUR_USD": +0.10, "GBP_USD": +0.05, "AUD_USD": +0.05,
        "NZD_USD": +0.05, "USD_JPY": -0.05, "USD_CAD": -0.05,
        "USD_CHF": -0.05,
    }
    cfg = _default_cfg()
    cfg["cross_pair_closes"] = _make_cross_pair_closes(returns_long)
    frame = _build_h4_frame(60)
    sig_long = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert sig_long is not None
    assert sig_long.side == "long"
    expected_long_stop = float(sig_long.features["last_close"]) - 2.0 * float(
        sig_long.features["prior_atr_h4"]
    )
    assert abs(float(sig_long.stop_price) - expected_long_stop) < 1e-4

    # Short
    returns_short = {
        "EUR_USD": -0.10, "GBP_USD": -0.05, "AUD_USD": -0.05,
        "NZD_USD": -0.05, "USD_JPY": +0.05, "USD_CAD": +0.05,
        "USD_CHF": +0.05,
    }
    cfg["cross_pair_closes"] = _make_cross_pair_closes(returns_short)
    sig_short = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert sig_short is not None
    assert sig_short.side == "short"
    expected_short_stop = float(sig_short.features["last_close"]) + 2.0 * float(
        sig_short.features["prior_atr_h4"]
    )
    assert abs(float(sig_short.stop_price) - expected_short_stop) < 1e-4


# ===========================================================================
# 8. R3 / R4 fail-closed (5 cases)
# ===========================================================================


def test_r3_no_signal_when_cross_pair_closes_missing(eur_usd: Instrument):
    """R3: cross_pair_closes missing from ctx.config → None."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    cfg = _default_cfg()  # no cross_pair_closes key
    frame = _build_h4_frame(60)
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_r3_no_signal_when_pair_set_mismatch(eur_usd: Instrument):
    """R3: cross_pair_closes key-set doesn't match EXPECTED_PAIRS → None."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    cfg = _default_cfg()
    # Build closes for only a subset of the 7 pairs.
    cfg["cross_pair_closes"] = _make_cross_pair_closes(
        {"EUR_USD": 0.0, "GBP_USD": 0.0}
    )
    frame = _build_h4_frame(60)
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_r4_no_signal_when_pair_has_insufficient_lookback(eur_usd: Instrument):
    """R4: any pair's close series shorter than n+1 = 25 bars → None."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    cfg = _default_cfg()
    # Build closes with only 10 bars per pair (< 25 required).
    short_closes = _make_cross_pair_closes(
        {p: 0.0 for p in EXPECTED_PAIRS}, lookback_bars=9
    )
    cfg["cross_pair_closes"] = short_closes
    frame = _build_h4_frame(60)
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_r4_no_signal_when_close_is_non_finite(eur_usd: Instrument):
    """R4: any pair's close is NaN / inf → None."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    cfg = _default_cfg()
    closes = _make_cross_pair_closes({p: 0.0 for p in EXPECTED_PAIRS})
    # Inject a NaN at the last index of one pair's series.
    closes["USD_JPY"].iloc[-1] = float("nan")
    cfg["cross_pair_closes"] = closes
    frame = _build_h4_frame(60)
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


def test_r4_no_signal_when_close_is_non_positive(eur_usd: Instrument):
    """R4: any pair's close is <= 0 → None."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    cfg = _default_cfg()
    closes = _make_cross_pair_closes({p: 0.0 for p in EXPECTED_PAIRS})
    closes["AUD_USD"].iloc[0] = -0.5  # negative close
    cfg["cross_pair_closes"] = closes
    frame = _build_h4_frame(60)
    assert strat.generate_signal(_ctx(frame, eur_usd, config=cfg)) is None


# ===========================================================================
# 9. No-lookahead structural audit (4 cases)
# ===========================================================================


def test_strategy_module_does_not_read_forbidden_bar_t_fields():
    """The strategy must not read bar-t high/low/open/volume by index."""
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    forbidden = [
        r'df\["high"\]\.iloc\[-1\]',
        r'df\["low"\]\.iloc\[-1\]',
        r'df\["open"\]\.iloc\[-1\]',
        r'df\["volume"\]\.iloc\[-1\]',
    ]
    for pattern in forbidden:
        assert re.search(pattern, src_stripped) is None, (
            f"strategy module reads forbidden bar-t field: {pattern!r}"
        )


def test_strategy_module_reads_close_for_stop_only():
    """close[t] is read only in R7 (stop placement)."""
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    # R7 reads df["close"].iloc[-1] for stop placement
    assert re.search(r'df\["close"\]\.iloc\[-1\]', src_stripped) is not None


def test_signal_id_is_deterministic(eur_usd: Instrument):
    """Same inputs → same signal_id across two instances."""
    strat1 = CrossPairCurrencyStrengthRotationStrategy()
    strat2 = CrossPairCurrencyStrengthRotationStrategy()
    returns = {
        "EUR_USD": +0.10, "GBP_USD": +0.05, "AUD_USD": +0.05,
        "NZD_USD": +0.05, "USD_JPY": -0.05, "USD_CAD": -0.05,
        "USD_CHF": -0.05,
    }
    cfg = _default_cfg()
    cfg["cross_pair_closes"] = _make_cross_pair_closes(returns)
    frame = _build_h4_frame(60)
    sig1 = strat1.generate_signal(_ctx(frame, eur_usd, config=cfg))
    sig2 = strat2.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert sig1 is not None and sig2 is not None
    assert sig1.signal_id == sig2.signal_id


def test_strategy_does_not_mutate_config(eur_usd: Instrument):
    """signal generation reads cfg but never mutates."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    returns = {
        "EUR_USD": +0.10, "GBP_USD": +0.05, "AUD_USD": +0.05,
        "NZD_USD": +0.05, "USD_JPY": -0.05, "USD_CAD": -0.05,
        "USD_CHF": -0.05,
    }
    cfg = _default_cfg()
    cfg["cross_pair_closes"] = _make_cross_pair_closes(returns)
    cfg_keys_before = set(cfg.keys())
    cfg_lookback_before = cfg["currency_strength_lookback_bars"]
    frame = _build_h4_frame(60)
    _ = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert set(cfg.keys()) == cfg_keys_before
    assert cfg["currency_strength_lookback_bars"] == cfg_lookback_before


# ===========================================================================
# 10. Forbidden imports / usages (4 cases)
# ===========================================================================


def test_strategy_module_does_not_import_random_or_numpy_random():
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    assert "import random" not in src_stripped
    assert "from random import" not in src_stripped
    assert "import numpy.random" not in src_stripped
    assert "from numpy.random" not in src_stripped
    assert "np.random" not in src_stripped
    assert "numpy.random" not in src_stripped


def test_strategy_module_does_not_import_secrets():
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    assert "import secrets" not in src_stripped
    assert "from secrets" not in src_stripped


def test_strategy_module_does_not_use_builtin_hash():
    """Builtin hash() is not deterministic across processes."""
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    bare_hash_calls = re.findall(r"(?<![\.\w])hash\s*\(", src_stripped)
    assert not bare_hash_calls, (
        f"strategy module uses built-in hash(): {bare_hash_calls}"
    )


def test_strategy_module_does_not_import_broker_execution_loops():
    src = _STRATEGY_SOURCE
    forbidden_imports = (
        "from forex_bot.broker",
        "from forex_bot.execution",
        "from forex_bot.loops",
        "import forex_bot.broker",
        "import forex_bot.execution",
        "import forex_bot.loops",
    )
    for forbidden in forbidden_imports:
        assert forbidden not in src, (
            f"strategy module contains forbidden import: {forbidden!r}"
        )


# ===========================================================================
# 11. Rejected-family contamination audit (4 cases)
# ===========================================================================


def test_no_campaign_002_trend_following_keys():
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    forbidden = ("donchian", "ema_fast", "ema_slow", "adx_threshold", "trend_following")
    for key in forbidden:
        assert key.lower() not in src_stripped.lower(), (
            f"strategy module references CAMPAIGN_002-family key: {key!r}"
        )


def test_no_campaign_010_session_breakout_keys():
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    forbidden = (
        "asian_session_hours", "london_session_hours",
        "min_asian_range_atr_fraction", "session_breakout",
        "in_asian_window", "in_london_window",
    )
    for key in forbidden:
        assert key.lower() not in src_stripped.lower(), (
            f"strategy module references CAMPAIGN_010-family key: {key!r}"
        )


def test_no_campaign_011_random_entry_keys():
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    forbidden = (
        "master_seed", "entry_probability_per_bar", "random_entry_anchor",
    )
    for key in forbidden:
        assert key.lower() not in src_stripped.lower(), (
            f"strategy module references CAMPAIGN_011-family key: {key!r}"
        )


def test_no_campaign_012_regime_switcher_keys():
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    forbidden = (
        "daily_atr_lookback", "regime_lookback_days",
        "regime_percentile_threshold", "min_close_move_atr_fraction",
        "trend_lookback_h4_bars", "regime_switcher_atr_percentile",
    )
    for key in forbidden:
        assert key.lower() not in src_stripped.lower(), (
            f"strategy module references CAMPAIGN_012-family key: {key!r}"
        )


# ===========================================================================
# 12. Approval / safety regression (4 cases)
# ===========================================================================


def test_approved_strategies_yaml_remains_empty():
    """The scaffold sprint MUST NOT add this candidate to the registry."""
    path = _REPO_ROOT / "configs" / "approved_strategies.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data == {"approved": []}, (
        f"approved_strategies.yaml is no longer empty: {data}"
    )


def test_cross_pair_rotation_not_enabled_in_paper_config():
    path = _REPO_ROOT / "configs" / "paper.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    enabled = data.get("strategy", {}).get("enabled", [])
    assert "cross_pair_currency_strength_rotation" not in enabled


def test_cross_pair_rotation_not_enabled_in_practice_config():
    path = _REPO_ROOT / "configs" / "practice.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    enabled = data.get("strategy", {}).get("enabled", [])
    assert "cross_pair_currency_strength_rotation" not in enabled


def test_strategy_class_exposes_no_approval_shaped_attribute():
    forbidden_substrings = ("approve", "approval", "promote", "promotion")
    public_attrs = [
        attr
        for attr in dir(CrossPairCurrencyStrengthRotationStrategy)
        if not attr.startswith("_")
    ]
    for attr in public_attrs:
        for sub in forbidden_substrings:
            assert sub not in attr.lower(), (
                f"strategy exposes approval-shaped attribute: {attr!r}"
            )


# ===========================================================================
# 13. Signal emission shape (2 cases)
# ===========================================================================


def test_signal_emitted_with_expected_fields(eur_usd: Instrument):
    """When a signal fires, every expected feature is populated."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    returns = {
        "EUR_USD": +0.10, "GBP_USD": +0.05, "AUD_USD": +0.05,
        "NZD_USD": +0.05, "USD_JPY": -0.05, "USD_CAD": -0.05,
        "USD_CHF": -0.05,
    }
    cfg = _default_cfg()
    cfg["cross_pair_closes"] = _make_cross_pair_closes(returns)
    frame = _build_h4_frame(60)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert sig is not None
    assert sig.strategy_name == "cross_pair_currency_strength_rotation"
    assert sig.strategy_version == "0.1.0-c013"
    assert sig.instrument == "EUR_USD"
    assert sig.timeframe == "H4"
    assert sig.side in ("long", "short")
    assert sig.entry_intent == "market"
    assert sig.exit_model == "time_stop_only"
    assert sig.stop_model == "ATR14*2.0"
    for required_feature in (
        "currency_strength_lookback_bars",
        "rank_gap_threshold",
        "rank_gap",
        "base_currency",
        "quote_currency",
        "base_rank",
        "quote_rank",
        "prior_atr_h4",
        "last_close",
        "strength_EUR", "strength_GBP", "strength_USD", "strength_JPY",
        "strength_AUD", "strength_CAD", "strength_CHF", "strength_NZD",
    ):
        assert required_feature in sig.features
    assert sig.features["base_currency"] == "EUR"
    assert sig.features["quote_currency"] == "USD"


def test_signal_reason_describes_rotation(eur_usd: Instrument):
    """The reason string describes the cross-pair rotation."""
    strat = CrossPairCurrencyStrengthRotationStrategy()
    returns = {
        "EUR_USD": +0.10, "GBP_USD": +0.05, "AUD_USD": +0.05,
        "NZD_USD": +0.05, "USD_JPY": -0.05, "USD_CAD": -0.05,
        "USD_CHF": -0.05,
    }
    cfg = _default_cfg()
    cfg["cross_pair_closes"] = _make_cross_pair_closes(returns)
    frame = _build_h4_frame(60)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert sig is not None
    reason_lower = sig.reason.lower()
    assert "cross-pair" in reason_lower or "rotation" in reason_lower
    assert "gap" in reason_lower


# ===========================================================================
# 14. Helper-level no-state audit (2 cases)
# ===========================================================================


def test_log_return_n_pure_function():
    """_log_return_n inspects only the two endpoints (iloc[-1] and iloc[-1-n]).

    Binding: matches the strategy's no-lookahead contract — only the
    closed endpoints are read; intermediate bars are irrelevant to
    the log-return value (and irrelevant to fail-closed checks).
    """
    series = pd.Series([1.0, 1.01, 1.02, 1.03, 1.04, 1.05])
    a = _log_return_n(series, 5)
    b = _log_return_n(series, 5)
    assert a == b
    assert a == pytest.approx(float(np.log(1.05) - np.log(1.0)))
    # Insufficient history: returns None.
    assert _log_return_n(series, 10) is None
    # Non-finite at the LAST index: returns None.
    bad_last = pd.Series([1.0, 1.01, 1.02, 1.03, 1.04, float("nan")])
    assert _log_return_n(bad_last, 5) is None
    # Non-finite at the prior endpoint (iloc[-1-n]): returns None.
    bad_first = pd.Series([float("nan"), 1.01, 1.02, 1.03, 1.04, 1.05])
    assert _log_return_n(bad_first, 5) is None
    # <= 0 at the LAST index: returns None.
    neg_last = pd.Series([1.0, 1.01, 1.02, 1.03, 1.04, -0.5])
    assert _log_return_n(neg_last, 5) is None
    # <= 0 at the prior endpoint: returns None.
    neg_first = pd.Series([-0.5, 1.01, 1.02, 1.03, 1.04, 1.05])
    assert _log_return_n(neg_first, 5) is None


def test_helpers_independent_of_input_ordering():
    """_compute_strength + _compute_ranks: same inputs in different
    dict-insertion order produce the same outputs."""
    pairs_fwd = [(p, float(i * 0.001)) for i, p in enumerate(EXPECTED_PAIRS)]
    pairs_rev = list(reversed(pairs_fwd))
    r_fwd = dict(pairs_fwd)
    r_rev = dict(pairs_rev)
    assert _compute_strength(r_fwd) == _compute_strength(r_rev)
    s = _compute_strength(r_fwd)
    s2 = _compute_strength(r_rev)
    assert _compute_ranks(s) == _compute_ranks(s2)


# ===========================================================================
# 15. NON_USD_CURRENCIES + EXPECTED_PAIRS consistency (1 case)
# ===========================================================================


def test_module_constants_consistent():
    """NON_USD_CURRENCIES covers all 7 non-USD currencies; EXPECTED_PAIRS has 7 entries."""
    assert len(EXPECTED_PAIRS) == 7
    assert len(NON_USD_CURRENCIES) == 7
    assert set(NON_USD_CURRENCIES) == {"EUR", "GBP", "AUD", "NZD", "JPY", "CAD", "CHF"}
    # Each pair contains USD.
    for pair in EXPECTED_PAIRS:
        assert "USD" in pair.split("_")

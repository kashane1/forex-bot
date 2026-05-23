"""Model + schema tests for the free / local parity verifier.

Pins the verifier-side data contracts: Bar OHLC consistency, candle
series sortedness/uniqueness, config invariants, the
`strategy_evidence: false` and `risk_engine_used: false` rails on
``VerifierResult`` / ``ComparisonReport``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError
from research.parity_verifier.data_loader import (
    DEFAULT_BESPOKE_REFERENCE_PATH,
    DEFAULT_CONFIG_PATH,
    config_hash,
    load_bespoke_reference,
    load_verifier_config,
)
from research.parity_verifier.instruments import (
    CAMPAIGN_002_INSTRUMENTS,
    get_instrument,
)
from research.parity_verifier.models import (
    Bar,
    CandleSeries,
    ComparisonReport,
    ComparisonStatus,
    DivergenceClassification,
    PairComparison,
    PairResult,
    Side,
    TradeExitReason,
    VerifierConfig,
    VerifierResult,
)


def _bar(ts: datetime, *, open_: float = 1.10, close: float = 1.10) -> Bar:
    return Bar(
        time=ts,
        open=open_,
        high=close + 0.001,
        low=open_ - 0.001,
        close=close,
        bid_open=open_ - 0.00005,
        bid_high=close + 0.001 - 0.00005,
        bid_low=open_ - 0.001 - 0.00005,
        bid_close=close - 0.00005,
        ask_open=open_ + 0.00005,
        ask_high=close + 0.001 + 0.00005,
        ask_low=open_ - 0.001 + 0.00005,
        ask_close=close + 0.00005,
        volume=10,
    )


def test_bar_rejects_high_less_than_low() -> None:
    with pytest.raises(ValidationError):
        Bar(
            time=datetime(2024, 1, 1, tzinfo=UTC),
            open=1.0, high=0.9, low=1.05, close=1.0,
            bid_open=1.0, bid_high=0.9, bid_low=1.05, bid_close=1.0,
            ask_open=1.0, ask_high=0.9, ask_low=1.05, ask_close=1.0,
        )


def test_bar_rejects_ask_below_bid() -> None:
    with pytest.raises(ValidationError):
        Bar(
            time=datetime(2024, 1, 1, tzinfo=UTC),
            open=1.0, high=1.01, low=0.99, close=1.0,
            bid_open=1.001, bid_high=1.011, bid_low=0.991, bid_close=1.001,
            ask_open=0.999, ask_high=1.009, ask_low=0.989, ask_close=0.999,
        )


def test_candle_series_rejects_unsorted() -> None:
    later = _bar(datetime(2024, 1, 2, tzinfo=UTC))
    earlier = _bar(datetime(2024, 1, 1, tzinfo=UTC))
    with pytest.raises(ValidationError):
        CandleSeries(instrument="EUR_USD", bars=[later, earlier])


def test_candle_series_rejects_duplicate_timestamps() -> None:
    ts = datetime(2024, 1, 1, tzinfo=UTC)
    with pytest.raises(ValidationError):
        CandleSeries(instrument="EUR_USD", bars=[_bar(ts), _bar(ts)])


def test_verifier_config_rejects_ema_fast_ge_slow() -> None:
    with pytest.raises(ValidationError):
        VerifierConfig(
            ema_fast=200,
            ema_slow=200,
            donchian_lookback=20,
            atr_lookback=14,
            atr_stop_multiple=2.0,
            trailing_stop_atr_multiple=2.0,
            max_bars_in_trade=240,
            risk_per_trade_pct=0.25,
            starting_equity_usd=500.0,
            fixed_slippage_pips=0.2,
            spread_slippage_multiplier=0.5,
        )


def test_verifier_config_rejects_zero_risk() -> None:
    with pytest.raises(ValidationError):
        VerifierConfig(
            ema_fast=50,
            ema_slow=200,
            donchian_lookback=20,
            atr_lookback=14,
            atr_stop_multiple=2.0,
            trailing_stop_atr_multiple=2.0,
            max_bars_in_trade=240,
            risk_per_trade_pct=0.0,
            starting_equity_usd=500.0,
            fixed_slippage_pips=0.2,
            spread_slippage_multiplier=0.5,
        )


def test_verifier_result_rejects_strategy_evidence_true() -> None:
    with pytest.raises(ValidationError):
        VerifierResult(
            parity_target="x",
            risk_engine_used=False,
            fill_timing="signal_bar_close",
            window_start=datetime(2020, 1, 1, tzinfo=UTC),
            window_end=datetime(2026, 5, 20, tzinfo=UTC),
            config_hash="x",
            strategy_evidence=True,
            total_trades=0,
            pairs=[],
        )


def test_verifier_result_rejects_risk_engine_used() -> None:
    with pytest.raises(ValidationError):
        VerifierResult(
            parity_target="x",
            risk_engine_used=True,
            fill_timing="signal_bar_close",
            window_start=datetime(2020, 1, 1, tzinfo=UTC),
            window_end=datetime(2026, 5, 20, tzinfo=UTC),
            config_hash="x",
            strategy_evidence=False,
            total_trades=0,
            pairs=[],
        )


def test_verifier_result_rejects_total_mismatch() -> None:
    with pytest.raises(ValidationError):
        VerifierResult(
            parity_target="x",
            fill_timing="signal_bar_close",
            window_start=datetime(2020, 1, 1, tzinfo=UTC),
            window_end=datetime(2026, 5, 20, tzinfo=UTC),
            config_hash="x",
            total_trades=999,
            pairs=[PairResult(instrument="EUR_USD", candle_count=10, trades=0)],
        )


def test_verifier_result_accepts_consistent_totals() -> None:
    res = VerifierResult(
        parity_target="x",
        fill_timing="signal_bar_close",
        window_start=datetime(2020, 1, 1, tzinfo=UTC),
        window_end=datetime(2026, 5, 20, tzinfo=UTC),
        config_hash="x",
        total_trades=3,
        pairs=[
            PairResult(instrument="EUR_USD", candle_count=10, trades=2),
            PairResult(instrument="GBP_USD", candle_count=10, trades=1),
        ],
    )
    assert res.total_trades == 3


def test_comparison_report_rejects_strategy_evidence_true() -> None:
    with pytest.raises(ValidationError):
        ComparisonReport(
            bespoke_reference_path="x",
            verifier_result_path=None,
            pairs=[],
            bespoke_total_trades=0,
            verifier_total_trades=None,
            total_trade_count_delta_pct=None,
            overall_status=ComparisonStatus.OK,
            overall_classification=DivergenceClassification.NONE,
            strategy_evidence=True,
        )


def test_pair_comparison_roundtrip() -> None:
    pc = PairComparison(
        instrument="EUR_USD",
        bespoke_trades=233,
        verifier_trades=230,
        trade_count_delta_pct=-1.288,
        bespoke_expectancy_r=-0.196,
        verifier_expectancy_r=-0.18,
        expectancy_r_delta=0.016,
        bespoke_return_pct=-10.83,
        verifier_return_pct=-10.3,
        return_pct_delta=0.53,
        status=ComparisonStatus.WARN,
        classification=DivergenceClassification.UNKNOWN,
    )
    dump = pc.model_dump()
    assert PairComparison(**dump) == pc


def test_instrument_metadata_complete() -> None:
    expected = {
        "EUR_USD",
        "GBP_USD",
        "USD_JPY",
        "AUD_USD",
        "USD_CAD",
        "USD_CHF",
        "NZD_USD",
    }
    assert set(CAMPAIGN_002_INSTRUMENTS) == expected
    for name in expected:
        spec = get_instrument(name)
        if "JPY" in name:
            assert spec.pip_size == 0.01
            assert spec.display_precision == 3
        else:
            assert spec.pip_size == 0.0001
            assert spec.display_precision == 5


def test_instrument_lookup_unknown_raises() -> None:
    with pytest.raises(KeyError):
        get_instrument("BTC_USD")


def test_load_verifier_config_from_authoritative_json() -> None:
    config = load_verifier_config(DEFAULT_CONFIG_PATH)
    assert config.ema_fast == 50
    assert config.ema_slow == 200
    assert config.donchian_lookback == 20
    assert config.atr_lookback == 14
    assert config.atr_stop_multiple == 2.0
    assert config.trailing_stop_atr_multiple == 2.0
    assert config.max_bars_in_trade == 240
    assert config.risk_per_trade_pct == 0.25
    assert config.starting_equity_usd == 500.0
    assert config.fixed_slippage_pips == 0.2
    assert config.spread_slippage_multiplier == 0.5
    assert config.min_atr_pips == {}


def test_config_hash_deterministic() -> None:
    a = load_verifier_config(DEFAULT_CONFIG_PATH)
    b = load_verifier_config(DEFAULT_CONFIG_PATH)
    assert config_hash(a) == config_hash(b)
    assert len(config_hash(a)) == 64


def test_load_bespoke_reference_shape() -> None:
    ref = load_bespoke_reference(DEFAULT_BESPOKE_REFERENCE_PATH)
    assert ref["parity_target"] == "CAMPAIGN_002 H4 trend_following baseline"
    assert ref["strategy_evidence"] is False
    assert ref["risk_engine_used"] is False
    assert ref["total_trades"] == 1647
    pairs = {p["instrument"]: p for p in ref["pairs"]}
    assert set(pairs) == {
        "EUR_USD",
        "GBP_USD",
        "USD_JPY",
        "AUD_USD",
        "USD_CAD",
        "USD_CHF",
        "NZD_USD",
    }


def test_side_and_exit_reason_enum_values() -> None:
    assert Side.LONG.value == "long"
    assert Side.SHORT.value == "short"
    assert Side.FLAT.value == "flat"
    assert TradeExitReason.STOP.value == "stop"
    assert TradeExitReason.TRAILING_STOP.value == "trailing_stop"
    assert TradeExitReason.TIME.value == "time"
    assert TradeExitReason.EOD.value == "eod"


def test_verifier_package_does_not_import_forex_bot() -> None:
    """Independence rail: no file under research/parity_verifier/ may
    import the bespoke engine. A grep is sufficient because Python's
    import resolution only fires on the exact name."""

    pkg = Path(__file__).resolve().parents[2] / "research" / "parity_verifier"
    offenders: list[str] = []
    for path in pkg.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if "forex_bot" in stripped and (
                stripped.startswith("import ") or stripped.startswith("from ")
            ):
                offenders.append(f"{path}:{line_no}: {stripped}")
    assert offenders == [], "verifier must not import forex_bot:\n" + "\n".join(offenders)

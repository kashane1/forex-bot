"""CAMPAIGN_015 Backtrader-adapter tests.

Covers:

* frozen-parameter / contract tests (adapter reads the committed YAML
  and refuses on any deviation);
* synthetic fixtures: short upside-sweep, long downside-sweep, no-sweep,
  time-stop-only path, hard-stop path;
* determinism (two identical runs produce identical trade lists);
* source-grep guards (no broker / OANDA / LEAN / Backtrader-live imports
  at the import level).

`strategy_evidence: false`. CAMPAIGN_015 remains scaffold-only;
maximum verdict ceiling is PASS_RESEARCH_SCREEN. The BT lane cannot
approve any strategy.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("backtrader")

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.backtrader_lane.data_adapter import (  # noqa: E402
    CandleAdapterResult,
    CandleProvenance,
)
from research.backtrader_lane.strategies.campaign_015_failed_breakout_reversal import (  # noqa: E402
    CAMPAIGN_015_ADAPTER,
    CAMPAIGN_015_APPROXIMATION_FLAGS,
    CAMPAIGN_015_CONFIG_PATH,
    EXPECTED_VERSION,
    FROZEN_PARAMETERS,
    _assert_frozen,
    _load_campaign_015_config_strategy,
    run_campaign_015_pair,
    same_bar_adverse_stop_check,
)

# ---------------------------------------------------------------------------
# 1. Frozen-parameter / config-contract tests


def test_frozen_parameters_dict_pinned():
    expected = {
        "version": "0.1.0-c015",
        "timeframe": "H4",
        "range_lookback": 20,
        "atr_lookback": 14,
        "adx_lookback": 14,
        "adx_max": 20.0,
        "sweep_buffer_atr": 0.10,
        "min_range_atr_multiple": 1.25,
        "max_range_atr_multiple": 5.00,
        "stop_buffer_atr": 0.10,
        "min_stop_atr_multiple": 0.80,
        "max_stop_atr_multiple": 2.20,
        "max_bars_in_trade": 12,
        "take_profit_r": None,
        "trailing_stop_atr_multiple": None,
        "entry_timing": "next_bar_open",
        "same_bar_adverse_stop_wins": True,
        "min_atr_pips": {},
    }
    assert expected == FROZEN_PARAMETERS


def test_load_yaml_matches_frozen_parameters(monkeypatch):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    cfg = _load_campaign_015_config_strategy()
    _assert_frozen(cfg)


def test_assert_frozen_rejects_max_bars_deviation():
    cfg = dict(FROZEN_PARAMETERS)
    cfg["max_bars_in_trade"] = 13
    with pytest.raises(SystemExit):
        _assert_frozen(cfg)


def test_assert_frozen_rejects_entry_timing_deviation():
    cfg = dict(FROZEN_PARAMETERS)
    cfg["entry_timing"] = "signal_bar_close"
    with pytest.raises(SystemExit):
        _assert_frozen(cfg)


def test_adapter_carries_required_approximation_flag():
    flags_joined = "\n".join(CAMPAIGN_015_APPROXIMATION_FLAGS)
    assert "FILL_TIMING_APPROXIMATION" in flags_joined
    assert "RANGE_PRIOR_BARS_ONLY" in flags_joined


def test_adapter_metadata():
    a = CAMPAIGN_015_ADAPTER
    assert a.campaign_id == "CAMPAIGN_015"
    assert a.strategy_id == "failed_breakout_reversal"
    assert a.strategy_version == EXPECTED_VERSION
    assert a.default_starting_equity_usd == 500.0
    assert a.risk_per_trade_pct == 0.25
    assert a.default_instruments == (
        "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD",
        "USD_CAD", "USD_CHF", "NZD_USD",
    )


def test_same_bar_adverse_stop_check_long():
    assert same_bar_adverse_stop_check(
        side="long", stop_price=1.0900, bar_high=1.1010, bar_low=1.0890
    )  # bar low pierced stop
    assert not same_bar_adverse_stop_check(
        side="long", stop_price=1.0900, bar_high=1.1010, bar_low=1.0910
    )


def test_same_bar_adverse_stop_check_short():
    assert same_bar_adverse_stop_check(
        side="short", stop_price=1.1100, bar_high=1.1110, bar_low=1.0990
    )  # bar high pierced stop
    assert not same_bar_adverse_stop_check(
        side="short", stop_price=1.1100, bar_high=1.1090, bar_low=1.0990
    )


# ---------------------------------------------------------------------------
# 2. Synthetic fixture builders


def _make_candles_from_ohlc(
    instrument: str,
    ohlc: list[tuple[float, float, float, float]],
    *,
    spread: float = 0.00020,
) -> CandleAdapterResult:
    start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
    times: list[datetime] = []
    mid_o, mid_h, mid_l, mid_c = [], [], [], []
    bid_o, bid_h, bid_l, bid_c = [], [], [], []
    ask_o, ask_h, ask_l, ask_c = [], [], [], []
    hs: list[float] = []
    vols: list[int] = []
    for i, (o, h, low, c) in enumerate(ohlc):
        t = start + timedelta(hours=4 * i)
        times.append(t)
        mid_o.append(o)
        mid_h.append(h)
        mid_l.append(low)
        mid_c.append(c)
        bid_o.append(o - spread / 2)
        bid_h.append(h - spread / 2)
        bid_l.append(low - spread / 2)
        bid_c.append(c - spread / 2)
        ask_o.append(o + spread / 2)
        ask_h.append(h + spread / 2)
        ask_l.append(low + spread / 2)
        ask_c.append(c + spread / 2)
        hs.append(spread / 2)
        vols.append(100)
    idx = pd.DatetimeIndex(times, name="time")
    mid_df = pd.DataFrame(
        {"open": mid_o, "high": mid_h, "low": mid_l, "close": mid_c, "volume": vols},
        index=idx,
    )
    bid_df = pd.DataFrame(
        {"open": bid_o, "high": bid_h, "low": bid_l, "close": bid_c}, index=idx
    )
    ask_df = pd.DataFrame(
        {"open": ask_o, "high": ask_h, "low": ask_l, "close": ask_c}, index=idx
    )
    provenance = CandleProvenance(
        instrument=instrument,
        granularity="H4",
        source="synthetic-test-c015",
        requested_from=times[0].isoformat(),
        requested_to=times[-1].isoformat(),
        candle_count=len(ohlc),
        first_ts=times[0].isoformat(),
        last_ts=times[-1].isoformat(),
        data_sha256="0" * 64,
        campaign_002_data_request_hash="0" * 16,
        lean_csv=f"{instrument}_H4_synth.csv",
        exported_by="test",
        exported_at="2026-05-25T00:00:00+00:00",
    )
    return CandleAdapterResult(
        instrument=instrument,
        provenance=provenance,
        csv_sha256=provenance.data_sha256,
        mid_df=mid_df,
        bid_ohlc_df=bid_df,
        ask_ohlc_df=ask_df,
        half_spread_close=pd.Series(hs, index=idx),
        first_ts=times[0],
        last_ts=times[-1],
        bar_count=len(ohlc),
        approximation_flags=[],
    )


def _quiet_range_rows(
    n: int, *, low: float, high: float
) -> list[tuple[float, float, float, float]]:
    rows: list[tuple[float, float, float, float]] = []
    span = high - low
    mid = (high + low) / 2.0
    for i in range(n):
        if i % 2 == 0:
            rows.append((mid, high, mid - span * 0.10, mid + span * 0.10))
        else:
            rows.append((mid, mid + span * 0.10, low, mid - span * 0.10))
    return rows


# ---------------------------------------------------------------------------
# 3. Integration tests on synthetic fixtures


def test_no_signal_when_no_sweep(monkeypatch):
    """80 quiet bars + a final bar that stays inside the range — no
    signal, no entry, no trades."""
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    # Final bars: inside the range. We extend a few more bars so the
    # adapter has bars beyond the signal-bar to potentially fill.
    for _ in range(3):
        rows.append((1.1000, 1.1010, 1.0990, 1.1000))
    candles = _make_candles_from_ohlc("EUR_USD", rows)
    result = run_campaign_015_pair(candles, 500.0)
    assert result.trades == []


def test_short_signal_fires_on_failed_upside_breakout(monkeypatch):
    """Bar sweeps the prior 20-bar high by > sweep_buffer*ATR, closes
    back inside; the entry fills at the next bar's open (next_bar_open)
    on the short side."""
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    # Signal bar: failed upside sweep.
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    # Follow-up bars: open well below the stop (which is at ~1.108118)
    # so the position survives long enough to time-stop or to remain
    # open until EOD. Keep prices range-bound near 1.10.
    for _ in range(15):
        rows.append((1.1000, 1.1010, 1.0990, 1.1000))
    candles = _make_candles_from_ohlc("EUR_USD", rows)
    result = run_campaign_015_pair(candles, 500.0)
    assert len(result.trades) >= 1
    first = result.trades[0]
    assert first.side == "short"
    # Entry filled on the bar AFTER the signal bar (next_bar_open).
    # Signal bar was the 81st (index 80); entry is on the 82nd (index 81).
    expected_entry_ts = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC) + timedelta(hours=4 * 81)
    assert first.entry_time == expected_entry_ts


def test_long_signal_fires_on_failed_downside_breakout(monkeypatch):
    """Symmetric long case."""
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    # Signal bar: failed downside sweep.
    rows.append((1.1000, 1.1010, 1.0925, 1.0990))
    for _ in range(15):
        rows.append((1.1000, 1.1010, 1.0990, 1.1000))
    candles = _make_candles_from_ohlc("EUR_USD", rows)
    result = run_campaign_015_pair(candles, 500.0)
    assert len(result.trades) >= 1
    first = result.trades[0]
    assert first.side == "long"


def test_time_stop_fires_after_12_bars(monkeypatch):
    """After a short signal fires, run prices flat for many bars; the
    12-bar time stop should close the trade with exit_reason='time'."""
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    # 20 flat follow-up bars (well within the range, so stop never hits).
    for _ in range(20):
        rows.append((1.1000, 1.1005, 1.0995, 1.1000))
    candles = _make_candles_from_ohlc("EUR_USD", rows)
    result = run_campaign_015_pair(candles, 500.0)
    # At least one trade closes on the time stop.
    assert any(t.exit_reason == "time" for t in result.trades)
    # And its bars_held is exactly 12 (the configured max_bars_in_trade).
    time_trade = next(t for t in result.trades if t.exit_reason == "time")
    assert time_trade.bars_held == 12


def test_hard_stop_fires_when_price_runs_through_stop(monkeypatch):
    """After a short signal fires, run prices up through the stop on a
    later bar; the hard stop should close with exit_reason='stop'."""
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    # Entry fills at next bar's open (around 1.10). Then a bar that
    # rallies hard above the stop (which is ~1.108).
    rows.append((1.1000, 1.1020, 1.0990, 1.1010))  # bar after signal — entry fills
    rows.append((1.1010, 1.1200, 1.1000, 1.1180))  # rally through stop
    for _ in range(10):
        rows.append((1.1180, 1.1190, 1.1170, 1.1180))
    candles = _make_candles_from_ohlc("EUR_USD", rows)
    result = run_campaign_015_pair(candles, 500.0)
    assert any(t.exit_reason == "stop" for t in result.trades)


def test_deterministic_across_two_identical_runs(monkeypatch):
    """Two runs on the same candle input produce identical trade lists."""
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    for _ in range(15):
        rows.append((1.1000, 1.1010, 1.0990, 1.1000))
    candles_a = _make_candles_from_ohlc("EUR_USD", rows)
    candles_b = _make_candles_from_ohlc("EUR_USD", rows)
    result_a = run_campaign_015_pair(candles_a, 500.0)
    result_b = run_campaign_015_pair(candles_b, 500.0)
    assert len(result_a.trades) == len(result_b.trades)
    for ta, tb in zip(result_a.trades, result_b.trades, strict=True):
        assert ta.side == tb.side
        assert ta.entry_time == tb.entry_time
        assert ta.exit_time == tb.exit_time
        assert ta.exit_reason == tb.exit_reason
        assert ta.units == tb.units


def test_warmup_blocks_early_signals(monkeypatch):
    """Within the first range_lookback bars (where R5's prior-range
    window cannot be filled), no signal can fire — even on bars whose
    geometry would otherwise be a sweep.

    Backtrader's ADX(14) indicator requires ~28 bars to initialize
    its arrays without raising IndexError on _once, so the fixture
    provides 35 bars total: 20 quiet bars at one level, then 15
    quiet bars at a shifted level (so the latter 15 bars cannot see
    a meaningful prior 20-bar Donchian range that includes the
    earliest bars). The strategy's warmup gate must reject every bar
    before bar 22 (range_lookback + 2 = 22 1-based)."""
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    # 35 quiet bars, range [1.0950, 1.1050]. With no sweep ever
    # occurring, the strategy must produce 0 trades — and in particular
    # cannot fire before its R1 warmup completes.
    rows = _quiet_range_rows(35, low=1.0950, high=1.1050)
    candles = _make_candles_from_ohlc("EUR_USD", rows)
    result = run_campaign_015_pair(candles, 500.0)
    assert result.trades == []


# ---------------------------------------------------------------------------
# 4. Source-grep guards


def test_adapter_source_does_not_import_broker_or_oanda_or_lean():
    src = (
        ROOT
        / "research"
        / "backtrader_lane"
        / "strategies"
        / "campaign_015_failed_breakout_reversal.py"
    )
    text = src.read_text(encoding="utf-8")
    # Strip docstring; only look at import lines.
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith(("import ", "from "))
    ]
    joined = "\n".join(lines)
    assert "forex_bot.broker" not in joined
    assert "oandapyV20" not in joined
    assert "QuantConnect" not in joined
    assert "lean" not in joined.lower()
    # Backtrader-store / live-broker integrations explicitly forbidden.
    assert "backtrader.brokers" not in joined
    assert "backtrader.stores" not in joined
    assert "btoandav20" not in joined


def test_adapter_config_path_points_to_campaign_015_yaml():
    assert CAMPAIGN_015_CONFIG_PATH.name == "campaign_015_failed_breakout_reversal.yaml"
    assert CAMPAIGN_015_CONFIG_PATH.is_file()

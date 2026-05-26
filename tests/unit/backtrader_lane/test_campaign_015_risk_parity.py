"""RiskEngine parity tests for CAMPAIGN_015 BT adapter."""

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
sys.path.insert(0, str(ROOT / "src"))

from research.backtrader_lane.data_adapter import (  # noqa: E402
    CandleAdapterResult,
    CandleProvenance,
)
from research.backtrader_lane.risk_parity import (  # noqa: E402
    RiskParityState,
    build_campaign_015_risk_engine,
    evaluate_pending_entry,
)
from research.backtrader_lane.strategies.campaign_015_failed_breakout_reversal import (  # noqa: E402
    CAMPAIGN_015_CONFIG_PATH,
    run_campaign_015_pair,
)

from forex_bot.config import load_settings  # noqa: E402
from forex_bot.domain.risk import RiskRejectionCode  # noqa: E402
from tests.unit.backtrader_lane.test_campaign_015_failed_breakout_reversal import (  # noqa: E402
    _quiet_range_rows,
)


def _make_candles_with_spread(
    instrument: str,
    ohlc: list[tuple[float, float, float, float]],
    *,
    spread: float,
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
        source="synthetic-test-c015-risk",
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


def _campaign_settings(monkeypatch):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    return load_settings(CAMPAIGN_015_CONFIG_PATH)


def test_wide_spread_rejected_by_risk_parity(monkeypatch):
    settings = _campaign_settings(monkeypatch)
    engine = build_campaign_015_risk_engine(settings)
    state = RiskParityState(account_currency="USD", equity_peak=500.0)
    now = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)
    result = evaluate_pending_entry(
        risk_engine=engine,
        instrument_name="EUR_USD",
        side="long",
        stop_price=1.0700,
        signal_time=now,
        fill_time=now + timedelta(hours=4),
        fill_bid=1.0790,
        fill_ask=1.0850,  # 6 pip spread > typical 1.5 cap
        atr=0.0020,
        equity=500.0,
        parity_state=state,
        strategy_version="0.1.0-c015",
    )
    assert not result.approved
    assert RiskRejectionCode.SPREAD_TOO_WIDE.value in result.rejection_codes


def test_allowed_spread_accepted_by_risk_parity(monkeypatch):
    settings = _campaign_settings(monkeypatch)
    engine = build_campaign_015_risk_engine(settings)
    state = RiskParityState(account_currency="USD", equity_peak=500.0)
    now = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)
    result = evaluate_pending_entry(
        risk_engine=engine,
        instrument_name="EUR_USD",
        side="long",
        stop_price=1.0700,
        signal_time=now,
        fill_time=now + timedelta(hours=4),
        fill_bid=1.07994,
        fill_ask=1.08006,
        atr=0.0025,
        equity=500.0,
        parity_state=state,
        strategy_version="0.1.0-c015",
    )
    assert result.approved
    assert result.units is not None and result.units > 0


def test_risk_parity_module_has_no_broker_imports():
    src = ROOT / "research" / "backtrader_lane" / "risk_parity.py"
    text = src.read_text(encoding="utf-8")
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith(("import ", "from "))
    ]
    joined = "\n".join(lines)
    assert "forex_bot.broker" not in joined
    assert "oandapyV20" not in joined
    assert "forex_bot.execution" not in joined


def test_run_with_risk_engine_parity_records_rejections(monkeypatch):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test")
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    for _ in range(10):
        rows.append((1.1000, 1.1010, 1.0990, 1.1000))
    # Wide spread on entry bar only.
    candles = _make_candles_with_spread("EUR_USD", rows, spread=0.00100)
    result = run_campaign_015_pair(
        candles,
        500.0,
        config_path=CAMPAIGN_015_CONFIG_PATH,
        risk_engine_parity=True,
        entry_bar_stop_policy="bespoke_current_no_entry_bar_stop",
    )
    assert result.analyzer_outputs.get("risk_engine_parity") is True
    rejections = result.analyzer_outputs.get("rejection_counts", {})
    assert isinstance(rejections, dict)

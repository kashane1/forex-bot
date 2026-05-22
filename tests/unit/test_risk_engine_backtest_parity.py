"""Task D parity test: a signal rejected by RiskEngine in live mode must
also be rejected when the BacktestEngine drives the same RiskEngine in
backtest mode.

This guards against the BacktestEngine ever drifting from the production
risk path. If new operational-only gates land in RiskEngine in the future
they should be exempted via `mode='backtest'`, and the parity test will
catch silent drift.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from forex_bot.backtesting.engine import BacktestEngine
from forex_bot.backtesting.fills import FillModel
from forex_bot.config import load_settings
from forex_bot.domain.account import AccountSnapshot
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.risk import RiskRejectionCode
from forex_bot.domain.signals import Signal
from forex_bot.risk.policy import RiskEngine, RiskInputs
from forex_bot.strategies.trend_following import TrendFollowingStrategy


@pytest.fixture
def practice_settings(practice_config_path: Path, monkeypatch, tmp_path):
    """Practice config relocated so each test has an isolated DB / KILL_SWITCH."""
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "x")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "y")
    text = practice_config_path.read_text(encoding="utf-8")
    text = text.replace("./KILL_SWITCH", str(tmp_path / "KILL_SWITCH"))
    text = text.replace("./data/bot.sqlite3", str(tmp_path / "bot.sqlite3"))
    text = text.replace("./logs/bot.jsonl", str(tmp_path / "bot.jsonl"))
    out = tmp_path / "practice.yaml"
    out.write_text(text, encoding="utf-8")
    return load_settings(out)


def _frame_long_uptrend(instrument: str, n: int = 300) -> CandleFrame:
    """Synthetic uptrend that reliably breaks Donchian-20 with EMA 50/200 stack."""
    base = Decimal("1.0500")
    candles = []
    for i in range(n):
        m = base + Decimal("0.0002") * i
        bid_c = m - Decimal("0.0001")
        ask_c = m + Decimal("0.0001")
        prev = base + Decimal("0.0002") * (i - 1) if i > 0 else m
        bid_o = prev - Decimal("0.0001")
        ask_o = prev + Decimal("0.0001")
        candles.append(
            Candle(
                instrument=instrument,
                granularity="H4",
                time=datetime(2025, 1, 1, tzinfo=UTC) + timedelta(hours=4 * i),
                complete=True,
                volume=1000,
                bid_o=bid_o, bid_h=bid_c, bid_l=bid_o, bid_c=bid_c,
                ask_o=ask_o, ask_h=ask_c, ask_l=ask_o, ask_c=ask_c,
            )
        )
    return CandleFrame.from_candles(instrument, "H4", candles)


def _account(nav: Decimal = Decimal("500")) -> AccountSnapshot:
    return AccountSnapshot(
        account_id="acc",
        currency="USD",
        balance=nav,
        nav=nav,
        time=datetime(2026, 5, 21, tzinfo=UTC),
    )


def _signal(stop: Decimal = Decimal("1.07810")) -> Signal:
    return Signal(
        signal_id="sig-1",
        strategy_name="trend_following",
        strategy_version="0.1.0-baseline-frozen",
        instrument="EUR_USD",
        timeframe="H4",
        timestamp=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
        side="long",
        stop_model="ATR14*2.0",
        stop_price=stop,
        exit_model="trailing",
        features={"atr_pips": 10.0},
    )


def _wide_spread_market_state() -> MarketState:
    bid = Decimal("1.0795")
    ask = Decimal("1.0800")  # 5 pip spread vs 1.5 pip cap
    quote = Quote(
        instrument="EUR_USD",
        time=datetime(2026, 5, 21, 12, tzinfo=UTC),
        bid=bid,
        ask=ask,
    )
    return MarketState(
        quote=quote,
        spread_snapshot=SpreadSnapshot(
            instrument="EUR_USD",
            time=quote.time,
            bid=bid,
            ask=ask,
            spread_pips=Decimal("5.0"),
        ),
    )


def test_spread_rejection_parity_live_vs_backtest(practice_settings, eur_usd, quote_eur_usd):
    """A wide-spread signal must be rejected with SPREAD_TOO_WIDE in both
    live mode and backtest mode."""
    live = RiskEngine(practice_settings, mode="live")
    bt = RiskEngine(practice_settings, mode="backtest")

    inputs = RiskInputs(
        signal=_signal(),
        instrument=eur_usd,
        account=_account(),
        market_state=_wide_spread_market_state(),
        positions=[],
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
    )
    live_dec, _ = live.evaluate(inputs)
    bt_dec, _ = bt.evaluate(inputs)

    assert RiskRejectionCode.SPREAD_TOO_WIDE in live_dec.rejection_codes
    assert RiskRejectionCode.SPREAD_TOO_WIDE in bt_dec.rejection_codes
    # Backtest mode must reject for the *same strategy reason* even though
    # operational gates may differ.
    common = set(live_dec.rejection_codes) & set(bt_dec.rejection_codes)
    assert RiskRejectionCode.SPREAD_TOO_WIDE in common


def test_kill_switch_only_in_live_mode(practice_settings, eur_usd, quote_eur_usd):
    """Backtest mode skips the KILL_SWITCH gate (it's an operational signal,
    not a strategy/risk gate)."""
    Path(practice_settings.app.kill_switch_path).write_text("stop")
    try:
        live = RiskEngine(practice_settings, mode="live")
        bt = RiskEngine(practice_settings, mode="backtest")
        ms = MarketState(
            quote=Quote(
                instrument="EUR_USD",
                time=datetime(2026, 5, 21, 12, tzinfo=UTC),
                bid=Decimal("1.07990"),
                ask=Decimal("1.08010"),
            ),
            spread_snapshot=SpreadSnapshot(
                instrument="EUR_USD",
                time=datetime(2026, 5, 21, 12, tzinfo=UTC),
                bid=Decimal("1.07990"),
                ask=Decimal("1.08010"),
                spread_pips=Decimal("2.0"),
            ),
        )
        inputs = RiskInputs(
            signal=_signal(),
            instrument=eur_usd,
            account=_account(),
            market_state=ms,
            positions=[],
            quotes_by_instrument={"EUR_USD": quote_eur_usd},
        )
        live_dec, _ = live.evaluate(inputs)
        bt_dec, _ = bt.evaluate(inputs)
        assert RiskRejectionCode.KILL_SWITCH in live_dec.rejection_codes
        assert RiskRejectionCode.KILL_SWITCH not in bt_dec.rejection_codes
    finally:
        Path(practice_settings.app.kill_switch_path).unlink(missing_ok=True)


def test_backtest_engine_records_rejected_signals_when_spread_wide(
    practice_settings, eur_usd
):
    """End-to-end: drive the BacktestEngine on a frame with a wide-spread
    instrument; the result must surface the rejection."""
    # Build a frame where the last few bars have wide spreads. We use a
    # narrow set: 250 bars at 1 pip spread, then the trend-breakout bar
    # blown out to 5 pips.
    candles = []
    base = Decimal("1.0500")
    for i in range(260):
        m = base + Decimal("0.0002") * i
        # Wide spread on every bar — forces RiskEngine to reject all entries.
        spread = Decimal("0.0005")  # 5 pip
        bid_c = m - spread / 2
        ask_c = m + spread / 2
        prev = base + Decimal("0.0002") * (i - 1) if i > 0 else m
        bid_o = prev - spread / 2
        ask_o = prev + spread / 2
        candles.append(
            Candle(
                instrument="EUR_USD",
                granularity="H4",
                time=datetime(2025, 1, 1, tzinfo=UTC) + timedelta(hours=4 * i),
                complete=True,
                volume=1000,
                bid_o=bid_o, bid_h=bid_c, bid_l=bid_o, bid_c=bid_c,
                ask_o=ask_o, ask_h=ask_c, ask_l=ask_o, ask_c=ask_c,
            )
        )
    frame = CandleFrame.from_candles("EUR_USD", "H4", candles)
    fm = FillModel(
        fixed_slippage_pips=Decimal("0"),
        spread_slippage_multiplier=Decimal("0"),
    )
    engine = BacktestEngine(
        instrument=eur_usd,
        strategy=TrendFollowingStrategy(version="0.1.0-baseline-frozen"),
        strategy_config={
            "ema_fast": 20,
            "ema_slow": 60,
            "donchian_lookback": 10,
            "atr_lookback": 14,
            "atr_stop_multiple": 2.0,
            "min_atr_pips": {},
            "max_bars_in_trade": 60,
            "timeframe": "H4",
        },
        fill_model=fm,
        starting_equity=Decimal("500"),
        account_currency="USD",
        risk_engine=RiskEngine(practice_settings, mode="backtest"),
        settings=practice_settings,
    )
    result = engine.run(frame)
    # Every signal should have been rejected because spread=5 > 1.5 pip cap.
    # Strategy fired on the uptrend → RiskEngine vetoed → zero trades, but
    # rejections present.
    assert result.metrics.trade_count == 0
    assert RiskRejectionCode.SPREAD_TOO_WIDE.value in result.rejection_counts
    assert result.rejection_counts[RiskRejectionCode.SPREAD_TOO_WIDE.value] > 0
    assert result.risk_engine_used is True


def test_backtest_without_risk_engine_still_works(eur_usd):
    """The legacy no-risk-engine code path is still available for parity
    comparisons; nothing in the new code should require risk_engine != None."""
    candles = []
    base = Decimal("1.0500")
    for i in range(300):
        m = base + Decimal("0.0002") * i
        bid_c = m - Decimal("0.0001")
        ask_c = m + Decimal("0.0001")
        prev = base + Decimal("0.0002") * (i - 1) if i > 0 else m
        bid_o = prev - Decimal("0.0001")
        ask_o = prev + Decimal("0.0001")
        candles.append(
            Candle(
                instrument="EUR_USD",
                granularity="H4",
                time=datetime(2025, 1, 1, tzinfo=UTC) + timedelta(hours=4 * i),
                complete=True,
                volume=1000,
                bid_o=bid_o, bid_h=bid_c, bid_l=bid_o, bid_c=bid_c,
                ask_o=ask_o, ask_h=ask_c, ask_l=ask_o, ask_c=ask_c,
            )
        )
    frame = CandleFrame.from_candles("EUR_USD", "H4", candles)
    engine = BacktestEngine(
        instrument=eur_usd,
        strategy=TrendFollowingStrategy(version="0.1.0-baseline-frozen"),
        strategy_config={
            "ema_fast": 20,
            "ema_slow": 60,
            "donchian_lookback": 10,
            "atr_lookback": 14,
            "atr_stop_multiple": 2.0,
            "max_bars_in_trade": 60,
            "timeframe": "H4",
        },
        fill_model=FillModel(
            fixed_slippage_pips=Decimal("0"),
            spread_slippage_multiplier=Decimal("0"),
        ),
        starting_equity=Decimal("500"),
        risk_engine=None,
    )
    result = engine.run(frame)
    assert result.risk_engine_used is False
    assert result.rejection_counts == {}

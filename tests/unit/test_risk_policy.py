"""Risk engine tests: kill switch, missing stop, wide spread, exposure caps,
session blackout, loss limits, sizing-to-zero, duplicate-instrument."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from forex_bot.config import load_settings
from forex_bot.domain.account import AccountSnapshot
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.domain.risk import RiskRejectionCode
from forex_bot.domain.signals import Signal
from forex_bot.risk.policy import RiskEngine, RiskInputs


@pytest.fixture
def settings_paper(paper_config_path, monkeypatch):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "x")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "y")
    return load_settings(paper_config_path)


@pytest.fixture
def settings_practice(practice_config_path, monkeypatch, tmp_path):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "x")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "y")
    text = practice_config_path.read_text(encoding="utf-8")
    # Redirect kill switch into tmp_path so we can poke it.
    text = text.replace("./KILL_SWITCH", str(tmp_path / "KILL_SWITCH"))
    custom = tmp_path / "practice.yaml"
    custom.write_text(text, encoding="utf-8")
    return load_settings(custom)


def _account(nav: Decimal = Decimal("500"), used: Decimal = Decimal("0")) -> AccountSnapshot:
    return AccountSnapshot(
        account_id="acc",
        currency="USD",
        balance=nav,
        nav=nav,
        margin_used=used,
        margin_available=nav,
        margin_closeout_percent=Decimal("0"),
        unrealized_pl=Decimal("0"),
        pl=Decimal("0"),
        open_trade_count=0,
        open_position_count=0,
        pending_order_count=0,
        time=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
    )


def _market_state(
    instrument: str,
    *,
    spread_pips: Decimal = Decimal("1.0"),
    tradeable: bool = True,
) -> MarketState:
    bid = Decimal("1.07990")
    ask = Decimal("1.07990") + spread_pips * Decimal("0.0001")
    quote = Quote(
        instrument=instrument,
        time=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
        bid=bid,
        ask=ask,
        tradeable=tradeable,
        status="tradeable" if tradeable else "non-tradeable",
    )
    return MarketState(
        quote=quote,
        spread_snapshot=SpreadSnapshot(
            instrument=instrument,
            time=quote.time,
            bid=bid,
            ask=ask,
            spread_pips=spread_pips,
        ),
    )


def _signal(side: str = "long", stop: Decimal = Decimal("1.07810")) -> Signal:
    return Signal(
        signal_id="sig-1",
        strategy_name="trend_following",
        strategy_version="0.1.0",
        instrument="EUR_USD",
        timeframe="H4",
        timestamp=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
        side=side,  # type: ignore[arg-type]
        entry_intent="market",
        stop_model="ATR14*2.5",
        stop_price=stop,
        exit_model="trailing",
        features={"atr_pips": 10.0},
        reason="test",
    )


def test_paper_mode_rejects_trading_disabled(settings_paper, eur_usd, quote_eur_usd):
    engine = RiskEngine(settings_paper)
    inputs = RiskInputs(
        signal=_signal(),
        instrument=eur_usd,
        account=_account(),
        market_state=_market_state("EUR_USD"),
        positions=[],
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
    )
    decision, plan = engine.evaluate(inputs)
    assert not decision.approved
    assert RiskRejectionCode.TRADING_DISABLED in decision.rejection_codes
    assert plan is None


def test_practice_approves_clean_long(settings_practice, eur_usd, quote_eur_usd):
    engine = RiskEngine(settings_practice)
    # signal is at noon UTC = 8am NY → outside default blackout windows
    inputs = RiskInputs(
        signal=_signal(),
        instrument=eur_usd,
        account=_account(),
        market_state=_market_state("EUR_USD"),
        positions=[],
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
    )
    decision, plan = engine.evaluate(inputs)
    assert decision.approved, decision.rejection_codes
    assert plan is not None
    assert plan.side == "buy"
    assert plan.stop_loss_price == _signal().stop_price


def test_practice_rejects_kill_switch(settings_practice, eur_usd, quote_eur_usd, tmp_path):
    Path(settings_practice.app.kill_switch_path).write_text("stop")
    engine = RiskEngine(settings_practice)
    inputs = RiskInputs(
        signal=_signal(),
        instrument=eur_usd,
        account=_account(),
        market_state=_market_state("EUR_USD"),
        positions=[],
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
    )
    decision, plan = engine.evaluate(inputs)
    assert not decision.approved
    assert RiskRejectionCode.KILL_SWITCH in decision.rejection_codes
    assert plan is None


def test_unreconciled_rejects(settings_practice, eur_usd, quote_eur_usd):
    engine = RiskEngine(settings_practice)
    inputs = RiskInputs(
        signal=_signal(),
        instrument=eur_usd,
        account=_account(),
        market_state=_market_state("EUR_USD"),
        positions=[],
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
        reconciled=False,
    )
    decision, plan = engine.evaluate(inputs)
    assert not decision.approved
    assert RiskRejectionCode.UNRECONCILED in decision.rejection_codes
    assert plan is None


def test_wide_spread_rejects(settings_practice, eur_usd, quote_eur_usd):
    engine = RiskEngine(settings_practice)
    inputs = RiskInputs(
        signal=_signal(),
        instrument=eur_usd,
        account=_account(),
        market_state=_market_state("EUR_USD", spread_pips=Decimal("3.0")),  # > 1.5 cap
        positions=[],
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
    )
    decision, plan = engine.evaluate(inputs)
    assert not decision.approved
    assert RiskRejectionCode.SPREAD_TOO_WIDE in decision.rejection_codes
    assert plan is None


def test_non_tradeable_rejects(settings_practice, eur_usd, quote_eur_usd):
    engine = RiskEngine(settings_practice)
    inputs = RiskInputs(
        signal=_signal(),
        instrument=eur_usd,
        account=_account(),
        market_state=_market_state("EUR_USD", tradeable=False),
        positions=[],
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
    )
    decision, plan = engine.evaluate(inputs)
    assert not decision.approved
    assert RiskRejectionCode.NOT_TRADEABLE in decision.rejection_codes


def test_existing_position_blocks(settings_practice, eur_usd, quote_eur_usd):
    engine = RiskEngine(settings_practice)
    inputs = RiskInputs(
        signal=_signal(),
        instrument=eur_usd,
        account=_account(),
        market_state=_market_state("EUR_USD"),
        positions=[Position(instrument="EUR_USD", long_units=Decimal("100"))],
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
    )
    decision, plan = engine.evaluate(inputs)
    assert not decision.approved
    assert RiskRejectionCode.MAX_PER_INSTRUMENT in decision.rejection_codes
    assert plan is None


def test_daily_loss_limit_blocks(settings_practice, eur_usd, quote_eur_usd):
    engine = RiskEngine(settings_practice)
    inputs = RiskInputs(
        signal=_signal(),
        instrument=eur_usd,
        account=_account(),
        market_state=_market_state("EUR_USD"),
        positions=[],
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
        realized_pl_today=Decimal("-50"),  # exceeds 1% of 500 NAV
    )
    decision, plan = engine.evaluate(inputs)
    assert not decision.approved
    assert RiskRejectionCode.DAILY_LOSS_LIMIT in decision.rejection_codes


def test_missing_stop_rejects(settings_practice, eur_usd, quote_eur_usd):
    """If size_position cannot produce units (zero stop), reject."""
    sig = _signal(stop=Decimal("1.07990") + Decimal("0.00010"))  # same as ask
    engine = RiskEngine(settings_practice)
    inputs = RiskInputs(
        signal=sig,
        instrument=eur_usd,
        account=_account(),
        market_state=_market_state("EUR_USD"),
        positions=[],
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
    )
    decision, plan = engine.evaluate(inputs)
    assert not decision.approved
    assert plan is None

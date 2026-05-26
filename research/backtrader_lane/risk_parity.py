"""Read-only RiskEngine parity for Backtrader CAMPAIGN_015 lane.

Evaluates the production ``RiskEngine`` at pending-entry fill time using
local candle bid/ask data only. No broker calls, no order submission, no
execution-loop imports.

``strategy_evidence: false``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

import pandas as pd

from forex_bot.domain.account import AccountSnapshot
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.risk import RiskRejectionCode
from forex_bot.domain.signals import Signal
from forex_bot.risk.policy import RiskEngine, RiskInputs

# CAMPAIGN_015 H4 universe — mirrors tests/conftest + campaign_002 constants.
_CAMPAIGN_015_INSTRUMENTS: dict[str, Instrument] = {
    "EUR_USD": Instrument(
        name="EUR_USD",
        type="CURRENCY",
        display_precision=5,
        pip_location=-4,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        margin_rate=Decimal("0.02"),
    ),
    "GBP_USD": Instrument(
        name="GBP_USD",
        type="CURRENCY",
        display_precision=5,
        pip_location=-4,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        margin_rate=Decimal("0.02"),
    ),
    "USD_JPY": Instrument(
        name="USD_JPY",
        type="CURRENCY",
        display_precision=3,
        pip_location=-2,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        margin_rate=Decimal("0.04"),
    ),
    "AUD_USD": Instrument(
        name="AUD_USD",
        type="CURRENCY",
        display_precision=5,
        pip_location=-4,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        margin_rate=Decimal("0.02"),
    ),
    "USD_CAD": Instrument(
        name="USD_CAD",
        type="CURRENCY",
        display_precision=5,
        pip_location=-4,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        margin_rate=Decimal("0.02"),
    ),
    "USD_CHF": Instrument(
        name="USD_CHF",
        type="CURRENCY",
        display_precision=5,
        pip_location=-4,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        margin_rate=Decimal("0.02"),
    ),
    "NZD_USD": Instrument(
        name="NZD_USD",
        type="CURRENCY",
        display_precision=5,
        pip_location=-4,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        margin_rate=Decimal("0.02"),
    ),
}

EntryBarStopPolicy = str  # backtrader_default | bespoke_current_no_entry_bar_stop

ENTRY_BAR_STOP_POLICIES = frozenset(
    {"backtrader_default", "bespoke_current_no_entry_bar_stop"}
)


@dataclass
class RiskParityState:
    """Tracks equity history for RiskEngine drawdown / loss windows."""

    account_currency: str
    realized_pnls: list[tuple[datetime, Decimal]] = field(default_factory=list)
    equity_peak: float = 0.0

    def record_exit(self, *, exit_time: datetime, pnl: float, equity: float) -> None:
        ts = exit_time if exit_time.tzinfo else exit_time.replace(tzinfo=UTC)
        self.realized_pnls.append((ts, Decimal(str(pnl))))
        self.equity_peak = max(self.equity_peak, equity)

    def drawdown_pct(self, equity: float) -> Decimal:
        peak = max(self.equity_peak, equity)
        if peak <= 0:
            return Decimal("0")
        dd = (peak - equity) / peak * 100
        return Decimal(str(round(dd, 4)))

    @staticmethod
    def _realized_windows(
        ts: datetime,
        realized: list[tuple[datetime, Decimal]],
    ) -> tuple[Decimal, Decimal]:
        if not realized:
            return Decimal("0"), Decimal("0")
        now = ts if ts.tzinfo else ts.replace(tzinfo=UTC)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = day_start - pd.Timedelta(days=day_start.weekday())
        today = sum(
            (pnl for t, pnl in realized if t >= day_start),
            start=Decimal("0"),
        )
        week = sum(
            (pnl for t, pnl in realized if t >= week_start),
            start=Decimal("0"),
        )
        return today, week


def instrument_for(name: str) -> Instrument:
    if name not in _CAMPAIGN_015_INSTRUMENTS:
        raise KeyError(f"{name!r} not in CAMPAIGN_015 RiskEngine parity universe")
    return _CAMPAIGN_015_INSTRUMENTS[name]


def build_campaign_015_risk_engine(settings: Any) -> RiskEngine:
    """Construct the same backtest-mode RiskEngine as ``run_campaign_015.py``."""

    return RiskEngine(settings, mode="backtest")


def _synthetic_account(*, ts: datetime, equity: float, currency: str) -> AccountSnapshot:
    eq = Decimal(str(equity))
    return AccountSnapshot(
        account_id="backtest",
        currency=currency,
        balance=eq,
        nav=eq,
        margin_used=Decimal("0"),
        margin_available=eq,
        margin_closeout_percent=Decimal("0"),
        unrealized_pl=Decimal("0"),
        pl=Decimal("0"),
        open_trade_count=0,
        open_position_count=0,
        pending_order_count=0,
        time=ts,
    )


def _market_state(
    *,
    instrument: str,
    ts: datetime,
    bid: Decimal,
    ask: Decimal,
    pip_size: Decimal,
) -> MarketState:
    spread_pips = (ask - bid) / pip_size
    quote = Quote(instrument=instrument, time=ts, bid=bid, ask=ask)
    return MarketState(
        quote=quote,
        spread_snapshot=SpreadSnapshot(
            instrument=instrument,
            time=ts,
            bid=bid,
            ask=ask,
            spread_pips=spread_pips,
        ),
    )


@dataclass(frozen=True)
class RiskParityResult:
    approved: bool
    rejection_codes: tuple[str, ...]
    rejection_messages: tuple[str, ...]
    units: int | None = None
    stop_price: Decimal | None = None


def evaluate_pending_entry(
    *,
    risk_engine: RiskEngine,
    instrument_name: str,
    side: str,
    stop_price: float,
    signal_time: datetime,
    fill_time: datetime,
    fill_bid: float,
    fill_ask: float,
    atr: float,
    equity: float,
    parity_state: RiskParityState,
    strategy_version: str,
) -> RiskParityResult:
    """Evaluate RiskEngine at next-bar-open fill time (read-only)."""

    instrument = instrument_for(instrument_name)
    pip_size = instrument.pip_size
    bid = Decimal(str(fill_bid))
    ask = Decimal(str(fill_ask))
    fill_market = _market_state(
        instrument=instrument_name,
        ts=fill_time,
        bid=bid,
        ask=ask,
        pip_size=pip_size,
    )
    fill_quote = fill_market.quote
    atr_pips = Decimal(str(round(atr / float(pip_size), 4))) if atr > 0 else None

    signal = Signal(
        signal_id=uuid4().hex,
        strategy_name="failed_breakout_reversal",
        strategy_version=strategy_version,
        instrument=instrument_name,
        timeframe="H4",
        timestamp=signal_time,
        side=side,  # type: ignore[arg-type]
        stop_model="atr_buffer",
        stop_price=Decimal(str(stop_price)),
        exit_model="hard_stop_or_time",
        features={"atr_pips": float(atr_pips) if atr_pips is not None else None},
    )

    realized_today, realized_week = parity_state._realized_windows(
        fill_time, parity_state.realized_pnls
    )
    inputs = RiskInputs(
        signal=signal,
        instrument=instrument,
        account=_synthetic_account(
            ts=fill_time,
            equity=equity,
            currency=parity_state.account_currency,
        ),
        market_state=fill_market,
        positions=[],
        quotes_by_instrument={instrument_name: fill_quote},
        realized_pl_today=realized_today,
        realized_pl_week=realized_week,
        drawdown_pct=parity_state.drawdown_pct(equity),
        atr_pips=atr_pips,
        reconciled=True,
    )
    decision, plan = risk_engine.evaluate(inputs)
    if not decision.approved or plan is None:
        return RiskParityResult(
            approved=False,
            rejection_codes=tuple(c.value for c in decision.rejection_codes),
            rejection_messages=tuple(decision.rejection_messages),
        )
    return RiskParityResult(
        approved=True,
        rejection_codes=(),
        rejection_messages=(),
        units=int(plan.units),
        stop_price=plan.stop_loss_price,
    )


def record_rejections(
    counts: dict[str, int],
    codes: tuple[str, ...],
) -> None:
    for code in codes:
        if code and code != RiskRejectionCode.OK.value:
            counts[code] = counts.get(code, 0) + 1

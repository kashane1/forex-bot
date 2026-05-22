"""Risk engine. The *only* component allowed to approve an OrderPlan."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from forex_bot.clock import utcnow
from forex_bot.config import RiskConfig, SessionFilterConfig, Settings, SpreadFilterConfig
from forex_bot.domain.account import AccountSnapshot
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote
from forex_bot.domain.orders import OrderPlan
from forex_bot.domain.positions import Position
from forex_bot.domain.risk import RiskDecision, RiskRejectionCode
from forex_bot.domain.signals import Signal
from forex_bot.risk.exposure import currency_exposure, has_open_position
from forex_bot.risk.kill_switch import KillSwitch
from forex_bot.risk.sizing import size_position

RiskMode = Literal["live", "backtest"]


@dataclass
class RiskInputs:
    signal: Signal
    instrument: Instrument
    account: AccountSnapshot
    market_state: MarketState
    positions: list[Position]
    quotes_by_instrument: dict[str, Quote]
    realized_pl_today: Decimal = Decimal("0")
    realized_pl_week: Decimal = Decimal("0")
    drawdown_pct: Decimal = Decimal("0")
    atr_pips: Decimal | None = None
    reconciled: bool = True


@dataclass
class _DecisionDraft:
    rejection_codes: list[RiskRejectionCode] = field(default_factory=list)
    rejection_messages: list[str] = field(default_factory=list)

    def reject(self, code: RiskRejectionCode, message: str) -> None:
        self.rejection_codes.append(code)
        self.rejection_messages.append(message)

    @property
    def approved(self) -> bool:
        return not self.rejection_codes


class RiskEngine:
    """Stateless evaluator. The caller persists every decision.

    `mode="live"` runs every gate including operational ones (trading_enabled,
    kill switch, reconciliation, pending order count). `mode="backtest"`
    skips those because they don't apply in a historical replay — but every
    *strategy/risk* gate (stop loss, spread, session blackout, sizing,
    exposure, margin) still runs identically.
    """

    def __init__(self, settings: Settings, *, mode: RiskMode = "live") -> None:
        self.settings = settings
        self.mode: RiskMode = mode
        self.config_hash = settings.config_hash
        self.risk: RiskConfig = settings.risk
        self.spread_filter: SpreadFilterConfig = settings.spread_filter
        self.session_filter: SessionFilterConfig = settings.session_filter
        self.kill_switch = KillSwitch(
            path=Path(settings.app.kill_switch_path),
            trading_enabled=settings.app.trading_enabled,
        )

    def evaluate(self, inputs: RiskInputs) -> tuple[RiskDecision, OrderPlan | None]:
        draft = _DecisionDraft()
        signal = inputs.signal

        if signal.side == "flat":
            draft.reject(RiskRejectionCode.INVALID_SIGNAL, "side=flat is not an entry")
        if signal.stop_price is None:
            draft.reject(RiskRejectionCode.MISSING_STOP_LOSS, "signal has no stop_price")

        # Operational gates — skipped in backtest mode because they don't apply
        # in a historical replay.
        if self.mode == "live":
            if not inputs.reconciled:
                draft.reject(
                    RiskRejectionCode.UNRECONCILED, "ledger not reconciled with broker"
                )
            if self.kill_switch.is_active():
                draft.reject(RiskRejectionCode.KILL_SWITCH, self.kill_switch.reason())
            if not self.settings.app.trading_enabled:
                draft.reject(RiskRejectionCode.TRADING_DISABLED, "trading_enabled=false")

        # Market sanity
        quote = inputs.market_state.quote
        spread_pips: Decimal | None = inputs.market_state.spread_snapshot.spread_pips
        if not quote.tradeable:
            draft.reject(RiskRejectionCode.NOT_TRADEABLE, f"status={quote.status}")
        if quote.bid <= 0 or quote.ask <= 0:
            draft.reject(RiskRejectionCode.STALE_PRICE, "missing bid/ask")

        instrument = inputs.instrument
        if instrument is None:
            draft.reject(RiskRejectionCode.MISSING_INSTRUMENT_METADATA, "no metadata")

        max_per_inst = self.spread_filter.max_spread_pips.get(signal.instrument)
        if self.spread_filter.enabled:
            if max_per_inst is None:
                draft.reject(
                    RiskRejectionCode.SPREAD_TOO_WIDE,
                    f"no spread cap configured for {signal.instrument}",
                )
            elif spread_pips is not None and spread_pips > Decimal(str(max_per_inst)):
                draft.reject(
                    RiskRejectionCode.SPREAD_TOO_WIDE,
                    f"spread {spread_pips} > cap {max_per_inst} pips",
                )
            if inputs.atr_pips is not None and inputs.atr_pips > 0 and spread_pips is not None:
                ratio_pct = (spread_pips / inputs.atr_pips) * Decimal("100")
                if ratio_pct > Decimal(str(self.spread_filter.max_spread_to_atr_pct)):
                    draft.reject(
                        RiskRejectionCode.SPREAD_TO_ATR,
                        f"spread/atr {ratio_pct:.2f}% > {self.spread_filter.max_spread_to_atr_pct}%",
                    )

        # Session filter
        if self.session_filter.enabled and self._in_blocked_session(signal.timestamp):
            draft.reject(RiskRejectionCode.SESSION_BLOCKED, "inside blocked session window")

        # Loss limits
        nav = inputs.account.nav
        daily_limit = nav * Decimal(str(self.risk.max_daily_loss_pct)) / Decimal("100")
        weekly_limit = nav * Decimal(str(self.risk.max_weekly_loss_pct)) / Decimal("100")
        if -inputs.realized_pl_today >= daily_limit:
            draft.reject(
                RiskRejectionCode.DAILY_LOSS_LIMIT,
                f"daily loss {-inputs.realized_pl_today} >= limit {daily_limit}",
            )
        if -inputs.realized_pl_week >= weekly_limit:
            draft.reject(
                RiskRejectionCode.WEEKLY_LOSS_LIMIT,
                f"weekly loss {-inputs.realized_pl_week} >= limit {weekly_limit}",
            )
        if inputs.drawdown_pct >= Decimal(str(self.risk.max_total_drawdown_pct)):
            draft.reject(
                RiskRejectionCode.DRAWDOWN_LIMIT,
                f"drawdown {inputs.drawdown_pct}% >= cap {self.risk.max_total_drawdown_pct}%",
            )

        # Exposure
        open_positions = [p for p in inputs.positions if not p.is_flat]
        if len(open_positions) >= self.risk.max_open_positions:
            draft.reject(
                RiskRejectionCode.MAX_OPEN_POSITIONS,
                f"open={len(open_positions)} cap={self.risk.max_open_positions}",
            )
        if has_open_position(inputs.positions, signal.instrument):
            draft.reject(
                RiskRejectionCode.MAX_PER_INSTRUMENT,
                f"already open in {signal.instrument}",
            )

        exposure = currency_exposure(open_positions)
        signal_base, signal_quote = signal.instrument.split("_", 1)
        if exposure.get(signal_base, Decimal("0")) != 0 or exposure.get(signal_quote, Decimal("0")) != 0:
            draft.reject(
                RiskRejectionCode.CORRELATED_EXPOSURE,
                f"existing exposure on {signal_base} or {signal_quote}",
            )

        if self.mode == "live":
            if inputs.account.pending_order_count >= self.risk.max_pending_orders:
                draft.reject(
                    RiskRejectionCode.MAX_PENDING_ORDERS,
                    f"pending={inputs.account.pending_order_count} "
                    f"cap={self.risk.max_pending_orders}",
                )

        # Margin closeout floor
        if inputs.account.margin_closeout_percent >= Decimal(
            str(self.settings.margin.reject_if_margin_closeout_percent_above)
        ):
            draft.reject(
                RiskRejectionCode.MARGIN_BUFFER,
                f"margin closeout {inputs.account.margin_closeout_percent}%",
            )

        # Sizing
        entry_price = (
            inputs.market_state.quote.ask
            if signal.side == "long"
            else inputs.market_state.quote.bid
        )
        sizing = None
        if instrument is not None and signal.stop_price is not None and signal.side != "flat":
            sizing = size_position(
                instrument=instrument,
                account_currency=inputs.account.currency,
                nav_home=nav,
                risk_per_trade_pct=Decimal(str(self.risk.risk_per_trade_pct)),
                entry_price=entry_price,
                stop_price=signal.stop_price,
                quotes_by_instrument=inputs.quotes_by_instrument,
            )
        if sizing is None:
            draft.reject(RiskRejectionCode.PIP_VALUE_UNAVAILABLE, "could not size position")
        else:
            if sizing.units <= 0:
                draft.reject(
                    RiskRejectionCode.UNITS_ROUNDED_TO_ZERO,
                    f"raw_units={sizing.raw_units} rounded to {sizing.units}",
                )
            if instrument is not None and sizing.units < instrument.minimum_trade_size:
                draft.reject(
                    RiskRejectionCode.MIN_TRADE_SIZE,
                    f"units={sizing.units} < min={instrument.minimum_trade_size}",
                )
            margin_used_after = inputs.account.margin_used + sizing.estimated_margin_home
            max_margin_used = (
                nav
                * Decimal(str(self.settings.margin.max_margin_used_pct_of_nav))
                / Decimal("100")
            )
            if margin_used_after > max_margin_used:
                draft.reject(
                    RiskRejectionCode.MARGIN_BUFFER,
                    f"margin {margin_used_after} > cap {max_margin_used}",
                )

        decision = RiskDecision(
            signal_id=signal.signal_id,
            decided_at=utcnow(),
            approved=draft.approved,
            rejection_codes=list(draft.rejection_codes),
            rejection_messages=list(draft.rejection_messages),
            account_nav=nav,
            instrument_metadata_version=inputs.market_state.instrument_metadata_version,
            spread_pips=spread_pips,
            stop_distance_pips=sizing.stop_distance_pips if sizing else None,
            raw_units=sizing.raw_units if sizing else None,
            units=sizing.units if sizing else None,
            estimated_risk=sizing.risk_amount_home if sizing else None,
            estimated_margin=sizing.estimated_margin_home if sizing else None,
            config_hash=self.config_hash,
            extras={
                "entry_price": str(entry_price),
                "side": signal.side,
                "instrument": signal.instrument,
                "strategy": f"{signal.strategy_name}:{signal.strategy_version}",
            },
        )

        if not decision.approved or sizing is None:
            return decision, None

        client_id = _client_order_id(signal, self.config_hash)
        plan = OrderPlan(
            plan_id=uuid.uuid4().hex,
            signal_id=signal.signal_id,
            strategy_name=signal.strategy_name,
            strategy_version=signal.strategy_version,
            instrument=signal.instrument,
            side="buy" if signal.side == "long" else "sell",
            order_type="MARKET",
            units=sizing.units,
            requested_price=entry_price,
            stop_loss_price=signal.stop_price,
            take_profit_price=signal.take_profit_price,
            client_order_id=client_id,
            config_hash=self.config_hash,
            created_at=utcnow(),
            extras={
                "raw_units": str(sizing.raw_units),
                "pip_value_per_unit_home": str(sizing.pip_value_per_unit_home),
                "risk_pct": str(self.risk.risk_per_trade_pct),
            },
        )
        return decision, plan

    # ------------------------------------------------------------------ session

    def _in_blocked_session(self, ts: datetime) -> bool:
        tz = ZoneInfo(self.session_filter.timezone)
        local = ts.astimezone(tz)
        for window in self.session_filter.block_new_trades:
            if window.day and local.strftime("%A") != window.day:
                continue
            start_h, start_m = (int(x) for x in window.start.split(":"))
            end_h, end_m = (int(x) for x in window.end.split(":"))
            start_dt = local.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
            end_dt = local.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
            if end_dt < start_dt:
                end_dt += timedelta(days=1)
            if start_dt <= local <= end_dt:
                return True
        return False


def _client_order_id(signal: Signal, config_hash: str) -> str:
    """Deterministic so that retrying the same signal can't double-book.

    Spec: bucket the timestamp so a re-run within the same H4 bar produces
    the same ID. Bucket is `date_hour//4`.
    """
    bucket = signal.timestamp.strftime("%Y%m%dT%H")
    raw = f"{signal.strategy_name}:{signal.strategy_version}:{signal.signal_id}:{bucket}:{config_hash[:8]}"
    digest = hashlib.sha1(raw.encode()).hexdigest()[:24]
    return f"fbot-{digest}"


def loss_window_bounds(now: datetime, tz_name: str) -> tuple[datetime, datetime, datetime]:
    """Return (start_of_day, start_of_week, now) all in tz_name."""
    tz = ZoneInfo(tz_name)
    local = now.astimezone(tz)
    sod_local = local.replace(hour=0, minute=0, second=0, microsecond=0)
    weekday = local.weekday()  # Monday=0
    sow_local = sod_local - timedelta(days=weekday)
    return sod_local, sow_local, local


__all__ = ["RiskEngine", "RiskInputs", "loss_window_bounds"]

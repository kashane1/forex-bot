"""Executor. The *only* code allowed to call broker.submit_order().

Safety properties enforced here:
  - The executor refuses to act unless the OrderPlan has a stop_loss_price
    AND the settings demand server-side protection.
  - The executor checks the local ledger and broker for the same
    client_order_id before submission to avoid duplicate orders after a
    retry / restart.
  - Unknown-status responses block further trading until reconciliation.
  - Live submission is gated by config; the OANDA adapter also refuses
    on its own to call live as defense-in-depth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from forex_bot.broker.base import Broker
from forex_bot.broker.errors import (
    BrokerOrderRejectError,
    BrokerUnknownStatusError,
)
from forex_bot.broker.mapping import map_broker_order
from forex_bot.config import ConfigError, Settings
from forex_bot.data.repositories import (
    AccountSnapshotRepo,
    BrokerOrderRepo,
    OrderPlanRepo,
    SystemEventRepo,
    TransactionRepo,
)
from forex_bot.domain.orders import BrokerOrderResult, OrderPlan
from forex_bot.execution.reconciliation import Reconciler


@dataclass
class ExecutionResult:
    submitted: bool
    result: BrokerOrderResult | None
    reason: str
    trading_blocked: bool = False


class Executor:
    def __init__(
        self,
        settings: Settings,
        broker: Broker,
        plans: OrderPlanRepo,
        orders: BrokerOrderRepo,
        transactions: TransactionRepo,
        snapshots: AccountSnapshotRepo,
        events: SystemEventRepo,
        reconciler: Reconciler,
    ) -> None:
        self.settings = settings
        self.broker = broker
        self.plans = plans
        self.orders = orders
        self.transactions = transactions
        self.snapshots = snapshots
        self.events = events
        self.reconciler = reconciler
        self.trading_blocked = False

    def submit(self, plan: OrderPlan) -> ExecutionResult:
        if self.trading_blocked:
            return ExecutionResult(False, None, "trading_blocked_flag", trading_blocked=True)

        app = self.settings.app
        if not (app.trading_enabled and app.allow_order_submission):
            return ExecutionResult(
                False,
                None,
                "config disallows order submission (paper mode or guards off)",
            )

        if (
            self.settings.broker.environment == "live"
            and not (
                app.mode == "live"
                and app.allow_live_trading
                and app.live_acknowledgement
                and app.live_acknowledgement == app.required_live_acknowledgement
            )
        ):
            raise ConfigError("Executor refused live submission: live gates not all green")

        if self.settings.risk.require_stop_loss and plan.stop_loss_price is None:
            return ExecutionResult(False, None, "plan missing stop_loss_price")

        existing = self.plans.get_by_client_id(plan.client_order_id)
        if existing is not None and existing.plan_id != plan.plan_id:
            return ExecutionResult(
                False,
                None,
                f"duplicate client_order_id={plan.client_order_id}; needs reconciliation",
                trading_blocked=True,
            )

        # Refuse if broker already has an order with this client_order_id.
        try:
            broker_open = self.broker.list_open_orders()
        except Exception as exc:
            self._record_event("broker_open_orders_fetch_failed", "warn", str(exc))
            return ExecutionResult(
                False, None, f"broker open-orders fetch failed: {exc}", trading_blocked=True
            )
        if any(o.client_order_id == plan.client_order_id for o in broker_open):
            self._record_event(
                "duplicate_open_order", "warn", f"client_id={plan.client_order_id}"
            )
            self.trading_blocked = True
            return ExecutionResult(
                False,
                None,
                "broker already has open order with this client id",
                trading_blocked=True,
            )

        try:
            result = self.broker.submit_order(plan)
        except BrokerUnknownStatusError as exc:
            self.trading_blocked = True
            self._record_event("unknown_status_after_submit", "error", str(exc))
            return ExecutionResult(
                False, None, f"unknown status after submit: {exc}", trading_blocked=True
            )
        except BrokerOrderRejectError as exc:
            result = BrokerOrderResult(
                status="REJECTED",
                client_order_id=plan.client_order_id,
                error_message=str(exc),
                error_code=exc.code,
                raw={},
            )

        self.orders.insert_result(plan.plan_id, result)
        self._maybe_store_broker_order(plan, result)

        if result.status == "FILLED":
            if self._needs_unprotected_block(plan, result):
                self.trading_blocked = True
                self._record_event(
                    "unprotected_fill_detected",
                    "error",
                    f"plan={plan.plan_id} client_id={plan.client_order_id}",
                    extras=result.model_dump(),
                )

        if result.status in {"UNKNOWN", "REJECTED"}:
            report = self.reconciler.run()
            if not report.clean:
                self.trading_blocked = True

        if result.status == "FILLED":
            self.reconciler.run()

        return ExecutionResult(
            submitted=result.status in {"FILLED", "PENDING", "CANCELLED", "REJECTED"},
            result=result,
            reason=result.status,
            trading_blocked=self.trading_blocked,
        )

    def _needs_unprotected_block(self, plan: OrderPlan, result: BrokerOrderResult) -> bool:
        if not self.settings.risk.require_server_side_protection:
            return False
        raw = result.raw or {}
        order_create = raw.get("orderCreateTransaction") or {}
        return "stopLossOnFill" not in order_create

    def _maybe_store_broker_order(self, plan: OrderPlan, result: BrokerOrderResult) -> None:
        raw = result.raw or {}
        order_create = raw.get("orderCreateTransaction")
        if not order_create:
            return
        broker_order = map_broker_order(
            {
                **order_create,
                "clientExtensions": {"id": plan.client_order_id},
            }
        )
        self.orders.upsert(broker_order, plan_id=plan.plan_id)

    def _record_event(
        self, kind: str, level: str, message: str, extras: dict[str, Any] | None = None
    ) -> None:
        self.events.record(kind, level, message, extras)

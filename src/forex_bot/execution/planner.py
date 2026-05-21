"""Pipeline from signal → risk decision → (maybe) order plan, persisted."""

from __future__ import annotations

from dataclasses import dataclass

from forex_bot.data.repositories import (
    OrderPlanRepo,
    RiskDecisionRepo,
    SignalRepo,
)
from forex_bot.domain.orders import OrderPlan
from forex_bot.domain.risk import RiskDecision
from forex_bot.risk.policy import RiskEngine, RiskInputs


@dataclass
class Planner:
    risk: RiskEngine
    signals: SignalRepo
    decisions: RiskDecisionRepo
    plans: OrderPlanRepo

    def plan(self, inputs: RiskInputs) -> tuple[RiskDecision, OrderPlan | None]:
        self.signals.insert(inputs.signal)
        decision, plan = self.risk.evaluate(inputs)
        self.decisions.insert(decision)
        if plan is not None:
            self.plans.insert(plan)
        return decision, plan

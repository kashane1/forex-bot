"""Risk layer. Strategies emit signals; the risk engine emits the only
type of object the executor is allowed to act on (an OrderPlan)."""

from forex_bot.risk.exposure import currency_exposure, has_open_position
from forex_bot.risk.kill_switch import KillSwitch
from forex_bot.risk.policy import RiskEngine, RiskInputs
from forex_bot.risk.sizing import SizingResult, compute_pip_value_home, size_position

__all__ = [
    "KillSwitch",
    "RiskEngine",
    "RiskInputs",
    "SizingResult",
    "compute_pip_value_home",
    "currency_exposure",
    "has_open_position",
    "size_position",
]

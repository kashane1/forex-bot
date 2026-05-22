"""Operational guards used by CLI commands.

These are *defense in depth* on top of the config-layer gates. The intent
is to refuse risky operations when the inputs are even slightly ambiguous,
so a human can investigate before any data is fetched / order is sent.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from forex_bot.config import ConfigError, Settings


@dataclass(frozen=True)
class EnvironmentGuardResult:
    is_practice: bool
    declared_environment: str
    account_id_env_var: str
    account_id_redacted: str


def assert_practice_data_environment(settings: Settings) -> EnvironmentGuardResult:
    """Refuse historical-data fetches if the environment is anything but
    *unambiguously* a practice account.

    Checks (must all pass):
      * `broker.environment == "practice"` in config.
      * `OANDA_ENVIRONMENT` env var, when set, equals `"practice"`.
      * `broker.account_id_env` name contains `PRACTICE` (configured side).
      * The resolved account id does not look like a placeholder.
      * No `*_LIVE` env vars are set that share the value of the practice
        token (defense against accidental token reuse).
    """
    if settings.broker.environment != "practice":
        raise ConfigError(
            f"environment guard: broker.environment must be 'practice' for "
            f"historical fetches, got '{settings.broker.environment}'"
        )

    declared = os.environ.get("OANDA_ENVIRONMENT", "").strip().lower()
    if declared and declared != "practice":
        raise ConfigError(
            f"environment guard: OANDA_ENVIRONMENT='{declared}' contradicts "
            f"broker.environment='practice'. Refusing to fetch."
        )

    account_env = settings.broker.account_id_env
    token_env = settings.broker.token_env
    if "PRACTICE" not in account_env or "PRACTICE" not in token_env:
        raise ConfigError(
            f"environment guard: broker.account_id_env='{account_env}' / "
            f"token_env='{token_env}' must contain 'PRACTICE'."
        )

    account_id, token = settings.broker_credentials()

    live_account = os.environ.get("OANDA_ACCOUNT_ID_LIVE", "").strip()
    if live_account and live_account == account_id:
        raise ConfigError(
            "environment guard: OANDA_ACCOUNT_ID_LIVE is set to the same "
            "account id as OANDA_ACCOUNT_ID_PRACTICE. Refusing to proceed."
        )
    live_token = os.environ.get("OANDA_ACCESS_TOKEN_LIVE", "").strip()
    if live_token and live_token == token:
        raise ConfigError(
            "environment guard: live and practice tokens are identical. "
            "Refusing to proceed."
        )

    redacted = (
        account_id[:7] + "…" + account_id[-4:] if len(account_id) > 12 else "<short>"
    )
    return EnvironmentGuardResult(
        is_practice=True,
        declared_environment=declared or "practice",
        account_id_env_var=account_env,
        account_id_redacted=redacted,
    )


# ---------------------------------------------------------------------------
# Approved-strategy registry — the research-freeze safety guard.
# ---------------------------------------------------------------------------

# The registry lives at a fixed path in the repo. Research Marathon 001
# closed NO-GO, so it ships EMPTY: no strategy may run in a paper, demo,
# or live loop. Backtesting is research and is NEVER gated by this guard —
# only signal-emitting / order-capable loops are.
APPROVED_STRATEGIES_PATH = (
    Path(__file__).resolve().parents[2] / "configs" / "approved_strategies.yaml"
)


class StrategyNotApprovedError(ConfigError):
    """Raised when a paper / demo / live loop is asked to run a strategy
    absent from the approved-strategy registry."""


def load_approved_strategies(registry_path: Path | None = None) -> set[str]:
    """Return the set of strategy names approved for live-loop execution.

    The research-freeze default is an empty set: no strategy is approved.
    A missing or empty registry file is treated as empty — the guard
    fails closed.
    """
    path = registry_path or APPROVED_STRATEGIES_PATH
    if not path.exists():
        return set()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise StrategyNotApprovedError(
            f"approved-strategy registry {path} is not valid YAML: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise StrategyNotApprovedError(
            f"approved-strategy registry {path} must be a YAML mapping"
        )
    approved = data.get("approved") or []
    if not isinstance(approved, list):
        raise StrategyNotApprovedError(
            f"approved-strategy registry {path}: 'approved' must be a list"
        )
    return {str(s) for s in approved}


def assert_loop_strategies_approved(
    loop_mode: str,
    enabled_strategies: list[str],
    *,
    registry_path: Path | None = None,
) -> None:
    """Refuse a paper / demo / live loop unless *every* enabled strategy
    is in the approved-strategy registry.

    This is the research-freeze safety guard. Backtesting is research and
    is never gated; only signal-emitting / order-capable loops are. With
    the registry empty (the NO-GO default) every loop is refused. Live
    mode is additionally blocked by the existing config-layer live gates.
    """
    registry = registry_path or APPROVED_STRATEGIES_PATH
    approved = load_approved_strategies(registry)
    unapproved = sorted(s for s in enabled_strategies if s not in approved)
    if unapproved:
        raise StrategyNotApprovedError(
            f"{loop_mode}-loop refused: strategy/strategies {unapproved} "
            f"are not in the approved-strategy registry ('{registry.name}'). "
            f"As of the research freeze (Research Marathon 001 closed "
            f"NO-GO) NO strategy is approved for paper, demo, or live "
            f"trading. See docs/research/FINAL_RESEARCH_DECISION_MEMO.md "
            f"and docs/research/STRATEGY_STATUS.md. Approving a strategy "
            f"requires a human to add it to the registry — a deliberate, "
            f"reviewed action, never a default."
        )

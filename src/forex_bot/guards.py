"""Operational guards used by CLI commands.

These are *defense in depth* on top of the config-layer gates. The intent
is to refuse risky operations when the inputs are even slightly ambiguous,
so a human can investigate before any data is fetched / order is sent.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

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

"""Safety tests for config loading.

These tests prove that the spec-required live-mode refusals fire BEFORE
any broker code runs.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from forex_bot.config import ConfigError, load_settings


def write(tmp_path: Path, yaml_body: str, name: str = "cfg.yaml") -> Path:
    path = tmp_path / name
    path.write_text(textwrap.dedent(yaml_body), encoding="utf-8")
    return path


def base_paper_yaml() -> str:
    return """\
    app:
      name: bot
      mode: paper
      trading_enabled: false
      allow_order_submission: false
      allow_live_trading: false
      database_path: ./data/x.sqlite3
      log_path: ./logs/x.jsonl
      kill_switch_path: ./KILL_SWITCH
    broker:
      name: oanda
      environment: practice
      account_id_env: OANDA_ACCOUNT_ID_PRACTICE
      token_env: OANDA_ACCESS_TOKEN_PRACTICE
    market:
      account_currency: USD
      instruments: [EUR_USD]
      granularity: H4
    strategy:
      enabled: [trend_following]
      trend_following:
        version: 0.1.0
    risk:
      starting_equity_usd: 500
      risk_per_trade_pct: 0.25
      max_risk_per_trade_pct: 0.5
      max_daily_loss_pct: 1
      max_weekly_loss_pct: 2
      max_total_drawdown_pct: 8
      max_open_positions: 1
      max_pending_orders: 1
      max_correlated_positions: 1
      require_stop_loss: true
      require_server_side_protection: true
      allow_martingale: false
      allow_grid: false
      allow_averaging_down: false
    spread_filter:
      enabled: true
      max_spread_pips:
        EUR_USD: 1.5
    """


def test_paper_config_loads(tmp_path: Path) -> None:
    path = write(tmp_path, base_paper_yaml())
    settings = load_settings(path)
    assert settings.app.mode == "paper"
    assert settings.config_hash


def test_committed_paper_config_loads(paper_config_path: Path) -> None:
    settings = load_settings(paper_config_path)
    assert settings.app.mode == "paper"
    assert settings.app.allow_order_submission is False
    assert settings.app.allow_live_trading is False


def test_committed_practice_config_loads(practice_config_path: Path) -> None:
    settings = load_settings(practice_config_path)
    assert settings.app.mode == "practice"
    assert settings.app.allow_live_trading is False


def test_live_example_config_refuses(live_example_config_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_settings(live_example_config_path)


def test_paper_with_order_submission_refused(tmp_path: Path) -> None:
    yaml = base_paper_yaml().replace(
        "allow_order_submission: false", "allow_order_submission: true"
    )
    with pytest.raises(ConfigError):
        load_settings(write(tmp_path, yaml))


def test_require_stop_loss_false_refused(tmp_path: Path) -> None:
    yaml = base_paper_yaml().replace("require_stop_loss: true", "require_stop_loss: false")
    with pytest.raises(ConfigError):
        load_settings(write(tmp_path, yaml))


def test_allow_martingale_refused(tmp_path: Path) -> None:
    yaml = base_paper_yaml().replace("allow_martingale: false", "allow_martingale: true")
    with pytest.raises(ConfigError):
        load_settings(write(tmp_path, yaml))


def test_allow_grid_refused(tmp_path: Path) -> None:
    yaml = base_paper_yaml().replace("allow_grid: false", "allow_grid: true")
    with pytest.raises(ConfigError):
        load_settings(write(tmp_path, yaml))


def test_allow_averaging_down_refused(tmp_path: Path) -> None:
    yaml = base_paper_yaml().replace(
        "allow_averaging_down: false", "allow_averaging_down: true"
    )
    with pytest.raises(ConfigError):
        load_settings(write(tmp_path, yaml))


def test_risk_per_trade_above_max_refused(tmp_path: Path) -> None:
    yaml = base_paper_yaml().replace("risk_per_trade_pct: 0.25", "risk_per_trade_pct: 1.0")
    with pytest.raises(ConfigError):
        load_settings(write(tmp_path, yaml))


def test_empty_instruments_refused(tmp_path: Path) -> None:
    yaml = base_paper_yaml().replace("instruments: [EUR_USD]", "instruments: []")
    with pytest.raises(ConfigError):
        load_settings(write(tmp_path, yaml))


def test_missing_spread_filter_for_instrument_refused(tmp_path: Path) -> None:
    yaml = base_paper_yaml().replace("EUR_USD: 1.5", "USD_JPY: 2.0")
    with pytest.raises(ConfigError):
        load_settings(write(tmp_path, yaml))


def test_live_mode_requires_all_gates(tmp_path: Path) -> None:
    yaml = base_paper_yaml()
    yaml = yaml.replace("mode: paper", "mode: live")
    yaml = yaml.replace("environment: practice", "environment: live")
    yaml = yaml.replace(
        "account_id_env: OANDA_ACCOUNT_ID_PRACTICE",
        "account_id_env: OANDA_ACCOUNT_ID_LIVE",
    )
    yaml = yaml.replace(
        "token_env: OANDA_ACCESS_TOKEN_PRACTICE",
        "token_env: OANDA_ACCESS_TOKEN_LIVE",
    )
    with pytest.raises(ConfigError):
        load_settings(write(tmp_path, yaml))


def test_live_mode_with_wrong_acknowledgement_refused(tmp_path: Path) -> None:
    yaml = textwrap.dedent(
        """\
        app:
          name: bot
          mode: live
          trading_enabled: true
          allow_order_submission: true
          allow_live_trading: true
          live_acknowledgement: NOT_THE_RIGHT_PHRASE
          required_live_acknowledgement: I_ACCEPT_THE_RISK
          approved_config_hash: deadbeef
          database_path: ./data/x.sqlite3
          log_path: ./logs/x.jsonl
          kill_switch_path: ./KILL_SWITCH
        broker:
          name: oanda
          environment: live
          account_id_env: OANDA_ACCOUNT_ID_LIVE
          token_env: OANDA_ACCESS_TOKEN_LIVE
        market:
          account_currency: USD
          instruments: [EUR_USD]
          granularity: H4
        strategy:
          enabled: [trend_following]
          trend_following:
            version: 0.1.0
        risk:
          starting_equity_usd: 500
          risk_per_trade_pct: 0.25
          max_risk_per_trade_pct: 0.5
          max_daily_loss_pct: 1
          max_weekly_loss_pct: 2
          max_total_drawdown_pct: 8
          max_open_positions: 1
          max_pending_orders: 1
          max_correlated_positions: 1
          require_stop_loss: true
          require_server_side_protection: true
          allow_martingale: false
          allow_grid: false
          allow_averaging_down: false
        spread_filter:
          enabled: true
          max_spread_pips:
            EUR_USD: 1.5
        """
    )
    with pytest.raises(ConfigError, match="live_acknowledgement"):
        load_settings(write(tmp_path, yaml))


def test_live_env_with_practice_var_refused(tmp_path: Path) -> None:
    """broker.environment=live cannot use *_PRACTICE env vars."""
    yaml = base_paper_yaml()
    yaml = yaml.replace("mode: paper", "mode: live")
    yaml = yaml.replace("environment: practice", "environment: live")
    with pytest.raises(ConfigError):
        load_settings(write(tmp_path, yaml))


def test_practice_environment_refuses_live_env_vars(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """practice broker must use *_PRACTICE env var names."""
    yaml = base_paper_yaml().replace(
        "account_id_env: OANDA_ACCOUNT_ID_PRACTICE",
        "account_id_env: OANDA_ACCOUNT_ID_LIVE",
    )
    monkeypatch.setenv("OANDA_ACCOUNT_ID_LIVE", "x")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "y")
    settings = load_settings(write(tmp_path, yaml))
    with pytest.raises(ConfigError):
        settings.broker_credentials()


def test_debug_sensitive_refused(tmp_path: Path) -> None:
    yaml = base_paper_yaml()
    yaml = yaml.replace(
        "app:",
        "app:\n  debug_sensitive: true",
    )
    with pytest.raises(ConfigError, match="debug_sensitive"):
        load_settings(write(tmp_path, yaml))


def test_missing_env_vars_at_credential_lookup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("OANDA_ACCOUNT_ID_PRACTICE", raising=False)
    monkeypatch.delenv("OANDA_ACCESS_TOKEN_PRACTICE", raising=False)
    settings = load_settings(write(tmp_path, base_paper_yaml()))
    with pytest.raises(ConfigError):
        settings.broker_credentials()

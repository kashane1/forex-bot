"""Configuration models and loader.

All safety gates are enforced here. Loading a config that would allow
live trading without every required flag, env var, and acknowledgement
phrase being present causes an immediate ConfigError before any broker
or strategy code runs.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Annotated, Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ConfigError(ValueError):
    """Raised when a config cannot be loaded or violates a safety rule."""


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    mode: Literal["paper", "practice", "live"]
    trading_enabled: bool = False
    allow_order_submission: bool = False
    allow_live_trading: bool = False
    live_acknowledgement: str | None = None
    required_live_acknowledgement: str | None = None
    approved_config_hash: str | None = None
    database_path: str
    log_path: str
    kill_switch_path: str
    debug_sensitive: bool = False

    @field_validator("debug_sensitive")
    @classmethod
    def _refuse_debug_sensitive(cls, value: bool) -> bool:
        if value:
            raise ConfigError(
                "debug_sensitive must never be true in a committed config. "
                "Override only via a local, gitignored file you control."
            )
        return value


class BrokerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Literal["oanda"]
    environment: Literal["practice", "live"]
    account_id_env: str
    token_env: str
    request_timeout_seconds: float = 10.0
    max_retries: int = 3


class MarketConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_currency: str
    instruments: list[str]
    granularity: Literal["M1", "M5", "M15", "M30", "H1", "H4", "D"]
    candle_price_components: Literal["B", "A", "M", "BA", "BM", "AM", "BAM"] = "BA"
    daily_alignment: int = 17
    alignment_timezone: str = "America/New_York"
    weekly_alignment: Literal[
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ] = "Friday"

    @field_validator("instruments")
    @classmethod
    def _require_instruments(cls, value: list[str]) -> list[str]:
        if not value:
            raise ConfigError("market.instruments must not be empty")
        for instrument in value:
            if "_" not in instrument:
                raise ConfigError(
                    f"instrument '{instrument}' must be in OANDA BASE_QUOTE form (e.g., EUR_USD)"
                )
        return value


class TrendFollowingStrategyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    ema_fast: int = 50
    ema_slow: int = 200
    donchian_lookback: int = 20
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.5
    trailing_stop_atr_multiple: float | None = None
    min_atr_pips: dict[str, float] = Field(default_factory=dict)
    max_bars_in_trade: int = 80
    # Optional ADX trend-strength gate. None → disabled (frozen baseline
    # behavior). Set (e.g. 25.0) → entry requires ADX-adx_lookback above it.
    adx_lookback: int = 14
    adx_min: float | None = None

    @model_validator(mode="after")
    def _check_lookbacks(self) -> TrendFollowingStrategyConfig:
        if self.ema_fast >= self.ema_slow:
            raise ConfigError("ema_fast must be < ema_slow")
        if self.donchian_lookback < 5:
            raise ConfigError("donchian_lookback must be >= 5")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        if self.adx_lookback < 2:
            raise ConfigError("adx_lookback must be >= 2")
        if self.adx_min is not None and not (0 < self.adx_min < 100):
            raise ConfigError("adx_min must be between 0 and 100 when set")
        return self


class VolatilityBreakoutStrategyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    atr_lookback: int = 14
    breakout_lookback: int = 20
    compression_lookback: int = 60
    compression_percentile: float = 40.0
    atr_stop_multiple: float = 2.0
    trailing_stop_atr_multiple: float | None = 2.0
    max_bars_in_trade: int = 120
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> VolatilityBreakoutStrategyConfig:
        if self.atr_lookback < 2:
            raise ConfigError("atr_lookback must be >= 2")
        if self.breakout_lookback < 5:
            raise ConfigError("breakout_lookback must be >= 5")
        if self.compression_lookback < 20:
            raise ConfigError(
                "compression_lookback must be >= 20 for a stable percentile"
            )
        if not (0 < self.compression_percentile < 100):
            raise ConfigError("compression_percentile must be between 0 and 100")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        return self


class PullbackContinuationStrategyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    ema_fast: int = 50
    ema_slow: int = 200
    atr_lookback: int = 14
    pullback_lookback: int = 6
    pullback_band: float = 0.5
    atr_stop_multiple: float = 2.0
    trailing_stop_atr_multiple: float | None = 2.0
    max_bars_in_trade: int = 120
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> PullbackContinuationStrategyConfig:
        if self.ema_fast >= self.ema_slow:
            raise ConfigError("ema_fast must be < ema_slow")
        if self.pullback_lookback < 2:
            raise ConfigError("pullback_lookback must be >= 2")
        if self.pullback_band <= 0:
            raise ConfigError("pullback_band must be > 0")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        return self


class MeanReversionStrategyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    atr_lookback: int = 14
    zscore_lookback: int = 20
    zscore_long_threshold: float = -2.0
    zscore_short_threshold: float = 2.0
    rsi_lookback: int = 14
    regime_ema: int = 200
    adx_lookback: int = 14
    adx_max: float = 20.0
    atr_stop_multiple: float = 1.5
    trailing_stop_atr_multiple: float | None = None
    max_bars_in_trade: int = 40
    # Opt-in midline-target exit (CAMPAIGN_009). False → behaviour is
    # identical to CAMPAIGN_008 (mean_reversion 0.1.0-c008).
    midline_exit: bool = False
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> MeanReversionStrategyConfig:
        if self.zscore_long_threshold >= 0 or self.zscore_short_threshold <= 0:
            raise ConfigError(
                "zscore_long_threshold must be < 0 and short threshold > 0"
            )
        if not (0 < self.adx_max < 100):
            raise ConfigError("adx_max must be between 0 and 100")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        return self


class StrategyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: list[str]
    trend_following: TrendFollowingStrategyConfig | None = None
    volatility_breakout: VolatilityBreakoutStrategyConfig | None = None
    pullback_continuation: PullbackContinuationStrategyConfig | None = None
    mean_reversion: MeanReversionStrategyConfig | None = None

    @model_validator(mode="after")
    def _check_enabled(self) -> StrategyConfig:
        if not self.enabled:
            raise ConfigError("strategy.enabled must list at least one strategy")
        if "trend_following" in self.enabled and self.trend_following is None:
            raise ConfigError("strategy.trend_following config required when enabled")
        if (
            "volatility_breakout" in self.enabled
            and self.volatility_breakout is None
        ):
            raise ConfigError(
                "strategy.volatility_breakout config required when enabled"
            )
        if (
            "pullback_continuation" in self.enabled
            and self.pullback_continuation is None
        ):
            raise ConfigError(
                "strategy.pullback_continuation config required when enabled"
            )
        if "mean_reversion" in self.enabled and self.mean_reversion is None:
            raise ConfigError(
                "strategy.mean_reversion config required when enabled"
            )
        return self


class RiskConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    starting_equity_usd: float
    risk_per_trade_pct: float
    max_risk_per_trade_pct: float
    max_daily_loss_pct: float
    max_weekly_loss_pct: float
    max_total_drawdown_pct: float
    max_open_positions: int
    max_pending_orders: int
    max_correlated_positions: int
    max_positions_per_instrument: int = 1
    require_stop_loss: bool
    require_server_side_protection: bool
    allow_martingale: bool
    allow_grid: bool
    allow_averaging_down: bool
    auto_flatten_on_loss_limit: bool = False

    @model_validator(mode="after")
    def _check_bounds(self) -> RiskConfig:
        if self.risk_per_trade_pct > self.max_risk_per_trade_pct:
            raise ConfigError("risk_per_trade_pct must be <= max_risk_per_trade_pct")
        if self.risk_per_trade_pct <= 0:
            raise ConfigError("risk_per_trade_pct must be > 0")
        if not self.require_stop_loss:
            raise ConfigError("require_stop_loss must be true (hard prohibition)")
        if self.allow_martingale:
            raise ConfigError("allow_martingale must be false (hard prohibition)")
        if self.allow_grid:
            raise ConfigError("allow_grid must be false (hard prohibition)")
        if self.allow_averaging_down:
            raise ConfigError("allow_averaging_down must be false (hard prohibition)")
        if self.max_open_positions < 0:
            raise ConfigError("max_open_positions must be >= 0")
        return self


class MarginConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_margin_available_pct_of_nav: float = 80.0
    max_margin_used_pct_of_nav: float = 10.0
    reject_if_margin_closeout_percent_above: float = 20.0


class SpreadFilterConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    max_spread_to_atr_pct: float = 10.0
    max_spread_pips: dict[str, float] = Field(default_factory=dict)


class SessionWindow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    start: str
    end: str
    day: (
        Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        | None
    ) = None


class SessionFilterConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    timezone: str = "America/New_York"
    block_new_trades: list[SessionWindow] = Field(default_factory=list)


class BacktestConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fixed_slippage_pips: float = 0.3
    spread_slippage_multiplier: float = 0.5
    starting_equity_usd: float = 500.0
    commission_per_unit: float = 0.0
    # When a backtest entry fills. Defaults to signal_bar_close so prior
    # campaign configs (which omit this key) reproduce their exact prior
    # behaviour. next_bar_open is strictly opt-in. See
    # docs/research/FILL_TIMING_MODEL.md.
    fill_timing: Literal["signal_bar_close", "next_bar_open"] = "signal_bar_close"
    # How exit fills handle a bar that OPENED past the stop / TP level.
    # Defaults to "none" so prior campaign configs (which omit this key)
    # reproduce their exact prior config_hash. "gap_through" is strictly
    # opt-in and produces a distinct config_hash. See
    # docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md.
    gap_fill_policy: Literal["none", "gap_through"] = "none"


class KillSwitchConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    block_new_orders: bool = True
    cancel_pending_orders: bool = True
    flatten_positions: bool = False


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: AppConfig
    broker: BrokerConfig
    market: MarketConfig
    strategy: StrategyConfig
    risk: RiskConfig
    margin: MarginConfig = Field(default_factory=MarginConfig)
    spread_filter: SpreadFilterConfig = Field(default_factory=SpreadFilterConfig)
    session_filter: SessionFilterConfig = Field(default_factory=SessionFilterConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    kill_switch: KillSwitchConfig = Field(default_factory=KillSwitchConfig)

    config_hash: Annotated[str, Field(default="")] = ""
    config_source_path: Annotated[str | None, Field(default=None)] = None

    # ---- cross-section validation --------------------------------------

    @model_validator(mode="after")
    def _validate_combinations(self) -> Settings:
        app = self.app
        broker = self.broker

        if app.allow_order_submission and not app.trading_enabled:
            raise ConfigError(
                "allow_order_submission=true requires trading_enabled=true"
            )

        if app.mode == "paper":
            if app.allow_order_submission:
                raise ConfigError("paper mode forbids allow_order_submission=true")
            if app.trading_enabled:
                raise ConfigError("paper mode forbids trading_enabled=true")

        if app.mode == "practice":
            if broker.environment != "practice":
                raise ConfigError(
                    "practice mode requires broker.environment=practice"
                )

        if broker.environment == "live":
            if app.mode != "live":
                raise ConfigError(
                    "broker.environment=live requires app.mode=live"
                )
            if "PRACTICE" in broker.account_id_env or "PRACTICE" in broker.token_env:
                raise ConfigError(
                    "broker.environment=live cannot use *_PRACTICE env vars"
                )

        if app.mode == "live" or broker.environment == "live":
            # Live gates: must all be explicitly enabled.
            if not (
                app.trading_enabled
                and app.allow_order_submission
                and app.allow_live_trading
            ):
                raise ConfigError(
                    "live mode requires trading_enabled, allow_order_submission, "
                    "and allow_live_trading to all be true"
                )
            if (
                not app.required_live_acknowledgement
                or not app.live_acknowledgement
                or app.live_acknowledgement != app.required_live_acknowledgement
            ):
                raise ConfigError(
                    "live mode requires live_acknowledgement to exactly match "
                    "required_live_acknowledgement"
                )
            if (
                not app.approved_config_hash
                or app.approved_config_hash == "replace_with_manual_approval_hash"
            ):
                raise ConfigError(
                    "live mode requires approved_config_hash to be set to the "
                    "manually reviewed config hash"
                )
            if app.approved_config_hash != self.config_hash:
                raise ConfigError(
                    "live mode requires approved_config_hash to equal the "
                    "computed config hash"
                )

        for instrument in self.market.instruments:
            if (
                self.spread_filter.enabled
                and instrument not in self.spread_filter.max_spread_pips
            ):
                raise ConfigError(
                    f"spread_filter.max_spread_pips missing entry for {instrument}"
                )

        kill_path = Path(self.app.kill_switch_path)
        if str(kill_path) in {".", ""}:
            raise ConfigError("app.kill_switch_path must be a real file path")

        return self

    # ---- broker credential lookup --------------------------------------

    def broker_credentials(self) -> tuple[str, str]:
        """Look up (account_id, access_token) from env. Refuse mismatched env."""
        account_env = self.broker.account_id_env
        token_env = self.broker.token_env

        if self.broker.environment == "practice":
            if "PRACTICE" not in account_env or "PRACTICE" not in token_env:
                raise ConfigError(
                    "practice broker must use *_PRACTICE env var names"
                )
        if self.broker.environment == "live":
            if "PRACTICE" in account_env or "PRACTICE" in token_env:
                raise ConfigError(
                    "live broker must not use *_PRACTICE env var names"
                )

        account_id = os.environ.get(account_env, "").strip()
        token = os.environ.get(token_env, "").strip()
        if not account_id or account_id.startswith("replace_me"):
            raise ConfigError(f"env var {account_env} is missing or unset")
        if not token or token.startswith("replace_me"):
            raise ConfigError(f"env var {token_env} is missing or unset")
        return account_id, token


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def compute_config_hash(raw_text: str) -> str:
    """Stable hash of the raw config file text (after stripping trailing ws)."""
    canonical = "\n".join(line.rstrip() for line in raw_text.splitlines()).strip() + "\n"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_settings(path: str | Path, *, env: dict[str, str] | None = None) -> Settings:
    """Load a config file. Env vars from `env` override os.environ for tests."""
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"config file not found: {config_path}")
    raw_text = config_path.read_text(encoding="utf-8")
    config_hash = compute_config_hash(raw_text)

    if env is not None:
        for key, value in env.items():
            os.environ[key] = value

    try:
        data: dict[str, Any] = yaml.safe_load(raw_text) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {config_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"config root must be a mapping, got {type(data).__name__}")

    data.setdefault("config_hash", config_hash)
    data.setdefault("config_source_path", str(config_path))

    try:
        settings = Settings.model_validate(data)
    except ConfigError:
        raise
    except Exception as exc:  # pydantic ValidationError, etc.
        raise ConfigError(str(exc)) from exc
    return settings

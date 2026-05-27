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


class ProtectiveStopConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    favorable_excursion_r_threshold: float = 1.0
    stop_after_transition: Literal["entry_price"] = "entry_price"
    ratchet: bool = False

    @model_validator(mode="after")
    def _check(self) -> ProtectiveStopConfig:
        if not self.enabled:
            raise ConfigError("protective_stop.enabled must be true for c018")
        if self.favorable_excursion_r_threshold != 1.0:
            raise ConfigError(
                "protective_stop.favorable_excursion_r_threshold must be 1.0 "
                "(precommitted — no tuning)"
            )
        if self.stop_after_transition != "entry_price":
            raise ConfigError("protective_stop.stop_after_transition must be entry_price")
        if self.ratchet:
            raise ConfigError("protective_stop.ratchet must be false in v0.1.0-c018")
        return self


class MeanReversionProtectiveStopStrategyConfig(MeanReversionStrategyConfig):
    """CAMPAIGN_018 — C008-identical entries + protective stop (engine)."""

    midline_exit: bool = False
    protective_stop: ProtectiveStopConfig = Field(default_factory=ProtectiveStopConfig)

    @model_validator(mode="after")
    def _check_c018(self) -> MeanReversionProtectiveStopStrategyConfig:
        if self.midline_exit:
            raise ConfigError("midline_exit must be false for mean_reversion_protective_stop")
        return self


class ThesisInvalidationConfig(BaseModel):
    """CAMPAIGN_019 thesis-invalidation exit — precommitted fixed thresholds."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    zscore_lookback: int = 20
    long_exit_zscore: float = -3.0
    short_exit_zscore: float = 3.0

    @model_validator(mode="after")
    def _check_c019(self) -> ThesisInvalidationConfig:
        if not self.enabled:
            raise ConfigError("thesis_invalidation.enabled must be true for c019")
        if self.zscore_lookback != 20:
            raise ConfigError(
                "thesis_invalidation.zscore_lookback must be 20 (precommitted — matches entry)"
            )
        if self.long_exit_zscore != -3.0:
            raise ConfigError(
                "thesis_invalidation.long_exit_zscore must be -3.0 (precommitted — no tuning)"
            )
        if self.short_exit_zscore != 3.0:
            raise ConfigError(
                "thesis_invalidation.short_exit_zscore must be 3.0 (precommitted — no tuning)"
            )
        return self


class MeanReversionThesisInvalidationStrategyConfig(MeanReversionStrategyConfig):
    """CAMPAIGN_019 — C008-identical entries + thesis invalidation (engine)."""

    midline_exit: bool = False
    thesis_invalidation: ThesisInvalidationConfig = Field(default_factory=ThesisInvalidationConfig)

    @model_validator(mode="after")
    def _check_c019(self) -> MeanReversionThesisInvalidationStrategyConfig:
        if self.midline_exit:
            raise ConfigError("midline_exit must be false for mean_reversion_thesis_invalidation")
        return self


class SessionBreakoutStrategyConfig(BaseModel):
    # CAMPAIGN_010 research candidate (`session_breakout 0.1.0-c010`).
    # CANDIDATE SCAFFOLD ONLY — not approved for paper/demo/live.
    # See docs/research/ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md.
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.0
    trailing_stop_atr_multiple: float | None = None
    max_bars_in_trade: int = 6
    min_atr_pips: dict[str, float] = Field(default_factory=dict)
    asian_session_hours_utc_start: int = 22
    asian_session_hours_utc_end: int = 6
    london_session_hours_utc_start: int = 6
    london_session_hours_utc_end: int = 12
    min_asian_range_atr_fraction: float = 0.30

    @model_validator(mode="after")
    def _check(self) -> SessionBreakoutStrategyConfig:
        if self.atr_lookback < 2:
            raise ConfigError("atr_lookback must be >= 2")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        if self.max_bars_in_trade < 1:
            raise ConfigError("max_bars_in_trade must be >= 1")
        if self.min_asian_range_atr_fraction <= 0:
            raise ConfigError("min_asian_range_atr_fraction must be > 0")
        for name in (
            "asian_session_hours_utc_start",
            "asian_session_hours_utc_end",
            "london_session_hours_utc_start",
            "london_session_hours_utc_end",
        ):
            value = getattr(self, name)
            if not (0 <= value <= 24):
                raise ConfigError(f"{name} must be in [0, 24]")
        if self.asian_session_hours_utc_start == self.asian_session_hours_utc_end:
            raise ConfigError(
                "asian_session_hours_utc_start must differ from asian_session_hours_utc_end"
            )
        if self.london_session_hours_utc_start >= self.london_session_hours_utc_end:
            raise ConfigError(
                "london_session_hours_utc_start must be < london_session_hours_utc_end "
                "(London window does not wrap midnight in v1)"
            )
        return self


class RandomEntryAnchorStrategyConfig(BaseModel):
    # CAMPAIGN_011 research candidate (`random_entry_anchor 0.1.0-c011`).
    # CANDIDATE SCAFFOLD ONLY — NULL MODEL by design; cannot be approved,
    # cannot be deployed, cannot be used for paper/demo/live.
    # See docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md.
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    master_seed: int = 20260523
    entry_probability_per_bar: float = 0.05
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.0
    trailing_stop_atr_multiple: float | None = None
    max_bars_in_trade: int = 6
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> RandomEntryAnchorStrategyConfig:
        if self.atr_lookback < 2:
            raise ConfigError("atr_lookback must be >= 2")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        if self.max_bars_in_trade < 1:
            raise ConfigError("max_bars_in_trade must be >= 1")
        if not (0.0 < self.entry_probability_per_bar < 1.0):
            raise ConfigError(
                "entry_probability_per_bar must be in (0, 1) (exclusive)"
            )
        if self.trailing_stop_atr_multiple is not None:
            raise ConfigError(
                "trailing_stop_atr_multiple must be None in v1 — "
                "the null model uses time-stop only"
            )
        return self


class RegimeSwitcherAtrPercentileStrategyConfig(BaseModel):
    # CAMPAIGN_012 research candidate (`regime_switcher_atr_percentile 0.1.0-c012`).
    # CANDIDATE SCAFFOLD ONLY — not approved for paper/demo/live.
    # See docs/research/REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md.
    #
    # Frozen parameters pre-committed by the discovery-003 sprint
    # (see docs/research/C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md §2).
    # Any deviation constitutes a NEW candidate; the validator rejects
    # several specific deviations explicitly (e.g. trailing-stop in v1).
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    # H4 ATR for stop sizing (mirrors session_breakout / random_entry_anchor
    # naming; the design doc calls this `atr_lookback_h4` for descriptive
    # clarity but the value and intent are identical).
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.0
    trailing_stop_atr_multiple: float | None = None
    max_bars_in_trade: int = 6
    min_atr_pips: dict[str, float] = Field(default_factory=dict)
    # D1AGG ATR (the regime feature input).
    daily_atr_lookback: int = 14
    regime_lookback_days: int = 60
    regime_percentile_threshold: float = 0.70
    min_close_move_atr_fraction: float = 0.25
    trend_lookback_h4_bars: int = 4

    @model_validator(mode="after")
    def _check(self) -> RegimeSwitcherAtrPercentileStrategyConfig:
        if self.atr_lookback < 2:
            raise ConfigError("atr_lookback must be >= 2")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        if self.max_bars_in_trade < 1:
            raise ConfigError("max_bars_in_trade must be >= 1")
        if self.daily_atr_lookback < 2:
            raise ConfigError("daily_atr_lookback must be >= 2")
        if self.regime_lookback_days < 10:
            raise ConfigError(
                "regime_lookback_days must be >= 10 for a stable percentile"
            )
        if not (0.0 < self.regime_percentile_threshold < 1.0):
            raise ConfigError(
                "regime_percentile_threshold must be in (0, 1) (exclusive)"
            )
        if self.min_close_move_atr_fraction <= 0:
            raise ConfigError("min_close_move_atr_fraction must be > 0")
        if self.trend_lookback_h4_bars < 1:
            raise ConfigError("trend_lookback_h4_bars must be >= 1")
        if self.trailing_stop_atr_multiple is not None:
            raise ConfigError(
                "trailing_stop_atr_multiple must be None in v1 — "
                "the regime switcher uses time-stop only"
            )
        return self


class CrossPairCurrencyStrengthRotationStrategyConfig(BaseModel):
    # CAMPAIGN_013 research candidate (`cross_pair_currency_strength_rotation 0.1.0-c013`).
    # CANDIDATE SCAFFOLD ONLY — not approved for paper/demo/live.
    # See docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md.
    #
    # Frozen parameters pre-committed by the discovery-004 sprint
    # (see docs/research/NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md §5).
    # Any deviation constitutes a NEW candidate; the validator rejects
    # several specific deviations explicitly (e.g. trailing-stop in v1;
    # rank_gap_threshold outside [1, 7]).
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    # Rolling-window n-bar log-return window for the currency-strength
    # computation. 24 H4 bars ~= 4 trading days.
    currency_strength_lookback_bars: int = 24
    # Minimum |rank(quote) - rank(base)| to fire a signal. The 8-currency
    # rank spectrum runs 1..8; rank_gap_threshold = 4 is the half-spectrum
    # (top half vs bottom half). Must be in [1, 7].
    rank_gap_threshold: int = 4
    # H4 ATR for stop sizing (mirrors session_breakout / random_entry_anchor /
    # regime_switcher_atr_percentile convention).
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.0
    trailing_stop_atr_multiple: float | None = None
    max_bars_in_trade: int = 6
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> CrossPairCurrencyStrengthRotationStrategyConfig:
        if self.currency_strength_lookback_bars < 2:
            raise ConfigError("currency_strength_lookback_bars must be >= 2")
        if self.rank_gap_threshold < 1 or self.rank_gap_threshold > 7:
            raise ConfigError("rank_gap_threshold must be in [1, 7]")
        if self.atr_lookback < 2:
            raise ConfigError("atr_lookback must be >= 2")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        if self.max_bars_in_trade < 1:
            raise ConfigError("max_bars_in_trade must be >= 1")
        if self.trailing_stop_atr_multiple is not None:
            raise ConfigError(
                "trailing_stop_atr_multiple must be None in v1 — "
                "the cross-pair rotator uses time-stop only"
            )
        return self


class CalendarEventWindowAnomalyStrategyConfig(BaseModel):
    # CAMPAIGN_014 research candidate (`calendar_event_window_anomaly 0.1.0-c014`).
    # CANDIDATE SCAFFOLD ONLY — not approved for paper/demo/live.
    # See docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md.
    #
    # Frozen parameters pre-committed by the discovery-005 sprint
    # (see docs/research/NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md §7).
    # Any deviation constitutes a NEW candidate; the validator rejects
    # several specific deviations explicitly (e.g. trailing-stop in v1;
    # impact_ordering must be a permutation of event_set).
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    # Path to the committed event-calendar fixture (broker-free, local).
    event_calendar_path: str = "research/calendar/fixtures/campaign_014_events.json"
    # Binding event-class set (mirrors implementation spec §8). Must be a
    # subset of {NFP, FOMC, ECB, BoJ, BoE}; no expansion mid-sprint.
    event_set: list[str] = Field(
        default_factory=lambda: ["NFP", "FOMC", "ECB", "BoJ", "BoE"]
    )
    # Overlap precedence (high → low) for R4 resolution. Must be a
    # permutation of event_set.
    impact_ordering: list[str] = Field(
        default_factory=lambda: ["FOMC", "NFP", "ECB", "BoJ", "BoE"]
    )
    # Post-event signal window length, in completed H4 bars after the
    # event bar. = max_post_event_bars by design.
    post_event_window_bars: int = 6
    # H4 ATR for stop sizing (mirrors session_breakout /
    # random_entry_anchor / regime_switcher_atr_percentile /
    # cross_pair_currency_strength_rotation convention).
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.0
    trailing_stop_atr_multiple: float | None = None
    max_post_event_bars: int = 6
    re_entry_block_bars: int = 3
    event_warmup_bars: int = 1
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> CalendarEventWindowAnomalyStrategyConfig:
        allowed_classes = {"NFP", "FOMC", "ECB", "BoJ", "BoE"}
        bad_events = [c for c in self.event_set if c not in allowed_classes]
        if bad_events:
            raise ConfigError(
                f"event_set contains unsupported classes {bad_events!r}; "
                f"allowed: {sorted(allowed_classes)}"
            )
        if not self.event_set:
            raise ConfigError("event_set must contain at least one event class")
        if set(self.impact_ordering) != set(self.event_set):
            raise ConfigError(
                "impact_ordering must be a permutation of event_set "
                f"(event_set={sorted(self.event_set)}, "
                f"impact_ordering={sorted(self.impact_ordering)})"
            )
        if len(self.impact_ordering) != len(set(self.impact_ordering)):
            raise ConfigError("impact_ordering must not contain duplicates")
        if self.post_event_window_bars < 1:
            raise ConfigError("post_event_window_bars must be >= 1")
        if self.post_event_window_bars > 30:
            raise ConfigError(
                "post_event_window_bars must be <= 30 "
                "(standing guardrails §4 time-stop range)"
            )
        if self.atr_lookback < 2:
            raise ConfigError("atr_lookback must be >= 2")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        if self.max_post_event_bars < 1:
            raise ConfigError("max_post_event_bars must be >= 1")
        if self.max_post_event_bars > 30:
            raise ConfigError(
                "max_post_event_bars must be <= 30 "
                "(standing guardrails §4 time-stop range)"
            )
        if self.re_entry_block_bars < 0:
            raise ConfigError("re_entry_block_bars must be >= 0")
        if self.event_warmup_bars < 0:
            raise ConfigError("event_warmup_bars must be >= 0")
        if self.trailing_stop_atr_multiple is not None:
            raise ConfigError(
                "trailing_stop_atr_multiple must be None in v1 — "
                "the calendar-event-window anomaly uses time-stop only"
            )
        return self


class WeeklyCrossSectionalMomentumLowTurnoverStrategyConfig(BaseModel):
    # CAMPAIGN_016 research candidate.
    # CANDIDATE SCAFFOLD ONLY — not approved for paper/demo/live.
    # See docs/research/CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_PRECOMMIT.md.
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    momentum_lookback_fast_weeks: int = 4
    momentum_lookback_slow_weeks: int = 12
    momentum_blend_fast: float = 0.5
    momentum_blend_slow: float = 0.5
    volatility_lookback_weeks: int = 12
    volatility_floor: float = 1.0e-8
    max_same_currency_exposure: int = 1
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.5
    max_bars_in_trade: int = 42
    take_profit_r: float | None = None
    trailing_stop_atr_multiple: float | None = None
    entry_timing: Literal["next_bar_open", "signal_bar_close"] = "next_bar_open"
    same_bar_adverse_stop_wins: bool = True
    spread_to_atr_max: float = 0.15
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> WeeklyCrossSectionalMomentumLowTurnoverStrategyConfig:
        if self.momentum_lookback_fast_weeks < 1:
            raise ConfigError("momentum_lookback_fast_weeks must be >= 1")
        if self.momentum_lookback_slow_weeks <= self.momentum_lookback_fast_weeks:
            raise ConfigError(
                "momentum_lookback_slow_weeks must be > momentum_lookback_fast_weeks"
            )
        if not (0 < self.momentum_blend_fast < 1):
            raise ConfigError("momentum_blend_fast must be in (0, 1)")
        if not (0 < self.momentum_blend_slow < 1):
            raise ConfigError("momentum_blend_slow must be in (0, 1)")
        if abs(self.momentum_blend_fast + self.momentum_blend_slow - 1.0) > 1e-9:
            raise ConfigError("momentum_blend_fast + momentum_blend_slow must equal 1")
        if self.volatility_lookback_weeks < 2:
            raise ConfigError("volatility_lookback_weeks must be >= 2")
        if self.volatility_floor <= 0:
            raise ConfigError("volatility_floor must be > 0")
        if self.max_same_currency_exposure < 1:
            raise ConfigError("max_same_currency_exposure must be >= 1")
        if self.atr_lookback < 2:
            raise ConfigError("atr_lookback must be >= 2")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        if self.max_bars_in_trade < 1 or self.max_bars_in_trade > 60:
            raise ConfigError("max_bars_in_trade must be in [1, 60]")
        if self.take_profit_r is not None:
            raise ConfigError("take_profit_r must be None in v1")
        if self.trailing_stop_atr_multiple is not None:
            raise ConfigError("trailing_stop_atr_multiple must be None in v1")
        if not self.same_bar_adverse_stop_wins:
            raise ConfigError("same_bar_adverse_stop_wins must be True in v1")
        if self.spread_to_atr_max <= 0:
            raise ConfigError("spread_to_atr_max must be > 0")
        return self


class WeeklyVolatilityContractionBreakoutStrategyConfig(BaseModel):
    # CAMPAIGN_017 research candidate.
    # CANDIDATE SCAFFOLD ONLY — not approved for paper/demo/live.
    # See docs/research/CAMPAIGN_017_WEEKLY_VOLATILITY_CONTRACTION_BREAKOUT_PRECOMMIT.md.
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    compression_lookback_weeks: int = 12
    compression_percentile_threshold: float = 25.0
    breakout_buffer_atr_multiple: float = 0.25
    atr_lookback_h4: int = 14
    max_bars_in_trade: int = 42
    take_profit_r: float | None = None
    trailing_stop_atr_multiple: float | None = None
    entry_timing: Literal["next_bar_open", "signal_bar_close"] = "next_bar_open"
    same_bar_adverse_stop_wins: bool = True
    spread_to_atr_max: float = 0.15
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> WeeklyVolatilityContractionBreakoutStrategyConfig:
        if self.compression_lookback_weeks < 2:
            raise ConfigError("compression_lookback_weeks must be >= 2")
        if not (0 < self.compression_percentile_threshold < 100):
            raise ConfigError(
                "compression_percentile_threshold must be in (0, 100)"
            )
        if self.breakout_buffer_atr_multiple <= 0:
            raise ConfigError("breakout_buffer_atr_multiple must be > 0")
        if self.atr_lookback_h4 < 2:
            raise ConfigError("atr_lookback_h4 must be >= 2")
        if self.max_bars_in_trade < 1 or self.max_bars_in_trade > 60:
            raise ConfigError("max_bars_in_trade must be in [1, 60]")
        if self.take_profit_r is not None:
            raise ConfigError("take_profit_r must be None in v1")
        if self.trailing_stop_atr_multiple is not None:
            raise ConfigError("trailing_stop_atr_multiple must be None in v1")
        if not self.same_bar_adverse_stop_wins:
            raise ConfigError("same_bar_adverse_stop_wins must be True in v1")
        if self.spread_to_atr_max <= 0:
            raise ConfigError("spread_to_atr_max must be > 0")
        return self


class FailedBreakoutReversalStrategyConfig(BaseModel):
    # CAMPAIGN_015 research candidate (`failed_breakout_reversal 0.1.0-c015`).
    # CANDIDATE SCAFFOLD ONLY — not approved for paper/demo/live.
    # See docs/research/CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md.
    #
    # Frozen parameters pre-committed by the campaign-015 sprint (Phase 0
    # pre-commit doc, §5). Any deviation constitutes a NEW candidate; the
    # validator rejects several deviations explicitly (e.g. trailing-stop
    # or take-profit in v1; min_stop_atr_multiple >= max_stop_atr_multiple).
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    range_lookback: int = 20
    atr_lookback: int = 14
    adx_lookback: int = 14
    adx_max: float = 20.0
    sweep_buffer_atr: float = 0.10
    min_range_atr_multiple: float = 1.25
    max_range_atr_multiple: float = 5.00
    stop_buffer_atr: float = 0.10
    min_stop_atr_multiple: float = 0.80
    max_stop_atr_multiple: float = 2.20
    max_bars_in_trade: int = 12
    take_profit_r: float | None = None
    trailing_stop_atr_multiple: float | None = None
    entry_timing: Literal["next_bar_open", "signal_bar_close"] = "next_bar_open"
    same_bar_adverse_stop_wins: bool = True
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> FailedBreakoutReversalStrategyConfig:
        if self.range_lookback < 5:
            raise ConfigError("range_lookback must be >= 5")
        if self.atr_lookback < 2:
            raise ConfigError("atr_lookback must be >= 2")
        if self.adx_lookback < 2:
            raise ConfigError("adx_lookback must be >= 2")
        if not (0 < self.adx_max < 100):
            raise ConfigError("adx_max must be between 0 and 100")
        if self.sweep_buffer_atr < 0:
            raise ConfigError("sweep_buffer_atr must be >= 0")
        if self.min_range_atr_multiple <= 0:
            raise ConfigError("min_range_atr_multiple must be > 0")
        if self.max_range_atr_multiple <= self.min_range_atr_multiple:
            raise ConfigError(
                "max_range_atr_multiple must be > min_range_atr_multiple"
            )
        if self.stop_buffer_atr < 0:
            raise ConfigError("stop_buffer_atr must be >= 0")
        if self.min_stop_atr_multiple <= 0:
            raise ConfigError("min_stop_atr_multiple must be > 0")
        if self.max_stop_atr_multiple <= self.min_stop_atr_multiple:
            raise ConfigError(
                "max_stop_atr_multiple must be > min_stop_atr_multiple"
            )
        if self.max_bars_in_trade < 1:
            raise ConfigError("max_bars_in_trade must be >= 1")
        if self.max_bars_in_trade > 60:
            raise ConfigError(
                "max_bars_in_trade must be <= 60 "
                "(standing guardrails on time-stop range)"
            )
        if self.take_profit_r is not None:
            raise ConfigError(
                "take_profit_r must be None in v1 — the failed-breakout "
                "reversal uses time-stop + hard-stop only"
            )
        if self.trailing_stop_atr_multiple is not None:
            raise ConfigError(
                "trailing_stop_atr_multiple must be None in v1 — the "
                "failed-breakout reversal uses time-stop + hard-stop only"
            )
        if not self.same_bar_adverse_stop_wins:
            raise ConfigError(
                "same_bar_adverse_stop_wins must be True in v1 — binding "
                "ambiguity rule from the pre-commit doc"
            )
        return self


class LowerTimeframeMtfConfluenceEntryStrategyConfig(BaseModel):
    # CAMPAIGN_021 research candidate (`lower_timeframe_mtf_confluence_entry 0.1.0-c021`).
    # SCAFFOLD ONLY — not approved. See CAMPAIGN_021_LTF_MTF_CONFLUENCE_PRECOMMIT.md.
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["M15"] = "M15"
    d1_ema_fast: int = 20
    d1_ema_slow: int = 50
    h4_ema_context: int = 50
    h1_ema_slope_bars: int = 3
    m15_pullback_lookback: int = 8
    adx_lookback: int = 14
    adx_min: float = 18.0
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.0
    max_bars_in_trade: int = 32
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> LowerTimeframeMtfConfluenceEntryStrategyConfig:
        if self.d1_ema_fast < 2 or self.d1_ema_slow <= self.d1_ema_fast:
            raise ConfigError("d1_ema_slow must be > d1_ema_fast >= 2")
        if self.h4_ema_context < 2:
            raise ConfigError("h4_ema_context must be >= 2")
        if self.h1_ema_slope_bars < 1:
            raise ConfigError("h1_ema_slope_bars must be >= 1")
        if self.m15_pullback_lookback < 1:
            raise ConfigError("m15_pullback_lookback must be >= 1")
        if self.adx_lookback < 2 or not (0 < self.adx_min < 100):
            raise ConfigError("adx_lookback >= 2 and adx_min in (0, 100)")
        if self.atr_lookback < 2 or self.atr_stop_multiple <= 0:
            raise ConfigError("atr_lookback >= 2 and atr_stop_multiple > 0")
        if self.max_bars_in_trade < 1 or self.max_bars_in_trade > 200:
            raise ConfigError("max_bars_in_trade must be in [1, 200]")
        return self


class MultiTimeframeConfluencePullbackStrategyConfig(BaseModel):
    # CAMPAIGN_020 research candidate (`multi_timeframe_confluence_pullback 0.1.0-c020`).
    # CANDIDATE SCAFFOLD ONLY — not approved for paper/demo/live.
    # See docs/research/CAMPAIGN_020_MTF_CONFLUENCE_PRECOMMIT.md.
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    d1_ema_fast: int = 20
    d1_ema_slow: int = 50
    h4_ema_context: int = 50
    h4_ema_pullback: int = 20
    pullback_lookback: int = 6
    pullback_band_atr: float = 0.5
    rsi_lookback: int = 14
    rsi_pullback_long: float = 40.0
    rsi_pullback_short: float = 60.0
    adx_lookback: int = 14
    adx_min: float = 18.0
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.0
    trailing_stop_atr_multiple: float | None = None
    max_bars_in_trade: int = 24
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> MultiTimeframeConfluencePullbackStrategyConfig:
        if self.d1_ema_fast < 2 or self.d1_ema_slow <= self.d1_ema_fast:
            raise ConfigError("d1_ema_slow must be > d1_ema_fast >= 2")
        if self.h4_ema_context < 2 or self.h4_ema_pullback < 2:
            raise ConfigError("h4 EMA lengths must be >= 2")
        if self.pullback_lookback < 1:
            raise ConfigError("pullback_lookback must be >= 1")
        if self.pullback_band_atr <= 0:
            raise ConfigError("pullback_band_atr must be > 0")
        if self.rsi_lookback < 2:
            raise ConfigError("rsi_lookback must be >= 2")
        if not (0 < self.rsi_pullback_long < self.rsi_pullback_short < 100):
            raise ConfigError(
                "rsi_pullback_long < rsi_pullback_short and both in (0, 100)"
            )
        if self.adx_lookback < 2 or not (0 < self.adx_min < 100):
            raise ConfigError("adx_lookback >= 2 and adx_min in (0, 100)")
        if self.atr_lookback < 2:
            raise ConfigError("atr_lookback must be >= 2")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        if self.max_bars_in_trade < 1 or self.max_bars_in_trade > 60:
            raise ConfigError("max_bars_in_trade must be in [1, 60]")
        if self.trailing_stop_atr_multiple is not None:
            raise ConfigError(
                "trailing_stop_atr_multiple must be None in v1 — hard stop + time only"
            )
        return self


class StrategyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: list[str]
    trend_following: TrendFollowingStrategyConfig | None = None
    volatility_breakout: VolatilityBreakoutStrategyConfig | None = None
    pullback_continuation: PullbackContinuationStrategyConfig | None = None
    mean_reversion: MeanReversionStrategyConfig | None = None
    mean_reversion_protective_stop: MeanReversionProtectiveStopStrategyConfig | None = None
    mean_reversion_thesis_invalidation: MeanReversionThesisInvalidationStrategyConfig | None = None
    session_breakout: SessionBreakoutStrategyConfig | None = None
    random_entry_anchor: RandomEntryAnchorStrategyConfig | None = None
    regime_switcher_atr_percentile: (
        RegimeSwitcherAtrPercentileStrategyConfig | None
    ) = None
    cross_pair_currency_strength_rotation: (
        CrossPairCurrencyStrengthRotationStrategyConfig | None
    ) = None
    calendar_event_window_anomaly: (
        CalendarEventWindowAnomalyStrategyConfig | None
    ) = None
    failed_breakout_reversal: (
        FailedBreakoutReversalStrategyConfig | None
    ) = None
    weekly_cross_sectional_momentum_low_turnover: (
        WeeklyCrossSectionalMomentumLowTurnoverStrategyConfig | None
    ) = None
    weekly_volatility_contraction_breakout: (
        WeeklyVolatilityContractionBreakoutStrategyConfig | None
    ) = None
    multi_timeframe_confluence_pullback: (
        MultiTimeframeConfluencePullbackStrategyConfig | None
    ) = None
    lower_timeframe_mtf_confluence_entry: (
        LowerTimeframeMtfConfluenceEntryStrategyConfig | None
    ) = None

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
        if (
            "mean_reversion_protective_stop" in self.enabled
            and self.mean_reversion_protective_stop is None
        ):
            raise ConfigError(
                "strategy.mean_reversion_protective_stop config required when enabled"
            )
        if (
            "mean_reversion_thesis_invalidation" in self.enabled
            and self.mean_reversion_thesis_invalidation is None
        ):
            raise ConfigError(
                "strategy.mean_reversion_thesis_invalidation config required when enabled"
            )
        if "session_breakout" in self.enabled and self.session_breakout is None:
            raise ConfigError(
                "strategy.session_breakout config required when enabled"
            )
        if (
            "random_entry_anchor" in self.enabled
            and self.random_entry_anchor is None
        ):
            raise ConfigError(
                "strategy.random_entry_anchor config required when enabled"
            )
        if (
            "regime_switcher_atr_percentile" in self.enabled
            and self.regime_switcher_atr_percentile is None
        ):
            raise ConfigError(
                "strategy.regime_switcher_atr_percentile config required when enabled"
            )
        if (
            "cross_pair_currency_strength_rotation" in self.enabled
            and self.cross_pair_currency_strength_rotation is None
        ):
            raise ConfigError(
                "strategy.cross_pair_currency_strength_rotation config required when enabled"
            )
        if (
            "calendar_event_window_anomaly" in self.enabled
            and self.calendar_event_window_anomaly is None
        ):
            raise ConfigError(
                "strategy.calendar_event_window_anomaly config required when enabled"
            )
        if (
            "failed_breakout_reversal" in self.enabled
            and self.failed_breakout_reversal is None
        ):
            raise ConfigError(
                "strategy.failed_breakout_reversal config required when enabled"
            )
        if (
            "weekly_cross_sectional_momentum_low_turnover" in self.enabled
            and self.weekly_cross_sectional_momentum_low_turnover is None
        ):
            raise ConfigError(
                "strategy.weekly_cross_sectional_momentum_low_turnover config "
                "required when enabled"
            )
        if (
            "weekly_volatility_contraction_breakout" in self.enabled
            and self.weekly_volatility_contraction_breakout is None
        ):
            raise ConfigError(
                "strategy.weekly_volatility_contraction_breakout config "
                "required when enabled"
            )
        if (
            "multi_timeframe_confluence_pullback" in self.enabled
            and self.multi_timeframe_confluence_pullback is None
        ):
            raise ConfigError(
                "strategy.multi_timeframe_confluence_pullback config "
                "required when enabled"
            )
        if (
            "lower_timeframe_mtf_confluence_entry" in self.enabled
            and self.lower_timeframe_mtf_confluence_entry is None
        ):
            raise ConfigError(
                "strategy.lower_timeframe_mtf_confluence_entry config "
                "required when enabled"
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

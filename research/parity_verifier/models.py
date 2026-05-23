"""Verifier data models.

Pydantic models pin the shapes the verifier consumes and emits. Every
field is mandatory unless explicitly defaulted; ``extra="forbid"``
catches schema drift early. Models are intentionally simple: a Bar is
a row of OHLC + bid/ask + a timestamp, a Trade is the verifier's view
of one completed position, etc.

None of these models import from ``forex_bot``. They are independent.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Side(str, Enum):
    """Trade direction. ``flat`` is used for the no-position state in
    the event loop, not for trade records."""

    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


class TradeExitReason(str, Enum):
    """How a verifier trade closed. Mirrors the bespoke engine's
    semantics from the mapping spec §5: stop, trailing_stop, time, eod.
    The ``unknown`` value is reserved for unclassified divergences."""

    STOP = "stop"
    TRAILING_STOP = "trailing_stop"
    TIME = "time"
    EOD = "eod"
    UNKNOWN = "unknown"


class ComparisonStatus(str, Enum):
    """Per-pair and overall comparison status, matching the
    `LEAN_PARITY_COMPARISON_METHOD.md` ladder."""

    OK = "ok"
    WARN = "warn"
    FAIL = "fail"
    BLOCKED = "blocked"


class DivergenceClassification(str, Enum):
    """Divergence taxonomy. Extends the LEAN-era taxonomy
    (`LEAN_PARITY_COMPARISON_METHOD.md`) with the
    `FREE_LOCAL_PARITY_VERIFIER_PLAN.md` §9 entries."""

    NONE = "none"
    DATA_MISMATCH = "data_mismatch"
    TIMESTAMP_SESSION_MISMATCH = "timestamp_session_mismatch"
    INDICATOR_MISMATCH = "indicator_mismatch"
    ENTRY_EXIT_RULE_MISMATCH = "entry_exit_rule_mismatch"
    SPREAD_SLIPPAGE_FILL_MISMATCH = "spread_slippage_fill_mismatch"
    STOP_TRAILING_MISMATCH = "stop_trailing_mismatch"
    SIZING_PNL_MISMATCH = "sizing_pnl_mismatch"
    FINANCING_MISMATCH = "financing_mismatch"
    UNKNOWN = "unknown"


class Bar(BaseModel):
    """One completed H4 candle.

    Indicators consume ``open/high/low/close`` (mid prices in the
    bespoke export). Fills consume ``bid_close`` / ``ask_close``.
    ``time`` is the 17:00-New-York-aligned open timestamp.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    time: datetime
    open: float
    high: float
    low: float
    close: float
    bid_open: float
    bid_high: float
    bid_low: float
    bid_close: float
    ask_open: float
    ask_high: float
    ask_low: float
    ask_close: float
    volume: int = 0

    @model_validator(mode="after")
    def _check_ohlc(self) -> Bar:
        if self.high < self.low:
            raise ValueError(f"bar at {self.time}: high < low")
        if not (self.low <= self.open <= self.high):
            raise ValueError(f"bar at {self.time}: open not in [low, high]")
        if not (self.low <= self.close <= self.high):
            raise ValueError(f"bar at {self.time}: close not in [low, high]")
        if self.ask_close < self.bid_close:
            raise ValueError(f"bar at {self.time}: ask_close < bid_close")
        return self


class CandleSeries(BaseModel):
    """Timestamp-sorted, deduplicated bars for one instrument."""

    model_config = ConfigDict(extra="forbid")

    instrument: str
    bars: list[Bar]

    @model_validator(mode="after")
    def _check_sorted_unique(self) -> CandleSeries:
        if not self.bars:
            return self
        times = [bar.time for bar in self.bars]
        if times != sorted(times):
            raise ValueError(f"{self.instrument}: bars are not sorted ascending by time")
        if len(set(times)) != len(times):
            raise ValueError(f"{self.instrument}: duplicate timestamps")
        return self


class InstrumentSpec(BaseModel):
    """Static instrument metadata the verifier needs for sizing / pip
    math. The pip_size mirrors the bespoke engine's convention without
    importing the bespoke definition: JPY pairs use 0.01, everything
    else 0.0001."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    pip_size: float
    quote_currency: str
    base_currency: str

    @model_validator(mode="after")
    def _check_pip(self) -> InstrumentSpec:
        if self.pip_size <= 0:
            raise ValueError(f"{self.name}: pip_size must be > 0")
        return self


class VerifierConfig(BaseModel):
    """The frozen CAMPAIGN_002 parameter set the verifier replays.

    Loaded from ``research/lean_parity/lean_parity_config.json`` by the
    data loader; not editable from inside the verifier code path.
    """

    model_config = ConfigDict(extra="forbid")

    ema_fast: int
    ema_slow: int
    donchian_lookback: int
    atr_lookback: int
    atr_stop_multiple: float
    trailing_stop_atr_multiple: float
    max_bars_in_trade: int
    risk_per_trade_pct: float
    starting_equity_usd: float
    fixed_slippage_pips: float
    spread_slippage_multiplier: float
    min_atr_pips: dict[str, float] = Field(default_factory=dict)
    account_currency: str = "USD"

    @model_validator(mode="after")
    def _check(self) -> VerifierConfig:
        if self.ema_fast <= 0 or self.ema_slow <= 0:
            raise ValueError("ema lengths must be > 0")
        if self.ema_fast >= self.ema_slow:
            raise ValueError("ema_fast must be < ema_slow")
        if self.donchian_lookback <= 0 or self.atr_lookback <= 0:
            raise ValueError("donchian / atr lookback must be > 0")
        if self.atr_stop_multiple <= 0 or self.trailing_stop_atr_multiple <= 0:
            raise ValueError("stop multiples must be > 0")
        if self.max_bars_in_trade <= 0:
            raise ValueError("max_bars_in_trade must be > 0")
        if not (0 < self.risk_per_trade_pct <= 5):
            raise ValueError("risk_per_trade_pct must be in (0, 5]")
        if self.starting_equity_usd <= 0:
            raise ValueError("starting_equity_usd must be > 0")
        return self


class Signal(BaseModel):
    """The decision made on one completed bar: enter long, enter short,
    or no entry. Exits are evaluated separately by the event loop."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    time: datetime
    side: Side
    close: float
    atr: float
    is_entry: bool


class StopState(BaseModel):
    """Mutable stop state of one open position. The event loop ratchets
    ``stop_price`` per bar and records whether the stop ever moved off
    its initial level (which controls the exit-reason label)."""

    model_config = ConfigDict(extra="forbid")

    initial_stop_price: float
    stop_price: float
    has_trailed: bool = False


class Trade(BaseModel):
    """One closed verifier position."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    instrument: str
    side: Side
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    exit_reason: TradeExitReason
    units: int
    initial_stop_price: float
    final_stop_price: float
    bars_held: int
    r_multiple: float
    return_pct: float


class PairResult(BaseModel):
    """The verifier's per-pair summary, shaped to be directly
    comparable to the bespoke reference and the LEAN
    ``parity_summary.json`` shape."""

    model_config = ConfigDict(extra="forbid")

    instrument: str
    candle_count: int
    trades: int
    expectancy_r: float | None = None
    return_pct: float | None = None
    profit_factor: float | None = None
    win_rate: float | None = None


class VerifierResult(BaseModel):
    """Top-level verifier output for one full run."""

    model_config = ConfigDict(extra="forbid")

    parity_target: str
    risk_engine_used: bool = False
    fill_timing: str
    window_start: datetime
    window_end: datetime
    config_hash: str
    strategy_evidence: bool = False
    total_trades: int
    pairs: list[PairResult]

    @model_validator(mode="after")
    def _check(self) -> VerifierResult:
        if self.strategy_evidence:
            raise ValueError(
                "strategy_evidence must be False — the verifier is a "
                "diagnostic instrument and cannot approve a strategy"
            )
        if self.risk_engine_used:
            raise ValueError(
                "risk_engine_used must be False — the verifier targets "
                "the no-RiskEngine bespoke reference"
            )
        total = sum(p.trades for p in self.pairs)
        if total != self.total_trades:
            raise ValueError(
                f"total_trades ({self.total_trades}) does not equal the sum of per-pair trades ({total})"
            )
        return self


class PairComparison(BaseModel):
    """One pair's row in the comparison report."""

    model_config = ConfigDict(extra="forbid")

    instrument: str
    bespoke_trades: int
    verifier_trades: int | None
    trade_count_delta_pct: float | None
    bespoke_expectancy_r: float | None
    verifier_expectancy_r: float | None
    expectancy_r_delta: float | None
    bespoke_return_pct: float | None
    verifier_return_pct: float | None
    return_pct_delta: float | None
    status: ComparisonStatus
    classification: DivergenceClassification


class ComparisonReport(BaseModel):
    """Top-level comparison output."""

    model_config = ConfigDict(extra="forbid")

    bespoke_reference_path: str
    verifier_result_path: str | None
    pairs: list[PairComparison]
    bespoke_total_trades: int
    verifier_total_trades: int | None
    total_trade_count_delta_pct: float | None
    overall_status: ComparisonStatus
    overall_classification: DivergenceClassification
    notes: list[str] = Field(default_factory=list)
    strategy_evidence: bool = False

    @model_validator(mode="after")
    def _check(self) -> ComparisonReport:
        if self.strategy_evidence:
            raise ValueError(
                "strategy_evidence must be False — the comparison is "
                "diagnostic and cannot approve a strategy"
            )
        return self

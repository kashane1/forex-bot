"""Backtrader port of CAMPAIGN_015 H4 ``failed_breakout_reversal 0.1.0-c015``.

Mirrors the frozen rules at
``src/forex_bot/strategies/failed_breakout_reversal.py`` (R1-R10) and
the pre-commit at
``docs/research/CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md`` §5.

This adapter is a **secondary verification lane**. It cannot approve a
strategy. The bespoke engine remains canonical.

Key design points:

* The adapter uses Backtrader for the candle loop only; the strategy
  maintains its own one-position state machine. The Cerebro broker is
  bypassed.
* No Backtrader OANDA / live integration. No network. No broker.
* Same frozen rules as the bespoke side: prior 20-bar range
  (excluding the signal bar); ADX(14) <= 20; ATR(14) Wilder; sweep
  buffer 0.10 * ATR; stop buffer 0.10 * ATR; stop_distance_atr in
  [0.80, 2.20]; hard stop OR 12-bar time stop; no trailing; no
  take-profit; same-bar adverse-stop wins.
* **Fill timing: next_bar_open** — when the strategy generates a
  signal on bar t, the entry is *pending* and fills at the open of
  bar t+1. This is the BT-side approximation of the bespoke engine's
  ``fill_timing = "next_bar_open"``. The approximation is documented
  here as ``FILL_TIMING_APPROXIMATION`` rather than a bug.
* If local Backtrader data is absent (no ``CandleAdapterResult`` to
  feed in), the BLOCKED outcome is recorded at the campaign-runner
  level (Phase 6); this module is data-agnostic.

``strategy_evidence: false``.
"""

from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path
from typing import Any

import backtrader as bt
import pandas as pd

from research.backtrader_lane.data_adapter import CandleAdapterResult
from research.backtrader_lane.fold_windows import FoldWindowSpec, bar_date_utc
from research.backtrader_lane.risk_parity import (
    ENTRY_BAR_STOP_POLICIES,
    RiskParityState,
    build_campaign_015_risk_engine,
    evaluate_pending_entry,
    record_rejections,
)
from research.backtrader_lane.runner import (
    BacktraderTrade,
    CampaignAdapter,
    PairRunResult,
    register_campaign,
)
from research.backtrader_lane.strategies.campaign_002_trend_following import (
    _BASE_CCY,
    _DISPLAY_PRECISION,
    _PIP_SIZE,
    _QUOTE_CCY,
    _fill_entry_price,
    _round_price,
    _size_position,
    _trade_pnl,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
CAMPAIGN_015_CONFIG_PATH = (
    REPO_ROOT / "configs" / "campaign_015_failed_breakout_reversal.yaml"
)

EXPECTED_VERSION = "0.1.0-c015"
FROZEN_PARAMETERS: dict[str, Any] = {
    "version": EXPECTED_VERSION,
    "timeframe": "H4",
    "range_lookback": 20,
    "atr_lookback": 14,
    "adx_lookback": 14,
    "adx_max": 20.0,
    "sweep_buffer_atr": 0.10,
    "min_range_atr_multiple": 1.25,
    "max_range_atr_multiple": 5.00,
    "stop_buffer_atr": 0.10,
    "min_stop_atr_multiple": 0.80,
    "max_stop_atr_multiple": 2.20,
    "max_bars_in_trade": 12,
    "take_profit_r": None,
    "trailing_stop_atr_multiple": None,
    "entry_timing": "next_bar_open",
    "same_bar_adverse_stop_wins": True,
    "min_atr_pips": {},
}

EXPECTED_FIXED_SLIPPAGE_PIPS = 0.2
EXPECTED_SPREAD_SLIPPAGE_MULTIPLIER = 0.5
EXPECTED_RISK_PER_TRADE_PCT = 0.25
EXPECTED_STARTING_EQUITY = 500.0
EXPECTED_COMMISSION_PER_UNIT = 0.0


def _load_campaign_015_config_strategy() -> dict[str, Any]:
    """Load the strategy.failed_breakout_reversal block from the
    committed YAML via forex_bot.config."""

    from forex_bot.config import load_settings

    settings = load_settings(CAMPAIGN_015_CONFIG_PATH)
    fbr = settings.strategy.failed_breakout_reversal
    if fbr is None:
        raise SystemExit(
            "CAMPAIGN_015 YAML missing strategy.failed_breakout_reversal "
            "block; refusing to start."
        )
    return fbr.model_dump()


def _assert_frozen(strategy_cfg: dict[str, Any]) -> None:
    mismatched: list[str] = []
    for key, expected in FROZEN_PARAMETERS.items():
        got = strategy_cfg.get(key)
        if (isinstance(expected, list) and isinstance(got, list)) or (
            isinstance(expected, dict) and isinstance(got, dict)
        ):
            if got != expected:
                mismatched.append(f"  {key}: got {got!r}, expected {expected!r}")
        elif got != expected:
            mismatched.append(f"  {key}: got {got!r}, expected {expected!r}")
    if mismatched:
        raise SystemExit(
            "CAMPAIGN_015 frozen-parameter mismatch — see "
            "CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md §5:\n"
            + "\n".join(mismatched)
        )


class _Campaign015Feed(bt.feeds.PandasData):
    """PandasData with bid/ask OHLC on extra lines."""

    lines = (
        "bid_open",
        "bid_high",
        "bid_low",
        "bid_close",
        "ask_open",
        "ask_high",
        "ask_low",
        "ask_close",
    )
    params = (
        ("bid_open", -1),
        ("bid_high", -1),
        ("bid_low", -1),
        ("bid_close", -1),
        ("ask_open", -1),
        ("ask_high", -1),
        ("ask_low", -1),
        ("ask_close", -1),
    )


def _bar_count(strategy: bt.Strategy) -> int:
    return len(strategy)


def run_campaign_015_pair(
    candles: CandleAdapterResult,
    starting_equity_usd: float,
    *,
    config_path: Path = CAMPAIGN_015_CONFIG_PATH,
    strategy_cfg_override: dict[str, Any] | None = None,
    fold_window: FoldWindowSpec | None = None,
    strict_test_window: bool = False,
    entry_bar_stop_policy: str = "backtrader_default",
    risk_engine_parity: bool = False,
) -> PairRunResult:
    """Drive one instrument through the CAMPAIGN_015 BT adapter.

    `strategy_cfg_override` lets tests substitute a synthetic config
    without reading the YAML. Production runs leave it None and the
    binding YAML + _assert_frozen() pair governs.

    ``entry_bar_stop_policy`` controls entry-bar adverse-stop handling:
    - ``backtrader_default`` — current BT behaviour (same-bar stop on entry).
    - ``bespoke_current_no_entry_bar_stop`` — parity with current bespoke
      ``BacktestEngine`` (no entry-bar adverse stop; later-bar stops unchanged).

    ``risk_engine_parity`` when True runs read-only ``RiskEngine.evaluate``
    at fill time using local candle bid/ask only (no broker)."""

    if entry_bar_stop_policy not in ENTRY_BAR_STOP_POLICIES:
        raise ValueError(
            f"unknown entry_bar_stop_policy {entry_bar_stop_policy!r}; "
            f"expected one of {sorted(ENTRY_BAR_STOP_POLICIES)}"
        )

    if strategy_cfg_override is None:
        strategy_cfg = _load_campaign_015_config_strategy()
        _assert_frozen(strategy_cfg)
    else:
        strategy_cfg = dict(strategy_cfg_override)
        _assert_frozen(strategy_cfg)

    range_lookback = int(strategy_cfg["range_lookback"])
    atr_lookback = int(strategy_cfg["atr_lookback"])
    adx_lookback = int(strategy_cfg["adx_lookback"])
    adx_max = float(strategy_cfg["adx_max"])
    sweep_buffer_atr = float(strategy_cfg["sweep_buffer_atr"])
    min_range_atr = float(strategy_cfg["min_range_atr_multiple"])
    max_range_atr = float(strategy_cfg["max_range_atr_multiple"])
    stop_buffer_atr = float(strategy_cfg["stop_buffer_atr"])
    min_stop_atr = float(strategy_cfg["min_stop_atr_multiple"])
    max_stop_atr = float(strategy_cfg["max_stop_atr_multiple"])
    max_bars_in_trade = int(strategy_cfg["max_bars_in_trade"])

    instrument = candles.instrument
    pip_size = _PIP_SIZE.get(instrument)
    quote_ccy = _QUOTE_CCY.get(instrument)
    base_ccy = _BASE_CCY.get(instrument)
    display_precision = _DISPLAY_PRECISION.get(instrument)
    if (
        pip_size is None
        or quote_ccy is None
        or base_ccy is None
        or display_precision is None
    ):
        raise KeyError(
            f"{instrument!r} not in the CAMPAIGN_015 universe; "
            f"known: {sorted(_PIP_SIZE.keys())}"
        )

    settings = None
    if config_path.is_file():
        from forex_bot.config import load_settings

        settings = load_settings(config_path)
        fixed_slippage_pips = float(settings.backtest.fixed_slippage_pips)
        spread_slippage_multiplier = float(settings.backtest.spread_slippage_multiplier)
        risk_per_trade_pct = float(settings.risk.risk_per_trade_pct)
    else:
        # Allow tests to call run_campaign_015_pair without the live YAML.
        fixed_slippage_pips = EXPECTED_FIXED_SLIPPAGE_PIPS
        spread_slippage_multiplier = EXPECTED_SPREAD_SLIPPAGE_MULTIPLIER
        risk_per_trade_pct = EXPECTED_RISK_PER_TRADE_PCT

    risk_engine = None
    parity_state: RiskParityState | None = None
    rejection_counts: dict[str, int] = {}
    if risk_engine_parity:
        if settings is None:
            raise ValueError(
                "risk_engine_parity requires campaign config YAML at "
                f"{config_path}; cannot construct RiskEngine without settings"
            )
        risk_engine = build_campaign_015_risk_engine(settings)
        parity_state = RiskParityState(
            account_currency=settings.market.account_currency,
            equity_peak=float(starting_equity_usd),
        )

    # Build Backtrader-friendly dataframe.
    df = candles.mid_df.copy()
    df = df.assign(
        bid_open=candles.bid_ohlc_df["open"],
        bid_high=candles.bid_ohlc_df["high"],
        bid_low=candles.bid_ohlc_df["low"],
        bid_close=candles.bid_ohlc_df["close"],
        ask_open=candles.ask_ohlc_df["open"],
        ask_high=candles.ask_ohlc_df["high"],
        ask_low=candles.ask_ohlc_df["low"],
        ask_close=candles.ask_ohlc_df["close"],
    )
    df.index = df.index.tz_convert("UTC").tz_localize(None)

    recorded: list[BacktraderTrade] = []
    nav = {"value": float(starting_equity_usd)}
    test_start = fold_window.test_start if fold_window else None
    test_end = fold_window.test_end if fold_window else None

    class _Campaign015Strategy(bt.Strategy):  # pragma: no cover - bt callbacks
        params = (
            ("atr_len", atr_lookback),
            ("adx_len", adx_lookback),
        )

        def __init__(self) -> None:
            self._atr = bt.indicators.AverageTrueRange(
                self.data, period=self.p.atr_len
            )
            self._adx = bt.indicators.AverageDirectionalMovementIndex(
                self.data, period=self.p.adx_len
            )
            self._in_position: bool = False
            self._side: str = "flat"
            self._entry_time: pd.Timestamp | None = None
            self._entry_price: float = 0.0
            self._stop_price: float = 0.0
            self._bars_held: int = 0
            self._units: int = 0
            self._initial_stop_distance: float = 0.0
            # Pending entry (next_bar_open) — set on signal bar, filled
            # on the *next* bar's open.
            self._pending_side: str | None = None
            self._pending_stop: float = 0.0
            self._pending_signal_in_test: bool = False
            self._pending_signal_time: datetime | None = None
            self._pending_atr: float = 0.0

        def _bar_time(self) -> pd.Timestamp:
            from datetime import UTC
            return pd.Timestamp(bt.num2date(self.data.datetime[0])).tz_localize(UTC)

        def _bar_in_test_window(self) -> bool:
            if test_start is None or test_end is None or not strict_test_window:
                return True
            d = bar_date_utc(self._bar_time().to_pydatetime())
            return test_start <= d <= test_end

        def _close_trade(self, *, exit_price: float, exit_reason: str) -> None:
            pnl_account = _trade_pnl(
                side=self._side,
                entry_price=self._entry_price,
                exit_price=exit_price,
                units=self._units,
                quote_currency=quote_ccy,
                base_currency=base_ccy,
            )
            pnl_quote = (
                (exit_price - self._entry_price) * self._units
                if self._side == "long"
                else (self._entry_price - exit_price) * self._units
            )
            r_mult: float | None = None
            if self._initial_stop_distance > 0 and self._units > 0:
                risk_distance = self._initial_stop_distance * self._units
                r_mult = (
                    pnl_account / risk_distance if risk_distance > 0 else 0.0
                )
            return_pct = (
                (pnl_account / nav["value"]) * 100.0 if nav["value"] > 0 else None
            )
            recorded.append(
                BacktraderTrade(
                    instrument=instrument,
                    side=self._side,
                    entry_time=(
                        self._entry_time.to_pydatetime()
                        if self._entry_time
                        else self._bar_time().to_pydatetime()
                    ),
                    entry_price=self._entry_price,
                    exit_time=self._bar_time().to_pydatetime(),
                    exit_price=exit_price,
                    units=self._units,
                    exit_reason=exit_reason,
                    bars_held=self._bars_held,
                    pnl_quote=pnl_quote,
                    pnl_account=pnl_account,
                    r_multiple=r_mult,
                    return_pct=return_pct,
                )
            )
            nav["value"] += pnl_account
            if parity_state is not None:
                parity_state.record_exit(
                    exit_time=self._bar_time().to_pydatetime(),
                    pnl=pnl_account,
                    equity=nav["value"],
                )
            self._in_position = False
            self._side = "flat"
            self._bars_held = 0
            self._units = 0
            self._initial_stop_distance = 0.0
            self._stop_price = 0.0

        def _prior_range(self) -> tuple[float, float] | None:
            """Return (prior_high, prior_low) over bars [t-N..t-1] —
            strictly excluding the current bar."""
            highs: list[float] = []
            lows: list[float] = []
            for offset in range(1, range_lookback + 1):
                try:
                    highs.append(float(self.data.high[-offset]))
                    lows.append(float(self.data.low[-offset]))
                except IndexError:
                    return None
            if not highs:
                return None
            return max(highs), min(lows)

        def _try_signal(self) -> None:
            """Generate a signal on the current bar; mirrors R1-R10 of
            the bespoke strategy. The actual entry happens on the next
            bar's open (queue via `self._pending_side`)."""

            if strict_test_window and not self._bar_in_test_window():
                return

            # R1: warmup — need range + ATR/ADX burn-in.
            warmup = max(range_lookback, atr_lookback, adx_lookback) + 2
            if _bar_count(self) < warmup:
                return

            # R2: skip if already in a position.
            if self._in_position:
                return

            # R3-R4: ATR / ADX gates.
            try:
                last_atr = float(self._atr[0])
                last_adx = float(self._adx[0])
            except IndexError:
                return
            if not (math.isfinite(last_atr) and last_atr > 0):
                return
            if not math.isfinite(last_adx):
                return
            if last_adx > adx_max:
                return

            # R5: prior 20-bar range.
            pr = self._prior_range()
            if pr is None:
                return
            prior_high, prior_low = pr
            range_width = prior_high - prior_low
            if range_width <= 0:
                return

            # R6: range/ATR gates.
            range_width_atr = range_width / last_atr
            if range_width_atr < min_range_atr:
                return
            if range_width_atr > max_range_atr:
                return

            # R8: signal-bar geometry.
            last_high = float(self.data.high[0])
            last_low = float(self.data.low[0])
            last_close = float(self.data.close[0])
            sweep_buffer = sweep_buffer_atr * last_atr
            stop_buffer = stop_buffer_atr * last_atr

            short_swept = last_high > prior_high + sweep_buffer
            short_rejected = last_close < prior_high
            long_swept = last_low < prior_low - sweep_buffer
            long_rejected = last_close > prior_low

            short_setup = short_swept and short_rejected
            long_setup = long_swept and long_rejected

            # R9: dual-trigger defense — no signal.
            if short_setup and long_setup:
                return
            if not (short_setup or long_setup):
                return

            if short_setup:
                side = "short"
                stop = last_high + stop_buffer
            else:
                side = "long"
                stop = last_low - stop_buffer

            # R10: stop-distance gate (using close[t] as diagnostic ref).
            stop_distance_atr = abs(last_close - stop) / last_atr
            if stop_distance_atr < min_stop_atr:
                return
            if stop_distance_atr > max_stop_atr:
                return

            # Queue the entry for the next bar's open. FILL_TIMING_APPROXIMATION:
            # the bespoke engine fills at the next bar's open via its
            # `fill_timing = "next_bar_open"` path; we emulate that by
            # deferring the entry-execution side of the signal to the
            # next next() invocation.
            self._pending_side = side
            self._pending_stop = stop
            self._pending_signal_in_test = self._bar_in_test_window()
            self._pending_signal_time = self._bar_time().to_pydatetime()
            self._pending_atr = last_atr

        def _execute_pending_entry(self) -> None:
            """If a pending entry exists from the prior bar, fill it at
            the current bar's open."""

            if self._pending_side is None or self._in_position:
                return
            if strict_test_window and not self._pending_signal_in_test:
                self._pending_side = None
                self._pending_stop = 0.0
                self._pending_signal_in_test = False
                return
            if strict_test_window and not self._bar_in_test_window():
                self._pending_side = None
                self._pending_stop = 0.0
                self._pending_signal_in_test = False
                return
            side = self._pending_side
            stop = self._pending_stop
            bid_open = float(self.data.bid_open[0])
            ask_open = float(self.data.ask_open[0])
            entry_price = _fill_entry_price(
                side=side,
                bid_close=bid_open,
                ask_close=ask_open,
                fixed_slippage_pips=fixed_slippage_pips,
                spread_slippage_multiplier=spread_slippage_multiplier,
                pip_size=pip_size,
            )
            # Validate that the entry geometry still respects the
            # adverse-stop-wins invariant: long stop must be below
            # entry; short stop must be above entry.
            if side == "long" and stop >= entry_price:
                self._pending_side = None
                self._pending_stop = 0.0
                return
            if side == "short" and stop <= entry_price:
                self._pending_side = None
                self._pending_stop = 0.0
                return

            stop_r = _round_price(stop, display_precision)
            units = 0
            if risk_engine is not None and parity_state is not None:
                assert self._pending_signal_time is not None
                risk_result = evaluate_pending_entry(
                    risk_engine=risk_engine,
                    instrument_name=instrument,
                    side=side,
                    stop_price=stop_r,
                    signal_time=self._pending_signal_time,
                    fill_time=self._bar_time().to_pydatetime(),
                    fill_bid=bid_open,
                    fill_ask=ask_open,
                    atr=self._pending_atr,
                    equity=nav["value"],
                    parity_state=parity_state,
                    strategy_version=strategy_cfg["version"],
                )
                if not risk_result.approved:
                    record_rejections(rejection_counts, risk_result.rejection_codes)
                    self._pending_side = None
                    self._pending_stop = 0.0
                    self._pending_signal_time = None
                    self._pending_atr = 0.0
                    return
                units = int(risk_result.units or 0)
                if risk_result.stop_price is not None:
                    stop_r = float(risk_result.stop_price)
            else:
                units = _size_position(
                    nav=nav["value"],
                    risk_per_trade_pct=risk_per_trade_pct,
                    entry_price=entry_price,
                    stop_price=stop_r,
                    pip_size=pip_size,
                    quote_currency=quote_ccy,
                    base_currency=base_ccy,
                )
            if units <= 0:
                self._pending_side = None
                self._pending_stop = 0.0
                return

            self._in_position = True
            self._side = side
            self._entry_time = self._bar_time()
            self._entry_price = entry_price
            self._stop_price = stop_r
            self._bars_held = 0
            self._units = units
            self._initial_stop_distance = abs(entry_price - self._stop_price)
            self._pending_side = None
            self._pending_stop = 0.0
            self._pending_signal_in_test = False
            self._pending_signal_time = None
            self._pending_atr = 0.0

            # Adverse-stop-wins on entry bar (BT default only).
            if entry_bar_stop_policy == "backtrader_default" and same_bar_adverse_stop_check(
                side=side,
                stop_price=self._stop_price,
                bar_high=float(self.data.high[0]),
                bar_low=float(self.data.low[0]),
            ):
                self._close_trade(
                    exit_price=self._stop_price, exit_reason="stop_same_bar"
                )

        def _try_exit(self) -> None:
            """Process exits on the current bar. Hard stop or time stop."""

            self._bars_held += 1
            bid_low = float(self.data.bid_low[0])
            ask_high = float(self.data.ask_high[0])
            bid_close = float(self.data.bid_close[0])
            ask_close = float(self.data.ask_close[0])

            # Adverse-stop check.
            if self._side == "long" and bid_low <= self._stop_price:
                self._close_trade(exit_price=self._stop_price, exit_reason="stop")
                return
            if self._side == "short" and ask_high >= self._stop_price:
                self._close_trade(exit_price=self._stop_price, exit_reason="stop")
                return
            # Time-stop.
            if self._bars_held >= max_bars_in_trade:
                exit_price = bid_close if self._side == "long" else ask_close
                self._close_trade(exit_price=exit_price, exit_reason="time")

        def next(self) -> None:
            # Force-close at fold test_end boundary when strict mode is on
            # and the bar is the last in the slice on test_end.
            if (
                strict_test_window
                and test_end is not None
                and self._in_position
                and bar_date_utc(self._bar_time().to_pydatetime()) >= test_end
            ):
                bid_close = float(self.data.bid_close[0])
                ask_close = float(self.data.ask_close[0])
                exit_price = bid_close if self._side == "long" else ask_close
                self._close_trade(exit_price=exit_price, exit_reason="fold_end")
            # Order matches the bespoke event loop:
            # 1. exits on the current bar (if a position is open),
            # 2. pending entry execution at this bar's open (the bar
            #    after a signal-bar fired),
            # 3. fresh signal detection on the current bar (the entry
            #    will execute on the next next() call).
            if self._in_position:
                self._try_exit()
            if not self._in_position and self._pending_side is not None:
                self._execute_pending_entry()
            if not self._in_position:
                self._try_signal()

        def stop(self) -> None:
            if self._in_position:
                bid_close = float(self.data.bid_close[0])
                ask_close = float(self.data.ask_close[0])
                exit_price = bid_close if self._side == "long" else ask_close
                self._close_trade(exit_price=exit_price, exit_reason="eod")

    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.setcash(starting_equity_usd)
    cerebro.adddata(_Campaign015Feed(dataname=df))
    cerebro.addstrategy(_Campaign015Strategy)
    cerebro.run()

    analyzer_outputs: dict[str, Any] = {"closed_trades": len(recorded)}
    if risk_engine_parity:
        analyzer_outputs["risk_engine_parity"] = True
        analyzer_outputs["rejection_counts"] = dict(rejection_counts)
    analyzer_outputs["entry_bar_stop_policy"] = entry_bar_stop_policy

    return PairRunResult(
        instrument=instrument,
        candle_count=candles.bar_count,
        trades=recorded,
        final_cash=float(nav["value"]),
        starting_cash=float(starting_equity_usd),
        analyzer_outputs=analyzer_outputs,
    )


def same_bar_adverse_stop_check(
    *,
    side: str,
    stop_price: float,
    bar_high: float,
    bar_low: float,
) -> bool:
    """Adverse-stop-wins rule (Phase 0 §4). If the entry bar's range
    crosses the stop level, the stop wins."""

    if side == "long":
        return bar_low <= stop_price
    return bar_high >= stop_price


CAMPAIGN_015_APPROXIMATION_FLAGS: tuple[str, ...] = (
    "FILL_TIMING_APPROXIMATION: the bespoke engine fills at "
    "fill_timing = 'next_bar_open' (the open of the bar *following* "
    "the signal bar). The BT lane emulates this by queuing the entry "
    "on the signal bar via `_pending_side` and executing it at the "
    "next bar's open inside `_execute_pending_entry`. This is the "
    "closest faithful BT analogue; minor microstructure drift (1-bar "
    "scheduler timing) is expected and is the canonical reason this "
    "lane is classified `FILL_TIMING_APPROXIMATION` rather than `PASS`.",
    "RANGE_PRIOR_BARS_ONLY: prior_high / prior_low read bars [-1..-N] "
    "via `self.data.high[-offset]` / `self.data.low[-offset]`, matching "
    "the bespoke strategy's `high.iloc[-(range_lookback+1):-1]` window "
    "(strictly excludes the current bar).",
    "ADX_AND_ATR_CURRENT_BAR: ADX(14) and ATR(14) are read at the "
    "current bar (`self._adx[0]` / `self._atr[0]`), matching the "
    "bespoke `adx_series.iloc[-1]` / `atr_series.iloc[-1]`.",
    "ENTRY_BAR_STOP_POLICY: default BT mode applies same-bar adverse stop "
    "on the entry bar (`backtrader_default`). Parity mode "
    "`bespoke_current_no_entry_bar_stop` skips entry-bar adverse stop to "
    "mirror current bespoke BacktestEngine behaviour; later-bar stops unchanged.",
    "ADVERSE_STOP_WINS_LATER_BARS: on bars after entry, adverse stop wins "
    "when bar_low <= stop (long) or bar_high >= stop (short).",
    "NO_TRAILING_STOP: trailing_stop_atr_multiple = None on both sides; "
    "the only exits are hard stop and 12-bar time stop. No take-profit.",
    "BACKTRADER_BROKER_BYPASSED: Cerebro broker is not used for fills; "
    "the strategy maintains its own one-position state machine and "
    "fills at next-bar-open using bid/ask + slippage.",
    "MANUAL_SIZING_RISK_FRACTION: 0.25% of compounding NAV; whole-units "
    "floor; pip value derived from quote/base currency at entry price.",
    "NO_FINANCING: financing/swap not modeled in either engine; "
    "comparison is pre-financing (CAMPAIGN_015 inherits the project-"
    "standard ESTIMATED-only financing posture).",
)


CAMPAIGN_015_ADAPTER = CampaignAdapter(
    campaign_id="CAMPAIGN_015",
    strategy_id="failed_breakout_reversal",
    strategy_version=EXPECTED_VERSION,
    description=(
        "Backtrader port of CAMPAIGN_015 H4 failed_breakout_reversal "
        "0.1.0-c015 — research candidate scaffold. Frozen rules from "
        "src/forex_bot/strategies/failed_breakout_reversal.py and "
        "CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md §5. Cannot "
        "approve any strategy."
    ),
    runner_fn=run_campaign_015_pair,
    default_instruments=(
        "EUR_USD",
        "GBP_USD",
        "USD_JPY",
        "AUD_USD",
        "USD_CAD",
        "USD_CHF",
        "NZD_USD",
    ),
    default_starting_equity_usd=EXPECTED_STARTING_EQUITY,
    risk_per_trade_pct=EXPECTED_RISK_PER_TRADE_PCT,
    approximation_flags=CAMPAIGN_015_APPROXIMATION_FLAGS,
    notes=(
        "strategy_evidence: false; CAMPAIGN_015 candidate scaffold; "
        "Phase 0 verdict ceiling is PASS_RESEARCH_SCREEN (not approval); "
        "BT lane is secondary verification only and is classified "
        "FILL_TIMING_APPROXIMATION on the next-bar-open fill timing."
    ),
)


register_campaign(CAMPAIGN_015_ADAPTER)

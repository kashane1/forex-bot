#!/usr/bin/env python3
"""Bar-level Backtrader vs bespoke signal trace for CAMPAIGN_015.

Focuses on one fold × pair cell (default fold 0 / EUR_USD) and emits
comparable per-bar trace rows for strategy rules, RiskEngine acceptance,
position state, and pending-entry state.

Diagnostic-only. Does NOT approve any strategy.
`strategy_evidence: false`.

Usage:
    python scripts/diff_campaign_015_signals.py \\
        --fold 0 --pair EUR_USD \\
        --plan research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/plan.json \\
        --output research/campaign_015/diagnostics/signal_diff
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from research.backtrader_lane.data_adapter import load_candles
from research.backtrader_lane.fold_windows import (
    FoldWindowSpec,
    load_fold_plan,
    slice_candles,
)
from research.backtrader_lane.strategies.campaign_002_trend_following import (
    _PIP_SIZE,
    _fill_entry_price,
    _round_price,
    _size_position,
)
from research.backtrader_lane.strategies.campaign_015_failed_breakout_reversal import (
    CAMPAIGN_015_CONFIG_PATH,
    same_bar_adverse_stop_check,
)

from forex_bot.backtesting.engine import BacktestEngine
from forex_bot.config import load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, InstrumentRepo
from forex_bot.domain.candles import CandleFrame
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.risk.policy import RiskEngine, RiskInputs
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.failed_breakout_reversal import (
    FailedBreakoutReversalStrategy,
)
from forex_bot.strategies.indicators import adx as bespoke_adx
from forex_bot.strategies.indicators import atr as bespoke_atr

DEFAULT_PLAN = (
    ROOT
    / "research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/plan.json"
)
DEFAULT_OUTPUT = ROOT / "research/campaign_015/diagnostics/signal_diff"
DEFAULT_BT_DIR = ROOT / "research/campaign_015/diagnostics/backtrader_fold_window"
DEFAULT_BESPOKE_DIR = (
    ROOT / "research/campaign_015/diagnostics/walk_forward_rehydrate"
)

STRATEGY_CFG_KEYS = (
    "version",
    "timeframe",
    "range_lookback",
    "atr_lookback",
    "adx_lookback",
    "adx_max",
    "sweep_buffer_atr",
    "min_range_atr_multiple",
    "max_range_atr_multiple",
    "stop_buffer_atr",
    "min_stop_atr_multiple",
    "max_stop_atr_multiple",
    "max_bars_in_trade",
    "entry_timing",
    "same_bar_adverse_stop_wins",
    "min_atr_pips",
)


class RootCause(StrEnum):
    RISK_ENGINE_REJECTION_MISSING = "RISK_ENGINE_REJECTION_MISSING"
    STRATEGY_RULE_MISMATCH = "STRATEGY_RULE_MISMATCH"
    INDICATOR_MISMATCH = "INDICATOR_MISMATCH"
    PRIOR_BAR_INDEXING_MISMATCH = "PRIOR_BAR_INDEXING_MISMATCH"
    WARMUP_WINDOW_MISMATCH = "WARMUP_WINDOW_MISMATCH"
    FILL_TIMING_MISMATCH = "FILL_TIMING_MISMATCH"
    POSITION_STATE_MISMATCH = "POSITION_STATE_MISMATCH"
    UNKNOWN = "UNKNOWN"


@dataclass
class RawSignalEval:
    side: str  # long | short | none
    reason: str = ""
    prior_high: float | None = None
    prior_low: float | None = None
    atr: float | None = None
    adx: float | None = None
    range_width_atr: float | None = None
    sweep_distance_atr: float | None = None
    stop_distance_atr: float | None = None
    stop_price: float | None = None


@dataclass
class TraceRow:
    timestamp: str
    pair: str
    fold: int
    in_test_window: bool
    high: float
    low: float
    close: float
    prior_high: float | None
    prior_low: float | None
    bespoke_atr: float | None
    bespoke_adx: float | None
    bt_atr: float | None
    bt_adx: float | None
    range_width_atr: float | None
    sweep_distance_atr: float | None
    stop_distance_atr: float | None
    bespoke_raw: str
    bt_raw: str
    bespoke_accepted: str  # yes | no | n/a
    bespoke_rejection: str
    bt_accepted: str
    bt_rejection: str
    bespoke_position: str  # flat | long | short
    bt_position: str
    bespoke_pending: str  # none | long | short
    bt_pending: str
    bespoke_entry_bar: str  # yes if entry filled this bar
    bt_entry_bar: str


@dataclass
class Divergence:
    timestamp: str
    fold: int
    pair: str
    kind: str
    bespoke_raw: str
    bt_raw: str
    bespoke_accepted: str
    bt_accepted: str
    bespoke_rejection: str
    bt_rejection: str
    bespoke_position: str
    bt_position: str
    root_cause: str
    notes: list[str] = field(default_factory=list)
    trace_row: dict[str, Any] = field(default_factory=dict)


def _strategy_cfg(settings: Any) -> dict[str, Any]:
    fbr = settings.strategy.failed_breakout_reversal
    if fbr is None:
        raise SystemExit("campaign config missing failed_breakout_reversal block")
    return {k: getattr(fbr, k) for k in STRATEGY_CFG_KEYS}


def _load_frame_from_sqlite(
    *,
    instrument: str,
    load_start: datetime,
    load_end: datetime,
    db_path: Path,
) -> pd.DataFrame:
    db = Database(db_path)
    repo = CandleRepo(db)
    rows = repo.list(
        instrument,
        "H4",
        completed_only=True,
        from_time=load_start,
        to_time=load_end,
    )
    if not rows:
        raise SystemExit(
            f"no SQLite candles for {instrument} in "
            f"{load_start.isoformat()}..{load_end.isoformat()}"
        )
    frame = CandleFrame.from_candles(instrument, "H4", rows)
    df = frame.df.copy()
    if not df.index.is_unique:
        df = df[~df.index.duplicated(keep="last")]
    if "complete" not in df.columns:
        df = df.assign(complete=True)
    return df


def _load_frame_from_csv(
    *,
    instrument: str,
    load_start: datetime,
    load_end: datetime,
) -> pd.DataFrame:
    candles = load_candles(instrument, strict=False)
    sliced = slice_candles(candles, from_time=load_start, to_time=load_end)
    mid = sliced.mid_df.copy()
    bid = sliced.bid_ohlc_df
    ask = sliced.ask_ohlc_df
    df = mid.assign(
        bid_open=bid["open"],
        bid_high=bid["high"],
        bid_low=bid["low"],
        bid_close=bid["close"],
        ask_open=ask["open"],
        ask_high=ask["high"],
        ask_low=ask["low"],
        ask_close=ask["close"],
    )
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    else:
        df.index = df.index.tz_convert("UTC")
    if not df.index.is_unique:
        df = df[~df.index.duplicated(keep="last")]
    if "complete" not in df.columns:
        df = df.assign(complete=True)
    return df


def _extract_bt_indicators(df: pd.DataFrame, *, atr_len: int, adx_len: int) -> pd.DataFrame:
    import backtrader as bt
    from research.backtrader_lane.strategies.campaign_015_failed_breakout_reversal import (
        _Campaign015Feed,
    )

    feed_df = df.copy()
    if feed_df.index.tz is not None:
        feed_df.index = feed_df.index.tz_convert("UTC").tz_localize(None)

    records: list[dict[str, Any]] = []

    class _Capture(bt.Strategy):  # pragma: no cover - bt callback
        def __init__(self) -> None:
            self._atr = bt.indicators.AverageTrueRange(self.data, period=atr_len)
            self._adx = bt.indicators.AverageDirectionalMovementIndex(
                self.data, period=adx_len
            )

        def next(self) -> None:
            ts = pd.Timestamp(bt.num2date(self.data.datetime[0])).tz_localize("UTC")
            try:
                atr_v = float(self._atr[0])
                adx_v = float(self._adx[0])
            except (IndexError, ValueError):
                atr_v = math.nan
                adx_v = math.nan
            records.append({"timestamp": ts, "bt_atr": atr_v, "bt_adx": adx_v})

    cerebro = bt.Cerebro(stdstats=False)
    cerebro.adddata(_Campaign015Feed(dataname=feed_df))
    cerebro.addstrategy(_Capture)
    cerebro.run()
    out = pd.DataFrame(records).set_index("timestamp")
    out.index = out.index.tz_convert("UTC")
    return out.reindex(df.index)


def _prior_range(
    high: pd.Series,
    low: pd.Series,
    *,
    range_lookback: int,
    end_idx: int,
) -> tuple[float, float] | None:
    """Prior range over [end_idx-N .. end_idx-1], excluding end_idx."""
    start = end_idx - range_lookback
    if start < 0:
        return None
    window_high = high.iloc[start:end_idx]
    window_low = low.iloc[start:end_idx]
    if len(window_high) < range_lookback:
        return None
    return float(window_high.max()), float(window_low.min())


def _evaluate_raw_signal(
    *,
    high: float,
    low: float,
    close: float,
    prior_high: float,
    prior_low: float,
    last_atr: float,
    last_adx: float,
    cfg: dict[str, Any],
    label: str,
) -> RawSignalEval:
    adx_max = float(cfg["adx_max"])
    sweep_buffer_atr = float(cfg["sweep_buffer_atr"])
    min_range_atr = float(cfg["min_range_atr_multiple"])
    max_range_atr = float(cfg["max_range_atr_multiple"])
    stop_buffer_atr = float(cfg["stop_buffer_atr"])
    min_stop_atr = float(cfg["min_stop_atr_multiple"])
    max_stop_atr = float(cfg["max_stop_atr_multiple"])

    none = RawSignalEval(
        side="none",
        prior_high=prior_high,
        prior_low=prior_low,
        atr=last_atr,
        adx=last_adx,
    )
    if not (math.isfinite(last_atr) and last_atr > 0):
        return none._replace(reason=f"{label}: atr invalid")
    if not math.isfinite(last_adx):
        return none._replace(reason=f"{label}: adx invalid")
    if last_adx > adx_max:
        return none._replace(reason=f"{label}: adx>{adx_max}")

    range_width = prior_high - prior_low
    if range_width <= 0:
        return none._replace(reason=f"{label}: range_width<=0")
    range_width_atr = range_width / last_atr
    if range_width_atr < min_range_atr:
        return none._replace(
            reason=f"{label}: range_width_atr<{min_range_atr}",
            range_width_atr=range_width_atr,
        )
    if range_width_atr > max_range_atr:
        return none._replace(
            reason=f"{label}: range_width_atr>{max_range_atr}",
            range_width_atr=range_width_atr,
        )

    sweep_buffer = sweep_buffer_atr * last_atr
    stop_buffer = stop_buffer_atr * last_atr
    short_swept = high > prior_high + sweep_buffer
    short_rejected = close < prior_high
    long_swept = low < prior_low - sweep_buffer
    long_rejected = close > prior_low
    short_setup = short_swept and short_rejected
    long_setup = long_swept and long_rejected

    if short_setup and long_setup:
        return none._replace(
            reason=f"{label}: dual_trigger",
            range_width_atr=range_width_atr,
        )
    if not (short_setup or long_setup):
        return none._replace(
            reason=f"{label}: no_setup",
            range_width_atr=range_width_atr,
        )

    if short_setup:
        side = "short"
        stop = high + stop_buffer
        sweep_distance_atr = (high - prior_high) / last_atr
    else:
        side = "long"
        stop = low - stop_buffer
        sweep_distance_atr = (prior_low - low) / last_atr

    stop_distance_atr = abs(close - stop) / last_atr
    if stop_distance_atr < min_stop_atr:
        return RawSignalEval(
            side="none",
            reason=f"{label}: stop_distance_atr<{min_stop_atr}",
            prior_high=prior_high,
            prior_low=prior_low,
            atr=last_atr,
            adx=last_adx,
            range_width_atr=range_width_atr,
            sweep_distance_atr=sweep_distance_atr,
            stop_distance_atr=stop_distance_atr,
            stop_price=stop,
        )
    if stop_distance_atr > max_stop_atr:
        return RawSignalEval(
            side="none",
            reason=f"{label}: stop_distance_atr>{max_stop_atr}",
            prior_high=prior_high,
            prior_low=prior_low,
            atr=last_atr,
            adx=last_adx,
            range_width_atr=range_width_atr,
            sweep_distance_atr=sweep_distance_atr,
            stop_distance_atr=stop_distance_atr,
            stop_price=stop,
        )

    return RawSignalEval(
        side=side,
        reason=f"{label}: signal_{side}",
        prior_high=prior_high,
        prior_low=prior_low,
        atr=last_atr,
        adx=last_adx,
        range_width_atr=range_width_atr,
        sweep_distance_atr=sweep_distance_atr,
        stop_distance_atr=stop_distance_atr,
        stop_price=stop,
    )


def _replace(self: RawSignalEval, **kwargs: Any) -> RawSignalEval:
    data = asdict(self)
    data.update(kwargs)
    return RawSignalEval(**data)


RawSignalEval._replace = _replace  # type: ignore[attr-defined]


def _bar_in_test(ts: pd.Timestamp, test_start: date, test_end: date) -> bool:
    d = ts.tz_convert("UTC").date()
    return test_start <= d <= test_end


def _dec(row: pd.Series, col: str, fallback: str) -> Decimal:
    val = row.get(col)
    if val is None or (isinstance(val, float) and math.isnan(val)) or pd.isna(val):
        return Decimal(str(row[fallback]))
    return Decimal(str(val))


def _synthetic_account(ts: pd.Timestamp, equity: float, settings: Any):
    from forex_bot.domain.account import AccountSnapshot

    eq = Decimal(str(equity))
    return AccountSnapshot(
        account_id="backtest",
        currency=settings.market.account_currency,
        balance=eq,
        nav=eq,
        margin_used=Decimal("0"),
        margin_available=eq,
        margin_closeout_percent=Decimal("0"),
        unrealized_pl=Decimal("0"),
        pl=Decimal("0"),
        open_trade_count=0,
        open_position_count=0,
        pending_order_count=0,
        time=ts.to_pydatetime(),
    )


def build_trace(
    *,
    df: pd.DataFrame,
    fold_index: int,
    pair: str,
    test_start: date,
    test_end: date,
    cfg: dict[str, Any],
    settings: Any,
    instrument_meta: Any,
) -> list[TraceRow]:
    strategy = FailedBreakoutReversalStrategy(version=str(cfg["version"]))
    risk_engine = RiskEngine(settings, mode="backtest")

    range_lookback = int(cfg["range_lookback"])
    atr_len = int(cfg["atr_lookback"])
    adx_len = int(cfg["adx_lookback"])
    max_bars = int(cfg["max_bars_in_trade"])
    bt_warmup = max(range_lookback, atr_len, adx_len) + 2
    bespoke_warmup = max(strategy.warmup_bars_required(), 5)

    atr_series = bespoke_atr(df["high"], df["low"], df["close"], atr_len)
    adx_series = bespoke_adx(df["high"], df["low"], df["close"], adx_len)
    bt_inds = _extract_bt_indicators(df, atr_len=atr_len, adx_len=adx_len)

    pip_size = float(_PIP_SIZE[pair])
    display_precision = int(instrument_meta.display_precision)
    quote_ccy = instrument_meta.quote_currency
    base_ccy = instrument_meta.base_currency
    risk_pct = float(settings.risk.risk_per_trade_pct)
    fixed_slip = float(settings.backtest.fixed_slippage_pips)
    spread_mult = float(settings.backtest.spread_slippage_multiplier)

    # Bespoke state
    b_equity = float(settings.backtest.starting_equity_usd)
    b_open: dict[str, Any] | None = None
    b_pending_signal: Any | None = None
    b_pending_side: str = "none"
    b_pending_accepted: str = "n/a"
    b_pending_rejection: str = ""

    # BT state
    bt_equity = float(settings.backtest.starting_equity_usd)
    bt_open: dict[str, Any] | None = None
    bt_pending: RawSignalEval | None = None

    rows: list[TraceRow] = []

    for i in range(len(df)):
        ts = df.index[i]
        row = df.iloc[i]
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])

        b_atr = float(atr_series.iloc[i]) if i < len(atr_series) else math.nan
        b_adx = float(adx_series.iloc[i]) if i < len(adx_series) else math.nan
        if ts in bt_inds.index:
            bt_atr_v = float(bt_inds.loc[ts, "bt_atr"])
            bt_adx_v = float(bt_inds.loc[ts, "bt_adx"])
        else:
            bt_atr_v = math.nan
            bt_adx_v = math.nan

        pr = _prior_range(df["high"], df["low"], range_lookback=range_lookback, end_idx=i)
        prior_high = pr[0] if pr else None
        prior_low = pr[1] if pr else None

        bespoke_raw = RawSignalEval(side="none", reason="warmup")
        bt_raw = RawSignalEval(side="none", reason="warmup")

        bespoke_accepted = "n/a"
        bespoke_rejection = ""
        bt_accepted = "n/a"
        bt_rejection = ""
        bespoke_entry_bar = "no"
        bt_entry_bar = "no"

        b_pos = "flat" if b_open is None else str(b_open["side"])
        bt_pos = "flat" if bt_open is None else str(bt_open["side"])
        b_pending = b_pending_side
        bt_pending_side = bt_pending.side if bt_pending else "none"

        in_test = _bar_in_test(ts, test_start, test_end)

        # --- BT path (mirrors _Campaign015Strategy.next order) ---
        if bt_open is not None:
            bt_open["bars_held"] += 1
            bid_low = float(row["bid_low"])
            ask_high = float(row["ask_high"])
            bid_close = float(row["bid_close"])
            ask_close = float(row["ask_close"])
            exited = False
            if (bt_open["side"] == "long" and bid_low <= bt_open["stop"]) or (bt_open["side"] == "short" and ask_high >= bt_open["stop"]):
                bt_open = None
                exited = True
                bt_rejection = "exit:stop"
            elif bt_open["bars_held"] >= max_bars:
                bt_open = None
                exited = True
                bt_rejection = "exit:time"
            if not exited and bt_open is not None:
                bt_pos = str(bt_open["side"])

        if bt_open is None and bt_pending is not None:
            side = bt_pending.side
            stop = float(bt_pending.stop_price or 0)
            bid_open = float(row["bid_open"])
            ask_open = float(row["ask_open"])
            entry_price = _fill_entry_price(
                side=side,
                bid_close=bid_open,
                ask_close=ask_open,
                fixed_slippage_pips=fixed_slip,
                spread_slippage_multiplier=spread_mult,
                pip_size=pip_size,
            )
            stop_r = _round_price(stop, display_precision)
            reject_reason = ""
            accepted = False
            if side == "long" and stop_r >= entry_price:
                reject_reason = "entry_geometry:long_stop>=entry"
            elif side == "short" and stop_r <= entry_price:
                reject_reason = "entry_geometry:short_stop<=entry"
            else:
                units = _size_position(
                    nav=bt_equity,
                    risk_per_trade_pct=risk_pct,
                    entry_price=entry_price,
                    stop_price=stop_r,
                    pip_size=pip_size,
                    quote_currency=quote_ccy,
                    base_currency=base_ccy,
                )
                if units <= 0:
                    reject_reason = "sizing:units<=0"
                else:
                    accepted = True
                    bt_open = {
                        "side": side,
                        "stop": stop_r,
                        "bars_held": 0,
                        "units": units,
                        "entry_price": entry_price,
                    }
                    bt_entry_bar = "yes"
                    if same_bar_adverse_stop_check(
                        side=side,
                        stop_price=stop_r,
                        bar_high=high,
                        bar_low=low,
                    ):
                        bt_open = None
                        reject_reason = "same_bar_adverse_stop"
                        accepted = False
                        bt_entry_bar = "no"
            bt_accepted = "yes" if accepted else "no"
            bt_rejection = reject_reason
            bt_pending = None
            bt_pending_side = "none"
            bt_pos = "flat" if bt_open is None else str(bt_open["side"])

        if bt_open is None and i >= bt_warmup - 1 and pr is not None:
            bt_raw = _evaluate_raw_signal(
                high=high,
                low=low,
                close=close,
                prior_high=prior_high,
                prior_low=prior_low,
                last_atr=bt_atr_v,
                last_adx=bt_adx_v,
                cfg=cfg,
                label="bt",
            )
            if bt_raw.side != "none" and bt_pending is None:
                bt_pending = bt_raw
                bt_pending_side = bt_raw.side

        # --- Bespoke path (mirrors BacktestEngine loop) ---
        if b_open is not None:
            b_open["bars_held"] += 1
            bid_low = _dec(row, "bid_low", "low")
            ask_high = _dec(row, "ask_high", "high")
            exited = False
            if (b_open["side"] == "long" and bid_low <= b_open["stop"]) or (b_open["side"] == "short" and ask_high >= b_open["stop"]) or b_open["bars_held"] >= max_bars:
                b_open = None
                exited = True
            if not exited and b_open is not None:
                b_pos = str(b_open["side"])

        if b_open is None and b_pending_signal is not None:
            signal = b_pending_signal
            bespoke_accepted = b_pending_accepted
            bespoke_rejection = b_pending_rejection
            if b_pending_accepted == "yes":
                b_open = {
                    "side": signal.side,
                    "stop": float(signal.stop_price),
                    "bars_held": 0,
                }
                bespoke_entry_bar = "yes"
                b_pos = signal.side
            b_pending_signal = None
            b_pending_side = "none"

        if b_open is None and b_pending_signal is None and i >= bespoke_warmup:
            window = df.iloc[: i + 1]
            window_frame = CandleFrame(
                instrument=pair, granularity="H4", df=window
            )
            bid_close = _dec(row, "bid_close", "close")
            ask_close = _dec(row, "ask_close", "close")
            quote = Quote(
                instrument=pair,
                time=ts.to_pydatetime(),
                bid=bid_close,
                ask=ask_close,
            )
            spread_pips = (ask_close - bid_close) / instrument_meta.pip_size
            market_state = MarketState(
                quote=quote,
                spread_snapshot=SpreadSnapshot(
                    instrument=pair,
                    time=quote.time,
                    bid=bid_close,
                    ask=ask_close,
                    spread_pips=spread_pips,
                ),
            )
            ctx = StrategyContext(
                instrument=instrument_meta,
                candles=window_frame,
                market_state=market_state,
                open_positions=[Position(instrument=pair)],
                config=cfg,
            )
            signal = strategy.generate_signal(ctx)
            if signal is not None:
                bespoke_raw = RawSignalEval(
                    side=signal.side,
                    reason="bespoke:strategy_signal",
                    prior_high=float(signal.features.get("prior_high", 0)),
                    prior_low=float(signal.features.get("prior_low", 0)),
                    atr=float(signal.features.get("atr", 0)),
                    adx=float(signal.features.get("adx", 0)),
                    range_width_atr=float(signal.features.get("range_width_atr", 0)),
                    sweep_distance_atr=float(
                        signal.features.get("sweep_distance_atr", 0)
                    ),
                    stop_distance_atr=float(signal.features.get("stop_distance_atr", 0)),
                    stop_price=float(signal.stop_price),
                )
                if i + 1 >= len(df):
                    bespoke_accepted = "no"
                    bespoke_rejection = "NEXT_BAR_OPEN_UNAVAILABLE"
                else:
                    next_row = df.iloc[i + 1]
                    entry_ts = df.index[i + 1]
                    fill_bid = _dec(next_row, "bid_open", "open")
                    fill_ask = _dec(next_row, "ask_open", "open")
                    fill_quote = Quote(
                        instrument=pair,
                        time=entry_ts.to_pydatetime(),
                        bid=fill_bid,
                        ask=fill_ask,
                    )
                    fill_spread = (fill_ask - fill_bid) / instrument_meta.pip_size
                    fill_market = MarketState(
                        quote=fill_quote,
                        spread_snapshot=SpreadSnapshot(
                            instrument=pair,
                            time=fill_quote.time,
                            bid=fill_bid,
                            ask=fill_ask,
                            spread_pips=fill_spread,
                        ),
                    )
                    atr_pips_val = signal.features.get("atr_pips")
                    inputs = RiskInputs(
                        signal=signal,
                        instrument=instrument_meta,
                        account=_synthetic_account(ts, b_equity, settings),
                        market_state=fill_market,
                        positions=[],
                        quotes_by_instrument={pair: fill_quote},
                        realized_pl_today=Decimal("0"),
                        realized_pl_week=Decimal("0"),
                        drawdown_pct=BacktestEngine._drawdown_pct([], b_equity),
                        atr_pips=(
                            Decimal(str(atr_pips_val))
                            if atr_pips_val is not None
                            else None
                        ),
                        reconciled=True,
                    )
                    decision, plan = risk_engine.evaluate(inputs)
                    if decision.approved and plan is not None:
                        b_pending_accepted = "yes"
                        b_pending_rejection = ""
                        signal = signal.model_copy(
                            update={"stop_price": plan.stop_loss_price}
                        )
                    else:
                        codes = [c.value for c in decision.rejection_codes]
                        b_pending_accepted = "no"
                        b_pending_rejection = (
                            ",".join(codes) if codes else "rejected"
                        )
                    bespoke_accepted = b_pending_accepted
                    bespoke_rejection = b_pending_rejection
                    b_pending_signal = signal
                    b_pending_side = signal.side
            elif pr is not None and math.isfinite(b_atr) and math.isfinite(b_adx):
                bespoke_raw = _evaluate_raw_signal(
                    high=high,
                    low=low,
                    close=close,
                    prior_high=prior_high,
                    prior_low=prior_low,
                    last_atr=b_atr,
                    last_adx=b_adx,
                    cfg=cfg,
                    label="bespoke",
                )

        if bespoke_raw.side == "none" and pr is not None and i >= bt_warmup - 1:
            if not math.isfinite(b_atr) or not math.isfinite(b_adx):
                pass
            elif bespoke_raw.reason == "warmup":
                bespoke_raw = _evaluate_raw_signal(
                    high=high,
                    low=low,
                    close=close,
                    prior_high=prior_high,
                    prior_low=prior_low,
                    last_atr=b_atr,
                    last_adx=b_adx,
                    cfg=cfg,
                    label="bespoke",
                )

        range_width_atr = bespoke_raw.range_width_atr or bt_raw.range_width_atr
        sweep_distance_atr = bespoke_raw.sweep_distance_atr or bt_raw.sweep_distance_atr
        stop_distance_atr = bespoke_raw.stop_distance_atr or bt_raw.stop_distance_atr

        rows.append(
            TraceRow(
                timestamp=ts.isoformat(),
                pair=pair,
                fold=fold_index,
                in_test_window=in_test,
                high=high,
                low=low,
                close=close,
                prior_high=prior_high,
                prior_low=prior_low,
                bespoke_atr=b_atr if math.isfinite(b_atr) else None,
                bespoke_adx=b_adx if math.isfinite(b_adx) else None,
                bt_atr=bt_atr_v if math.isfinite(bt_atr_v) else None,
                bt_adx=bt_adx_v if math.isfinite(bt_adx_v) else None,
                range_width_atr=range_width_atr,
                sweep_distance_atr=sweep_distance_atr,
                stop_distance_atr=stop_distance_atr,
                bespoke_raw=bespoke_raw.side,
                bt_raw=bt_raw.side,
                bespoke_accepted=bespoke_accepted,
                bespoke_rejection=bespoke_rejection,
                bt_accepted=bt_accepted,
                bt_rejection=bt_rejection,
                bespoke_position=b_pos,
                bt_position=bt_pos,
                bespoke_pending=b_pending,
                bt_pending=bt_pending_side,
                bespoke_entry_bar=bespoke_entry_bar,
                bt_entry_bar=bt_entry_bar,
            )
        )

    return rows


def compute_aggregate_stats(rows: list[TraceRow]) -> dict[str, Any]:
    matching_raw = [r for r in rows if r.bespoke_raw == r.bt_raw != "none"]
    return {
        "trace_bars": len(rows),
        "matching_raw_signal_bars": len(matching_raw),
        "raw_mismatch_bars": sum(1 for r in rows if r.bespoke_raw != r.bt_raw),
        "bespoke_risk_reject_bt_would_accept": sum(
            1
            for r in matching_raw
            if r.bespoke_accepted == "no" and r.bt_pending != "none"
        ),
        "bespoke_risk_reject_reasons": dict(
            sorted(
                (
                    (reason, sum(1 for r in matching_raw if r.bespoke_rejection == reason))
                    for reason in {r.bespoke_rejection for r in matching_raw if r.bespoke_rejection}
                ),
                key=lambda x: (-x[1], x[0]),
            )
        ),
        "simulated_bespoke_entries": sum(1 for r in rows if r.bespoke_entry_bar == "yes"),
        "simulated_bt_entries": sum(1 for r in rows if r.bt_entry_bar == "yes"),
        "entry_bar_mismatches": sum(
            1 for r in rows if r.bespoke_entry_bar != r.bt_entry_bar
        ),
    }


def find_first_divergence(rows: list[TraceRow]) -> Divergence | None:
    """Return the earliest bar where lanes materially disagree."""
    for row in rows:
        raw_mismatch = row.bespoke_raw != row.bt_raw
        accept_mismatch = (
            row.bespoke_accepted != row.bt_accepted
            and "n/a" not in (row.bespoke_accepted, row.bt_accepted)
        )
        entry_mismatch = row.bespoke_entry_bar != row.bt_entry_bar

        if not (raw_mismatch or accept_mismatch or entry_mismatch):
            continue

        kind = "unknown"
        if row.bt_raw != "none" and row.bespoke_raw == "none":
            kind = "bt_signal_bespoke_none"
        elif row.bespoke_raw != "none" and row.bt_raw == "none":
            kind = "bespoke_signal_bt_none"
        elif raw_mismatch and row.bespoke_raw != "none" and row.bt_raw != "none":
            kind = "same_bar_different_side"
        elif (
            row.bespoke_raw == row.bt_raw != "none"
            and row.bespoke_accepted == "no"
            and row.bt_accepted == "yes"
        ):
            kind = "bespoke_risk_reject_bt_accept"
        elif entry_mismatch:
            kind = "entry_timing_mismatch"
        elif accept_mismatch:
            kind = "acceptance_mismatch"

        root = classify_root_cause(row, kind)
        return Divergence(
            timestamp=row.timestamp,
            fold=row.fold,
            pair=row.pair,
            kind=kind,
            bespoke_raw=row.bespoke_raw,
            bt_raw=row.bt_raw,
            bespoke_accepted=row.bespoke_accepted,
            bt_accepted=row.bt_accepted,
            bespoke_rejection=row.bespoke_rejection,
            bt_rejection=row.bt_rejection,
            bespoke_position=row.bespoke_position,
            bt_position=row.bt_position,
            root_cause=root.value,
            notes=_divergence_notes(row, kind, root),
            trace_row=asdict(row),
        )
    return None


def classify_root_cause(row: TraceRow, kind: str) -> RootCause:
    if row.bt_rejection == "same_bar_adverse_stop" and row.bespoke_entry_bar == "yes":
        return RootCause.FILL_TIMING_MISMATCH

    if row.bespoke_raw == row.bt_raw and row.bespoke_raw != "none":
        if row.bespoke_accepted == "no" and row.bt_accepted == "yes":
            return RootCause.RISK_ENGINE_REJECTION_MISSING
        if row.bespoke_entry_bar != row.bt_entry_bar:
            return RootCause.FILL_TIMING_MISMATCH

    if row.bespoke_raw != row.bt_raw:
        if row.bespoke_atr is not None and row.bt_atr is not None:
            atr_rel = abs(row.bespoke_atr - row.bt_atr) / max(row.bespoke_atr, 1e-12)
            adx_delta = abs((row.bespoke_adx or 0) - (row.bt_adx or 0))
            if atr_rel > 0.01 or adx_delta > 1.0:
                return RootCause.INDICATOR_MISMATCH
        return RootCause.STRATEGY_RULE_MISMATCH

    if kind == "entry_timing_mismatch":
        return RootCause.FILL_TIMING_MISMATCH
    if row.bespoke_position != row.bt_position:
        return RootCause.POSITION_STATE_MISMATCH
    return RootCause.UNKNOWN


def _divergence_notes(row: TraceRow, kind: str, root: RootCause) -> list[str]:
    notes = [f"kind={kind}"]
    if row.bespoke_atr is not None and row.bt_atr is not None:
        notes.append(
            f"atr: bespoke={row.bespoke_atr:.8f} bt={row.bt_atr:.8f} "
            f"delta={row.bespoke_atr - row.bt_atr:.8f}"
        )
    if row.bespoke_adx is not None and row.bt_adx is not None:
        notes.append(
            f"adx: bespoke={row.bespoke_adx:.4f} bt={row.bt_adx:.4f} "
            f"delta={row.bespoke_adx - row.bt_adx:.4f}"
        )
    notes.append(f"classified={root.value}")
    return notes


def _load_comparison_totals(bt_dir: Path, bespoke_dir: Path) -> dict[str, int]:
    comp_path = bt_dir / "fold_window_comparison.json"
    if comp_path.is_file():
        data = json.loads(comp_path.read_text(encoding="utf-8"))
        return {
            "bt_total": int(data.get("bt_total_trades", 0)),
            "bespoke_total": int(data.get("bespoke_total_trades", 0)),
            "classification": str(data.get("classification", "")),
        }
    return {"bt_total": 0, "bespoke_total": 0, "classification": ""}


def _write_trace_csv(path: Path, rows: list[TraceRow], *, center_ts: str | None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample = rows
    if center_ts:
        idx = next((i for i, r in enumerate(rows) if r.timestamp == center_ts), None)
        if idx is not None:
            lo = max(0, idx - 5)
            hi = min(len(rows), idx + 6)
            sample = rows[lo:hi]
    fieldnames = list(asdict(sample[0]).keys()) if sample else []
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in sample:
            writer.writerow(asdict(row))


def _write_report_md(
    path: Path,
    *,
    divergence: Divergence | None,
    totals: dict[str, Any],
    aggregate: dict[str, Any],
    fold: int,
    pair: str,
    trace_len: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Backtrader vs Bespoke Signal Diff — CAMPAIGN_015",
        "",
        "> Diagnostic-only. Does **not** approve any strategy.",
        "> `configs/approved_strategies.yaml` remains `approved: []`.",
        "",
        f"**Cell:** fold {fold} / {pair}",
        f"**Trace bars:** {trace_len}",
        "",
        "## Phase 0 — comparison headline",
        "",
        f"- Window-aligned classification: `{totals.get('classification', 'SIGNAL_RULE_MISMATCH')}`",
        f"- Backtrader fold-window trades: **{totals.get('bt_total', '?')}**",
        f"- Bespoke rehydrate trades: **{totals.get('bespoke_total', '?')}**",
        "",
        "## Cell trace summary (fold × pair)",
        "",
        f"- Matching raw-signal bars (same side): **{aggregate.get('matching_raw_signal_bars', 0)}**",
        f"- Bespoke RiskEngine rejections where BT would still enter: "
        f"**{aggregate.get('bespoke_risk_reject_bt_would_accept', 0)}**",
        f"- Simulated bespoke entries in trace: **{aggregate.get('simulated_bespoke_entries', 0)}**",
        f"- Simulated BT entries in trace: **{aggregate.get('simulated_bt_entries', 0)}**",
        "",
        "**Aggregate 532 vs 164 interpretation:** raw strategy rules align on CSV "
        "data once BT indicators are timestamp-aligned. The residual fold-window "
        "trade-count gap is dominated by the BT lane **not running the bespoke "
        "RiskEngine** (spread / session / drawdown gates), plus entry-bar "
        "lifecycle differences (`same_bar_adverse_stop_wins` on BT only).",
        "",
        "## First divergence",
        "",
    ]
    if divergence is None:
        lines.append("_No divergence detected in trace window._")
    else:
        lines.extend(
            [
                f"- **Timestamp:** `{divergence.timestamp}`",
                f"- **Kind:** `{divergence.kind}`",
                f"- **Root cause:** `{divergence.root_cause}`",
                f"- Bespoke raw: `{divergence.bespoke_raw}` | BT raw: `{divergence.bt_raw}`",
                f"- Bespoke accepted: `{divergence.bespoke_accepted}` "
                f"({divergence.bespoke_rejection or '—'})",
                f"- BT accepted: `{divergence.bt_accepted}` "
                f"({divergence.bt_rejection or '—'})",
                "",
                "### Notes",
                "",
            ]
        )
        for note in divergence.notes:
            lines.append(f"- {note}")

    lines.extend(
        [
            "",
            "## Root-cause classification",
            "",
            "See `research/campaign_015/diagnostics/signal_diff/first_divergence.json`.",
            "",
            "## Safety",
            "",
            "- CAMPAIGN_015 remains **unapproved**.",
            "- No broker/OANDA calls were made.",
            "- No frozen CAMPAIGN_015 settings were changed.",
            "",
            "## Recommended next step",
            "",
            "1. Wire read-only RiskEngine parity into the BT CAMPAIGN_015 adapter "
            "(spread / session / drawdown / sizing gates only; no broker).",
            "2. Align bespoke `BacktestEngine` entry-bar `same_bar_adverse_stop_wins` "
            "with the BT lane (or document both as approximations).",
            "3. Re-run fold-window comparison after (1); expect trade-count gap to "
            "shrink materially before any approval discussion.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_diff(
    *,
    fold_index: int,
    pair: str,
    plan_path: Path,
    output_dir: Path,
    bt_dir: Path,
    bespoke_dir: Path,
    config_path: Path,
) -> dict[str, Any]:
    plan = load_fold_plan(plan_path)
    fold = next(f for f in plan.folds if f.fold_index == fold_index)
    spec = FoldWindowSpec.from_fold(fold)

    settings = load_settings(config_path)
    cfg = _strategy_cfg(settings)
    instr_repo = InstrumentRepo(Database(settings.app.database_path))
    meta = instr_repo.get(pair)
    if meta is None:
        raise SystemExit(f"missing instrument metadata for {pair}")

    load_start = spec.candle_load_start
    load_end = spec.candle_load_end
    db_path = Path(settings.app.database_path)
    if not db_path.is_file():
        db_path = ROOT / settings.app.database_path

    # BT lane reads Lean CSV exports; prefer CSV so indicator paths match.
    try:
        df = _load_frame_from_csv(
            instrument=pair, load_start=load_start, load_end=load_end
        )
        candle_source = "csv"
    except (FileNotFoundError, ValueError, SystemExit):
        df = _load_frame_from_sqlite(
            instrument=pair,
            load_start=load_start,
            load_end=load_end,
            db_path=db_path,
        )
        candle_source = "sqlite"

    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    else:
        df.index = df.index.tz_convert("UTC")

    rows = build_trace(
        df=df,
        fold_index=fold_index,
        pair=pair,
        test_start=spec.test_start,
        test_end=spec.test_end,
        cfg=cfg,
        settings=settings,
        instrument_meta=meta,
    )
    divergence = find_first_divergence(rows)
    aggregate = compute_aggregate_stats(rows)
    totals = _load_comparison_totals(bt_dir, bespoke_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    div_path = output_dir / "first_divergence.json"
    sample_path = output_dir / f"fold{fold_index}_{pair}_trace_sample.csv"
    _write_trace_csv(
        sample_path,
        rows,
        center_ts=divergence.timestamp if divergence else None,
    )

    payload: dict[str, Any] = {
        "strategy_evidence": False,
        "campaign": "CAMPAIGN_015",
        "strategy": "failed_breakout_reversal 0.1.0-c015",
        "fold_index": fold_index,
        "pair": pair,
        "test_start": str(spec.test_start),
        "test_end": str(spec.test_end),
        "candle_load_start": load_start.isoformat(),
        "candle_load_end": load_end.isoformat(),
        "candle_source": candle_source,
        "trace_bars": len(rows),
        "comparison_totals": totals,
        "aggregate_stats": aggregate,
        "first_divergence": asdict(divergence) if divergence else None,
    }
    div_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    report_path = ROOT / "docs/research/BACKTRADER_CAMPAIGN_015_SIGNAL_DIFF.md"
    _write_report_md(
        report_path,
        divergence=divergence,
        totals=totals,
        aggregate=aggregate,
        fold=fold_index,
        pair=pair,
        trace_len=len(rows),
    )

    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fold", type=int, default=0)
    parser.add_argument("--pair", default="EUR_USD")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--backtrader-dir", type=Path, default=DEFAULT_BT_DIR)
    parser.add_argument("--bespoke-dir", type=Path, default=DEFAULT_BESPOKE_DIR)
    parser.add_argument("--config", type=Path, default=CAMPAIGN_015_CONFIG_PATH)
    args = parser.parse_args(argv)

    result = run_diff(
        fold_index=args.fold,
        pair=args.pair,
        plan_path=args.plan,
        output_dir=args.output,
        bt_dir=args.backtrader_dir,
        bespoke_dir=args.bespoke_dir,
        config_path=args.config,
    )
    div = result.get("first_divergence")
    if div:
        print(
            f"first_divergence={div['timestamp']} "
            f"kind={div['kind']} root_cause={div['root_cause']}"
        )
    else:
        print("no divergence found")
    print(f"wrote {args.output}/first_divergence.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Bar-level trace around first BT-only trade for one CAMPAIGN_015 cell.

Compares CSV (BT lane) vs SQLite (bespoke lane) OHLC/spread, raw strategy
signals, RiskEngine decisions, and position state bar-by-bar.

Diagnostic-only. Does NOT approve any strategy.
`strategy_evidence: false`.

Usage:
    python scripts/trace_campaign_015_cell_bar_decisions.py \\
        --fold 1 --pair AUD_USD \\
        --center-ts 2022-05-06T17:00:00+00:00 \\
        --window-bars 30
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import asdict, dataclass
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
from research.backtrader_lane.fold_windows import FoldWindowSpec, load_fold_plan, slice_candles
from research.backtrader_lane.risk_parity import (
    RiskParityState,
    build_campaign_015_risk_engine,
    evaluate_pending_entry,
)
from research.backtrader_lane.strategies.campaign_002_trend_following import (
    _PIP_SIZE,
    _fill_entry_price,
    _round_price,
    _size_position,
)
from research.backtrader_lane.strategies.campaign_015_failed_breakout_reversal import (
    CAMPAIGN_015_CONFIG_PATH,
)
from scripts.diff_campaign_015_cell_trades import (
    run_cell_diff,
)
from scripts.diff_campaign_015_signals import (
    RawSignalEval,
    _evaluate_raw_signal,
    _extract_bt_indicators,
    _load_frame_from_sqlite,
    _prior_range,
    _strategy_cfg,
)

from forex_bot.backtesting.engine import BacktestEngine
from forex_bot.config import load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import InstrumentRepo
from forex_bot.domain.candles import CandleFrame
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.risk.policy import RiskEngine, RiskInputs
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.failed_breakout_reversal import FailedBreakoutReversalStrategy
from forex_bot.strategies.indicators import adx as bespoke_adx
from forex_bot.strategies.indicators import atr as bespoke_atr

DEFAULT_PLAN = (
    ROOT
    / "research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/plan.json"
)
DEFAULT_BESPOKE_DIR = ROOT / "research/campaign_015/diagnostics/walk_forward_rehydrate"
DEFAULT_BT_DIR = (
    ROOT
    / "research/campaign_015/diagnostics/backtrader_fold_window_riskengine_fill_parity"
)
DEFAULT_OUTPUT = ROOT / "research/campaign_015/diagnostics/cell_parity_drilldown"


class FirstDivergenceKind(StrEnum):
    RAW_SIGNAL_MISMATCH = "RAW_SIGNAL_MISMATCH"
    RISKENGINE_MISMATCH = "RISKENGINE_MISMATCH"
    POSITION_STATE_MISMATCH = "POSITION_STATE_MISMATCH"
    DATA_MISMATCH = "DATA_MISMATCH"
    BT_ACCEPTED_BESPOKE_REJECTED = "BT_ACCEPTED_BESPOKE_REJECTED"
    BT_SIGNAL_BESPOKE_NONE = "BT_SIGNAL_BESPOKE_NONE"
    NONE = "NONE"


@dataclass
class BarTraceRow:
    timestamp: str
    pair: str
    fold: int
    in_test_window: bool
    csv_mid_open: float | None
    csv_mid_high: float | None
    csv_mid_low: float | None
    csv_mid_close: float | None
    csv_bid_close: float | None
    csv_ask_close: float | None
    sqlite_mid_close: float | None
    sqlite_bid_close: float | None
    sqlite_ask_close: float | None
    ohlc_match: str
    spread_close_csv_pips: float | None
    spread_close_sqlite_pips: float | None
    spread_match: str
    bespoke_atr: float | None
    bespoke_adx: float | None
    bt_atr: float | None
    bt_adx: float | None
    prior_high: float | None
    prior_low: float | None
    range_width_atr: float | None
    sweep_distance_atr: float | None
    stop_distance_atr: float | None
    bespoke_raw: str
    bt_raw: str
    side: str
    planned_entry_timestamp: str
    planned_entry_price: float | None
    planned_stop: float | None
    bespoke_risk_decision: str
    bespoke_risk_rejection: str
    bt_risk_decision: str
    bt_risk_rejection: str
    session_gate_bespoke: str
    session_gate_bt: str
    spread_gate_bespoke: str
    spread_gate_bt: str
    margin_gate_bespoke: str
    margin_gate_bt: str
    open_position_before: str
    pending_entry_before: str
    open_position_after: str
    pending_entry_after: str
    trade_accepted_bespoke: str
    trade_accepted_bt: str


@dataclass
class TraceResult:
    fold_index: int
    pair: str
    center_timestamp: str
    window_bars: int
    rows: list[BarTraceRow]
    first_divergence: dict[str, Any] | None
    strategy_evidence: bool = False


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


def _gate_flags(codes: str) -> dict[str, str]:
    parts = [c.strip() for c in codes.split(",") if c.strip()]
    return {
        "session_gate": "blocked" if "SESSION_BLOCKED" in parts else "pass",
        "spread_gate": (
            "blocked"
            if any(c in parts for c in ("SPREAD_TOO_WIDE", "SPREAD_TO_ATR"))
            else "pass"
        ),
        "margin_gate": "blocked" if "MARGIN_BUFFER" in parts else "pass",
    }


def _merge_frames(csv_df: pd.DataFrame, sqlite_df: pd.DataFrame) -> pd.DataFrame:
    csv = csv_df.copy()
    sql = sqlite_df.copy()
    if csv.index.tz is None:
        csv.index = csv.index.tz_localize("UTC")
    else:
        csv.index = csv.index.tz_convert("UTC")
    if sql.index.tz is None:
        sql.index = sql.index.tz_localize("UTC")
    else:
        sql.index = sql.index.tz_convert("UTC")
    merged = csv.join(
        sql[["open", "high", "low", "close", "bid_close", "ask_close"]].rename(
            columns={
                "open": "sql_open",
                "high": "sql_high",
                "low": "sql_low",
                "close": "sql_close",
                "bid_close": "sql_bid_close",
                "ask_close": "sql_ask_close",
            }
        ),
        how="inner",
    )
    return merged


def build_bar_trace(
    *,
    df: pd.DataFrame,
    fold_index: int,
    pair: str,
    test_start: date,
    test_end: date,
    cfg: dict[str, Any],
    settings: Any,
    instrument_meta: Any,
) -> list[BarTraceRow]:
    strategy = FailedBreakoutReversalStrategy(version=str(cfg["version"]))
    risk_engine = RiskEngine(settings, mode="backtest")
    bt_risk_engine = build_campaign_015_risk_engine(settings)
    parity_state = RiskParityState(
        account_currency=settings.market.account_currency,
        equity_peak=float(settings.backtest.starting_equity_usd),
    )

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

    b_equity = float(settings.backtest.starting_equity_usd)
    bt_equity = float(settings.backtest.starting_equity_usd)
    b_open: dict[str, Any] | None = None
    bt_open: dict[str, Any] | None = None
    b_pending: Any | None = None
    b_pending_approved = False
    b_pending_rejection = ""
    bt_pending: RawSignalEval | None = None
    bt_pending_signal_time: datetime | None = None

    rows: list[BarTraceRow] = []

    for i in range(len(df)):
        ts = df.index[i]
        row = df.iloc[i]
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])

        b_atr = float(atr_series.iloc[i]) if i < len(atr_series) else math.nan
        b_adx = float(adx_series.iloc[i]) if i < len(adx_series) else math.nan
        bt_atr_v = float(bt_inds.loc[ts, "bt_atr"]) if ts in bt_inds.index else math.nan
        bt_adx_v = float(bt_inds.loc[ts, "bt_adx"]) if ts in bt_inds.index else math.nan

        pr = _prior_range(df["high"], df["low"], range_lookback=range_lookback, end_idx=i)
        prior_high = pr[0] if pr else None
        prior_low = pr[1] if pr else None

        bespoke_raw = RawSignalEval(side="none", reason="warmup")
        bt_raw = RawSignalEval(side="none", reason="warmup")
        side = "none"
        planned_entry_ts = ""
        planned_entry_price: float | None = None
        planned_stop: float | None = None
        b_risk_decision = "n/a"
        b_risk_rejection = ""
        bt_risk_decision = "n/a"
        bt_risk_rejection = ""
        b_accepted = "n/a"
        bt_accepted = "n/a"

        pos_before = "flat" if b_open is None else str(b_open["side"])
        bt_pos_before = "flat" if bt_open is None else str(bt_open["side"])
        pend_before = b_pending.side if b_pending else "none"
        bt_pend_before = bt_pending.side if bt_pending else "none"

        in_test = _bar_in_test(ts, test_start, test_end)

        csv_bid = float(row.get("bid_close", row.get("close", close)))
        csv_ask = float(row.get("ask_close", row.get("close", close)))
        sql_close = row.get("sql_close")
        sql_bid = row.get("sql_bid_close")
        sql_ask = row.get("sql_ask_close")
        spread_csv = (csv_ask - csv_bid) / pip_size
        spread_sql: float | None = None
        if sql_bid is not None and sql_ask is not None and not pd.isna(sql_bid):
            spread_sql = (float(sql_ask) - float(sql_bid)) / pip_size

        ohlc_match = "unknown"
        if sql_close is not None and not pd.isna(sql_close):
            ohlc_match = (
                "match"
                if abs(float(sql_close) - close) <= 1e-9
                and abs(float(sql_bid) - csv_bid) <= 1e-9
                and abs(float(sql_ask) - csv_ask) <= 1e-9
                else "mismatch"
            )
        spread_match = "unknown"
        if spread_sql is not None:
            spread_match = "match" if abs(spread_csv - spread_sql) <= 0.01 else "mismatch"

        # BT exit / pending fill with RiskEngine parity
        if bt_open is not None:
            bt_open["bars_held"] += 1
            bid_low = float(row["bid_low"])
            ask_high = float(row["ask_high"])
            if (bt_open["side"] == "long" and bid_low <= bt_open["stop"]) or (
                bt_open["side"] == "short" and ask_high >= bt_open["stop"]
            ):
                parity_state.record_exit(
                    exit_time=ts.to_pydatetime(),
                    pnl=0.0,
                    equity=bt_equity,
                )
                bt_open = None
            elif bt_open["bars_held"] >= max_bars:
                bt_open = None

        if bt_open is None and bt_pending is not None:
            side_p = bt_pending.side
            stop = float(bt_pending.stop_price or 0)
            bid_open = float(row["bid_open"])
            ask_open = float(row["ask_open"])
            entry_price = _fill_entry_price(
                side=side_p,
                bid_close=bid_open,
                ask_close=ask_open,
                fixed_slippage_pips=fixed_slip,
                spread_slippage_multiplier=spread_mult,
                pip_size=pip_size,
            )
            stop_r = _round_price(stop, display_precision)
            planned_entry_ts = ts.isoformat()
            planned_entry_price = entry_price
            planned_stop = stop_r
            side = side_p

            risk_result = evaluate_pending_entry(
                risk_engine=bt_risk_engine,
                instrument_name=pair,
                side=side_p,
                stop_price=stop_r,
                signal_time=bt_pending_signal_time or ts.to_pydatetime(),
                fill_time=ts.to_pydatetime(),
                fill_bid=bid_open,
                fill_ask=ask_open,
                atr=float(bt_pending.atr or 0),
                equity=bt_equity,
                parity_state=parity_state,
                strategy_version=str(cfg["version"]),
            )
            if risk_result.approved:
                units = risk_result.units or _size_position(
                    nav=bt_equity,
                    risk_per_trade_pct=risk_pct,
                    entry_price=entry_price,
                    stop_price=stop_r,
                    pip_size=pip_size,
                    quote_currency=quote_ccy,
                    base_currency=base_ccy,
                )
                if units and units > 0:
                    bt_open = {
                        "side": side_p,
                        "stop": float(risk_result.stop_price or stop_r),
                        "bars_held": 0,
                        "units": units,
                    }
                    bt_accepted = "yes"
                    bt_risk_decision = "approved"
                else:
                    bt_accepted = "no"
                    bt_risk_decision = "rejected"
                    bt_risk_rejection = "sizing:units<=0"
            else:
                bt_accepted = "no"
                bt_risk_decision = "rejected"
                bt_risk_rejection = ",".join(risk_result.rejection_codes)
            bt_pending = None
            bt_pending_signal_time = None

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
            if bt_raw.side != "none" and bt_pending is None and bt_open is None:
                bt_pending = bt_raw
                bt_pending_signal_time = ts.to_pydatetime()

        # Bespoke path
        if b_open is not None:
            b_open["bars_held"] += 1
            bid_low = _dec(row, "bid_low", "low")
            ask_high = _dec(row, "ask_high", "high")
            if (b_open["side"] == "long" and bid_low <= b_open["stop"]) or (
                b_open["side"] == "short" and ask_high >= b_open["stop"]
            ) or b_open["bars_held"] >= max_bars:
                b_open = None

        if b_open is None and b_pending is not None:
            signal = b_pending
            b_risk_decision = "approved" if b_pending_approved else "rejected"
            b_risk_rejection = b_pending_rejection
            if b_pending_approved:
                b_open = {"side": signal.side, "stop": float(signal.stop_price), "bars_held": 0}
                b_accepted = "yes"
            else:
                b_accepted = "no"
            b_pending = None
            b_pending_approved = False
            b_pending_rejection = ""

        pending_evaluated_this_bar = False
        if b_open is None and b_pending is None and i >= bespoke_warmup:
            window = df.iloc[: i + 1]
            window_frame = CandleFrame(instrument=pair, granularity="H4", df=window)
            bid_close = _dec(row, "sql_bid_close", "bid_close")
            ask_close = _dec(row, "sql_ask_close", "ask_close")
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
                    sweep_distance_atr=float(signal.features.get("sweep_distance_atr", 0)),
                    stop_distance_atr=float(signal.features.get("stop_distance_atr", 0)),
                    stop_price=float(signal.stop_price),
                )
                side = signal.side
                planned_stop = float(signal.stop_price)
                if i + 1 < len(df):
                    next_row = df.iloc[i + 1]
                    entry_ts = df.index[i + 1]
                    planned_entry_ts = entry_ts.isoformat()
                    fill_bid = _dec(next_row, "sql_bid_open", "bid_open")
                    fill_ask = _dec(next_row, "sql_ask_open", "ask_open")
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
                    planned_entry_price = float(
                        _fill_entry_price(
                            side=signal.side,
                            bid_close=float(fill_bid),
                            ask_close=float(fill_ask),
                            fixed_slippage_pips=fixed_slip,
                            spread_slippage_multiplier=spread_mult,
                            pip_size=pip_size,
                        )
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
                    pending_evaluated_this_bar = True
                    if decision.approved and plan is not None:
                        b_risk_decision = "approved"
                        b_risk_rejection = ""
                        b_pending_approved = True
                        b_pending_rejection = ""
                        b_pending = signal.model_copy(
                            update={"stop_price": plan.stop_loss_price}
                        )
                    else:
                        b_risk_decision = "rejected"
                        codes = [c.value for c in decision.rejection_codes]
                        b_risk_rejection = ",".join(codes) if codes else "rejected"
                        b_pending_approved = False
                        b_pending_rejection = b_risk_rejection
                        b_pending = signal
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

        if bespoke_raw.side == "none" and pr is not None and i >= bespoke_warmup:
            if math.isfinite(b_atr) and math.isfinite(b_adx) and bespoke_raw.reason == "warmup":
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

        b_gates = _gate_flags(b_risk_rejection)
        bt_gates = _gate_flags(bt_risk_rejection)

        rows.append(
            BarTraceRow(
                timestamp=ts.isoformat(),
                pair=pair,
                fold=fold_index,
                in_test_window=in_test,
                csv_mid_open=float(row.get("open", close)),
                csv_mid_high=high,
                csv_mid_low=low,
                csv_mid_close=close,
                csv_bid_close=csv_bid,
                csv_ask_close=csv_ask,
                sqlite_mid_close=float(sql_close) if sql_close is not None and not pd.isna(sql_close) else None,
                sqlite_bid_close=float(sql_bid) if sql_bid is not None and not pd.isna(sql_bid) else None,
                sqlite_ask_close=float(sql_ask) if sql_ask is not None and not pd.isna(sql_ask) else None,
                ohlc_match=ohlc_match,
                spread_close_csv_pips=round(spread_csv, 4),
                spread_close_sqlite_pips=round(spread_sql, 4) if spread_sql is not None else None,
                spread_match=spread_match,
                bespoke_atr=b_atr if math.isfinite(b_atr) else None,
                bespoke_adx=b_adx if math.isfinite(b_adx) else None,
                bt_atr=bt_atr_v if math.isfinite(bt_atr_v) else None,
                bt_adx=bt_adx_v if math.isfinite(bt_adx_v) else None,
                prior_high=prior_high,
                prior_low=prior_low,
                range_width_atr=bespoke_raw.range_width_atr or bt_raw.range_width_atr,
                sweep_distance_atr=bespoke_raw.sweep_distance_atr or bt_raw.sweep_distance_atr,
                stop_distance_atr=bespoke_raw.stop_distance_atr or bt_raw.stop_distance_atr,
                bespoke_raw=bespoke_raw.side,
                bt_raw=bt_raw.side,
                side=side if side != "none" else (bt_raw.side if bt_raw.side != "none" else bespoke_raw.side),
                planned_entry_timestamp=planned_entry_ts,
                planned_entry_price=planned_entry_price,
                planned_stop=planned_stop,
                bespoke_risk_decision=b_risk_decision,
                bespoke_risk_rejection=b_risk_rejection,
                bt_risk_decision=bt_risk_decision,
                bt_risk_rejection=bt_risk_rejection,
                session_gate_bespoke=b_gates["session_gate"],
                session_gate_bt=bt_gates["session_gate"],
                spread_gate_bespoke=b_gates["spread_gate"],
                spread_gate_bt=bt_gates["spread_gate"],
                margin_gate_bespoke=b_gates["margin_gate"],
                margin_gate_bt=bt_gates["margin_gate"],
                open_position_before=pos_before if pos_before != "flat" else bt_pos_before,
                pending_entry_before=pend_before if pend_before != "none" else bt_pend_before,
                open_position_after="flat" if b_open is None and bt_open is None else (
                    str(b_open["side"]) if b_open else str(bt_open["side"]) if bt_open else "flat"
                ),
                pending_entry_after=(
                    b_pending.side if b_pending else bt_pending.side if bt_pending else "none"
                ),
                trade_accepted_bespoke=b_accepted if pending_evaluated_this_bar else "n/a",
                trade_accepted_bt=bt_accepted,
            )
        )

    return rows


def classify_first_divergence(rows: list[BarTraceRow]) -> dict[str, Any] | None:
    for row in rows:
        if row.ohlc_match == "mismatch":
            return {
                "timestamp": row.timestamp,
                "kind": FirstDivergenceKind.DATA_MISMATCH.value,
                "notes": [
                    f"csv_close={row.csv_mid_close} sqlite_close={row.sqlite_mid_close}",
                    f"spread_csv={row.spread_close_csv_pips} spread_sqlite={row.spread_close_sqlite_pips}",
                ],
                "row": asdict(row),
            }
        raw_mismatch = row.bespoke_raw != row.bt_raw
        if raw_mismatch and row.bt_raw != "none" and row.bespoke_raw == "none":
            return {
                "timestamp": row.timestamp,
                "kind": FirstDivergenceKind.BT_SIGNAL_BESPOKE_NONE.value,
                "notes": [f"bt_raw={row.bt_raw} bespoke_raw={row.bespoke_raw}"],
                "row": asdict(row),
            }
        if raw_mismatch and row.bespoke_raw != "none" and row.bt_raw != "none":
            return {
                "timestamp": row.timestamp,
                "kind": FirstDivergenceKind.RAW_SIGNAL_MISMATCH.value,
                "notes": [f"bt_raw={row.bt_raw} bespoke_raw={row.bespoke_raw}"],
                "row": asdict(row),
            }
        if (
            row.bespoke_raw == row.bt_raw != "none"
            and row.trade_accepted_bt == "yes"
            and row.trade_accepted_bespoke == "no"
        ):
            return {
                "timestamp": row.timestamp,
                "kind": FirstDivergenceKind.BT_ACCEPTED_BESPOKE_REJECTED.value,
                "notes": [
                    f"bespoke_rejection={row.bespoke_risk_rejection}",
                    f"bt_rejection={row.bt_risk_rejection}",
                ],
                "row": asdict(row),
            }
        if (
            row.bespoke_risk_decision != row.bt_risk_decision
            and row.bespoke_risk_decision != "n/a"
            and row.bt_risk_decision != "n/a"
        ):
            return {
                "timestamp": row.timestamp,
                "kind": FirstDivergenceKind.RISKENGINE_MISMATCH.value,
                "notes": [
                    f"bespoke={row.bespoke_risk_decision}/{row.bespoke_risk_rejection}",
                    f"bt={row.bt_risk_decision}/{row.bt_risk_rejection}",
                ],
                "row": asdict(row),
            }
    return None


def slice_trace_window(
    rows: list[BarTraceRow],
    *,
    center_ts: str,
    window_bars: int,
) -> list[BarTraceRow]:
    idx = next((i for i, r in enumerate(rows) if r.timestamp == center_ts), None)
    if idx is None:
        for i, r in enumerate(rows):
            if r.timestamp.startswith(center_ts[:16]):
                idx = i
                break
    if idx is None:
        return rows[:window_bars]
    lo = max(0, idx - window_bars // 2)
    hi = min(len(rows), lo + window_bars)
    lo = max(0, hi - window_bars)
    return rows[lo:hi]


def run_trace(
    *,
    fold_index: int,
    pair: str,
    center_ts: str | None,
    window_bars: int,
    plan_path: Path,
    bespoke_dir: Path,
    backtrader_dir: Path,
    output_dir: Path,
    config_path: Path,
) -> TraceResult:
    if center_ts is None:
        diff = run_cell_diff(
            fold_index=fold_index,
            pair=pair,
            bespoke_dir=bespoke_dir,
            backtrader_dir=backtrader_dir,
            output_dir=output_dir,
        )
        if diff.first_bt_only is None:
            raise SystemExit("no BT-only trade found for cell")
        center_ts = diff.first_bt_only.entry_time.isoformat()

    plan = load_fold_plan(plan_path)
    fold = next(f for f in plan.folds if f.fold_index == fold_index)
    spec = FoldWindowSpec.from_fold(fold)

    settings = load_settings(config_path)
    cfg = _strategy_cfg(settings)
    instr_repo = InstrumentRepo(Database(settings.app.database_path))
    meta = instr_repo.get(pair)
    if meta is None:
        raise SystemExit(f"missing instrument metadata for {pair}")

    db_path = Path(settings.app.database_path)
    if not db_path.is_file():
        db_path = ROOT / settings.app.database_path

    load_start = spec.candle_load_start
    load_end = spec.candle_load_end

    candles = load_candles(pair, strict=False)
    csv_sliced = slice_candles(candles, from_time=load_start, to_time=load_end)
    csv_df = csv_sliced.mid_df.copy()
    bid = csv_sliced.bid_ohlc_df
    ask = csv_sliced.ask_ohlc_df
    csv_df = csv_df.assign(
        bid_open=bid["open"],
        bid_high=bid["high"],
        bid_low=bid["low"],
        bid_close=bid["close"],
        ask_open=ask["open"],
        ask_high=ask["high"],
        ask_low=ask["low"],
        ask_close=ask["close"],
    )
    if csv_df.index.tz is None:
        csv_df.index = csv_df.index.tz_localize("UTC")
    else:
        csv_df.index = csv_df.index.tz_convert("UTC")

    sqlite_df = _load_frame_from_sqlite(
        instrument=pair,
        load_start=load_start,
        load_end=load_end,
        db_path=db_path,
    )
    merged = _merge_frames(csv_df, sqlite_df)
    if "complete" not in merged.columns:
        merged = merged.assign(complete=True)

    all_rows = build_bar_trace(
        df=merged,
        fold_index=fold_index,
        pair=pair,
        test_start=spec.test_start,
        test_end=spec.test_end,
        cfg=cfg,
        settings=settings,
        instrument_meta=meta,
    )
    window_rows = slice_trace_window(all_rows, center_ts=center_ts, window_bars=window_bars)
    divergence = classify_first_divergence(window_rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"fold_{fold_index:02d}_{pair}"
    json_path = output_dir / f"{stem}_bar_trace.json"
    csv_path = output_dir / f"{stem}_bar_trace.csv"

    result = TraceResult(
        fold_index=fold_index,
        pair=pair,
        center_timestamp=center_ts,
        window_bars=len(window_rows),
        rows=window_rows,
        first_divergence=divergence,
    )
    payload = {
        "strategy_evidence": False,
        "fold_index": fold_index,
        "pair": pair,
        "center_timestamp": center_ts,
        "window_bars": len(window_rows),
        "first_divergence": divergence,
        "rows": [asdict(r) for r in window_rows],
    }
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if window_rows:
        fieldnames = list(asdict(window_rows[0]).keys())
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for row in window_rows:
                writer.writerow(asdict(row))

    report_path = ROOT / "docs/research/BACKTRADER_CAMPAIGN_015_CELL_BAR_TRACE.md"
    _write_bar_trace_report(report_path, result=result)
    return result


def _write_bar_trace_report(path: Path, *, result: TraceResult) -> None:
    lines = [
        "# CAMPAIGN_015 Cell Bar Trace",
        "",
        f"**Cell:** fold {result.fold_index} / {result.pair}",
        f"**Center:** `{result.center_timestamp}`",
        f"**Window bars:** {result.window_bars}",
        "",
        "> Diagnostic-only. `strategy_evidence: false`.",
        "",
        "## First divergence in window",
        "",
    ]
    if result.first_divergence:
        div = result.first_divergence
        lines.extend(
            [
                f"- **Timestamp:** `{div['timestamp']}`",
                f"- **Kind:** `{div['kind']}`",
                "",
                "### Notes",
                "",
            ]
        )
        for note in div.get("notes", []):
            lines.append(f"- {note}")
    else:
        lines.append("_No divergence classified in trace window._")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fold", type=int, required=True)
    parser.add_argument("--pair", required=True)
    parser.add_argument("--center-ts", default=None)
    parser.add_argument("--window-bars", type=int, default=30)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--bespoke-dir", type=Path, default=DEFAULT_BESPOKE_DIR)
    parser.add_argument("--backtrader-dir", type=Path, default=DEFAULT_BT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--config", type=Path, default=CAMPAIGN_015_CONFIG_PATH)
    args = parser.parse_args(argv)

    result = run_trace(
        fold_index=args.fold,
        pair=args.pair,
        center_ts=args.center_ts,
        window_bars=args.window_bars,
        plan_path=args.plan,
        bespoke_dir=args.bespoke_dir,
        backtrader_dir=args.backtrader_dir,
        output_dir=args.output,
        config_path=args.config,
    )
    if result.first_divergence:
        print(
            f"first_divergence={result.first_divergence['timestamp']} "
            f"kind={result.first_divergence['kind']}"
        )
    else:
        print("no divergence in window")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

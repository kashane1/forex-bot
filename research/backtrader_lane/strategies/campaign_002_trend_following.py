"""Backtrader port of CAMPAIGN_002 H4 `trend_following 0.1.0-baseline-frozen`.

Mirrors the frozen rules documented in
`docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md` §3–§7 and reproduced
in `research/parity_verifier/rules.py`. The port:

- Computes indicators via Backtrader's `bt.indicators` where the
  recurrences match the bespoke definitions (`ExponentialMovingAverage`
  for EMA, `AverageTrueRange` with Wilder's smoothing for ATR).
- Computes Donchian-20 from the prior 20 *completed* bars (excluding
  the current bar) via a manual rolling window. Backtrader's stock
  `Highest`/`Lowest` includes the current bar — that would be a
  look-ahead bug for this campaign.
- Bypasses Backtrader's broker for fills. The strategy maintains its
  own one-position state machine and computes entry/exit prices and
  sizing exactly per the mapping spec (bid/ask-aware fills at the
  signal bar's close, mid-close-anchored initial stop, 0.25%-of-equity
  whole-units sizing).
- Emits one `BacktraderTrade` per closed position.

This strategy adapter is **frozen**: parameters are read-only constants
from `lean_parity_config.json` and the mapping spec; nothing in this
file is tunable. The adapter cannot approve a strategy. CAMPAIGN_002
remains REJECT.

`strategy_evidence: false`.
"""

from __future__ import annotations

import json
from collections import deque
from datetime import UTC
from decimal import Decimal
from pathlib import Path
from typing import Any

import backtrader as bt
import pandas as pd

from research.backtrader_lane.data_adapter import CandleAdapterResult
from research.backtrader_lane.runner import (
    BacktraderTrade,
    CampaignAdapter,
    PairRunResult,
    register_campaign,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
LEAN_PARITY_CONFIG_PATH = (
    REPO_ROOT / "research" / "lean_parity" / "lean_parity_config.json"
)


def _load_lean_parity_config() -> dict[str, Any]:
    return json.loads(LEAN_PARITY_CONFIG_PATH.read_text(encoding="utf-8"))


# CAMPAIGN_002 H4 universe — re-derived from the FX-major convention so
# this adapter does not import `forex_bot.domain.instruments`.
_PIP_SIZE = {
    "EUR_USD": 0.0001,
    "GBP_USD": 0.0001,
    "USD_JPY": 0.01,
    "AUD_USD": 0.0001,
    "USD_CAD": 0.0001,
    "USD_CHF": 0.0001,
    "NZD_USD": 0.0001,
    "TEST_PAIR": 0.0001,  # fixtures
}
_QUOTE_CCY = {
    "EUR_USD": "USD",
    "GBP_USD": "USD",
    "USD_JPY": "JPY",
    "AUD_USD": "USD",
    "USD_CAD": "CAD",
    "USD_CHF": "CHF",
    "NZD_USD": "USD",
    "TEST_PAIR": "USD",
}
_BASE_CCY = {
    "EUR_USD": "EUR",
    "GBP_USD": "GBP",
    "USD_JPY": "USD",
    "AUD_USD": "AUD",
    "USD_CAD": "USD",
    "USD_CHF": "USD",
    "NZD_USD": "NZD",
    "TEST_PAIR": "TST",
}
_DISPLAY_PRECISION = {
    "EUR_USD": 5,
    "GBP_USD": 5,
    "USD_JPY": 3,
    "AUD_USD": 5,
    "USD_CAD": 5,
    "USD_CHF": 5,
    "NZD_USD": 5,
    "TEST_PAIR": 5,
}


def _round_price(price: float, display_precision: int) -> float:
    """Match `forex_bot.domain.instruments.Instrument.round_price`.

    Convert via str, ``quantize`` with ``ROUND_HALF_UP``, then back to
    float. The verifier's matching helper documents this in detail."""

    quant = Decimal(1).scaleb(-display_precision)
    return float(Decimal(str(price)).quantize(quant, rounding="ROUND_HALF_UP"))


def _fill_entry_price(
    *,
    side: str,
    bid_close: float,
    ask_close: float,
    fixed_slippage_pips: float,
    spread_slippage_multiplier: float,
    pip_size: float,
) -> float:
    spread_pips = (ask_close - bid_close) / pip_size
    slip_pips = max(fixed_slippage_pips, spread_pips * spread_slippage_multiplier)
    slip = slip_pips * pip_size
    if side == "long":
        return ask_close + slip
    return bid_close - slip


def _size_position(
    *,
    nav: float,
    risk_per_trade_pct: float,
    entry_price: float,
    stop_price: float,
    pip_size: float,
    quote_currency: str,
    base_currency: str,
) -> int:
    risk_amount = nav * risk_per_trade_pct / 100.0
    stop_distance_pips = abs(entry_price - stop_price) / pip_size
    if stop_distance_pips <= 0:
        return 0
    if quote_currency == "USD":
        pip_value_home = pip_size
    elif base_currency == "USD":
        pip_value_home = pip_size / entry_price
    else:
        raise ValueError(
            f"_size_position only supports USD-quote or USD-base pairs; "
            f"got base={base_currency} quote={quote_currency}"
        )
    raw = risk_amount / (stop_distance_pips * pip_value_home)
    return int(raw)  # floor to whole units


def _trade_pnl(
    *,
    side: str,
    entry_price: float,
    exit_price: float,
    units: int,
    quote_currency: str,
    base_currency: str,
) -> float:
    diff = (exit_price - entry_price) if side == "long" else (entry_price - exit_price)
    gross_quote = diff * units
    if quote_currency == "USD":
        return gross_quote
    if base_currency == "USD":
        return gross_quote / exit_price
    raise ValueError(
        f"_trade_pnl only supports USD-quote or USD-base pairs; got base={base_currency} quote={quote_currency}"
    )


class _Campaign002Feed(bt.feeds.PandasData):
    """A PandasData feed that carries bid/ask OHLC on extra lines.

    Backtrader's `PandasData` exposes columns by name through the
    `lines` mechanism. We add the four bid + four ask OHLC components
    we need for the fill model.
    """

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
    """Convenience — Backtrader's `len(self)` already returns the 1-based
    bar count, but a wrapped accessor keeps callers readable."""

    return len(strategy)


def run_campaign_002_pair(
    candles: CandleAdapterResult,
    starting_equity_usd: float,
    *,
    lean_parity_config_path: Path = LEAN_PARITY_CONFIG_PATH,
) -> PairRunResult:
    """Drive one instrument through the CAMPAIGN_002 trend_following port."""

    cfg = json.loads(lean_parity_config_path.read_text(encoding="utf-8"))
    strategy_cfg = cfg["strategy"]
    cost_cfg = cfg["cost_model"]
    sizing_cfg = cfg["sizing"]

    ema_fast = int(strategy_cfg["ema_fast"])
    ema_slow = int(strategy_cfg["ema_slow"])
    donchian_lookback = int(strategy_cfg["donchian_lookback"])
    atr_lookback = int(strategy_cfg["atr_lookback"])
    atr_stop_multiple = float(strategy_cfg["atr_stop_multiple"])
    trailing_stop_atr_multiple = float(strategy_cfg["trailing_stop_atr_multiple"])
    max_bars_in_trade = int(strategy_cfg["max_bars_in_trade"])
    min_atr_pips_by_pair = strategy_cfg.get("min_atr_pips") or {}
    fixed_slippage_pips = float(cost_cfg["fixed_slippage_pips"])
    spread_slippage_multiplier = float(cost_cfg["spread_slippage_multiplier"])
    risk_per_trade_pct = float(sizing_cfg["risk_per_trade_pct"])

    instrument = candles.instrument
    pip_size = _PIP_SIZE.get(instrument)
    quote_ccy = _QUOTE_CCY.get(instrument)
    base_ccy = _BASE_CCY.get(instrument)
    display_precision = _DISPLAY_PRECISION.get(instrument)
    if pip_size is None or quote_ccy is None or base_ccy is None or display_precision is None:
        raise KeyError(
            f"{instrument!r} not in the CAMPAIGN_002 / fixture universe; "
            f"known: {sorted(_PIP_SIZE.keys())}"
        )
    min_atr_pips_for_pair = float(min_atr_pips_by_pair.get(instrument, 0.0))

    # Combined dataframe so PandasData has every line it needs.
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
    n_bars = len(df)

    recorded: list[BacktraderTrade] = []
    nav = {"value": float(starting_equity_usd)}

    # Backtrader strategy: mirror the bespoke per-bar event loop exactly
    # (exits first, then entry on the same bar if flat). Use bt.indicators
    # for EMA/ATR; manual deque for prior-bars Donchian.
    class _Campaign002Strategy(bt.Strategy):  # pragma: no cover - bt callbacks
        params = (
            ("ema_fast_len", ema_fast),
            ("ema_slow_len", ema_slow),
            ("atr_len", atr_lookback),
            ("donchian_len", donchian_lookback),
        )

        def __init__(self) -> None:
            self._ema_fast = bt.indicators.ExponentialMovingAverage(
                self.data.close, period=self.p.ema_fast_len
            )
            self._ema_slow = bt.indicators.ExponentialMovingAverage(
                self.data.close, period=self.p.ema_slow_len
            )
            self._atr = bt.indicators.AverageTrueRange(self.data, period=self.p.atr_len)

            # Prior-bars Donchian: a deque of the last donchian_len highs / lows
            # *that have already completed*. We push the just-seen high/low at
            # the END of each next() call (after evaluating signals), so when
            # next() reads `_dch_high()` for bar t, the deque holds bars
            # [t-donchian_len .. t-1].
            self._dch_highs: deque[float] = deque(maxlen=self.p.donchian_len)
            self._dch_lows: deque[float] = deque(maxlen=self.p.donchian_len)

            self._in_position: bool = False
            self._side: str = "flat"
            self._entry_time: pd.Timestamp | None = None
            self._entry_price: float = 0.0
            self._stop_price: float = 0.0
            self._initial_stop_price: float = 0.0
            self._has_trailed: bool = False
            self._bars_held: int = 0
            self._units: int = 0
            self._initial_stop_distance: float = 0.0

        def _dch_high(self) -> float | None:
            if len(self._dch_highs) < self.p.donchian_len:
                return None
            return max(self._dch_highs)

        def _dch_low(self) -> float | None:
            if len(self._dch_lows) < self.p.donchian_len:
                return None
            return min(self._dch_lows)

        def _bar_time(self) -> pd.Timestamp:
            return pd.Timestamp(bt.num2date(self.data.datetime[0])).tz_localize(UTC)

        def _close_trade(
            self,
            *,
            exit_price: float,
            exit_reason: str,
        ) -> None:
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
                risk_home = self._initial_stop_distance * self._units
                if base_ccy == "USD":
                    risk_home = risk_home / exit_price
                r_mult = pnl_account / risk_home if risk_home > 0 else 0.0
            return_pct = (pnl_account / nav["value"]) * 100.0 if nav["value"] > 0 else None
            recorded.append(
                BacktraderTrade(
                    instrument=instrument,
                    side=self._side,
                    entry_time=self._entry_time.to_pydatetime() if self._entry_time else self._bar_time().to_pydatetime(),
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
            self._in_position = False
            self._side = "flat"
            self._has_trailed = False
            self._bars_held = 0
            self._units = 0
            self._initial_stop_distance = 0.0
            self._stop_price = 0.0
            self._initial_stop_price = 0.0

        def _try_entry(self) -> None:
            """Evaluate entry on the current bar. Mirrors the spec §4."""

            close = float(self.data.close[0])
            try:
                ef = float(self._ema_fast[0])
                es = float(self._ema_slow[0])
                atrv = float(self._atr[0])
            except IndexError:
                return
            if any(v != v for v in (ef, es, atrv)):  # NaN
                return
            dh = self._dch_high()
            dl = self._dch_low()
            if dh is None or dl is None:
                return
            if atrv <= 0:
                return
            atr_pips = atrv / pip_size
            if atr_pips < min_atr_pips_for_pair:
                return
            side: str | None = None
            if ef > es and close > dh:
                side = "long"
            elif ef < es and close < dl:
                side = "short"
            if side is None:
                return
            # Initial stop anchored at mid close, then display-precision rounded.
            raw_stop = (
                close - atr_stop_multiple * atrv
                if side == "long"
                else close + atr_stop_multiple * atrv
            )
            stop = _round_price(raw_stop, display_precision)
            # Bid/ask-aware fill at signal-bar close.
            bid_close = float(self.data.bid_close[0])
            ask_close = float(self.data.ask_close[0])
            entry_price = _fill_entry_price(
                side=side,
                bid_close=bid_close,
                ask_close=ask_close,
                fixed_slippage_pips=fixed_slippage_pips,
                spread_slippage_multiplier=spread_slippage_multiplier,
                pip_size=pip_size,
            )
            units = _size_position(
                nav=nav["value"],
                risk_per_trade_pct=risk_per_trade_pct,
                entry_price=entry_price,
                stop_price=stop,
                pip_size=pip_size,
                quote_currency=quote_ccy,
                base_currency=base_ccy,
            )
            if units <= 0:
                return
            self._in_position = True
            self._side = side
            self._entry_time = self._bar_time()
            self._entry_price = entry_price
            self._stop_price = stop
            self._initial_stop_price = stop
            self._has_trailed = False
            self._bars_held = 0
            self._units = units
            self._initial_stop_distance = abs(entry_price - stop)

        def _try_exit(self) -> bool:
            """Trail / check exit on a bar after entry. Returns True if exited."""

            self._bars_held += 1
            try:
                atrv = float(self._atr[0])
            except IndexError:
                atrv = float("nan")
            bid_close = float(self.data.bid_close[0])
            ask_close = float(self.data.ask_close[0])
            # Trailing stop ratchet first.
            if atrv == atrv and atrv > 0:  # not NaN
                distance = atr_stop_multiple * atrv  # same multiple per spec
                if self._side == "long":
                    candidate = bid_close - trailing_stop_atr_multiple * atrv
                    if candidate > self._stop_price:
                        self._stop_price = candidate
                        self._has_trailed = True
                elif self._side == "short":
                    candidate = ask_close + trailing_stop_atr_multiple * atrv
                    if candidate < self._stop_price:
                        self._stop_price = candidate
                        self._has_trailed = True
                del distance  # silence unused — kept for symmetry with spec
            # Adverse-stop check (priority 1).
            bid_low = float(self.data.bid_low[0])
            ask_high = float(self.data.ask_high[0])
            if self._side == "long" and bid_low <= self._stop_price:
                reason = "trailing_stop" if self._has_trailed else "stop"
                self._close_trade(exit_price=self._stop_price, exit_reason=reason)
                return True
            if self._side == "short" and ask_high >= self._stop_price:
                reason = "trailing_stop" if self._has_trailed else "stop"
                self._close_trade(exit_price=self._stop_price, exit_reason=reason)
                return True
            # Time-stop (priority 2).
            if self._bars_held >= max_bars_in_trade:
                exit_price = bid_close if self._side == "long" else ask_close
                self._close_trade(exit_price=exit_price, exit_reason="time")
                return True
            # End-of-data (priority 3).
            if _bar_count(self) >= n_bars:
                exit_price = bid_close if self._side == "long" else ask_close
                self._close_trade(exit_price=exit_price, exit_reason="eod")
                return True
            return False

        def next(self) -> None:
            # Order matches the bespoke event loop exactly: exits on this
            # bar first, then a possible same-bar re-entry if we just exited.
            if self._in_position:
                self._try_exit()
            if not self._in_position:
                self._try_entry()
            # After the bar is processed, push this bar's high/low onto the
            # Donchian deque so the next bar reads `t-1..t-N` not `t..t-N+1`.
            self._dch_highs.append(float(self.data.high[0]))
            self._dch_lows.append(float(self.data.low[0]))

        def stop(self) -> None:
            # If still in a position at the very end (`len(self) == n_bars`
            # was the EOD trigger inside `_try_exit` and would already have
            # closed; this branch only fires if EOD was missed for some
            # edge-case reason).
            if self._in_position:
                bid_close = float(self.data.bid_close[0])
                ask_close = float(self.data.ask_close[0])
                exit_price = bid_close if self._side == "long" else ask_close
                self._close_trade(exit_price=exit_price, exit_reason="eod")

    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.setcash(starting_equity_usd)
    cerebro.adddata(_Campaign002Feed(dataname=df))
    cerebro.addstrategy(_Campaign002Strategy)
    cerebro.run()

    return PairRunResult(
        instrument=instrument,
        candle_count=candles.bar_count,
        trades=recorded,
        final_cash=float(nav["value"]),
        starting_cash=float(starting_equity_usd),
        analyzer_outputs={"closed_trades": len(recorded)},
    )


CAMPAIGN_002_APPROXIMATION_FLAGS: tuple[str, ...] = (
    "BACKTRADER_INDICATORS: EMA(50/200) and ATR(14) are computed via "
    "Backtrader's `ExponentialMovingAverage` and `AverageTrueRange` "
    "(Wilder's smoothing). The recurrence matches pandas `ewm(adjust=False)` "
    "exactly, but early-warmup seeding may produce sub-pip differences in the "
    "first few hundred bars.",
    "DONCHIAN_PRIOR_BARS_ONLY: Donchian-20 is computed manually from a deque "
    "of the prior 20 completed bars' highs/lows (Backtrader's stock "
    "`Highest`/`Lowest` includes the current bar — using it would be a "
    "look-ahead bug).",
    "BACKTRADER_BROKER_BYPASSED: the Cerebro broker is NOT used for fills. "
    "The strategy maintains its own one-position state machine, fills at "
    "signal_bar_close using bid/ask + slippage, and anchors the initial "
    "stop at the bar's mid close (not at the post-slippage entry price).",
    "MANUAL_SIZING_RISK_FRACTION: 0.25% of compounding NAV; whole-units "
    "floor; pip value derived from quote/base currency at entry price.",
    "TRAILING_STOP_RATCHET: same multiple as initial (2.0×ATR), ratchet-up "
    "for longs using `bid_close - 2.0×ATR`, ratchet-down for shorts using "
    "`ask_close + 2.0×ATR`, per CAMPAIGN_002_LEAN_MAPPING_SPEC.md §5.",
    "NO_RISK_ENGINE: spread / session / loss-limit gates not applied "
    "(matches the no-RiskEngine bespoke reference at 1,647 trades).",
    "NO_FINANCING: financing/swap not modeled in either engine; comparison "
    "is pre-financing.",
)


CAMPAIGN_002_ADAPTER = CampaignAdapter(
    campaign_id="CAMPAIGN_002",
    strategy_id="trend_following",
    strategy_version="0.1.0-baseline-frozen",
    description=(
        "Backtrader port of CAMPAIGN_002 H4 trend_following baseline. "
        "Frozen rules from docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md. "
        "CAMPAIGN_002 remains REJECT regardless of this port's output."
    ),
    runner_fn=run_campaign_002_pair,
    default_instruments=(
        "EUR_USD",
        "GBP_USD",
        "USD_JPY",
        "AUD_USD",
        "USD_CAD",
        "USD_CHF",
        "NZD_USD",
    ),
    default_starting_equity_usd=500.0,
    risk_per_trade_pct=0.25,
    approximation_flags=CAMPAIGN_002_APPROXIMATION_FLAGS,
    notes="strategy_evidence: false; CAMPAIGN_002 REJECT — not a paper candidate",
)


register_campaign(CAMPAIGN_002_ADAPTER)

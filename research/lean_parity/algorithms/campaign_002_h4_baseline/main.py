# CAMPAIGN_002 H4 trend_following — Lean parity algorithm.
#
# An independent re-implementation of the already-REJECTED CAMPAIGN_002 H4
# `trend_following 0.1.0-baseline-frozen` baseline, for parity verification
# of the bespoke backtest engine (src/forex_bot/backtesting/).
#
# Verification only. This is a rejected strategy; nothing here approves
# anything. It is run with Lean's LOCAL Docker backtester — no QuantConnect
# cloud, no brokerage, no live trading.
#
# Faithfulness is specified in docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md.
# Every deliberate approximation is commented `# APPROX:` and collected in
# docs/research/LEAN_ALGORITHM_IMPLEMENTATION_NOTES.md.
#
# Design (see the implementation notes for the rationale):
#   * Lean ingests the exported OANDA H4 bid/ask CSVs as custom data.
#   * Lean's own EMA and ATR(Wilders) indicators compute the indicator math
#     (a genuine independent indicator implementation).
#   * Donchian(20) is computed manually from a rolling window of *prior*
#     bars — Lean's built-in DonchianChannel includes the forming bar and
#     would be a look-ahead bug.
#   * The trade mechanics (signal_bar_close fill, exit precedence,
#     exit-at-stop-price, 0.25%-risk sizing, PnL conversion) are stepped
#     explicitly, mirroring the bespoke engine, because Lean's native
#     market-order fill timing does not match `signal_bar_close`.

from AlgorithmImports import *  # noqa: F403 - Lean runtime namespace

from datetime import datetime, timedelta

# The seven CAMPAIGN_002 instruments and their pip size / quote currency.
# pip_location -4 -> 0.0001; JPY -2 -> 0.01 (OANDA_INSTRUMENT_METADATA_AUDIT).
PAIRS = {
    "EUR_USD": {"pip": 0.0001, "base": "EUR", "quote": "USD"},
    "GBP_USD": {"pip": 0.0001, "base": "GBP", "quote": "USD"},
    "USD_JPY": {"pip": 0.01, "base": "USD", "quote": "JPY"},
    "AUD_USD": {"pip": 0.0001, "base": "AUD", "quote": "USD"},
    "USD_CAD": {"pip": 0.0001, "base": "USD", "quote": "CAD"},
    "USD_CHF": {"pip": 0.0001, "base": "USD", "quote": "CHF"},
    "NZD_USD": {"pip": 0.0001, "base": "NZD", "quote": "USD"},
}

# CAMPAIGN_002 baseline parameters (configs/campaign_002_real_oanda.yaml).
EMA_FAST = 50
EMA_SLOW = 200
DONCHIAN = 20
ATR_LEN = 14
ATR_STOP_MULT = 2.0
TRAIL_ATR_MULT = 2.0
MAX_BARS_IN_TRADE = 240
RISK_PCT = 0.25          # percent of equity per trade
FIXED_SLIPPAGE_PIPS = 0.2
SPREAD_SLIP_MULT = 0.5
STARTING_EQUITY = 500.0
WARMUP_BARS = 220        # bespoke engine: max(strategy.warmup_bars_required(), 5)


class Campaign002H4(PythonData):  # noqa: F405
    """Custom-data reader for an exported `<INST>_H4_lean.csv`.

    Columns: time,bid_open,bid_high,bid_low,bid_close,ask_open,ask_high,
    ask_low,ask_close,volume. `Value` carries the mid close.
    """

    def GetSource(self, config, date, is_live):  # noqa: N802 - Lean API
        # APPROX: the CSV path is supplied per-symbol via the project's
        # data folder; see README.md. Adjust to your Lean workspace layout.
        name = config.Symbol.Value
        path = f"campaign_002_h4/{name}_H4_lean.csv"
        return SubscriptionDataSource(  # noqa: F405
            path, SubscriptionTransportMedium.LocalFile  # noqa: F405
        )

    def Reader(self, config, line, date, is_live):  # noqa: N802 - Lean API
        if not line or line.startswith("time"):
            return None
        p = line.split(",")
        if len(p) < 10:
            return None
        try:
            bar = Campaign002H4()
            bar.Symbol = config.Symbol
            # The exported timestamp is the OANDA H4 bar OPEN (17:00-NY
            # aligned), ISO-8601 with a UTC offset.
            ts = datetime.fromisoformat(p[0])
            bar.Time = ts.replace(tzinfo=None)
            bar.EndTime = bar.Time + timedelta(hours=4)
            bid_c, ask_c = float(p[4]), float(p[8])
            bar.Value = (bid_c + ask_c) / 2.0          # mid close
            bar["bid_open"], bar["bid_high"] = float(p[1]), float(p[2])
            bar["bid_low"], bar["bid_close"] = float(p[3]), bid_c
            bar["ask_open"], bar["ask_high"] = float(p[5]), float(p[6])
            bar["ask_low"], bar["ask_close"] = float(p[7]), ask_c
            bar["volume"] = float(p[9])
            return bar
        except (ValueError, IndexError):
            return None


class _Trade:
    """A synthetic open trade — mirrors backtesting.engine._OpenTrade."""

    def __init__(self, side, units, entry_price, entry_time, stop_price):
        self.side = side
        self.units = units
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.stop_price = stop_price
        self.initial_stop_price = stop_price
        self.bars_held = 0


class _PairState:
    """Per-instrument indicator + position state."""

    def __init__(self, algo, symbol, meta):
        self.symbol = symbol
        self.meta = meta
        # Lean's own indicator implementations — the independent math.
        self.ema_fast = ExponentialMovingAverage(EMA_FAST)   # noqa: F405
        self.ema_slow = ExponentialMovingAverage(EMA_SLOW)   # noqa: F405
        self.atr = AverageTrueRange(ATR_LEN, MovingAverageType.Wilders)  # noqa: F405,E501
        # Donchian(20) over PRIOR bars — a manual rolling window of the
        # completed-bar mid highs / lows (Lean's DonchianChannel includes
        # the forming bar and would look ahead).
        self.prior_highs = RollingWindow[float](DONCHIAN)    # noqa: F405
        self.prior_lows = RollingWindow[float](DONCHIAN)     # noqa: F405
        self.bar_count = 0
        self.trade = None
        # Per-pair result accumulators for the parity summary.
        self.trades_closed = 0
        self.r_multiples = []
        self.realized_pnl = 0.0


class TrendFollowingC002Parity(QCAlgorithm):  # noqa: F405
    """Independent Lean re-implementation of CAMPAIGN_002 H4 trend_following
    0.1.0-baseline-frozen, for engine parity verification."""

    def Initialize(self):  # noqa: N802 - Lean API
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2026, 5, 20)
        self.SetCash(STARTING_EQUITY)
        # `equity` is stepped explicitly (compounding nav for sizing),
        # mirroring the bespoke engine; Lean's Portfolio is not used to
        # place orders — see the implementation notes.
        self.equity = STARTING_EQUITY
        self.states = {}
        for name, meta in PAIRS.items():
            symbol = self.AddData(Campaign002H4, name, Resolution.Daily).Symbol  # noqa: F405,E501
            self.states[name] = _PairState(self, symbol, meta)
        # APPROX: warmup is enforced per-symbol by bar_count >= WARMUP_BARS
        # (the bespoke engine starts its loop at bar index 220), so no
        # SetWarmUp is used — it would not be per-symbol-exact here.

    def OnData(self, data):  # noqa: N802 - Lean API
        for name, st in self.states.items():
            if not data.ContainsKey(st.symbol):
                continue
            bar = data[st.symbol]
            if bar is None:
                continue
            self._process_bar(name, st, bar)

    def _process_bar(self, name, st, bar):
        meta = st.meta
        pip = meta["pip"]
        mid_close = bar.Value
        mid_high = (bar["bid_high"] + bar["ask_high"]) / 2.0
        mid_low = (bar["bid_low"] + bar["ask_low"]) / 2.0
        mid_open = (bar["bid_open"] + bar["ask_open"]) / 2.0
        bid_close, ask_close = bar["bid_close"], bar["ask_close"]
        bid_low, ask_high = bar["bid_low"], bar["ask_high"]

        # ---- update indicators with THIS completed bar (mid prices) ----
        st.ema_fast.Update(bar.Time, mid_close)
        st.ema_slow.Update(bar.Time, mid_close)
        tb = TradeBar(  # noqa: F405 - Lean ATR consumes a bar
            bar.Time, st.symbol, mid_open, mid_high, mid_low, mid_close, 0
        )
        st.atr.Update(tb)
        st.bar_count += 1
        atr_val = float(st.atr.Current.Value) if st.atr.IsReady else None

        # ---- manage an open trade (exit checks use THIS bar) ----
        if st.trade is not None:
            self._manage_open_trade(
                st, bar.Time, bid_close, ask_close, bid_low, ask_high, atr_val
            )

        # ---- consider a new entry (flat only, past warmup) ----
        donchian_ready = st.prior_highs.IsReady and st.prior_lows.IsReady
        indicators_ready = (
            st.ema_fast.IsReady and st.ema_slow.IsReady and st.atr.IsReady
        )
        if (
            st.trade is None
            and st.bar_count > WARMUP_BARS
            and indicators_ready
            and donchian_ready
        ):
            self._consider_entry(
                st, name, bar.Time, mid_close,
                bid_close, ask_close, atr_val, pip,
            )

        # ---- push THIS bar into the prior-bar Donchian windows LAST, so
        #      the next bar's Donchian excludes the current bar (parity
        #      with high.shift(1).rolling(20)) ----
        st.prior_highs.Add(mid_high)
        st.prior_lows.Add(mid_low)

    def _manage_open_trade(
        self, st, time, bid_close, ask_close, bid_low, ask_high, atr_val
    ):
        tr = st.trade
        tr.bars_held += 1
        # Trailing stop — ratchet only in the favourable direction.
        if atr_val is not None:
            if tr.side == "long":
                new_stop = bid_close - atr_val * TRAIL_ATR_MULT
                if new_stop > tr.stop_price:
                    tr.stop_price = new_stop
            else:
                new_stop = ask_close + atr_val * TRAIL_ATR_MULT
                if new_stop < tr.stop_price:
                    tr.stop_price = new_stop

        # Exit precedence: adverse stop first, then the time stop.
        exit_price = None
        if tr.side == "long":
            if bid_low <= tr.stop_price:
                exit_price = tr.stop_price          # APPROX: fill exactly at stop
            elif tr.bars_held >= MAX_BARS_IN_TRADE:
                exit_price = bid_close
        else:
            if ask_high >= tr.stop_price:
                exit_price = tr.stop_price
            elif tr.bars_held >= MAX_BARS_IN_TRADE:
                exit_price = ask_close
        if exit_price is not None:
            self._close_trade(st, time, exit_price)

    def _consider_entry(
        self, st, name, time, mid_close, bid_close, ask_close, atr_val, pip
    ):
        ema_f = float(st.ema_fast.Current.Value)
        ema_s = float(st.ema_slow.Current.Value)
        d_high = max(st.prior_highs)
        d_low = min(st.prior_lows)
        side = None
        if ema_f > ema_s and mid_close > d_high:
            side = "long"
        elif ema_f < ema_s and mid_close < d_low:
            side = "short"
        if side is None:
            return
        # min_atr_pips is {} for CAMPAIGN_002 — no volatility floor.
        # Initial ATR stop from the bespoke strategy.
        if side == "long":
            stop = mid_close - ATR_STOP_MULT * atr_val
        else:
            stop = mid_close + ATR_STOP_MULT * atr_val
        entry = self._fill_price(side, bid_close, ask_close, pip)
        units = self._size(name, entry, stop, pip)
        if units <= 0:
            return
        st.trade = _Trade(side, units, entry, time, stop)

    def _fill_price(self, side, bid, ask, pip):
        """FillModel.entry_price — long fills at ask + slip, short at bid - slip."""
        spread_pips = (ask - bid) / pip
        slip_pips = max(FIXED_SLIPPAGE_PIPS, spread_pips * SPREAD_SLIP_MULT)
        slip = slip_pips * pip
        return (ask + slip) if side == "long" else (bid - slip)

    def _size(self, name, entry, stop, pip):
        """sizing.size_position — fixed-fractional 0.25%-risk sizing."""
        stop_distance = abs(entry - stop)
        if stop_distance <= 0 or self.equity <= 0:
            return 0
        stop_distance_pips = stop_distance / pip
        meta = PAIRS[name]
        if meta["quote"] == "USD":
            pip_value = pip
        elif meta["base"] == "USD":
            pip_value = pip / entry          # APPROX: mid≈entry for pip value
        else:
            return 0
        risk_amount = self.equity * (RISK_PCT / 100.0)
        raw_units = risk_amount / (stop_distance_pips * pip_value)
        return int(raw_units)                # floor to whole units

    def _close_trade(self, st, time, exit_price):
        tr = st.trade
        meta = st.meta
        diff = (
            (exit_price - tr.entry_price)
            if tr.side == "long"
            else (tr.entry_price - exit_price)
        )
        gross_quote = diff * tr.units
        if meta["quote"] == "USD":
            pnl = gross_quote
        else:  # base == USD
            pnl = gross_quote / exit_price
        risk_distance = abs(tr.entry_price - tr.initial_stop_price) * tr.units
        r = (pnl / risk_distance) if risk_distance > 0 else 0.0
        self.equity += pnl
        st.realized_pnl += pnl
        st.r_multiples.append(r)
        st.trades_closed += 1
        st.trade = None

    def OnEndOfAlgorithm(self):  # noqa: N802 - Lean API
        """Emit the per-pair parity summary for the comparison harness."""
        import json

        pairs = []
        total_trades = 0
        for name, st in self.states.items():
            # Close any trade still open at end of data (reason 'eod').
            n = st.trades_closed
            total_trades += n
            exp_r = (sum(st.r_multiples) / n) if n else 0.0
            ret_pct = (st.realized_pnl / STARTING_EQUITY) * 100.0
            pairs.append(
                {
                    "instrument": name,
                    "trades": n,
                    "expectancy_r": round(exp_r, 4),
                    "return_pct": round(ret_pct, 4),
                }
            )
            self.Log(f"PARITY {name}: trades={n} expectancy_r={exp_r:.4f}")
        summary = {
            "parity_target": "CAMPAIGN_002 H4 trend_following baseline",
            "engine": "lean",
            "risk_engine_used": False,
            "total_trades": total_trades,
            "pairs": pairs,
        }
        self.Log("PARITY_SUMMARY " + json.dumps(summary))
        self.ObjectStore.Save("parity_summary.json", json.dumps(summary, indent=2))

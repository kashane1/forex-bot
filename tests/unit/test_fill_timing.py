"""Fill-timing model tests (Phase 1, infra-execution-fidelity-001).

Proves the backtest engine supports two explicit fill timings:

  * signal_bar_close — the prior, optimistic behaviour (default);
  * next_bar_open    — fill at bar N+1's open.

and that next_bar_open uses no future data, skips a final-bar signal
explicitly, and that the chosen timing is recorded in trade records and
exports. signal_bar_close stays the default so prior campaigns reproduce.
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from forex_bot.backtesting.engine import BacktestEngine
from forex_bot.backtesting.exporters import write_all
from forex_bot.backtesting.fills import (
    FILL_TIMINGS,
    NEXT_BAR_OPEN_UNAVAILABLE,
    FillModel,
)
from forex_bot.config import BacktestConfig, ConfigError
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext

_ZERO_FILL = FillModel(
    fixed_slippage_pips=Decimal("0"), spread_slippage_multiplier=Decimal("0")
)


class _OneShotLong:
    """Test strategy: emits exactly one long signal, on the bar where the
    rolling window first contains `fire_at_len` candles. The engine passes
    `window = df.iloc[: i + 1]`, so firing at window length L pins the
    signal to bar index L - 1."""

    name = "oneshot_long"
    version = "0.0.0-test"

    def __init__(self, fire_at_len: int, stop_offset: Decimal = Decimal("0.0100")):
        self._fire_at_len = fire_at_len
        self._stop_offset = stop_offset

    def warmup_bars_required(self) -> int:
        return 2

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.df
        if len(df) != self._fire_at_len:
            return None
        ts = df.index[-1]
        close = Decimal(str(df["close"].iloc[-1]))
        return Signal(
            signal_id=f"oneshot-{self._fire_at_len}",
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe="H4",
            timestamp=ts.to_pydatetime(),
            side="long",
            stop_model="test_fixed",
            stop_price=close - self._stop_offset,
            exit_model="test",
        )


def _candle(k: int, bid_o: Decimal) -> Candle:
    """One H4 candle with a deterministic 5-pip body and 2-pip spread."""
    bid_c = bid_o + Decimal("0.0005")
    bid_h = max(bid_o, bid_c) + Decimal("0.0003")
    bid_l = min(bid_o, bid_c) - Decimal("0.0003")
    sp = Decimal("0.0002")
    return Candle(
        instrument="EUR_USD",
        granularity="H4",
        time=datetime(2025, 3, 3, tzinfo=UTC) + timedelta(hours=4 * k),
        complete=True,
        volume=1000,
        bid_o=bid_o, bid_h=bid_h, bid_l=bid_l, bid_c=bid_c,
        ask_o=bid_o + sp, ask_h=bid_h + sp, ask_l=bid_l + sp, ask_c=bid_c + sp,
    )


def _uptrend(n: int = 20) -> tuple[CandleFrame, list[Candle]]:
    """A calm uptrend: each bar opens 10 pips above the previous bar's
    open. No bar reverses, so a long with a far stop never stops out."""
    candles = [_candle(k, Decimal("1.1000") + Decimal("0.0010") * k) for k in range(n)]
    return CandleFrame.from_candles("EUR_USD", "H4", candles), candles


def _engine(strategy: _OneShotLong, eur_usd, fill_timing: str | None) -> BacktestEngine:
    kwargs = dict(
        instrument=eur_usd,
        strategy=strategy,
        strategy_config={},
        fill_model=_ZERO_FILL,
        starting_equity=Decimal("500"),
        account_currency="USD",
        max_bars_in_trade=200,
    )
    if fill_timing is not None:
        kwargs["fill_timing"] = fill_timing
    return BacktestEngine(**kwargs)  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# Config + defaults
# --------------------------------------------------------------------------


def test_backtest_config_defaults_to_signal_bar_close():
    assert BacktestConfig().fill_timing == "signal_bar_close"


def test_backtest_config_accepts_next_bar_open():
    assert BacktestConfig(fill_timing="next_bar_open").fill_timing == "next_bar_open"


def test_backtest_config_rejects_unknown_fill_timing():
    with pytest.raises((ConfigError, ValueError)):
        BacktestConfig(fill_timing="instant")  # type: ignore[arg-type]


def test_engine_default_fill_timing_is_signal_bar_close(eur_usd):
    engine = _engine(_OneShotLong(fire_at_len=11), eur_usd, fill_timing=None)
    assert engine.fill_timing == "signal_bar_close"
    assert "signal_bar_close" in FILL_TIMINGS and "next_bar_open" in FILL_TIMINGS


# --------------------------------------------------------------------------
# signal_bar_close preserves prior behaviour
# --------------------------------------------------------------------------


def test_signal_bar_close_default_matches_explicit(eur_usd):
    """Omitting fill_timing and passing 'signal_bar_close' explicitly must
    produce byte-identical results — the default is the prior behaviour."""
    frame, _ = _uptrend()
    implicit = _engine(_OneShotLong(11), eur_usd, fill_timing=None).run(frame)
    explicit = _engine(_OneShotLong(11), eur_usd, fill_timing="signal_bar_close").run(
        frame
    )
    assert implicit.config_hash == explicit.config_hash
    assert implicit.fill_timing == explicit.fill_timing == "signal_bar_close"
    assert [t.entry_price for t in implicit.trades] == [
        t.entry_price for t in explicit.trades
    ]
    assert implicit.metrics.final_equity == explicit.metrics.final_equity


def test_signal_bar_close_fills_at_signal_bar_close(eur_usd):
    """signal_bar_close: a long fills at the signal bar's ask close."""
    frame, candles = _uptrend()
    result = _engine(_OneShotLong(11), eur_usd, "signal_bar_close").run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    # window length 11 -> bar index 10 is the signal bar.
    assert trade.entry_price == candles[10].ask_c
    assert trade.entry_time == candles[10].time
    assert trade.fill_timing == "signal_bar_close"


# --------------------------------------------------------------------------
# next_bar_open
# --------------------------------------------------------------------------


def test_next_bar_open_fills_at_next_candle_open(eur_usd):
    """next_bar_open: the same signal fills at bar N+1's ask open, one bar
    later than signal_bar_close."""
    frame, candles = _uptrend()
    result = _engine(_OneShotLong(11), eur_usd, "next_bar_open").run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    # Signal bar index 10 -> fill at bar 11's open.
    assert trade.entry_price == candles[11].ask_o
    assert trade.entry_time == candles[11].time
    assert trade.fill_timing == "next_bar_open"


def test_next_bar_open_differs_from_signal_bar_close(eur_usd):
    """The two timings genuinely diverge: different entry price, different
    entry bar, and a distinct config hash so artifacts never get confused."""
    frame, _ = _uptrend()
    sbc = _engine(_OneShotLong(11), eur_usd, "signal_bar_close").run(frame)
    nbo = _engine(_OneShotLong(11), eur_usd, "next_bar_open").run(frame)
    assert sbc.trades[0].entry_price != nbo.trades[0].entry_price
    assert nbo.trades[0].entry_time > sbc.trades[0].entry_time
    assert sbc.config_hash != nbo.config_hash


def test_next_bar_open_missing_next_bar_is_explicit_skip(eur_usd):
    """A signal on the final bar has no bar N+1 — next_bar_open records an
    explicit skipped signal and opens no trade (never a silent drop, never
    a same-bar fallback fill)."""
    frame, candles = _uptrend(n=20)
    # window length 20 -> bar index 19, the final bar.
    result = _engine(_OneShotLong(20), eur_usd, "next_bar_open").run(frame)
    assert result.trades == []
    assert len(result.rejected_signals) == 1
    rej = result.rejected_signals[0]
    assert rej.rejection_codes == [NEXT_BAR_OPEN_UNAVAILABLE]
    assert "final bar" in rej.rejection_messages[0]
    assert result.rejection_counts.get(NEXT_BAR_OPEN_UNAVAILABLE) == 1


def test_signal_bar_close_still_fills_on_the_final_bar(eur_usd):
    """The same final-bar signal that next_bar_open skips DOES fill under
    signal_bar_close — confirming the skip is a fill-timing property."""
    frame, _ = _uptrend(n=20)
    result = _engine(_OneShotLong(20), eur_usd, "signal_bar_close").run(frame)
    assert len(result.trades) == 1
    assert result.rejected_signals == []


# --------------------------------------------------------------------------
# No lookahead
# --------------------------------------------------------------------------


def test_next_bar_open_uses_no_data_after_the_fill_bar(eur_usd):
    """The entry must depend only on bar N+1's open. Mutating every bar
    strictly after N+1 must leave the entry price and time unchanged."""
    base, candles = _uptrend(n=20)
    # A divergent frame: identical through bar 11, then a violent crash.
    mutated = list(candles[:12])
    for k in range(12, 20):
        mutated.append(_candle(k, Decimal("0.9000") - Decimal("0.0050") * k))
    mutated_frame = CandleFrame.from_candles("EUR_USD", "H4", mutated)

    base_trade = _engine(_OneShotLong(11), eur_usd, "next_bar_open").run(base).trades[0]
    mut_trade = (
        _engine(_OneShotLong(11), eur_usd, "next_bar_open").run(mutated_frame).trades[0]
    )
    assert base_trade.entry_price == mut_trade.entry_price == candles[11].ask_o
    assert base_trade.entry_time == mut_trade.entry_time == candles[11].time


def test_next_bar_open_no_trade_exits_before_it_enters(eur_usd):
    """Every trade's exit is at or after its entry — the engine cannot
    close a position on a bar before the one it filled on."""
    frame, _ = _uptrend()
    result = _engine(_OneShotLong(11), eur_usd, "next_bar_open").run(frame)
    assert result.trades
    for trade in result.trades:
        assert trade.exit_time >= trade.entry_time
        assert trade.entry_time >= trade.exit_time - timedelta(days=365)


# --------------------------------------------------------------------------
# Trade log / export propagation
# --------------------------------------------------------------------------


def test_trade_csv_and_reports_state_fill_timing(eur_usd, tmp_path):
    """The fill timing is auditable: in every trade-CSV row, the metrics
    Markdown, and the summary / metrics JSON."""
    frame, _ = _uptrend()
    result = _engine(_OneShotLong(11), eur_usd, "next_bar_open").run(frame)
    paths = write_all(result, tmp_path, "ft_test")

    with paths["trades_csv"].open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows and all(r["fill_timing"] == "next_bar_open" for r in rows)

    assert "next_bar_open" in paths["metrics_md"].read_text(encoding="utf-8").lower()

    summary = json.loads(paths["summary_json"].read_text(encoding="utf-8"))
    assert summary["fill_timing"] == "next_bar_open"
    metrics = json.loads(paths["metrics_json"].read_text(encoding="utf-8"))
    assert metrics["fill_timing"] == "next_bar_open"

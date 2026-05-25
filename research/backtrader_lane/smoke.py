"""Minimal Backtrader smoke utilities used by the Phase 1 smoke test.

These exist so the smoke test can call deterministic helpers instead of
constructing a Cerebro inline. They are the *only* code in this package that
is allowed to instantiate Backtrader objects without a frozen campaign
adapter — every other entry point goes through a campaign adapter.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True)
class SmokeBar:
    """One H4 OHLC bar used by the deterministic smoke fixture."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


def deterministic_h4_bars(
    n: int = 30,
    start: datetime | None = None,
    base_price: float = 1.10000,
    step: float = 0.00010,
) -> list[SmokeBar]:
    """Generate a deterministic linear-up H4 OHLC sequence.

    Pure function; no random source. The smoke test depends on this being
    reproducible bit-for-bit.
    """

    if n < 1:
        raise ValueError("n must be >= 1")
    if start is None:
        start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=UTC)
    bars: list[SmokeBar] = []
    for i in range(n):
        mid = base_price + i * step
        bars.append(
            SmokeBar(
                timestamp=start + timedelta(hours=4 * i),
                open=mid,
                high=mid + 0.5 * step,
                low=mid - 0.5 * step,
                close=mid + 0.2 * step,
                volume=100,
            )
        )
    return bars


def bars_to_pandas(bars: Iterable[SmokeBar]):
    """Convert SmokeBars to a pandas DataFrame indexed by timestamp.

    Lazily imports pandas so this module can be imported with no extras.
    """

    import pandas as pd

    rows = [
        {
            "open": b.open,
            "high": b.high,
            "low": b.low,
            "close": b.close,
            "volume": b.volume,
        }
        for b in bars
    ]
    index = [b.timestamp for b in bars]
    return pd.DataFrame(rows, index=index)


def run_noop_cerebro(bars: Iterable[SmokeBar]) -> int:
    """Run a Cerebro with a no-op strategy and return the strategy count.

    Verifies Backtrader can load a feed and execute a strategy.next() loop
    without raising. Lazily imports backtrader so this module is importable
    without the extra.
    """

    import backtrader as bt

    bars_list = list(bars)
    df = bars_to_pandas(bars_list)

    class _NoOp(bt.Strategy):  # pragma: no cover - trivial
        def next(self) -> None:
            return None

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10_000.0)
    feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(feed)
    cerebro.addstrategy(_NoOp)
    results = cerebro.run()
    return len(results)


def run_oneshot_cerebro(bars: Iterable[SmokeBar]) -> dict[str, float | int]:
    """Run a Cerebro that enters at bar 5 and exits at bar 10.

    Returns a dict with the closed-trade count, final cash, and net PnL.
    This is the deterministic-trade smoke test.
    """

    import backtrader as bt

    bars_list = list(bars)
    df = bars_to_pandas(bars_list)

    class _TradeRecorder(bt.Analyzer):
        def start(self) -> None:
            self.trades: list[dict[str, float]] = []

        def notify_trade(self, trade) -> None:  # type: ignore[no-untyped-def]
            if trade.isclosed:
                self.trades.append({"pnl": float(trade.pnl), "pnlcomm": float(trade.pnlcomm)})

        def get_analysis(self) -> dict[str, list[dict[str, float]]]:
            return {"trades": self.trades}

    class _OneShot(bt.Strategy):  # pragma: no cover - trivial deterministic
        params = (("entry_bar", 5), ("exit_bar", 10), ("size", 1000))

        def __init__(self) -> None:
            self._opened = False
            self._closed = False

        def next(self) -> None:
            n = len(self)
            if not self._opened and n == self.p.entry_bar:
                self.buy(size=self.p.size)
                self._opened = True
            elif self._opened and not self._closed and n == self.p.exit_bar:
                self.sell(size=self.p.size)
                self._closed = True

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10_000.0)
    feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(feed)
    cerebro.addstrategy(_OneShot)
    cerebro.addanalyzer(_TradeRecorder, _name="trades")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    results = cerebro.run()
    strat = results[0]
    recorded = strat.analyzers.trades.get_analysis()
    ta = strat.analyzers.ta.get_analysis()
    closed = (
        ta.total.closed
        if hasattr(ta, "total") and hasattr(ta.total, "closed")
        else len(recorded["trades"])
    )
    return {
        "closed_trades": int(closed),
        "final_cash": float(cerebro.broker.getcash()),
        "net_pnl": float(sum(t["pnl"] for t in recorded["trades"])),
    }

"""Same-bar SL+TP ambiguous-exit instrumentation.

Sprint `infra-exit-fidelity-001` Phase 1. Adds a per-trade
`TradeRecord.ambiguous_exit` flag and an aggregate
`BacktestMetrics.ambiguous_exit_count` for bars where the adverse stop
won the tie-break BUT the take-profit was also in range on the same bar.

Pure observation — never changes the exit, the exit_price, or any PnL.
The tie-break itself (stop wins) is the load-bearing rule from
[CAMPAIGN_009_PRECOMMIT.md §59](docs/research/CAMPAIGN_009_PRECOMMIT.md);
this sprint does NOT change it.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pandas as pd

from forex_bot.backtesting.engine import BacktestEngine
from forex_bot.backtesting.fills import FillModel
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext

_ZERO_FILL = FillModel(
    fixed_slippage_pips=Decimal("0"), spread_slippage_multiplier=Decimal("0")
)


# ---------------------------------------------------------------------------
# Test scaffolding
# ---------------------------------------------------------------------------


class _OneShotStrategy:
    """Emits a single signal at a fixed bar. Carries both stop and TP."""

    name = "oneshot"

    def __init__(
        self,
        *,
        fire_at: int,
        side: str,
        stop_offset: Decimal,
        take_profit_offset: Decimal | None,
    ) -> None:
        self.version = "test"
        self._fire_at = fire_at
        self._side = side
        self._stop_offset = stop_offset
        self._take_profit_offset = take_profit_offset

    def warmup_bars_required(self) -> int:
        return 2

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        if len(df) != self._fire_at:
            return None
        last = df.index[-1]
        close = Decimal(str(df["close"].iloc[-1]))
        if self._side == "long":
            stop = close - self._stop_offset
            tp = close + self._take_profit_offset if self._take_profit_offset else None
        else:
            stop = close + self._stop_offset
            tp = close - self._take_profit_offset if self._take_profit_offset else None
        return Signal(
            signal_id=f"oneshot-{self._fire_at}-{self._side}",
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe="H4",
            timestamp=pd.Timestamp(last).tz_convert(UTC).to_pydatetime(),
            side=self._side,  # type: ignore[arg-type]
            stop_model="fixed",
            stop_price=stop,
            take_profit_price=tp,
            exit_model="target" if tp else "stop_only",
        )


def _candle(
    k: int,
    *,
    bid_o: Decimal,
    bid_h: Decimal,
    bid_l: Decimal,
    bid_c: Decimal,
    spread: Decimal = Decimal("0.0002"),
) -> Candle:
    """One H4 candle with explicit bid OHLC and a fixed spread to ask side."""
    return Candle(
        instrument="EUR_USD",
        granularity="H4",
        time=datetime(2025, 3, 3, tzinfo=UTC) + timedelta(hours=4 * k),
        complete=True,
        volume=1000,
        bid_o=bid_o,
        bid_h=bid_h,
        bid_l=bid_l,
        bid_c=bid_c,
        ask_o=bid_o + spread,
        ask_h=bid_h + spread,
        ask_l=bid_l + spread,
        ask_c=bid_c + spread,
    )


def _make_engine(
    strategy,
    eur_usd,
    *,
    risk_engine=None,
    max_bars_in_trade: int = 999,
) -> BacktestEngine:
    return BacktestEngine(
        instrument=eur_usd,
        strategy=strategy,
        strategy_config={},
        fill_model=_ZERO_FILL,
        starting_equity=Decimal("500"),
        account_currency="USD",
        max_bars_in_trade=max_bars_in_trade,
        risk_engine=risk_engine,
    )


# ---------------------------------------------------------------------------
# Long-side detection
# ---------------------------------------------------------------------------


_ENTRY_BAR_INDEX = 5  # The engine forces warmup=max(strategy.warmup, 5).
_FIRE_AT_LEN = _ENTRY_BAR_INDEX + 1  # signal fires when window len reaches this


def _quiet_bar(k: int) -> Candle:
    return _candle(
        k,
        bid_o=Decimal("1.10000"),
        bid_h=Decimal("1.10005"),
        bid_l=Decimal("1.09995"),
        bid_c=Decimal("1.10000"),
    )


def _long_setup_with_wide_exit_bar(
    *,
    tp_in_range: bool,
) -> CandleFrame:
    """Quiet warmup bars + entry-trigger bar + a 'wide' exit bar.

    Entry: close 1.1000 at bar `_ENTRY_BAR_INDEX`. Strategy emits long
    with stop=1.0950, tp=1.1050. The exit bar's geometry decides whether
    the stop AND tp are both touchable:

      * tp_in_range=True  → wide bar: bid_low=1.0940 (hits stop),
        bid_high=1.1055 (hits tp). Ambiguous.
      * tp_in_range=False → bar wicks down only: bid_low=1.0940,
        bid_high=1.1010 (does NOT reach tp). NOT ambiguous.
    """
    exit_bid_high = Decimal("1.10550") if tp_in_range else Decimal("1.10100")
    bars = [_quiet_bar(k) for k in range(_ENTRY_BAR_INDEX + 1)]
    bars.append(
        _candle(
            _ENTRY_BAR_INDEX + 1,
            bid_o=Decimal("1.10000"),
            bid_h=exit_bid_high,
            bid_l=Decimal("1.09400"),  # below stop 1.0950 → stop fires
            bid_c=Decimal("1.09800"),
        )
    )
    return CandleFrame.from_candles("EUR_USD", "H4", bars)


def test_long_stop_with_tp_in_range_flags_ambiguous(eur_usd):
    strat = _OneShotStrategy(
        fire_at=_FIRE_AT_LEN,
        side="long",
        stop_offset=Decimal("0.0050"),
        take_profit_offset=Decimal("0.0050"),
    )
    frame = _long_setup_with_wide_exit_bar(tp_in_range=True)
    result = _make_engine(strat, eur_usd).run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.exit_reason == "stop"
    assert trade.ambiguous_exit is True
    assert result.metrics.ambiguous_exit_count == 1
    assert result.ambiguous_exit_count == 1


def test_long_stop_with_tp_out_of_range_does_not_flag(eur_usd):
    strat = _OneShotStrategy(
        fire_at=_FIRE_AT_LEN,
        side="long",
        stop_offset=Decimal("0.0050"),
        take_profit_offset=Decimal("0.0050"),
    )
    frame = _long_setup_with_wide_exit_bar(tp_in_range=False)
    result = _make_engine(strat, eur_usd).run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.exit_reason == "stop"
    assert trade.ambiguous_exit is False
    assert result.metrics.ambiguous_exit_count == 0


# ---------------------------------------------------------------------------
# Short-side detection
# ---------------------------------------------------------------------------


def _short_setup_with_wide_exit_bar(
    *,
    tp_in_range: bool,
) -> CandleFrame:
    """Quiet warmup + entry + wide exit bar (mirror of long setup).

    Entry: close 1.1000 at `_ENTRY_BAR_INDEX`. Strategy emits short with
    stop=1.1050, tp=1.0950. The exit bar:

      * tp_in_range=True  → wide bar: ask_high=1.1060 (hits stop),
        ask_low=1.0945 (hits tp). Ambiguous.
      * tp_in_range=False → ask wicks up only: ask_high=1.1060,
        ask_low=1.0990 (does NOT reach tp). NOT ambiguous.

    Note: short stops check `ask_high >= stop_price`; short tps check
    `ask_low <= tp_price`.
    """
    exit_ask_low = Decimal("1.09450") if tp_in_range else Decimal("1.09900")
    spread = Decimal("0.0002")
    bars = [_quiet_bar(k) for k in range(_ENTRY_BAR_INDEX + 1)]
    bars.append(
        _candle(
            _ENTRY_BAR_INDEX + 1,
            # ask_high = bid_h + spread = 1.10600 → above stop 1.1050
            bid_o=Decimal("1.10000"),
            bid_h=Decimal("1.10580"),
            bid_l=exit_ask_low - spread,
            bid_c=Decimal("1.10200"),
            spread=spread,
        )
    )
    return CandleFrame.from_candles("EUR_USD", "H4", bars)


def test_short_stop_with_tp_in_range_flags_ambiguous(eur_usd):
    strat = _OneShotStrategy(
        fire_at=_FIRE_AT_LEN,
        side="short",
        stop_offset=Decimal("0.0050"),
        take_profit_offset=Decimal("0.0050"),
    )
    frame = _short_setup_with_wide_exit_bar(tp_in_range=True)
    result = _make_engine(strat, eur_usd).run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.exit_reason == "stop"
    assert trade.ambiguous_exit is True
    assert result.metrics.ambiguous_exit_count == 1


def test_short_stop_with_tp_out_of_range_does_not_flag(eur_usd):
    strat = _OneShotStrategy(
        fire_at=_FIRE_AT_LEN,
        side="short",
        stop_offset=Decimal("0.0050"),
        take_profit_offset=Decimal("0.0050"),
    )
    frame = _short_setup_with_wide_exit_bar(tp_in_range=False)
    result = _make_engine(strat, eur_usd).run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.exit_reason == "stop"
    assert trade.ambiguous_exit is False
    assert result.metrics.ambiguous_exit_count == 0


# ---------------------------------------------------------------------------
# Negative cases — what should NEVER be flagged ambiguous
# ---------------------------------------------------------------------------


def test_tp_only_strategy_never_ambiguous(eur_usd):
    """A strategy with no take_profit_price can never produce an ambiguous
    exit — the flag is only set when both a stop AND a tp are in range."""
    strat = _OneShotStrategy(
        fire_at=_FIRE_AT_LEN,
        side="long",
        stop_offset=Decimal("0.0050"),
        take_profit_offset=None,  # no TP
    )
    frame = _long_setup_with_wide_exit_bar(tp_in_range=True)
    result = _make_engine(strat, eur_usd).run(frame)
    assert len(result.trades) == 1
    assert result.trades[0].exit_reason == "stop"
    assert result.trades[0].ambiguous_exit is False
    assert result.metrics.ambiguous_exit_count == 0


def test_eod_exit_never_ambiguous(eur_usd):
    """An EOD close (last-bar fallback) is not a stop or trailing_stop —
    it must NOT flag ambiguous regardless of bar geometry."""
    strat = _OneShotStrategy(
        fire_at=_FIRE_AT_LEN,
        side="long",
        stop_offset=Decimal("0.0500"),  # very wide stop, never hit
        take_profit_offset=Decimal("0.0500"),  # very wide tp, never hit
    )
    # Quiet warmup + entry + one quiet bar; engine will close at EOD.
    frame = CandleFrame.from_candles(
        "EUR_USD",
        "H4",
        [_quiet_bar(k) for k in range(_ENTRY_BAR_INDEX + 2)],
    )
    result = _make_engine(strat, eur_usd).run(frame)
    assert len(result.trades) == 1
    assert result.trades[0].exit_reason == "eod"
    assert result.trades[0].ambiguous_exit is False


def test_time_stop_never_ambiguous(eur_usd):
    """A time-stop fires only when neither stop nor TP is in range — so by
    construction the ambiguous condition cannot hold."""
    strat = _OneShotStrategy(
        fire_at=_FIRE_AT_LEN,
        side="long",
        stop_offset=Decimal("0.0500"),
        take_profit_offset=Decimal("0.0500"),
    )
    # Quiet warmup + entry + 2 quiet bars, max_bars_in_trade=1 → time stop
    # fires on the bar after entry.
    frame = CandleFrame.from_candles(
        "EUR_USD",
        "H4",
        [_quiet_bar(k) for k in range(_ENTRY_BAR_INDEX + 3)],
    )
    result = _make_engine(strat, eur_usd, max_bars_in_trade=1).run(frame)
    assert len(result.trades) == 1
    assert result.trades[0].exit_reason == "time"
    assert result.trades[0].ambiguous_exit is False


# ---------------------------------------------------------------------------
# Trailing-stop detection
# ---------------------------------------------------------------------------


def test_trailing_stop_with_tp_in_range_flags_ambiguous(eur_usd):
    """A trailing stop is also a stop-precedence exit — the ambiguous flag
    must fire when the trailing-stop-exit bar also has tp in range.

    Geometry: 5 quiet warmup bars + entry bar + 10 quiet bars that float
    ABOVE the future trailing-stop level (so the trailing ratchets there
    without the bar's own low triggering it) + 1 wide drop bar that hits
    the trailing stop AND has tp in range.
    """
    strat = _OneShotStrategy(
        fire_at=_FIRE_AT_LEN,
        side="long",
        stop_offset=Decimal("0.0100"),  # wide initial stop at 1.0900
        take_profit_offset=Decimal("0.0050"),  # tp at 1.10500
    )
    bars = [_quiet_bar(k) for k in range(_FIRE_AT_LEN)]
    # Floating bars above the trailing level. With tight quiet bars,
    # ATR-5 stays ~0.00010. Trailing = bid_close - 2*0.0001 = close - 0.0002.
    # Setting bid_c=1.10120 gives trailing ~1.10100; bid_l=1.10115 stays
    # above it so the bar does not trigger its own new stop.
    for k in range(_FIRE_AT_LEN, _FIRE_AT_LEN + 10):
        bars.append(
            _candle(
                k,
                bid_o=Decimal("1.10120"),
                bid_h=Decimal("1.10125"),
                bid_l=Decimal("1.10115"),
                bid_c=Decimal("1.10120"),
            )
        )
    # The wide exit bar: bid_l drops to 1.09400 (below the trailing stop),
    # bid_h rises to 1.10550 (above the tp 1.10500). On this bar:
    #   * trailing update: bid_c=1.09500 → new_stop = 1.09500 - 0.0002 =
    #     1.09480 < current 1.10100 → no ratchet (long ratchets only up);
    #   * range check: bid_l=1.09400 <= 1.10100 → stop fires at 1.10100;
    #   * exit_reason: trailing_stop (stop_price != initial_stop_price);
    #   * ambiguous: bid_h=1.10550 >= tp 1.10500 → True.
    bars.append(
        _candle(
            _FIRE_AT_LEN + 10,
            bid_o=Decimal("1.10100"),
            bid_h=Decimal("1.10550"),
            bid_l=Decimal("1.09400"),
            bid_c=Decimal("1.09500"),
        )
    )
    frame = CandleFrame.from_candles("EUR_USD", "H4", bars)
    engine = BacktestEngine(
        instrument=eur_usd,
        strategy=strat,
        strategy_config={},
        fill_model=_ZERO_FILL,
        starting_equity=Decimal("500"),
        account_currency="USD",
        max_bars_in_trade=999,
        trailing_stop_atr_multiple=2.0,
        atr_lookback=5,
        risk_engine=None,
    )
    result = engine.run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.exit_reason == "trailing_stop"
    assert trade.ambiguous_exit is True


# ---------------------------------------------------------------------------
# Aggregate counter
# ---------------------------------------------------------------------------


def test_ambiguous_exit_count_aggregates_no_trades(eur_usd):
    """Empty trade list → compute_metrics returns ambiguous_exit_count=0,
    matching the populated-trades shape."""
    # A strategy that never fires.
    strat = _OneShotStrategy(
        fire_at=999,
        side="long",
        stop_offset=Decimal("0.0050"),
        take_profit_offset=Decimal("0.0050"),
    )
    frame = _long_setup_with_wide_exit_bar(tp_in_range=True)
    result = _make_engine(strat, eur_usd).run(frame)
    assert result.metrics.trade_count == 0
    assert result.metrics.ambiguous_exit_count == 0
    assert result.metrics.gap_fill_exit_count == 0
    assert result.ambiguous_exit_count == 0
    assert result.gap_fill_exit_count == 0


# ---------------------------------------------------------------------------
# Risk-engine parity — the ambiguous flag must work the same under both
# the legacy direct-sizing path and the risk-engine path.
# ---------------------------------------------------------------------------


def test_ambiguous_exit_with_risk_engine(eur_usd, paper_settings):
    """The risk-engine path uses `plan.stop_loss_price` (= signal.stop_price)
    and `plan.units`; the exit-check block is identical to the legacy
    path. The ambiguous flag must fire the same way.

    Disables the spread + session filters so the synthetic signal isn't
    rejected at the gate (the test exists to prove the EXIT path under
    risk_engine, not to re-test the gate logic).
    """
    from forex_bot.risk.policy import RiskEngine

    # Disable the spread and session filters so the synthetic-data
    # signal makes it through to the engine's exit path. The detection
    # is a property of the exit-check block, not of the gates.
    settings = paper_settings.model_copy(
        update={
            "spread_filter": paper_settings.spread_filter.model_copy(
                update={"enabled": False}
            ),
            "session_filter": paper_settings.session_filter.model_copy(
                update={"enabled": False}
            ),
        }
    )
    risk_engine = RiskEngine(settings, mode="backtest")
    strat = _OneShotStrategy(
        fire_at=_FIRE_AT_LEN,
        side="long",
        stop_offset=Decimal("0.0050"),
        take_profit_offset=Decimal("0.0050"),
    )
    frame = _long_setup_with_wide_exit_bar(tp_in_range=True)
    engine = _make_engine(strat, eur_usd, risk_engine=risk_engine)
    result = engine.run(frame)
    assert len(result.trades) == 1, (
        f"risk-engine rejected the synthetic signal: "
        f"rejection_counts={result.rejection_counts}"
    )
    assert result.trades[0].exit_reason == "stop"
    assert result.trades[0].ambiguous_exit is True


# ---------------------------------------------------------------------------
# Hash invariance — Phase 1 must NOT change config_hash for any of the
# pinned campaign configs from the Phase 0 snapshot.
# ---------------------------------------------------------------------------


def _check_primitives(value, path: str) -> None:
    """Recursively assert value contains only repr-stable primitive types."""
    if isinstance(value, bool | int | float | str | type(None)):
        return
    if isinstance(value, list | tuple):
        for i, v in enumerate(value):
            _check_primitives(v, f"{path}[{i}]")
        return
    if isinstance(value, dict):
        for k, v in value.items():
            _check_primitives(v, f"{path}.{k}")
        return
    raise AssertionError(
        f"non-primitive at {path}: {type(value).__name__} = {value!r}. "
        "Adding non-primitive types to strategy_config can produce "
        "Python-version-dependent repr() and silently drift the "
        "config_hash. Only int/float/str/bool/None/list/dict allowed."
    )


def test_strategy_config_hash_input_types_are_repr_stable():
    """`strategy_config` is hashed via `repr(dict)` — non-primitive values
    (numpy scalars, Path objects, Decimal, etc.) can produce
    Python-version-dependent repr() and drift the hash. Asserts every
    pinned campaign config contains only primitive types.

    Imports the PINNED list from the snapshot script (DRY) so adding a
    config to the pinned list automatically extends this check too.
    """
    from pathlib import Path

    from scripts.snapshot_pre_sprint_hashes import PINNED

    from forex_bot.config import load_settings
    from forex_bot.loops import build_strategies

    repo_root = Path(__file__).resolve().parent.parent.parent
    for label, rel_path in PINNED:
        settings = load_settings(repo_root / rel_path)
        for strat, cfg in build_strategies(settings):
            _check_primitives(cfg, f"{label}:{strat.name}")


def test_hash_dict_key_order_is_stable(eur_usd):
    """Building two engines with the same kwargs must produce a
    byte-identical config_hash. Guards against any future spread-syntax
    change that could perturb dict insertion order."""
    import pandas as pd

    from forex_bot.backtesting.engine import BacktestEngine
    from forex_bot.domain.candles import CandleFrame

    def _make(cfg: dict) -> str:
        engine = BacktestEngine(
            instrument=eur_usd,
            strategy=_OneShotStrategy(
                fire_at=999, side="long",
                stop_offset=Decimal("0.0050"),
                take_profit_offset=None,
            ),
            strategy_config=cfg,
            fill_model=_ZERO_FILL,
            starting_equity=Decimal("500"),
            account_currency="USD",
        )
        return engine.run(
            CandleFrame(instrument="EUR_USD", granularity="H4", df=pd.DataFrame())
        ).config_hash

    cfg = {"version": "0.1.0-test", "ema_fast": 50, "ema_slow": 200}
    h1 = _make(cfg)
    h2 = _make(cfg)
    h3 = _make(dict(cfg))  # constructed differently, identical content
    assert h1 == h2 == h3, f"hash drift: {h1} vs {h2} vs {h3}"


def test_phase1_does_not_change_config_hash_for_pinned_configs():
    """Reproduces the Phase 0 hash snapshot exactly. Failing this test
    means Phase 1 introduced a hash drift — fix the code, not the
    snapshot."""
    import json
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent.parent
    fixture = json.loads(
        (repo_root / "tests" / "fixtures" / "pre_sprint_config_hashes.json")
        .read_text(encoding="utf-8")
    )
    # Re-run the same routine the snapshot script uses.
    from scripts.snapshot_pre_sprint_hashes import PINNED, _hash_for

    from forex_bot.config import load_settings

    for label, rel_path in PINNED:
        settings = load_settings(repo_root / rel_path)
        actual = _hash_for(settings)
        expected = fixture[label]
        assert actual == expected, (
            f"hash regression for {label}: snapshot says {expected}, "
            f"got {actual}. Either fix the code (preferred) or, only if "
            "an intentional refactor changed hash inputs, regenerate the "
            "snapshot with scripts/snapshot_pre_sprint_hashes.py AFTER "
            "verifying with the sprint author."
        )

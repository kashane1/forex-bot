"""Tests for failed_breakout_reversal 0.1.0-c015 (CAMPAIGN_015 candidate).

Verifies the failed-breakout reversal entry: a single H4 bar sweeps the
prior 20-bar range extreme by at least sweep_buffer_atr * ATR(14) and
closes back inside the range; signal fires in the reversal direction.
No EMA / regime / event filter; ADX(14) <= adx_max only.
"""

from __future__ import annotations

import pathlib
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.failed_breakout_reversal import (
    FailedBreakoutReversalStrategy,
)

_CFG: dict = {
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
    "timeframe": "H4",
}


def _candle(
    t: datetime, o: float, h: float, low: float, c: float
) -> Candle:
    half = 0.00005
    return Candle(
        instrument="EUR_USD",
        granularity="H4",
        time=t,
        complete=True,
        volume=1000,
        bid_o=Decimal(str(o - half)), bid_h=Decimal(str(h - half)),
        bid_l=Decimal(str(low - half)), bid_c=Decimal(str(c - half)),
        ask_o=Decimal(str(o + half)), ask_h=Decimal(str(h + half)),
        ask_l=Decimal(str(low + half)), ask_c=Decimal(str(c + half)),
    )


def _frame(rows: list[tuple[float, float, float, float]]) -> CandleFrame:
    t0 = datetime(2025, 1, 1, tzinfo=UTC)
    candles = [
        _candle(t0 + timedelta(hours=4 * i), o, h, low, c)
        for i, (o, h, low, c) in enumerate(rows)
    ]
    return CandleFrame.from_candles("EUR_USD", "H4", candles)


def _ctx(frame: CandleFrame, eur_usd: Instrument, cfg: dict | None = None) -> StrategyContext:
    last = float(frame.df["close"].iloc[-1])
    q = Quote(
        instrument="EUR_USD",
        time=frame.df.index[-1].to_pydatetime(),
        bid=Decimal(str(last - 0.00005)),
        ask=Decimal(str(last + 0.00005)),
    )
    return StrategyContext(
        instrument=eur_usd,
        candles=frame,
        market_state=MarketState(
            quote=q,
            spread_snapshot=SpreadSnapshot(
                instrument="EUR_USD", time=q.time, bid=q.bid, ask=q.ask,
                spread_pips=Decimal("1.0"),
            ),
        ),
        open_positions=[Position(instrument="EUR_USD")],
        config=dict(cfg or _CFG),
    )


# --- helpers to build a base range -----------------------------------------


def _quiet_range_rows(
    n: int, low: float, high: float
) -> list[tuple[float, float, float, float]]:
    """Build n quiet-ish bars that step between `low` and `high` so the
    prior 20-bar range is exactly [low, high]. ATR stays small."""
    rows: list[tuple[float, float, float, float]] = []
    mid = (low + high) / 2.0
    span = (high - low)
    # alternate touches of high and low to set the Donchian extremes.
    for i in range(n):
        # First half bias to high, second half to low.
        if i % 2 == 0:
            rows.append((mid, high, mid - span * 0.10, mid + span * 0.10))
        else:
            rows.append((mid, mid + span * 0.10, low, mid - span * 0.10))
    return rows


# --- tests -----------------------------------------------------------------


def test_warmup_returns_none(eur_usd):
    """Fewer bars than ATR / range warmup → no signal."""
    rows = [(1.10, 1.1010, 1.0990, 1.10) for _ in range(20)]
    sig = FailedBreakoutReversalStrategy().generate_signal(_ctx(_frame(rows), eur_usd))
    assert sig is None


def test_no_signal_without_sweep(eur_usd):
    """Quiet range, last bar stays inside the prior range → no signal."""
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    # Final bar: stays inside range, no sweep.
    rows.append((1.1000, 1.1010, 1.0990, 1.1000))
    sig = FailedBreakoutReversalStrategy().generate_signal(_ctx(_frame(rows), eur_usd))
    assert sig is None


def test_no_signal_if_sweep_closes_outside_breakout_direction(eur_usd):
    """Sweep up AND close above prior_high → this is a successful
    breakout (Donchian-direction), not a failed one. No reversal signal."""
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    # Up-sweep AND close > prior_high (the breakout, not the reversal).
    rows.append((1.1000, 1.1080, 1.0990, 1.1070))
    sig = FailedBreakoutReversalStrategy().generate_signal(_ctx(_frame(rows), eur_usd))
    assert sig is None


def test_short_signal_on_upside_sweep_and_close_back_inside(eur_usd):
    """Bar pokes above prior_high by > sweep_buffer * ATR, then closes
    below prior_high → short signal."""
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    # Sweep above 1.1050 by ~20 pips; close at 1.1040 (inside).
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    sig = FailedBreakoutReversalStrategy().generate_signal(_ctx(_frame(rows), eur_usd))
    assert sig is not None
    assert sig.side == "short"
    assert sig.strategy_name == "failed_breakout_reversal"
    # Stop must sit above the sweep extreme.
    assert sig.stop_price > Decimal("1.10750") - Decimal("0.00001")
    assert sig.features["prior_high"] == 1.1050
    assert sig.features["prior_low"] == 1.0950
    # range_width_atr in pre-commit-allowed band.
    assert 1.25 <= sig.features["range_width_atr"] <= 5.0
    # stop_distance_atr in pre-commit-allowed band.
    assert 0.80 <= sig.features["stop_distance_atr"] <= 2.20


def test_long_signal_on_downside_sweep_and_close_back_inside(eur_usd):
    """Bar pokes below prior_low by > sweep_buffer * ATR, then closes
    above prior_low → long signal."""
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1010, 1.0925, 1.0990))
    sig = FailedBreakoutReversalStrategy().generate_signal(_ctx(_frame(rows), eur_usd))
    assert sig is not None
    assert sig.side == "long"
    # Stop must sit below the sweep extreme.
    assert sig.stop_price < Decimal("1.09250") + Decimal("0.00001")
    assert sig.features["prior_low"] == 1.0950


def test_prior_range_excludes_current_bar(eur_usd):
    """The current bar's own extremes must not be included in
    prior_high / prior_low. We construct a case where including the
    current bar would change prior_high (and thus mask the sweep)."""
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    # Sweep candidate: high reaches 1.1090. If current bar were included
    # in prior_high, prior_high would become 1.1090 and the gate
    # `high[t] > prior_high + sweep_buffer*ATR` could not fire.
    rows.append((1.1000, 1.1090, 1.0990, 1.1010))
    sig = FailedBreakoutReversalStrategy().generate_signal(_ctx(_frame(rows), eur_usd))
    assert sig is not None
    assert sig.features["prior_high"] == 1.1050  # NOT 1.1090
    assert sig.side == "short"


def test_adx_gate_blocks_strong_trend(eur_usd):
    """A strongly-trending input series produces ADX > 20 and the
    failed-breakout setup is blocked, even when the geometry would
    otherwise qualify."""
    rows: list[tuple[float, float, float, float]] = []
    # Trending series — each bar is shifted up by 8 pips, generating a
    # large +DI / -DI divergence and ADX > 20.
    base = 1.0950
    for i in range(80):
        o = base + 0.0008 * i
        h = o + 0.0010
        low = o - 0.0002
        c = o + 0.0008
        rows.append((o, h, low, c))
    # Append a final "sweep-and-reject" candidate against the local prior
    # range. The ADX gate must still block.
    prior_h = max(r[1] for r in rows[-20:])
    rows.append((prior_h, prior_h + 0.0030, prior_h - 0.0005, prior_h - 0.0010))
    sig = FailedBreakoutReversalStrategy().generate_signal(_ctx(_frame(rows), eur_usd))
    assert sig is None


def test_min_range_atr_multiple_gate(eur_usd):
    """If the prior range is too narrow vs ATR, no signal."""
    cfg = dict(_CFG, min_range_atr_multiple=4.99)
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    sig = FailedBreakoutReversalStrategy().generate_signal(
        _ctx(_frame(rows), eur_usd, cfg=cfg)
    )
    assert sig is None


def test_max_range_atr_multiple_gate(eur_usd):
    """If the prior range is too wide vs ATR, no signal."""
    cfg = dict(_CFG, max_range_atr_multiple=1.20)
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    sig = FailedBreakoutReversalStrategy().generate_signal(
        _ctx(_frame(rows), eur_usd, cfg=cfg)
    )
    assert sig is None


def test_min_stop_atr_multiple_gate(eur_usd):
    """If the stop distance (relative to last close) is below
    min_stop_atr_multiple in ATR units, no signal."""
    cfg = dict(_CFG, min_stop_atr_multiple=5.0)
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    sig = FailedBreakoutReversalStrategy().generate_signal(
        _ctx(_frame(rows), eur_usd, cfg=cfg)
    )
    assert sig is None


def test_max_stop_atr_multiple_gate(eur_usd):
    """If the stop distance exceeds max_stop_atr_multiple in ATR units,
    no signal."""
    cfg = dict(_CFG, max_stop_atr_multiple=0.10)
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    sig = FailedBreakoutReversalStrategy().generate_signal(
        _ctx(_frame(rows), eur_usd, cfg=cfg)
    )
    assert sig is None


def test_no_signal_with_existing_open_position(eur_usd):
    """An open position in the same instrument blocks re-entry."""
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    ctx = _ctx(_frame(rows), eur_usd)
    ctx = StrategyContext(
        instrument=ctx.instrument,
        candles=ctx.candles,
        market_state=ctx.market_state,
        open_positions=[Position(instrument="EUR_USD", short_units=Decimal("100"))],
        config=ctx.config,
    )
    assert FailedBreakoutReversalStrategy().generate_signal(ctx) is None


def test_stop_is_beyond_sweep_extreme(eur_usd):
    """For a short signal, stop > sweep high. For a long signal, stop
    < sweep low."""
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    short_sig = FailedBreakoutReversalStrategy().generate_signal(
        _ctx(_frame(rows), eur_usd)
    )
    assert short_sig is not None
    assert short_sig.side == "short"
    assert short_sig.stop_price > Decimal("1.10750")

    rows2 = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows2.append((1.1000, 1.1010, 1.0925, 1.0990))
    long_sig = FailedBreakoutReversalStrategy().generate_signal(
        _ctx(_frame(rows2), eur_usd)
    )
    assert long_sig is not None
    assert long_sig.side == "long"
    assert long_sig.stop_price < Decimal("1.09250")


def test_signal_id_deterministic(eur_usd):
    """Same input → same signal_id across two strategy invocations."""
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    s1 = FailedBreakoutReversalStrategy().generate_signal(
        _ctx(_frame(rows), eur_usd)
    )
    s2 = FailedBreakoutReversalStrategy().generate_signal(
        _ctx(_frame(rows), eur_usd)
    )
    assert s1 is not None and s2 is not None
    assert s1.signal_id == s2.signal_id
    assert s1.strategy_name == "failed_breakout_reversal"
    assert s1.strategy_version == "0.1.0-c015"


def test_sweep_buffer_atr_must_be_strict(eur_usd):
    """If the sweep does not clear `prior_high + sweep_buffer_atr * ATR`,
    no signal — even with a clear close-back-inside."""
    # Set a very large sweep buffer so the modest 25-pip sweep cannot
    # clear it.
    cfg = dict(_CFG, sweep_buffer_atr=100.0)
    rows = _quiet_range_rows(80, low=1.0950, high=1.1050)
    rows.append((1.1000, 1.1075, 1.0990, 1.1010))
    sig = FailedBreakoutReversalStrategy().generate_signal(
        _ctx(_frame(rows), eur_usd, cfg=cfg)
    )
    assert sig is None


def _import_lines(text: str) -> str:
    """Strip module docstrings + comments; return only import/from lines.

    The strategy module's docstring intentionally mentions
    ``forex_bot.broker`` to declare the no-broker invariant; a literal
    substring grep would incorrectly trip on that text. We scan only
    actual ``import`` / ``from`` statements at the top of the module."""
    lines: list[str] = []
    in_docstring = False
    quote = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not in_docstring:
            if line.startswith(('"""', "'''")) and not (
                len(line) > 3 and line.endswith(line[:3])
            ):
                in_docstring = True
                quote = line[:3]
                continue
            if line.startswith(("import ", "from ")):
                lines.append(line)
        else:
            if line.endswith(quote):
                in_docstring = False
    return "\n".join(lines)


def test_no_broker_import_in_strategy_module():
    """The strategy module must not import from forex_bot.broker."""
    src = (
        pathlib.Path(__file__).resolve().parent.parent.parent
        / "src" / "forex_bot" / "strategies" / "failed_breakout_reversal.py"
    )
    imports = _import_lines(src.read_text(encoding="utf-8"))
    assert "forex_bot.broker" not in imports
    assert "from forex_bot.broker" not in imports


def test_no_lean_or_oanda_sdk_import_in_strategy_module():
    """The strategy module must not import LEAN or oandapyV20."""
    src = (
        pathlib.Path(__file__).resolve().parent.parent.parent
        / "src" / "forex_bot" / "strategies" / "failed_breakout_reversal.py"
    )
    imports = _import_lines(src.read_text(encoding="utf-8"))
    assert "oandapyV20" not in imports
    assert "QuantConnect" not in imports
    assert "lean" not in imports.lower()


def test_warmup_bars_required_matches_design():
    """warmup_bars_required is at least range_lookback + atr_lookback."""
    s = FailedBreakoutReversalStrategy()
    assert s.warmup_bars_required() >= 20 + 14


def test_strategy_name_and_version():
    s = FailedBreakoutReversalStrategy()
    assert s.name == "failed_breakout_reversal"
    assert s.version == "0.1.0-c015"
    s2 = FailedBreakoutReversalStrategy(version="0.2.0")
    assert s2.version == "0.2.0"

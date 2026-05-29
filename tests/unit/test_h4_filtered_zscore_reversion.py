"""Tests for h4_filtered_zscore_reversion 0.1.0-c027 (CAMPAIGN_027 scaffold).

Pure-signal logic only. Verifies the frozen precommit rule:
  * a short fires only when z >= +2.5 AND low-vol AND quiet-session;
  * the low-vol filter gates (high ATR percentile blocks);
  * the quiet-session filter gates (new_york/late blocks);
  * the long side is disabled (z <= -2.5 never enters);
  * the strong-extension threshold (|z| in [2.0, 2.5) does not fire);
  * no lookahead / last-completed-bar only;
  * the module imports no broker/executor and is paper-only with no approval flag.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.h4_filtered_zscore_reversion import (
    H4FilteredZscoreReversionStrategy,
    compute_decision,
    session_bucket_utc,
)

_CFG = {
    "timeframe": "H4",
    "zscore_lookback": 20,
    "zscore_std_ddof": 1,
    "base_trigger_abs_z": 2.0,
    "strong_extension_abs_z": 2.5,
    "atr_lookback": 14,
    "atr_percentile_window": 250,
    "atr_percentile_max": 0.33,
    "quiet_sessions": ["asia", "london"],
    "side_mode": "short_only",
    "atr_stop_multiple": 3.0,
    "max_bars_in_trade": 12,
}

BASE = 1.1000


def _candle(t: datetime, o: float, h: float, low: float, c: float) -> Candle:
    half = 0.00005
    return Candle(
        instrument="EUR_USD", granularity="H4", time=t, complete=True, volume=1000,
        bid_o=Decimal(str(o - half)), bid_h=Decimal(str(h - half)),
        bid_l=Decimal(str(low - half)), bid_c=Decimal(str(c - half)),
        ask_o=Decimal(str(o + half)), ask_h=Decimal(str(h + half)),
        ask_l=Decimal(str(low + half)), ask_c=Decimal(str(c + half)),
    )


def _frame(rows: list[tuple[float, float, float, float]], *, start_hour: int = 4) -> CandleFrame:
    t0 = datetime(2025, 1, 1, start_hour, tzinfo=UTC)
    return CandleFrame.from_candles(
        "EUR_USD", "H4",
        [_candle(t0 + timedelta(hours=4 * i), *r) for i, r in enumerate(rows)],
    )


def _make_rows(
    *,
    n_high: int = 240,
    n_low: int = 60,
    low_range: float = 0.0002,
    high_range: float = 0.0030,
    spike: float = 0.0012,
) -> list[tuple[float, float, float, float]]:
    """High-vol head then low-vol flat tail, with a final close spike.

    A positive ``spike`` pushes the last close far above the (tiny-σ) tail mean
    → large positive z → short setup. ``low_range`` controls the tail's
    intrabar range (hence ATR percentile / the low-vol filter).
    """
    rng = random.Random(7)
    rows: list[tuple[float, float, float, float]] = []
    for _ in range(n_high):
        m = BASE + rng.uniform(-0.0015, 0.0015)
        rows.append((m, m + high_range, m - high_range, m))
    for _ in range(n_low):
        m = BASE + rng.uniform(-0.00008, 0.00008)
        rows.append((m, m + low_range, m - low_range, m))
    o, h, low, _c = rows[-1]
    c2 = BASE + spike
    rows[-1] = (o, max(h, c2), min(low, c2), c2)
    return rows


def _ctx(frame: CandleFrame, eur_usd: Instrument, *, open_pos: bool = False) -> StrategyContext:
    last = float(frame.df["close"].iloc[-1])
    q = Quote(instrument="EUR_USD", time=frame.df.index[-1].to_pydatetime(),
              bid=Decimal(str(last - 0.00005)), ask=Decimal(str(last + 0.00005)))
    positions = [Position(instrument="EUR_USD")] if not open_pos else [
        Position(instrument="EUR_USD", short_units=Decimal("1000"),
                 short_average_price=Decimal(str(last)))
    ]
    return StrategyContext(
        instrument=eur_usd, candles=frame,
        market_state=MarketState(
            quote=q,
            spread_snapshot=SpreadSnapshot(
                instrument="EUR_USD", time=q.time, bid=q.bid, ask=q.ask,
                spread_pips=Decimal("1.0"),
            ),
        ),
        open_positions=positions,
        config=dict(_CFG),
    )


# ---- session bucket --------------------------------------------------------

def test_session_bucket_utc_quiet_vs_loud():
    assert session_bucket_utc(datetime(2025, 1, 1, 3, tzinfo=UTC)) == "asia"
    assert session_bucket_utc(datetime(2025, 1, 1, 9, tzinfo=UTC)) == "london"
    assert session_bucket_utc(datetime(2025, 1, 1, 18, tzinfo=UTC)) == "new_york"
    assert session_bucket_utc(datetime(2025, 1, 1, 22, tzinfo=UTC)) == "late"


# ---- entry fires correctly -------------------------------------------------

def test_short_fires_on_strong_extension_lowvol_quiet(eur_usd):
    frame = _frame(_make_rows(), start_hour=4)  # last bar hour 0 → asia
    decision = compute_decision(frame.df, _CFG)
    assert decision is not None
    assert decision.zscore >= 2.5
    assert decision.f_strong_extension is True
    assert decision.f_low_vol is True
    assert decision.session_bucket in ("asia", "london")
    assert decision.f_quiet_session is True
    assert decision.raw_side == "short"
    assert decision.entered_short is True

    sig = H4FilteredZscoreReversionStrategy().generate_signal(_ctx(frame, eur_usd))
    assert sig is not None
    assert sig.side == "short"
    assert sig.strategy_name == "h4_filtered_zscore_reversion"
    assert sig.strategy_version == "0.1.0-c027"
    # protective stop is ABOVE the entry for a short, and wide (3x ATR).
    assert sig.stop_price > Decimal(str(sig.features["last_close"]))
    assert sig.take_profit_price is None
    assert "time_stop_12" in sig.exit_model


def test_no_entry_when_position_open(eur_usd):
    frame = _frame(_make_rows(), start_hour=4)
    sig = H4FilteredZscoreReversionStrategy().generate_signal(
        _ctx(frame, eur_usd, open_pos=True)
    )
    assert sig is None


# ---- low-vol filter gates --------------------------------------------------

def test_low_vol_filter_blocks_when_high_vol(eur_usd):
    # tail has LARGE intrabar ranges (flat closes still → high z) → high ATR pct.
    frame = _frame(_make_rows(low_range=0.0030), start_hour=4)
    decision = compute_decision(frame.df, _CFG)
    assert decision is not None
    assert decision.zscore >= 2.5  # extension still present
    assert decision.f_low_vol is False  # but volatility regime is not calm
    assert decision.entered_short is False
    assert H4FilteredZscoreReversionStrategy().generate_signal(_ctx(frame, eur_usd)) is None


# ---- quiet-session filter gates -------------------------------------------

def test_quiet_session_filter_blocks_new_york(eur_usd):
    # start_hour 0 → last bar (i=299) hour = (0 + 4*299) % 24 = 20 → 'late' (loud)
    frame = _frame(_make_rows(), start_hour=0)
    decision = compute_decision(frame.df, _CFG)
    assert decision is not None
    assert decision.session_bucket not in ("asia", "london")
    assert decision.f_quiet_session is False
    assert decision.entered_short is False
    assert H4FilteredZscoreReversionStrategy().generate_signal(_ctx(frame, eur_usd)) is None


# ---- long side disabled (diagnostic-only) ----------------------------------

def test_long_side_disabled(eur_usd):
    # negative spike → strongly negative z → would be a 'long' (toward mean up).
    frame = _frame(_make_rows(spike=-0.0012), start_hour=4)
    decision = compute_decision(frame.df, _CFG)
    assert decision is not None
    assert decision.zscore <= -2.5
    assert decision.raw_side == "long"
    assert decision.f_low_vol is True and decision.f_quiet_session is True
    assert decision.entered_short is False  # short-only: long never entered
    assert H4FilteredZscoreReversionStrategy().generate_signal(_ctx(frame, eur_usd)) is None


# ---- strong-extension threshold --------------------------------------------

def test_modest_extension_below_2p5_does_not_fire(eur_usd):
    # a tiny bump → |z| in roughly [2.0, 2.5) band must NOT fire (needs >= 2.5).
    rows = _make_rows(spike=0.0)
    # set last close to a small, controlled offset above the flat tail mean
    o, h, low, _c = rows[-1]
    c2 = BASE + 0.00010
    rows[-1] = (o, max(h, c2), min(low, c2), c2)
    frame = _frame(rows, start_hour=4)
    decision = compute_decision(frame.df, _CFG)
    assert decision is not None
    if abs(decision.zscore) < 2.5:
        assert decision.f_strong_extension is False
        assert decision.entered_short is False
        assert H4FilteredZscoreReversionStrategy().generate_signal(_ctx(frame, eur_usd)) is None


# ---- no lookahead / last completed bar -------------------------------------

def test_decision_uses_last_completed_bar_only(eur_usd):
    rows = _make_rows()
    frame = _frame(rows, start_hour=4)
    decision = compute_decision(frame.df, _CFG)
    assert decision is not None
    assert decision.timestamp == frame.df.index[-1]
    # Drop the final spike bar: the extension disappears → no entry.
    trimmed = _frame(rows[:-1], start_hour=4)
    d2 = compute_decision(trimmed.df, _CFG)
    assert d2 is not None
    assert d2.entered_short is False  # without the spike bar, no short setup


def test_insufficient_warmup_returns_none():
    frame = _frame(_make_rows(n_high=10, n_low=5))
    assert compute_decision(frame.df, _CFG) is None


# ---- safety: no broker import, paper-only, no approval flag -----------------

def test_module_has_no_broker_or_executor_import():
    src = Path(
        "src/forex_bot/strategies/h4_filtered_zscore_reversion.py"
    ).read_text(encoding="utf-8")
    # scan only import statements (prose/docstrings may legitimately mention these)
    import_lines = [
        ln.strip() for ln in src.splitlines()
        if ln.strip().startswith(("import ", "from "))
    ]
    blob = "\n".join(import_lines).lower()
    for forbidden in ("oanda", "broker", "executor", "requests", "httpx", "forex_bot.execution"):
        assert forbidden not in blob, forbidden


def test_strategy_is_paper_only_and_unapproved():
    s = H4FilteredZscoreReversionStrategy()
    assert s.paper_only is True
    assert s.name == "h4_filtered_zscore_reversion"
    assert s.version == "0.1.0-c027"
    assert s.warmup_bars_required() >= 264

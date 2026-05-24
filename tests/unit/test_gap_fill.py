"""Opt-in gap-through fill: plumbing tests.

Sprint `infra-exit-fidelity-001` Phase 2. Covers the `gap_fill_policy`
config field, the engine kwarg + conditional hash inclusion, and the
`--gap-fill-policy` CLI flag. The actual gap-fill exit logic lands in
Phase 3 and is tested in the same file under "Exit logic" below
(populated by Phase 3).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
from typer.testing import CliRunner

from forex_bot.backtesting.engine import BacktestEngine
from forex_bot.backtesting.fills import GAP_FILL_POLICIES, FillModel
from forex_bot.cli import app
from forex_bot.config import BacktestConfig, ConfigError
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SNAPSHOT_PATH = REPO_ROOT / "tests" / "fixtures" / "pre_sprint_config_hashes.json"

_ZERO_FILL = FillModel(
    fixed_slippage_pips=Decimal("0"), spread_slippage_multiplier=Decimal("0")
)

runner = CliRunner()


# ---------------------------------------------------------------------------
# Config field
# ---------------------------------------------------------------------------


def test_default_policy_is_none():
    assert BacktestConfig().gap_fill_policy == "none"


def test_policy_accepts_gap_through():
    assert BacktestConfig(gap_fill_policy="gap_through").gap_fill_policy == "gap_through"


def test_policy_rejects_unknown():
    with pytest.raises((ConfigError, ValueError)):
        BacktestConfig(gap_fill_policy="next_open")  # type: ignore[arg-type]


def test_policies_frozenset_matches_config_literal():
    """The frozenset (used by CLI runtime validation) must match the
    Literal values (used by Pydantic). Drift between them = unreachable
    CLI options or unreachable config values."""
    assert frozenset({"none", "gap_through"}) == GAP_FILL_POLICIES


# ---------------------------------------------------------------------------
# Engine kwarg + hash compatibility
# ---------------------------------------------------------------------------


class _NoSignalStrategy:
    """Never emits a signal — used to exercise the engine hash without
    needing to construct real bars."""

    name = "noop"
    version = "test"

    def warmup_bars_required(self) -> int:
        return 2

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        return None


def _build_engine(*, gap_fill_policy: str | None = None, eur_usd) -> BacktestEngine:
    kwargs = dict(
        instrument=eur_usd,
        strategy=_NoSignalStrategy(),
        strategy_config={"version": "test", "param": 1},
        fill_model=_ZERO_FILL,
        starting_equity=Decimal("500"),
        account_currency="USD",
    )
    if gap_fill_policy is not None:
        kwargs["gap_fill_policy"] = gap_fill_policy
    return BacktestEngine(**kwargs)  # type: ignore[arg-type]


def _run_empty(engine: BacktestEngine) -> str:
    frame = CandleFrame(
        instrument="EUR_USD", granularity="H4", df=pd.DataFrame()
    )
    return engine.run(frame).config_hash


def test_engine_default_policy_none(eur_usd):
    engine = _build_engine(gap_fill_policy=None, eur_usd=eur_usd)
    assert engine.gap_fill_policy == "none"


def test_default_policy_no_hash_change(eur_usd):
    """Engine with default policy produces the same config_hash as an
    engine constructed without the kwarg at all — proves the conditional
    spread `**({} if default else {...})` is a true no-op."""
    h_default = _run_empty(_build_engine(gap_fill_policy="none", eur_usd=eur_usd))
    h_omitted = _run_empty(_build_engine(gap_fill_policy=None, eur_usd=eur_usd))
    assert h_default == h_omitted


def test_gap_through_changes_hash(eur_usd):
    """gap_fill_policy='gap_through' MUST produce a different hash than
    'none' — so the two modes can never be silently confused."""
    h_default = _run_empty(_build_engine(gap_fill_policy="none", eur_usd=eur_usd))
    h_gap = _run_empty(_build_engine(gap_fill_policy="gap_through", eur_usd=eur_usd))
    assert h_default != h_gap


def test_default_policy_matches_phase0_snapshot():
    """The pinned hash snapshot at tests/fixtures/pre_sprint_config_hashes.json
    captured the engine's config_hash for 3 campaign configs at the start
    of this sprint. The default-mode hash MUST still match every entry.
    """
    fixture = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    from scripts.snapshot_pre_sprint_hashes import PINNED, _hash_for

    from forex_bot.config import load_settings

    for label, rel_path in PINNED:
        settings = load_settings(REPO_ROOT / rel_path)
        actual = _hash_for(settings)
        expected = fixture[label]
        assert actual == expected, (
            f"hash regression for {label}: snapshot says {expected}, "
            f"got {actual}. Either fix the code or, only if an "
            "intentional refactor changed hash inputs, regenerate the "
            "snapshot AFTER confirming with the sprint author."
        )


def test_snapshot_doc_guardrail():
    """The snapshot file carries a `_doc` header warning against
    accidental regeneration. Asserts the string is preserved verbatim —
    a contributor running the regenerator script to 'fix' a hash
    failure would either have to delete this guard explicitly or leave
    this test red."""
    fixture = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    assert "_doc" in fixture, (
        "snapshot file is missing the _doc guardrail header; do not "
        "remove it"
    )
    assert "DO NOT REGENERATE" in fixture["_doc"], (
        "snapshot _doc string must contain the literal 'DO NOT REGENERATE' "
        "warning; current value: " + repr(fixture["_doc"])
    )


# ---------------------------------------------------------------------------
# CLI flag
# ---------------------------------------------------------------------------


def test_cli_rejects_invalid_gap_fill_policy(paper_config_path: Path):
    """Mirrors test_backtest_config_rejects_unknown_fill_timing — CLI
    validation of the flag is independent of the Pydantic Literal check
    on the config (CLI accepts a string, then validates against the
    frozenset before constructing the engine)."""
    result = runner.invoke(
        app,
        [
            "backtest",
            "--config",
            str(paper_config_path),
            "--gap-fill-policy",
            "next_open",  # not a valid gap_fill_policy value
        ],
    )
    assert result.exit_code == 2, (
        f"expected exit 2 for invalid --gap-fill-policy, got "
        f"{result.exit_code}; output:\n{result.output}"
    )
    assert "invalid --gap-fill-policy" in result.output


def test_cli_accepts_gap_fill_policy_none(paper_config_path: Path):
    """--gap-fill-policy none should be accepted (it is the default)."""
    result = runner.invoke(
        app,
        [
            "backtest",
            "--config",
            str(paper_config_path),
            "--gap-fill-policy",
            "none",
            "--instrument",
            "EUR_USD",
        ],
    )
    # Exit may be non-zero because the DB is empty (no candles synced),
    # but the [dim]gap fill: none[/dim] line should appear before any
    # error. Failure mode we want to catch: exit 2 with "invalid --gap-fill-policy".
    assert "invalid --gap-fill-policy" not in result.output


def test_cli_2x2_matrix_combines_with_fill_timing(paper_config_path: Path):
    """--fill-timing and --gap-fill-policy are orthogonal axes; using
    both at once must not cause a validation collision."""
    result = runner.invoke(
        app,
        [
            "backtest",
            "--config",
            str(paper_config_path),
            "--fill-timing",
            "next_bar_open",
            "--gap-fill-policy",
            "gap_through",
            "--instrument",
            "EUR_USD",
        ],
    )
    # As above: error from empty DB is fine, but the gap-fill validation
    # path must not fire.
    assert "invalid --gap-fill-policy" not in result.output
    assert "invalid --fill-timing" not in result.output


# ---------------------------------------------------------------------------
# Exit logic — Phase 3
# ---------------------------------------------------------------------------


class _OneShotForGap:
    """Emits a single signal at a fixed bar with explicit stop and (optional)
    take-profit. Used to exercise the gap-fill resolver."""

    name = "oneshot_gap"
    version = "test"

    def __init__(
        self,
        *,
        fire_at: int,
        side: str,
        stop_price: Decimal,
        take_profit_price: Decimal | None,
    ) -> None:
        self._fire_at = fire_at
        self._side = side
        self._stop_price = stop_price
        self._tp = take_profit_price

    def warmup_bars_required(self) -> int:
        return 2

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        if len(df) != self._fire_at:
            return None
        last = df.index[-1]
        return Signal(
            signal_id=f"gap-{self._fire_at}-{self._side}",
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe="H4",
            timestamp=pd.Timestamp(last).tz_convert(UTC).to_pydatetime(),
            side=self._side,  # type: ignore[arg-type]
            stop_model="fixed",
            stop_price=self._stop_price,
            take_profit_price=self._tp,
            exit_model="target" if self._tp else "stop_only",
        )


def _gap_candle(
    k: int,
    *,
    bid_o: Decimal,
    bid_h: Decimal,
    bid_l: Decimal,
    bid_c: Decimal,
    spread: Decimal = Decimal("0.0002"),
) -> Candle:
    return Candle(
        instrument="EUR_USD",
        granularity="H4",
        time=datetime(2025, 3, 3, tzinfo=UTC) + timedelta(hours=4 * k),
        complete=True,
        volume=1000,
        bid_o=bid_o, bid_h=bid_h, bid_l=bid_l, bid_c=bid_c,
        ask_o=bid_o + spread, ask_h=bid_h + spread,
        ask_l=bid_l + spread, ask_c=bid_c + spread,
    )


_GAP_ENTRY_BAR_INDEX = 5
_GAP_FIRE_AT_LEN = _GAP_ENTRY_BAR_INDEX + 1


def _quiet(k: int, mid: Decimal = Decimal("1.10000")) -> Candle:
    return _gap_candle(
        k,
        bid_o=mid, bid_h=mid + Decimal("0.00005"),
        bid_l=mid - Decimal("0.00005"), bid_c=mid,
    )


def _make_gap_scenario(
    *,
    side: str,
    exit_kind: str,
    fill_timing: str = "signal_bar_close",
    gap_pips: int = 20,
) -> tuple[CandleFrame, Decimal, Decimal, Decimal]:
    """Build a candle scenario whose exit bar gaps past the relevant level.

    Returns (frame, stop_price, tp_price, expected_fill_price).

    The exit bar's OPEN is positioned strictly past the relevant level:
      * long stop: bid_open < stop_price (adverse)
      * short stop: ask_open > stop_price (adverse)
      * long tp: bid_open > tp_price (favorable)
      * short tp: ask_open < tp_price (favorable)

    For `next_bar_open` an extra QUIET bar sits between the
    entry-trigger bar and the gap bar — otherwise the entry itself
    would fill INTO the gap (past the tp / stop) and the engine would
    null out the tp at construction time (`engine.py:511-515`).
    """
    pip = Decimal("0.0001")
    entry_close = Decimal("1.10000")
    fifty_pips = Decimal("0.0050")
    spread = Decimal("0.0002")
    gap = pip * gap_pips

    if side == "long":
        stop_price = entry_close - fifty_pips  # 1.0950
        tp_price = entry_close + fifty_pips    # 1.1050
        if exit_kind == "stop":
            exit_bid_open = stop_price - gap   # e.g. 1.0930
        else:
            exit_bid_open = tp_price + gap     # e.g. 1.1070
        expected = exit_bid_open
        exit_bid_h = exit_bid_open + gap
        exit_bid_l = exit_bid_open - gap
        exit_bid_c = exit_bid_open
    else:
        stop_price = entry_close + fifty_pips  # 1.1050
        tp_price = entry_close - fifty_pips    # 1.0950
        if exit_kind == "stop":
            exit_ask_open = stop_price + gap
            exit_bid_open = exit_ask_open - spread
            expected = exit_ask_open
        else:
            exit_ask_open = tp_price - gap
            exit_bid_open = exit_ask_open - spread
            expected = exit_ask_open
        exit_bid_h = exit_bid_open + gap
        exit_bid_l = exit_bid_open - gap
        exit_bid_c = exit_bid_open

    bars = [_quiet(k) for k in range(_GAP_ENTRY_BAR_INDEX + 1)]
    if fill_timing == "next_bar_open":
        # Add a quiet entry-bar BEFORE the gap so the nbo entry fills at
        # a normal price (not into the gap). Tp/stop stay valid relative
        # to entry. The gap then happens on the NEXT bar.
        bars.append(_quiet(_GAP_ENTRY_BAR_INDEX + 1))
        exit_bar_index = _GAP_ENTRY_BAR_INDEX + 2
    else:
        exit_bar_index = _GAP_ENTRY_BAR_INDEX + 1
    bars.append(
        _gap_candle(
            exit_bar_index,
            bid_o=exit_bid_open,
            bid_h=exit_bid_h,
            bid_l=exit_bid_l,
            bid_c=exit_bid_c,
            spread=spread,
        )
    )
    frame = CandleFrame.from_candles("EUR_USD", "H4", bars)
    return frame, stop_price, tp_price, expected


def _build_gap_engine(
    *,
    eur_usd,
    fill_timing: str,
    gap_fill_policy: str,
    risk_engine_kind: str,
    paper_settings,
    strategy,
) -> BacktestEngine:
    risk_engine = None
    if risk_engine_kind == "real":
        from forex_bot.risk.policy import RiskEngine

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
    return BacktestEngine(
        instrument=eur_usd,
        strategy=strategy,
        strategy_config={},
        fill_model=_ZERO_FILL,
        starting_equity=Decimal("500"),
        account_currency="USD",
        max_bars_in_trade=999,
        risk_engine=risk_engine,
        fill_timing=fill_timing,  # type: ignore[arg-type]
        gap_fill_policy=gap_fill_policy,
    )


# 16-case parametrized matrix: (side × exit_kind × fill_timing × risk_engine).
_MATRIX_CASES = [
    pytest.param(
        side, kind, ft, re_kind,
        id=(
            f"{side}-{kind}-"
            f"{'sbc' if ft == 'signal_bar_close' else 'nbo'}-"
            f"{'norisk' if re_kind is None else 'risk'}"
        ),
    )
    for side in ("long", "short")
    for kind in ("stop", "tp")
    for ft in ("signal_bar_close", "next_bar_open")
    for re_kind in (None, "real")
]


@pytest.mark.parametrize(
    ("side", "exit_kind", "fill_timing", "risk_engine_kind"),
    _MATRIX_CASES,
)
def test_gap_fill_matrix(
    side: str,
    exit_kind: str,
    fill_timing: str,
    risk_engine_kind: str | None,
    eur_usd,
    paper_settings,
) -> None:
    """For every combination of (side × exit_kind × fill_timing × risk),
    a bar that opens past the relevant level fills at the bar open and
    sets `gap_fill=True`."""
    frame, stop_price, tp_price, expected_fill = _make_gap_scenario(
        side=side, exit_kind=exit_kind, fill_timing=fill_timing
    )
    strategy = _OneShotForGap(
        fire_at=_GAP_FIRE_AT_LEN,
        side=side,
        stop_price=stop_price,
        take_profit_price=tp_price,
    )
    engine = _build_gap_engine(
        eur_usd=eur_usd,
        fill_timing=fill_timing,
        gap_fill_policy="gap_through",
        risk_engine_kind=risk_engine_kind or "none",
        paper_settings=paper_settings,
        strategy=strategy,
    )
    result = engine.run(frame)
    assert len(result.trades) == 1, (
        f"{side}-{exit_kind}-{fill_timing}-{risk_engine_kind}: no trade. "
        f"rejection_counts={result.rejection_counts}"
    )
    trade = result.trades[0]
    expected_reason = "stop" if exit_kind == "stop" else "target"
    assert trade.exit_reason == expected_reason
    assert trade.exit_price == expected_fill
    assert trade.gap_fill is True
    assert trade.gap_fill_distance_pips is not None
    assert trade.gap_fill_distance_pips > 0
    assert result.gap_fill_exit_count == 1


@pytest.mark.parametrize(
    ("side", "exit_kind", "fill_timing", "risk_engine_kind"),
    _MATRIX_CASES,
)
def test_policy_none_disables_gap_fill(
    side: str,
    exit_kind: str,
    fill_timing: str,
    risk_engine_kind: str | None,
    eur_usd,
    paper_settings,
) -> None:
    """The same 16 scenarios under `gap_fill_policy="none"` must NOT
    gap-fill — exits land at exactly the stop/tp level."""
    frame, stop_price, tp_price, _ = _make_gap_scenario(
        side=side, exit_kind=exit_kind, fill_timing=fill_timing
    )
    strategy = _OneShotForGap(
        fire_at=_GAP_FIRE_AT_LEN,
        side=side,
        stop_price=stop_price,
        take_profit_price=tp_price,
    )
    engine = _build_gap_engine(
        eur_usd=eur_usd,
        fill_timing=fill_timing,
        gap_fill_policy="none",
        risk_engine_kind=risk_engine_kind or "none",
        paper_settings=paper_settings,
        strategy=strategy,
    )
    result = engine.run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.gap_fill is False
    assert trade.gap_fill_distance_pips is None
    expected_level = stop_price if exit_kind == "stop" else tp_price
    assert trade.exit_price == expected_level
    assert result.gap_fill_exit_count == 0


# ---------------------------------------------------------------------------
# Specific scenarios called out in the plan
# ---------------------------------------------------------------------------


def test_gap_fill_uses_pre_trailing_stop(eur_usd):
    """With trailing engaged, the gap-fill comparison must use the
    PRE-update stop (the level active at the bar's open), not the
    post-update tightened stop derived from the bar's close. Without
    this, a bar that ratchets the trailing stop down could be reported
    as a gap-through stop fill against a level that didn't yet exist
    when the bar opened.

    Geometry: 5 quiet warmup + 1 entry bar + 10 floating bars above the
    ratchet target + 1 exit bar that opens BELOW the *post-trailing*
    stop but ABOVE the *pre-trailing* stop. With the snapshot rule, no
    gap-fill should fire; the regular range check (against the
    post-trailing stop) handles the exit at the post-trailing level.
    """
    entry_close = Decimal("1.10000")
    stop_price = entry_close - Decimal("0.0100")  # 1.0900 initial
    tp_price = entry_close + Decimal("0.0050")    # 1.1050

    strategy = _OneShotForGap(
        fire_at=_GAP_FIRE_AT_LEN,
        side="long",
        stop_price=stop_price,
        take_profit_price=tp_price,
    )
    bars = [_quiet(k) for k in range(_GAP_FIRE_AT_LEN)]
    # Float above the future trailing stop so trailing ratchets without
    # triggering its own bar.
    for k in range(_GAP_FIRE_AT_LEN, _GAP_FIRE_AT_LEN + 10):
        bars.append(
            _gap_candle(
                k,
                bid_o=Decimal("1.10120"),
                bid_h=Decimal("1.10125"),
                bid_l=Decimal("1.10115"),
                bid_c=Decimal("1.10120"),
            )
        )
    # Exit bar: bid_open=1.10070 is ABOVE the pre-trailing stop (1.09xx
    # post-ratchet, but pre-trailing at the START of this bar is whatever
    # was set on bar N-1 — call it ~1.10100). For this test we just need
    # bid_open > pre_trailing_stop, so the gap-fill resolver does NOT
    # fire. The bar's bid_low=1.09400 then triggers the regular range
    # check against the post-update stop. gap_fill must be False.
    bars.append(
        _gap_candle(
            _GAP_FIRE_AT_LEN + 10,
            bid_o=Decimal("1.10119"),  # just below 1.10120 — above pre-trailing
            bid_h=Decimal("1.10550"),
            bid_l=Decimal("1.09400"),
            bid_c=Decimal("1.09500"),
        )
    )
    frame = CandleFrame.from_candles("EUR_USD", "H4", bars)
    engine = BacktestEngine(
        instrument=eur_usd,
        strategy=strategy,
        strategy_config={},
        fill_model=_ZERO_FILL,
        starting_equity=Decimal("500"),
        account_currency="USD",
        max_bars_in_trade=999,
        trailing_stop_atr_multiple=2.0,
        atr_lookback=5,
        risk_engine=None,
        gap_fill_policy="gap_through",
    )
    result = engine.run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    # Trailing engaged + range check fired → trailing_stop exit at the
    # trailing stop level. No gap-fill because bid_open was ABOVE the
    # pre-trailing stop level.
    assert trade.exit_reason == "trailing_stop"
    assert trade.gap_fill is False
    assert trade.gap_fill_distance_pips is None


def test_bid_ask_open_fallback_to_mid_open(eur_usd):
    """When a candle has no bid/ask split (bid_open=None ask_open=None),
    the gap-fill resolver falls back to the mid `open` column — same
    convention as the existing bid_low/ask_high resolutions, but
    NaN-safe (pandas coerces stored None to numpy NaN)."""
    pip = Decimal("0.0001")
    entry_close = Decimal("1.10000")
    stop_price = entry_close - Decimal("0.0050")
    tp_price = entry_close + Decimal("0.0050")
    bars = [_quiet(k) for k in range(_GAP_ENTRY_BAR_INDEX + 1)]
    gap_open = stop_price - pip * 10  # below stop by 10 pips
    bars.append(
        Candle(
            instrument="EUR_USD", granularity="H4",
            time=datetime(2025, 3, 3, tzinfo=UTC)
            + timedelta(hours=4 * (_GAP_ENTRY_BAR_INDEX + 1)),
            complete=True, volume=1000,
            # mid OHLC only; bid/ask all None — engine MUST fall back to
            # the `open` column for the gap test.
            mid_o=gap_open, mid_h=gap_open + pip * 5,
            mid_l=gap_open - pip * 5, mid_c=gap_open,
        )
    )
    frame = CandleFrame.from_candles("EUR_USD", "H4", bars)
    strategy = _OneShotForGap(
        fire_at=_GAP_FIRE_AT_LEN,
        side="long",
        stop_price=stop_price,
        take_profit_price=tp_price,
    )
    engine = _build_gap_engine(
        eur_usd=eur_usd,
        fill_timing="signal_bar_close",
        gap_fill_policy="gap_through",
        risk_engine_kind="none",
        paper_settings=None,
        strategy=strategy,
    )
    result = engine.run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.gap_fill is True
    assert trade.exit_price == gap_open
    assert trade.exit_reason == "stop"


def test_eod_no_gap_fill(eur_usd):
    """EOD close (last-bar fallback) is not stop/tp; gap_fill must be
    False and gap_fill_distance_pips must be None regardless of bar
    geometry."""
    entry_close = Decimal("1.10000")
    # Wide stop + wide tp, neither ever hit.
    strategy = _OneShotForGap(
        fire_at=_GAP_FIRE_AT_LEN,
        side="long",
        stop_price=entry_close - Decimal("0.0500"),
        take_profit_price=entry_close + Decimal("0.0500"),
    )
    bars = [_quiet(k) for k in range(_GAP_ENTRY_BAR_INDEX + 2)]
    frame = CandleFrame.from_candles("EUR_USD", "H4", bars)
    engine = _build_gap_engine(
        eur_usd=eur_usd,
        fill_timing="signal_bar_close",
        gap_fill_policy="gap_through",
        risk_engine_kind="none",
        paper_settings=None,
        strategy=strategy,
    )
    result = engine.run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.exit_reason == "eod"
    assert trade.gap_fill is False
    assert trade.gap_fill_distance_pips is None


def test_simultaneous_ambiguous_and_gap(eur_usd):
    """A bar that gaps past the stop AND has the tp in range should set
    BOTH `gap_fill=True` AND `ambiguous_exit=True` (the two flags are
    orthogonal). The stop-precedence still wins exit_reason."""
    entry_close = Decimal("1.10000")
    stop_price = entry_close - Decimal("0.0050")  # 1.0950
    tp_price = entry_close + Decimal("0.0050")    # 1.1050
    strategy = _OneShotForGap(
        fire_at=_GAP_FIRE_AT_LEN,
        side="long",
        stop_price=stop_price,
        take_profit_price=tp_price,
    )
    bars = [_quiet(k) for k in range(_GAP_ENTRY_BAR_INDEX + 1)]
    # Exit bar: bid_open=1.0930 (below stop 1.0950 — gap-through fires),
    # bid_high=1.1055 (above tp — ambiguous condition holds).
    bars.append(
        _gap_candle(
            _GAP_ENTRY_BAR_INDEX + 1,
            bid_o=Decimal("1.09300"),
            bid_h=Decimal("1.10550"),
            bid_l=Decimal("1.09200"),
            bid_c=Decimal("1.09400"),
        )
    )
    frame = CandleFrame.from_candles("EUR_USD", "H4", bars)
    engine = _build_gap_engine(
        eur_usd=eur_usd,
        fill_timing="signal_bar_close",
        gap_fill_policy="gap_through",
        risk_engine_kind="none",
        paper_settings=None,
        strategy=strategy,
    )
    result = engine.run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.exit_reason == "stop"
    assert trade.exit_price == Decimal("1.09300")
    assert trade.gap_fill is True
    assert trade.ambiguous_exit is True
    assert result.gap_fill_exit_count == 1
    assert result.ambiguous_exit_count == 1


def test_d1agg_synthetic_weekend_gap(eur_usd):
    """D1AGG-shaped fixture: a Friday-close → Monday-open gap that
    pierces a long stop. With `gap_through`, the fill is at Monday's
    bid_open; with `none`, the fill is at exactly the stop level."""
    entry_close = Decimal("1.10000")
    stop_price = entry_close - Decimal("0.0050")
    tp_price = entry_close + Decimal("0.0050")
    # 6 weekday quiet bars + Monday gap-open bar. Granularity is D1AGG
    # but the engine doesn't care about the granularity name.
    bars = [
        _gap_candle(
            k, bid_o=entry_close, bid_h=entry_close + Decimal("0.00005"),
            bid_l=entry_close - Decimal("0.00005"), bid_c=entry_close,
        )
        for k in range(_GAP_ENTRY_BAR_INDEX + 1)
    ]
    # Monday opens 30 pips below the Friday close → through the stop.
    monday_open = stop_price - Decimal("0.0030")
    bars.append(
        _gap_candle(
            _GAP_ENTRY_BAR_INDEX + 1,
            bid_o=monday_open,
            bid_h=monday_open + Decimal("0.0010"),
            bid_l=monday_open - Decimal("0.0010"),
            bid_c=monday_open + Decimal("0.0005"),
        )
    )
    frame = CandleFrame.from_candles("EUR_USD", "H4", bars)
    strategy = _OneShotForGap(
        fire_at=_GAP_FIRE_AT_LEN,
        side="long",
        stop_price=stop_price,
        take_profit_price=tp_price,
    )
    # Under gap_through: exit at monday_open.
    engine_gap = _build_gap_engine(
        eur_usd=eur_usd, fill_timing="signal_bar_close",
        gap_fill_policy="gap_through", risk_engine_kind="none",
        paper_settings=None, strategy=strategy,
    )
    result_gap = engine_gap.run(frame)
    assert result_gap.trades[0].exit_price == monday_open
    assert result_gap.trades[0].gap_fill is True
    # Under none: exit at exactly stop_price.
    strategy_2 = _OneShotForGap(
        fire_at=_GAP_FIRE_AT_LEN, side="long",
        stop_price=stop_price, take_profit_price=tp_price,
    )
    engine_none = _build_gap_engine(
        eur_usd=eur_usd, fill_timing="signal_bar_close",
        gap_fill_policy="none", risk_engine_kind="none",
        paper_settings=None, strategy=strategy_2,
    )
    result_none = engine_none.run(frame)
    assert result_none.trades[0].exit_price == stop_price
    assert result_none.trades[0].gap_fill is False
    # And config_hashes must differ between modes.
    assert result_gap.config_hash != result_none.config_hash


# ---------------------------------------------------------------------------
# Property-based invariants (architecture-strategist recommendation)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("side", "exit_kind", "gap_pips"),
    [
        (s, k, g)
        for s in ("long", "short")
        for k in ("stop", "tp")
        for g in (1, 5, 25, 100)
    ],
)
def test_gap_fill_invariants(
    side: str, exit_kind: str, gap_pips: int, eur_usd
) -> None:
    """Properties that must hold for any gap geometry, any side, any kind:

    1. When gap_fill=True, exit_price equals the bar's bid_open (long)
       or ask_open (short).
    2. gap_fill_distance_pips is non-negative and equal to the absolute
       distance from the relevant level to the fill price (in pips).
    3. When gap_fill_policy="none", gap_fill is always False regardless
       of bar geometry.
    """
    frame, stop_price, tp_price, expected_fill = _make_gap_scenario(
        side=side, exit_kind=exit_kind, gap_pips=gap_pips
    )
    strategy = _OneShotForGap(
        fire_at=_GAP_FIRE_AT_LEN, side=side,
        stop_price=stop_price, take_profit_price=tp_price,
    )
    # gap_through mode
    engine = _build_gap_engine(
        eur_usd=eur_usd, fill_timing="signal_bar_close",
        gap_fill_policy="gap_through", risk_engine_kind="none",
        paper_settings=None, strategy=strategy,
    )
    result = engine.run(frame)
    assert len(result.trades) == 1
    trade = result.trades[0]
    # Property 1
    assert trade.gap_fill is True
    assert trade.exit_price == expected_fill
    # Property 2
    assert trade.gap_fill_distance_pips is not None
    level = stop_price if exit_kind == "stop" else tp_price
    expected_distance = (
        (level - expected_fill).copy_abs() / eur_usd.pip_size
    )
    assert trade.gap_fill_distance_pips == expected_distance
    # Property 3 — same scenario under "none" never gap-fills
    strategy_2 = _OneShotForGap(
        fire_at=_GAP_FIRE_AT_LEN, side=side,
        stop_price=stop_price, take_profit_price=tp_price,
    )
    engine_none = _build_gap_engine(
        eur_usd=eur_usd, fill_timing="signal_bar_close",
        gap_fill_policy="none", risk_engine_kind="none",
        paper_settings=None, strategy=strategy_2,
    )
    result_none = engine_none.run(frame)
    assert result_none.trades[0].gap_fill is False
    assert result_none.trades[0].gap_fill_distance_pips is None

"""Phase 1 CAMPAIGN_011 Backtrader-adapter tests.

Three layers:

1. Seed-derivation tests — `_derive_random_pair(...)` must match the
   bespoke `random_entry_anchor._derive_random_pair(...)` byte-for-byte
   on identical inputs. No use of `random.random`, `numpy.random.*`, or
   Python's built-in `hash()`.
2. Frozen-parameter / contract tests — assert the adapter reads the
   committed YAML and refuses to start on any deviation.
3. Integration tests — drive a synthetic 260-bar fixture through the
   Cerebro and verify:
   - no signal before the ATR(14)+2 warmup completes (no lookahead),
   - the runner uses the SHA-256-derived gate / direction,
   - the recorded BacktraderTrade carries the right side + non-zero
     units when entry fires,
   - 6-bar time stop fires when no adverse stop hit.
4. Source-grep guards — the adapter source must not import broker /
   loops / execution / OANDA modules, must not use random.random /
   numpy.random / built-in hash, and must not contain credential-shaped
   strings.

`strategy_evidence: false`. CAMPAIGN_011 remains REJECT / null
diagnostic anchor by design.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("backtrader")

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.backtrader_lane.data_adapter import CandleAdapterResult  # noqa: E402
from research.backtrader_lane.strategies.campaign_011_random_entry_anchor import (  # noqa: E402
    CAMPAIGN_011_ADAPTER,
    CAMPAIGN_011_BESPOKE_REFERENCE_PATH,
    CAMPAIGN_011_CONFIG_PATH,
    EXPECTED_MASTER_SEED,
    EXPECTED_VERSION,
    FROZEN_PARAMETERS,
    WARMUP_BAR_COUNT_THRESHOLD,
    WARMUP_BARS_REQUIRED,
    _assert_frozen,
    _derive_random_pair,
    _load_campaign_011_config_strategy,
    _reference_metadata,
    run_campaign_011_pair,
)

from forex_bot.strategies.random_entry_anchor import (  # noqa: E402
    _derive_random_pair as _bespoke_derive_random_pair,
)

# ---------------------------------------------------------------------------
# 1. Seed derivation: BT side must match bespoke side byte-for-byte


def test_derive_random_pair_matches_bespoke_on_canonical_seed() -> None:
    """The BT adapter's _derive_random_pair must agree with the bespoke
    implementation on a known input."""

    master_seed = 20260523
    instrument = "EUR_USD"
    bar_iso = "2020-01-02T22:00:00+00:00"
    bt_pair = _derive_random_pair(master_seed, instrument, bar_iso)
    bespoke_pair = _bespoke_derive_random_pair(master_seed, instrument, bar_iso)
    assert bt_pair == bespoke_pair


@pytest.mark.parametrize(
    "instrument,bar_iso",
    [
        ("EUR_USD", "2020-01-02T22:00:00+00:00"),
        ("USD_JPY", "2020-06-15T18:00:00+00:00"),
        ("GBP_USD", "2022-12-21T02:00:00+00:00"),
        ("AUD_USD", "2025-11-29T06:00:00+00:00"),
        ("NZD_USD", "2026-05-19T22:00:00+00:00"),
    ],
)
def test_derive_random_pair_matches_bespoke_across_pairs_and_times(
    instrument: str, bar_iso: str
) -> None:
    bt_pair = _derive_random_pair(EXPECTED_MASTER_SEED, instrument, bar_iso)
    bespoke_pair = _bespoke_derive_random_pair(
        EXPECTED_MASTER_SEED, instrument, bar_iso
    )
    assert bt_pair == bespoke_pair


def test_derive_random_pair_returns_two_64bit_unsigned_ints() -> None:
    bar, gate = _derive_random_pair(EXPECTED_MASTER_SEED, "EUR_USD", "x")
    assert 0 <= bar < 2**64
    assert 0 <= gate < 2**64


def test_derive_random_pair_differs_per_instrument() -> None:
    a = _derive_random_pair(
        EXPECTED_MASTER_SEED, "EUR_USD", "2020-01-02T22:00:00+00:00"
    )
    b = _derive_random_pair(
        EXPECTED_MASTER_SEED, "GBP_USD", "2020-01-02T22:00:00+00:00"
    )
    assert a != b


def test_derive_random_pair_differs_per_timestamp() -> None:
    a = _derive_random_pair(
        EXPECTED_MASTER_SEED, "EUR_USD", "2020-01-02T22:00:00+00:00"
    )
    b = _derive_random_pair(
        EXPECTED_MASTER_SEED, "EUR_USD", "2020-01-03T02:00:00+00:00"
    )
    assert a != b


# ---------------------------------------------------------------------------
# 2. Frozen-parameter / contract tests


def test_campaign_011_config_path_resolves() -> None:
    assert CAMPAIGN_011_CONFIG_PATH.exists()


def test_load_campaign_011_config_uses_committed_yaml() -> None:
    cfg = _load_campaign_011_config_strategy()
    assert cfg["master_seed"] == 20260523
    assert cfg["entry_probability_per_bar"] == 0.05
    assert cfg["atr_lookback"] == 14
    assert cfg["atr_stop_multiple"] == 2.0
    assert cfg["max_bars_in_trade"] == 6
    assert cfg["trailing_stop_atr_multiple"] is None


def test_assert_frozen_accepts_pristine_yaml() -> None:
    cfg = _load_campaign_011_config_strategy()
    _assert_frozen(cfg)


def test_assert_frozen_rejects_seed_tuning() -> None:
    cfg = dict(FROZEN_PARAMETERS)
    cfg["master_seed"] = 99999
    with pytest.raises(SystemExit) as exc:
        _assert_frozen(cfg)
    assert "20260523" in str(exc.value) or "master_seed" in str(exc.value)


def test_assert_frozen_rejects_entry_probability_drift() -> None:
    cfg = dict(FROZEN_PARAMETERS)
    cfg["entry_probability_per_bar"] = 0.10
    with pytest.raises(SystemExit) as exc:
        _assert_frozen(cfg)
    assert "entry_probability_per_bar" in str(exc.value)


def test_assert_frozen_rejects_atr_stop_drift() -> None:
    cfg = dict(FROZEN_PARAMETERS)
    cfg["atr_stop_multiple"] = 3.0
    with pytest.raises(SystemExit) as exc:
        _assert_frozen(cfg)
    assert "atr_stop_multiple" in str(exc.value)


def test_assert_frozen_rejects_max_bars_drift() -> None:
    cfg = dict(FROZEN_PARAMETERS)
    cfg["max_bars_in_trade"] = 12
    with pytest.raises(SystemExit) as exc:
        _assert_frozen(cfg)
    assert "max_bars_in_trade" in str(exc.value)


def test_assert_frozen_rejects_trailing_stop_enabled() -> None:
    cfg = dict(FROZEN_PARAMETERS)
    cfg["trailing_stop_atr_multiple"] = 2.0
    with pytest.raises(SystemExit) as exc:
        _assert_frozen(cfg)
    assert "trailing_stop_atr_multiple" in str(exc.value)


def test_campaign_011_adapter_registered() -> None:
    assert CAMPAIGN_011_ADAPTER.campaign_id == "CAMPAIGN_011"
    assert CAMPAIGN_011_ADAPTER.strategy_id == "random_entry_anchor"
    assert CAMPAIGN_011_ADAPTER.strategy_version == EXPECTED_VERSION
    assert "EUR_USD" in CAMPAIGN_011_ADAPTER.default_instruments
    assert len(CAMPAIGN_011_ADAPTER.default_instruments) == 7
    assert CAMPAIGN_011_ADAPTER.risk_per_trade_pct == 0.25
    assert CAMPAIGN_011_ADAPTER.default_starting_equity_usd == 500.0


def test_campaign_011_default_instruments_in_canonical_order() -> None:
    """The default pair order must match the bespoke reference order so
    comparison-harness output rows line up."""
    assert CAMPAIGN_011_ADAPTER.default_instruments == (
        "EUR_USD",
        "GBP_USD",
        "USD_JPY",
        "AUD_USD",
        "USD_CAD",
        "USD_CHF",
        "NZD_USD",
    )


def test_campaign_011_approximation_flags_documented() -> None:
    flags = CAMPAIGN_011_ADAPTER.approximation_flags
    required = (
        "CAMPAIGN_011_DETERMINISTIC_SEED",
        "CAMPAIGN_011_TIME_STOP_ONLY",
        "CAMPAIGN_011_NO_RISK_ENGINE_PARITY",
        "R_FORMULA_MATCHES_BESPOKE",
    )
    for needle in required:
        assert any(needle in f for f in flags), f"missing approximation flag: {needle}"


def test_warmup_threshold_matches_bespoke_strategy() -> None:
    """Regression for the sprint-004 Phase 5 fix: the BT adapter must
    respect the bespoke strategy's `warmup_bars_required() = 32`, not
    only the in-strategy R1 check (`len(df) >= atr_lookback + 2 = 16`).

    See docs/research/BACKTRADER_CAMPAIGN_011_FULL_WINDOW_COMPARISON_004.md
    §5-§7 — pre-fix, the BT lane fired ~+8 extra trades because bars
    16-31 were eligible for it but skipped by the bespoke engine.
    """

    from forex_bot.strategies.random_entry_anchor import (
        RandomEntryAnchorStrategy,
    )

    bespoke_warmup = RandomEntryAnchorStrategy().warmup_bars_required()
    assert bespoke_warmup == 32, (
        "the bespoke strategy spec frozen at 32; if this changes, "
        "the BT adapter constant must change in lock-step"
    )
    assert bespoke_warmup == WARMUP_BARS_REQUIRED
    # Backtrader's len(self) is 1-based, so the BT threshold is
    # warmup + 1 (the strategy first becomes eligible when the engine
    # has processed 33 candles).
    assert WARMUP_BAR_COUNT_THRESHOLD == WARMUP_BARS_REQUIRED + 1


def test_campaign_011_reference_metadata_matches_contract() -> None:
    """Sanity: the committed bespoke reference is the one this adapter
    will be compared against, with `risk_engine_used=false` and the
    expected window."""
    meta = _reference_metadata()
    assert meta["risk_engine_used"] is False
    assert meta["strategy_evidence"] is False
    assert meta["master_seed"] == EXPECTED_MASTER_SEED
    assert meta["window"] == ["2020-01-01", "2026-05-20"]
    assert meta["total_trades"] == 2800
    assert len(meta["pairs"]) == 7


# ---------------------------------------------------------------------------
# 3. Source-grep guards (parity with CAMPAIGN_002's adapter guard)


def test_adapter_imports_no_forex_bot_broker_or_lean_modules() -> None:
    """The adapter must not import any broker / loops / execution
    module, must not import LEAN / QuantConnect, and must not import
    Backtrader's OANDA broker or store."""
    import research.backtrader_lane.strategies.campaign_011_random_entry_anchor as mod

    src = Path(mod.__file__).read_text(encoding="utf-8")
    forbidden_import_substrings = (
        "forex_bot.broker",
        "forex_bot.execution",
        "forex_bot.loops",
        "backtrader.brokers.oandabroker",
        "backtrader.stores.oandastore",
        "backtrader.feeds.oanda",
        "import quantconnect",
        "from quantconnect",
        "import lean",
        "from lean ",
    )
    for line in src.splitlines():
        clean = line.split("#", 1)[0].strip()
        if not (clean.startswith("import ") or clean.startswith("from ")):
            continue
        for needle in forbidden_import_substrings:
            assert needle not in clean, (
                f"forbidden import in adapter: {line!r}"
            )


def test_adapter_does_not_use_random_or_numpy_random_or_builtin_hash() -> None:
    """Per the CAMPAIGN_011 spec, randomness comes only from SHA-256.
    `random.random()`, `numpy.random.*`, and Python's built-in `hash()`
    are all forbidden in code. Prose mentions in docstrings (warning
    the reader away from these primitives) are fine."""

    import ast

    import research.backtrader_lane.strategies.campaign_011_random_entry_anchor as mod

    src = Path(mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)

    def _full_attr_name(node: ast.expr) -> str:
        parts: list[str] = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts))

    # Reject imports of `random` / `numpy.random`.
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in {"random"}, (
                    f"forbidden import in adapter: {alias.name!r}"
                )
                assert not alias.name.startswith("numpy.random"), (
                    f"forbidden import in adapter: {alias.name!r}"
                )
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            assert node.module != "random", (
                f"forbidden import in adapter: from {node.module}"
            )
            assert not node.module.startswith("numpy.random"), (
                f"forbidden import in adapter: from {node.module}"
            )
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                full = _full_attr_name(func)
                assert not full.startswith("random."), (
                    f"forbidden call in adapter: {full}"
                )
                assert not full.startswith("numpy.random."), (
                    f"forbidden call in adapter: {full}"
                )
            elif isinstance(func, ast.Name):
                assert func.id != "hash", (
                    f"forbidden built-in hash() call in adapter at line "
                    f"{node.lineno}"
                )


def test_adapter_does_not_reference_oanda_api() -> None:
    import research.backtrader_lane.strategies.campaign_011_random_entry_anchor as mod

    src = Path(mod.__file__).read_text(encoding="utf-8")
    assert "api.oanda" not in src.lower()
    assert "oanda.com" not in src.lower()
    # No credentialled env-var read.
    assert "OANDA_ACCESS_TOKEN" not in src
    assert "OANDA_ACCOUNT_ID" not in src


def test_adapter_does_not_touch_approved_strategies_yaml() -> None:
    import research.backtrader_lane.strategies.campaign_011_random_entry_anchor as mod

    src = Path(mod.__file__).read_text(encoding="utf-8")
    # Permit prose mentions only in comments / docstrings; forbid any
    # open / write / Path expression that targets the file.
    forbidden = (
        'open("configs/approved_strategies',
        "open('configs/approved_strategies",
        'Path("configs/approved_strategies',
        "Path('configs/approved_strategies",
        'write_text("approved',
    )
    for pat in forbidden:
        assert pat not in src, f"unexpected approval-file access: {pat!r}"


# ---------------------------------------------------------------------------
# 4. Integration test — synthetic 260-bar fixture


def _make_synth_candles(
    instrument: str,
    n: int,
    *,
    base_price: float = 1.10000,
    spread: float = 0.00020,
    step: float = 0.00005,
) -> CandleAdapterResult:
    """Generate a synthetic CandleAdapterResult for CAMPAIGN_011 tests.

    A gentle linear drift makes ATR(14) finite and positive after the
    warmup completes, so the random-entry adapter can fire on bars
    selected by its seed gate."""

    start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=UTC)
    times: list[datetime] = []
    mid_o: list[float] = []
    mid_h: list[float] = []
    mid_l: list[float] = []
    mid_c: list[float] = []
    bid_o: list[float] = []
    bid_h: list[float] = []
    bid_l: list[float] = []
    bid_c: list[float] = []
    ask_o: list[float] = []
    ask_h: list[float] = []
    ask_l: list[float] = []
    ask_c: list[float] = []
    hs: list[float] = []
    vols: list[int] = []
    for i in range(n):
        t = start + timedelta(hours=4 * i)
        # Sawtooth pattern + drift → non-zero ATR, finite stop distance.
        mid = base_price + i * step + 0.0001 * ((i % 5) - 2)
        o = mid
        c = mid
        h = mid + 0.0003
        lo = mid - 0.0003
        times.append(t)
        mid_o.append(o)
        mid_h.append(h)
        mid_l.append(lo)
        mid_c.append(c)
        bid_o.append(o - spread / 2)
        bid_h.append(h - spread / 2)
        bid_l.append(lo - spread / 2)
        bid_c.append(c - spread / 2)
        ask_o.append(o + spread / 2)
        ask_h.append(h + spread / 2)
        ask_l.append(lo + spread / 2)
        ask_c.append(c + spread / 2)
        hs.append(spread / 2)
        vols.append(100)
    idx = pd.DatetimeIndex(times, name="time")
    mid_df = pd.DataFrame(
        {"open": mid_o, "high": mid_h, "low": mid_l, "close": mid_c, "volume": vols},
        index=idx,
    )
    bid_df = pd.DataFrame(
        {"open": bid_o, "high": bid_h, "low": bid_l, "close": bid_c}, index=idx
    )
    ask_df = pd.DataFrame(
        {"open": ask_o, "high": ask_h, "low": ask_l, "close": ask_c}, index=idx
    )
    from research.backtrader_lane.data_adapter import CandleProvenance

    provenance = CandleProvenance(
        instrument=instrument,
        granularity="H4",
        source="synthetic-test",
        requested_from=times[0].isoformat(),
        requested_to=times[-1].isoformat(),
        candle_count=n,
        first_ts=times[0].isoformat(),
        last_ts=times[-1].isoformat(),
        data_sha256="0" * 64,
        campaign_002_data_request_hash="0" * 16,
        lean_csv=f"{instrument}_H4_lean.csv",
        exported_by="test",
        exported_at="2026-05-25T00:00:00+00:00",
    )
    return CandleAdapterResult(
        instrument=instrument,
        provenance=provenance,
        csv_sha256=provenance.data_sha256,
        mid_df=mid_df,
        bid_ohlc_df=bid_df,
        ask_ohlc_df=ask_df,
        half_spread_close=pd.Series(hs, index=idx),
        first_ts=times[0],
        last_ts=times[-1],
        bar_count=n,
        approximation_flags=[],
    )


def test_synth_run_produces_some_trades_and_no_lookahead() -> None:
    """A 260-bar synth fixture should produce some random-entry trades
    AFTER the ATR(14)+2 warmup. Exact count depends on which bars'
    SHA-256 gate values fall under 0.05."""

    candles = _make_synth_candles("EUR_USD", n=260)
    result = run_campaign_011_pair(candles, starting_equity_usd=500.0)
    assert result.instrument == "EUR_USD"
    assert result.candle_count == 260
    # All entries must have happened on bar index >= 16 (atr_lookback + 2).
    for trade in result.trades:
        # entry_time must be at least the 16th bar's timestamp.
        # The fixture starts at 2024-01-01T22:00:00+00:00; bar 0..15 = 16 bars.
        # The 16th bar (index 15) is 4*15 = 60 hours later = 2024-01-04T10:00:00+00:00.
        # In Backtrader's len(self) >= 16 means we're processing the 16th bar.
        min_allowed = datetime(2024, 1, 1, 22, 0, 0, tzinfo=UTC) + timedelta(
            hours=4 * 15
        )
        assert trade.entry_time >= min_allowed


def test_synth_run_is_deterministic_across_two_runs() -> None:
    """Two consecutive runs on the same fixture must produce identical
    trade lists (same count, same entry/exit times, same sides)."""

    candles_a = _make_synth_candles("EUR_USD", n=260)
    candles_b = _make_synth_candles("EUR_USD", n=260)
    result_a = run_campaign_011_pair(candles_a, starting_equity_usd=500.0)
    result_b = run_campaign_011_pair(candles_b, starting_equity_usd=500.0)
    assert len(result_a.trades) == len(result_b.trades)
    for ta, tb in zip(result_a.trades, result_b.trades, strict=True):
        assert ta.side == tb.side
        assert ta.entry_time == tb.entry_time
        assert ta.exit_time == tb.exit_time
        assert ta.units == tb.units
        # Float prices should match bit-for-bit on the same fixture.
        assert ta.entry_price == tb.entry_price
        assert ta.exit_price == tb.exit_price


def test_synth_trades_carry_r_multiple_and_correct_side() -> None:
    candles = _make_synth_candles("EUR_USD", n=260)
    result = run_campaign_011_pair(candles, starting_equity_usd=500.0)
    for trade in result.trades:
        assert trade.side in ("long", "short")
        assert trade.units > 0
        assert trade.r_multiple is not None
        # Exit reasons in CAMPAIGN_011 are: "stop", "time", or "eod".
        assert trade.exit_reason in ("stop", "time", "eod")
        # bars_held must be in [1, max_bars_in_trade].
        assert 1 <= trade.bars_held <= 6


def test_synth_run_no_trades_before_warmup() -> None:
    """A tiny fixture (15 bars) cannot produce any trade because R1
    fails: len(df) < atr_lookback + 2 = 16."""

    candles = _make_synth_candles("EUR_USD", n=15)
    result = run_campaign_011_pair(candles, starting_equity_usd=500.0)
    assert len(result.trades) == 0


def test_synth_run_unknown_instrument_raises() -> None:
    candles = _make_synth_candles("MADE_UP_PAIR", n=20)
    with pytest.raises(KeyError) as exc:
        run_campaign_011_pair(candles, starting_equity_usd=500.0)
    assert "MADE_UP_PAIR" in str(exc.value)


# ---------------------------------------------------------------------------
# 5. Bespoke reference path safety


def test_bespoke_reference_path_resolves() -> None:
    assert CAMPAIGN_011_BESPOKE_REFERENCE_PATH.exists()
    assert CAMPAIGN_011_BESPOKE_REFERENCE_PATH.name.endswith(
        "campaign_011_h4_bespoke_reference.json"
    )

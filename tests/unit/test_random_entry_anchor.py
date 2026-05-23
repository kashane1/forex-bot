"""Unit tests for ``RandomEntryAnchorStrategy`` (CAMPAIGN_011 research candidate).

These tests are research-only and prove the null-model strategy is
**deterministic, no-lookahead, and structurally safe**. A passing suite is
NOT strategy approval; the candidate is a **null model by design** and
cannot be added to ``configs/approved_strategies.yaml`` under any
circumstance. ``configs/approved_strategies.yaml`` remains
``approved: []``; the strategy is not enabled in any active loop.

See:
- docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md
- docs/research/NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md
"""

from __future__ import annotations

import inspect
import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from forex_bot.config import (
    RandomEntryAnchorStrategyConfig,
    StrategyConfig,
)
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.random_entry_anchor import (
    RandomEntryAnchorStrategy,
    _derive_random_pair,
)

# ---------------------------------------------------------------------------
# Constants + helpers (mirrors test_session_breakout.py patterns)
# ---------------------------------------------------------------------------


# Use NY-standard H4 alignment: UTC bar opens at 22, 02, 06, 10, 14, 18.
_H4_HOURS_UTC: tuple[int, ...] = (22, 2, 6, 10, 14, 18)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STRATEGY_SOURCE = (
    _REPO_ROOT / "src" / "forex_bot" / "strategies" / "random_entry_anchor.py"
).read_text(encoding="utf-8")


def _bar_time(base: datetime, idx: int) -> datetime:
    return base + timedelta(hours=4 * idx)


def _make_candle(
    time: datetime,
    *,
    open_: float,
    high: float,
    low: float,
    close: float,
    complete: bool = True,
) -> Candle:
    spread = Decimal("0.00010")
    mid_o = Decimal(str(round(open_, 5)))
    mid_h = Decimal(str(round(high, 5)))
    mid_l = Decimal(str(round(low, 5)))
    mid_c = Decimal(str(round(close, 5)))
    return Candle(
        instrument="EUR_USD",
        granularity="H4",
        time=time,
        complete=complete,
        volume=1000,
        bid_o=mid_o - spread / 2,
        bid_h=mid_h - spread / 2,
        bid_l=mid_l - spread / 2,
        bid_c=mid_c - spread / 2,
        ask_o=mid_o + spread / 2,
        ask_h=mid_h + spread / 2,
        ask_l=mid_l + spread / 2,
        ask_c=mid_c + spread / 2,
    )


def _build_h4_frame(
    n: int,
    *,
    base_close: float = 1.0800,
    range_size: float = 0.0010,
    start: datetime | None = None,
) -> CandleFrame:
    """A simple H4 frame of n identical-spec bars. ATR converges to range_size."""
    base = start or datetime(2025, 1, 6, _H4_HOURS_UTC[0], tzinfo=UTC)
    candles: list[Candle] = []
    for i in range(n):
        t = _bar_time(base, i)
        candles.append(
            _make_candle(
                t,
                open_=base_close,
                high=base_close + range_size / 2,
                low=base_close - range_size / 2,
                close=base_close,
            )
        )
    return CandleFrame.from_candles("EUR_USD", "H4", candles)


def _ctx(
    frame: CandleFrame,
    instrument: Instrument,
    *,
    config: dict,
    open_position_units: Decimal = Decimal("0"),
) -> StrategyContext:
    last_close = float(frame.df["close"].iloc[-1]) if len(frame) else 1.0800
    quote_time = (
        frame.df.index[-1].to_pydatetime()
        if len(frame)
        else datetime(2025, 1, 1, tzinfo=UTC)
    )
    quote = Quote(
        instrument="EUR_USD",
        time=quote_time,
        bid=Decimal(str(last_close - 0.0001)),
        ask=Decimal(str(last_close + 0.0001)),
    )
    position = Position(
        instrument="EUR_USD",
        long_units=open_position_units,
    )
    return StrategyContext(
        instrument=instrument,
        candles=frame,
        market_state=MarketState(
            quote=quote,
            spread_snapshot=SpreadSnapshot(
                instrument="EUR_USD",
                time=quote.time,
                bid=quote.bid,
                ask=quote.ask,
                spread_pips=Decimal("2.0"),
            ),
        ),
        open_positions=[position],
        config=config,
    )


def _default_cfg(**overrides) -> dict:
    cfg = {
        "version": "0.1.0-c011",
        "timeframe": "H4",
        "master_seed": 20260523,
        # Use entry_probability = 1.0 - epsilon so the gate is ~always met
        # in the small fixture frames; the 0.05 value is enforced for the
        # frozen-parameter config separately.
        "entry_probability_per_bar": 0.999999,
        "atr_lookback": 14,
        "atr_stop_multiple": 2.0,
        "trailing_stop_atr_multiple": None,
        "max_bars_in_trade": 6,
        "min_atr_pips": {},
    }
    cfg.update(overrides)
    return cfg


# ---------------------------------------------------------------------------
# 1. Config defaults / validation (≥ 6 cases)
# ---------------------------------------------------------------------------


def test_default_config_matches_frozen_spec():
    c = RandomEntryAnchorStrategyConfig(version="0.1.0-c011")
    assert c.version == "0.1.0-c011"
    assert c.timeframe == "H4"
    assert c.master_seed == 20260523
    assert c.entry_probability_per_bar == 0.05
    assert c.atr_lookback == 14
    assert c.atr_stop_multiple == 2.0
    assert c.trailing_stop_atr_multiple is None
    assert c.max_bars_in_trade == 6
    assert c.min_atr_pips == {}


def test_config_rejects_entry_probability_at_or_below_zero():
    for bad in (-0.5, 0.0):
        with pytest.raises(
            ValidationError, match="entry_probability_per_bar must be in"
        ):
            RandomEntryAnchorStrategyConfig(
                version="0.1.0-c011", entry_probability_per_bar=bad
            )


def test_config_rejects_entry_probability_at_or_above_one():
    for bad in (1.0, 1.5):
        with pytest.raises(
            ValidationError, match="entry_probability_per_bar must be in"
        ):
            RandomEntryAnchorStrategyConfig(
                version="0.1.0-c011", entry_probability_per_bar=bad
            )


def test_config_rejects_atr_lookback_below_two():
    for bad in (-1, 0, 1):
        with pytest.raises(ValidationError, match="atr_lookback must be"):
            RandomEntryAnchorStrategyConfig(
                version="0.1.0-c011", atr_lookback=bad
            )


def test_config_rejects_non_positive_atr_stop_multiple():
    for bad in (-1.0, 0.0):
        with pytest.raises(ValidationError, match="atr_stop_multiple must be"):
            RandomEntryAnchorStrategyConfig(
                version="0.1.0-c011", atr_stop_multiple=bad
            )


def test_config_rejects_non_positive_max_bars_in_trade():
    for bad in (-1, 0):
        with pytest.raises(ValidationError, match="max_bars_in_trade must be"):
            RandomEntryAnchorStrategyConfig(
                version="0.1.0-c011", max_bars_in_trade=bad
            )


def test_config_rejects_non_null_trailing_stop_in_v1():
    with pytest.raises(
        ValidationError, match="trailing_stop_atr_multiple must be None"
    ):
        RandomEntryAnchorStrategyConfig(
            version="0.1.0-c011", trailing_stop_atr_multiple=1.5
        )


def test_config_rejects_extra_fields():
    """extra='forbid' is the standing convention for every StrategyConfig."""
    with pytest.raises(ValidationError):
        RandomEntryAnchorStrategyConfig(
            version="0.1.0-c011", undocumented_extra_field="surprise"
        )


def test_strategy_config_enabled_check_rejects_missing_random_entry_anchor():
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "strategy.random_entry_anchor config required when enabled"
        ),
    ):
        StrategyConfig(enabled=["random_entry_anchor"])


# ---------------------------------------------------------------------------
# 2. Determinism — seed dependence (≥ 4 cases)
# ---------------------------------------------------------------------------


def test_derive_random_pair_is_deterministic_for_same_inputs():
    a = _derive_random_pair(20260523, "EUR_USD", "2025-01-07T06:00:00+00:00")
    b = _derive_random_pair(20260523, "EUR_USD", "2025-01-07T06:00:00+00:00")
    assert a == b
    assert len(a) == 2
    # Each value is a 64-bit unsigned int.
    assert 0 <= a[0] < 2**64
    assert 0 <= a[1] < 2**64


def test_derive_random_pair_changes_with_master_seed():
    a = _derive_random_pair(20260523, "EUR_USD", "2025-01-07T06:00:00+00:00")
    b = _derive_random_pair(20260524, "EUR_USD", "2025-01-07T06:00:00+00:00")
    assert a != b
    # Independent halves both differ with overwhelming probability.
    assert a[0] != b[0]
    assert a[1] != b[1]


def test_derive_random_pair_changes_with_instrument():
    a = _derive_random_pair(20260523, "EUR_USD", "2025-01-07T06:00:00+00:00")
    b = _derive_random_pair(20260523, "GBP_USD", "2025-01-07T06:00:00+00:00")
    assert a != b


def test_derive_random_pair_changes_with_timestamp():
    a = _derive_random_pair(20260523, "EUR_USD", "2025-01-07T06:00:00+00:00")
    b = _derive_random_pair(20260523, "EUR_USD", "2025-01-07T10:00:00+00:00")
    assert a != b


def test_derive_random_pair_signature_contains_no_price_args():
    """No-lookahead structural rail: the seed input takes only
    (master_seed, instrument_name, bar_timestamp_iso) — never any
    price field or ATR. Enforces R3 §5 of the implementation spec."""
    sig = inspect.signature(_derive_random_pair)
    assert list(sig.parameters.keys()) == [
        "master_seed", "instrument_name", "bar_timestamp_iso"
    ]


def test_derive_random_pair_does_not_consult_close_or_atr():
    """A more aggressive check: the function's source body does not
    reference close, high, low, open, volume, or atr in any form."""
    src = inspect.getsource(_derive_random_pair)
    # Strip the docstring (the docstring legitimately discusses these
    # words while explaining what is NOT consumed). The non-greedy
    # ``.*?`` with DOTALL handles docstrings that contain ``"`` inside.
    src_without_doc = re.sub(
        r'""".*?"""', "", src, count=1, flags=re.DOTALL
    )
    # The function body should reference only its parameters + the
    # hashlib + integer-conversion machinery.
    for forbidden in ("close", "high", "low", "open(", "volume", "atr("):
        assert forbidden not in src_without_doc, (
            f"_derive_random_pair body references forbidden token {forbidden!r}"
        )


# ---------------------------------------------------------------------------
# 3. Determinism — content invariance (no-lookahead, ≥ 2 cases)
# ---------------------------------------------------------------------------


def test_decision_unchanged_when_bar_t_close_perturbed(eur_usd: Instrument):
    """Same (seed, pair, timestamp) → same direction even when close[t]
    moves. The decision is fully determined by R3/R4 before close[t] is
    consulted (close[t] is read ONLY for stop placement in R7)."""
    strat = RandomEntryAnchorStrategy(version="0.1.0-c011")
    cfg = _default_cfg()

    frame_a = _build_h4_frame(40, base_close=1.0800)
    frame_b = _build_h4_frame(40, base_close=1.5000)  # very different close

    sig_a = strat.generate_signal(_ctx(frame_a, eur_usd, config=cfg))
    sig_b = strat.generate_signal(_ctx(frame_b, eur_usd, config=cfg))

    # Same timestamp → same gate value, same direction. Different
    # close → different stop level only.
    assert sig_a is not None and sig_b is not None
    assert sig_a.side == sig_b.side
    assert sig_a.signal_id == sig_b.signal_id
    assert sig_a.stop_price != sig_b.stop_price  # stop reflects close[t]


def test_strategy_module_uses_only_close_for_stop_placement():
    """Source-level rail: bar-t reads of high/low/open/volume must not
    appear in the strategy module's body. The only bar-t read is
    close[t] for the stop reference (per R7)."""
    src = _STRATEGY_SOURCE
    # Strip the docstrings (the module docstring legitimately discusses
    # which fields are NOT consulted). Non-greedy across DOTALL so the
    # regex tolerates ``"`` characters inside docstrings.
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    forbidden_bar_t_reads = [
        # Forbidden indexed reads of bar-t fields. Bar-t-1 reads
        # (high/low at [-2], ATR at [-2]) are fine; bar-t reads of
        # anything other than close[t] would be a lookahead.
        r'df\["high"\]\.iloc\[-1\]',
        r'df\["low"\]\.iloc\[-1\]',
        r'df\["open"\]\.iloc\[-1\]',
        r'df\["volume"\]\.iloc\[-1\]',
    ]
    for pattern in forbidden_bar_t_reads:
        assert re.search(pattern, src_stripped) is None, (
            f"strategy module reads forbidden bar-t field: {pattern!r}"
        )
    # And it must read close[t] for the stop placement.
    assert re.search(r'df\["close"\]\.iloc\[-1\]', src_stripped) is not None


# ---------------------------------------------------------------------------
# 4. Distribution / frequency (≥ 2 cases)
# ---------------------------------------------------------------------------


def test_long_short_distribution_is_balanced_over_many_bars():
    """Over 10,000 deterministic-seed coin flips, long-share should be
    0.5 ± 3σ where σ = sqrt(p(1-p)/n) = sqrt(0.25/10000) = 0.005."""
    n = 10_000
    base_ts = datetime(2025, 1, 1, tzinfo=UTC)
    long_count = 0
    for i in range(n):
        ts = (base_ts + timedelta(hours=4 * i)).isoformat()
        bar_random, _ = _derive_random_pair(20260523, "EUR_USD", ts)
        if (bar_random & 1) == 0:
            long_count += 1
    long_share = long_count / n
    # 3σ band: |long_share - 0.5| < 0.015.
    assert abs(long_share - 0.5) < 0.015, (
        f"long-share {long_share} is outside the 3σ band around 0.5"
    )


def test_entry_probability_gate_rate_matches_design():
    """Over 10,000 bars with entry_probability_per_bar=0.05, the gate
    should fire at 5% ± 2σ where σ = sqrt(0.05*0.95/10000) ≈ 0.0022."""
    n = 10_000
    entry_prob = 0.05
    base_ts = datetime(2025, 1, 1, tzinfo=UTC)
    fired_count = 0
    for i in range(n):
        ts = (base_ts + timedelta(hours=4 * i)).isoformat()
        _, gate_random = _derive_random_pair(20260523, "EUR_USD", ts)
        gate_value = gate_random / float(2**64)
        if gate_value < entry_prob:
            fired_count += 1
    fire_rate = fired_count / n
    # 2σ band: |fire_rate - 0.05| < 0.005 (well within 3σ).
    assert abs(fire_rate - entry_prob) < 0.005, (
        f"fire rate {fire_rate} is outside the 2σ band around {entry_prob}"
    )


# ---------------------------------------------------------------------------
# 5. Strategy core — R1 / R2 / R5 / R7 (≥ 4 cases)
# ---------------------------------------------------------------------------


def test_warmup_returns_none_when_too_few_bars(eur_usd: Instrument):
    """R1: less than atr_lookback+2 completed bars → None."""
    strat = RandomEntryAnchorStrategy()
    frame = _build_h4_frame(10)  # < 14 + 2 = 16
    assert strat.generate_signal(
        _ctx(frame, eur_usd, config=_default_cfg())
    ) is None


def test_no_signal_when_open_position_present(eur_usd: Instrument):
    """R2: an open position blocks re-entry."""
    strat = RandomEntryAnchorStrategy()
    frame = _build_h4_frame(40)
    assert strat.generate_signal(
        _ctx(
            frame,
            eur_usd,
            config=_default_cfg(),
            open_position_units=Decimal("1000"),
        )
    ) is None


def test_fail_closed_when_atr_is_zero(eur_usd: Instrument):
    """R5: prior_atr <= 0 → None (degenerate range)."""
    strat = RandomEntryAnchorStrategy()
    # All bars identical → high == low == close → ATR = 0.
    frame = _build_h4_frame(40, range_size=0.0)
    assert strat.generate_signal(
        _ctx(frame, eur_usd, config=_default_cfg())
    ) is None


def test_stop_placement_long_below_close(eur_usd: Instrument):
    """R7: long-side stop = close[t] - atr_multiple * prior_atr."""
    strat = RandomEntryAnchorStrategy()
    # Find a (seed, pair, ts) combination where direction is "long".
    cfg = _default_cfg()
    base_close = 1.0800
    range_size = 0.0010
    # Try a few base timestamps until we get a long signal.
    for shift_hours in range(0, 200, 4):
        start = datetime(2025, 1, 6, _H4_HOURS_UTC[0], tzinfo=UTC) + timedelta(
            hours=shift_hours
        )
        frame = _build_h4_frame(40, base_close=base_close, range_size=range_size, start=start)
        sig = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
        if sig is not None and sig.side == "long":
            atr_pips = float(sig.features["prior_atr"])
            expected = float(sig.features["last_close"]) - 2.0 * atr_pips
            assert abs(float(sig.stop_price) - expected) < 1e-5
            return
    pytest.fail("could not find a long signal in 50 fixture timestamps")


def test_stop_placement_short_above_close(eur_usd: Instrument):
    """R7: short-side stop = close[t] + atr_multiple * prior_atr."""
    strat = RandomEntryAnchorStrategy()
    cfg = _default_cfg()
    base_close = 1.0800
    range_size = 0.0010
    for shift_hours in range(0, 200, 4):
        start = datetime(2025, 1, 6, _H4_HOURS_UTC[0], tzinfo=UTC) + timedelta(
            hours=shift_hours
        )
        frame = _build_h4_frame(40, base_close=base_close, range_size=range_size, start=start)
        sig = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
        if sig is not None and sig.side == "short":
            atr_pips = float(sig.features["prior_atr"])
            expected = float(sig.features["last_close"]) + 2.0 * atr_pips
            assert abs(float(sig.stop_price) - expected) < 1e-5
            return
    pytest.fail("could not find a short signal in 50 fixture timestamps")


def test_signal_emitted_with_expected_fields(eur_usd: Instrument):
    """R8: when a signal fires, every expected field is populated."""
    strat = RandomEntryAnchorStrategy()
    cfg = _default_cfg()
    # Use the default gate=0.999999 so the gate is almost always passed.
    frame = _build_h4_frame(40)
    sig = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert sig is not None
    assert sig.strategy_name == "random_entry_anchor"
    assert sig.strategy_version == "0.1.0-c011"
    assert sig.instrument == "EUR_USD"
    assert sig.timeframe == "H4"
    assert sig.side in ("long", "short")
    assert sig.entry_intent == "market"
    assert sig.exit_model == "time_stop_only"
    assert sig.stop_model == "ATR14*2.0"
    assert "bar_random" in sig.features
    assert "gate_random" in sig.features
    assert "gate_value" in sig.features
    assert "prior_atr" in sig.features
    assert "last_close" in sig.features
    assert "null-model" in sig.reason.lower() or "diagnostic" in sig.reason.lower()


def test_signal_id_is_deterministic(eur_usd: Instrument):
    """R8: same inputs → same signal_id across runs."""
    strat1 = RandomEntryAnchorStrategy()
    strat2 = RandomEntryAnchorStrategy()
    frame = _build_h4_frame(40)
    cfg = _default_cfg()
    sig1 = strat1.generate_signal(_ctx(frame, eur_usd, config=cfg))
    sig2 = strat2.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert sig1 is not None and sig2 is not None
    assert sig1.signal_id == sig2.signal_id


# ---------------------------------------------------------------------------
# 6. Structural audit — no forbidden imports / usages (≥ 3 cases)
# ---------------------------------------------------------------------------


def test_strategy_module_does_not_use_python_random_or_numpy_random():
    """R3 / null-model invariant: deterministic-by-construction means
    no stdlib random or numpy.random. Only hashlib.sha256."""
    src = _STRATEGY_SOURCE
    # Strip docstrings — the module docstring legitimately discusses
    # which random libraries are NOT used.
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    assert "import random" not in src_stripped
    assert "from random import" not in src_stripped
    assert "import numpy" not in src_stripped
    assert "from numpy" not in src_stripped
    assert "np.random" not in src_stripped
    assert "numpy.random" not in src_stripped


def test_strategy_module_does_not_use_builtin_hash():
    """The built-in `hash()` is not deterministic across processes
    (PYTHONHASHSEED). Use sha256 only."""
    src = _STRATEGY_SOURCE
    # Strip docstrings so "hash" inside the module docstring doesn't trip
    # this check. Non-greedy across DOTALL.
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    # Match bare `hash(` calls that aren't `hashlib.` or `_hash`.
    bare_hash_calls = re.findall(r"(?<![\.\w])hash\s*\(", src_stripped)
    assert not bare_hash_calls, (
        f"strategy module uses built-in hash(): {bare_hash_calls}"
    )


def test_strategy_module_does_not_import_broker_execution_loops():
    """No import from forex_bot.broker / .execution / .loops — the
    strategy emits Signal objects only and never touches order paths."""
    src = _STRATEGY_SOURCE
    forbidden_imports = (
        "from forex_bot.broker",
        "from forex_bot.execution",
        "from forex_bot.loops",
        "import forex_bot.broker",
        "import forex_bot.execution",
        "import forex_bot.loops",
    )
    for forbidden in forbidden_imports:
        assert forbidden not in src, (
            f"strategy module contains forbidden import: {forbidden!r}"
        )


# ---------------------------------------------------------------------------
# 7. Rejected-family contamination audit (≥ 2 cases)
# ---------------------------------------------------------------------------


def test_strategy_module_does_not_use_campaign_002_parameter_keys():
    """Per REJECTED_FAMILY_OVERFIT_GUARDRAILS.md: the strategy module
    must not reference CAMPAIGN_002 / trend_following / Donchian / EMA
    parameter keys (in code, not in docstrings)."""
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    forbidden_keys = (
        "donchian",
        "ema_fast",
        "ema_slow",
        "adx_threshold",
        "ema_short",
        "ema_long",
        "trend_following",
    )
    for key in forbidden_keys:
        assert key.lower() not in src_stripped.lower(), (
            f"strategy module references CAMPAIGN_002-family key: {key!r}"
        )


def test_strategy_module_does_not_use_campaign_010_parameter_keys():
    """Per REJECTED_FAMILY_OVERFIT_GUARDRAILS.md: the strategy module
    must not reference CAMPAIGN_010 / session_breakout / Asian / London
    parameter keys (in code, not in docstrings)."""
    src = _STRATEGY_SOURCE
    src_stripped = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    forbidden_keys = (
        "asian_session_hours",
        "london_session_hours",
        "min_asian_range_atr_fraction",
        "session_breakout",
        "in_asian_window",
        "in_london_window",
    )
    for key in forbidden_keys:
        assert key.lower() not in src_stripped.lower(), (
            f"strategy module references CAMPAIGN_010-family key: {key!r}"
        )


# ---------------------------------------------------------------------------
# 8. Approval / safety regression (≥ 3 cases)
# ---------------------------------------------------------------------------


def test_approved_strategies_yaml_remains_empty():
    """CAMPAIGN_011 must NOT be added to the approved registry by this
    scaffold sprint (or ever — it is a null model by design)."""
    path = _REPO_ROOT / "configs" / "approved_strategies.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data == {"approved": []}, (
        f"approved_strategies.yaml is no longer empty: {data}"
    )


def test_random_entry_anchor_not_enabled_in_paper_config():
    """The paper config must not enable random_entry_anchor."""
    path = _REPO_ROOT / "configs" / "paper.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    enabled = data.get("strategy", {}).get("enabled", [])
    assert "random_entry_anchor" not in enabled


def test_random_entry_anchor_not_enabled_in_practice_config():
    """The demo/practice config must not enable random_entry_anchor."""
    path = _REPO_ROOT / "configs" / "practice.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    enabled = data.get("strategy", {}).get("enabled", [])
    assert "random_entry_anchor" not in enabled


def test_strategy_class_exposes_no_approval_shaped_field():
    """Null-model invariant: the strategy must not expose any
    field / method whose name suggests it could be approved."""
    forbidden_substrings = ("approve", "approval", "promote", "promotion")
    public_attrs = [
        attr for attr in dir(RandomEntryAnchorStrategy)
        if not attr.startswith("_")
    ]
    for attr in public_attrs:
        for sub in forbidden_substrings:
            assert sub not in attr.lower(), (
                f"strategy exposes approval-shaped attribute: {attr!r}"
            )


def test_strategy_does_not_mutate_config_during_signal_generation(
    eur_usd: Instrument,
):
    """The frozen-config invariant: signal generation reads the config
    dict but never mutates it."""
    strat = RandomEntryAnchorStrategy()
    cfg = _default_cfg()
    cfg_snapshot = dict(cfg)
    frame = _build_h4_frame(40)
    _ = strat.generate_signal(_ctx(frame, eur_usd, config=cfg))
    assert cfg == cfg_snapshot

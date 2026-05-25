"""Backtrader port of CAMPAIGN_011 H4 ``random_entry_anchor 0.1.0-c011``.

Mirrors the frozen rules at
`src/forex_bot/strategies/random_entry_anchor.py` (R1-R8) and the
no-RiskEngine bespoke reference at
`research/lean_parity/campaign_011_h4_bespoke_reference.json` produced
by the previous sprint
(`infra-bespoke-campaign-011-norisk-reference-001`). The port:

- Derives a per-bar deterministic ``(bar_random, gate_random)`` pair
  by SHA-256-hashing the deterministic seed string
  ``f"{master_seed}|{instrument}|{bar_timestamp_iso}"`` byte-for-byte —
  no use of ``random.random()``, ``numpy.random.*``, or Python's
  built-in ``hash()``.
- Implements R1-R8: ATR(14) warm-up + position uniqueness + 5%-per-bar
  entry gate + fail-closed on bad ATR + ATR-stop (2.0× prior ATR) +
  6-bar time stop. No trailing stop. No spread/session/loss-limit
  gates (matches the no-RiskEngine bespoke reference).
- Bypasses Backtrader's broker for fills. The strategy maintains its
  own one-position state machine and uses bid/ask-aware fills at the
  signal-bar's close (same `signal_bar_close` timing the bespoke uses).
- Emits one ``BacktraderTrade`` per closed position.

This adapter is **frozen**: every parameter is read from the committed
``configs/campaign_011_random_entry_anchor.yaml`` and verified against
the pre-commit (`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §5). Mismatch
aborts before any backtest fires.

The adapter cannot approve a strategy. CAMPAIGN_011 remains
**REJECT / null diagnostic anchor by design**.

`strategy_evidence: false`.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC
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
from research.backtrader_lane.strategies.campaign_002_trend_following import (
    _BASE_CCY,
    _DISPLAY_PRECISION,
    _PIP_SIZE,
    _QUOTE_CCY,
    _fill_entry_price,
    _round_price,
    _size_position,
    _trade_pnl,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
CAMPAIGN_011_CONFIG_PATH = (
    REPO_ROOT / "configs" / "campaign_011_random_entry_anchor.yaml"
)
CAMPAIGN_011_BESPOKE_REFERENCE_PATH = (
    REPO_ROOT
    / "research"
    / "lean_parity"
    / "campaign_011_h4_bespoke_reference.json"
)

# Frozen parameters (verbatim from CAMPAIGN_011_PRECOMMIT_CHECKLIST.md §5).
# Mirrored from scripts/run_campaign_011.py and
# scripts/export_campaign_011_norisk_reference.py. Any deviation must
# fail-loud at load time.
EXPECTED_MASTER_SEED = 20260523
EXPECTED_VERSION = "0.1.0-c011"
FROZEN_PARAMETERS: dict[str, Any] = {
    "version": EXPECTED_VERSION,
    "timeframe": "H4",
    "master_seed": EXPECTED_MASTER_SEED,
    "entry_probability_per_bar": 0.05,
    "atr_lookback": 14,
    "atr_stop_multiple": 2.0,
    "trailing_stop_atr_multiple": None,
    "max_bars_in_trade": 6,
    "min_atr_pips": {},
}

# Cost model + sizing (read from the YAML at runtime; mirrors what the
# bespoke engine sees via load_settings(...)).
EXPECTED_FIXED_SLIPPAGE_PIPS = 0.2
EXPECTED_SPREAD_SLIPPAGE_MULTIPLIER = 0.5
EXPECTED_RISK_PER_TRADE_PCT = 0.25
EXPECTED_STARTING_EQUITY = 500.0
EXPECTED_COMMISSION_PER_UNIT = 0.0


# ---------------------------------------------------------------------------
# Deterministic seed derivation (mirrors
# src/forex_bot/strategies/random_entry_anchor.py:_derive_random_pair
# byte-for-byte).


def _derive_random_pair(
    master_seed: int,
    instrument_name: str,
    bar_timestamp_iso: str,
) -> tuple[int, int]:
    """Deterministic SHA-256-based ``(bar_random, gate_random)``.

    **Binding invariant:** input is exactly
    ``f"{master_seed}|{instrument_name}|{bar_timestamp_iso}"``.
    No bar-`t` price data, no ATR, no other features may appear here.
    A structural unit test in
    ``tests/unit/backtrader_lane/test_campaign_011_adapter.py``
    enforces parity with the bespoke implementation.
    """

    seed_input = f"{master_seed}|{instrument_name}|{bar_timestamp_iso}"
    digest = hashlib.sha256(seed_input.encode("utf-8")).digest()
    bar_random = int.from_bytes(digest[:8], "big")
    gate_random = int.from_bytes(digest[8:16], "big")
    return bar_random, gate_random


# ---------------------------------------------------------------------------
# Frozen-parameter enforcement


def _load_campaign_011_config_strategy() -> dict[str, Any]:
    """Load the strategy.random_entry_anchor block from the committed
    YAML. Defers to forex_bot.config so type validation is centralised.

    Importing forex_bot.config here is acceptable: that module is part of
    the research codebase (the bespoke engine's config), not the broker /
    execution / loops modules that the BT lane forbids.
    """

    # Local import keeps the side-effect (loading Pydantic config) cheap
    # at module-import time.
    from forex_bot.config import load_settings

    settings = load_settings(CAMPAIGN_011_CONFIG_PATH)
    rea = settings.strategy.random_entry_anchor
    if rea is None:
        raise SystemExit(
            "CAMPAIGN_011 YAML missing strategy.random_entry_anchor block; "
            "refusing to start."
        )
    return rea.model_dump()


def _assert_frozen(strategy_cfg: dict[str, Any]) -> None:
    """Fail-closed if the loaded YAML deviates from the pre-commit."""

    mismatched: list[str] = []
    for key, expected in FROZEN_PARAMETERS.items():
        got = strategy_cfg.get(key)
        if isinstance(expected, dict) and isinstance(got, dict):
            if got != expected:
                mismatched.append(f"  {key}: got {got!r}, expected {expected!r}")
        elif got != expected:
            mismatched.append(f"  {key}: got {got!r}, expected {expected!r}")
    if mismatched:
        raise SystemExit(
            "CAMPAIGN_011 frozen-parameter mismatch — see "
            "CAMPAIGN_011_PRECOMMIT_CHECKLIST.md §5:\n" + "\n".join(mismatched)
        )
    if int(strategy_cfg.get("master_seed", -1)) != EXPECTED_MASTER_SEED:
        raise SystemExit(
            f"CAMPAIGN_011 master_seed must be {EXPECTED_MASTER_SEED}; "
            f"got {strategy_cfg.get('master_seed')!r}. Seed tuning is "
            "forbidden — this is a null model anchor."
        )


# ---------------------------------------------------------------------------
# PandasData feed (carries bid/ask OHLC on extra lines).


class _Campaign011Feed(bt.feeds.PandasData):
    """Same line layout as the CAMPAIGN_002 feed — bid/ask OHLC on
    extra lines so the fill model can read them at signal-bar close.

    A second feed class (rather than reuse) keeps the two campaigns'
    lines registries cleanly separated."""

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
    return len(strategy)


def _bar_iso_utc(strategy: bt.Strategy) -> str:
    """Return the current bar's timestamp as a UTC ISO 8601 string,
    matching the bespoke strategy's seed input format.

    The dataframe handed to Backtrader was ``tz_convert("UTC")``-ed
    then ``tz_localize(None)``-ed (Backtrader's PandasData demands tz-
    naive). ``bt.num2date`` therefore returns a tz-naive Python
    datetime whose wall-clock matches the original UTC timestamp. We
    re-localize to UTC and ``.isoformat()`` it — identical to:

        pd.Timestamp(idx_t).tz_convert(UTC).isoformat()

    in ``src/forex_bot/strategies/random_entry_anchor.py:127``.
    """

    dt = bt.num2date(strategy.data.datetime[0])
    return pd.Timestamp(dt).tz_localize(UTC).isoformat()


# ---------------------------------------------------------------------------
# Per-pair runner


def run_campaign_011_pair(
    candles: CandleAdapterResult,
    starting_equity_usd: float,
    *,
    config_path: Path = CAMPAIGN_011_CONFIG_PATH,
) -> PairRunResult:
    """Drive one instrument through the CAMPAIGN_011 random_entry_anchor port."""

    strategy_cfg = _load_campaign_011_config_strategy()
    _assert_frozen(strategy_cfg)

    master_seed = int(strategy_cfg["master_seed"])
    entry_probability = float(strategy_cfg["entry_probability_per_bar"])
    atr_lookback = int(strategy_cfg["atr_lookback"])
    atr_stop_multiple = float(strategy_cfg["atr_stop_multiple"])
    max_bars_in_trade = int(strategy_cfg["max_bars_in_trade"])
    # CAMPAIGN_011 has no trailing stop — verified by _assert_frozen above.

    instrument = candles.instrument
    pip_size = _PIP_SIZE.get(instrument)
    quote_ccy = _QUOTE_CCY.get(instrument)
    base_ccy = _BASE_CCY.get(instrument)
    display_precision = _DISPLAY_PRECISION.get(instrument)
    if (
        pip_size is None
        or quote_ccy is None
        or base_ccy is None
        or display_precision is None
    ):
        raise KeyError(
            f"{instrument!r} not in the CAMPAIGN_011 / fixture universe; "
            f"known: {sorted(_PIP_SIZE.keys())}"
        )

    # Cost model + sizing — read from the same YAML the bespoke run uses.
    from forex_bot.config import load_settings

    settings = load_settings(config_path)
    fixed_slippage_pips = float(settings.backtest.fixed_slippage_pips)
    spread_slippage_multiplier = float(settings.backtest.spread_slippage_multiplier)
    risk_per_trade_pct = float(settings.risk.risk_per_trade_pct)

    # Build the dataframe Backtrader will consume.
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

    class _Campaign011Strategy(bt.Strategy):  # pragma: no cover - bt callbacks
        params = (("atr_len", atr_lookback),)

        def __init__(self) -> None:
            self._atr = bt.indicators.AverageTrueRange(
                self.data, period=self.p.atr_len
            )
            # Bespoke R5 reads "ATR at index -2" (i.e. the previous
            # completed bar's ATR). Backtrader's `self._atr[-1]` is the
            # previous-bar value, matching `prior_atr = atr_series.iloc[-2]`
            # in `random_entry_anchor.py:139` exactly.
            self._in_position: bool = False
            self._side: str = "flat"
            self._entry_time: pd.Timestamp | None = None
            self._entry_price: float = 0.0
            self._stop_price: float = 0.0
            self._initial_stop_price: float = 0.0
            self._bars_held: int = 0
            self._units: int = 0
            self._initial_stop_distance: float = 0.0
            # Track number of bars processed so R1 can fire correctly.
            # Backtrader's len(self) is 1-based and counts the current bar.
            self._bars_seen: int = 0

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
            # R formula matches bespoke engine.py:411-415 exactly
            # (and CAMPAIGN_002 sprint-003 fix):
            #     risk_distance = abs(entry - stop) * units   (quote ccy * units)
            #     r = pnl_home / risk_distance               (no quote→home conversion)
            r_mult: float | None = None
            if self._initial_stop_distance > 0 and self._units > 0:
                risk_distance = self._initial_stop_distance * self._units
                r_mult = (
                    pnl_account / risk_distance if risk_distance > 0 else 0.0
                )
            return_pct = (
                (pnl_account / nav["value"]) * 100.0 if nav["value"] > 0 else None
            )
            recorded.append(
                BacktraderTrade(
                    instrument=instrument,
                    side=self._side,
                    entry_time=(
                        self._entry_time.to_pydatetime()
                        if self._entry_time
                        else self._bar_time().to_pydatetime()
                    ),
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
            self._bars_held = 0
            self._units = 0
            self._initial_stop_distance = 0.0
            self._stop_price = 0.0
            self._initial_stop_price = 0.0

        def _try_entry(self) -> None:
            """Evaluate entry on the current bar. Mirrors R1-R8 verbatim."""

            # R1: sufficient warm-up. The bespoke spec checks
            # `len(df) >= atr_lookback + 2` where `df` is the slice up
            # to (and including) bar t. Backtrader's `_bar_count(self)`
            # returns the 1-based count of bars processed so far,
            # equivalent to `len(df)` at the bespoke side.
            if _bar_count(self) < atr_lookback + 2:
                return

            # R2: block re-entry while in position. Same-bar re-entry
            # cannot occur because the strategy refuses re-entry while
            # `self._in_position` is True; the bespoke engine also
            # blocks same-bar re-entry via its position uniqueness rule.
            if self._in_position:
                return

            # R3: deterministic seed input + score derivation. NO
            # bar-t price data, NO ATR appears in the seed input.
            bar_iso = _bar_iso_utc(self)
            bar_random, gate_random = _derive_random_pair(
                master_seed, instrument, bar_iso
            )

            # R4: entry-probability gate (5% per bar).
            gate_value = gate_random / float(2**64)
            if gate_value >= entry_probability:
                return

            # R5: fail-closed on NaN / non-finite / zero prior ATR.
            # The bespoke spec reads `atr_series.iloc[-2]` — the
            # previous bar's ATR. Backtrader's `self._atr[-1]` gives
            # the same value (it indexes backwards from the current
            # bar; -1 = one bar prior).
            try:
                prior_atr = float(self._atr[-1])
            except IndexError:
                return
            # NaN check via the canonical IEEE-754 self-inequality
            # test. math.isnan would also work but adds an import; the
            # `x != x` form is what ruff (SIM201) prefers over
            # `not (x == x)`.
            if prior_atr != prior_atr:
                return
            if prior_atr <= 0:
                return

            # R7: direction selection + ATR-stop placement.
            side: str = "long" if (bar_random & 1) == 0 else "short"

            # Stop placement uses MID close (matches the bespoke
            # strategy: `last_close = float(df["close"].iloc[-1])`).
            last_close = float(self.data.close[0])
            if side == "long":
                raw_stop = last_close - atr_stop_multiple * prior_atr
            else:
                raw_stop = last_close + atr_stop_multiple * prior_atr
            if raw_stop == last_close:
                # Defense in depth — unreachable given prior_atr > 0.
                return
            stop = _round_price(raw_stop, display_precision)

            # Bid/ask-aware fill at signal-bar close (matches the
            # bespoke engine with fill_timing=signal_bar_close).
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

            # R8: deterministic Signal — open a position.
            self._in_position = True
            self._side = side
            self._entry_time = self._bar_time()
            self._entry_price = entry_price
            self._stop_price = stop
            self._initial_stop_price = stop
            self._bars_held = 0
            self._units = units
            self._initial_stop_distance = abs(entry_price - stop)

        def _try_exit(self) -> bool:
            """Check exits on a bar after entry. Returns True if exited.

            CAMPAIGN_011 has no trailing stop. Order of precedence:
              1. Adverse stop (initial ATR stop is the only stop level)
              2. Time stop (max_bars_in_trade = 6)
              3. End-of-data
            """

            self._bars_held += 1
            bid_low = float(self.data.bid_low[0])
            ask_high = float(self.data.ask_high[0])
            bid_close = float(self.data.bid_close[0])
            ask_close = float(self.data.ask_close[0])

            # Adverse-stop check (priority 1).
            if self._side == "long" and bid_low <= self._stop_price:
                self._close_trade(exit_price=self._stop_price, exit_reason="stop")
                return True
            if self._side == "short" and ask_high >= self._stop_price:
                self._close_trade(exit_price=self._stop_price, exit_reason="stop")
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
            # bar first, then a possible same-bar re-entry if we just
            # exited (R2 will block this because _in_position is True
            # immediately after _close_trade resets it AND we just
            # closed; re-entry is therefore allowed on the SAME bar in
            # principle, but R2 says "block re-entry while in position",
            # which is False after close — so a fresh signal CAN fire.
            # This is the bespoke behaviour for CAMPAIGN_011 too).
            if self._in_position:
                self._try_exit()
            if not self._in_position:
                self._try_entry()

        def stop(self) -> None:
            # If we're still open at the end of the data, force EOD close.
            if self._in_position:
                bid_close = float(self.data.bid_close[0])
                ask_close = float(self.data.ask_close[0])
                exit_price = bid_close if self._side == "long" else ask_close
                self._close_trade(exit_price=exit_price, exit_reason="eod")

    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.setcash(starting_equity_usd)
    cerebro.adddata(_Campaign011Feed(dataname=df))
    cerebro.addstrategy(_Campaign011Strategy)
    cerebro.run()

    return PairRunResult(
        instrument=instrument,
        candle_count=candles.bar_count,
        trades=recorded,
        final_cash=float(nav["value"]),
        starting_cash=float(starting_equity_usd),
        analyzer_outputs={"closed_trades": len(recorded)},
    )


# ---------------------------------------------------------------------------
# Approximation flags + adapter registration


CAMPAIGN_011_APPROXIMATION_FLAGS: tuple[str, ...] = (
    "CAMPAIGN_011_DETERMINISTIC_SEED: per-bar (bar_random, gate_random) is "
    "derived from SHA-256 over the deterministic string "
    "`f\"{master_seed}|{instrument}|{bar_timestamp_iso}\"`, byte-for-byte "
    "matching `src/forex_bot/strategies/random_entry_anchor.py:_derive_random_pair`. "
    "No random.random, no numpy.random, no built-in hash(). master_seed is "
    "frozen at 20260523 (CAMPAIGN_011_PRECOMMIT_CHECKLIST.md §5/§6).",
    "CAMPAIGN_011_TIME_STOP_ONLY: exit_model is `time_stop_only` — no "
    "trailing stop; only the initial ATR(14)×2.0 stop and the 6-bar time "
    "stop. The 6-bar time stop fires when `bars_held >= max_bars_in_trade` "
    "on the bar after entry.",
    "CAMPAIGN_011_NO_RISK_ENGINE_PARITY: spread / session / loss-limit "
    "gates are intentionally absent on both sides of the comparison. The "
    "no-RiskEngine bespoke reference at "
    "research/lean_parity/campaign_011_h4_bespoke_reference.json has "
    "risk_engine_used=false.",
    "ATR_PRIOR_BAR: prior_atr reads `self._atr[-1]` (Backtrader's previous-"
    "bar ATR), matching the bespoke `atr_series.iloc[-2]` exactly.",
    "MID_CLOSE_FOR_STOP_PLACEMENT: stop level placement uses the MID close "
    "of the signal bar, matching `random_entry_anchor.py:149` "
    "(`last_close = float(df[\"close\"].iloc[-1])`); the actual entry fill "
    "still uses bid/ask + slippage at signal-bar close.",
    "BACKTRADER_BROKER_BYPASSED: the Cerebro broker is NOT used for fills. "
    "The strategy maintains its own one-position state machine and fills at "
    "signal_bar_close using bid/ask + slippage.",
    "MANUAL_SIZING_RISK_FRACTION: 0.25% of compounding NAV; whole-units "
    "floor; pip value derived from quote/base currency at entry price "
    "(reused from CAMPAIGN_002).",
    "NO_FINANCING: financing/swap not modeled in either engine; "
    "comparison is pre-financing.",
    "R_FORMULA_MATCHES_BESPOKE: r = pnl_home / ((entry - stop) × units), "
    "with NO conversion of the denominator to home currency — matches "
    "bespoke engine.py:411-415 and CAMPAIGN_002 sprint-003 fix exactly.",
)


CAMPAIGN_011_ADAPTER = CampaignAdapter(
    campaign_id="CAMPAIGN_011",
    strategy_id="random_entry_anchor",
    strategy_version=EXPECTED_VERSION,
    description=(
        "Backtrader port of CAMPAIGN_011 H4 random_entry_anchor 0.1.0-c011 "
        "(null-model diagnostic anchor). Frozen rules from "
        "src/forex_bot/strategies/random_entry_anchor.py and "
        "CAMPAIGN_011_PRECOMMIT_CHECKLIST.md §5. Comparison target is the "
        "no-RiskEngine bespoke reference at "
        "research/lean_parity/campaign_011_h4_bespoke_reference.json. "
        "CAMPAIGN_011 remains REJECT / null diagnostic anchor by design."
    ),
    runner_fn=run_campaign_011_pair,
    default_instruments=(
        "EUR_USD",
        "GBP_USD",
        "USD_JPY",
        "AUD_USD",
        "USD_CAD",
        "USD_CHF",
        "NZD_USD",
    ),
    default_starting_equity_usd=EXPECTED_STARTING_EQUITY,
    risk_per_trade_pct=EXPECTED_RISK_PER_TRADE_PCT,
    approximation_flags=CAMPAIGN_011_APPROXIMATION_FLAGS,
    notes=(
        "strategy_evidence: false; CAMPAIGN_011 REJECT — null model "
        "diagnostic anchor; cannot be added to configs/approved_strategies.yaml "
        "under any circumstance per CAMPAIGN_011_PRECOMMIT_CHECKLIST.md §2"
    ),
)


# Self-grep guard: the bespoke reference path is referenced as a string
# constant so the comparison harness can find it; the path is read-only
# here.
def reference_path() -> Path:
    return CAMPAIGN_011_BESPOKE_REFERENCE_PATH


def _reference_metadata() -> dict[str, Any]:
    """Read a small subset of the committed bespoke reference for tests."""

    return json.loads(CAMPAIGN_011_BESPOKE_REFERENCE_PATH.read_text(encoding="utf-8"))


register_campaign(CAMPAIGN_011_ADAPTER)

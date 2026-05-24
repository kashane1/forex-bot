"""Cross-pair currency-strength rotation — ``cross_pair_currency_strength_rotation 0.1.0-c013``.

CAMPAIGN_013 research candidate (the C6 cross-pair currency-strength
rotation selected by the
``research-new-candidate-strategy-discovery-004`` sprint).
**CANDIDATE SCAFFOLD ONLY — not approved for paper / demo / live
trading.** ``configs/approved_strategies.yaml`` remains
``approved: []``; CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
CAMPAIGN_012 all remain REJECT.

Hypothesis (binding — see
``docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md``
§1): aggregate H4 close-to-close returns across the 7-pair universe
into 8-currency strength scores; rank currencies; trade a pair iff
its ``base`` and ``quote`` currency rank-gap exceeds a threshold
large enough to overcome H4 cost drag.

Entry logic (R1-R8; binding — see implementation spec) at the latest
*completed* bar ``t`` taken from ``ctx.candles.completed_only().df``:

  R1. Warm-up: ``len(df) >= warmup_bars_required()`` (default 50).
  R2. No open position for ``ctx.instrument``.
  R3. Read sibling-pair H4 close series from
      ``ctx.config["cross_pair_closes"]``; fail-closed on missing
      or key-set mismatch (runner integration contract).
  R4. Compute per-pair ``n``-bar log returns; map to 8-currency
      strength scores (USD-base pairs contribute positive sign;
      USD-quote pairs invert sign; USD strength = ``−mean`` of
      non-USD strengths). Fail-closed on any NaN / ≤ 0 / insufficient
      history.
  R5. Rank currencies (1 = strongest, 8 = weakest); alphabetic
      tiebreak for determinism. Compute ``rank_gap = ranks[quote] −
      ranks[base]``. Fail-closed if ``|rank_gap| < rank_gap_threshold``.
      Side ``long`` if ``rank_gap > 0`` (base stronger than quote)
      else ``short`` (inclusive at threshold).
  R6. Fail-closed on NaN / non-finite / zero ``prior_atr_h4`` (H4
      ATR at index ``-2``).
  R7. Stop placement: ``close[t] -/+ atr_stop_multiple * prior_atr_h4``.
      ``close[t]`` is read ONLY in R7; never for the cross-pair
      strength feature.
  R8. Emit ``Signal`` with deterministic ``signal_id`` and
      ``exit_model="time_stop_only"``.

Implementation notes (binding):

* No use of ``random``, ``numpy.random``, ``secrets``, or Python's
  built-in ``hash()`` — the strategy is fully deterministic from
  price data. ``numpy.log`` is the only stochastic-looking call
  and it is purely functional.
* No import from ``forex_bot.broker`` / ``forex_bot.execution`` /
  ``forex_bot.loops`` (structural unit tests grep for these).
* No reference to CAMPAIGN_002 / ``trend_following`` / ``Donchian`` /
  ``EMA`` parameters (verified by source-grep).
* No reference to CAMPAIGN_010 / ``session_breakout`` / ``Asian`` /
  ``London`` parameters (verified by source-grep).
* No reference to CAMPAIGN_011 / ``random_entry_anchor`` /
  ``master_seed`` / ``entry_probability_per_bar`` parameters
  (verified by source-grep).
* No reference to CAMPAIGN_012 / ``regime_switcher_atr_percentile`` /
  ``daily_atr_lookback`` / ``regime_lookback_days`` /
  ``regime_percentile_threshold`` / ``min_close_move_atr_fraction`` /
  ``trend_lookback_h4_bars`` parameters (verified by source-grep).
* Strategy module never mutates the strategy config dict.
* ``CrossPairCurrencyStrengthRotationStrategy`` exposes no
  approval-shaped field / method.
* Cross-pair runner integration contract: the runner (future
  evidence sprint) supplies ``cross_pair_closes`` via
  ``ctx.config``; the strategy never reaches into engine / broker /
  data layer directly.
"""

from __future__ import annotations

import hashlib
import math
from datetime import UTC
from decimal import Decimal
from typing import Any

import numpy as np
import pandas as pd

from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import atr

# The 7-pair universe (binding; runner-enforced via ctx.config key-set check).
EXPECTED_PAIRS: tuple[str, ...] = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)

# Per-pair non-USD currency + sign convention. Binding from the
# implementation spec §3.2 — USD-base pairs contribute +log_return to
# the non-USD currency's strength; USD-quote pairs invert the sign.
_PAIR_NONUSD_CURRENCY: dict[str, tuple[str, int]] = {
    "EUR_USD": ("EUR", +1),
    "GBP_USD": ("GBP", +1),
    "AUD_USD": ("AUD", +1),
    "NZD_USD": ("NZD", +1),
    "USD_JPY": ("JPY", -1),
    "USD_CAD": ("CAD", -1),
    "USD_CHF": ("CHF", -1),
}

# The 8-currency set (USD + 7 non-USD).
NON_USD_CURRENCIES: tuple[str, ...] = (
    "EUR", "GBP", "AUD", "NZD", "JPY", "CAD", "CHF",
)


def _parse_pair(name: str) -> tuple[str, str]:
    """Parse ``"BASE_QUOTE"`` into ``("BASE", "QUOTE")``.

    Raises ``ValueError`` on malformed input. The runner / strategy
    callers should treat a ValueError as a pre-condition violation,
    not as a per-bar fail-closed; therefore this helper raises rather
    than returning None (signal-time fail-closure happens via
    ``cross_pair_closes`` key-set check in R3).
    """
    parts = name.split("_")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f"malformed pair name: {name!r}")
    base, quote = parts
    if not base.isupper() or not quote.isupper():
        raise ValueError(
            f"pair name parts must be uppercase currency codes: {name!r}"
        )
    return base, quote


def _log_return_n(closes: pd.Series, n: int) -> float | None:
    """Compute ``log(close[-1] / close[-1-n])``; None on bad data.

    Binding invariants (no-lookahead rail):
    * ``closes`` is assumed to be the *completed-only* close series
      for one pair (the runner supplies it that way).
    * Both indices accessed (``-1`` and ``-1 - n``) are closed bars
      by construction.
    * Returns None — never raises — on insufficient history,
      non-finite values, or ≤ 0 prices.
    """
    if len(closes) <= n:
        return None
    last = float(closes.iloc[-1])
    prior = float(closes.iloc[-1 - n])
    if not (math.isfinite(last) and math.isfinite(prior)):
        return None
    if last <= 0 or prior <= 0:
        return None
    return float(np.log(last) - np.log(prior))


def _compute_strength(returns: dict[str, float]) -> dict[str, float]:
    """Map per-pair log returns to 8-currency strength scores.

    Binding sign convention (implementation spec §3.2):
    * EUR/GBP/AUD/NZD strengths = ``+log_return(USD_base_pair)``.
    * JPY/CAD/CHF strengths     = ``−log_return(USD_quote_pair)``.
    * USD strength              = ``−mean(non-USD strengths)``.

    Pure functional; no module-level state.
    """
    strength: dict[str, float] = {}
    for pair, (currency, sign) in _PAIR_NONUSD_CURRENCY.items():
        strength[currency] = sign * returns[pair]
    non_usd_total = sum(strength[c] for c in NON_USD_CURRENCIES)
    strength["USD"] = -non_usd_total / len(NON_USD_CURRENCIES)
    return strength


def _compute_ranks(strength: dict[str, float]) -> dict[str, int]:
    """Rank currencies descending by strength; alphabetic tiebreak.

    Binding invariants:
    * Rank 1 = strongest, rank 8 = weakest.
    * Ties broken by ascending currency code (alphabetic) for
      determinism across runs / processes / pair iteration orders.
    * Purely functional; no module-level state.
    """
    sorted_currencies = sorted(strength.items(), key=lambda kv: (-kv[1], kv[0]))
    return {currency: rank for rank, (currency, _) in enumerate(sorted_currencies, start=1)}


class CrossPairCurrencyStrengthRotationStrategy:
    """Cross-pair currency-strength rotation — research scaffold only.

    CANDIDATE SCAFFOLD ONLY — NOT APPROVED. See
    ``docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md``
    for the binding R1-R8 specification, frozen parameters, sign
    convention, and no-lookahead invariants. The future
    ``research-cross-pair-currency-strength-rotation-walk-forward-001``
    evidence sprint will run the full walk-forward + financing
    overlay + risk diagnostics + verifier-status assessment; only
    that sprint can produce research evidence. Even a clean PASS
    produces a ``RESEARCH_PASS_UNAPPROVED`` candidate awaiting the
    verifier extension + a deliberate human approval action per
    ``STRATEGY_APPROVAL_PROCESS.md``.
    """

    name: str = "cross_pair_currency_strength_rotation"

    def __init__(self, version: str = "0.1.0-c013") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        # The R4 feature needs ``currency_strength_lookback_bars + 1
        # = 25`` H4 bars; R6 needs ``atr_lookback + 2 = 16``. Pinned
        # at 50 per the implementation spec for safety; the R3/R4
        # fail-closed checks provide stricter dynamic guards if the
        # H4 history actually yields fewer than 25 bars.
        return 50

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        lookback_bars = int(cfg.get("currency_strength_lookback_bars", 24))
        rank_gap_threshold = int(cfg.get("rank_gap_threshold", 4))
        atr_len = int(cfg.get("atr_lookback", 14))
        atr_multiple = float(cfg.get("atr_stop_multiple", 2.0))
        timeframe = cfg.get("timeframe", "H4")

        # R1: sufficient warm-up.
        if len(df) < self.warmup_bars_required():
            return None

        # R2: block re-entry if a position already exists.
        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        # R3: read sibling-pair closes from ctx.config (runner contract).
        cross_pair_closes = cfg.get("cross_pair_closes")
        if cross_pair_closes is None:
            return None
        if set(cross_pair_closes.keys()) != set(EXPECTED_PAIRS):
            return None

        # R4: compute per-pair log returns + 8-currency strength.
        returns: dict[str, float] = {}
        for pair in EXPECTED_PAIRS:
            r = _log_return_n(cross_pair_closes[pair], lookback_bars)
            if r is None or not math.isfinite(r):
                return None
            returns[pair] = r
        strength = _compute_strength(returns)
        if not all(math.isfinite(v) for v in strength.values()):
            return None

        # R5: rank currencies; compute pair rank gap; pick side.
        ranks = _compute_ranks(strength)
        try:
            base, quote = _parse_pair(ctx.instrument.name)
        except ValueError:
            return None
        if base not in ranks or quote not in ranks:
            return None
        rank_gap = ranks[quote] - ranks[base]
        if abs(rank_gap) < rank_gap_threshold:
            return None
        side: str = "long" if rank_gap > 0 else "short"

        # R6: fail-closed on NaN / non-finite / zero H4 ATR.
        h4_atr_series = atr(df["high"], df["low"], df["close"], atr_len)
        prior_atr_h4 = float(h4_atr_series.iloc[-2])
        if not math.isfinite(prior_atr_h4) or prior_atr_h4 <= 0:
            return None

        # R7: stop placement (close[t] is the stop reference; entry
        # decision was fully determined by R3 / R4 / R5 before close[t]
        # was consulted).
        last_close = float(df["close"].iloc[-1])
        if not math.isfinite(last_close):
            return None
        if side == "long":
            stop = last_close - atr_multiple * prior_atr_h4
        else:
            stop = last_close + atr_multiple * prior_atr_h4
        if stop == last_close:
            # Defense in depth — unreachable given prior_atr_h4 > 0 in R6.
            return None

        # R8: emit deterministic Signal.
        idx_t = df.index[-1]
        bar_timestamp_iso = pd.Timestamp(idx_t).tz_convert(UTC).isoformat()
        signal_id = _stable_signal_id(
            self.name,
            self.version,
            ctx.instrument.name,
            timeframe,
            bar_timestamp_iso,
            side,
        )

        return Signal(
            signal_id=signal_id,
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe=timeframe,
            timestamp=pd.Timestamp(idx_t).tz_convert(UTC).to_pydatetime(),
            side=side,  # type: ignore[arg-type]
            entry_intent="market",
            stop_model=f"ATR{atr_len}*{atr_multiple}",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="time_stop_only",
            features={
                "currency_strength_lookback_bars": int(lookback_bars),
                "rank_gap_threshold": int(rank_gap_threshold),
                "rank_gap": int(rank_gap),
                "base_currency": base,
                "quote_currency": quote,
                "base_rank": int(ranks[base]),
                "quote_rank": int(ranks[quote]),
                "prior_atr_h4": float(prior_atr_h4),
                "last_close": float(last_close),
                "strength_EUR": float(strength["EUR"]),
                "strength_GBP": float(strength["GBP"]),
                "strength_USD": float(strength["USD"]),
                "strength_JPY": float(strength["JPY"]),
                "strength_AUD": float(strength["AUD"]),
                "strength_CAD": float(strength["CAD"]),
                "strength_CHF": float(strength["CHF"]),
                "strength_NZD": float(strength["NZD"]),
            },
            reason=(
                f"Cross-pair currency strength rotation {side}: "
                f"{base}(rank={ranks[base]}) vs {quote}(rank={ranks[quote]}) "
                f"gap={rank_gap} (|gap| >= threshold={rank_gap_threshold})"
            ),
        )


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]

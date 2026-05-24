"""Calendar-event window anomaly — ``calendar_event_window_anomaly 0.1.0-c014``.

CAMPAIGN_014 research candidate (the C7 calendar-event window anomaly
candidate selected by the
``research-new-candidate-strategy-discovery-005`` sprint).
**CANDIDATE SCAFFOLD ONLY — not approved for paper / demo / live
trading.** ``configs/approved_strategies.yaml`` remains
``approved: []``; CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
CAMPAIGN_012 / CAMPAIGN_013 all remain REJECT.

Hypothesis (binding — see
``docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md``
§1): around scheduled high-impact macroeconomic events (NFP, FOMC,
ECB, BoJ, BoE), USD-pair returns exhibit a mean-reverting overshoot
in the H4 bars immediately after the event. Trade **counter to the
first post-event H4 bar's direction** with an H4 ATR-2 stop and a
max-hold time stop of ``max_post_event_bars`` H4 bars.

Entry logic (R1-R8; binding — see implementation spec §4) at the
latest *completed* bar ``t`` taken from
``ctx.candles.completed_only().df``:

  R1. Warm-up: ``len(df) >= warmup_bars_required()`` (default 32:
      atr_lookback + buffer for index -2). The event_warmup_bars (= 1)
      requirement is implicit via R3 — no signal fires until at least
      one completed event matches.
  R2. Event-fixture availability via ``ctx.config["event_fixture"]``
      (preloaded ``CalendarEventFixture``) or
      ``ctx.config["event_calendar_path"]`` (loaded lazily once).
      Fail-closed if neither is usable.
  R3. Event-window proximity: find the most recent eligible event
      with ``event_time_utc <= bar_t_minus_1_close_time`` matching
      the impacted-pairs mapping for ``ctx.instrument.name``. The
      trigger bar is the FIRST post-event bar (``bars_since_event ==
      1``); only then continue.
  R4. Overlap precedence: if multiple events of different classes
      fall in the same event bar, pick the one with the lowest
      precedence index in ``impact_ordering``
      (default ``["FOMC", "NFP", "ECB", "BoJ", "BoE"]``).
  R5. Counter-direction signal: ``event_bar_return =
      (close[event_bar] / open[event_bar]) − 1``. ``Side.SHORT`` if
      positive, ``Side.LONG`` if negative, NO SIGNAL if exactly zero
      (degenerate / data quality).
  R6. H4 ATR fail-closed: ``prior_atr_h4 = atr(...).iloc[-2]``; fail
      if NaN / non-finite / ≤ 0.
  R7. ATR stop placement: ``close[t] ± atr_stop_multiple * prior_atr_h4``
      (long: minus; short: plus). ``close[t]`` is read ONLY in R7;
      entry decision (R3 / R4 / R5) is fully determined before
      ``close[t]`` is consulted. Max-hold time stop at
      ``max_post_event_bars`` H4 bars enforced by runner.
  R8. Emit ``Signal`` with deterministic ``signal_id`` and
      ``exit_model="time_stop_only"``. Signal features include
      ``event_class``, ``event_id``, ``event_time_utc``,
      ``bars_since_event``, ``prior_atr_h4``, ``last_close``,
      ``event_bar_return``, ``post_event_window_bars``. **MUST NOT**
      include actual / forecast / surprise / revision / market-
      reaction / commentary.

Implementation notes (binding):

* No use of ``random``, ``numpy.random``, ``secrets``, or Python's
  built-in ``hash()`` — the strategy is fully deterministic from
  price + fixture data. SHA-1 is used only for ``signal_id``
  stability and is purely functional.
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
  ``regime_percentile_threshold`` parameters (verified by source-grep).
* No reference to CAMPAIGN_013 / ``cross_pair_currency_strength_rotation`` /
  ``currency_strength_lookback_bars`` / ``rank_gap_threshold`` /
  ``cross_pair_closes`` parameters (verified by source-grep).
* Strategy module never mutates the strategy config dict.
* ``CalendarEventWindowAnomalyStrategy`` exposes no approval-shaped
  field / method.
* The event-fixture loader is local-file-only; the strategy module
  performs NO network I/O at signal time.
"""

from __future__ import annotations

import hashlib
import math
from datetime import UTC, timedelta
from decimal import Decimal
from typing import Any

import pandas as pd

from forex_bot.calendar_events import (
    DEFAULT_IMPACT_ORDERING,
    CalendarEventFixture,
    class_precedence,
    eligible_events_at_or_before,
    impacted_pairs_for,
    load_event_fixture,
)
from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import atr

# Bar-width assumption for the strategy (matches CAMPAIGN_010 / 011 /
# 012 / 013 H4 conventions). H4 bars are 4 hours wide; the event bar
# is the bar whose [open_time, open_time + H4_WIDTH) interval contains
# the event timestamp.
_H4_WIDTH = timedelta(hours=4)


def _find_event_bar_index(df: pd.DataFrame, event_time: pd.Timestamp) -> int | None:
    """Find the bar index whose [open_time, open_time + H4_WIDTH) contains event_time.

    Returns None if no bar in `df` contains the event.

    Binding invariant (no-lookahead rail): the search uses df's index
    only; it does not reach into future bars. The returned index is
    a *positional* index into df.

    `df.index` values are H4 *open* timestamps (matches the CandleFrame
    convention used by all other strategies).
    """
    if event_time.tzinfo is None:
        return None
    # Convert event_time to UTC for comparison; df.index is UTC-aware.
    if event_time.tz_convert(UTC) is None:  # defensive
        return None
    et = event_time.tz_convert(UTC)
    # Find bars whose open <= event_time < open + H4_WIDTH.
    starts = df.index
    if len(starts) == 0:
        return None
    # Use vectorized comparison; pick the last matching index.
    in_window_mask = (starts <= et) & (et < starts + _H4_WIDTH)
    if not in_window_mask.any():
        return None
    # Convert positional via numpy.
    matching_positions = [i for i, m in enumerate(in_window_mask) if m]
    return matching_positions[-1] if matching_positions else None


def _get_fixture(cfg: dict[str, Any]) -> CalendarEventFixture | None:
    """Resolve the event fixture from ctx.config.

    Resolution order (binding R2 — implementation spec §4):
    1. ``ctx.config["event_fixture"]`` if it's a ``CalendarEventFixture``
       instance (preloaded by the future evidence runner).
    2. ``ctx.config["event_calendar_path"]`` if it's a string path —
       load lazily (the loader caches via Python's import-level state
       implicitly; for true caching, the runner should preload via
       option 1).

    Returns None on failure (R2 fail-closed); the strategy will emit
    no signal.
    """
    preloaded = cfg.get("event_fixture")
    if isinstance(preloaded, CalendarEventFixture):
        return preloaded
    path = cfg.get("event_calendar_path")
    if not isinstance(path, str) or not path:
        return None
    try:
        return load_event_fixture(path)
    except (FileNotFoundError, ValueError):
        # R2 fail-closed on missing or invalid fixture (EventFixtureError
        # subclasses ValueError; pydantic ValidationError also subclasses).
        return None


def _resolve_event_for_bar(
    fixture: CalendarEventFixture,
    *,
    instrument_name: str,
    bar_t_open: pd.Timestamp,
    df: pd.DataFrame,
    impact_ordering: tuple[str, ...],
    event_set: tuple[str, ...],
    post_event_window_bars: int,
) -> tuple[Any, int, int] | None:
    """Find the eligible event whose post-event window includes bar t.

    Returns (CalendarEvent, event_bar_pos, bars_since_event) where
    bars_since_event = (t - event_bar_pos), and 1 means "trigger bar".

    Returns None if no event is eligible for this bar / instrument.

    Binding invariants (R3 + R4):
    * Only events whose event_time_utc <= bar_t_minus_1_close_time
      are eligible (no future leakage). Since bar_t_open is the
      current bar's open and bar_t_minus_1_close = bar_t_open, this
      reduces to event_time_utc <= bar_t_open.
    * Among eligible events, pick the highest-precedence-class event
      whose bars_since_event is in [1, post_event_window_bars]. R4
      overlap precedence applies when two events fall in the SAME
      event-bar.
    """
    if bar_t_open.tzinfo is None:
        return None
    cutoff = bar_t_open.to_pydatetime()
    # Pull eligible past events of the configured set.
    candidates = eligible_events_at_or_before(
        list(fixture.events),
        cutoff,
        event_classes=event_set,
    )
    # Walk backwards through candidates (most-recent first) to find
    # one whose event-bar is in our trigger window.
    best: tuple[Any, int, int, int] | None = None  # (event, event_bar_pos, bars_since_event, precedence)
    # Look at most ~post_event_window_bars * len(event_set) recent
    # candidates; in practice the most recent 1-2 dominate. To keep
    # things deterministic we iterate the suffix.
    # Scan from the end backwards but cap the lookback to avoid O(n)
    # work per bar: only the most recent N events can possibly be in
    # the window (one event per H4 bar at most).
    max_scan = post_event_window_bars + 8  # small safety margin
    for ev in reversed(candidates[-max_scan:]):
        # Check impacted-pairs mapping for this event class.
        if instrument_name not in impacted_pairs_for(ev.event_class):
            continue
        # Find the event bar in df.
        event_ts = pd.Timestamp(ev.event_time_utc)
        event_bar_pos = _find_event_bar_index(df, event_ts)
        if event_bar_pos is None:
            continue
        # Current bar position is len(df) - 1; bars_since_event = (cur - event_bar_pos)
        cur_pos = len(df) - 1
        bars_since = cur_pos - event_bar_pos
        if bars_since < 1 or bars_since > post_event_window_bars:
            continue
        # R3 binding: trigger bar is the FIRST post-event bar (bars_since == 1).
        if bars_since != 1:
            continue
        # R4 overlap: pick the highest-precedence event class for
        # the SAME event bar.
        prec = class_precedence(ev.event_class, impact_ordering=impact_ordering)
        if best is None or event_bar_pos > best[1] or (
            event_bar_pos == best[1] and prec < best[3]
        ):
            best = (ev, event_bar_pos, bars_since, prec)
    if best is None:
        return None
    return best[0], best[1], best[2]


class CalendarEventWindowAnomalyStrategy:
    """Calendar-event window anomaly — research scaffold only.

    CANDIDATE SCAFFOLD ONLY — NOT APPROVED. See
    ``docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md``
    for the binding R1-R8 specification, frozen parameters, fixture
    schema, and no-lookahead invariants. The future
    ``research-calendar-event-window-anomaly-walk-forward-001``
    evidence sprint will run the full walk-forward + financing
    overlay + risk diagnostics + verifier-status assessment; only
    that sprint can produce research evidence. Even a clean PASS
    produces a ``RESEARCH_PASS_UNAPPROVED`` candidate awaiting the
    verifier extension + a deliberate human approval action per
    ``STRATEGY_APPROVAL_PROCESS.md``.
    """

    name: str = "calendar_event_window_anomaly"

    def __init__(self, version: str = "0.1.0-c014") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        # ATR(14) needs >=15 bars; +1 for index -2; +1 for finding the
        # event bar at index -2 (the trigger bar is the first post-event
        # bar, which is at most 1 bar back from current). Pinned at 32
        # for safety; the R3 / R6 fail-closed checks provide stricter
        # dynamic guards if H4 history actually yields fewer bars.
        return 32

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        atr_len = int(cfg.get("atr_lookback", 14))
        atr_multiple = float(cfg.get("atr_stop_multiple", 2.0))
        post_event_window_bars = int(cfg.get("post_event_window_bars", 6))
        event_set_list = cfg.get("event_set") or list(DEFAULT_IMPACT_ORDERING)
        impact_ordering_list = cfg.get("impact_ordering") or list(DEFAULT_IMPACT_ORDERING)
        event_set = tuple(event_set_list)
        impact_ordering = tuple(impact_ordering_list)
        timeframe = cfg.get("timeframe", "H4")

        # R1: sufficient warm-up for ATR + index -2 access.
        if len(df) < max(self.warmup_bars_required(), atr_len + 2):
            return None

        # R2: position already open → no re-entry (the engine's
        # max_positions_per_instrument = 1 enforces this; this is a
        # defense-in-depth check at the strategy layer too).
        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        # R2 (cont): resolve the event fixture from ctx.config.
        fixture = _get_fixture(cfg)
        if fixture is None:
            return None

        # R3 + R4: find the eligible event for this bar / instrument.
        bar_t_open = df.index[-1]
        resolved = _resolve_event_for_bar(
            fixture,
            instrument_name=ctx.instrument.name,
            bar_t_open=bar_t_open,
            df=df,
            impact_ordering=impact_ordering,
            event_set=event_set,
            post_event_window_bars=post_event_window_bars,
        )
        if resolved is None:
            return None
        event, event_bar_pos, bars_since_event = resolved

        # R5: counter-direction signal from event-bar return.
        event_open = float(df["open"].iloc[event_bar_pos])
        event_close = float(df["close"].iloc[event_bar_pos])
        if (
            not math.isfinite(event_open)
            or not math.isfinite(event_close)
            or event_open <= 0
            or event_close <= 0
        ):
            return None
        event_bar_return = (event_close / event_open) - 1.0
        if not math.isfinite(event_bar_return):
            return None
        if event_bar_return == 0.0:
            # Degenerate / data quality — no signal.
            return None
        side: str = "short" if event_bar_return > 0 else "long"

        # R6: fail-closed on NaN / non-finite / zero H4 ATR.
        h4_atr_series = atr(df["high"], df["low"], df["close"], atr_len)
        prior_atr_h4 = float(h4_atr_series.iloc[-2])
        if not math.isfinite(prior_atr_h4) or prior_atr_h4 <= 0:
            return None

        # R7: stop placement. close[t] is the stop reference; entry
        # decision was fully determined by R3 / R4 / R5 before close[t]
        # was consulted.
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
        event_time_iso = pd.Timestamp(event.event_time_utc).tz_convert(UTC).isoformat()
        signal_id = _stable_signal_id(
            self.name,
            self.version,
            ctx.instrument.name,
            timeframe,
            bar_timestamp_iso,
            side,
            event.event_id,
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
                "event_class": str(event.event_class),
                "event_id": str(event.event_id),
                "event_time_utc": event_time_iso,
                "bars_since_event": int(bars_since_event),
                "post_event_window_bars": int(post_event_window_bars),
                "event_bar_return": float(event_bar_return),
                "prior_atr_h4": float(prior_atr_h4),
                "last_close": float(last_close),
                "atr_lookback": int(atr_len),
                "atr_stop_multiple": float(atr_multiple),
            },
            reason=(
                f"Calendar-event window {side}: {event.event_class} "
                f"@ {event_time_iso} → bar+{bars_since_event} "
                f"(event_bar_return={event_bar_return:+.5f}; "
                f"counter-trend ATR-stop @ {atr_multiple}×ATR{atr_len})"
            ),
        )


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]

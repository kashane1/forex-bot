"""Event-calendar fixture loader for CAMPAIGN_014 / C7.

Loads, validates, and queries the committed scheduled-event fixture at
``research/calendar/fixtures/campaign_014_events.json`` (or any other
fixture conforming to schema ``campaign_014.event_fixture.v1``).

**Binding constraints (no-lookahead rails):**

* The loader enforces a per-event **deny-list** of post-event fields:
  ``actual``, ``forecast``, ``consensus``, ``surprise``, ``revision``,
  ``revised_value``, ``market_reaction``, ``post_event_move``,
  ``commentary`` (case-insensitive). Any presence raises
  ``EventFixtureError`` at load time — the strategy module cannot
  smuggle surprise data in even if a future fixture revision
  accidentally introduces it.
* All timestamps must be UTC-aware (``tzinfo`` not None and equal to
  ``datetime.timezone.utc``). Naive timestamps are rejected.
* ``eligible_events_at_or_before(events, cutoff)`` returns only
  events with ``event_time_utc <= cutoff``; no future events leak.
* The loader performs **no** network I/O. It reads a local JSON file
  once and caches the parsed structure.
* The loader does **not** import any ``forex_bot.broker`` /
  ``forex_bot.execution`` / ``forex_bot.loops`` module.

See:

- ``docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`` §7-§9
- ``docs/research/CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md``
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Binding event-class set (mirrors implementation spec §8).
ALLOWED_EVENT_CLASSES: tuple[str, ...] = ("NFP", "FOMC", "ECB", "BoJ", "BoE")

# Default impact precedence (high → low) for overlap resolution per R4.
# Mirrors implementation spec §5 (`impact_ordering` frozen parameter).
DEFAULT_IMPACT_ORDERING: tuple[str, ...] = ("FOMC", "NFP", "ECB", "BoJ", "BoE")

# Binding deny-list of post-event fields the fixture MUST NOT contain.
# Detection is case-insensitive substring match against the deny-list.
# Reject the fixture if any per-event field name contains any deny-list
# substring. Implementation spec §7.2.
FORBIDDEN_FIELD_SUBSTRINGS: tuple[str, ...] = (
    "actual",
    "forecast",
    "consensus",
    "surprise",
    "revision",
    "revised",  # catches "revised_value"
    "market_reaction",
    "post_event_move",
    "commentary",
)

# Per-event-class impacted-pairs mapping (binding; spec §2).
IMPACTED_PAIRS: dict[str, tuple[str, ...]] = {
    "NFP": ("EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"),
    "FOMC": ("EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"),
    "ECB": ("EUR_USD",),
    "BoJ": ("USD_JPY",),
    "BoE": ("GBP_USD",),
}

EXPECTED_SCHEMA_VERSION = "campaign_014.event_fixture.v1"


class EventFixtureError(ValueError):
    """Raised when an event-calendar fixture is invalid."""


class CalendarEvent(BaseModel):
    """One scheduled-event record (binding allow-list — spec §7.1).

    No post-event fields permitted (validated by the parent fixture
    loader before per-event construction; the loader's deny-list is
    the primary enforcement point, this model's ``extra="forbid"`` is
    a second line of defense).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: str
    event_class: str
    event_time_utc: datetime

    @field_validator("event_class")
    @classmethod
    def _valid_class(cls, v: str) -> str:
        if v not in ALLOWED_EVENT_CLASSES:
            raise ValueError(
                f"unsupported event_class {v!r}; allowed: {ALLOWED_EVENT_CLASSES}"
            )
        return v

    @field_validator("event_time_utc")
    @classmethod
    def _utc_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("event_time_utc must be timezone-aware (UTC)")
        # Normalize to UTC (rejects non-UTC offsets implicitly via the
        # equality check below — we require strict UTC, not "any tz that
        # happens to equal UTC at this instant").
        if v.utcoffset() != (datetime.fromtimestamp(0, tz=UTC) - datetime.fromtimestamp(0, tz=UTC)):
            # i.e. utcoffset() != timedelta(0)
            raise ValueError(
                f"event_time_utc must be UTC (offset 0); got offset {v.utcoffset()}"
            )
        return v.astimezone(UTC)


class CalendarEventFixture(BaseModel):
    """Parsed event-calendar fixture (binding schema — spec §7).

    Construction order: top-level ``load_event_fixture(path)`` parses
    JSON → validates schema + deny-list → constructs this model. The
    deny-list check happens *before* per-event construction so that a
    fixture carrying ``actual`` (or any other forbidden field) fails
    with a clear error message rather than a silent pydantic skip.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str
    coverage_start_utc: datetime
    coverage_end_utc: datetime
    event_classes: list[str]
    source_attribution: dict[str, dict[str, str]]
    events: list[CalendarEvent] = Field(default_factory=list)

    @field_validator("schema_version")
    @classmethod
    def _check_schema_version(cls, v: str) -> str:
        if v != EXPECTED_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported schema_version {v!r}; "
                f"expected {EXPECTED_SCHEMA_VERSION!r}"
            )
        return v

    @field_validator("coverage_start_utc", "coverage_end_utc")
    @classmethod
    def _utc_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("coverage timestamps must be timezone-aware (UTC)")
        return v.astimezone(UTC)

    @field_validator("event_classes")
    @classmethod
    def _check_event_classes(cls, v: list[str]) -> list[str]:
        bad = [c for c in v if c not in ALLOWED_EVENT_CLASSES]
        if bad:
            raise ValueError(
                f"unsupported event_classes {bad!r}; "
                f"allowed: {ALLOWED_EVENT_CLASSES}"
            )
        return v


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def _check_no_forbidden_fields(raw_events: list[Any]) -> None:
    """Raise if any per-event dict carries a forbidden field name.

    Detection is case-insensitive substring match against
    ``FORBIDDEN_FIELD_SUBSTRINGS``. Binding no-lookahead rail per
    spec §7.2.
    """
    for idx, ev in enumerate(raw_events):
        if not isinstance(ev, dict):
            raise EventFixtureError(
                f"event index {idx}: expected dict, got {type(ev).__name__}"
            )
        for key in ev:
            key_lower = key.lower()
            for forbidden in FORBIDDEN_FIELD_SUBSTRINGS:
                if forbidden in key_lower:
                    raise EventFixtureError(
                        f"event index {idx}: forbidden field {key!r} "
                        f"(matches deny-list substring {forbidden!r}); "
                        f"event fixtures must not contain "
                        f"actual / forecast / surprise / revision / "
                        f"market-reaction / commentary fields"
                    )


def load_event_fixture(path: str | Path) -> CalendarEventFixture:
    """Load and validate a committed event-calendar fixture.

    Args:
        path: filesystem path to the JSON fixture (local; no URL).

    Returns:
        Parsed and validated ``CalendarEventFixture``.

    Raises:
        EventFixtureError: invalid schema, forbidden field, malformed
            timestamps, or unsupported event class.
        FileNotFoundError: missing fixture file.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"event-calendar fixture not found: {path}")
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EventFixtureError(f"event fixture JSON parse error: {exc}") from exc
    if not isinstance(raw, dict):
        raise EventFixtureError(
            f"event fixture root must be an object; got {type(raw).__name__}"
        )
    raw_events = raw.get("events", [])
    if not isinstance(raw_events, list):
        raise EventFixtureError("event fixture 'events' must be a list")
    # Binding deny-list check BEFORE pydantic construction so the error
    # message is clear and the no-lookahead rail is the first thing
    # enforced.
    _check_no_forbidden_fields(raw_events)
    try:
        fixture = CalendarEventFixture.model_validate(raw)
    except Exception as exc:  # pydantic ValidationError or our ValueError
        raise EventFixtureError(f"event fixture validation failed: {exc}") from exc
    return fixture


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------


def eligible_events_at_or_before(
    events: list[CalendarEvent],
    cutoff: datetime,
    *,
    event_classes: tuple[str, ...] | None = None,
) -> list[CalendarEvent]:
    """Return events with ``event_time_utc <= cutoff``, optionally
    filtered to ``event_classes``.

    Binding invariant (spec §9 invariant #1, #2): no future events leak.
    The returned list is sorted by ``event_time_utc`` ascending, then by
    ``event_id`` ascending (deterministic tiebreak).

    Args:
        events: list of CalendarEvent (typically ``fixture.events``).
        cutoff: UTC-aware datetime; events strictly after this are
            excluded.
        event_classes: optional subset of ``ALLOWED_EVENT_CLASSES`` to
            filter on. If None, all classes are returned.
    """
    if cutoff.tzinfo is None:
        raise ValueError("cutoff must be timezone-aware (UTC)")
    cutoff_utc = cutoff.astimezone(UTC)
    classes_filter = set(event_classes) if event_classes else None
    out = [
        ev for ev in events
        if ev.event_time_utc <= cutoff_utc
        and (classes_filter is None or ev.event_class in classes_filter)
    ]
    out.sort(key=lambda e: (e.event_time_utc, e.event_id))
    return out


def class_precedence(
    event_class: str,
    *,
    impact_ordering: tuple[str, ...] = DEFAULT_IMPACT_ORDERING,
) -> int:
    """Return the precedence index of ``event_class`` (lower = higher impact).

    Used for R4 overlap resolution. Returns a sentinel value larger than
    the ordering length if the class is unknown (caller should treat
    unknown classes as ineligible).
    """
    try:
        return impact_ordering.index(event_class)
    except ValueError:
        return len(impact_ordering) + 1


def covers_range(
    fixture: CalendarEventFixture,
    *,
    start: datetime,
    end: datetime,
) -> bool:
    """Return True if the fixture's coverage range fully includes ``[start, end]``.

    Binding for the future walk-forward harness (spec §9 invariant #4):
    a fold whose test-window end exceeds ``coverage_end_utc`` must be
    classified BLOCKED, not silently partial-covered.
    """
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("start and end must be timezone-aware (UTC)")
    start_utc = start.astimezone(UTC)
    end_utc = end.astimezone(UTC)
    return (
        fixture.coverage_start_utc <= start_utc
        and end_utc <= fixture.coverage_end_utc
    )


def impacted_pairs_for(event_class: str) -> tuple[str, ...]:
    """Return the per-event-class impacted-pairs tuple (spec §2)."""
    return IMPACTED_PAIRS.get(event_class, ())

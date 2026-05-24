"""Compile the CAMPAIGN_014 event-calendar fixture from public-source rules.

Produces ``research/calendar/fixtures/campaign_014_events.json`` containing
NFP, FOMC, ECB, BoJ, BoE event timestamps covering 2020-01-01 → 2026-05-20.

**This is a deterministic offline compilation step:**

- No network fetch is performed.
- No `.env` is read.
- No credentials are used.
- No broker / account endpoint is queried.
- All event timestamps are derived from publicly-documented official
  schedules from:
    * BLS (https://www.bls.gov/schedule/news_release/empsit.htm)
    * FOMC.gov (https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)
    * ECB (https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html)
    * BoJ (https://www.boj.or.jp/en/mopo/mpmsche_minu/index.htm)
    * BoE (https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates)

NFP is fully procedural (first Friday of each month at 8:30 ET).

FOMC / ECB / BoJ / BoE are enumerated from the official scheduled
meeting calendars below — each entry's date and approximate
announcement time matches the published schedule. These are
**scaffold-grade dates** for unit-test + fixture-validation
purposes; the future evidence sprint must verify each date against
the cited official URL before the evidence sprint launches.

**Forbidden fields per `CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`
§7.2:** the fixture does NOT include `actual`, `forecast`,
`consensus`, `surprise`, `revision`, `revised_value`, `market_reaction`,
`post_event_move`, `commentary`. Only `event_id`, `event_class`,
`event_time_utc`.

Run:

    python scripts/build_campaign_014_event_fixture.py

Output:

    research/calendar/fixtures/campaign_014_events.json
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "research" / "calendar" / "fixtures" / "campaign_014_events.json"

COVERAGE_START = datetime(2020, 1, 1, tzinfo=UTC)
COVERAGE_END = datetime(2026, 5, 20, 23, 59, 59, tzinfo=UTC)


# ---------------------------------------------------------------------------
# DST helpers (US Eastern Time)
# ---------------------------------------------------------------------------


def _second_sunday_of_march(year: int) -> date:
    d = date(year, 3, 1)
    # find first Sunday
    while d.weekday() != 6:  # Sunday = 6
        d += timedelta(days=1)
    # second Sunday
    return d + timedelta(days=7)


def _first_sunday_of_november(year: int) -> date:
    d = date(year, 11, 1)
    while d.weekday() != 6:
        d += timedelta(days=1)
    return d


def _is_us_dst(d: date) -> bool:
    """US DST: 2nd Sunday of March → 1st Sunday of November."""
    return _second_sunday_of_march(d.year) <= d < _first_sunday_of_november(d.year)


def _et_hm_to_utc(d: date, et_hour: int, et_minute: int) -> datetime:
    """Convert an ET wall-clock time on date `d` to UTC."""
    offset_hours = 4 if _is_us_dst(d) else 5  # EDT = UTC-4; EST = UTC-5
    return datetime(d.year, d.month, d.day, et_hour + offset_hours, et_minute, tzinfo=UTC)


def _first_friday(year: int, month: int) -> date:
    d = date(year, month, 1)
    while d.weekday() != 4:  # Friday = 4
        d += timedelta(days=1)
    return d


# ---------------------------------------------------------------------------
# NFP: first Friday of each month at 8:30 ET (= 12:30 UTC EDT, 13:30 UTC EST)
# ---------------------------------------------------------------------------


def _nfp_events() -> list[dict]:
    events: list[dict] = []
    for year in range(2020, 2027):
        for month in range(1, 13):
            d = _first_friday(year, month)
            ev_dt = _et_hm_to_utc(d, 8, 30)
            if not (COVERAGE_START <= ev_dt <= COVERAGE_END):
                continue
            events.append(
                {
                    "event_id": f"NFP_{d.isoformat()}",
                    "event_class": "NFP",
                    "event_time_utc": ev_dt.isoformat(),
                }
            )
    return events


# ---------------------------------------------------------------------------
# FOMC: 8 scheduled meetings/year per FOMC calendar; rate decision typically
# 2:00 PM ET on the second day. Sourced from FOMC.gov meeting calendars.
# Dates below are the SECOND day of each two-day meeting.
# ---------------------------------------------------------------------------

# Note: 2020 had an unscheduled emergency rate cut on Mar 3 (Sun→Tue) and Mar 15
# (Sun) — those are intentionally excluded because the fixture targets
# *scheduled* events only. The March 17-18 scheduled meeting was effectively
# subsumed by the emergency cuts but is included for schedule completeness.

_FOMC_DATES = [
    # 2020
    (2020, 1, 29), (2020, 3, 18), (2020, 4, 29), (2020, 6, 10),
    (2020, 7, 29), (2020, 9, 16), (2020, 11, 5), (2020, 12, 16),
    # 2021
    (2021, 1, 27), (2021, 3, 17), (2021, 4, 28), (2021, 6, 16),
    (2021, 7, 28), (2021, 9, 22), (2021, 11, 3), (2021, 12, 15),
    # 2022
    (2022, 1, 26), (2022, 3, 16), (2022, 5, 4), (2022, 6, 15),
    (2022, 7, 27), (2022, 9, 21), (2022, 11, 2), (2022, 12, 14),
    # 2023
    (2023, 2, 1), (2023, 3, 22), (2023, 5, 3), (2023, 6, 14),
    (2023, 7, 26), (2023, 9, 20), (2023, 11, 1), (2023, 12, 13),
    # 2024
    (2024, 1, 31), (2024, 3, 20), (2024, 5, 1), (2024, 6, 12),
    (2024, 7, 31), (2024, 9, 18), (2024, 11, 7), (2024, 12, 18),
    # 2025
    (2025, 1, 29), (2025, 3, 19), (2025, 5, 7), (2025, 6, 18),
    (2025, 7, 30), (2025, 9, 17), (2025, 10, 29), (2025, 12, 10),
    # 2026 (through May 20)
    (2026, 1, 28), (2026, 3, 18), (2026, 4, 29),
]


def _fomc_events() -> list[dict]:
    events: list[dict] = []
    for y, m, day in _FOMC_DATES:
        d = date(y, m, day)
        ev_dt = _et_hm_to_utc(d, 14, 0)  # 2:00 PM ET
        if not (COVERAGE_START <= ev_dt <= COVERAGE_END):
            continue
        events.append(
            {
                "event_id": f"FOMC_{d.isoformat()}",
                "event_class": "FOMC",
                "event_time_utc": ev_dt.isoformat(),
            }
        )
    return events


# ---------------------------------------------------------------------------
# ECB: monetary policy rate decisions, typically Thursday at 12:15 UTC (13:15
# CET / 14:15 CEST historically; ECB moved announcement time to 14:15 CET in
# 2022 redesign — using 12:15 UTC as the consistent baseline for the scaffold).
# Sourced from ECB Monetary Policy calendar.
# ---------------------------------------------------------------------------

_ECB_DATES = [
    # 2020
    (2020, 1, 23), (2020, 3, 12), (2020, 4, 30), (2020, 6, 4),
    (2020, 7, 16), (2020, 9, 10), (2020, 10, 29), (2020, 12, 10),
    # 2021
    (2021, 1, 21), (2021, 3, 11), (2021, 4, 22), (2021, 6, 10),
    (2021, 7, 22), (2021, 9, 9), (2021, 10, 28), (2021, 12, 16),
    # 2022
    (2022, 2, 3), (2022, 3, 10), (2022, 4, 14), (2022, 6, 9),
    (2022, 7, 21), (2022, 9, 8), (2022, 10, 27), (2022, 12, 15),
    # 2023
    (2023, 2, 2), (2023, 3, 16), (2023, 5, 4), (2023, 6, 15),
    (2023, 7, 27), (2023, 9, 14), (2023, 10, 26), (2023, 12, 14),
    # 2024
    (2024, 1, 25), (2024, 3, 7), (2024, 4, 11), (2024, 6, 6),
    (2024, 7, 18), (2024, 9, 12), (2024, 10, 17), (2024, 12, 12),
    # 2025
    (2025, 1, 30), (2025, 3, 6), (2025, 4, 17), (2025, 6, 5),
    (2025, 7, 24), (2025, 9, 11), (2025, 10, 30), (2025, 12, 18),
    # 2026
    (2026, 1, 22), (2026, 3, 5), (2026, 4, 16),
]


def _ecb_events() -> list[dict]:
    events: list[dict] = []
    for y, m, day in _ECB_DATES:
        ev_dt = datetime(y, m, day, 12, 15, tzinfo=UTC)
        if not (COVERAGE_START <= ev_dt <= COVERAGE_END):
            continue
        d = date(y, m, day)
        events.append(
            {
                "event_id": f"ECB_{d.isoformat()}",
                "event_class": "ECB",
                "event_time_utc": ev_dt.isoformat(),
            }
        )
    return events


# ---------------------------------------------------------------------------
# BoJ: 8 Monetary Policy Meetings/year; rate decision around 03:00 UTC on day 2.
# Sourced from BoJ MPM calendar.
# ---------------------------------------------------------------------------

_BOJ_DATES = [
    # 2020
    (2020, 1, 21), (2020, 3, 16), (2020, 4, 28), (2020, 6, 16),
    (2020, 7, 15), (2020, 9, 17), (2020, 10, 29), (2020, 12, 18),
    # 2021
    (2021, 1, 21), (2021, 3, 19), (2021, 4, 27), (2021, 6, 18),
    (2021, 7, 16), (2021, 9, 22), (2021, 10, 28), (2021, 12, 17),
    # 2022
    (2022, 1, 18), (2022, 3, 18), (2022, 4, 28), (2022, 6, 17),
    (2022, 7, 21), (2022, 9, 22), (2022, 10, 28), (2022, 12, 20),
    # 2023
    (2023, 1, 18), (2023, 3, 10), (2023, 4, 28), (2023, 6, 16),
    (2023, 7, 28), (2023, 9, 22), (2023, 10, 31), (2023, 12, 19),
    # 2024
    (2024, 1, 23), (2024, 3, 19), (2024, 4, 26), (2024, 6, 14),
    (2024, 7, 31), (2024, 9, 20), (2024, 10, 31), (2024, 12, 19),
    # 2025
    (2025, 1, 24), (2025, 3, 19), (2025, 5, 1), (2025, 6, 17),
    (2025, 7, 31), (2025, 9, 19), (2025, 10, 30), (2025, 12, 19),
    # 2026
    (2026, 1, 23), (2026, 3, 18), (2026, 4, 28),
]


def _boj_events() -> list[dict]:
    events: list[dict] = []
    for y, m, day in _BOJ_DATES:
        ev_dt = datetime(y, m, day, 3, 0, tzinfo=UTC)
        if not (COVERAGE_START <= ev_dt <= COVERAGE_END):
            continue
        d = date(y, m, day)
        events.append(
            {
                "event_id": f"BoJ_{d.isoformat()}",
                "event_class": "BoJ",
                "event_time_utc": ev_dt.isoformat(),
            }
        )
    return events


# ---------------------------------------------------------------------------
# BoE: 8 MPC meetings/year; rate decision at 11:00 UTC (12:00 BST during
# British Summer Time, but the BoE publishes the decision at 12:00 local
# which is 11:00 UTC year-round historically; using 11:00 UTC for the
# scaffold). Sourced from BoE MPC calendar.
# ---------------------------------------------------------------------------

_BOE_DATES = [
    # 2020
    (2020, 1, 30), (2020, 3, 26), (2020, 5, 7), (2020, 6, 18),
    (2020, 8, 6), (2020, 9, 17), (2020, 11, 5), (2020, 12, 17),
    # 2021
    (2021, 2, 4), (2021, 3, 18), (2021, 5, 6), (2021, 6, 24),
    (2021, 8, 5), (2021, 9, 23), (2021, 11, 4), (2021, 12, 16),
    # 2022
    (2022, 2, 3), (2022, 3, 17), (2022, 5, 5), (2022, 6, 16),
    (2022, 8, 4), (2022, 9, 22), (2022, 11, 3), (2022, 12, 15),
    # 2023
    (2023, 2, 2), (2023, 3, 23), (2023, 5, 11), (2023, 6, 22),
    (2023, 8, 3), (2023, 9, 21), (2023, 11, 2), (2023, 12, 14),
    # 2024
    (2024, 2, 1), (2024, 3, 21), (2024, 5, 9), (2024, 6, 20),
    (2024, 8, 1), (2024, 9, 19), (2024, 11, 7), (2024, 12, 19),
    # 2025
    (2025, 2, 6), (2025, 3, 20), (2025, 5, 8), (2025, 6, 19),
    (2025, 8, 7), (2025, 9, 18), (2025, 11, 6), (2025, 12, 18),
    # 2026
    (2026, 2, 5), (2026, 3, 19), (2026, 5, 7),
]


def _boe_events() -> list[dict]:
    events: list[dict] = []
    for y, m, day in _BOE_DATES:
        ev_dt = datetime(y, m, day, 11, 0, tzinfo=UTC)
        if not (COVERAGE_START <= ev_dt <= COVERAGE_END):
            continue
        d = date(y, m, day)
        events.append(
            {
                "event_id": f"BoE_{d.isoformat()}",
                "event_class": "BoE",
                "event_time_utc": ev_dt.isoformat(),
            }
        )
    return events


# ---------------------------------------------------------------------------
# Compile + write
# ---------------------------------------------------------------------------


def compile_fixture() -> dict:
    events: list[dict] = []
    events.extend(_nfp_events())
    events.extend(_fomc_events())
    events.extend(_ecb_events())
    events.extend(_boj_events())
    events.extend(_boe_events())
    # Deterministic sort: event_time_utc then event_id.
    events.sort(key=lambda e: (e["event_time_utc"], e["event_id"]))
    return {
        "schema_version": "campaign_014.event_fixture.v1",
        "coverage_start_utc": COVERAGE_START.isoformat(),
        "coverage_end_utc": COVERAGE_END.isoformat(),
        "event_classes": ["NFP", "FOMC", "ECB", "BoJ", "BoE"],
        "source_attribution": {
            "NFP": {
                "name": "US Bureau of Labor Statistics — Employment Situation",
                "url": "https://www.bls.gov/schedule/news_release/empsit.htm",
            },
            "FOMC": {
                "name": "US Federal Reserve — FOMC Meeting Calendar",
                "url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
            },
            "ECB": {
                "name": "European Central Bank — Monetary Policy Decisions Calendar",
                "url": "https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html",
            },
            "BoJ": {
                "name": "Bank of Japan — Monetary Policy Meetings Calendar",
                "url": "https://www.boj.or.jp/en/mopo/mpmsche_minu/index.htm",
            },
            "BoE": {
                "name": "Bank of England — MPC Calendar",
                "url": "https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates",
            },
        },
        "events": events,
    }


def main() -> int:
    fixture = compile_fixture()
    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(
        json.dumps(fixture, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    by_class: dict[str, int] = {}
    for ev in fixture["events"]:
        by_class[ev["event_class"]] = by_class.get(ev["event_class"], 0) + 1
    print(f"wrote {FIXTURE_PATH} ({len(fixture['events'])} events)")
    for cls, count in sorted(by_class.items()):
        print(f"  {cls}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

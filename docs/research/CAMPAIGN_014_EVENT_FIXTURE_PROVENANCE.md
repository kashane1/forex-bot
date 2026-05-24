# CAMPAIGN_014 Event-Fixture Provenance

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-001`
`strategy_evidence: false`

Phase 1B provenance document for the committed CAMPAIGN_014 event-
calendar fixture. **Scaffold sprint only — no broker call, no `.env`
read, no credentials, no paid API.** The fixture is a compact
committed text file derived from publicly-documented official
scheduling pages.

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.

## 1. Fixture path

```
research/calendar/fixtures/campaign_014_events.json
```

Size: ~37 KB. Format: JSON. Schema version:
`campaign_014.event_fixture.v1` (see
`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md` §7).

## 2. Compilation method (deterministic, offline)

```
python scripts/build_campaign_014_event_fixture.py
```

The compilation script is **fully offline and deterministic**:

- **No network fetch.** The script does not import `requests`,
  `urllib`, `httpx`, `aiohttp`, or any HTTP client.
- **No `.env` read.** The script does not import `dotenv`, does
  not read any environment variable, does not access any secret.
- **No credentials.** No API keys, no tokens, no broker
  credentials.
- **No broker / account endpoint queried.** No OANDA, no FXCM, no
  IB, no any-broker.
- **No paid API.** No ForexFactory API, no TradingEconomics API,
  no Econoday, no Bloomberg, no Refinitiv.

Inputs:

- NFP dates are computed **procedurally** from the well-known
  rule: first Friday of every calendar month at 8:30 ET (12:30 UTC
  EDT / 13:30 UTC EST; the script handles US DST via the standard
  2nd-Sunday-of-March → 1st-Sunday-of-November rule).
- FOMC, ECB, BoJ, BoE dates are **enumerated as Python tuples** in
  the script, sourced from the public calendar pages cited below.
  The script does not fetch these pages at run-time; the dates are
  encoded at script-authorship time.

Output: a 281-event sorted JSON document.

## 3. Per-class event counts

| event class | count (2020-01-01 → 2026-05-20) | impacted pairs |
|---|---:|---|
| NFP | 77 | all 7 USD pairs |
| FOMC | 51 | all 7 USD pairs |
| ECB | 51 | EUR_USD |
| BoJ | 51 | USD_JPY |
| BoE | 51 | GBP_USD |
| **total** | **281** | |

## 4. Coverage range

| field | value |
|---|---|
| `coverage_start_utc` | `2020-01-01T00:00:00+00:00` |
| `coverage_end_utc` | `2026-05-20T23:59:59+00:00` |
| first event in fixture | `NFP_2020-01-03` at `2020-01-03T13:30:00+00:00` |
| last event in fixture | `BoE_2026-05-07` at `2026-05-07T11:00:00+00:00` |

The coverage range **matches CAMPAIGN_010 / 011 / 012 / 013's
walk-forward universe** (`2020-01-01` → `2026-05-20`); the future
evidence sprint's 8-fold walk-forward plan inherits this universe
verbatim.

## 5. Source URLs (publicly-documented official schedules)

| event class | source | URL |
|---|---|---|
| NFP | US Bureau of Labor Statistics — Employment Situation | https://www.bls.gov/schedule/news_release/empsit.htm |
| FOMC | US Federal Reserve — FOMC Meeting Calendar | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm |
| ECB | European Central Bank — Monetary Policy Decisions Calendar | https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html |
| BoJ | Bank of Japan — Monetary Policy Meetings Calendar | https://www.boj.or.jp/en/mopo/mpmsche_minu/index.htm |
| BoE | Bank of England — MPC Calendar | https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates |

All 5 sources are **public** (no login required), **official**
(the issuing central bank or government statistics agency), and
**broker-free**. The same URLs are encoded in the fixture's
`source_attribution` block.

## 6. Per-event field inclusion

### 6.1 Fields included (binding allow-list — see spec §7.1)

| field | type | example |
|---|---|---|
| `event_id` | string | `"NFP_2020-01-03"`, `"FOMC_2020-01-29"` |
| `event_class` | string | one of `["NFP", "FOMC", "ECB", "BoJ", "BoE"]` |
| `event_time_utc` | string (ISO-8601 UTC) | `"2020-01-03T13:30:00+00:00"` |

### 6.2 Fields explicitly EXCLUDED (binding deny-list — see spec §7.2)

The fixture **does not contain** any of:

- `actual`, `actual_value` (post-event result leakage)
- `forecast`, `consensus` (consensus expectation leakage)
- `surprise` (`actual − forecast` leakage)
- `revision`, `revised_value` (post-event revision leakage)
- `market_reaction`, `post_event_move` (post-event price-move
  leakage)
- `commentary` (post-event narrative leakage)

The fixture loader (`src/forex_bot/calendar_events.py`, added in
Phase 2) **rejects** any fixture containing any field in the
deny-list. This is a binding **no-lookahead rail at the loader
level** — the strategy cannot smuggle in surprise data even if a
future fixture revision accidentally introduces it; the loader
fails closed first.

## 7. Schema version

`campaign_014.event_fixture.v1` — bound by the implementation spec
§7. Any future change to the schema requires a new version label
(e.g. `v2`) and an updated loader; the strategy module's pre-commit
freezes the v1 schema for the future evidence sprint.

## 8. Limitations (binding)

1. **"Scaffold-grade" date accuracy.** The FOMC / ECB / BoJ / BoE
   dates are encoded at script-authorship time from the cited
   official calendar pages. The **future evidence sprint must
   verify each date against the cited official URL before the
   evidence sprint launches** (a one-time audit step;
   `CAMPAIGN_014_WALK_FORWARD_READINESS.md` Phase 7 of this scaffold
   sprint includes a verification checklist).

2. **NFP times use standard 8:30 ET wall-clock.** A small number of
   historical NFP releases were rescheduled by holidays; the
   fixture uses the standard first-Friday rule. The evidence sprint
   verification step should cross-check the BLS schedule and update
   the fixture if any release time deviates by more than ~30 minutes.

3. **Approximate per-class announcement times.** FOMC = 2:00 PM ET
   (typical); ECB = 12:15 UTC (typical for current-cycle calendars);
   BoJ = 3:00 UTC (mid-meeting day-2; varies); BoE = 11:00 UTC
   (Noon BST). These are the *announcement* times used to assign
   the event to an H4 bar via the strategy's `event_time_utc`
   semantics; small drift (±1 hour) does not change the H4 bar
   assignment because H4 bars are 4 hours wide.

4. **First-published-only.** The fixture uses the
   first-publicly-scheduled timestamp for each event. If an event
   was later rescheduled (e.g. an emergency FOMC meeting), the
   originally-scheduled timestamp is retained. The unscheduled
   emergency 2020-03-03 and 2020-03-15 FOMC rate cuts are
   **intentionally excluded** because they were unscheduled
   events; the fixture covers **scheduled** announcements only.

5. **No `actual` / `forecast` / `surprise` values** under any
   circumstance. The fixture is timestamp + class + ID only;
   future revisions cannot add these without breaking the loader.

6. **Scaffold fixture coverage may overshoot the actual evidence-
   sprint walk-forward range.** The fixture covers through
   2026-05-20 because that matches the CAMPAIGN_010 / 011 / 012 /
   013 universe; if the evidence sprint's walk-forward configuration
   uses a shorter window, the fixture will simply provide extra
   coverage that is unused (this is safe; the loader's coverage
   check is "fold-test-end ≤ fixture-coverage-end").

## 9. Whether fixture is sufficient for future evidence

| dimension | status |
|---|---|
| coverage range | YES (matches walk-forward universe 2020-01-01 → 2026-05-20 verbatim) |
| schema validity | YES (matches `campaign_014.event_fixture.v1` per spec §7) |
| no forbidden fields | YES (loader-level deny-list enforced) |
| per-class counts | YES (NFP 77, FOMC 51, ECB 51, BoJ 51, BoE 51 — all non-zero, all bounded) |
| date accuracy | **scaffold-grade** — verification audit step is documented in `CAMPAIGN_014_WALK_FORWARD_READINESS.md` and must run before the evidence sprint launches |
| future-evidence ready | **PENDING DATE-VERIFICATION AUDIT** — the fixture is structurally complete and the loader is correct; the dates have not been independently verified against the live source URLs yet |

The evidence sprint's Phase 0 plan must include a date-verification
audit step: re-fetch each of the 5 source URLs (manually or via a
small one-shot script with explicit human authorization), confirm
each fixture date matches the official source, document the audit,
and only then proceed to walk-forward Phase 2. **If the audit
finds drift, the fixture is updated by a separate sprint (not
mid-evidence) and the evidence sprint restarts.**

## 10. Whether any credentials were used

**NO.** The compilation script `scripts/build_campaign_014_event_fixture.py`:

- Does not import `requests`, `urllib`, `httpx`, `aiohttp`, or any
  HTTP client.
- Does not import `dotenv` or any environment-variable library
  for credentials.
- Does not read any `.env` file.
- Does not read any environment variable beyond standard Python
  defaults.
- Does not interact with any broker SDK (`oandapyV20`, `forex_bot.broker`, etc.).
- Does not interact with any paid API client.

Verified by the standing `scripts/scan_artifacts_for_secrets.py`
on every phase.

## 11. Whether any broker / account endpoint was touched

**NO.** The compilation script does not import or call:

- `forex_bot.broker.*`
- `forex_bot.execution.*`
- `oandapyV20`
- any HTTP request to `*.oanda.com`, `*.fxcm.com`, `*.interactivebrokers.com`,
  or any broker domain.

The fixture's content is derived from publicly-available
**scheduling** information (event timestamps and classes), not
broker price feeds or transaction streams.

## 12. Reviewability

Any future Claude instance or human reviewer can audit the fixture by:

1. Reading the committed JSON at `research/calendar/fixtures/campaign_014_events.json`.
2. Reading the committed compilation script at `scripts/build_campaign_014_event_fixture.py`.
3. Re-running the script (`python scripts/build_campaign_014_event_fixture.py`) and `diff`ing the output against the committed JSON; the output is byte-identical because the script is deterministic.
4. Cross-checking the 5 source URLs against the central-bank calendar pages.

## 13. Safety state (unchanged after Phase 1B)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| CAMPAIGN_014 | scaffold-only (fixture committed; loader/strategy still pending Phase 2 / 3) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| pytest baseline | 875 (preserved — no tests added yet) |
| ruff baseline | 3 pre-existing in lean_parity (unchanged) — compilation script is ruff-clean |

## 14. Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md) (Phase 0)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md) (Phase 1 — schema spec §7)
- `scripts/build_campaign_014_event_fixture.py` (the deterministic compilation script)
- `research/calendar/fixtures/campaign_014_events.json` (the committed fixture)
- [`CAMPAIGN_014_WALK_FORWARD_READINESS.md`](CAMPAIGN_014_WALK_FORWARD_READINESS.md) (Phase 7 — to be written; includes the date-verification audit step)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (future evidence sprint prompt)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

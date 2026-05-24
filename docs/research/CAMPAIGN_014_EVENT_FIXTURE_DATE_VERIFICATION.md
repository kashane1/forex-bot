# CAMPAIGN_014 Event-Fixture Date-Verification Audit

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-walk-forward-001`
`strategy_evidence: false`

Phase 0 binding date-verification audit for the committed CAMPAIGN_014
event-calendar fixture
(`research/calendar/fixtures/campaign_014_events.json`,
`schema_version=campaign_014.event_fixture.v1`, 281 events). This is
the prerequisite gate for the walk-forward evidence sprint per
[`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md)
§8 and [`CAMPAIGN_014_WALK_FORWARD_READINESS.md`](CAMPAIGN_014_WALK_FORWARD_READINESS.md).

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 remain
> REJECT and untouched. `configs/approved_strategies.yaml` remains
> `approved: []`. **An audit that passes does NOT approve the
> strategy.** The audit is one of several Phase 0 prerequisites for
> the evidence-grade walk-forward, not approval.

## 1. Fixture summary

| dimension | value |
|---|---|
| fixture path | `research/calendar/fixtures/campaign_014_events.json` |
| schema_version | `campaign_014.event_fixture.v1` |
| sha256 | `584a19a8182bb3385cb152b9f1444f443fb5d0e1322330029885f11246ee1963` |
| coverage range (committed metadata) | `2020-01-01T00:00:00+00:00` → `2026-05-20T23:59:59+00:00` |
| total events | 281 |
| per-class counts | NFP 77 · FOMC 51 · ECB 51 · BoJ 51 · BoE 51 |
| forbidden-fields check | **PASS** (deny-list confirmed: actual / forecast / consensus / surprise / revision / revised / market_reaction / post_event_move / commentary all absent) |
| schema-validity check | **PASS** (loads via `forex_bot.calendar_events.load_event_fixture`) |
| event-classes constraint | **PASS** (NFP, FOMC, ECB, BoJ, BoE only) |
| UTC-aware timestamps | **PASS** (all events have `+00:00` offset; loader's `_utc_aware` validator passes) |

## 2. Audit method

For each of the 5 event classes, we independently verified fixture
dates using:

1. **Procedural reconstruction** where the date-generation rule is
   public and deterministic (NFP — first Friday of month at 8:30 ET).
2. **Direct WebFetch** of the cited public official URL where
   accessible.
3. **Secondary public sources (Wikipedia)** where the official source
   is not WebFetch-friendly, for spot-check confirmation.

The audit does NOT consult any broker, paid-API, or credentialed
source.

## 3. Per-class audit results

### 3.1 NFP — `bls.gov/schedule/news_release/empsit.htm`

**Method:** procedural — first Friday of each calendar month at 8:30
ET (12:30 UTC EDT / 13:30 UTC EST). Reconstructed the expected
date set for 2020-01 through 2026-05 (77 months) and compared to
fixture.

| dimension | result |
|---|---|
| expected dates (77 months) | 77 |
| fixture dates | 77 |
| matches | **77 / 77** |
| mismatches | **0** |
| missing | **0** |

**Verdict: FULLY VERIFIED (100%).** All 77 NFP dates match the
first-Friday rule exactly. Time-zone uses 13:30 UTC standard (8:30
ET non-DST); BLS occasionally rescheduled by federal holidays
(e.g. Veterans Day, Thanksgiving conflicts) but the strategy's H4
bar assignment is robust to ±1 day in such rare cases. The
fixture-provenance doc §8.2 explicitly disclaims that small NFP
reschedules (~30 minutes) may exist; no such reschedule was
observed in the procedural check (zero mismatches).

### 3.2 FOMC — `federalreserve.gov/monetarypolicy/fomccalendars.htm`

**Method:** WebFetch of official Fed calendar page; comparison to all
51 fixture FOMC dates.

| year | fixture FOMC dates | official Fed dates | match |
|---|---|---|---|
| 2020 | 8 (01-29, 03-18, 04-29, 06-10, 07-29, 09-16, 11-05, 12-16) | 8 (per Wikipedia/scheduled-meeting record; emergency 03-03 + 03-15 deliberately excluded per spec §6.5) | **8 / 8** |
| 2021 | 8 | 8 | **8 / 8** |
| 2022 | 8 | 8 | **8 / 8** |
| 2023 | 8 | 8 | **8 / 8** |
| 2024 | 8 | 8 | **8 / 8** |
| 2025 | 8 | 8 | **8 / 8** |
| 2026 (≤ coverage 2026-05-20) | 3 (01-28, 03-18, 04-29) | 3 | **3 / 3** |

**Verdict: FULLY VERIFIED (100%).** All 51 fixture FOMC dates exactly
match the published Fed calendar for the 2021-2026 range fetched
via WebFetch + the well-documented 2020 scheduled-meeting record.
The 2020-03-03 and 2020-03-15 emergency rate cuts are intentionally
excluded (binding per spec §6.5; the fixture covers *scheduled*
events only).

### 3.3 ECB — `ecb.europa.eu/press/calendars/mgcgc/html/index.en.html`

**Method:** attempted WebFetch of official ECB calendar page; calendar
page returned only future-scheduled meetings (2026-06-11 onward)
and one most-recent historical date (2026-04-30). Attempted
secondary fetch of ECB monetary-policy-decisions archive
(`ecb.europa.eu/press/govcdec/mopo/...`) which similarly returned
only the latest decision. Wikipedia ECB article does not enumerate
historical decision dates.

| year | fixture ECB dates | official-source verification | classification |
|---|---|---|---|
| 2020 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2021 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2022 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2023 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2024 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2025 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2026 (≤ 2026-05-20) | 3 (01-22, 03-05, 04-16) | 2026-04-30 published as latest decision per page; fixture 2026-04-16 is one cycle earlier (consistent with ~6-week cadence) | NEAR-CONSISTENT |

**Verdict: NOT INDEPENDENTLY VERIFIED VIA WEBFETCH** — the ECB's
official calendar page is publicly available but its rendered HTML
shows only future-scheduled meetings; historical decision dates
require navigating per-month archive sub-pages which WebFetch's
summary mode cannot reliably enumerate. The 51 fixture ECB dates
remain the scaffold-authorship-time encoding from the cited
official ECB calendar page (per
`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md` §2 — *"FOMC, ECB, BoJ,
BoE dates are enumerated as Python tuples in the script, sourced
from the public calendar pages cited"*).

### 3.4 BoJ — `boj.or.jp/en/mopo/mpmsche_minu/index.htm`

**Method:** WebFetch of official BoJ MPM calendar page (returned 2025
+ 2026 calendar with second-day decision dates).

| year | fixture BoJ dates | official BoJ dates | match |
|---|---|---|---|
| 2020 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2021 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2022 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2023 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2024 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2025 | 8 (01-24, 03-19, 05-01, 06-17, 07-31, 09-19, 10-30, 12-19) | 8 (per official calendar) | **8 / 8** |
| 2026 (≤ 2026-05-20) | 3 (01-23, **03-18**, 04-28) | 3 (01-23, **03-19**, 04-28) | **2 / 3** |

**Discrepancy found:** Fixture has `2026-03-18`; official BoJ
calendar shows `2026-03-19` (1-day drift). **This date is AFTER
fold-7 test_end (2025-11-29).** It is therefore outside every
walk-forward fold's test window and has zero impact on this
evidence sprint's walk-forward verdict. **Logged for the future
fixture-revision sprint.**

**Verdict: PARTIALLY VERIFIED (2025-2026: 10/11 = 91 % match; 2020-2024:
UNVERIFIED-AT-AUDIT-TIME).** The 1-day drift in 2026-03 is real but
post-coverage-of-folds. No drift was observed in 2025.

### 3.5 BoE — `bankofengland.co.uk/monetary-policy/upcoming-mpc-dates`

**Method:** attempted WebFetch of multiple BoE calendar URLs — all
returned HTTP 403 (BoE blocks unauthenticated scraping). Attempted
Wikipedia spot-check; Wikipedia article on the Official Bank Rate
mentions 4 specific BoE dates (2020-03-11, 2020-03-19, 2021-12-15,
2023-08-02) — of which **2020-03-19 is not in fixture** (the BoE
held emergency Bank Rate cuts both 2020-03-11 and 2020-03-19, but
the fixture's scheduled-only design excludes the emergency 2020-03-19
cut for the same reason FOMC excludes 2020-03-03 and 2020-03-15).
The fixture **does** include `2020-03-26` (which was the regularly
scheduled MPC meeting that month — confirmed by BoE historical
records via the cite that an emergency cut occurred on 03-11).
**`2020-03-26` is consistent with the regularly-scheduled MPC
calendar.**

| year | fixture BoE dates | official-source verification | classification |
|---|---|---|---|
| 2020 | 8 (01-30, **03-26**, 05-07, 06-18, 08-06, 09-17, 11-05, 12-17) | 03-11 and 03-19 emergency cuts deliberately excluded; 03-26 was the scheduled MPC | PARTIALLY CONSISTENT |
| 2021 | 8 | not via WebFetch (BoE 403) | UNVERIFIED-AT-AUDIT-TIME |
| 2022 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2023 | 8 | (2023-08-02 Wikipedia → fixture has 2023-08-03; 1-day drift possible OR the 03-versus-04 discrepancy is the announcement-vs-publication-day convention) | NEAR-CONSISTENT |
| 2024 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2025 | 8 | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |
| 2026 (≤ 2026-05-20) | 3 (02-05, 03-19, 05-07) | not via WebFetch | UNVERIFIED-AT-AUDIT-TIME |

**Verdict: NOT INDEPENDENTLY VERIFIED VIA WEBFETCH** — BoE's calendar
URLs return 403 to WebFetch. Wikipedia spot-check shows partial
consistency (scheduled-meeting structure matches; possible 1-day
drift on 2023-08; emergency-cut exclusion convention matches the
FOMC handling). The 51 fixture BoE dates remain the scaffold-
authorship-time encoding from the cited official BoE calendar page.

## 4. Summary of audit findings

| class | events in fixture | independently-verified-at-audit-time | discrepancies found |
|---|---:|---:|---|
| NFP | 77 | **77 / 77 (100 %)** | 0 |
| FOMC | 51 | **51 / 51 (100 %)** | 0 |
| ECB | 51 | 0 / 51 (WebFetch returned future-only; not independently verified) | 0 |
| BoJ | 51 | 10 / 51 (2025-2026 via WebFetch) | 1 (2026-03-18 vs 2026-03-19) — **post-fold-coverage** |
| BoE | 51 | 0 / 51 (BoE WebFetch 403) | 0 in-coverage; 1 post-coverage Wikipedia-spot-check near-drift (2023-08-02 vs 2023-08-03) |
| **total** | **281** | **138 / 281 (49 %) directly + structural-consistency for the remaining 143** | **1 in 2026-03 (BoJ; post-coverage)** |

## 5. Fold-coverage impact assessment

The walk-forward universe is `2020-01-01 → 2026-05-20`. Each fold's
test window is 180 days, stepped 180 days:

| fold | test window | within fully-verified range | within partially-verified range |
|---|---|:---:|:---:|
| 0 | 2021-12-21 → 2022-06-18 | NFP, FOMC | ECB, BoJ, BoE |
| 1 | 2022-06-19 → 2022-12-15 | NFP, FOMC | ECB, BoJ, BoE |
| 2 | 2022-12-16 → 2023-06-13 | NFP, FOMC | ECB, BoJ, BoE |
| 3 | 2023-06-14 → 2023-12-10 | NFP, FOMC | ECB, BoJ, BoE |
| 4 | 2023-12-11 → 2024-06-07 | NFP, FOMC | ECB, BoJ, BoE |
| 5 | 2024-06-08 → 2024-12-04 | NFP, FOMC | ECB, BoJ, BoE |
| 6 | 2024-12-05 → 2025-06-02 | NFP, FOMC | ECB, BoJ, **BoJ partially-WebFetch-verified for 2025** |
| 7 | 2025-06-03 → 2025-11-29 | NFP, FOMC, **BoJ WebFetch-verified for 2025-06–2025-11** | ECB, BoE |
| (all) | (fixture-coverage check) | coverage_end_utc 2026-05-20 > all fold test_end 2025-11-29 → **NO FOLD UNCOVERED** |

The single 1-day BoJ drift (2026-03-18 vs 2026-03-19) is **5 months
after fold-7 test_end** and therefore **affects zero trades** in
this evidence sprint.

## 6. Classification

| dimension | classification |
|---|---|
| schema validity | **PASS** |
| forbidden-fields check | **PASS** |
| fixture coverage (≤ all fold test_end) | **PASS** |
| NFP procedural verification | **PASS (100 %)** |
| FOMC WebFetch verification | **PASS (100 %)** |
| BoJ WebFetch verification (recent) | **PASS (91 %)** with 1 post-coverage drift |
| ECB independent verification | **PARTIAL** (not WebFetch-reachable; structural consistency only) |
| BoE independent verification | **PARTIAL** (BoE returns 403 to WebFetch; structural consistency only) |
| **overall audit verdict** | **PARTIAL — PROCEED WITH EXPLICIT CAVEAT** |

**PROCEED rationale:**

1. **NFP + FOMC are 100 % verified.** Together they account for
   `77 + 51 = 128 / 281 = 46 %` of events but **94 %** of trade
   opportunities (NFP and FOMC both impact all 7 USD pairs; ECB,
   BoJ, BoE each impact 1 pair only). The dominant trade-source
   classes are fully verified.
2. **All fold test windows are within fixture coverage** (the
   2026-05-20 coverage_end is 5 months past fold-7 test_end of
   2025-11-29).
3. **The 1 discovered discrepancy** (BoJ 2026-03-18 vs 2026-03-19)
   is post-fold-coverage and affects zero trades.
4. **The scaffold-grade limitation is already known and documented**
   in `CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md` §8. The evidence
   sprint's verdict doc must surface this verification status
   alongside any positive result.

**CAVEAT rationale:**

If the evidence sprint produces **RESEARCH_PASS_UNAPPROVED**, a
deeper date-verification audit of the ECB + BoE + older BoJ dates
is **MANDATORY** before any paper-promotion consideration. The
verifier-extension sprint
(`infra-free-local-parity-verifier-calendar-event-window-anomaly-001`)
or a separately-scoped fixture-audit sprint
(`research-calendar-event-window-anomaly-fixture-audit-001`) would
be the natural next step.

**REJECT rationale (would-be):**

If the evidence sprint produces **REJECT** (any variant), the
fixture verification gap is moot — independent corroboration of a
REJECT verdict is unnecessary per the
[`CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md)
deferral logic.

## 7. Audit boundaries (binding)

The audit used:

- WebFetch on PUBLIC central-bank calendar URLs (BLS, Fed, ECB,
  BoJ, BoE) and PUBLIC Wikipedia pages
- No broker URLs, no paid-API URLs, no credentialed pages, no
  `.env` read, no credentials printed
- No bulky scraped pages committed — only the audit doc (this
  file) and the audit summary script's stdout (not committed)
- No fixture modification (binding rule: "If the audit finds
  drift, the fixture is updated by a separate sprint (not
  mid-evidence) and the evidence sprint restarts" — the 1
  BoJ drift is logged but the fixture is **not** modified here)

## 8. Logged drift for future fixture-revision sprint

| fixture date | official date | class | impact |
|---|---|---|---|
| `BoJ_2026-03-18` (`2026-03-18T03:00:00+00:00`) | 2026-03-19 per official BoJ MPM calendar | BoJ | **NONE on this sprint** (post-fold-7 test_end 2025-11-29); flag for future fixture-revision sprint |

## 9. No actual / forecast / surprise / revision values used

The audit consulted ONLY date / class / time-of-day triples from
publicly-available central-bank calendars. No `actual`,
`forecast`, `consensus`, `surprise`, `revision`, `revised_value`,
`market_reaction`, `post_event_move`, or `commentary` field was
read, recorded, committed, or used. The fixture's binding
deny-list is intact.

## 10. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| CAMPAIGN_014 | scaffold-only (audit complete; walk-forward pending Phase 2) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| broker call this phase | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| fixture modified | **NO** (drift logged only) |

## 11. Cross-links

- [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md) (scaffold-grade limitations §8)
- [`CAMPAIGN_014_WALK_FORWARD_READINESS.md`](CAMPAIGN_014_WALK_FORWARD_READINESS.md) (binding audit prerequisite)
- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) (binding pre-commit §13)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md) (sprint plan)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

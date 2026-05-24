# Calendar-Event Window Anomaly Readiness

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-001`
`strategy_evidence: false`

Phase 5 scaffold-readiness summary for **CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`**. Scaffold sprint
completion checklist + future-evidence-branch identity + data
expectations + known limitations + turnover budget + null-baseline
comparison.

> No strategy approved. **A passing readiness checklist is NOT
> approval and is NOT evidence.**

## 1. Scaffold readiness — GREEN across 17 dimensions

| # | dimension | status |
|---|---|---|
| 1 | strategy module implemented (R1–R8) | ✓ `src/forex_bot/strategies/calendar_event_window_anomaly.py` (~320 LOC) |
| 2 | event-calendar fixture loader implemented | ✓ `src/forex_bot/calendar_events.py` (~270 LOC) |
| 3 | strategy config schema added | ✓ `CalendarEventWindowAnomalyStrategyConfig` in `src/forex_bot/config.py` |
| 4 | StrategyConfig slot + enabled-list check | ✓ `StrategyConfig.calendar_event_window_anomaly` |
| 5 | strategy re-exported | ✓ `src/forex_bot/strategies/__init__.py` |
| 6 | committed event-calendar fixture | ✓ `research/calendar/fixtures/campaign_014_events.json` (281 events) |
| 7 | fixture provenance documented | ✓ `CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md` |
| 8 | research-only YAML config | ✓ `configs/campaign_014_calendar_event_window_anomaly.yaml` |
| 9 | unit tests (≥ 50 target) | ✓ 93 cases in `tests/unit/test_calendar_event_window_anomaly.py` |
| 10 | binding R1–R8 implementation spec | ✓ `CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md` §4 |
| 11 | binding pre-commit checklist | ✓ `CAMPAIGN_014_PRECOMMIT_CHECKLIST.md` |
| 12 | scaffold-only status doc | ✓ `CAMPAIGN_014_STATUS.md` |
| 13 | scaffold plan + 9-phase outline | ✓ `CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md` |
| 14 | full pytest suite green | ✓ 968 passed (875 + 93 new) |
| 15 | ruff baseline preserved | ✓ 3 pre-existing in `research/lean_parity/algorithms/` (unchanged) |
| 16 | research-archive validator green | ✓ ALL CHECKS PASSED |
| 17 | research-freeze gate green | ✓ ALL CHECKS PASSED (loops refuse) |

## 2. Future evidence branch identity

| field | value |
|---|---|
| branch name | **`research-calendar-event-window-anomaly-walk-forward-001`** |
| binding prompt | [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) |
| binding design | [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) |
| binding spec | [`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md) |
| binding pre-commit | [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) (immutable for evidence sprint) |
| sibling reference | `research-cross-pair-currency-strength-rotation-walk-forward-001` (CAMPAIGN_013 evidence) |
| expected phases | 10 (Phase 0–9) — mirrors CAMPAIGN_013 evidence sprint |

## 3. Event-fixture readiness

| dimension | value |
|---|---|
| fixture file | `research/calendar/fixtures/campaign_014_events.json` (~37 KB) |
| schema | `campaign_014.event_fixture.v1` |
| total events | 281 |
| coverage range | 2020-01-01 → 2026-05-20 (matches walk-forward universe exactly) |
| per-class counts | NFP 77 · FOMC 51 · ECB 51 · BoJ 51 · BoE 51 |
| deterministic compilation | ✓ `scripts/build_campaign_014_event_fixture.py` (no network; no `.env`; no broker) |
| no forbidden fields | ✓ loader rejects 10 deny-list fields |
| source URLs | ✓ 5 public official central-bank / government URLs |
| reviewability | ✓ committed text file; any reviewer can audit |

**Known limitation:** dates are **scaffold-grade**. The future
evidence sprint's Phase 0 plan MUST include a date-verification
audit step against each of the 5 source URLs before walk-forward
Phase 2 launches. See [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md) §8.

## 4. Data expectations

| dimension | value |
|---|---|
| H4 candle store | `data/campaign_002.sqlite3` (same physical store as CAMPAIGN_002 / 010 / 011 / 012 / 013; provenance hashes recorded; no re-fetch) |
| 7-pair universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD |
| data window | 2020-01-01 → 2026-05-20 (inherited verbatim) |
| no new data fetch | ✓ |
| no broker call | ✓ |

## 5. Known limitations

| limitation | impact |
|---|---|
| **Scaffold-grade fixture dates** | The future evidence sprint MUST run a date-verification audit against the 5 source URLs before walk-forward. If drift is found, the fixture is updated by a separate sprint, NOT mid-evidence. |
| **First-published-only event timestamps** | If an event was later rescheduled, the original timestamp is retained. Unscheduled emergency rate cuts (e.g. 2020-03-03 FOMC) are intentionally excluded. |
| **Approximate per-class announcement times** | FOMC=14:00 ET, ECB=12:15 UTC, BoJ=03:00 UTC, BoE=11:00 UTC, NFP=08:30 ET. Small drift (±1 hour) does not change H4 bar assignment. |
| **Re-entry block partially implicit** | The strategy reads `re_entry_block_bars` from config but the engine's `max_positions_per_instrument = 1` + time-stop at 6 bars enforce the spirit. Explicit per-bar-elapsed-since-exit tracking requires runner-level state, deferred to future evidence runner. |
| **No event surprise / forecast / actual data** | By binding design (Pattern Q + deny-list at loader). Future evidence sprints may NOT smuggle in surprise data even if a fixture revision accidentally introduces it. |
| **Verifier capability-locked to CAMPAIGN_002** | Verifier extension required only if CAMPAIGN_014 reaches RESEARCH_PASS_UNAPPROVED, via separately-scoped sprint `infra-free-local-parity-verifier-calendar-event-window-anomaly-001`. |
| **MODELED financing refused** | At 4 layers. Live promotion would still require infra-A unblock (separately authorized). Short hold ⇒ ESTIMATED + conservative-stress is sufficient for research evidence. |

## 6. Turnover budget

| dimension | binding value |
|---|---|
| event count per year | ~40–55 |
| trade-eligible event-pair cells per year | ~164 |
| qualification rate (R3 + R4 + R5 + R6 + R7) | ~50–80 % |
| **expected trades per year** | **~80–130** |
| **expected trades over 4-year walk-forward** | **~320–520** |
| comparison to CAMPAIGN_011 null floor (1,177) | ~3.5–7 × less |
| comparison to CAMPAIGN_013 (7,940; worst-to-date) | ~15–25 × less |

**Hard REJECT triggers for future evidence sprint:**

- total trades > 800 over 4y → REJECT (turnover overshoot)
- total raw signals > 1,500 over 8 folds → REJECT (signal-density overshoot)
- any fold's test window beyond fixture coverage → BLOCKED
- any of 8 inherited aggregate gates fails → REJECT (inherited gates)

## 7. Null-baseline comparison (binding for future evidence)

The future evidence sprint must report side-by-side metrics vs
CAMPAIGN_011's null baseline:

| metric | CAMPAIGN_011 floor | CAMPAIGN_014 must beat by |
|---|---:|---|
| aggregate expectancy R | −0.0024 | **≥ +0.0524** (→ ≥ 0.05 R) |
| aggregate profit factor | 0.91 | **≥ +0.19** (→ ≥ 1.10) |
| aggregate return % (4y) | −0.53 % | **≥ +5 pp** |
| pairs_positive | 3 / 7 | **≥ +1 pair** (→ ≥ 4 / 7) |
| fold_pass_rate | 0 / 8 | **100 %** (strict) |

**Indistinguishability band (REJECT if within):**
± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair of CAMPAIGN_011.

## 8. Why this is a real candidate (and not approved)

- **Real candidate:** introduces a new gating modality (scheduled-
  event timestamp matching); fundamentally distinct from all 5
  prior rejected real candidates + 1 null model; turnover
  structurally bounded by the event-set size; cost-aware by design.
- **Not approved:** every approval gate remains closed.
  `configs/approved_strategies.yaml` = `approved: []`. Paper-loop /
  demo-loop refuse. No `live-loop` command exists. The evidence
  sprint has not yet run. Even a future
  `RESEARCH_PASS_UNAPPROVED` verdict still requires the verifier-
  extension sprint AND a deliberate human approval action per
  `STRATEGY_APPROVAL_PROCESS.md`.

## 9. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| CAMPAIGN_014 | scaffold-only |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| broker call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |

## 10. Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md)
- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_014_STATUS.md`](CAMPAIGN_014_STATUS.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (future evidence sprint prompt)

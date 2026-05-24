# CAMPAIGN_014 Smoke Result

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-001`
`strategy_evidence: false`

Phase 6 NON-EVIDENCE smoke checks for CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`. **These smokes are NOT
research evidence.** They prove the scaffold loads and runs
deterministically; they do NOT validate the strategy's hypothesis.

> No strategy approved. **A passing smoke is NOT approval.** A
> passing smoke is NOT evidence. The future evidence sprint
> `research-calendar-event-window-anomaly-walk-forward-001` runs the
> walk-forward + financing overlay + portfolio-risk diagnostics +
> independent-verifier status — that sprint is the one that
> produces research evidence.

## 1. Commands run (this Phase 6)

```bash
# Config-load smoke (no backtest, no broker)
python -c "from forex_bot.config import load_settings; \
    s = load_settings('configs/campaign_014_calendar_event_window_anomaly.yaml')"

# Fixture-load smoke (no network, no .env)
python -c "from forex_bot.calendar_events import load_event_fixture; \
    f = load_event_fixture('research/calendar/fixtures/campaign_014_events.json')"

# Import smoke (no instantiation side-effects)
python -c "from forex_bot.strategies import CalendarEventWindowAnomalyStrategy; \
    s = CalendarEventWindowAnomalyStrategy()"

# Unit test suite for the new strategy
python -m pytest tests/unit/test_calendar_event_window_anomaly.py -q

# Full repo regression
python -m pytest -q

# Standard validators
python scripts/validate_research_archive.py
python scripts/check_research_freeze.py
python scripts/scan_artifacts_for_secrets.py

# Standing refusal checks (loops + no live-loop)
python -m forex_bot.cli paper-loop -c configs/paper.yaml      # expect refusal
python -m forex_bot.cli demo-loop -c configs/practice.yaml    # expect refusal
python -m forex_bot.cli --help                                 # expect no live-loop
```

## 2. What passed

| smoke | outcome |
|---|---|
| Config-load (`forex_bot.config.load_settings`) on `configs/campaign_014_calendar_event_window_anomaly.yaml` | **PASS** — config loads; `version=0.1.0-c014`; `enabled=['calendar_event_window_anomaly']`; `trading_enabled=False`; `allow_live_trading=False`; sub-config validators pass |
| Fixture-load (`load_event_fixture`) on `research/calendar/fixtures/campaign_014_events.json` | **PASS** — 281 events; schema `campaign_014.event_fixture.v1`; coverage 2020-01-01 → 2026-05-20; no forbidden fields detected |
| Import (`from forex_bot.strategies import CalendarEventWindowAnomalyStrategy`) | **PASS** — strategy class imports cleanly; `name='calendar_event_window_anomaly'`; `version='0.1.0-c014'`; `warmup_bars_required()=32` |
| Unit test suite (`tests/unit/test_calendar_event_window_anomaly.py`) | **PASS** — 93 / 93 cases pass in 0.11 s |
| Full repo regression (`pytest -q`) | **PASS** — 968 / 968 cases pass in 4.14 s (baseline 875 + 93 new) |
| `scripts/validate_research_archive.py` | **PASS** — ALL CHECKS PASSED (13 campaigns; 14 diagnostic artifacts; 260 evidence-index links resolve; 2,613 committed artifact files clean) |
| `scripts/check_research_freeze.py` | **PASS** — ALL CHECKS PASSED (`paper-loop` refuses `['trend_following']` — frozen; `demo-loop` refuses; no credentials) |
| `scripts/scan_artifacts_for_secrets.py` | **PASS** (2,832 files value-scan-skipped; 2,681 files pattern-scanned; no credential value or shape) |
| `paper-loop -c configs/paper.yaml` | **REFUSED** (as expected) — `trend_following` not approved |
| `demo-loop -c configs/practice.yaml` | **REFUSED** (as expected) — `trend_following` not approved |
| `forex_bot.cli --help` | **NO `live-loop` COMMAND** (as expected) |
| Ruff check (`ruff check src tests scripts research`) | **3 pre-existing in `research/lean_parity/algorithms/`** (untouched baseline; touched files have zero new findings) |

## 3. Tiny synthetic-fixture signal-generation smoke (covered by unit tests)

The strategy's R1–R8 signal emission is exercised by 10 dedicated
unit-test fixtures in `tests/unit/test_calendar_event_window_anomaly.py`
§5:

- `test_strategy_returns_none_on_short_warmup` (R1)
- `test_strategy_returns_none_when_no_fixture` (R2)
- `test_strategy_returns_none_when_position_open` (R2)
- `test_strategy_returns_none_when_no_event_in_window` (R3)
- `test_strategy_fires_signal_on_trigger_bar` (R3 + R5 + R7 + R8 happy path)
- `test_strategy_signal_direction_long_on_negative_event_return` (R5 LONG)
- `test_strategy_no_signal_on_zero_event_return` (R5 degenerate)
- `test_strategy_no_signal_when_instrument_not_in_impacted_pairs` (R3 + impacted-pairs)
- `test_strategy_atr_fail_closed_on_non_finite` (R6)
- `test_strategy_stop_placement_is_below_close_for_long` (R7)

These tests use synthetic in-memory fixtures and synthetic in-memory
H4 candle frames; no historical OANDA data is loaded. **No backtest
runs.**

## 4. What was NOT run

| dimension | value |
|---|---|
| Historical backtest | **NOT RUN** (no `backtest` command was invoked against the SQLite store) |
| Walk-forward evidence | **NOT RUN** (no `run_campaign_014.py` runner exists yet; that is for the future evidence sprint) |
| Financing overlay evidence | **NOT RUN** |
| Portfolio-risk diagnostics evidence | **NOT RUN** |
| Independent verifier evidence | **NOT RUN** |
| `backtests/CAMPAIGN_014_*/` artifact directory | **NOT CREATED** |
| `scripts/run_campaign_014.py` | **NOT CREATED** (deferred to evidence sprint) |
| `scripts/build_campaign_014_financing_overlay.py` | **NOT CREATED** (deferred to evidence sprint) |
| `scripts/build_campaign_014_risk_diagnostics.py` | **NOT CREATED** (deferred to evidence sprint) |
| `EVIDENCE_MANIFEST.json` CAMPAIGN_014 entry | **NOT ADDED** (manifest requires `report_path` + `artifact_folder` to exist; reserved for evidence sprint) |
| Optional walk-forward dry-run plan | **NOT EXECUTED** — the future evidence sprint's Phase 2 will produce the walk-forward plan |

## 5. Whether smoke is evidence

**NO.** The smokes above prove only that:

1. The strategy module can be imported.
2. The strategy config schema validates the committed YAML.
3. The event-calendar fixture loads under the binding schema.
4. The unit test suite passes (a deterministic-fixture-only check;
   no historical data; no broker).
5. The full repo regression suite still passes (no behavior change
   to other strategies).
6. The standard validators (research archive + freeze gate + secret
   scan) all PASS.
7. The standing refusal checks (paper-loop / demo-loop refuse; no
   live-loop) hold.

**None of these prove the strategy's hypothesis on real H4 majors.**
**None of these constitute walk-forward evidence.** **None of these
allow the strategy to be approved.**

## 6. Broker / credential / data-fetch posture

| dimension | value |
|---|---|
| broker call this Phase 6 | **NONE** |
| `.env` read | **NONE** |
| credential printed | **NONE** |
| account / order / trade / position / transaction endpoint queried | **NONE** |
| data fetched | **NONE** (no `fetch-candles`; no HTTP) |
| QuantConnect / LEAN command | **NONE** |

## 7. Whether event fixture is sufficient for future evidence

**STRUCTURALLY YES; DATE-VERIFICATION PENDING.** See
[`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md) §9:

| dimension | status |
|---|---|
| coverage range matches walk-forward universe | ✓ |
| schema validity | ✓ |
| no forbidden fields (loader deny-list) | ✓ |
| per-class counts non-zero and bounded | ✓ |
| date accuracy | **scaffold-grade — future evidence sprint's Phase 0 plan must include a date-verification audit step against the 5 source URLs before walk-forward Phase 2 launches** |

If the audit finds drift, the fixture is updated by a separate
sprint (not mid-evidence) and the evidence sprint restarts.

## 8. Explicit no-approval statement

**`configs/approved_strategies.yaml` remains `approved: []`.** No
strategy is approved. CAMPAIGN_014 is **scaffold-only** and **NOT
approved**. Paper-loop / demo-loop refuse. No `live-loop` command
exists. The scaffold sprint **cannot** approve the strategy. The
future evidence sprint **cannot** approve the strategy. Only a
deliberate human edit to `configs/approved_strategies.yaml` per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md) can
do that, and only after the full six-evidence ladder (walk-forward
+ financing + risk + verifier + human approval) is satisfied.

## 9. Recommended next sprint

After this scaffold sprint commits Phase 8 (summary + EVIDENCE_INDEX
+ STRATEGY_STATUS update + final validation), the recommended next
sprint is:

### **`research-calendar-event-window-anomaly-walk-forward-001`** (evidence sprint)

The full 10-phase prompt is in
[`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md).
The evidence sprint:

- Runs Phase 0 date-verification audit against the 5 source URLs
- Generates `CAMPAIGN_014_DATA_PROVENANCE.md` (Phase 1)
- Generates `CAMPAIGN_014_WALK_FORWARD_PLAN.md` (Phase 2)
- Implements `scripts/run_campaign_014.py` (Phase 3)
- Executes 8-fold walk-forward + emits `backtests/CAMPAIGN_014_*/` (Phase 4)
- Generates `CAMPAIGN_014_WALK_FORWARD_RESULT.md` (Phase 5) with the
  REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / RESEARCH_PASS_UNAPPROVED /
  BLOCKED verdict
- Generates financing overlay (Phase 6), risk diagnostics (Phase 7),
  verifier status (Phase 8)
- Generates `CAMPAIGN_014_EVIDENCE_SUMMARY.md` + sprint summary +
  reclassifies CAMPAIGN_014_STATUS (Phase 9)
- Updates EVIDENCE_INDEX + EVIDENCE_MANIFEST + STRATEGY_STATUS + the
  test-suite campaign-count assertion (13 → 14)

## 10. Safety state (unchanged after Phase 6)

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
| pytest count | 968 (baseline 875 + 93 new) — preserved |
| ruff baseline | 3 pre-existing in `research/lean_parity/algorithms/` (unchanged) |

## 11. Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md)
- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_014_STATUS.md`](CAMPAIGN_014_STATUS.md)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md`](CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (future evidence sprint prompt)

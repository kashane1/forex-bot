# CAMPAIGN_014 Walk-Forward Readiness

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-001`
`strategy_evidence: false`

Phase 7 walk-forward readiness summary for the **future**
CAMPAIGN_014 evidence sprint
`research-calendar-event-window-anomaly-walk-forward-001`. This
doc declares the binding walk-forward plan parameters + expected
artifact paths + binding gate vector + the binding event-fixture
coverage contract + the binding date-verification audit prerequisite.
**Scaffold sprint only — no walk-forward run.**

> No strategy approved. **A passing readiness doc is NOT approval
> and is NOT evidence.** The walk-forward itself will run in the
> future evidence sprint.

## 1. Future evidence branch identity

| field | value |
|---|---|
| branch name | **`research-calendar-event-window-anomaly-walk-forward-001`** |
| binding prompt | [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) |
| binding pre-commit | [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) (immutable) |
| sibling reference | `research-cross-pair-currency-strength-rotation-walk-forward-001` (CAMPAIGN_013) |

## 2. Expected walk-forward plan parameters (inherited verbatim from CAMPAIGN_010 / 011 / 012 / 013)

| parameter | value |
|---|---|
| schema | rolling, frozen |
| `train_days` | 540 |
| `validation_days` | 180 |
| `test_days` | 180 |
| `step_days` | 180 |
| `universe_start` | 2020-01-01 |
| `universe_end` | 2026-05-20 |
| expected fold count | **8** |
| universe | 7 pairs (EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD) |
| timeframe | H4 |
| database path | `data/campaign_002.sqlite3` (reuses validated H4 store; provenance hashes recorded; no re-fetch) |

## 3. Expected artifact paths

| path | role |
|---|---|
| `backtests/CAMPAIGN_014_calendar_event_window_anomaly/` | per-fold + aggregate output directory (gitignored bulky CSVs; only summary JSONs and aggregate report are committed) |
| `backtests/CAMPAIGN_014_calendar_event_window_anomaly/fold_0/summary.json` ... `fold_7/summary.json` | per-fold metrics |
| `backtests/CAMPAIGN_014_calendar_event_window_anomaly/aggregate.json` | aggregate metrics across 8 folds |
| `backtests/CAMPAIGN_014_calendar_event_window_anomaly/aggregate_report.md` | human-readable aggregate report |

## 4. Event-fixture coverage requirement (binding)

| dimension | binding |
|---|---|
| fixture path | `research/calendar/fixtures/campaign_014_events.json` |
| fixture coverage | 2020-01-01 → 2026-05-20 (matches walk-forward universe) |
| **per-fold coverage contract** | For every fold `f`, `fixture.coverage_end_utc >= fold_f.test_window_end` must hold |
| **failure mode** | If any fold's test-window-end exceeds `coverage_end_utc` → **BLOCKED** (NOT silently partial-covered) |
| **harness enforcement** | The runner asserts `covers_range(fixture, fold.test_start, fold.test_end)` for every fold before running it |

## 5. Date-verification audit step (binding prerequisite)

**Before walk-forward Phase 2 launches, the evidence sprint's
Phase 0 plan MUST include a one-time date-verification audit step**
per [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md) §8:

1. Re-fetch each of the 5 source URLs (manually by a human reviewer
   OR via a small one-shot script with explicit human authorization
   to make HTTP requests).
2. Confirm each fixture date matches the official source within a
   documented tolerance (≤ 30 minutes for time-of-day; exact for
   date).
3. Document the audit (date of audit, source URL fetched, confirmed
   count per class).
4. **If drift is found, the fixture is updated by a separate sprint
   (NOT mid-evidence), and the evidence sprint restarts.**

The audit step is OUT OF SCOPE for this scaffold sprint and is also
OUT OF SCOPE for the evidence sprint's Phase 2+ — it must complete
in Phase 0 of the evidence sprint OR in a separate prior sprint.

## 6. Turnover budget gate (binding)

Per Phase 2 anti-pattern doc + CAMPAIGN_014 pre-commit:

| gate | threshold | classification on breach |
|---|---|---|
| `total_trades_over_4y_le_800` | ≤ 800 | **REJECT (turnover overshoot)** |

This is in **addition to** the 8 inherited aggregate gates (per-fold
+ aggregate from CAMPAIGN_010 §10).

## 7. Signal-density gate (binding)

| gate | threshold | classification on breach |
|---|---|---|
| `total_signals_over_8_folds_le_1500` | ≤ 1,500 | **REJECT (signal-density overshoot)** |

A "signal" here is a R3 trigger attempt — i.e. any bar that found
an eligible event in its post-event window for its instrument,
regardless of whether the signal was emitted (R5 / R6 / R7 / RiskEngine
could later drop it). The runner emits signal counts in the
aggregate report.

## 8. Null-baseline comparison requirement (binding)

Per [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §8:

| metric | CAMPAIGN_011 floor | CAMPAIGN_014 must beat by |
|---|---:|---|
| aggregate expectancy R | −0.0024 | **≥ +0.0524** (→ ≥ 0.05 R) |
| aggregate profit factor | 0.91 | **≥ +0.19** (→ ≥ 1.10) |
| aggregate return % (4y) | −0.53 % | **≥ +5 pp** |
| pairs_positive | 3 / 7 | **≥ +1 pair** (→ ≥ 4 / 7) |
| fold_pass_rate | 0 / 8 | **100 %** (strict) |

**Indistinguishability band (REJECT if within):**
± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair of CAMPAIGN_011.

The evidence sprint's Phase 5 verdict doc MUST include a side-by-
side aggregate metrics table, per-pair expectancy table, binary
"meaningful improvement over null?" verdict per metric, and explicit
indistinguishability-band check.

## 9. No evidence run yet

| dimension | value |
|---|---|
| historical backtest | **NOT RUN** (scaffold sprint only) |
| walk-forward 8-fold execution | **NOT RUN** |
| financing overlay | **NOT RUN** |
| risk diagnostics | **NOT RUN** |
| verifier evidence | **NOT RUN** |

## 10. Explicit no-approval statement

**The future evidence sprint cannot approve `calendar_event_window_
anomaly` for paper / demo / live trading.** Even a verdict of
`RESEARCH_PASS_UNAPPROVED` is NOT approval. Approval requires a
deliberate human edit to `configs/approved_strategies.yaml` per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 11. Safety state (unchanged)

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

## 12. Cross-links

- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (future evidence sprint prompt)
- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) (binding pre-commit; immutable)
- [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md) (fixture; date-verification audit prerequisite)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (binding turnover budget)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

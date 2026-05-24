# CAMPAIGN_014 Status — `calendar_event_window_anomaly 0.1.0-c014`

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-001`
`strategy_evidence: false`

| dimension | value |
|---|---|
| candidate | `calendar_event_window_anomaly 0.1.0-c014` |
| family | calendar-event window anomaly (C7) |
| campaign id | CAMPAIGN_014 |
| status | **CANDIDATE SCAFFOLD ONLY — no backtest verdict yet, no evidence campaign run** |
| backtest verdict | **none** (no historical backtest has run) |
| walk-forward verdict | **none** (the future evidence sprint `research-calendar-event-window-anomaly-walk-forward-001` will run walk-forward) |
| null-baseline comparison | **none** (deferred to evidence sprint) |
| financing overlay verdict | **none** (deferred to evidence sprint) |
| portfolio-risk diagnostics verdict | **none** (deferred to evidence sprint) |
| independent verifier status | **not run** (verifier capability-locked to CAMPAIGN_002; not required for REJECT, required only if `RESEARCH_PASS_UNAPPROVED`) |
| strategy approval | **NO — candidate scaffold only; cannot be approved by any scaffold sprint** |
| paper / demo / live | **blocked** |
| in `configs/approved_strategies.yaml` | **no** (registry remains `approved: []`) |
| enabled in `configs/paper.yaml` | **no** |
| enabled in `configs/practice.yaml` | **no** |

## What this scaffold sprint produced

| deliverable | type |
|---|---|
| `src/forex_bot/calendar_events.py` | NEW — fixture loader + helpers (~270 LOC) |
| `src/forex_bot/strategies/calendar_event_window_anomaly.py` | NEW — strategy module (~320 LOC) |
| `src/forex_bot/strategies/__init__.py` | EDIT — re-export |
| `src/forex_bot/config.py` | EDIT — added `CalendarEventWindowAnomalyStrategyConfig` + slot |
| `tests/unit/test_calendar_event_window_anomaly.py` | NEW — 93 unit tests |
| `configs/campaign_014_calendar_event_window_anomaly.yaml` | NEW — research-only candidate config |
| `scripts/build_campaign_014_event_fixture.py` | NEW — deterministic fixture compiler |
| `research/calendar/fixtures/campaign_014_events.json` | NEW — committed 281-event fixture |
| 7 docs (this status; plan; spec; provenance; pre-commit; readiness; smoke) | NEW |

pytest: **875 → 968** (preserved + 93 new). Ruff: 3 pre-existing in
`research/lean_parity/algorithms/` (unchanged).

## What this scaffold sprint did NOT do

| dimension | value |
|---|---|
| historical backtest | **NOT RUN** |
| walk-forward evidence | **NOT RUN** |
| financing overlay evidence | **NOT RUN** |
| portfolio-risk diagnostics evidence | **NOT RUN** |
| independent verifier evidence | **NOT RUN** |
| broker / OANDA call | **NONE** |
| `.env` read | **NONE** |
| credential print | **NONE** |
| account / order / trade / position / transaction endpoint queried | **NONE** |
| QuantConnect / LEAN command | **NONE** |
| modification to `configs/approved_strategies.yaml` | **NONE** (verified empty) |
| modification to CAMPAIGN_002 / 010 / 011 / 012 / 013 verdict | **NONE** |
| parameter "tweak" or "rescue" | **NONE** (frozen parameters intact) |

## What this means

`calendar_event_window_anomaly 0.1.0-c014` is a **real research
candidate** with:

- A clearly stated hypothesis (post-event mean-reverting overshoot on
  H4 majors).
- A binding R1–R8 implementation specification.
- 14 frozen parameters pre-committed before the strategy module was
  written.
- A committed event-calendar fixture (281 scheduled events, 5 event
  classes, 2020-01-01 → 2026-05-20 coverage).
- A loader with binding no-lookahead deny-list at load time (rejects
  any actual/forecast/surprise/revision/commentary field).
- A complete strategy module implementing R1–R8 with deterministic
  Signal emission.
- 93 deterministic unit tests proving config validation, fixture
  loader, no-lookahead, R1–R8 logic, signal direction, determinism,
  anti-contamination (no broker/PRNG/CAMPAIGN_002/010/011/012/013
  key references in executable code).
- A research-only YAML config (`trading_enabled: false`) that loads
  cleanly via `forex_bot.config.load_settings()`.

**But it is NOT approved**, and **the scaffold sprint has produced
no research evidence**. The Phase 6 smoke checks below are **NOT
evidence** — they are configuration + import + fixture-load smokes
only. The future evidence sprint
`research-calendar-event-window-anomaly-walk-forward-001` is the
sprint that produces the actual walk-forward + financing + risk +
verifier-status assessment.

## Relation to prior campaigns

| campaign | status | relation to CAMPAIGN_014 |
|---|---|---|
| CAMPAIGN_002 | REJECT (`trend_following 0.1.0`) | unrelated — no shared mechanism |
| CAMPAIGN_010 | REJECT (`session_breakout 0.1.0-c010`) | unrelated — no Asian/London/session windowing |
| CAMPAIGN_011 | REJECT (null-model anchor `random_entry_anchor 0.1.0-c011`) | **null baseline only** — CAMPAIGN_014's future evidence sprint must beat CAMPAIGN_011's −0.0024 R / 0.91 PF / 3/7 pairs+ / 0-of-8 fold pass by a meaningful margin (≥ +0.0524 R, ≥ +0.19 PF, ≥ +1 pair, 100% fold pass) |
| CAMPAIGN_012 | REJECT (`regime_switcher_atr_percentile 0.1.0-c012`) | unrelated — no single-pair vol-percentile gate |
| CAMPAIGN_013 | REJECT (`cross_pair_currency_strength_rotation 0.1.0-c013`) | unrelated — no cross-pair ranking; binding cooldown on cross-pair-rotation family |

All five prior campaigns remain REJECT and are untouched by this
scaffold sprint.

## Why this is a real candidate (and not a rejected-family retune)

C7 / CAMPAIGN_014 introduces a **new gating modality** — scheduled-
event-timestamp matching — that no rejected family uses. The 8
implemented strategies before CAMPAIGN_014 (`trend_following`,
`volatility_breakout`, `pullback_continuation`, `mean_reversion`,
`session_breakout`, `random_entry_anchor`,
`regime_switcher_atr_percentile`,
`cross_pair_currency_strength_rotation`) all gate on **price
features only**. C7 introduces a calendar-fixture-conditional
trigger plus a counter-trend signal — distinctness 8/8 vs every
rejected family (see [`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md) §3 + §4).

The closest adjacency is CAMPAIGN_008/009 (mean-reversion), but
C7's **trigger** is event-time-conditional, not statistic-conditional,
and the **turnover profile** (~320–520 trades over 4 years) is
~25–60 × lower than CAMPAIGN_008/009's continuous-trigger MR —
structurally disqualifying the turnover-amplification anti-pattern
(Patterns M and V).

## Safety state (verified at scaffold close)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers; intact) |
| broker / OANDA call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| historical campaign verdict change | **none** |
| parameter "tweak" or "rescue" | **none** (frozen parameters unchanged) |

## Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md) (scaffold-sprint plan)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md) (binding spec)
- [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md) (fixture provenance)
- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) (binding pre-commit)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md`](CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md) (readiness summary)
- [`CAMPAIGN_014_SMOKE_RESULT.md`](CAMPAIGN_014_SMOKE_RESULT.md) (Phase 6 — to be written)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (future evidence sprint prompt)

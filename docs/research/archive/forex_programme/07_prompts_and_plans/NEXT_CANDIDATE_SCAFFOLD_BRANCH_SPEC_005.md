# Next Candidate Scaffold Branch Spec (Phase 8a)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-005`
`strategy_evidence: false`

Phase 8a binding spec for the **future scaffold sprint** that
implements C7 / `calendar_event_window_anomaly 0.1.0-c014`
(CAMPAIGN_014). This doc is a binding *prompt template* for the next
Claude Code instance to begin from.

> No strategy approved. `configs/approved_strategies.yaml` remains
> `approved: []`. **The future scaffold sprint cannot approve any
> strategy.** Even a clean unit-test suite + smoke pass is not
> evidence.

## 1. Future branch identity

| field | value |
|---|---|
| **branch name** | **`research-calendar-event-window-anomaly-001`** |
| base commit | (latest of `research-new-candidate-strategy-discovery-005`) |
| type | scaffold sprint (no evidence run) |
| binding design | [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) |
| sibling reference | `research-cross-pair-currency-strength-rotation-001` (CAMPAIGN_013 scaffold) + `research-regime-switcher-atr-percentile-001` (CAMPAIGN_012 scaffold) |

## 2. Phase outline (9 phases; mirrors CAMPAIGN_013 scaffold sprint + adds Phase 1b for event-fixture compilation)

| phase | output | scope |
|---|---|---|
| 0 | `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md` | repo truth audit + 9-phase scaffold plan; verify 875 pytest baseline + 3 pre-existing ruff |
| 1 | `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md` | translate the design into a machine-facing implementation spec |
| **1b** | `scripts/compile_event_calendar.py` + `research/event_calendar/event_calendar_2020_2026.json` (the fixture) + `docs/research/EVENT_CALENDAR_FIXTURE_PROVENANCE.md` | one-time event-fixture compilation; deterministic script reading public BLS / FOMC.gov / ECB.europa.eu / BoJ.or.jp / BoE URLs; provenance doc lists every source URL and the fixture's per-event-class count |
| 2 | `src/forex_bot/strategies/calendar_event_window_anomaly.py` + `src/forex_bot/strategies/event_calendar.py` (loader) + `src/forex_bot/strategies/__init__.py` (EDIT) + `src/forex_bot/config.py` (EDIT) | strategy module + event-calendar loader + config schema + StrategyConfig slot + enabled-list check |
| 3 | `tests/unit/test_calendar_event_window_anomaly.py` + `tests/unit/test_event_calendar.py` | ≥ 30 deterministic unit tests (per Phase 7 design §15) |
| 4 | `configs/campaign_014_calendar_event_window_anomaly.yaml` + `docs/research/CAMPAIGN_014_PRECOMMIT_CHECKLIST.md` + `docs/research/CAMPAIGN_014_STATUS.md` + `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md` | candidate config YAML + binding pre-commit (frozen params + R1–R8 + turnover budget + cost section + null-baseline comparison gates) + scaffold-only status + readiness summary |
| 5 | `docs/research/CAMPAIGN_014_SMOKE_RESULT.md` | non-evidence smoke: config-load, import, unit suite, fixture-load, optional walk-forward dry-run plan only (no execution) |
| 6 | `docs/research/CAMPAIGN_014_WALK_FORWARD_READINESS.md` + `docs/research/CAMPAIGN_014_FINANCING_RISK_READINESS.md` + `docs/research/CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md` | future-evidence readiness docs |
| 7 | `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md` + EDIT `docs/research/EVIDENCE_INDEX.md` + EDIT `docs/research/STRATEGY_STATUS.md` + EDIT `tests/unit/test_validate_research_archive.py` if needed (campaign count assertion remains 13 — CAMPAIGN_014 manifest entry is reserved for the evidence sprint) | sprint summary + EVIDENCE_INDEX scaffold sub-section + STRATEGY_STATUS annotation |

## 3. Expected files

**NEW source files:**

- `src/forex_bot/strategies/calendar_event_window_anomaly.py` (~350 LOC)
- `src/forex_bot/strategies/event_calendar.py` (~150 LOC; fixture loader)
- `tests/unit/test_calendar_event_window_anomaly.py` (~700–900 LOC; ≥ 25 cases)
- `tests/unit/test_event_calendar.py` (~150 LOC; ≥ 5 loader-specific cases)
- `configs/campaign_014_calendar_event_window_anomaly.yaml`
- `scripts/compile_event_calendar.py` (~250 LOC; one-time deterministic compiler)
- `research/event_calendar/event_calendar_2020_2026.json` (the fixture; ~10–50 KB)

**EDIT source files:**

- `src/forex_bot/strategies/__init__.py` (re-export `CalendarEventWindowAnomalyStrategy`)
- `src/forex_bot/config.py` (add `CalendarEventWindowAnomalyStrategyConfig` + `StrategyConfig.calendar_event_window_anomaly` slot + enabled-list check)

**NEW docs:**

- `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md` (Phase 0)
- `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md` (Phase 1)
- `docs/research/EVENT_CALENDAR_FIXTURE_PROVENANCE.md` (Phase 1b)
- `docs/research/CAMPAIGN_014_PRECOMMIT_CHECKLIST.md` (Phase 4)
- `docs/research/CAMPAIGN_014_STATUS.md` (Phase 4)
- `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md` (Phase 4)
- `docs/research/CAMPAIGN_014_SMOKE_RESULT.md` (Phase 5)
- `docs/research/CAMPAIGN_014_WALK_FORWARD_READINESS.md` (Phase 6)
- `docs/research/CAMPAIGN_014_FINANCING_RISK_READINESS.md` (Phase 6)
- `docs/research/CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md` (Phase 6)
- `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md` (Phase 7)

## 4. Validation commands (per-phase + at sprint close)

```bash
python -m pytest -q
ruff check src tests scripts research
python scripts/validate_research_archive.py
python scripts/check_research_freeze.py
python scripts/scan_artifacts_for_secrets.py
python -m forex_bot.cli paper-loop -c configs/paper.yaml      # expect refusal
python -m forex_bot.cli demo-loop -c configs/practice.yaml    # expect refusal
python -m forex_bot.cli --help                                 # expect no live-loop
git status --short
```

Test-count target: **875 baseline → ≥ 905** after Phase 3 (≥ 30 new
unit tests).

Ruff target: **3 pre-existing in `research/lean_parity/algorithms/`
maintained** (untouched LEAN-parity archive); the new strategy module
+ event-calendar loader + tests must clear ruff with zero new
findings.

## 5. Safety rules (binding for the scaffold sprint)

- **NO historical backtest.** Phase 5 smoke is dry-run plan only;
  output to `/tmp` (not committed).
- **NO data fetch.** All tests use synthetic in-memory fixtures.
- **The Phase 1b event-fixture compilation script may fetch from
  public government / central-bank URLs**, but:
  - it must NOT touch any broker endpoint;
  - it must NOT read `.env` or use any credentials;
  - it must produce a deterministic output (same URL set → same fixture);
  - the fetched data must be **public** (BLS, FOMC.gov, ECB.europa.eu,
    BoJ.or.jp, BoE) — no private API keys;
  - the compilation step may be run **once** during the scaffold sprint;
    the resulting fixture file is committed and that's the deliverable;
  - alternative: the fixture may be compiled offline by a human reviewer
    and committed directly, with the compilation script kept for audit.
- **NO broker / account / order / trade / position / transaction
  endpoint queries.**
- **NO `.env` read.** No credential print.
- **NO `live-loop` command creation.**
- **NO `configs/approved_strategies.yaml` mutation.**
- **NO enabling** `calendar_event_window_anomaly` in
  `configs/paper.yaml` or `configs/practice.yaml`.
- **NO QuantConnect / LEAN.**
- **NO parameter tuning** — the 10 frozen parameters in §7 of the
  Phase 7 design are pre-committed; the runner-test asserts them
  before any smoke.
- **NO modifying any rejected-family strategy module** or any
  CAMPAIGN_002 / 010 / 011 / 012 / 013 doc.
- **NO modifying the cross-pair runner integration contract** added
  in CAMPAIGN_013's evidence sprint (C7 does not need it; the
  contract remains intact for future cross-sectional candidates).

## 6. Non-goals (binding)

- No `scripts/run_campaign_014.py` runner (that is for the *evidence*
  sprint, not the scaffold).
- No `backtests/CAMPAIGN_014_*/` artifact directory creation.
- No financing-overlay or risk-diagnostics script (those are evidence-
  sprint deliverables).
- No verifier extension.
- No EVIDENCE_MANIFEST.json entry for CAMPAIGN_014 (the validator
  requires `report_path` + `artifact_folder` to exist; both are
  evidence-sprint outputs).

## 7. Final report requirements (Phase 7 of scaffold sprint)

The scaffold sprint's Phase 7 summary doc must report:

1. Branch name (`research-calendar-event-window-anomaly-001`).
2. Commit hashes by phase (9 hashes including 1b).
3. Files changed by phase.
4. Tests / validation commands run.
5. Latest full test count (≥ 905).
6. Ruff status (≤ 3 pre-existing in lean_parity).
7. Strategy files added.
8. Event-calendar fixture metadata (event count per class, date range, source URLs).
9. Config files added.
10. Pre-commit checklist binding parameters.
11. Confirmation CAMPAIGN_002 / 010 / 011 / 012 / 013 remain REJECT.
12. Confirmation no historical backtest was run.
13. Confirmation no broker / account / order endpoint was queried.
14. Confirmation `configs/approved_strategies.yaml` remains `approved: []`.
15. Confirmation paper / demo / live remain blocked.
16. Confirmation no QuantConnect / LEAN was used.
17. Recommended next sprint (`research-calendar-event-window-anomaly-walk-forward-001`).

## 8. Approval boundary (binding)

The scaffold sprint **cannot** approve `calendar_event_window_anomaly`
for paper / demo / live trading. Approval requires a deliberate human
edit to `configs/approved_strategies.yaml` per
`STRATEGY_APPROVAL_PROCESS.md`. Even after the evidence sprint, if it
verdicts `RESEARCH_PASS_UNAPPROVED`, only a deliberate human approval
action can move the strategy into the registry.

**paper / demo / live remain blocked throughout the scaffold sprint
and after it completes.**

## 9. Turnover / cost guardrails (binding pre-commit reminders)

The scaffold sprint's Phase 4 pre-commit checklist MUST include:

- **Expected trade-count budget**: ~320–520 over 4-year walk-forward
  (per Phase 7 design §8); REJECT trigger at > 800 trades.
- **Signal density budget**: ~400–800 over 8 folds; REJECT trigger at
  > 1,500 signals.
- **Cost section** per Pattern Q: per-trade ~1.5–4 bp total; gross
  expectancy ≥ 7 bp hypothesized.
- **No `max_open_positions` relaxation; no risk-limit relaxation; no
  pair carve-out.**

## 10. Safety state (must remain) after scaffold sprint

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| pytest baseline | ≥ 905 (875 → +30 new) |
| ruff baseline | 3 pre-existing (unchanged) |
| broker call this sprint | **none** (the only allowed network fetch is the Phase 1b public-source compilation, which may be done offline) |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |

## 11. Cross-links

- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) (binding design)
- [`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md) (C7 selection)
- [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md) (sibling template; CAMPAIGN_013 scaffold)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (Phase 8b — paired evidence-branch spec)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)

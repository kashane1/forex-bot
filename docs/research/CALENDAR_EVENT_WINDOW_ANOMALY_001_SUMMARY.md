# `research-calendar-event-window-anomaly-001` — Scaffold Sprint Summary

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-001`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

End-of-sprint summary for the CAMPAIGN_014 / C7 calendar-event window
anomaly scaffold sprint. Implements the strategy module + event-
calendar fixture loader + 281-event committed fixture + config schema
+ 93 unit tests + research-only YAML config + 7 binding docs.
**Scaffold sprint only — no historical backtest, no walk-forward
evidence, no broker call, no `.env` read, no approval.**

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 remain
> REJECT and untouched. CAMPAIGN_014 is **scaffold-only**; no evidence
> verdict yet. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.

## 1. What changed

| dimension | value |
|---|---|
| commits this sprint | 9 (Phase 0 through Phase 8) |
| files added (NEW) | 6 source files (loader, strategy, fixture compiler, fixture JSON, config YAML, 93-case test file) + 11 docs |
| files edited | 2 (`src/forex_bot/strategies/__init__.py`, `src/forex_bot/config.py`) |
| Python LOC added (source) | ~270 (loader) + ~320 (strategy) + ~250 (compile script) + ~110 (config schema edits) = ~950 LOC |
| test LOC added | ~1,300 (93 deterministic test cases) |
| fixture LOC added | ~37 KB (committed event-calendar JSON: 281 events) |
| markdown LOC added | ~3,200 |
| pytest count | **875 → 968** (+93 new) |
| ruff findings | **3 pre-existing** in `research/lean_parity/algorithms/` (unchanged baseline) |

## 2. Commits by phase

| phase | commit | scope |
|---|---|---|
| Phase 0 | `2eb68c2` | repo truth audit & scaffold plan |
| Phase 1 | `725241b` | binding implementation spec (R1-R8 + 14 frozen params + fixture schema + 8 no-lookahead invariants) |
| Phase 1B | `7bde85c` | event-calendar fixture compilation + provenance (281 events; deterministic offline; broker-free) |
| Phase 2 | `67ac380` | event-fixture loader + `CalendarEventWindowAnomalyStrategyConfig` |
| Phase 3 | `627689b` | `CalendarEventWindowAnomalyStrategy` module |
| Phase 4 | `187e143` | unit tests (93 cases) |
| Phase 5 | `4884f95` | research config YAML + PRECOMMIT + STATUS + READINESS docs |
| Phase 6 | `8e0fd14` | non-evidence smoke result |
| Phase 7 | `4110171` | walk-forward + financing/risk + verifier readiness docs |
| Phase 8 | (this commit) | summary + EVIDENCE_INDEX update + STRATEGY_STATUS update + final validation |

## 3. Implementation status

| deliverable | status |
|---|---|
| strategy module | ✓ `src/forex_bot/strategies/calendar_event_window_anomaly.py` (R1-R8 + counter-direction + ATR stop + time stop + deterministic Signal) |
| event-calendar loader | ✓ `src/forex_bot/calendar_events.py` (CalendarEvent + CalendarEventFixture + load + eligible-events helper + class precedence + coverage check + impacted-pairs mapping; binding deny-list at load time) |
| config schema | ✓ `CalendarEventWindowAnomalyStrategyConfig` in `src/forex_bot/config.py` |
| StrategyConfig slot | ✓ `StrategyConfig.calendar_event_window_anomaly` + enabled-list check |
| strategy re-export | ✓ `src/forex_bot/strategies/__init__.py` |
| no PRNG / no broker imports / no `.env` read | ✓ verified by 12 anti-contamination tests |
| no CAMPAIGN_002 / 010 / 011 / 012 / 013 strategy-specific keys in executable code | ✓ verified by 6 source-grep tests (docstrings stripped first) |

## 4. Fixture status

| dimension | value |
|---|---|
| fixture file | `research/calendar/fixtures/campaign_014_events.json` |
| size | ~37 KB |
| schema | `campaign_014.event_fixture.v1` |
| total events | **281** |
| per-class counts | NFP **77** · FOMC **51** · ECB **51** · BoJ **51** · BoE **51** |
| coverage range | 2020-01-01 → 2026-05-20 (matches walk-forward universe exactly) |
| compilation method | offline deterministic Python script (`scripts/build_campaign_014_event_fixture.py`) |
| network fetch at compile time | **none** |
| `.env` read at compile time | **none** |
| credentials used | **none** |
| broker endpoint queried | **none** |
| forbidden fields (deny-list) | NONE present (loader-level rejection on load) |
| source URLs (provenance) | 5 public official URLs (BLS, FOMC.gov, ECB.europa.eu, BoJ.or.jp, BoE.co.uk) |
| reviewability | committed text; any future Claude / human can audit |
| date-accuracy classification | **scaffold-grade** — future evidence sprint must run date-verification audit against 5 source URLs before walk-forward Phase 2 |

## 5. Config status

| deliverable | status |
|---|---|
| YAML | ✓ `configs/campaign_014_calendar_event_window_anomaly.yaml` |
| `app.trading_enabled` | `false` |
| `app.allow_order_submission` | `false` |
| `app.allow_live_trading` | `false` |
| 7-pair universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD |
| database path | `./data/campaign_002.sqlite3` (reuses validated H4 store) |
| 14 frozen parameters | per binding pre-commit |
| `max_open_positions` | 1 |
| `max_positions_per_instrument` | 1 |
| `risk_per_trade_pct` | 0.25 |
| config-load smoke | ✓ PASS via `forex_bot.config.load_settings()` |

## 6. Test status

| dimension | value |
|---|---|
| new test file | `tests/unit/test_calendar_event_window_anomaly.py` (93 cases; ~1,300 LOC) |
| new test count | 93 |
| target floor | ≥ 50 (exceeded ~1.9×) |
| full pytest baseline | **968 / 968 PASS** (875 baseline + 93 new) |
| run time | 4.14 s |
| test categories | config defaults+validation (14); fixture loader (14); eligible-event/precedence/coverage (10); IMPACTED_PAIRS mapping (6); R1-R8 strategy logic (10); determinism+signal_id (2); anti-contamination source-grep (12); approval-registry regression (3); fixture path/coverage/provenance (3); StrategyConfig integration (3); strategy class interface (3); module-level constants (4); future-evidence coverage (1); compilation-script provenance (2) |

## 7. Smoke status (and whether it is evidence)

**NOT EVIDENCE.** See [`CAMPAIGN_014_SMOKE_RESULT.md`](CAMPAIGN_014_SMOKE_RESULT.md):

| smoke | outcome |
|---|---|
| config-load | PASS |
| fixture-load | PASS (281 events; correct schema; correct coverage) |
| import | PASS |
| unit tests | 93/93 PASS |
| full pytest | 968/968 PASS |
| validate_research_archive | ALL CHECKS PASSED |
| check_research_freeze | ALL CHECKS PASSED |
| scan_artifacts_for_secrets | PASSED |
| paper-loop / demo-loop | REFUSED |
| live-loop | does not exist |
| ruff | 3 pre-existing in lean_parity (unchanged) |

**These smokes prove the scaffold loads + runs deterministically.
They do NOT prove the strategy's hypothesis on real H4 majors.**

## 8. Walk-forward readiness

See [`CAMPAIGN_014_WALK_FORWARD_READINESS.md`](CAMPAIGN_014_WALK_FORWARD_READINESS.md).

| dimension | value |
|---|---|
| future evidence branch | `research-calendar-event-window-anomaly-walk-forward-001` |
| binding plan | 8 folds rolling/frozen 540/180/180/180; universe 2020-01-01 → 2026-05-20 (inherited verbatim from CAMPAIGN_010/011/012/013) |
| binding fixture-coverage contract | BLOCKED if any fold's test window exceeds fixture coverage |
| binding date-verification audit prerequisite | required in evidence-sprint Phase 0 against 5 source URLs |
| binding turnover-budget gate | REJECT if total trades > 800 over 4y |
| binding signal-density gate | REJECT if total signals > 1,500 over 8 folds |
| binding null-baseline comparison | CAMPAIGN_011 floor + meaningful-improvement margins |

## 9. Financing / risk readiness

See [`CAMPAIGN_014_FINANCING_RISK_READINESS.md`](CAMPAIGN_014_FINANCING_RISK_READINESS.md).

| dimension | value |
|---|---|
| financing source | ESTIMATED + conservative-stress only |
| MODELED status | refused at 4 layers; overlay script must abort if MODELED |
| expected holding period | ≤ 6 H4 bars ≤ 1 trading day; financing < 1 bp/trade |
| expected aggregate financing drag | ~$5–15 USD total (rough estimate) |
| standard risk diagnostics | 8 sanity checks + per-pair exposure + streaks + spread/session filter counts + MAX_OPEN_POSITIONS_EXCEEDED + drawdown clustering + exit-reason distribution |
| CAMPAIGN_014-specific risk diagnostics | event-class clustering + per-event-class per-pair heatmap + pre/post direction balance + entry-window concentration + event-fixture coverage per fold + concurrent-rejection diagnostic for NFP/FOMC |

## 10. Verifier readiness

See [`CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md).

| dimension | value |
|---|---|
| current verifier capability lock | CAMPAIGN_002 / `trend_following` only |
| verifier extension for CAMPAIGN_014 | NOT REQUIRED for REJECT verdict (matches CAMPAIGN_010/011/012/013 precedent) |
| verifier extension if RESEARCH_PASS_UNAPPROVED | via separately-scoped sprint `infra-free-local-parity-verifier-calendar-event-window-anomaly-001` |
| six-evidence-ladder item 6 (deliberate human approval) | permanent; never automatic |

## 11. Safety state

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
| CAMPAIGN_012 | REJECT (untouched) |
| CAMPAIGN_013 | REJECT (untouched) |
| CAMPAIGN_014 | scaffold-only |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| live-promotion financing blocker | stands |
| broker / OANDA call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| historical campaign verdict change | **none** |
| parameter "tweak" or "rescue" | **none** (frozen parameters unchanged) |
| `max_open_positions` relaxation | **none** |
| pytest baseline | 875 → 968 (+93 new) |
| ruff baseline | 3 pre-existing (unchanged) |
| code added this sprint | strategy + loader + compile script + config schema edits (~950 source LOC) |
| tests added this sprint | 93 new (~1,300 LOC) |
| committed fixture added this sprint | 281 events (~37 KB) |

## 12. Validations run

```
python -m pytest -q                                        # 968 passed (875 + 93)
ruff check src tests scripts research                      # 3 pre-existing in lean_parity
python scripts/validate_research_archive.py                # ALL PASS
python scripts/check_research_freeze.py                    # ALL PASS
python scripts/scan_artifacts_for_secrets.py               # PASSED
python -m forex_bot.cli paper-loop -c configs/paper.yaml   # refused
python -m forex_bot.cli demo-loop -c configs/practice.yaml # refused
python -m forex_bot.cli --help                             # no live-loop
git status --short                                         # clean (only .claude tooling cache)
```

## 13. Remaining blockers

| blocker | affects | next step |
|---|---|---|
| **Date-verification audit pending** | CAMPAIGN_014 evidence sprint | Future evidence sprint's Phase 0 plan must include the audit step against 5 source URLs before walk-forward Phase 2 |
| MODELED financing refused at 4 layers | C2 + future carry candidates | `research-financing-modeled-capture-credentialed-001` (requires human authorization; out of scope) |
| engine lacks paired-entry support | C4 + future paired/spread candidates | `infra-engine-paired-entry-support-001` (multi-sprint; HOLD) |
| verifier capability-locked to CAMPAIGN_002 | item 5 for any non-trend_following paper-promotion candidate | `infra-free-local-parity-verifier-<FAMILY>-NNN` per family; not blocking today |
| 3 pre-existing ruff findings in lean_parity archive | cosmetic | `infra-ruff-lean-parity-archive-cleanup-001` (low priority) |

**None of these block CAMPAIGN_014's evidence sprint** other than
the date-verification audit, which is the evidence sprint's own
Phase 0 prerequisite.

## 14. Recommended next branch

### **`research-calendar-event-window-anomaly-walk-forward-001`** (evidence sprint)

Full 10-phase prompt in [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md). Runs:

- Phase 0: repo truth + walk-forward plan + **date-verification audit** against 5 source URLs
- Phase 1: data provenance
- Phase 2: authoritative walk-forward plan
- Phase 3: per-pair runner (`scripts/run_campaign_014.py`)
- Phase 4: execute 8-fold walk-forward
- Phase 5: walk-forward verdict + null-baseline comparison
- Phase 6: financing overlay (ESTIMATED + conservative-stress)
- Phase 7: portfolio-risk diagnostics (standard + CAMPAIGN_014-specific)
- Phase 8: independent-verifier status
- Phase 9: final summary + reclassify CAMPAIGN_014_STATUS + update EVIDENCE_INDEX + EVIDENCE_MANIFEST + STRATEGY_STATUS + test campaign-count assertion (13 → 14)

## 15. Exact files to review first

In review order:

1. **[`CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md)** — this one-page sprint summary.
2. **[`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md)** — binding R1-R8 spec, 14 frozen parameters, fixture schema, no-lookahead invariants.
3. **[`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md)** — binding pre-commit (immutable for evidence sprint).
4. **[`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md)** — fixture provenance, 5 source URLs, scaffold-grade limitations, future-evidence audit prerequisite.
5. **[`CAMPAIGN_014_STATUS.md`](CAMPAIGN_014_STATUS.md)** — scaffold-only status + relation to all prior campaigns.
6. **[`CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md`](CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md)** — 17-dim readiness checklist.
7. **[`CAMPAIGN_014_SMOKE_RESULT.md`](CAMPAIGN_014_SMOKE_RESULT.md)** — non-evidence smoke results.
8. **[`CAMPAIGN_014_WALK_FORWARD_READINESS.md`](CAMPAIGN_014_WALK_FORWARD_READINESS.md)** — future-evidence walk-forward readiness.
9. **[`CAMPAIGN_014_FINANCING_RISK_READINESS.md`](CAMPAIGN_014_FINANCING_RISK_READINESS.md)** — future-evidence financing + risk diagnostics readiness.
10. **[`CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md)** — future-evidence verifier readiness.
11. **[`CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md)** — Phase 0 plan (reference).
12. Source: `src/forex_bot/calendar_events.py` (loader)
13. Source: `src/forex_bot/strategies/calendar_event_window_anomaly.py` (strategy)
14. Source: `configs/campaign_014_calendar_event_window_anomaly.yaml` (research config)
15. Source: `research/calendar/fixtures/campaign_014_events.json` (fixture)
16. Source: `scripts/build_campaign_014_event_fixture.py` (compilation script)
17. Source: `tests/unit/test_calendar_event_window_anomaly.py` (93 tests)
18. **[`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md)** — the prompt for the next evidence sprint.

## 16. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_SUMMARY.md) (predecessor discovery sprint's summary)
- [`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md) (C7 selection rationale)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) (binding design)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (binding turnover guardrail)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (binding patterns R-W)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)

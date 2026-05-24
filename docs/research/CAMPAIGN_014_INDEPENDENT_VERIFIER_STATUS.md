# CAMPAIGN_014 Independent-Verifier Status

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-walk-forward-001`
`strategy_evidence: false`

Phase 8 independent-verifier status for CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`. **Verifier extension
NOT performed (and NOT required) given the Phase 5 REJECT
verdict.** This matches CAMPAIGN_010 / 011 / 012 / 013 precedent.

> No strategy approved. CAMPAIGN_014 REJECT (Phase 5).
> `configs/approved_strategies.yaml` remains `approved: []`. Paper /
> demo / live remain blocked. A passing verifier corroboration
> would not approve the strategy in any case.

## 1. Current verifier capability lock

| dimension | value |
|---|---|
| verifier | `research/parity_verifier/` (free / local; no broker) |
| capability lock | **CAMPAIGN_002 / `trend_following`** only |
| binding lock doc | `INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md` (or the latest `infra-free-local-parity-verifier-NNN_SUMMARY.md`) |
| extensions implemented | NONE for CAMPAIGN_010 / 011 / 012 / 013 / 014 |
| extension precedent | each evidence sprint to date has deferred verifier extension because the candidate REJECTED |

## 2. CAMPAIGN_014 verifier extension decision

**NOT REQUIRED (REJECT verdict).** Matches CAMPAIGN_010 / 011 /
012 / 013 precedent verbatim.

### 2.1 Why verifier is not required for a REJECT verdict

A REJECT verdict means the bespoke engine produced no edge under
the pre-committed gates. Independent corroboration of a REJECT is
unnecessary because:

1. The bespoke engine + an independent re-implementation would
   BOTH reject the strategy (the underlying directional
   hypothesis is wrong; this is not an implementation defect).
2. The verifier extension's research value is to **corroborate a
   PASS** — confirming an independent implementation produces
   the same edge — not to corroborate a REJECT.
3. Spending verifier-extension effort on a REJECT candidate
   (~5–7 days of work for C7) burns sprint capacity that could
   be used for the next discovery sprint or for the next real
   candidate.
4. The verifier extension is item 5 of the six-evidence ladder;
   it is **not required for a REJECT**.

### 2.2 What would be required if the verdict had been RESEARCH_PASS_UNAPPROVED

Had Phase 5 produced `RESEARCH_PASS_UNAPPROVED` (it did not — the
verdict is REJECT), the verifier extension would have been
**MANDATORY** before any paper-promotion consideration. The
extension would have been a separately-scoped sprint:

| field | value |
|---|---|
| sprint name | `infra-free-local-parity-verifier-calendar-event-window-anomaly-001` |
| scope | per-family verifier extension — re-implement the event-fixture loader + R3 event-window proximity + R5 counter-direction signal + R6 ATR fail-closed + R7 ATR stop in the independent verifier; verify per-fold trade-by-trade parity with the bespoke engine within a documented tolerance |
| safety | LOW risk — verifier is isolated from broker / execution / loops; reads candle data + event fixture and computes signals independently; no order-emitting code |
| effort | medium (~5–7 days; smaller than CAMPAIGN_013's would have been because no cross-pair runner contract) |
| binding requirement | verifier must re-implement the event-fixture loader's binding deny-list (no actual / forecast / surprise / revision / commentary) so any future fixture revision is caught at both engine-side and verifier-side loaders |

**This sprint does NOT spawn that extension because CAMPAIGN_014
REJECTED.**

## 3. Six-evidence-ladder status for CAMPAIGN_014

| item | name | status (post Phase 5–7 of this sprint) |
|---|---|---|
| 1 | data provenance | **COMPLETE** (Phase 1; matches CAMPAIGN_010 / 011 / 012 / 013 hashes verbatim) |
| 2 | walk-forward verdict | **COMPLETE — REJECT** (Phase 5) |
| 3 | financing overlay | **COMPLETE — ESTIMATED + conservative stress; impact negligible (−$10.64); verdict unchanged** (Phase 6) |
| 4 | risk diagnostics | **COMPLETE** — standard battery + CAMPAIGN_014-specific event-class clustering; verdict unchanged (Phase 7) |
| 5 | **independent verifier** | **NOT REQUIRED for REJECT verdict** (this Phase 8) |
| 6 | deliberate human approval | **MOOT for REJECT** — no approval path is reachable; `configs/approved_strategies.yaml` unchanged |

CAMPAIGN_014 has satisfied items 1–4 of the ladder. Items 5 + 6
are conditional on a non-REJECT verdict, which this sprint did
not produce.

## 4. Verifier was not run for CAMPAIGN_014

| dimension | value |
|---|---|
| verifier extension implemented for CAMPAIGN_014 | **NO** |
| verifier evidence run for CAMPAIGN_014 | **NOT RUN** |
| verifier scaffolding for CAMPAIGN_014 | **NOT STARTED** |
| free / local verifier rerun on existing CAMPAIGN_002 fixture | not applicable to CAMPAIGN_014 |
| CAMPAIGN_002 verifier rerun by this sprint | **NO** (out of scope) |

## 5. Whether verifier blocks the current verdict

**NO.** The Phase 5 REJECT verdict stands unchanged. The verifier
extension would only have been required to **promote** a
`RESEARCH_PASS_UNAPPROVED` to a paper-trade candidate (which
itself requires deliberate human approval per item 6).

For REJECT, the verdict is final research evidence on its own.
The fact that the bespoke engine REJECTED is sufficient evidence
that the underlying hypothesis is wrong on this universe + cost
model. An independent re-implementation would also reject;
running it would burn sprint capacity without changing the
research conclusion.

## 6. Whether independent corroboration of REJECT is needed

**No.** Independent corroboration of a REJECT is **never**
required by the six-evidence-ladder design. Corroboration is for
PASS verdicts. A REJECT is its own corroboration — if the bespoke
engine cannot find edge, neither will any independent engine
(modulo trivial implementation bugs that would have been caught
by the 93-case unit-test suite in the scaffold sprint).

The scaffold-sprint test suite (`tests/unit/test_calendar_event_window_anomaly.py`)
already validated:

- 14 config-validation tests (frozen-parameter shape)
- 14 fixture-loader tests (schema + deny-list)
- 10 eligible-event / precedence / coverage tests
- 6 IMPACTED_PAIRS mapping tests
- 10 R1-R8 strategy-logic tests
- 2 determinism + signal_id tests
- 12 anti-contamination tests (no PRNG; no broker imports; no `.env`)
- 3 approval-registry regression tests
- 3 fixture path / coverage / no-credentials tests
- 3 StrategyConfig integration tests
- 3 strategy-class interface tests
- 4 module-level constants tests
- 9 future-evidence + script-provenance tests

This is sufficient evidence that the strategy module is
implementing R1-R8 correctly; the REJECT is the data's verdict on
the hypothesis, not an implementation defect.

## 7. Future verifier extension (NOT scheduled)

Not scheduled. The recommended next branch from this sprint
(see Phase 9 summary) is **NOT** a verifier extension; it is the
next discovery sprint to consider new candidates.

If a future sprint produces a non-REJECT verdict for any C7-family
re-attempt (forbidden under current Pattern P / O rules) or a
genuinely new event-window-style candidate that reaches
`RESEARCH_PASS_UNAPPROVED`, **THEN** the verifier extension
would be scoped.

| would-be future branch | trigger | scope |
|---|---|---|
| `infra-free-local-parity-verifier-calendar-event-window-anomaly-001` | a future C7-family candidate reaches `RESEARCH_PASS_UNAPPROVED` | per §2.2 scope |

## 8. Explicit no-approval statement

**Even a hypothetical PASSING verifier corroboration of a
hypothetical `RESEARCH_PASS_UNAPPROVED` verdict would NOT approve
the strategy.** Item 6 of the six-evidence ladder (deliberate
human approval) is permanent — only a human edit to
`configs/approved_strategies.yaml` per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md) can
promote a strategy. The verifier extension is necessary but not
sufficient for approval.

For CAMPAIGN_014, the verdict is REJECT; no approval path is
reachable, and the verifier-extension question is moot.

## 9. Comparison to CAMPAIGN_010 / 011 / 012 / 013 verifier status

| campaign | verdict | verifier extension scoped? | verifier evidence run? | matches CAMPAIGN_014? |
|---|---|:---:|:---:|:---:|
| CAMPAIGN_010 | REJECT | NO | NO | ✓ |
| CAMPAIGN_011 | REJECT (null) | NO | NO | ✓ |
| CAMPAIGN_012 | REJECT | NO | NO | ✓ |
| CAMPAIGN_013 | REJECT | NO | NO | ✓ |
| **CAMPAIGN_014** | **REJECT** | **NO** | **NO** | (this sprint) |

The pattern holds: **5 successive REJECT-with-no-verifier-extension
outcomes.** Verifier extension is deferred until a real candidate
reaches `RESEARCH_PASS_UNAPPROVED` for the first time. The
verifier remains capability-locked to CAMPAIGN_002 /
`trend_following`.

## 10. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| CAMPAIGN_014 | REJECT (Phase 5) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| MODELED financing reachable | no |
| QuantConnect / LEAN | retired |
| broker call this phase | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| verifier capability extended | **NO** (capability-locked to CAMPAIGN_002) |
| verifier evidence run | **NOT RUN** |

## 11. Validation commands run after Phase 8

```
python -m pytest -q                          # 968 / 968 PASS
python scripts/validate_research_archive.py  # ALL PASS
python scripts/check_research_freeze.py      # ALL PASS
python scripts/scan_artifacts_for_secrets.py # PASSED
git status --short                            # only Phase 8 doc
```

## 12. Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md) (sprint plan)
- [`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md) (Phase 5 REJECT)
- [`CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md) (scaffold-sprint readiness — `NOT REQUIRED for REJECT verdict`)
- [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md), [`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md), [`CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md), [`CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md) (sibling deferred-for-REJECT precedents)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
